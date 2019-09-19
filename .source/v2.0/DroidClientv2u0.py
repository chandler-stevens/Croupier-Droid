from socket import socket, AF_INET, SOCK_DGRAM
from .DroidModel import *

def Transmit(message, datalink, mainframe):
    datalink.sendto(bytes(message, "utf-8"), mainframe)

def Receive(datalink):
    message, mainframe = datalink.recvfrom(4096)
    return str(message.decode("utf-8"))

def Main():
    datalink = socket(AF_INET, SOCK_DGRAM)
    mainframe = ("127.0.0.1", 8080)
    player = Join()
    message = "Joined:" + player
    Transmit(message, datalink, mainframe)
    while message != "All players have joined.":
        message = Receive(datalink)
        Display(message)
        if message == ("You have been designated as " +
                       "the dealer for this round."):
            while not Validate(message) or int(message) <= 1:
                message = input("How many total players, including yourself, " +
                                "are playing in this round?\t")
            Transmit(message, datalink, mainframe)
        elif message == "There are enough players for this round.":
            RequestEnd()
            return
    funds = Start()
    betting = False
    while funds != "q" and (
            (betting and funds >= 0) or (not betting and funds > 0)):
        DisplayFunds(funds)
        funds, betting, message = Action(funds, betting)
        if funds != "q":
            Transmit(message, datalink, mainframe)
        else:
            Transmit("Quit:" + player, datalink, mainframe)
            RequestEnd()
        if Validate(funds) and funds <= 0:
            DisplayEliminated()
            Transmit("Eliminated:" + player, datalink, mainframe)
            RequestEnd()
            return
