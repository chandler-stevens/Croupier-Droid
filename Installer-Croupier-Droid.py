from os import path, getcwd, chdir, walk, mkdir, remove
from zipfile import ZipFile
from shutil import move, rmtree
from urllib import request
from re import findall
import ssl

# Bypass SSL certificate errors
ssl._create_default_https_context = ssl._create_unverified_context

print("Downloading updates ...")

# Determine supported OS version
if path.isdir("C:"):
    installPath = "C:"
elif path.isdir("/storage/emulated/0/qpython"):
    installPath = "/storage/emulated/0/qpython"
else:
    input("Error! Expected either 'C:' Windows\n" +
          "\tdirectory to exist or\n" +
          "\t'/storage/emulated/0/qpython'\n" +
          "\tdirectory to exist!")
    exit()

installPath += "/CroupierDroid"

# Create source directory if necessary
if not path.isdir(installPath):
    mkdir(installPath)
    mkdir(installPath + "/.source/")

# Navigate to source directory
chdir(installPath + "/.source")

# Download repo as ZIP file
request.urlretrieve("https://github.com/chandler-stevens/Croupier-Droid/archive/master.zip", "./Croupier-Droid-master.zip")

# Extract ZIP file
repo = ZipFile("Croupier-Droid-master.zip", "r")
repo.extractall("./")
repo.close()

print("Installing updates ...")
# Declare source and destination directory
source = "./Croupier-Droid-master/" + version[0:version.find(".")] + "/" + version
destination = "./" + version
# Move/Overwrite all version files
for src_dir, dirs, files in walk(source):
    # Determine destination path
    dst_dir = src_dir.replace(source, destination)
    # Create destination directory, if necessary
    if not path.exists(dst_dir):
        mkdir(dst_dir)
    # For each new version file
    for file in files:
        # Append filename to source and destination paths
        src_file = path.join(src_dir, file)
        dst_file = path.join(dst_dir, file)
        # Overwrite existing file
        if path.exists(dst_file):
            remove(dst_file)
        # Move file
        move(src_file, dst_dir)
# Remove extracted files
rmtree("./Croupier-Droid-master")
# Remove ZIP file
remove("./Croupier-Droid-master.zip")
input("Successfully installed all updates in\n\t" + installPath)
