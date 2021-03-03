import argparse
import hashlib
import os
import pathlib

def parse():
    parser = argparse.ArgumentParser(description='File duplicates')
    parser.add_argument("-s", "--source", default=pathlib.Path(__file__).resolve().parent, required=False, type=str, help='source folder')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()

    return pathlib.Path(args.source).resolve()

def main():
    source = parse()
    print("Scanning folder: {}".format(source))
    scan = Scan(source)
    #scan.file_full_list()
    scan.check_duplicates()
    scan.mark_to_keep()
    #scan.file_to_be_deleted_list()
    scan.delete()

class Scan: 

    def __init__(self, path):
        self.path = path
        self.file_list = []
        self.duplicates = {}
        self._scan()

    def _scan(self):
        self.file_list = [File(x) for x in pathlib.Path(self.path).iterdir() if x.is_file()]
   
    def check_duplicates(self):
        duplicates = {}
        for file in self.file_list:
            duplicates[file.checksum] = duplicates.get(file.checksum, []) + [file]
        
        self.duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    
    def mark_to_keep(self):
        for k, v in self.duplicates.items():
            print("- Checksum: {}".format(k))
            for index, file in enumerate(v):
                print("{}: {}".format(index, file))
            print("What file do you want to keep?")
            choice = input("Index: ")
            del(self.duplicates[k][int(choice)])

    def delete(self):
        for k, v in self.duplicates.items():
            for file in v:
                if os.path.exists(file.path):
                    print("Removing {}".format(file.path))
                    # os.remove(file.path)

    def file_full_list(self):
        print("Files full list:")
        for file in self.file_list:
            print(file.__repr__())
    
    def file_to_be_deleted_list(self):
        print("Files to be deleted:")
        for k, v in self.duplicates.items():
            for file in v:
                print(file.__repr__())
            
class File:
    def __init__(self, file):
        md5_hash = hashlib.md5()
        fh = open(file, "rb")
        content = fh.read()
        md5_hash.update(content)

        self.path = file
        self.name = pathlib.Path(file).name
        self.extension = pathlib.Path(file).suffix
        self.size = pathlib.Path(file).stat().st_size
        self.checksum = md5_hash.hexdigest()

    def __repr__(self):
        return "File(path={}, name={}, extension={}, size={}, checksum={})".format(self.path, self.name, self.extension, self.size, self.checksum)

if __name__ == "__main__":
    main()