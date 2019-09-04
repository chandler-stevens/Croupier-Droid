from socket import socket, AF_INET, SOCK_DGRAM
from DroidModel import *

def Transmit(message, datalink, mainframe):
    datalink.sendto(bytes(message, "utf-8"), mainframe)

def Compute(player, funds, datalink, mainframe):
    result = Action(funds)
    if result[1] > 0:
        if (result[0] == "Ante"):
            message = result[0] + ":" + str(result[1]) + ":" + str(result[2])
        if (result[0] == "Open"):
            message = result[0] + ":" + str(funds[1])
        # # Receive response message
        # print('\nPending confirmation...')
        # receivedMessage, mainframe = datalink.recvfrom(4096)
        # receivedMessage = str(receivedMessage.decode("utf-8"))
    else:
        print("\nYou have gone bankrupt!\n")
        Transmit("Eliminated:" + player, datalink, mainframe)
        return False
    Transmit(message, datalink, mainframe)
    return True

datalink = socket(AF_INET, SOCK_DGRAM)
mainframe = ("192.168.254.29", 8080)
player, funds = Start()
Transmit("Joined:" + player, datalink, mainframe)
eliminated = False
while (not eliminated):
    eliminated = Compute(player, funds, datalink, mainframe)
