try:
    # Import OS directory modules
    from os.path import basename, isdir
    # Import regex module
    from re import search
    # Determine current version
    version = search("v[0-9]+\.[0-9]+", basename(__file__)).group().replace(".", "u")

    # Determine version's directory
    directory = "source/" + version + "/"
    # Account for QPython working directory
    if isdir("/storage"):
        directory = "CroupierDroid/" + directory

    # Import path marker module
    from sys import path
    # Import version's source code
    path.append(directory)

    # Import importer module
    from importlib import import_module
    # Import version initialziation module
    initialize = import_module("__init__")

    # Launch version
    if version.startswith("v2u"):
        initialize.LaunchServer(version, import_module)
# Capture any runtime errors
except Exception as error:
    input("ERROR! " + str(error))
