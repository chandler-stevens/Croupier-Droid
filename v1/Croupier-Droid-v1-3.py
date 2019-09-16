from DroidControllerv1u3 import *

def Start():
    funds = RequestStart()
    if funds != "x":
        return funds
    return "q"


def Ante(funds):
    game = RequestGame(funds)
    if Validate(game):
        funds -= game
        sabacc = RequestSabacc(funds)
        if Validate(sabacc):
            return funds - sabacc
    return "x"

def Bet(RequestFunction, funds):
    amount = RequestFunction(funds)
    if Validate(amount):
        return funds - amount
    return "x"

def Win(funds):
    winAmount = RequestWin()
    if Validate(winAmount):
        return funds + winAmount
    return "x"    
    
    
def Action(funds, betting):
    while True:
        if betting:
            if funds > 0:
                choice = RequestBetting()
                if choice == "o":
                    newFunds = Bet(RequestOpen, funds)
                    if newFunds != "x":
                        return newFunds, True
                    continue
                elif choice == "c":
                    newFunds = Bet(RequestCall, funds)
                    if newFunds != "x":
                        return newFunds, True
                    continue
                elif choice == "r":
                    newFunds = Bet(Requestise, funds)
                    if newFunds != "x":
                        return newFunds, True
                    continue
            else:
                choice = RequestBankrupt()
            if choice == "p":
                return funds, True
            elif choice == "f":
                return funds, False
        else:
            choice = RequestAnte()
            if choice == "a":
                newFunds = Ante(funds)
                if newFunds != "x":
                    return newFunds, True
                continue
        if choice == "w":
            newFunds = Win(funds)
            if newFunds != "x":
                return newFunds, False
            continue
        elif choice == "q":
            return "q", False
        DisplaySelection()
        
        
def Main():
    funds = Start()
    betting = False
    while funds != "q" and ((betting and funds >= 0) or (not betting and funds > 0)):
        DisplayFunds(funds)
        funds, betting = Action(funds, betting)
    if funds != "q":
        DisplayEliminated()
    RequestEnd()
    
Main()
