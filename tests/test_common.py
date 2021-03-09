import unittest
import shutil

from main import *


class CommonTestCase(unittest.TestCase):

    def setUp(self):
        self.test_files = {
            "image.jpg": "d68e763c825dc0e388929ae1b375ce18",
            "text_copy.txt": "51037a4a37730f52c8732586d3aaa316",
            "text_different.txt": "29e4b66fa8076de4d7a26c727b8dbdfa",
            "text.txt": "51037a4a37730f52c8732586d3aaa316"
        }
        
        self.path_current = pathlib.Path(__file__).resolve().parent
        self.path_files = os.path.join(self.path_current, "files")

        self.tearDown()
        shutil.copytree(f"{self.path_files}_master", self.path_files)
       
    def tearDown(self):
        shutil.rmtree(self.path_files, ignore_errors=True)
