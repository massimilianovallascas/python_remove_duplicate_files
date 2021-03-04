import argparse
import hashlib
import os
import pathlib
import sys

def parse():
    parser = argparse.ArgumentParser(description="Remove duplicate files")
    parser.add_argument("-d", "--dryrun", default=False, required=False, action="store_true", help="dry run")
    parser.add_argument("-r", "--recursive", default=False, required=False, action="store_true", help="recursive")
    parser.add_argument("-s", "--source", default=pathlib.Path(__file__).resolve().parent, required=False, type=str, help="source folder")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()

    return pathlib.Path(args.source).resolve(), args.recursive, args.dryrun

def main():
    source, recursive, dry_run = parse()
    print("Scanning folder: {}".format(source))
    scan = Scan(source, recursive, dry_run)
    #scan.file_full_list()
    scan.check_duplicates()
    scan.mark_to_keep()
    #scan.file_to_be_deleted_list()
    scan.delete()

class Scan: 

    def __init__(self, path, recursive=False, dry_run=True):
        self.path = path
        self.recursive = recursive
        self.dry_run = dry_run
        self.file_list = []
        self.duplicates = {}
        self._scan()

    def _scan(self):
        pattern = "**/*" if self.recursive else "*"
        files = pathlib.Path(self.path).glob(pattern)
        self.file_list = [File(x) for x in files if x.is_file()]
   
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
        if len(self.duplicates) > 0:
            if not self.dry_run:
                print("*** WARNING")
                print("*** The script is not running in dry-run mode")
                print("*** Please make sure to backup your files before proceed")
                choice = input("Do you want to proceed? [Y/n]: ")
                if choice.lower() != "y":
                    sys.exit(1)

            for k, v in self.duplicates.items():
                for file in v:
                    if os.path.exists(file.path):
                        print("Removing {}".format(file.path))
                        os.remove(file.path)
        else:
            print("No duplicates found")

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