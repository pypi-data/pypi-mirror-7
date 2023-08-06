# -*- coding: utf-8 -*-
import os.path
try:
    import settings
except ImportError:
    settings = None

import mimetypes

mimetypes.add_type('application/x-tika-ooxml', '.docx')

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB = getattr(settings, 'REDIS_DB', 0)
DEFAULT_REDIS_QUEUE_KEY = getattr(settings, 'DEFAULT_REDIS_QUEUE_KEY',
                                  'insight-reloaded')
REDIS_QUEUE_KEYS = getattr(settings, 'REDIS_QUEUE_KEYS', [])

if DEFAULT_REDIS_QUEUE_KEY not in REDIS_QUEUE_KEYS:
    REDIS_QUEUE_KEYS.append(DEFAULT_REDIS_QUEUE_KEY)


ALLOWED_EXTENSIONS = getattr(settings, 'ALLOWED_EXTENSIONS',
                             ['.pdf', '.jpeg', '.jpg', '.doc', '.docx', '.xls',
                              '.xlsx', '.odt', '.ods', '.ppt', '.pptx', '.odp',
                              '.png', '.gif', '.txt'])

PREVIEW_SIZES = getattr(settings, 'PREVIEW_SIZES',
                        {'150': 'small', '750': 'normal', '1000': 'large'})
CROP_SIZE = getattr(settings, "CROP_SIZE", 12)  # In percents (%)

PREFIX_URL = getattr(settings, 'PREFIX_URL', 'http://localhost/viewer_cache')
DOCVIEWER_SUFFIX = getattr(settings, 'DOCVIEWER_SUFFIX',
                           'document_{size}_p{page}.png')
TEMP_DIRECTORY = getattr(settings, 'TEMP_DIRECTORY', '/tmp')
DESTINATION_ROOT = getattr(settings, 'DESTINATION_ROOT',
                           os.path.join(TEMP_DIRECTORY, 'previews'))

SENTRY_DSN = getattr(settings, 'SENTRY_DSN', None)

STORAGE_CLASS = getattr(settings, 'STORAGE_CLASS',
                        'insight_reloaded.storage.file_system:'
                        'FileSystemStorage')  # FS or S3

# Amazon S3

S3_ACCESS_KEY = getattr(settings, 'S3_ACCESS_KEY', None)
S3_SECRET_KEY = getattr(settings, 'S3_SECRET_KEY', None)
S3_BUCKET_NAME = getattr(settings, 'S3_BUCKET_NAME', 'insight-previews-test')

# Rackspace cloudfiles

CLOUDFILES_USERNAME = getattr(settings, 'CLOUDFILES_USERNAME', None)
CLOUDFILES_API_KEY = getattr(settings, 'CLOUDFILES_API_KEY', None)
CLOUDFILES_COUNTAINER = getattr(settings, 'CLOUDFILES_COUNTAINER',
                                'insight-previews-test')
CLOUDFILES_SERVICENET = getattr(settings, 'CLOUDFILES_SERVICENET', False)
CLOUDFILES_DEFAULT_REGION = getattr(settings, 'CLOUDFILES_DEFAULT_REGION', 'LON')
