def Validate(num):
    try:
        int(str(num).replace(",", ""))
        return True
    except ValueError:
        return False


def Display(message):
    print(message)


def Request(funds, message):
    while True:
        num = input(message)
        if num == "x":
            return num
        elif Validate(num):
            if int(num) <= 0:
                print("Invalid Number: Please enter a positive integer.")
            elif funds != "N/A" and int(num) > funds:
                print("Insufficient Funds: You only have", funds, "credits.")
            else:
                return int(num)
        else:
            print("Invalid Input: Please enter a positive integer.")
        print("Type (x) if you want to cancel.")


def RequestJoin():
    return input("What is your name?\n\t")

def RequestStart():
    return Request("N/A", "How many credits are you starting with?\n\t")


def RequestGame(funds):
    return Request(funds, "How many credits are you using to\n" +
                          "\tante into the Game Pot?\n\t")

def RequestSabacc(funds):
   return Request(funds, "How many credits are you using to\n" +
                         "\tante into the Sabacc Pot?\n\t")
def RequestOpen(funds):
    return Request(funds, "How many credits would you like to open with?\n\t")

def RequestCall(funds):
    return Request(funds, "How many credits would you like to call with?\n\t")

def RequestRaise(funds):
    return Request(funds, "How many total credits would you like to\n" +
                          "\traise the highest bet to?\n\t")

def RequestType():
    return (input("Did you win with a Nulrhek (n) or with a Sabacc (s)\n\t")).lower()

def RequestWin():
    return Request("N/A", "How many more credits did you win?\n\t")


def RequestAnte():
    return (input("\nPlease type the letter of your chosen action:\n" +
                  "\tAnte/Buy In (a)\n" +
                  "\tWin (w)\n" +
                  "\tQuit/End Game (q)\n\t")).lower()

def RequestBetting():
    return (input("\nPlease type the letter of your chosen action:\n" +
                  "\tPass/Check (p)\n" +
                  "\tOpen/Bet (o)\n" +
                  "\tCall/See (c)\n" +
                  "\tRaise (r)\n" +
                  "\tFold/Junk (f)\n" +
                  "\tWin (w)\n" +
                  "\tQuit/End Game (q)\n\t")).lower()

def RequestEnd():
    input("Game Over.")


def DisplaySelection():
    print("Invalid Selection: Please select an\n" +
          "\tavailable option.")

def DisplayFunds(funds):
    if funds != 1:
        print("You now have", funds, "credits remaining.")
    else:
        print("You now have", funds, "credit remaining.")

def DisplayEliminated():
    print("You have been eliminated from the game and\n" +
          "\tcleaned out of all your credits!")
