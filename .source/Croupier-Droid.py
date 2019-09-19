from os import path
from warnings import filterwarnings
filterwarnings("ignore", category=DeprecationWarning)
from imp import load_module, PY_SOURCE

version = path.basename(__file__)[15:-3]

directory = ".source/" + version + "/"

if path.isdir("/storage"):
    directory = "CroupierDroid/" + directory

package = directory + "__init__.py"

with open(package, "rb") as fp:
    module = load_module(directory, fp, package, (".py", "rb", PY_SOURCE))
    
module.Main()
