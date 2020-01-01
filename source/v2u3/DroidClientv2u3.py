from importlib import import_module


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
# Parameters: controller (module), version (string), import_module (module)
# Returns: Datalink (socket), mainframe (address)
def Connect(controller, version, importModule):
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

    mainframe = ("127.0.0.1", 2187)  # #######################################

    # Ask for name until successfully joined
    message = ""
    player = ""
    while message != "Success":
        # Check for naming conflict
        if message == "Conflict":
            controller.DisplayConflict()
        # Retrieve player name
        player = controller.RequestJoin()

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
    while message != "All":
        # Wait to receive message from mainframe
        values = Receive(datalink)
        if len(values) >= 1:
            message = values[0]

            # Check if player is current dealer
            if message == "Dealer":
                # Set player as the dealer
                dealer = True
                controller.DisplayDealer()
                # Import house rules
                houseRules = importModule("HouseRules" + version)
                # Wait for dealer to provide valid house rule and transmit
                rule = controller.RequestRule(houseRules.rulesList)
                Transmit("Rule:" + str(rule), datalink, mainframe)
                # Wait for dealer to provide
                # valid number of players for round and transmit
                Transmit("Quantity:" +
                         str(controller.RequestPlayers(
                             houseRules.rulesList[rule][5])),
                         datalink, mainframe)
            # Check if dealer was notified that player joined
            elif dealer and message == "Joining":
                name = values[1]
                index = int(values[2])
                playerList.append(name + " (" + str(index) + ")")
                numberOrder.append(index)
            # Check if session is full
            elif message == "Reject":
                controller.DisplayRejection()
                # Reject extra player
                controller.RequestOver()
            # Check if waiting for more players
            elif message == "Wait":
                controller.DisplayWait()

    if not dealer:
        # Wait to receive ready message from mainframe
        values = [""]
        while values[0] != "Ready":
            values = Receive(datalink)
        # Notify all players that all players have joined
        controller.DisplayAllJoined()
    # Once all players have joined, ask dealer
    # to provide physical ordering of players
    else:
        controller.DisplayAllJoined()
        # Initialize order of players
        playerOrder = []
        # If there are more than two total players, including the dealer
        if len(playerList) > 1:
            # While the player list has more than one player
            while len(playerList) > 1:
                # If at least one player has already been properly ordered
                if len(playerOrder) != 0:
                    # Display most recently ordered player within prompt and
                    # the remaining unordered players
                    nextPlayer = controller.RequestOrder(playerOrder[-1],
                                                         playerList,
                                                         numberOrder)
                # Otherwise, if no players have been ordered yet
                else:
                    # Display dealer's player name within prompt and
                    # the remaining unordered players
                    nextPlayer = controller.RequestOrder(player, playerList,
                                                         numberOrder)
                # Remove the player from the list of unordered player numbers
                numberOrder.remove(nextPlayer)
                # Remove the player from the list of unordered player names
                #  and add the player name to the list of ordered players
                target = playerList.pop(nextPlayer - 2)
                playerOrder.append(target[:target.index(" (")])
            # Add the final remaining player name to the ordered list
            target = playerList.pop()
            playerOrder.append(target[:target.index(" (")])
        # Otherwise, if there is just one player playing against the dealer
        elif len(playerList) == 1:
            # Begin the ordered list with the opposing player
            target = playerList[0]
            playerOrder.append(target[:target.index(" (")])
        # Add the dealer's player name to the very end of the ordered list
        playerOrder.append(player)
        # Transmit ordered list of players to mainframe
        Transmit("Order:" + str(playerOrder), datalink, mainframe)
        # Capture unneeded ready message
        Receive(datalink)

    # Return datalink, mainframe, and dealer status
    return datalink, mainframe, dealer


