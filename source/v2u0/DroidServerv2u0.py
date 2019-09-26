# Purpose: Transmit message to droid
# Parameters: Transmit message (string), datalink (socket), droid (address)
# Returns: None
def Transmit(message, datalink, droid):
    # Convert message to UTF-8 Bytes and transmit
    datalink.sendto(bytes(str(message), "utf-8"), droid)

# Purpose: Transmit message to all connected droids
# Parameters: Transmit message (string), datalink (socket), droids (list of addresses)
# Returns: None
def Broadcast(message, datalink, droids):
    # Iterate through each connected droid
    for droid in droids:
        # Convert message to UTF-8 Bytes and transmit
        datalink.sendto(bytes(message, "utf-8"), droid)

# Purpose: Receive message from droid
# Parameters: Datalink (socket)
# Returns: Received message (string)
def Receive(datalink):
    # Receive message with recommended buffer size and identify droid
    message, droid = datalink.recvfrom(4096)
    # Convert from UTF-8 Bytes
    return str(message.decode("utf-8")), droid


# Purpose: Receive message from droid
# Parameters: Players (list of strings), droids (list of addresses), datalink (socket)
# Returns: None
def Play(players, droids, datalink):
    # Initialize list of currently folded players
    folded = []
    
    # Initialize both pots and current highest bet to zero
    gamePot = 0
    sabaccPot = 0
    highestBet = 0

    # Constantly listen for message from clients
    while True:
        # Wait for message from client
        message, droid = Receive(datalink)

        # Find index of colon in message
        colon = message.index(":") + 1

        # Reject player attempting to join already filled session
        if message.startswith("Joined"):
            Transmit("There are enough players for this round.", datalink, droid)
            print("Rejected extra player " + message[colon:])
        # Process ante
        elif message.startswith("Ante"):
            # Find index of second colon in message
            colon2 = message.index(":", colon)

            # Increment both pots by corresponding ante
            gamePot += int(message[colon:colon2])
            sabaccPot += int(message[colon2 + 1:])
            print("Ante", gamePot, sabaccPot)
        # Process Draw Phase Fee
        elif message.startswith("Fee"):
            # Find index of second colon in message
            colon2 = message.index(":", colon)

            # Increment both pots by corresponding fee
            gamePot += int(message[colon:colon2])
            sabaccPot += int(message[colon2 + 1:])
            print("Fee", gamePot, sabaccPot)
        # Process pass
        elif message.startswith("Pass"):
            # Maintain both pots
            print("Pass")
        # Process open
        elif message.startswith("Open"):
            # Update current highest bet
            highestBet = int(message[colon:])

            # Add bet to Game Pot
            gamePot += highestBet
            print("Open", gamePot, highestBet)
        # Process call
        elif message.startswith("Call"):
            # Add bet difference to Game Pot
            gamePot += int(message[colon:])
            print("Call", gamePot, highestBet)
        # Process raise
        elif message.startswith("Raise"):
            # Find index of second colon in message
            colon2 = message.index(":", colon)
            
            # Extract bet difference
            bet = int(message[colon:colon2])
            
            # Update current highest bet
            # New highest bet equals bet difference plus
            # total contribution in current Betting Phase
            highestBet = bet + int(message[colon2 + 1:])

            # Add bet difference to Game Pot
            gamePot += bet
            print("Raise", gamePot, highestBet)
        # Process fold
        elif message.startswith("Fold"):
            # Determine droid and player that folded
            index = droids.index(droid)

            # Add droid and player to folded list
            folded.append([players[index], droids[index]])
            print("Fold", folded)
        # Process Nulrhek win
        elif message.startswith("Nulrhek"):
            # Reset Game Pot
            gamePot = 0

            # Reset current highest bet
            highestBet = 0
            print("Nulrhek win")
        # Process Sabacc win
        elif message.startswith("Sabacc"):
            # Reset both pots
            gamePot = 0
            sabaccPot = 0

            # Reset current highest bet
            highestBet = 0
            print("Sabacc win")
        # Process elimination of player quit
        elif message.startswith("Eliminated") or message.startswith("Quit"):
            # Determine droid and player that is out
            index = droids.index(droid)

            # Remove player and droid from list of players and droids
            players.pop(index)
            droids.pop(index)
            print(players, droids)

