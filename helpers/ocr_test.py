import unittest

from ocr import is_commercial_text

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