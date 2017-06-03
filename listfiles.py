from __future__ import print_function

import os
import httplib2
from apiclient import discovery
import argparse
import logging

import creds

flags = argparse.ArgumentParser().parse_args()

# time to stop
_MAX_COUNT = 10000

# Page size for API list call
_PAGE_SIZE = 500;

account_name = 'quickstart'

_LOG_FILENAME = 'listfiles.log'
_LOG_FILE_PATH = 'log'

if not os.path.exists(_LOG_FILE_PATH):
    os.makedirs(_LOG_FILE_PATH)

logging.basicConfig(filename='%s/%s' % (_LOG_FILE_PATH, _LOG_FILENAME), level=logging.DEBUG)


class ItemKey(object):
    """Type representing a key generated from the item. Suspected duplicates will have same key."""

    def __init__(self, item):
        self.md5Checksum = item.get('md5Checksum')
        self.name = item.get('name')
        # self.size = item.get('size')
        self.mimeType = item.get('mimeType')
        self.originalFilename = item.get('originalFilename')

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def __ne__(self, other):
        return self.__str__() != other.__str__()

    def __hash__(self):
        return hash(self.__str__())


class FileLister(object):
    """Utility to find and list files in Google drive, detecting duplicates."""

    def __init__(self, service=None, account_name="quickstart"):
        """Service: use None for actual drive service, or pass a mock."""
        self._service = service
        self._count = 0
        self._no_key_count = 0
        if service == None:
            self._service = self.connect(account_name)

    def connect(self, account_name):
        """Connects to Google Drive."""
        credentials = creds.get_credentials(account_name)
        http = credentials.authorize(httplib2.Http())
        return discovery.build('drive', 'v3', http=http)

    def read_chunk(self, continuation_token):
        """Reads a page of from the list results."""
        return self._service.files().list(
            pageSize=_PAGE_SIZE, pageToken=continuation_token,
            includeTeamDriveItems=False,
            corpora="user",
            spaces="drive",
            fields="nextPageToken, files(id, name, size, md5Checksum, mimeType, fullFileExtension, originalFilename,"
                   "description, modifiedTime, trashed, parents)"
        ).execute()

    def get_item(self, id):
        """Finds the item by fileId and returns it's name and parent's fileId."""
        return self._service.files().get(fileId=id, fields='parents,name').execute()

    # TODO: @memoize
    def build_path(self, id):
        """Builds path of the containing folder by the folder's fileId."""
        parents = []
        folder = self.get_item(id)
        while folder.get('parents'):
            parents.insert(0, folder.get('name'))
            parentId = folder.get('parents')[0]
            folder = self.get_item(parentId)
        return '/' + '/'.join(parents)

    def load_all_files(self):
        """Loads all docs from the drive.
         
        :return dictionary of lists of docs by the keys.
        """
        self._count = 0
        self._no_key_count = 0
        all_docs = {}

        # TODO: add stats
        next_page_token = None
        done = False
        while not done:
            results = self.read_chunk(next_page_token)
            self.insert_items(all_docs, results.get('files', []))
            next_page_token = results.get('nextPageToken')
            done = not (next_page_token and self._count < _MAX_COUNT)
        return all_docs

    def need(self, item):
        """Returns a boolean whether to keep the item."""
        return not item['trashed'] and not item['mimeType'] == 'application/vnd.google-apps.document'

    def insert_items(self, all_docs, items):
        if not items:
            logging.debug(u'No more items.')
            return
        logging.debug(u'Inserting {0} items.'.format(len(items)))
        self._count += len(items)
        for item in items:
            if not self.need(item):
                logging.debug(u'Ignoring: {0} -> {1}'.format(item['name'], item))
                continue
            logging.debug(u'{0} -> {1}'.format(item['name'], item))
            key = ItemKey(item)
            if key:
                if not all_docs.has_key(key):
                    all_docs[key] = []
                all_docs[key] += [item]
                logging.debug(u'added doc id={0} {1}'.format(item['id'], item['name']))
            else:
                self._no_key_count += 1

    def find_dups(self, all_docs):
        """Loads all files from the drive, finds duplicate susptects."""
        logging.info(u'Started findDups')
        dups = [all_docs[key] for key in all_docs if len(all_docs[key]) > 1]
        logging.info(u'Done findDups')
        return dups

    def get_report(self):
        fmt = """
===============
Finished. Processed files: {0}
Found duplicate suspects: {1}
Skipped - cannot generate key: {2}
===============

=====
DUPS: 
=====
{3}
=====
"""
        all_dups = self.find_dups(self.load_all_files())
        report_lines = ""
        for file_dups in all_dups:
            name = file_dups[0]['name']
            print(u'found {0} duplicates for {1}'.format(len(file_dups), name))
            report_lines += u'** {0}\n'.format(name)
            for item in file_dups:
                path = self.build_path(item['id'])
                report_lines += u'\t{0}\n'.format(path)
        return fmt.format(self._count, len(all_dups), self._no_key_count, report_lines)


def main():
    """Reads files from Google Drive API and tries to identify duplicates."""
    print(FileLister(None).get_report())


if __name__ == '__main__':
    main()
