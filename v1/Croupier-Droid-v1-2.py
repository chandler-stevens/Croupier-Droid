from DroidControllerv1u2 import *

def Start():
    funds = RequestStart()
    if Validate(funds):
        return funds
    elif funds == "x":
        return "q"
    Start()

def Ante(funds):
    game = RequestGame(funds)
    if Validate(game):
        funds -= game
        sabacc = RequestSabacc(funds)
        if Validate(sabacc):
            return funds - sabacc
    return "x"

def Open(funds):
    openAmount = RequestOpen(funds)
    if Validate(openAmount):
        return funds - openAmount
    return "x"

def Call(funds):
    callAmount = RequestCall(funds)
    if Validate(callAmount):
        return funds - callAmount
    return "x"

def Raise(funds):
    raiseAmount = RequestRaise(funds)
    if Validate(raiseAmount):
        return funds - raiseAmount
    return "x"

def Win(funds):
    winAmount = RequestWin()
    if Validate(winAmount):
        return funds + winAmount
    return "x"
    

def Play(funds, betting):
    while True:
        newFunds = funds
        if betting:
            choice = RequestBetting()
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
            choice = RequestAnte()
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
        DisplaySelection()
        
        
def Main():
    funds = Start()
    betting = False
    while funds != "q" and ((betting and funds >= 0) or (not betting and funds > 0)):
        DisplayFunds(funds)
        funds, betting = Play(funds, betting)
        if Validate(funds) and funds <= 0:
            DisplayEliminated()
    RequestEnd()
    
Main()
