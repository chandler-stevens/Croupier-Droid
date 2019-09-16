from DroidControllerv1u4 import *

def Rule():
    rule = RequestRule()
    if rule == "x":
        RequestOver()
    elif rule == 2:
        return 4
    else:
        return 3


def ComputeAnte(funds):
    game = RequestGame(funds)
    if game != "x":
        funds -= game
        sabacc = RequestSabacc(funds)
        if sabacc != "x":
            return funds - sabacc
    return "x"

def ComputeBet(RequestFunction, funds):
    amount = RequestFunction(funds)
    if amount != "x":
        return funds - amount
    return "x"

def ComputeWin(funds):
    winAmount = RequestWin()
    if winAmount != "x":
        return funds + winAmount
    return "x"    


def Ante(funds):
    while True:
        choice = RequestAnte()
        if choice == "a":
            newFunds = ComputeAnte(funds)
            if newFunds != "x":
                return newFunds
            continue
        elif choice == "q":
            RequestOver()
        DisplaySelection()

def Bet(funds):
    while True:
        if funds > 0:
            choice = RequestBetting()
            if choice == "o":
                newFunds = ComputeBet(RequestOpen, funds)
                if newFunds != "x":
                    return newFunds, False
                continue
            elif choice == "c":
                newFunds = ComputeBet(RequestCall, funds)
                if newFunds != "x":
                    return newFunds, False
                continue
            elif choice == "r":
                newFunds = ComputeBet(RequestRaise, funds)
                if newFunds != "x":
                    return newFunds, False
                continue
            elif choice == "d":
                newFunds = ComputeBet(RequestFee, funds)
                if newFunds != "x":
                    return newFunds, False
                continue
        else:
            choice = RequestBankrupt()
        if choice == "p":
            return funds, False
        elif choice == "f":
            return funds, True
        elif choice == "q":
            RequestOver()
        DisplaySelection()

def Win(funds):
    while True:
        choice = RequestEnd()
        if choice == "w" or choice == "s":
            newFunds = ComputeWin(funds)
            if newFunds != "x":
                return newFunds
            continue
        elif choice == "n":
            return funds
        elif choice == "q":
            RequestOver()
        DisplaySelection()


def Main():
    turns = Rule()
    funds = RequestStart()
    DisplayFunds(funds)
    while funds > 0:
        funds = Ante(funds)
        DisplayFunds(funds)
        for turn in range(0, turns):
            DisplayTurn(turn)
            funds, folded = Bet(funds)
            if folded:
                break
            DisplayFunds(funds)
        funds = Win(funds)
        DisplayFunds(funds)
    DisplayEliminated()
    RequestOver()

Main()
