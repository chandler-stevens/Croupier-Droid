

# Purpose: Transmit message to mainframe
# Parameters: Transmit message (string), datalink (socket), mainframe (address)
# Returns: None
def Transmit(message, datalink, mainframe):
    # Convert message to UTF-8 Bytes and transmit
    datalink.sendto(bytes(str(message), "utf-8"), mainframe)


# Purpose: Receive message from mainframe
# Parameters: Datalink (socket)
# Returns: Values (list)
def Receive(datalink):
    # Receive message with recommended buffer size and convert from UTF-8 Bytes
    message = str((datalink.recv(4096)).decode("utf-8"))

    # Initialize starting index and values list
    start = 0
    values = []

    # Extract each segment from message
    # Check if starting index is still within message bounds
    while start < len(message):
        # Try to find a colon
        try:
            # Get the index of the next colon starting from the offset
            colon = message.index(":", start)
            # Extract the segment and add it to values list
            values.append(message[start:colon])
            # Increment offset to character after found colon
            start = colon + 1
        # If no more colons found
        except ValueError:
            # Extract the rest of the message into the values list
            values.append(message[start:])
            # Break out from the while loop
            break

    # Return values
    return values


# Purpose: Establish connection to server
# Parameters: controller (module), version (string)
# Returns: Datalink (socket), mainframe (address)
def Connect(controller, version):
    # Import networking package
    from socket import socket, AF_INET, SOCK_DGRAM
    # Setup datalink
    datalink = socket(AF_INET, SOCK_DGRAM)

    # Identify mainframe
    mainframe = ""
    # Connect to dummy socket to determine default gateway
    datalink.connect(("8.8.8.8", 80))
    # Determine connected IPv4 address
    ip = datalink.getsockname()[0]
    # Close dummy socket
    datalink.close()
    # Restart socket
    datalink = socket(AF_INET, SOCK_DGRAM)
    # Find last dot in connected IPv4 address
    dot = ip.rfind(".") + 1
    # Extract subnet to determine default gateway
    ip = ip[:dot]
    # Import select module
    from select import select

    # Initialize connection status to unconnected
    connected = False
    while not connected:
        # Iterate through all possible IPv4 addresses in subnet
        for i in range(1, 254):
            try:
                # Transmit test message
                Transmit("TEST:", datalink, (ip + str(i), 2187))
            except ConnectionResetError:
                continue

        # Initialize received message
        message = ""
        # Wait until correct server responds
        while message != "TRUE":
            # Wait for response from a server with 10 second timeout
            response = select([datalink], [], [], 10)
            # If response received
            if response[0]:
                try:
                    # Receive message
                    message, mainframe = datalink.recvfrom(4096)
                    # Convert message from UTF-8 Bytes
                    message = str(message.decode("utf-8"))
                except ConnectionResetError:
                    # Ignore unavailable server
                    continue
            else:
                # Notify player of connection failure
                controller.RequestUnconnected()
                break
        if message == "TRUE":
            connected = True

    # Close socket in case other servers responded
    datalink.close()
    # Restart socket
    datalink = socket(AF_INET, SOCK_DGRAM)

    # Ask for name until successfully joined
    message = ""
    player = ""
    while message != "Success":
        # Retrieve player name
        player = controller.RequestJoin(message)
        # Transmit player joined
        Transmit("Joined:" + player, datalink, mainframe)

        # Ensure no name conflict
        values = Receive(datalink)
        message = values[0]

    # Initialize whether this player is the dealer
    dealer = False
    # Initialize list of players in case this player is the dealer
    playerList = []
    numberOrder = []

    # Wait for all players to join session
    while message != "All players have joined.":
        # Wait to receive message from mainframe
        values = Receive(datalink)
        if len(values) == 1:
            message = values[0]

            # Check if player is current dealer
            if message == "You have been designated as the dealer for this round.":
                # Set player as the dealer
                dealer = True
                controller.DisplayMessage(message)
                # Import house rules
                houseRules = import_module("HouseRules" + version)
                # Wait for dealer to provide valid house rule and transmit
                rule = controller.RequestRule(houseRules.rulesList)
                Transmit("Rule:" + str(rule), datalink, mainframe)
                # Wait for dealer to provide valid number of players for round and transmit
                Transmit("Quantity:" + str(controller.RequestPlayers(houseRules.rulesList[rule][5])), datalink, mainframe)
            # Check if dealer was notified that player joined
            elif dealer and message.endswith("has joined the game."):
                playerList.append(message[:message.index(" (Player #")] + " (" + message[(message.index("Player #") + 8):message.index(" has joined the game.")])
                numberOrder.append(int(message[(message.index("Player #") + 8):message.index(") has joined the game.")]))
            # Check if session is full
            elif message == "There are enough players for this round.":
                # Reject extra player
                controller.RequestOver()
            # Directly display a received message
            elif message != "TRUE":
                controller.DisplayMessage(message)

    # Once all players have joined, ask dealer to provide physical ordering of players
    if dealer:
        # Initialize order of players
        playerOrder = []
        # If there are more than two total players, including the dealer
        if len(playerList) > 1:
            # While the player list is not empty
            while len(playerList) != 0:
                # If at least one player has already been properly ordered
                if len(playerOrder) != 0:
                    # Display most recently ordered player within prompt and the remaining unordered players
                    nextPlayer = controller.requestOrder(playerOrder[-1], playerList, numberOrder)
                # Otherwise, if no players have been ordered yet
                else:
                    # Display dealer's player name within prompt and the remaining unordered players
                    nextPlayer = controller.requestOrder(player, playerList, numberOrder)
                numberOrder.remove(nextPlayer)
                playerOrder.append(playerList.pop(nextPlayer - 2)[:-4])
        # Otherwise, if there is just one player playing against the dealer
        else:
            # Begin the ordered list with the opposing player
            playerOrder.append(playerList[0][:-4])
        # Add the dealer's player name to the very end of the ordered list
        playerOrder.append(player)
        # Transmit ordered list of players to mainframe
        Transmit("Order:" + str(playerOrder), datalink, mainframe)

    # Return datalink, mainframe, and dealer status
    return datalink, mainframe, dealer


