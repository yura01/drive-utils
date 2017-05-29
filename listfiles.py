from __future__ import print_function
import os

import httplib2
from apiclient import discovery
import logging

import creds

# time to stop
_MAX_COUNT = 10000

# Page size for API list call
_PAGE_SIZE = 500;

account_name = 'quickstart'

_LOG_FILENAME='listfiles.log'
_LOG_FILE_PATH = 'log'

if not os.path.exists(_LOG_FILE_PATH):
    os.makedirs(_LOG_FILE_PATH)

logging.basicConfig(filename='%s/%s' % (_LOG_FILE_PATH, _LOG_FILENAME), level=logging.DEBUG)

def get_service():
    credentials = creds.get_credentials(account_name)
    http = credentials.authorize(httplib2.Http())
    return discovery.build('drive', 'v3', http=http)


def read_chunk(service, continuation_token):
    return service.files().list(
        pageSize=_PAGE_SIZE, pageToken=continuation_token,
        includeTeamDriveItems=False,
        corpora="user",
        spaces="drive",
        fields="nextPageToken, files(id, name, size, md5Checksum, mimeType, fullFileExtension, originalFilename,"
               "description, modifiedTime, trashed, parents)"
        ).execute()


def getItem(id):
    """Finds item by fileId and returns it's name and parent's fileId."""
    return service.files().get(fileId=id, fields='parents,name').execute()


#TODO: @memoize
def getPath(id):
    """Builds path of the containing folder by the folder's fileId."""
    parents = []
    folder = getItem(id)
    while folder.get('parents') != [id]:
        parents.insert(0, folder.get('name'))
        parentId = folder.get('parents')[0]
        folder = getItem(parentId)
    return '/'.join(parents)


class ItemKey(object):
    def __init__(self, item):
        self.md5Checksum = item.get('md5Checksum')
        self.name = item.get('name')
        self.size = item.get('size')
        self.mimeType = item.get('mimeType')
        self.originalFilename = item.get('originalFilename')


def makeKey(item):
    return ItemKey(item)


def printDup(item):
    path = u"/".join(item['path'])

    print(u"FILE:{0}\n\tPATH:{1}\n".format(item['name'], path))


def main():
    """Reads files from Google Drive API and tries to identify duplicates."""
    service = get_service()
    count = 0
    no_key_count = 0
    all_docs = {}
    
    #TODO: add meters
    results = read_chunk(service, None)
    done = False
    while not done:
        items = results.get('files', [])
        
        if items:
            count += len(items)
            for item in items:
                if item['trashed'] or item['mimeType'] == 'application/vnd.google-apps.document':
                    continue
                logging.debug(u'{0} -> {1}'.format(item['name'], item))
                key = makeKey(item)
                if key:
                    if not all_docs.has_key(key):
                        all_docs[key] = []
                    all_docs[key] += [item]
                    logging.debug(u'added doc id={0} {1}'.format(item['id'], item['name']))
                else:
                    no_key_count += 1
        next_page_token = results.get('nextPageToken')
        done = not (next_page_token and count < _MAX_COUNT)
        results = read_chunk(service, next_page_token)

    dups = [all_docs[key] for key in all_docs if len(all_docs[key]) > 1]
    logging.info("Finished")
    print("""
===============
Finished. Processed files: {0}
Found duplicate suspects: {1}
Skipped - cannot generate key: {2}
===============
"""
          .format(count, len(dups), no_key_count))
    print('\n====\nDUPS: \n')

    #TODO: Eliminate some false positives.
    #TODO: print path in Drive.
    #TODO: always write to file. Separate from log info.
    for dup in dups:
        print(u"found {0} duplicates for {1}".format(len(dup), dup[0]['name']))
        for item in dup:
            printDup(item)

 
if __name__ == '__main__':
    main()
