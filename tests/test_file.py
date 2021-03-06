import os
import unittest

from .test_common import *
from main import *


class FileTestCase(CommonTestCase):

    def setUp(self):
        super().setUp()
        self.file = [ File(os.path.join(self.path_files, file)) for file in self.test_files.keys() ]

    def test_file_checksum(self):
        for file in self.file:
            self.assertEqual(file.checksum, self.test_files[file.name])

    def test_repr(self):
        for file in self.file:
            self.assertEqual(file.path, os.path.join(self.path_files, file.name))
            self.assertEqual(file.checksum, self.test_files[file.name])
            self.assertIn(file.name, self.test_files)


if __name__ == '__main__':
    unittest.main()
