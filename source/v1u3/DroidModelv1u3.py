from DroidControllerv1u3 import *

def Start():
    funds = RequestStart()
    if funds != "x":
        return funds
    RequestOver()


def Ante(funds):
    while True:
        choice = RequestAnte()
        if choice == "a":
            newFunds = funds
            gamePotAnte = RequestGame(newFunds)
            if gamePotAnte != "x":
                newFunds -= gamePotAnte
                sabaccPotAnte = RequestSabacc(newFunds)
                if sabaccPotAnte != "x":
                    return newFunds - sabaccPotAnte, gamePotAnte, sabaccPotAnte
            continue
        elif choice == "q":
            RequestOver()
        DisplaySelection()


def Bet(funds):
    while True:
        if funds > 0:
            choice = RequestBetting()
            if choice == "o":
                bet = RequestOpen(funds)
                if bet != "x":
                    return funds - bet, bet, False
                continue
            elif choice == "c":
                bet = RequestCall(funds)
                if bet != "x":
                    return funds - bet, bet, False
                continue
            elif choice == "r":
                bet = RequestRaise(funds)
                if bet != "x":
                    return funds - bet, bet, False
                continue
            elif choice == "d":
                bet = RequestFee(funds)
                if bet != "x":
                    return funds - bet, bet, False
                continue
        else:
            choice = RequestBankrupt()
        if choice == "p":
            return funds, 0, False
        elif choice == "f" or choice == "e":
            return funds, 0, True
        elif choice == "q":
            RequestOver()
        DisplaySelection()

def Win(funds, gamePot, sabaccPot):
    while True:
        winner = RequestWinner()
        if winner != "q":
            hand = RequestHand()
            if hand == "s":
                if winner == "y":
                    gameWinnings = RequestGamePot()
                    if gameWinnings != "x":
                        sabaccWinnings = RequestSabaccPot()
                        if sabaccWinnings != "x":
                            return (funds + gamePot + sabaccPot +
                                    gameWinnings + sabaccWinnings), 0
                        continue
                    continue
                elif winner == "o":
                    DisplayGamePot(gamePot)
                    DisplaySabaccPot(sabaccPot)
                    return funds, 0
                else:
                    DisplaySelection()
                    continue
            elif hand == "n":
                newFunds = funds
                if winner == "y":
                    gameWinnings = RequestGamePot()
                    if gameWinnings != "x":
                        newFunds += gamePot + gameWinnings
                    else:
                        continue
                elif winner == "o":
                    DisplayGamePot(gamePot)
                else:
                    DisplaySelection()
                    continue
                proceed = RequestProceed()
                if proceed == "n":
                    return newFunds, sabaccPot
                elif proceed == "s":
                    winner = RequestWinner()
                    if winner == "y":
                        sabaccWinnings = RequestSabaccPot()
                        if sabaccWinnings != "x":
                            return newFunds + sabaccPot + sabaccWinnings, 0
                        continue
                    elif winner == "o":
                        DisplaySabaccPot(sabaccPot)
                        return newFunds, 0
                    elif winner == "q":
                        RequestOver()
                elif proceed == "q":
                    RequestOver()
            elif hand == "q":
                RequestOver()
            DisplaySelection()
        else:
            RequestOver()


def Main():
    sabaccPot = 0
    funds = Start()
    DisplayFunds(funds)
    while funds > 0:
        funds, gamePot, sabaccPotAnte = Ante(funds)
        sabaccPot += sabaccPotAnte
        DisplayFunds(funds)
        roundOver = False
        while not roundOver:
            funds, bet, roundOver = Bet(funds)
            gamePot += bet
            DisplayFunds(funds)
        funds, sabaccPot = Win(funds, gamePot, sabaccPot)
        DisplayFunds(funds)
    DisplayEliminated()
    RequestOver()
