from __future__ import print_function
import httplib2

from apiclient import discovery
import creds

#time to stop
_MAX_COUNT = 2000

def get_service():
    credentials = creds.get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('drive', 'v3', http=http)



def read_chunk(service, continuation_token):
    return service.files().list(
        pageSize=100, pageToken=continuation_token,
        fields="nextPageToken, files(id, name, size, md5Checksum)"
        ).execute()

def main():
    """Shows basic usage of the Google Drive API.
        
        Creates a Google Drive API service object and outputs the names and IDs
        for up to 10 files.
        """
    verbose = False #TODO: Read from flag
    service = get_service()
    count = 0
    no_checksum_count = 0
    all_docs = {}
    
    #TODO: add meters
    #TODO: better logging
    results = read_chunk(service, None)
    done = False
    while not done:
        items = results.get('files', [])
        
        if items:
            count += len(items)
            for item in items:
                if verbose:
                    print(u'{0} -> {1}'.format(item['name'], item))
                checksum = item.get('md5Checksum')
                if (checksum):
                    if (not all_docs.has_key(checksum)):
                        all_docs[checksum] = []
                    all_docs[checksum] += [item]
                    if verbose:
                        print(u'added doc id={0} {1}'.format(item['id'], item['name']))
                else:
                    #TODO: Try to guess. If it is a Google doc, compare contents?
                    no_checksum_count += 1
                    print(u'WARNING: doc has no checksum: {0}'.format(item))
        next_page_token = results.get('nextPageToken')
        done = not (next_page_token and count < _MAX_COUNT)
        results = read_chunk(service, next_page_token)

        print ('processed: {0}...'.format(count))

    dups = [all_docs[key] for key in all_docs if len(all_docs[key]) > 1]

    print("""
===============
Finished. Processed files: {0}
Found duplicate suspects: {1}
Files without checksum skipped: {2}
===============
"""
          .format(count, len(dups), no_checksum_count))
    print ('\n====\nDUPS: \n')

    #TODO: Eliminate more false positives.
    #TODO: print path in Drive.
    #TODO: always write to file. Separate from log info.
    for dup in dups:
        print(u"found {0} duplicates for {1}".format(len(dup), dup[0]['name']))
        for item in dup:
            print(u"\t{0}".format(item))



   
if __name__ == '__main__':
    main()