# Purpose: Get starting funds or end game
# Parameters: CFG parser (ConfigParser), CFG file path (string),
#             controller (module)
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
# Parameters: Current funds (integer),
#             CFG parser (ConfigParser), CFG file path (string)
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
def Play(version, importModule):
    # Import controller
    controller = importModule("DroidController" + version)
    # Establish connection to mainframe
    datalink, mainframe, dealer = Connect(controller, version, importModule)

    # Import CFG parser
    from configparser import ConfigParser
    # Initialize CFG parser
    parser = ConfigParser()
    
    # Import parent directory name
    from os.path import dirname
    # Locate CFG
    saveFile = dirname(__file__) + "/DroidCache" + version + ".cfg"
    
    # Ask for starting funds
    funds = Start(parser, saveFile, controller)

    # Transmit starting funds to mainframe
    Transmit("Start:" + str(funds), datalink, mainframe)

    # Play rounds until eliminated
    while funds > 0:
        # Retrieve chosen house rule details message
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
        controller.DisplayRule(title)

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
            controller.DisplayFailedAnte()
            # Notify player of available funds and update CFG
            controller.DisplayFunds(funds)
            UpdateSave(funds, parser, saveFile)
            # End game
            controller.RequestOver()

        # Initialize round to not over
        inRound = True
        # Loop until round is over
        while inRound:
            # Get message from mainframe
            values = Receive(datalink)
            action = values[0]

            # Check if starting a new turn
            if action == "Turn":
                controller.DisplayTurn(values[1])
            # Otherwise, if currently in a Betting Phase
            elif action == "Betting":
                # Initialize betting cycle to unfinished
                bettingComplete = False
                # Loop until Betting Phase complete and while round not over
                while inRound and not bettingComplete:
                    # Get bet info from mainframe
                    values = Receive(datalink)
                    action = values[0]

                    # If player needs to make a bet
                    if action == "Bet":
                        highestBet = int(values[1])

                        # Send chosen bet option to mainframe
                        bet = controller.RequestBetting(highestBet, funds)
                        Transmit(bet, datalink, mainframe)

                        # Get remaining funds from mainframe
                        values = Receive(datalink)
                        result = values[0]
                        if result == "Over":
                            controller.DisplayOver(values[1],
                                                   int(values[2]))
                            # Get decision
                            while result != "Next" and \
                                    result != "Won" and result != "Lost":
                                values = Receive(datalink)
                                result = values[0]
                            # If proceeding to next round
                            if result == "Next":
                                controller.DisplayNext()
                            # Otherwise, if proceeding to Single Blind Card Draw
                            else:
                                # If player won Single Blind Card Draw
                                if result == "Won":
                                    amount = int(values[1])
                                    # Display congratulations
                                    controller.DisplayWinResult(True, amount,
                                                                "sbcd")
                                    # Award winnings
                                    funds += amount
                                # Otherwise, if opponent won
                                # Single Blind Card Draw
                                elif result == "Lost":
                                    amount = int(values[1])
                                    # Display who won and
                                    # how much was won by the winner
                                    controller.DisplayWinResult(False, amount,
                                                                "sbcd",
                                                                values[2])
                                # Notify player of available funds and
                                # update CFG
                                controller.DisplayFunds(funds)
                                UpdateSave(funds, parser, saveFile)
                                # End game
                                controller.RequestOver()
                        funds = int(values[1])
                        # Notify player of available funds and update CFG
                        controller.DisplayFunds(funds)
                        UpdateSave(funds, parser, saveFile)

                        # Check if player did not fold
                        if bet != "Fold":
                            # If betting cycle finished
                            if Receive(datalink)[1] == "False":
                                # End betting cycle
                                bettingComplete = False
                            # Otherwise, if betting cycle not finished
                            else:
                                # Continue betting cycle
                                bettingComplete = True
                        # Otherwise, if player did fold
                        else:
                            # End betting cycle and end round
                            bettingComplete = True
                            inRound = False
                    # Otherwise, if getting update of round details
                    elif action == "Round":
                        # If betting cycle finished
                        if values[1] == "False":
                            # End betting cycle
                            bettingComplete = False
                        # Otherwise, if betting cycle not finished
                        else:
                            # Continue betting cycle
                            bettingComplete = True
                        # Display resulting outcome in betting cycle
                        controller.DisplayOutcome(values[2], values[3],
                                                  int(values[4]))
                    # Otherwise, if player is only one not folded
                    elif action == "Unfolded":
                        winnings = int(values[1])
                        # Add winnings to player funds
                        funds += winnings
                        controller.DisplayLastPlayerStanding(winnings, False)
                        # Notify player of available funds and update CFG
                        controller.DisplayFunds(funds)
                        UpdateSave(funds, parser, saveFile)
                        # Check if player is dealer
                        if dealer:
                            # Ask dealer how to proceed
                            # Either go on to next round or
                            # end with Single Blind Card Draw
                            action = controller.RequestProceed()
                            # Transmit decision to mainframe
                            Transmit(action, datalink, mainframe)
                            # If ending with Single Blind Card Draw
                            if action == "s":
                                # Receive player list and number of players
                                values = Receive(datalink)
                                # Ask dealer who won the Single Blind Card Draw
                                winner = str(
                                    controller.RequestWinner(values[1],
                                                             int(values[2])))
                                # Transmit winner to mainframe
                                # use "s" as alias for Single Blind Card Draw
                                # so that it evaluates the same as a Sabacc
                                Transmit("Winner:" + winner + ":s", datalink,
                                         mainframe)

                        # Get decision
                        values = Receive(datalink)
                        result = values[0]
                        # If proceeding to next round
                        if result == "Next":
                            controller.DisplayNext()
                        # Otherwise, if proceeding to Single Blind Card Draw
                        else:
                            # If player won Single Blind Card Draw
                            if result == "Won":
                                amount = int(values[1])
                                # Display congratulations
                                controller.DisplayWinResult(True, amount,
                                                            "sbcd")
                                # Award winnings
                                funds += amount
                            # Otherwise, if opponent won Single Blind Card Draw
                            elif result == "Lost":
                                amount = int(values[1])
                                # Display who won and
                                # how much was won by the winner
                                controller.DisplayWinResult(False, amount,
                                                            "sbcd", values[2])
                            # Notify player of available funds and update CFG
                            controller.DisplayFunds(funds)
                            UpdateSave(funds, parser, saveFile)
                            # End game
                            controller.RequestOver()
                    # Otherwise, if player is only one not eliminated
                    elif action == "Last":
                        winnings = int(values[1])
                        # Add winnings to player funds
                        funds += winnings
                        controller.DisplayLastPlayerStanding(winnings, True)
                        # Notify player of available funds and update CFG
                        controller.DisplayFunds(funds)
                        UpdateSave(funds, parser, saveFile)
                        controller.RequestOver()
                    # Otherwise, if player was eliminated
                    elif action == "Eliminated":
                        controller.DisplayEliminated()
                        controller.DisplayFunds(funds)
                        controller.RequestOver()
            # Otherwise, if asking for Draw Phase Fee
            elif action == "Fee":
                # Retrieve Draw Phase fees paid
                funds, gamePotFees, sabaccPotFees = controller.RequestFee(
                                                                funds, drawFees)

                # Transmit fee to mainframe
                Transmit("Paid:" + str(gamePotFees) + ":" +
                         str(sabaccPotFees), datalink, mainframe)

                # Get remaining funds from mainframe
                values = Receive(datalink)
                funds = int(values[1])
                # Notify player of available funds and update CFG
                controller.DisplayFunds(funds)
                UpdateSave(funds, parser, saveFile)
            # Otherwise, if round over
            elif action == "Win":
                inRound = False

        # Determine win results
        hand = "n"
        # Check if player is dealer
        if dealer:
            # Ask dealer which player was the winner
            winner = str(controller.RequestWinner(values[1], int(values[2])))
            # Ask dealer which hand the winner had
            hand = controller.RequestHand()
            # Transmit win results to mainframe
            Transmit("Winner:" + winner + ":" + hand, datalink, mainframe)

        # Display win results
        values = Receive(datalink)
        result = values[0]
        # Check if player won
        if result == "Won":
            amount = int(values[1])
            # Display congratulations
            controller.DisplayWinResult(True, amount, hand)
            # Award winnings
            funds += amount
        # Otherwise, if opponent won
        elif result == "Lost":
            amount = int(values[1])
            # Display who won and how much was won by the winner
            controller.DisplayWinResult(False, amount, hand, values[2])
        # Notify player of available funds and update CFG
        controller.DisplayFunds(funds)
        UpdateSave(funds, parser, saveFile)

        # Check if hand was Nulrhek since Single Blind Card Draw may follow
        if hand == "n":
            # Check if player is dealer
            if dealer:
                # Ask dealer how to proceed
                # Either go on to next round or end with Single Blind Card Draw
                action = controller.RequestProceed()
                # Transmit decision to mainframe
                Transmit(action, datalink, mainframe)
                # If ending with Single Blind Card Draw
                if action == "s":
                    # Receive player list and number of players
                    values = Receive(datalink)
                    # Ask dealer who won the Single Blind Card Draw
                    winner = str(controller.RequestWinner(values[1],
                                                          int(values[2])))
                    # Transmit winner to mainframe
                    # use "s" as alias for Single Blind Card Draw
                    # so that it evaluates the same as a Sabacc
                    Transmit("Winner:" + winner + ":s", datalink, mainframe)

            # Get decision
            values = Receive(datalink)
            result = values[0]
            # If proceeding to next round
            if result == "Next":
                controller.DisplayNext()
            # Otherwise, if proceeding to Single Blind Card Draw
            else:
                # If player won Single Blind Card Draw
                if result == "Won":
                    amount = int(values[1])
                    # Display congratulations
                    controller.DisplayWinResult(True, amount, "sbcd")
                    # Award winnings
                    funds += amount
                # Otherwise, if opponent won Single Blind Card Draw
                elif result == "Lost":
                    amount = int(values[1])
                    # Display who won and how much was won by the winner
                    controller.DisplayWinResult(False, amount, "sbcd",
                                                values[2])
                # Notify player of available funds and update CFG
                controller.DisplayFunds(funds)
                UpdateSave(funds, parser, saveFile)
                # End game
                controller.RequestOver()


Play("v2u3", import_module)
