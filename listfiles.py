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
        self.size = item.get('size')
        self.mimeType = item.get('mimeType')
        self.originalFilename = item.get('originalFilename')

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ListFiles(object):
    def __init__(self, service=None, account_name="quickstart"):
        """Service: use None for actual drive service, or pass a mock."""
        self._service = service
        if service == None:
            self._service = self.connectToDrive(account_name)

    def connectToDrive(self, account_name):
        credentials = creds.get_credentials(account_name)
        http = credentials.authorize(httplib2.Http())
        return discovery.build('drive', 'v3', http=http)

    def readChunk(self, continuation_token):
        return self._service.files().list(
            pageSize=_PAGE_SIZE, pageToken=continuation_token,
            includeTeamDriveItems=False,
            corpora="user",
            spaces="drive",
            fields="nextPageToken, files(id, name, size, md5Checksum, mimeType, fullFileExtension, originalFilename,"
                   "description, modifiedTime, trashed, parents)"
        ).execute()

    def getItem(self, id):
        """Finds item by fileId and returns it's name and parent's fileId."""
        return self._service.files().get(fileId=id, fields='parents,name').execute()

    # TODO: @memoize
    def getPath(self, id):
        """Builds path of the containing folder by the folder's fileId."""
        parents = []
        folder = self.getItem(id)
        while folder.get('parents'):
            parents.insert(0, folder.get('name'))
            parentId = folder.get('parents')[0]
            folder = self.getItem(parentId)
        return '/' + '/'.join(parents)

    def loadDocs(self):
        """Loads all docs from the drive.
         
         :return list of docs.
         """
        count = 0
        no_key_count = 0
        all_docs = {}

        # TODO: add meters
        next_page_token = None
        done = False
        while not done:
            results = self.readChunk(next_page_token)
            items = results.get('files', [])

            if items:
                count += len(items)
                for item in items:
                    if not self.need(item):
                        continue
                    logging.debug(u'{0} -> {1}'.format(item['name'], item))
                    key = ItemKey(item)
                    if key:
                        if not all_docs.has_key(key):
                            all_docs[key] = []
                        all_docs[key] += [item]
                        logging.debug(u'added doc id={0} {1}'.format(item['id'], item['name']))
                    else:
                        no_key_count += 1
            next_page_token = results.get('nextPageToken')
            done = not (next_page_token and count < _MAX_COUNT)

        return all_docs, count, no_key_count

    def findDups(self):
        """Loads all files from the drive, finds duplicate susptects."""
        all_docs, count, no_key_count = self.loadDocs()
        dups = [all_docs[key] for key in all_docs if len(all_docs[key]) > 1]

        logging.info("Finished")
        return dups, count, no_key_count

    def need(self, item):
        """Returns a boolean whether to keep the item."""
        return not item['trashed'] and not item['mimeType'] == 'application/vnd.google-apps.document'


def printDups():
    fmt = """
===============
Finished. Processed files: {0}
Found duplicate suspects: {1}
Skipped - cannot generate key: {2}
===============
"""
    lister = ListFiles(None)
    dups, count, no_key_count = lister.findDups()

    print(fmt.format(count, len(dups), no_key_count))
    print('\n====\nDUPS: \n')

    # TODO: Eliminate some false positives.
    # TODO: print path in Drive.
    # TODO: always write to file. Separate from log info.
    for dup in dups:
        print(u"found {0} duplicates for {1}".format(len(dup), dup[0]['name']))
        for item in dup:
            printDup(item, lister.getPath(item['id']))


def printDup(item, path):
    print(u"FILE:{0}\n\tPATH:{1}\n".format(item['name'], path))


def main():
    """Reads files from Google Drive API and tries to identify duplicates."""
    printDups()


if __name__ == '__main__':
    main()
