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
            if str(funds).isdigit() and userInput > funds:
                print("Insufficient Funds: You only have", funds, "credits.")
            elif funds == "rule" and userInput > 4:
                print("Invalid Number: Please enter a valid house rule number.")
            else:
                return userInput
        else:
            print("Invalid Input: Please enter a positive integer.")
        print("Type (x) if you want to cancel.")


def RequestRule():
    return Request("rule",
                   "Please type the number of your chosen house rule:\n" +
                   "\tFort Ypso Lodge (1)\n" +
                   "\tYarith Bespin Casino (2)\n" +
                   "\tRock-Lion Cantina (3)\n" +
                   "\tMos Eisley Cantina (4)\n\t")

def RequestStart():
    return Request("start", "How many credits are you starting with?\n\t")

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

def RequestWin():
    return Request("win", "How many more credits did you win?\n\t")


def RequestAnte():
    return (input("\nPlease type the letter of your chosen action:\n" +
                  "\tAnte/Buy In (a)\n"+
                  "\tQuit (q)\n\t")).lower()

def RequestBetting():
    return (input("\nPlease type the letter of your chosen action:\n" +
                  "\tDraw Phase Fee (d)\n" +
                  "\tPass/Check (p)\n" +
                  "\tOpen/Bet (o)\n" +
                  "\tCall/See (c)\n" +
                  "\tRaise (r)\n" +
                  "\tFold/Junk (f)\n" +
                  "\tQuit (q)\n\t")).lower()

def RequestBankrupt():
    return (input("\nPlease type the letter of your chosen action:\n" +
                  "\tPass/Check (p)\n" +
                  "\tFold/Junk (f)\n" +
                  "\tQuit (q)\n\t")).lower()

def RequestEnd():
    return (input("\nPlease type the letter of your chosen action:\n" +
                  "\tWin (w)\n" +
                  "\tNext Round (n)\n" +
                  "\tSingle Blind Card Draw Win (s)\n" +
                  "\tQuit (q)\n\t")).lower()

def RequestOver():
    input("Game Over.")
    exit()


def DisplaySelection():
    print("Invalid Selection: Please select an available option.")

def DisplayTurn(turn):
    print("\nBetting Phase of Turn #" + str(turn + 1))

def DisplayFunds(funds):
    if funds != 1:
        print("You now have", funds, "credits.")
    else:
        print("You now have", funds, "credit.")

def DisplayEliminated():
    print("You have been eliminated from the game and\n" +
          "\tcleaned out of all your credits!")
