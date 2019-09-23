from socket import socket, AF_INET, SOCK_DGRAM

def Transmit(message, datalink, droid):
    datalink.sendto(bytes(message, "utf-8"), droid)

def Broadcast(message, datalink, droids):
    for droid in droids:
        datalink.sendto(bytes(message, "utf-8"), droid)


def Receive(datalink):
    message, droid = datalink.recvfrom(4096)
    return str(message.decode("utf-8")), droid


def Play(players, droids, total, datalink):
    folded = []
    gamePot = 0
    sabaccPot = 0
    highestBet = 0
    while (True):
        message, droid = Receive(datalink)
        colon = message.index(":") + 1
        if (message.startswith("Joined")):
            Transmit("There are enough players for this round.",
                     datalink, droid)
        # elif (message.startswith("Ante")):
        #     colon2 = message.index(":", colon)
        #     gamePot += int(message[colon:colon2])
        #     sabaccPot += int(message[colon2 + 1:])
        #     print("Ante", gamePot, sabaccPot)
        # elif (message.startswith("Pass")):
        #     print("Pass")
        # elif (message.startswith("Open")):
        #     highestBet = int(message[colon:])
        #     gamePot += highestBet
        #     print("Open", gamePot, highestBet)
        # elif (message.startswith("Call")):
        #     gamePot += highestBet
        #     print("Call", gamePot, highestBet)
        # elif (message.startswith("Raise")):
        #     highestBet += int(message[colon:])
        #     gamePot += highestBet
        #     print("Raise", gamePot, highestBet)
        # elif (message.startswith("Fold")):
        #     folded.append(message[colon:])
        #     print("Fold", folded)
        # elif (message.startswith("Nulrhek")):
        #     gamePot = 0
        #     highestBet = 0
        # elif (message.startswith("Sabacc")):
        #     gamePot = 0
        #     sabaccPot = 0
        #     highestBet = 0
        elif (message.startswith("Eliminated") or message.startswith("Quit")):
            players.remove(message[colon:])
            print(players)

def Main():
    quantity = 1
    total = 1
    players = []
    droids = []
    datalink = socket(AF_INET, SOCK_DGRAM)
    datalink.bind(("127.0.0.1", 8080))
    message, droid = Receive(datalink)
    colon = message.index(":") + 1
    if (message.startswith("Joined")):
        player = message[colon:]
        players.append(player)
        Transmit("You have been designated as the dealer for this round.",
                 datalink, droid)
        message, droid = Receive(datalink)
        total = int(message)
        Transmit("Waiting for other players to join.", datalink, droid)
    while quantity < total:
        message, droid = Receive(datalink)
        colon = message.index(":") + 1
        if (message.startswith("Joined")):
            player = message[colon:]
            players.append(player)
            Transmit(player + " (Player #" + str(quantity + 1) +
                     ") has joined the game.", datalink, droids[0])
            droids.append(droid)
            if (quantity + 1) == total:
                Broadcast("All players have joined.", datalink, droids)
    # Play(players, droids, total, datalink)

Main()
