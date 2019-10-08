# Purpose: Transmit message to mainframe
# Parameters: Transmit message (string), datalink (socket), mainframe (address)
# Returns: None
def Transmit(message, datalink, mainframe):
    # Convert message to UTF-8 Bytes and transmit
    datalink.sendto(bytes(str(message), "utf-8"), mainframe)

# Purpose: Receive message from mainframe
# Parameters: Datalink (socket)
# Returns: Received message (string)
def Receive(datalink):
    # Receive message with recommended buffer size and convert from UTF-8 Bytes
    return str((datalink.recv(4096)).decode("utf-8"))


# Purpose: Establish connection to server
# Parameters: Model (module), controller (module)
# Returns: Datalink (socket), mainframe (address)
def Connect(model, controller):
    # Import networking package
    from socket import socket, AF_INET, SOCK_DGRAM
    # Setup datalink
    datalink = socket(AF_INET, SOCK_DGRAM)
    
    # Identify mainframe
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

    # Initiialize connection status to unconnected
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

    # Retrieve player name
    player = model.Join(controller)
    # Transmit player joined
    Transmit("Joined:" + player, datalink, mainframe)

    # Wait for all players to join session
    while message != "All players have joined.":
        # Wait to receive message from mainframe
        message = Receive(datalink)
        if message != "TRUE":
            controller.DisplayMessage(message)

        # Check if player is current dealer
        if message == "You have been designated as the dealer for this round.":
            # Wait for dealer to provide valid number of players for round and transmit
            Transmit(controller.RequestPlayers(), datalink, mainframe)
        # Check if session is full
        elif message == "There are enough players for this round.":
            # Reject extra player
            controller.RequestOver()

    # Return datalink and mainframe
    return datalink, mainframe


# Purpose: Play round
# Parameters: Program version (string), import_module (module)
# Returns: None
def Play(version, import_module):
    # Import model
    model = import_module("DroidModel" + version)
    
    # Import controller
    controller = import_module("DroidController" + version)

    # Establish connection to mainframe
    datalink, mainframe = Connect(model, controller)

    # Import CFG parser
    from configparser import ConfigParser
    # Initialize CFG parser
    parser = ConfigParser()
    
    # Import parent directory name
    from os.path import dirname
    # Locate CFG
    saveFile = dirname(__file__) + "/DroidCache" + version + ".cfg"
    
    # Retrieve starting funds
    funds = model.Start(parser, saveFile, controller)
    
    # Import house rules
    houseRules = import_module("HouseRules" + version)
    # Retrieve house rule
    title, gamePotAnte, sabaccPotAnte, order, drawFees = controller.RequestRule(funds, houseRules.rulesList)
    
    # Initialize Sabacc Pot to empty
    sabaccPot = 0
    # Play rounds until program closes itself
    while True:
        # Notify player ante is being payed
        controller.DisplayAnte(gamePotAnte, sabaccPotAnte)
        # Deduct current funds by ante
        funds -= (gamePotAnte + sabaccPotAnte)

        # Transmit ante to mainframe
        Transmit("Ante:"+str(gamePotAnte)+":"+str(sabaccPotAnte), datalink, mainframe)

        # Reset Game Pot to Game Pot ante
        gamePot = gamePotAnte
        # Increment Sabacc Pot by Sabacc Pot ante
        sabaccPot += sabaccPotAnte

        # Notify player of available funds and update CFG
        controller.DisplayFunds(funds)
        model.UpdateSave(funds, parser, saveFile)

        # Initialize current turn counter and bet amount both to zero
        turn = 0
        bet = 0

        # Iterate through phase ordering of selected house rule
        for section in order:
            # Start of turn
            if section == 0:
                # Increment counter
                turn += 1
                # Notify player of current turn number
                controller.DisplayTurn(turn)
            # Betting Phase
            elif section == 1:
                # Initialize turn end and betting cycle end both to False
                turnOver = False
                end = False

                # Initialize player contribution to zero
                phaseSum = 0

                # Loop until end of turn
                while not turnOver:
                    # Wager a bet
                    funds, bet, turnOver, betType = model.Bet(funds, phaseSum, end, controller)

                    if betType != "Raise:":
                        # Transmit bet to mainframe
                        Transmit(betType + str(bet), datalink, mainframe)
                    else:
                        # Transmit raise to mainframe
                        Transmit(betType + str(bet) + ":" + str(phaseSum), datalink, mainframe)

                    # If not folded
                    if bet != -1:
                        # Increment player contribution by bet amount
                        phaseSum += bet
                        # Increment Game Pot by bet amount
                        gamePot += bet

                        # Notify player of available funds and update CFG
                        controller.DisplayFunds(funds)
                        model.UpdateSave(funds, parser, saveFile)
                        # Enable ability to directly end Betting Phase
                        end = True
                    # End turn if folded
                    else:
                        break
                # End round if folded
                if bet == -1:
                    break
            # Draw Phase fee
            elif section == 2:
                # Retrieve Draw Phase fees paid
                funds, gamePotFees, sabaccPotFees = controller.RequestFee(funds, drawFees)

                # Transmit fee to mainframe
                Transmit("Fee:"+str(gamePotFees)+":"+str(sabaccPotFees), datalink, mainframe)

                # Increment both pots by fees
                gamePot += gamePotFees
                sabaccPot += sabaccPotFees

                # Notify player of available funds and update CFG
                controller.DisplayFunds(funds)
                model.UpdateSave(funds, parser, saveFile)
        # Retrieve win results affecting current funds and Sabacc Pot
        funds, sabaccPot, winType = model.Win(funds, gamePot, sabaccPot, bet, controller)

        # Transmit win result to mainframe
        Transmit(winType, datalink, mainframe)

        # Notify player of available funds and update CFG
        controller.DisplayFunds(funds)
        model.UpdateSave(funds, parser, saveFile)

        # Check if player was cleaned out
        if funds <= 0:
            # Notify player of elimination
            controller.DisplayEliminated()

            # Transmit elimination to mainframe
            Transmit("Eliminated:", datalink, mainframe)

            # End game
            controller.RequestOver()

        # Retrieve next house rule
        title, gamePotAnte, sabaccPotAnte, order, drawFees = controller.RequestRule(funds, houseRules.rulesList)
