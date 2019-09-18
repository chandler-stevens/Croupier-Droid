from DroidControllerv1u4 import *

def Start():
    funds = RequestStart()
    if funds != "x":
        return funds
    return "x"

def ComputeAnte(funds, gamePotAnte, sabaccPotAnte):
    DisplayAnte(gamePotAnte, sabaccPotAnte)
    return funds - gamePotAnte - sabaccPotAnte

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


def Ante(funds, gamePotAnte, sabaccPotAnte):
    while True:
        choice = RequestAnte()
        if choice == "a":
            return ComputeAnte(funds, gamePotAnte, sabaccPotAnte)
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
            # elif choice == "d":
            #     newFunds = ComputeBet(RequestFee, funds)
            #     if newFunds != "x":
            #         return newFunds, False
            #     continue
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
    title, gamePotAnte, sabaccPotAnte, bettingPhases = RequestRule()
    funds = Start()
    DisplayFunds(funds)
    while funds > 0:
        funds = Ante(funds, gamePotAnte, sabaccPotAnte)
        DisplayFunds(funds)
        for turn in range(0, bettingPhases):
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
