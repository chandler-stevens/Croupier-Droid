def Start():
    return int(input("How many credits are you starting with?\n"))

def Action(funds):
    choice = (input("\nPlease type and enter an action:\n"+
                    "\tAnte/Buy In (a)\n"+
                    "\tPass/Check (p)\n"+
                    "\tOpen/Bet (o)\n"+
                    "\tCall/See (c)\n"+
                    "\tRaise (r)\n"+
                    "\tFold/Junk (f)\n"+
                    "\tWin (w)\n"+
                    "\tQuit/End Game (q)\n")).lower()
    if (choice == "a"):
        gamePotAnte = int(input("\nHow many credits are you using to ante into the Game Pot?\n"))
        sabaccPotAnte = int(input("\nHow many credits are you using to ante into the Sabacc Pot?\n"))
        funds -= gamePotAnte + sabaccPotAnte
    elif (choice == "o"):
        funds -= int(input("\nHow many credits would you like to open with?\n"))
    elif (choice == "c"):
        funds -= int(input("\nHow many credits would you like to call with?\n"))
    elif (choice == "r"):
        funds -= int(input("\nHow many total credits would you like to raise the highest bet to?\n"))
    elif (choice == "w"):
        funds += int(input("\nHow many more credits did you win?\n"))
    elif (choice == "q"):
        return choice
    return funds

def Main():
    funds = Start()
    while funds > 0:
        funds = Action(funds)
        if (funds != "q"):
            if (funds != 1):
                print("\nYou now have", funds, "credits remaining.\n")
            else:
                print("\nYou now have", funds, "credit remaining.\n")
        else:
            input("Game Over.")
            return 0
    print("You have been cleaned out of all your credits!")
    if (funds < 0):
        funds = abs(funds)
        if (funds != 1):
            print("You owe the house", funds, "credits of debt!")
        else:
            print("You owe the house", funds, "credit of debt!")
    input("Game Over.")
    return 0

Main()
