import unittest
from unittest import TestCase
from listfiles import FileLister
from listfiles import ItemKey

ITEM1 = {
    u'mimeType': u'text/plain',
    u'md5Checksum': u'a6e952b763e16a7dc6e8772e5a90f1c5',
    u'name': u'some_file.txt',
    u'modifiedTime': u'2017-05-22T01:50:45.610Z',
    u'fullFileExtension': u'txt',
    u'parents': [u'PARENT1'],
    u'originalFilename': u'italy-movie-notes.txt',
    u'id': u'0BylQJTWU7tFzeTlMRDIzQTdPNFE',
    u'trashed': False,
    u'size': u'83'
}

ITEM1A = {
    u'mimeType': u'text/plain',
    u'md5Checksum': u'a6e952b763e16a7dc6e8772e5a90f1c5',
    u'name': u'some_file.txt',
    u'modifiedTime': u'2017-05-22T01:50:45.610Z',
    u'fullFileExtension': u'txt',
    u'parents': [u'PARENT2'],
    u'originalFilename': u'italy-movie-notes.txt',
    u'id': u'0BylQJTWU7tFzeTlMRDIzQTdPNFE',
    u'trashed': False,
    u'size': u'83'
}

ITEM2 = {
    u'mimeType': u'text/plain',
    u'md5Checksum': u'a6e952b763e16a7dc6e8772e5a90f1c6',
    u'name': u'some_file.txt',
    u'modifiedTime': u'2017-05-22T01:50:45.610Z',
    u'fullFileExtension': u'txt',
    u'parents': [u'PARENT2'],
    u'originalFilename': u'italy-movie-notes.txt',
    u'id': u'0BylQJTWU7tFzeTlMRDIzQTdPNFE',
    u'trashed': False,
    u'size': u'83'
}

ITEM3 = {
    u'mimeType': u'text/plain',
    u'name': u'some_file.txt',
    u'modifiedTime': u'2017-05-22T01:50:45.610Z',
    u'fullFileExtension': u'txt',
    u'parents': [u'PARENT3'],
    u'originalFilename': u'italy-movie-notes.txt',
    u'id': u'0BylQJTWU7tFzeTlMRDIzQTdPNFE',
    u'trashed': False,
    u'size': u'83'
}

ITEM3A = {
    u'mimeType': u'text/plain',
    u'name': u'some_file.txt',
    u'modifiedTime': u'2017-05-22T01:50:45.610Z',
    u'fullFileExtension': u'txt',
    u'parents': [u'PARENT4'],
    u'originalFilename': u'italy-movie-notes.txt',
    u'id': u'0BylQJTWU7tFzeTlMRDIzQTdPNFE',
    u'trashed': False,
    u'size': u'83'
}

DUP1 = {u'mimeType': u'image/png', u'md5Checksum': u'b230c3fcb55878f9ccbd1751f4306846', u'name': u'factory.png',
        u'modifiedTime': u'2017-05-22T01:25:39.135Z', u'fullFileExtension': u'png',
        u'originalFilename': u'factory.png', u'id': u'0BylQJTWU7tFzYkM5bTJEOC1WQWs',
        u'trashed': False, u'size': u'5014',
        u'parents': [u'0BylQJTWU7tFzQUpWTUxBdVdPTVk']}
DUP2 = {u'mimeType': u'image/png', u'md5Checksum': u'b230c3fcb55878f9ccbd1751f4306846', u'name': u'factory.png',
        u'modifiedTime': u'2017-05-22T01:25:36.313Z', u'fullFileExtension': u'png',
        u'originalFilename': u'factory.png', u'id': u'0BylQJTWU7tFzVVpmZEhBNlY0dFU',
        u'trashed': False, u'size': u'5014',
        u'parents': [u'0AClQJTWU7tFzUk9PVA']}


class Test_listfiles(TestCase):
    # Unit testing

    def test_ItemKey_eq(self):
        ki1 = ItemKey(DUP1)
        ki2 = ItemKey(DUP2)
        self.assertEqual(ki1, ki2)

    def test_ItemKey_neq(self):
        ki1 = ItemKey(ITEM1)
        ki2 = ItemKey(ITEM2)
        self.assertNotEqual(ki1, ki2)

    def test_ItemKey_eq_nomdsum(self):
        ki1 = ItemKey(ITEM3)
        ki2 = ItemKey(ITEM3A)
        self.assertEqual(ki1, ki2)

    # Integration testing

    def test_FileLister_path(self):
        id = u'0BylQJTWU7tFzRXdHYmV5dEF2azA'
        expected = u'/Stuff/freeciv-server.png'
        service = FileLister()
        actual = service.build_path(id)
        self.assertEqual(expected, actual)

    def test_FileLister_find_dups(self):
        all_docs = {}
        items = [DUP1, DUP2]
        FileLister().insert_items(all_docs, items)
        self.assertEqual(len(all_docs.keys()), 1)


if __name__ == '__main__':
    unittest.main()
