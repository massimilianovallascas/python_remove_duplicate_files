import random
import string
import unittest

from unittest import mock
from unittest.mock import patch

from .test_common import *
from main import *


class ScanCommonTestCase(CommonTestCase):

    recursive = False
    dry_run = True
    choice = "n"

    def setUp(self):
        super().setUp()
        if self.recursive:
            self.test_files["recursive.txt"] = "51037a4a37730f52c8732586d3aaa316"
        self.scan = Scan(self.path_files, self.recursive, self.dry_run)

    def test_scan(self):
        self.assertEqual(len(self.test_files), len(self.scan.file_list))
        for file in self.scan.file_list:
            self.assertIn(file.name, self.test_files)

    def test_check_duplicates(self):
        self.assertEqual(len(self.scan.duplicates), 0)
        self.scan.check_duplicates()
        self.assertEqual(len(self.scan.duplicates), 1)

    def test_mark_to_keep(self):
        self.scan.check_duplicates()
        with mock.patch("builtins.input", return_value="0"):
            self.scan.mark_to_keep()
            for checksum, files in self.scan.duplicates.items():
                self.assertEqual(len(files), 1)
                self.assertEqual(files[0].name, "text.txt")

    def test_delete_no_dry_run(self):
        self.scan.check_duplicates()
        with mock.patch("builtins.input", return_value="0"):
            self.scan.mark_to_keep()
            if self.dry_run:
                with mock.patch("builtins.input", return_value=random.choice(string.ascii_letters)):
                    self.scan.delete()
            else:
                if self.choice == "n":
                    with mock.patch("builtins.input", return_value="n"):
                        with self.assertRaises(SystemExit) as se:
                            self.scan.delete()
                            self.assertEqual(se.exception, 1)
                if self.choice == "y":
                    file = os.path.join(self.path_files, "text.txt")
                    self.assertTrue(os.path.isfile(file))
                    with mock.patch("builtins.input", return_value="y"):
                        self.scan.delete()
                    
                    self.assertFalse(os.path.isfile(file))


class ScanDTestCase(ScanCommonTestCase):
    def setUp(self):
        self.recursive = False
        self.dry_run = True
        super().setUp()


class ScanRDTestCase(ScanCommonTestCase):
    def setUp(self):
        self.recursive = True
        self.dry_run = True
        super().setUp()


class ScanRTestCase(ScanCommonTestCase):
    def setUp(self):
        self.recursive = True
        self.dry_run = False
        self.choice = "n"
        super().setUp()


class ScanTestCase(ScanCommonTestCase):
    def setUp(self):
        self.recursive = False
        self.dry_run = False
        self.choice = "y"
        super().setUp()


del(ScanCommonTestCase)


if __name__ == '__main__':
    unittest.main()
