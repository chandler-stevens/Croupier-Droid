# Import select modules from OS package
from os import path, getcwd, chdir, mkdir, walk, remove, system, listdir
# Import move/rename module and recursive delete module
from shutil import move, rmtree

# Purpose: Self-update installer/updater and download source code
# Parameters: None
# Returns: None
def UpdateSelf():
    # import ssl package
    import ssl
    # Bypass SSL certificate errors
    ssl._create_default_https_context = ssl._create_unverified_context

    # Capture current working directory
    originalPath = getcwd()

    print("Downloading updates ...")

    # Determine supported OS version
    if path.isdir("C:"):
        installPath = "C:"
    elif path.isdir("/storage/emulated/0/qpython"):
        installPath = "/storage/emulated/0/qpython"
    else:
        input("ERROR! Expected either 'C:' Windows\n" +
              "\tdirectory to exist or\n" +
              "\t'/storage/emulated/0/qpython'\n" +
              "\tdirectory to exist!")
        exit()

    installPath += "/CroupierDroid/"

    # Create install directory if necessary
    if not path.isdir(installPath):
        mkdir(installPath)

    sourcePath = installPath + "source/"

    # Create source directory if necessary
    if not path.isdir(sourcePath):
        mkdir(sourcePath)

    # Navigate to source directory
    chdir(sourcePath)
    
    # Import downloader module and internet error module
    from urllib.request import urlretrieve
    from urllib.error import URLError
    # Download repo as ZIP file
    try:
        urlretrieve("https://github.com/chandler-stevens/Croupier-Droid/archive/master.zip", "./Croupier-Droid-master.zip")
    except URLError:
        input("ERROR! No Internet connection!")
        exit()

    # Import ZIP extractor module
    from zipfile import ZipFile
    # Extract ZIP file
    repo = ZipFile(sourcePath + "Croupier-Droid-master.zip", "r")
    repo.extractall(sourcePath)
    repo.close()
    
    # Retrieve new updater
    move(sourcePath + "Croupier-Droid-master/Install-Croupier-Droid.py", installPath + "Temp.py")
    move(sourcePath + "Croupier-Droid-master/__init__.py", installPath)

    # Import path marker module
    from sys import path as syspath
    # Mark installation path as import location
    syspath.append(installPath)
    
    # Import importer module
    from importlib import import_module
    # Import updater initialization module
    module = import_module("__init__")

    # Install updates
    module.UpdateSource(installPath, sourcePath, originalPath)


# Purpose: Move files and overwrite any existing conflicts
# Parameters: Source path (string), destination path (string)
# Returns: None
def Update(source, destination):
    # Move/Overwrite all version files
    for src_dir, dirs, files in walk(source):
        # Determine destination path
        dst_dir = src_dir.replace(source, destination)
        # Create destination directory if necessary
        if not path.exists(dst_dir):
            mkdir(dst_dir)
        # For each new version file
        for fileName in files:
            # Append filename to source and destination paths
            src_file = path.join(src_dir, fileName)
            dst_file = path.join(dst_dir, fileName)
            # Overwrite existing file
            if path.exists(dst_file):
                remove(dst_file)
            # Move file
            move(src_file, dst_dir)

# Purpose: Updates source code to latest stable version(s)
# Parameters: Installation path (string), installed source path (string), this file's path (string) 
# Returns: None
def UpdateSource(installPath, sourcePath, originalPath):
    # Import regex package
    from re import findall, fullmatch
    
    # Cleanup launchers
    for fileName in listdir(installPath):
        filePath = path.join(installPath, fileName)
        if path.isfile(filePath) and fullmatch("Croupier\-Droid\-v[0-9]+\.[0-9]+\.py", fileName) != None:
            remove(filePath)

    # Cleanup source
    for folder in listdir(sourcePath):
        folderPath = path.join(sourcePath, folder)
        if path.isdir(folderPath) and fullmatch("v[0-9]+u[0-9]+", folder) != None:
            rmtree(folderPath)
    
    # Determine latest stable versions
    versions = []
    with open(sourcePath + "Croupier-Droid-master/README.md") as readme:
        versions = findall("v[0-9]+\.[0-9]+", readme.readlines()[1][25:])

    # Confirm latest stable versions were found
    if len(versions):
        print("Installing updates ...")
        for version in versions:
            Update("Croupier-Droid-master/source/" + version.replace(".", "u"), version.replace(".", "u"))
            move(sourcePath + "Croupier-Droid-master/source/Croupier-Droid.py", installPath + "/Croupier-Droid-" + version + ".py")
            print("Successfully updated", version)
    else:
        input("ERROR! No stable versions found!")

    # Overwrite updater
    if path.isfile(installPath + "Temp.py"):
        move(installPath + "Temp.py", installPath + "Update-Croupier-Droid.py")

    # Remove initialization
    if path.isfile(installPath + "__init__.py"):
        remove(installPath + "__init__.py")

    # Remove extracted files
    if path.isdir(sourcePath + "Croupier-Droid-master"):
        rmtree(sourcePath + "Croupier-Droid-master")

    # Remove caches
    if path.isdir(installPath + "__pycache__"):
        rmtree(installPath + "__pycache__")
    if path.isdir(originalPath + "\__pycache__"):
        rmtree(originalPath + "\__pycache__")

    # Remove ZIP file
    if path.isfile(sourcePath + "Croupier-Droid-master.zip"):
        remove(sourcePath + "Croupier-Droid-master.zip")

    # Hide source code in Windows
    if sourcePath[0] == "C":
        from ctypes import windll
        windll.kernel32.SetFileAttributesW(sourcePath, 2)

    input("Successfully installed all updates in\n" + installPath)


try:
    # Self-update updater if not done so already
    if not path.isfile("C:/CroupierDroid/Temp.py") and not path.isfile("/storage/emulated/0/qpython/CroupierDroid/Temp.py"):
        UpdateSelf()
# Capture any installation errors
except Exception as error:
        input("ERROR! " + str(error))
