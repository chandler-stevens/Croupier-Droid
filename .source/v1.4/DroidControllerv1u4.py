from .HouseRulesv1u4 import rulesList

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
            elif funds == "rule" and userInput > len(rulesList):
                print("Invalid Number: Please enter a valid house rule number.")
            else:
                return userInput
        else:
            print("Invalid Input: Please enter a positive integer.")
        print("Type (x) if you want to cancel.")


def RequestRule():
    prompt = "Please type the number of your chosen house rule:\n"
    for index, rule in enumerate(rulesList, start=1):
        prompt += "\t" + rule[0] + " (" + str(index) + ")\n"
    choice = Request("rule", (prompt + "\t"))
    if choice == "x":
        RequestOver()
    choice = rulesList[choice - 1]
    return choice[0], choice[1], choice[2], choice[3]

def RequestStart():
    return Request("start", "How many credits are you starting with?\n\t")

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
                  #"\tDraw Phase Fee (d)\n" +
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

def DisplayAnte(gamePotAnte, sabaccPotAnte):
    message = "Buying in with an ante of\n\t" + str(gamePotAnte) + " credit"
    if gamePotAnte != 1:
        message += "s"
    message += " into the Game Pot and\n\t" + str(sabaccPotAnte) + " credit"
    if sabaccPotAnte != 1:
        message += "s"
    message += " into the Sabacc Pot."
    print(message)

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
