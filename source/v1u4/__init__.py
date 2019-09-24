# Purpose: Launch specific version of Croupier Droid program
# Parameters: Program version (string), import_module (module)
# Returns: None
def Launch(version, import_module):
    try:
        # Import primary version module
        module = import_module("DroidModel" + version)
        # Run Play function in primary version module
        module.Play(version, import_module)
    # Capture any runtime errors
    except Exception as error:
        input("ERROR! " + str(error))
