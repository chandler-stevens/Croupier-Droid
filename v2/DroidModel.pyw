def Start():
    return input("What is your name?\n"), int(input("How many credits are you starting with?\n"))

def Action(funds):
    choice = (input("\nPlease type and enter an action:\n\tAnte\n\tCheck\n\tOpen\n\tCall\n\tRaise\n\tFold\n\tWin\n")).lower()
    if (choice == "ante" or choice == "a"):
        gamePotAnte = int(input("\nHow many credits are you using to ante into the Game Pot?\n"))
        sabaccPotAnte = int(input("\nHow many credits are you using to ante into the Sabacc Pot?\n"))
        funds -= gamePotAnte + sabaccPotAnte
        result = ("Ante", funds, gamePotAnte, sabaccPotAnte)
    elif (choice == "check" or choice == "p"):
        result = ("Check", funds)
    elif (choice == "open" or choice == "o"):
        openAmount = int(input("\nHow many credits would you like to open with?\n"))
        funds -= openAmount
        result = ("Open", funds, openAmount)
    elif (choice == "call" or choice == "c"):
        callAmount = int(input("\nHow many credits would you like to call with?\n"))
        funds -= callAmount
        result = ("Call", funds)
    elif (choice == "raise" or choice == "r"):
        raiseAmount = int(input("\nHow many more credits would you like to raise the highest bet to?\n"))
        funds -= raiseAmount
        result = ("Raise", funds, raiseAmount)
    elif (choice == "fold" or choice == "f"):
        result = ("Fold", funds)
    elif (choice == "win" or choice == "w"):
        winType = (input("\nDid you win with a Nulrhek or with a Sabacc?\n")).lower()
        if (winType == "nulrhek" or winType == "n"):
            funds += int(input("\nHow many more credits did you win?\n"))
            result = ("Nulrhek", funds)
        elif (winType == "sabacc" or winType == "s"):
            funds += int(input("\nHow many more credits did you win?\n"))
            result = ("Sabacc", funds)
    return result
