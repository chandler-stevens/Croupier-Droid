def Validate(num):
    try:
        int(str(num).replace(",", ""))
        return True
    except ValueError:
        return False

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


def Start():
    funds = Request("N/A", "How many credits are you starting with?\n\t")
    if Validate(funds):
        return funds
    elif funds == "x":
        return "q"
    Start()

def Ante(funds):
    game = Request(funds, "\nHow many credits are you using to\n"+
                          "\tante into the Game Pot?\n\t")
    if Validate(game):
        sabacc = Request(funds - game, "\nHow many credits are you using to\n"+
                                       "\tante into the Sabacc Pot?\n\t")
        if Validate(sabacc):
            return funds - game - sabacc
    return "x"

def Open(funds):
    openAmount = Request(funds, "\nHow many credits would you like to open with?\n\t")
    if Validate(openAmount):
        return funds - openAmount
    return "x"

def Call(funds):
    callAmount = Request(funds, "\nHow many credits would you like to call with?\n\t")
    if Validate(callAmount):
        return funds - callAmount
    return "x"

def Raise(funds):
    raiseAmount = Request(funds, "\nHow many total credits would you like to"+
                                 "\traise the highest bet to?\n\t")
    if Validate(raiseAmount):
        return funds - raiseAmount
    return "x"

def Win(funds):
    winAmount = Request("N/A", "\nHow many more credits did you win?\n\t")
    if Validate(winAmount):
        return funds + winAmount
    return "x"
    

def Play(funds, betting):
    while True:
        newFunds = funds
        if betting:
            choice = (input("\nPlease type the letter of your chosen action:\n"+
                            "\tPass/Check (p)\n"+
                            "\tOpen/Bet (o)\n"+
                            "\tCall/See (c)\n"+
                            "\tRaise (r)\n"+
                            "\tFold/Junk (f)\n"+
                            "\tWin (w)\n"+
                            "\tQuit/End Game (q)\n\t")).lower()
            if choice == "o":
                newFunds = Open(funds)
                if newFunds != "x":
                    return newFunds, betting
            elif choice == "c":
                newFunds = Call(funds)
                if newFunds != "x":
                    return newFunds, betting
            elif choice == "r":
                newFunds = Raise(funds)
                if newFunds != "x":
                    return newFunds, betting
            elif choice == "f":
                return funds, False          
        else:
            choice = (input("\nPlease type the letter of your chosen action:\n"+
                            "\tAnte/Buy In (a)\n"+
                            "\tWin (w)\n"+
                            "\tQuit/End Game (q)\n\t")).lower()
            if choice == "a":
                newFunds = Ante(funds)
                if newFunds != "x":
                    return newFunds, True
        if choice == "w":
            newFunds = Win(funds)
            if newFunds != "x":
                return newFunds, False
        elif choice == "q":
            return choice, betting
        if newFunds == "x" or choice == "p":
                return funds, betting
        print("Invalid Selection: Please select an\n"+
              "\tavailable option.")
        
        
def Main():
    funds = Start()
    betting = False
    while funds != "q" and (betting and funds >= 0) or (not betting and funds > 0):
        if funds != 1:
            print("\nYou now have", funds, "credits remaining.\n")
        else:
            print("\nYou now have", funds, "credit remaining.\n")
        funds, betting = Play(funds, betting)
        if Validate(funds) and funds <= 0:
            print("You have been eliminated from the game and\n"+
                  "\tcleaned out of all your credits!")
    input("Game Over.")
    return 0

Main()