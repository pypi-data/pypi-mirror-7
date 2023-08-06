from os import makedirs
from os.path import join
from shutil import move
from insight_reloaded.insight_settings import (DESTINATION_ROOT, PREFIX_URL)


class FileSystemStorage(object):

    def __init__(self, document_url, document_hash, destination_root=None,
                 prefix_url=None):
        if not destination_root:
            destination_root = DESTINATION_ROOT
        self.destination_root = destination_root
        self.document_hash = document_hash

        if not prefix_url:
            prefix_url = PREFIX_URL
        self.prefix_url = prefix_url

        self.document_url = document_url

    def prepare(self):
        """Create a unique identifier for the document, create the path
        and return it.
        """
        document_path = join(self.destination_root,
                             string_to_folder_path(self.document_hash))
        try:
            makedirs(document_path)
        except OSError:
            print "%s already exists." % document_path
        self.destination_folder = document_path

    def get_path(self, path):
        return join(self.destination_folder, path)

    def save(self, path, filename):
        move(path, join(self.destination_folder, filename))

    def get_base_document_url(self):
        return self.destination_folder.replace(self.destination_root,
                                               self.prefix_url)


def string_to_folder_path(s):
    """Split a string into 2-char length folders.

    >>> string_to_folder_path('3614816AA000002781')
    '361/481/6AA/000/002/781'

    """
    if s:
        size = len(s) / 3 * 3
        folders = [s[i:i + 3] for i in range(0, size, 3)]
        return join(*folders)
    return ""