# Purpose: Get starting funds or end game
# Parameters: CFG parser (ConfigParser), CFG file path (string), controller (module)
# Returns: Starting funds (integer)
def Start(parser, saveFile, controller):
    # Read CFG
    parser.read(saveFile)
    # Retrieve value of funds left over from previous game
    lastFunds = parser["GENERAL"]["last_funds"]

    # Retrieve starting funds
    funds = controller.RequestStart(lastFunds)

    # Accept valid starting funds
    if funds != "x":
        return funds

    # End game if 'x' cancel option given
    controller.RequestOver()


# Purpose: Update current funds in configuration file
# Parameters: Current funds (integer), CFG parser (ConfigParser), CFG file path (string)
# Returns: None
def UpdateSave(funds, parser, saveFile):
    # Read CFG
    parser.read(saveFile)
    # Open CFG with editing permission
    with open(saveFile, 'w+') as cfg:
        # Update current funds saved in CFG
        parser.set("GENERAL", "last_funds", str(funds))
        parser.write(cfg)
        cfg.close()


# Purpose: Play round
# Parameters: Program version (string), import_module (module)
# Returns: None
def Play(version, import_module):
    # Import controller
    controller = import_module("DroidController" + version)

    # Establish connection to mainframe
    datalink, mainframe, dealer = Connect(controller, version)

    # Import CFG parser
    from configparser import ConfigParser
    # Initialize CFG parser
    parser = ConfigParser()
    
    # Import parent directory name
    from os.path import dirname
    # Locate CFG
    saveFile = dirname(__file__) + "/DroidCache" + version + ".cfg"
    
    # Retrieve starting funds
    funds = Start(parser, saveFile, controller)

    # Transmit starting funds to mainframe
    Transmit("Start:" + str(funds), datalink, mainframe)

    # Play rounds until eliminated
    while funds > 0:
        # Retrieve for chosen house rule details message
        values = Receive(datalink)

        # Extract house rule title
        title = values[0]
        # Extract house rule ante
        gamePotAnte = int(values[1])
        sabaccPotAnte = int(values[2])
        # Import string to list converter
        from json import loads
        # Extract house rule draw fees
        drawFees = loads(values[3])

        # Notify player of chosen house rule
        controller.DisplayMessage("Starting a round under " + title + " house rules.")

        # Attempt to ante
        Transmit("Ante:", datalink, mainframe)

        # Wait for ante success message from mainframe
        values = Receive(datalink)
        status = values[0]
        funds = int(values[1])

        if status == "Ante OK":
            # Notify player ante is being payed
            controller.DisplayAnte(gamePotAnte, sabaccPotAnte)

            # Notify player of available funds and update CFG
            controller.DisplayFunds(funds)
            UpdateSave(funds, parser, saveFile)
        elif status == "Ante failed":
            # Notify player of elimination
            controller.DisplayEliminated()

            # End game
            controller.RequestOver()

        # Loop until round is over
        inRound = True
        while inRound:
            # Get turn number or round end from mainframe
            values = Receive(datalink)
            action = values[0]

            if action == "Turn":
                controller.DisplayTurn(values[1])
            elif action == "Win":
                inRound = False

            # Loop until Betting Phase complete
            bettingComplete = False
            while inRound and not bettingComplete:
                # Get bet info from mainframe
                values = Receive(datalink)
                action = values[0]

                if action == "Bet":
                    highestBet = int(values[1])
                    funds = int(values[2])

                    # Send chosen bet option to mainframe
                    Transmit(controller.RequestBetting(highestBet, funds), datalink, mainframe)

                    # Get remaining funds from mainframe
                    values = Receive(datalink)
                    funds = int(values[1])
                    controller.DisplayFunds(funds)
                    UpdateSave(funds, parser, saveFile)
                    # Get betting cycle status from mainframe
                    if Receive(datalink)[1] == "False":
                        bettingComplete = False
                    else:
                        bettingComplete = True
                elif action == "Round":
                    # Get betting cycle status from mainframe
                    if values[1] == "False":
                        bettingComplete = False
                    else:
                        bettingComplete = True
                    controller.DisplayOutcome(values[2], values[3], int(values[4]))

# DRAW PHASE START
#
# # Retrieve Draw Phase fees paid
# funds, gamePotFees, sabaccPotFees = controller.RequestFee(funds, drawFees)
#
# # Transmit fee to mainframe
# Transmit("Fee:"+str(gamePotFees)+":"+str(sabaccPotFees), datalink, mainframe)
#
# # Notify player of available funds and update CFG
# controller.DisplayFunds(funds)
# model.UpdateSave(funds, parser, saveFile)
#
# DRAW PHASE END
#

        if dealer:
            Transmit("Winner:" + str(
                controller.RequestWinner(values[1], int(values[2]))) +
                     ":" + controller.RequestHand(), datalink, mainframe)
        values = Receive(datalink)
        message = values[0]
        controller.DisplayMessage(message)
        if message.startswith("You won "):
            funds += int(message[8:message.index(" credits")])
        controller.DisplayFunds(funds)
        UpdateSave(funds, parser, saveFile)
