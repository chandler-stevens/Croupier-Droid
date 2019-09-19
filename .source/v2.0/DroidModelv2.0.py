from .DroidControllerv2u0 import *

def Join():
    return RequestJoin()

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
            return (funds - sabacc), ("Ante:" + str(game) + ":" + str(sabacc))
    return "x", "x"

def Open(funds):
    openAmount = RequestOpen(funds)
    if Validate(openAmount):
        return (funds - openAmount), ("Open:" + str(openAmount))
    return "x", "x"

def Call(funds):
    callAmount = RequestCall(funds)
    if Validate(callAmount):
        return (funds - callAmount), ("Call:" + str(callAmount))
    return "x", "x"

def Raise(funds):
    raiseAmount = RequestRaise(funds)
    if Validate(raiseAmount):
        return (funds - raiseAmount), ("Raise:" + str(raiseAmount))
    return "x", "x"

def Win(funds):
    winType = RequestType()
    winAmount = RequestWin()
    if Validate(winAmount):
        if winType == "n":
            return (funds + winAmount), ("Nulrhek:" + str(winAmount))
        elif winType == "s":
            return (funds + winAmount), ("Sabacc:" + str(winAmount))
    return "x", "x"


def Action(funds, betting):
    while True:
        newFunds = funds
        if betting:
            choice = RequestBetting()
            if choice == "p":
                return funds, betting, "Pass:"
            elif choice == "o":
                newFunds, message = Open(funds)
                if newFunds != "x":
                    return newFunds, betting, message
            elif choice == "c":
                newFunds, message = Call(funds)
                if newFunds != "x":
                    return newFunds, betting, message
            elif choice == "r":
                newFunds, message = Raise(funds)
                if newFunds != "x":
                    return newFunds, betting, message
            elif choice == "f":
                return funds, False, "Fold:"
        else:
            choice = RequestAnte()
            if choice == "a":
                newFunds, message = Ante(funds)
                if newFunds != "x":
                    return newFunds, True, message
        if choice == "w":
            newFunds, message = Win(funds)
            if newFunds != "x":
                return newFunds, False, message
        elif choice == "q":
            return choice, betting, "Quit:"
        if newFunds != "x":
            DisplaySelection()
