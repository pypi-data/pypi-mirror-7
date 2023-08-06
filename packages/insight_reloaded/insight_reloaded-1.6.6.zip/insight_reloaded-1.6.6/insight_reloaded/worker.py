# -*- coding: utf-8 -*-
from redis import StrictRedis
import json
import requests
import os
from tempfile import NamedTemporaryFile
import mimetypes
import traceback
import sys

from insight_reloaded.preview import (DocumentPreview,
                                      PreviewException)
from insight_reloaded.insight_settings import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, SENTRY_DSN, REDIS_QUEUE_KEYS,
    DEFAULT_REDIS_QUEUE_KEY, ALLOWED_EXTENSIONS, TEMP_DIRECTORY, CROP_SIZE,
    PREVIEW_SIZES, DOCVIEWER_SUFFIX, STORAGE_CLASS)
from utils import resolve_name

try:
    from raven import Client
except ImportError:
    if SENTRY_DSN:
        SENTRY_DSN = None
        print "SENTRY_DSN is defined but raven isn't installed."


redis = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


class InsightWorkerException(Exception):
    pass


def abort(exception, requested_ressource, callback_url=None):
    """Raise an error but send it first to the callback"""
    if callback_url:
        try:
            requests.post(callback_url,
                          verify=False,
                          data={'success': False,
                                'error_message': str(exception),
                                'requested_ressource': requested_ressource})
        except requests.exceptions.ConnectionError:
            pass
    raise InsightWorkerException('%s : %s' % (requested_ressource,
                                              exception))


def main():
    if SENTRY_DSN:
        client = Client(dsn=SENTRY_DSN)
        while True:
            try:
                start_worker(sys.argv)
            except Exception:
                client.get_ident(client.captureException())
    else:
        while True:
            try:
                start_worker(sys.argv)
            except InsightWorkerException:
                traceback.print_exc()


def start_worker(argv):
    # Init from CLI
    worker_command = argv[0]
    argv = argv[1:]
    argc = len(argv)

    if argc > 1:
        print "USAGE: %s [REDIS_QUEUE_KEY]" % worker_command
        sys.exit(1)
    elif argc == 1:
        queue = argv[0]
        if queue not in REDIS_QUEUE_KEYS:
            print "WRONG QUEUE: %s not in %s" % (queue, REDIS_QUEUE_KEYS)
            sys.exit(2)
    else:
        queue = DEFAULT_REDIS_QUEUE_KEY

    print "Launch insight worker on '%s' redis queue." % queue
    while 1:
        msg = redis.blpop(queue)  # BLPOP is blocking for the next entry
        try:
            params = json.loads(msg[1])
        except ValueError as exc:
            abort(exc, msg)

        print u"Consuming task for doc %s" % params['url']

        # Getting callback url
        if 'callback' in params:
            callback = params['callback']
        else:
            callback = None

        # Downloading file
        try:
            # No need to verify SSL
            r = requests.get(params['url'], verify=False)
            r.raise_for_status()
        except requests.exceptions.ConnectionError, e:
            abort(e, params['url'], callback)
        except requests.exceptions.HTTPError, e:
            abort(e, params['url'], callback)

        extensions = []
        if 'content-type' in r.headers:
            extensions += mimetypes.guess_all_extensions(
                r.headers['content-type'])

        if 'content-disposition' in r.headers:
            filename = r.headers['content-disposition'].split('filename=')[-1]
            filename = filename.strip('"').strip("'")
            extensions.extend(os.path.splitext(filename)[1:])

        # Verify if the file is accepted
        accepted_extensions = list(
            set([ext for ext in extensions if ext in ALLOWED_EXTENSIONS]))
        if len(accepted_extensions) > 0:
            extension = accepted_extensions[0]
        else:
            abort(InsightWorkerException('%s not allowed' %
                                         r.headers['content-type']),
                  params['url'], callback)

        # Creating temporary file
        file_obj = NamedTemporaryFile(suffix=extension, dir=TEMP_DIRECTORY)
        file_obj.write(r.content)
        file_obj.seek(0)

        # Settings parameters
        max_previews = params['max_previews']
        try:
            crop = int(params['crop'])
        except:
            crop = CROP_SIZE

        # Create the storage
        storage_class = resolve_name(STORAGE_CLASS)
        storage = storage_class(params['url'], params['hash'])

        # Here comes the document preview engine
        preview = DocumentPreview(file_obj, callback, PREVIEW_SIZES,
                                  max_previews, TEMP_DIRECTORY,
                                  storage, crop)
        try:
            preview.create_previews()
        except PreviewException, e:
            preview.cleanup()
            file_obj.close()
            abort(e, params['url'], callback)
        else:
            preview.cleanup()
            file_obj.close()

        base_document_url = storage.get_base_document_url()
        docviewer_url = os.path.join(base_document_url, DOCVIEWER_SUFFIX)

        print u"Document previewed in %s" % docviewer_url\
            .replace('{size}', 'normal').replace('{page}', '1')

        if callback:
            requests.post(params['callback'],
                          verify=False,
                          data={'success': True, 'num_pages': preview.pages,
                                'docviewer_url': docviewer_url})


if __name__ == "__main__":
    main()
