def Validate(userInput):
    userInput = "".join(userInput.split())
    if userInput != "":
        if userInput != "x":
            userInput = userInput.replace(",", "")
            userInput = userInput.replace("x", "*")
            userInput = userInput.replace("X", "*")
            try:
                return int(userInput)
            except ValueError:
                for char in userInput:
                    if char not in "0123456789+-*/.":
                        return False
                try:
                    return int(eval(userInput))
                except ValueError:
                    return False
        return "x"
    return False


def Request(funds, message):
    while True:
        userInput = Validate(str(input(message)))
        if userInput == "x":
            return "x"
        elif userInput > 0:
            if funds != "N/A" and userInput > funds:
                print("Insufficient Funds: You only have", funds, "credits.")
            else:
                return userInput
        else:
            print("Invalid Input: Please enter a positive integer.")
        print("Type (x) if you want to cancel.")


def RequestStart():
    return Request("N/A", "How many credits are you starting with?\n\t")

def RequestGame(funds):
    return Request(funds, "How many credits are you using to\n" +
                          "\tante into the Game Pot?\n\t")

def RequestSabacc(funds):
   return Request(funds, "How many credits are you using to\n" +
                         "\tante into the Sabacc Pot?\n\t")

def RequestFee(funds):
    return Request(funds, "How many total credits did you pay as a\n" +
                          "\tfee during the previous Draw Phase?\n\t")

def RequestOpen(funds):
    return Request(funds, "How many credits would you like to open with?\n\t")

def RequestCall(funds):
    return Request(funds, "How many credits would you like to call with?\n\t")

def RequestRaise(funds):
    return Request(funds, "How many credits would you like to\n" +
                          "\traise the highest bet to?\n" +
                          "(Enter only the amount that you have not\n" +
                          "\tyet paid in the current betting phase.)\n\t")

def RequestGamePot():
    return Request("N/A", "How many total credits did your\n" +
                          "\topponents pay into the\n" +
                          "\tGame Pot?\n\t")

def RequestSabaccPot():
    return Request("N/A", "How many total credits did your\n" +
                          "\topponents pay into the\n" +
                          "\tSabacc Pot?\n\t")


def RequestAnte():
    return (input("\nPlease type the letter of your chosen action:\n" +
                  "\tAnte/Buy In (a)\n"+
                  "\tQuit (q)\n\t")).lower()

def RequestBetting():
    return (input("\nPlease type the letter of your chosen bet:\n" +
                  "\tDraw Phase Fee (d)\n" +
                  "\tPass/Check (p)\n" +
                  "\tOpen/Bet (o)\n" +
                  "\tCall/See (c)\n" +
                  "\tRaise (r)\n" +
                  "\tFold/Junk (f)\n" +
                  "\tEnd Round (e)\n" +
                  "\tQuit (q)\n\t")).lower()

def RequestBankrupt():
    return (input("\nPlease type the letter of your chosen bet:\n" +
                  "\tPass/Check (p)\n" +
                  "\tFold/Junk (f)\n" +
                  "\tEnd Round (e)\n" +
                  "\tQuit (q)\n\t")).lower()

def RequestWinner():
    return (input("\nPlease type the letter of the round result:\n" +
                  "\tYou Won (y)\n" +
                  "\tOpponent Won (o)\n" +
                  "\tQuit (q)\n\t")).lower()

def RequestHand():
    return (input("\nPlease type the letter of the winning hand:\n" +
                  "\tSabacc (s)\n" +
                  "\tNulrhek (n)\n" +
                  "\tQuit (q)\n\t")).lower()

def RequestProceed():
    return (input("\nPlease type the letter of the chosen action:\n" +
                  "\tNext Round (n)\n" +
                  "\tSingle Blind Card Draw (s)\n" +
                  "\tQuit (q)\n\t")).lower()

def RequestOver():
    input("Game Over.")
    exit()


def DisplaySelection():
    print("Invalid Selection: Please select\n\tan available option.")

def DisplayFunds(funds):
    if funds != 1:
        print("You now have", funds, "credits.")
    else:
        print("You now have", funds, "credit.")

def DisplayGamePot(gamePot):
    print("Notify the winner that you paid\n\t" +
          str(gamePot) + " credits into the\n" +
          "\tGame Pot.")

def DisplaySabaccPot(sabaccPot):
    print("Notify the winner that you paid\n\t" +
          str(gamePot) + " credits into the\n" +
          "\tSabacc Pot.")

def DisplayEliminated():
    print("You have been eliminated from the game and\n" +
          "\tcleaned out of all your credits!")
