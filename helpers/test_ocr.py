import unittest

from .ocr import is_commercial_text, sequenceize

class TestSequenceize(unittest.TestCase):
    def test_sequenceize_n4(self):
        self.assertEqual([('',)], sequenceize(None, ns=[4]))
        self.assertEqual([('',)], sequenceize('', ns=[4]))
        self.assertEqual([('abc',)], sequenceize('abc', ns=[4]))
        self.assertEqual([('abc def',)], sequenceize('abc def', ns=[4]))
        self.assertEqual([('abc def ghi',)], sequenceize('abc def ghi', ns=[4]))
        self.assertEqual([('abc def ghi jkl',)], sequenceize('abc def ghi jkl', ns=[4]))
        self.assertEqual([('abc def ghi jkl',), ('def ghi jkl mno',)], sequenceize('abc def ghi jkl mno', ns=[4]))
        self.assertEqual([('abc def ghi jkl',), ('def ghi jkl mno',), ('ghi jkl mno pqr',)], sequenceize('abc def ghi jkl mno pqr', ns=[4]))
        self.assertEqual([('abc def ghi jkl',), ('def ghi jkl mno',), ('ghi jkl mno pqr',)], sequenceize('abc def ghi\njkl mno pqr', ns=[4]))
        self.assertEqual([('abc def ghi jkl',), ('def ghi jkl mno',), ('ghi jkl mno pqr',)], sequenceize('abc def ghi jkl mno\npqr', ns=[4]))
        self.assertEqual([('abc def ghi jkl',), ('def ghi jkl mno',), ('ghi jkl mno pqr',)], sequenceize('abc def ghi\njkl mno\npqr', ns=[4]))
    
    def test_sequenceize_n34(self):
        self.assertEqual([('abc def ghi',), ('def ghi jkl',), ('abc def ghi jkl',)], sequenceize('abc def ghi jkl', ns=[3, 4]))
        self.assertEqual([('abc def ghi',), ('def ghi jkl',), ('ghi jkl mno',), ('jkl mno pqr',), ('abc def ghi jkl',), ('def ghi jkl mno',), ('ghi jkl mno pqr',)], sequenceize('abc def ghi jkl mno pqr', ns=[3, 4]))

    def test_sequenceize_n234(self):
        self.assertEqual([('abc def',), ('def ghi',), ('ghi jkl',), ('abc def ghi',), ('def ghi jkl',), ('abc def ghi jkl',)], sequenceize('abc def ghi jkl'))
        self.assertEqual([('abc def',), ('def ghi',), ('ghi jkl',), ('jkl mno',), ('mno pqr',), ('abc def ghi',), ('def ghi jkl',), ('ghi jkl mno',), ('jkl mno pqr',), ('abc def ghi jkl',), ('def ghi jkl mno',), ('ghi jkl mno pqr',)], sequenceize('abc def ghi jkl mno pqr'))

class TestIsCommercialText(unittest.TestCase):
    def test_test(self):
        self.assertTrue(is_commercial_text([['commercial break in progress']]))
        self.assertTrue(is_commercial_text([['conmercial break in progress']]))
        self.assertTrue(is_commercial_text([['commercial break']]))
        self.assertTrue(is_commercial_text([['c0mercial break']]))
        self.assertTrue(is_commercial_text([['break in progress']]))
        self.assertTrue(is_commercial_text([['break ln proqress']]))


if __name__ == '__main__':
    unittest.main()