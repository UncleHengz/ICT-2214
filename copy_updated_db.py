
import shutil
import os
import tarfile

def copy_file():
    source_directory = "/home/suibiandeming/ICT-2214/external_database_update/Links"  # Replace this with the actual source directory
    filename_to_check = "ALL-phishing-links.txt"  # Replace this with the actual filename

    source_path = os.path.join(source_directory, filename_to_check)
    if os.path.isfile(source_path):
        shutil.copy(source_path, os.getcwd())
        print(f"File '{filename_to_check}' copied to the current directory.")
    else:
        print(f"File '{filename_to_check}' does not exist in the specified directory.")


if __name__ == '__main__':
    copy_file()
