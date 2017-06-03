import unittest
from unittest import TestCase
from listfiles import ListFiles
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


class Test_listfiles(TestCase):

    def test_ItemKey_eq(self):
        ki1 = ItemKey(ITEM1)
        ki2 = ItemKey(ITEM1A)
        self.assertEqual(ki1, ki2)

    def test_ItemKey_neq(self):
        ki1 = ItemKey(ITEM1)
        ki2 = ItemKey(ITEM2)
        self.assertNotEqual(ki1, ki2)

    def test_ItemKey_eq_nomdsum(self):
        ki1 = ItemKey(ITEM3)
        ki2 = ItemKey(ITEM3A)
        self.assertEqual(ki1, ki2)

    def test_ListFiles_path(self):
        id = u'0BylQJTWU7tFzRXdHYmV5dEF2azA'
        expected = u'/Stuff/freeciv-server.png'
        service = ListFiles()
        actual = service.getPath(id)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()