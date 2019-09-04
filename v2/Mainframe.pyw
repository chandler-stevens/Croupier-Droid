# Import socket library
from socket import socket, AF_INET, SOCK_DGRAM

# Open a socket
datalink = socket(AF_INET, SOCK_DGRAM)
# Bind the open socket to the selected IPv4 and port
datalink.bind(("192.168.254.29", 8080))

players = []
folded = []
gamePot = 0
sabaccPot = 0
highestBet = 0

while (True):
    # Receive response message
    message, address = datalink.recvfrom(4096)
    message = str(message.decode("utf-8"))
    colon = message.index(":") + 1
    if (message.startswith("Joined")):
        players.append(message[colon:])
        print(players)
    elif (message.startswith("Eliminated")):
        players.remove(message[colon:])
        print(players)
    elif (message.startswith("Fold")):
        folded.append(message[colon:])
        print(folded)
    elif (message.startswith("Ante")):
        colon2 = message.index(":", colon)
        gamePot += int(message[colon:colon2])
        sabaccPot += int(message[colon2 + 1:])
        print("Ante", gamePot, sabaccPot)
    elif (message.startswith("Open")):
        highestBet = int(message[colon:])
        gamePot += highestBet
        print("Open", gamePot, highestBet)
    elif (message.startswith("Call")):
        gamePot += highestBet
        print("Call", gamePot, highestBet)
    elif (message.startswith("Raise")):
        highestBet += int(message[colon:])
        gamePot += highestBet
        print("Raise", gamePot, highestBet)
    elif (message.startswith("Nulrhek")):
        gamePot = 0
        highestBet = 0
    elif (message.startswith("Sabacc")):
        gamePot = 0
        sabaccPot = 0
        highestBet = 0

        # Send back message
        # sentMessage = datalink.sendto(message, address)
        # print('Sending '+str(len(message.decode('utf-8')))+' Bytes back to port '+str(address[1])+' of IPv4 address '+address[0]+'\n')
