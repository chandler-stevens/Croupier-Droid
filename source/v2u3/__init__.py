# Purpose: Launch specific version of Croupier Droid program
# Parameters: Program version (string), import_module (module)
# Returns: None
def LaunchClient(version, import_module):
    try:
        # Import client version module
        module = import_module("DroidClient" + version)
        # Run Play function in client version module
        module.Play(version, import_module)
    # Capture any runtime errors
    except Exception as error:
        input("ERROR! " + str(error))


# Purpose: Launch specific version of Mainframe program
# Parameters: Program version (string), import_module (module)
# Returns: None
def LaunchServer(version, import_module):
    try:
        # Import server version module
        module = import_module("DroidServer" + version)
        # Run Setup function in server version module
        module.Setup(version, import_module)
    # Capture any runtime errors
    except Exception as error:
        input("ERROR! " + str(error))