# Purpose: Setup session
# Parameters: None
# Returns: None
def Setup():
    # Initialize joined number of players to one
    quantity = 1
    # Initialize list of player names
    players = []
    # Initialize list of droid addresses
    droids = []
    # Initialize queue of pending players
    queue = []

    # Import networking package
    from socket import socket, AF_INET, SOCK_DGRAM
    # Setup datalink
    datalink = socket(AF_INET, SOCK_DGRAM)
    datalink.bind(("", 2187))

    # Wait for first player to join session
    message, droid = Receive(datalink)

    # Ensure message is for player joining
    while not message.startswith("Joined"):
        Transmit("TRUE", datalink, droid)
        message, droid = Receive(datalink)
    print(message)
    # Locate index of comma in received message
    colon = message.index(":") + 1
    
    # Extract player name from message
    player = message[colon:]
    # Add player and droid to lists
    players.append(player)
    droids.append(droid)

    # Notify initial player they will be the dealer for first round
    Transmit("You have been designated as the dealer for this round.", datalink, droid)

    # Wait for dealer to input number of players
    while not message.isdigit() or droid != droids[0]:
        # Wait to receive message from dealer
        message, droid = Receive(datalink)

        # Check if received message was not from dealer
        if droid != droids[0]:
            # Ensure message is for player joining
            while not message.startswith("Joined"):
                Transmit("TRUE", datalink, droid)
                message, droid = Receive(datalink)
            # Locate index of comma in received message
            colon = message.index(":") + 1
            # Ensure message is for player joining
            if (message.startswith("Joined")):
                # Extract player name from message
                player = message[colon:]
                # Add player and droid to queue
                queue.append([player, droid])
                Transmit("Waiting for other players to join.", datalink, droid)

    # Set dealer input to total number of players allowed in round
    total = int(message)
    print("Player cap set to " + str(total))

    # While round player limit not exceeded
    while quantity < total and (quantity - 1) < len(queue):
        # Add players in queue to lists
        players.append(queue[quantity - 1][0])
        droids.append(queue[quantity - 1][1])
        print("Joined:" + players[-1])

        # Notify dealer of joining player
        Transmit(queue[quantity - 1][0] + " (Player #" + str(quantity + 1) +
                 ") has joined the game.", datalink, droids[0])

        # Increment number of players joined
        quantity += 1

    # Reject extra players in queue
    if quantity == total:
        # Iterate through extra players in queue
        while quantity <= len(queue):
            # Reject extra player
            Transmit("There are enough players for this round.", datalink, queue[quantity - 1][1])
            print("Rejected extra player " + queue[quantity-1][0])
            # Increment counter
            quantity += 1

    # Wait for any other players to join
    while quantity < total:
        Transmit("Waiting for other players to join.", datalink, droids[0])
        # Ensure message is for player joining
        while not message.startswith("Joined"):
            Transmit("TRUE", datalink, droid)
            message, droid = Receive(datalink)
        print(message)
        # Locate index of comma in received message
        colon = message.index(":") + 1
        # Ensure message is for player joining
        if (message.startswith("Joined")):
            # Extract player name from message
            player = message[colon:]
            # Add player and droid to lists
            players.append(player)
            droids.append(droid)

            Transmit("Waiting for other players to join.", datalink, droid)

            # Notify dealer of joining player
            Transmit(player + " (Player #" + str(quantity + 1) +
                     ") has joined the game.", datalink, droids[0])

            # Increment number of players joined
            quantity += 1

    # Notify all players that all players have joined
    Broadcast("All players have joined.", datalink, droids)

    # Begin round
    Play(players, droids, datalink)
