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

    text = f"Scanning folder: {source}"
    print(f"{text}\n{'=' * len(text)}")

    if dry_run:
        print("Running in dryrun mode")

    scan = Scan(source, recursive, dry_run)
    #scan.file_full_list()
    scan.check_duplicates()
    scan.mark_to_keep()
    #scan.file_to_be_deleted_list()
    scan.delete()

class Scan: 

    def __init__(self, path: str, recursive: bool = False, dry_run: bool = True):
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
            choice: int = -1
            print(f"\n*** Checksum: {k} ***")
            for index, file in enumerate(v):
                print(f"{index}: {file}")
            index_range = range(len(v))
            while int(choice) not in index_range:
                choice = input(f"What file do you want to keep? {list(map(str, index_range))}: ")
                try:
                    int(choice)
                except ValueError:
                    choice = -1   
            del(self.duplicates[k][int(choice)])

    def delete(self):
        print("\n")
        if len(self.duplicates) > 0:
            remove_text = "Removing"
            choice = str()
            if self.dry_run:
                text = "*** INFO: The script is running in dry-run mode, files won't be deleted"
                print(f"{text}\n{'=' * len(text)}")
                input("Press any key to continue...")
                remove_text = f"(dry-run) - {remove_text}"
            else:
                text = "*** WARNING: The script is not running in dry-run mode. Please make sure to backup your files before proceeding"
                print(f"{text}\n{'=' * len(text)}")
                while choice.lower() not in ["y","n"]:
                    choice = input("Do you want to proceed? [Y/n]: ")

                if choice.lower() != "y":
                    sys.exit(1)

            for k, v in self.duplicates.items():
                for file in v:
                    if os.path.exists(file.path):
                        print(f"{remove_text} {file.path}")
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
    def __init__(self, file: str):
        self.path = file
        self.name = pathlib.Path(file).name
        self.extension = pathlib.Path(file).suffix
        self.size = pathlib.Path(file).stat().st_size
        self.checksum = self._file_checksum()

    def _file_checksum(self) -> str:
        md5_hash = hashlib.md5()
        fh = open(self.path, "rb")
        content = fh.read()
        fh.close()
        md5_hash.update(content)
        return md5_hash.hexdigest()

    def __repr__(self) -> str:
        return f"File(path={self.path}, checksum={self.checksum}, name={self.name}, extension={self.extension}, size={self.size})"


if __name__ == "__main__":
    main()