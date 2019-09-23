from os import path, getcwd
from sys import path as syspath
from importlib import import_module

try:
    version = (path.basename(__file__)[15:-3]).replace(".", "u")

    directory = "source/" + version + "/"

    if getcwd() == "/storage/emulated/0/qpython":
        directory = "CroupierDroid/" + directory

    syspath.append(directory)

    module = import_module("__init__")

    module.Main()
except Exception as error:
    input("ERROR! " + str(error))
