from importlib import import_module

# TODO: Multiple Rounds, Joining,
#  Comments, Optimization,
#  Quitting


# Class representing an instance of a player
class Player(object):
    # Member variables:
    #  droid: Tuple of socket address
    #  player: String of player's name
    #  funds: Integer of player's current funds remaining
    #  contribution: Integer of player's total bet in current betting phase
    #  folded: Boolean of whether or not player has folded in current round
    def __init__(self, droid=("", 2187), name="", funds=0, contribution=0,
                 folded=False):
        # initialize member variables
        self.droid = droid
        self.name = name
        self.funds = funds
        self.contribution = contribution
        self.folded = folded

    # Class method for resetting all players' contributions back to zero
    def clear_contribution(self):
        import gc
        for instance in (obj for obj in gc.get_referrers(self.__class__)
                         if isinstance(obj, self.__class__)):
            instance.contribution = 0

    # Class method for checking if the current Betting Cycle/Phase is complete
    def check_complete(self, highestBet):
        import gc
        for instance in (obj for obj in gc.get_referrers(self.__class__)
                         if isinstance(obj, self.__class__)):
            if not instance.folded and instance.contribution != highestBet:
                return False
        return True

    # Class method for resetting all players' folded status back to false
    def unfold(self):
        import gc
        for instance in (obj for obj in gc.get_referrers(self.__class__)
                         if isinstance(obj, self.__class__)):
            instance.folded = False

    # Purpose: Class method to transmit message to droid
    # Arguments: Transmit message (string), datalink (socket)
    # Returns: None
    def unicast(self, message, datalink):
        # Convert message to UTF-8 Bytes and transmit
        datalink.sendto(bytes(message, "utf-8"), self.droid)

    # Purpose: Class method to transmit message to all connected droids
    # Arguments: Transmit message (string), datalink (socket)
    # Returns: None
    def broadcast(self, message, datalink):
        import gc
        for instance in (obj for obj in gc.get_referrers(self.__class__)
                         if isinstance(obj, self.__class__)):
            if not instance.folded:
                # Convert message to UTF-8 Bytes and transmit to all droids
                datalink.sendto(bytes(message, "utf-8"), instance.droid)


# Purpose: Transmit message to droid
# Parameters: Transmit message (string), datalink (socket), droid (address)
# Returns: None
def Unicast(message, datalink, droid):
    # Convert message to UTF-8 Bytes and transmit
    datalink.sendto(bytes(message, "utf-8"), droid)


# Purpose: Transmit message to specified connected droids
# Parameters: Transmit message (string), datalink (socket),
#             included droids (list of addresses)
# Returns: None
def Multicast(message, datalink, included):
    # Iterate through each specified connected droid
    for droid in included:
        # Convert message to UTF-8 Bytes and transmit
        datalink.sendto(bytes(message, "utf-8"), droid)


# Purpose: Transmit message to all connected droids
# Parameters: Transmit message (string), datalink (socket),
#             droids (list of addresses)
# Returns: None
def Broadcast(message, datalink, droids):
    # Iterate through each connected droid
    for droid in droids:
        # Convert message to UTF-8 Bytes and transmit
        datalink.sendto(bytes(message, "utf-8"), droid)


# Purpose: Receive message from a droid
# Parameters: Datalink (socket)
# Returns: Droid (address), values (list)
def Receive(datalink):
    # Receive message with recommended buffer size and identify droid
    message, droid = datalink.recvfrom(4096)
    # Convert from UTF-8 Bytes
    message = str(message.decode("utf-8"))

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

    # Return droid address and values
    return droid, values


# Purpose: Identify which player transmitted a message
# Parameters: Droid (address), players (list of Players)
# Returns: Transmitting player (Player instance), index of player (integer)
def Identify(droid, players):
    index = 0
    for player in players:
        if player.droid == droid:
            return player, index
        index += 1


# Purpose: Receive message from droid
# Parameters: Players in order (list of Player instances), datalink (socket),
#             house rule (list)
# Returns: None
def Play(players, datalink, rule):
    # Initialize both pots, current highest bet, and turn counter to zero
    gamePot = 0
    sabaccPot = 0
    turn = 0

    # Initialize list of folded players
    folded = []

    # Initialize ante amounts and phase ordering
    gamePotAnte = rule[1]
    sabaccPotAnte = rule[2]
    totalAnte = gamePotAnte + sabaccPotAnte
    order = rule[3]

    # Initialize boolean keeping track of whether all players have anted-in
    allAnte = False

    # Constantly listen for message from clients until all have payed the ante
    while not allAnte:
        # Wait for message from client
        droid, values = Receive(datalink)
        action = values[0]
        # Determine player index
        player, index = Identify(droid, players)

        # Process starting funds
        if action == "Start":
            # Set player funds
            player.funds = int(values[1])

            # Notify player of house rule details including title,
            # Game Pot ante, Sabacc Pot ante, and Draw Phase fees
            player.unicast(rule[0] + ":" + str(rule[1]) + ":" +
                           str(rule[2]) + ":" + str(rule[4]), datalink)

            print(action, player.name, player.funds)

        # Process ante
        elif action == "Ante":
            # Check if player has enough funds to pay ante
            if player.funds >= totalAnte:
                # Increment both pots by corresponding ante
                gamePot += gamePotAnte
                sabaccPot += sabaccPotAnte

                # Deduct ante from player funds
                player.funds -= totalAnte

                # Notify player of succesful ante
                player.unicast("Ante OK:" + str(player.funds), datalink)

                print(action, player.name, gamePot, sabaccPot)

                # Check if all players have payed the ante
                if gamePot == (len(players) * gamePotAnte):
                    # Proceed to first turn
                    allAnte = True
            else:
                # Notify player of elimination from game
                player.unicast("Ante failed:" + str(player.funds), datalink)

                # Remove player instance from list
                players.pop(index)

                # Check if only one player left
                if len(players) <= 1:
                    players[0].unicast("Last:" +
                                       str(sabaccPot), datalink)
                    # End game
                    exit(0)

                print("Elimination. Players remaining:", len(players))

        # Reject player attempting to join already filled session
        elif action == "Joined":
            Unicast("Reject", datalink, droid)

            print("Rejected extra player " + values[1])

    # Iterate through phase ordering of selected house rule
    for section in order:
        # Start of turn
        if section == 0:
            # Increment counter
            turn += 1
            # Notify all players of current turn number
            players[0].broadcast("Turn:" + str(turn), datalink)

            print("Turn", turn)

        # Betting Phase
        elif section == 1:
            # Reset all contributions to zero
            players[0].clear_contribution()
            highestBet = 0

            # Declare/Reset phase end to False
            over = False
            cycled = False
            index = 0
            droid = ""
            values = ""

            # Notify all players of Betting Phase
            players[0].broadcast("Betting:", datalink)

            # Loop until end of phase
            while not over:
                # Get next player in betting cycle
                player = players[index]

                # Eliminate player if not enough funds to call
                if player.funds < highestBet:
                    # Notify player of elimination
                    player.unicast("Eliminated", datalink)
                    # Remove player instance from list
                    players.pop(index)

                    # Check if more players remaining
                    if len(players) > 1:
                        # Reset index if last player in list eliminated
                        if index == len(players):
                            index = 0
                        # Get next player in betting cycle
                        player = players[index]
                    # Otherwise, if only one player left, notify them of win
                    else:
                        players[0].unicast("Last:" +
                                           str(gamePot + sabaccPot), datalink)
                        # End game
                        exit(0)

                    print("Elimination. Players remaining:", len(players))

                # Ask player for bet
                player.unicast("Bet:" + str(highestBet), datalink)
                # Wait for bet from client
                while droid != player.droid:
                    droid, values = Receive(datalink)
                action = values[0]

                # Process fold whether or not any player opened
                if action == "Fold":
                    # Denote that player folded
                    player.folded = True
                    # Pop from list of players into list of folded players
                    folded.append([index, players.pop(index)])
                    # Offset index
                    index -= 1

                    if len(players) <= 1:
                        player.unicast("Over:" + players[0].name + ":" +
                                       str(gamePot), datalink)
                        players[0].unicast("Unfolded:" + str(gamePot), datalink)
                        droid, values = Receive(datalink)
                        action = values[0]
                        # If proceeding to Single Blind Card Draw
                        if action == "s":
                            # Set all players to not folded status
                            players[0].unfold()
                            for index in range((len(folded) - 1), -1, -1):
                                players.insert(folded[index][0],
                                               folded[index][1])
                            # Ask dealer who won
                            message = "Win:"
                            indexOne = 1
                            for player in players:
                                message += "\t" + player.name + " (" + str(
                                    indexOne) + ")\n"
                                indexOne += 1
                            players[-1].unicast(
                                message + ":" + str(indexOne - 1), datalink)

                            droid = ""
                            values = ""
                            # Wait for message from dealer
                            while droid != players[-1].droid or\
                                    values[0] != "Winner":
                                droid, values = Receive(datalink)
                            winner = players[int(values[1])]
                            # Calculate winnings
                            winnings = gamePot + sabaccPot
                            # Transfer both pots to winner
                            winner.funds += winnings

                            winner.unicast("Won:" + str(winnings), datalink)

                            included = []
                            for player in players:
                                if player.droid != winner.droid:
                                    included.append(player.droid)
                            Multicast(
                                "Lost:" + str(winnings) + ":" + winner.name,
                                datalink, included)

                            # Reset both pots
                            gamePot = 0
                            sabaccPot = 0
                            exit(0)
                        # Otherwise, if proceeding to next round
                        elif action == "n":
                            players.broadcast("Next", datalink)
                    else:
                        player.unicast("Folding:", datalink)

                # Check if no player has yet opened
                if highestBet == 0:
                    # Process pass
                    if action == "Pass":
                        # No operation
                        # Literally pass, lol
                        pass
                    # Process open
                    elif action == "Open":
                        # Update current highest bet
                        highestBet = int(values[1])

                        # Add bet to Game Pot
                        gamePot += highestBet

                        # Add bet to player contribution
                        player.contribution = highestBet

                        # Deduct bet from player funds
                        player.funds -= highestBet
                # Check if a player has opened
                elif highestBet > 0:
                    # Process call
                    if action == "Call":
                        # Calculate bet difference
                        bet = highestBet - player.contribution

                        # Add bet difference to Game Pot
                        gamePot += bet

                        # Set player contribution to current highest bet
                        player.contribution = highestBet

                        # Deduct bet difference from player funds
                        player.funds -= bet
                    # Process raise
                    elif action == "Raise":
                        # Extract new highest bet
                        highestBet = int(values[1])

                        # Calculate bet difference
                        bet = highestBet - player.contribution

                        # Add bet difference to Game Pot
                        gamePot += bet

                        # Set player contribution to new highest bet
                        player.contribution = highestBet

                        # Deduct bet difference from player funds
                        player.funds -= bet

                player.unicast("Funds:" + str(player.funds), datalink)

                index += 1
                if index >= len(players):
                    index = 0
                    cycled = True
                if len(players) == 1:
                    over = True
                elif cycled:
                    over = player.check_complete(highestBet)
                player.broadcast("Round:" + str(over) + ":" + player.name +
                                 ":" + action + ":" + str(highestBet),
                                 datalink)

                print(action, player.name, gamePot, highestBet)

        # Draw Phase fee
        elif section == 2:
            # Loop until all players have processed any Draw Phase Fees
            for player in players:
                droid = ""
                values = ""
                player.unicast("Fee:", datalink)
                # Wait for message from client
                while droid != player.droid:
                    droid, values = Receive(datalink)
                action = values[0]
                gamePotFee = int(values[1])
                sabaccPotFee = int(values[2])
                # Process Draw Phase Fee
                # Increment both pots by respective fee
                gamePot += gamePotFee
                sabaccPot += sabaccPotFee

                # Deduct fees from player funds
                player.funds -= (gamePotFee + sabaccPotFee)

                player.unicast("Funds:" + str(player.funds), datalink)

                print(action, player.name, gamePot, sabaccPot)

    # Ask dealer who won
    message = "Win:"
    indexOne = 1
    for player in players:
        message += "\t" + player.name + " (" + str(indexOne) + ")\n"
        indexOne += 1
    players[0].broadcast(message + ":" + str(indexOne - 1), datalink)

    droid = ""
    values = ""
    # Wait for message from dealer
    while droid != players[-1].droid or values[0] != "Winner":
        droid, values = Receive(datalink)

    winner = players[int(values[1])]

    # Set all players to not folded status
    players[0].unfold()
    for index in range((len(folded) - 1), -1, -1):
        players.insert(folded[index][0], folded[index][1])

    # Process Nulrhek win
    if values[2] == "n":
        # Transfer Game Pot to winner
        winner.funds += gamePot

        winner.unicast("Won:" + str(gamePot), datalink)

        included = []
        for player in players:
            if player.droid != winner.droid:
                included.append(player.droid)
        Multicast("Lost:" + str(gamePot) + ":" + winner.name,
                  datalink, included)

        # Reset Game Pot
        gamePot = 0

        print("Nulrhek", winner.name)

        droid = ""
        # Wait for message from dealer
        while droid != players[-1].droid:
            droid, values = Receive(datalink)
        action = values[0]
        # If proceeding to Single Blind Card Draw
        if action == "s":
            # Ask dealer who won
            message = "Win:"
            indexOne = 1
            for player in players:
                message += "\t" + player.name + " (" + str(indexOne) + ")\n"
                indexOne += 1
            players[-1].unicast(message + ":" + str(indexOne - 1), datalink)

            droid = ""
            values = ""
            # Wait for message from dealer
            while droid != players[-1].droid or values[0] != "Winner":
                droid, values = Receive(datalink)
            winner = players[int(values[1])]
        # Otherwise, if proceeding to next round
        elif action == "n":
            players.broadcast("Next", datalink)
            # Bypass Sabacc win with dummy values
            values = ["", "", ""]

    # Process Sabacc win
    if values[2] == "s":
        # Calculate winnings
        winnings = gamePot + sabaccPot
        # Transfer both pots to winner
        winner.funds += winnings

        winner.unicast("Won:" + str(winnings), datalink)

        included = []
        for player in players:
            if player.droid != winner.droid:
                included.append(player.droid)
        Multicast("Lost:" + str(winnings) + ":" + winner.name,
                  datalink, included)

        # Reset both pots
        gamePot = 0
        sabaccPot = 0

        print("Sabacc", winner.name)


def QueueFilter(dealerName, dealerDroid, queue, datalink):
    # Initialize variables to null
    action = ""
    values = ""
    # Wait for dealer to provide awaited input
    while action != "Rule" and action != "Quantity":
        # Wait to receive message from dealer
        droid, values = Receive(datalink)
        action = values[0]
        # Check if received message was not from dealer
        if droid != dealerDroid:
            # Ensure message is for player joining
            while action != "Joined":
                Unicast("TRUE", datalink, droid)
                droid, values = Receive(datalink)
                action = values[0]

            name = values[1]
            while name in queue or name == dealerName:
                Unicast("Conflict", datalink, droid)
                droid, values = Receive(datalink)
                action = values[0]
                while action != "Joined":
                    Unicast("TRUE", datalink, droid)
                    droid, values = Receive(datalink)
                    action = values[0]
                name = values[1]

            Unicast("Success", datalink, droid)

            # Add player to queue
            queue.append([values[1], droid])
            Unicast("Wait", datalink, droid)
    return queue, int(values[1])


# Purpose: Setup session
# Parameters: Program version (string), import_module (module)
# Returns: None
def Setup(version, importModule):
    # Initialize current number of players (zero-based)
    quantityZero = 0
    # Initialize current number of players (one-based)
    quantityOne = 1
    # Initialize list of players
    players = []
    # Initialize queue of pending players
    queue = []

    # Import networking package
    from socket import socket, AF_INET, SOCK_DGRAM
    # Setup datalink
    datalink = socket(AF_INET, SOCK_DGRAM)
    # Accept any IP address known to the host system using port 2187
    datalink.bind(("", 2187))

    print("Mainframe activated")

    # Wait for first player to join session
    droid, values = Receive(datalink)
    action = values[0]

    # Ensure message is for player joining
    while action != "Joined":
        Unicast("TRUE", datalink, droid)
        droid, values = Receive(datalink)
        action = values[0]
    dealerName = values[1]
    Unicast("Success", datalink, droid)
    print(action, dealerName)
    
    # Save dealer droid address
    dealerDroid = droid
    # Add dealer player instance to list
    players.append(Player(dealerDroid, dealerName))

    # Notify initial player they will be the dealer for first round
    Unicast("Dealer", datalink, dealerDroid)

    # Wait for dealer to input chosen house rule
    queue, value = QueueFilter(dealerName, dealerDroid, queue, datalink)

    # Set dealer input to house rule
    houseRules = importModule("HouseRules" + version)
    rule = houseRules.rulesList[value]
    print("House Rule set to " + rule[0])

    # Wait for dealer to input number of players
    queue, total = QueueFilter(dealerName, dealerDroid, queue, datalink)
    print("Player cap set to " + str(total))

    print("Queue", queue)

    # While round player limit not exceeded
    while quantityOne < total and quantityZero < len(queue):
        droid = queue[quantityZero][1]
        name = queue[quantityZero][0]

        # Add player instance to list
        players.append(Player(droid, name))

        # Notify dealer of joining player
        Unicast("Joining:" + name + ":" + str(quantityOne + 1),
                datalink, dealerDroid)

        print(action, name)

        # Increment number of players joined
        quantityZero += 1
        quantityOne += 1

    # Reject extra players in queue
    if quantityOne == total:
        # Iterate through extra players in queue
        while quantityOne <= len(queue):
            # Reject extra player
            Unicast("Reject", datalink, queue[quantityZero][1])
            print("Rejected extra player " + queue[quantityZero][0])

            # Increment counters
            quantityZero += 1
            quantityOne += 1

    # If still not enough players, wait for the rest to join
    while quantityOne < total:
        Unicast("Wait", datalink, dealerDroid)
        # Reset action to null
        action = ""
        # Ensure message is for player joining
        while action != "Joined":
            Unicast("TRUE", datalink, droid)
            droid, values = Receive(datalink)
            action = values[0]

        names = []
        for player in players:
            names.append(player.name)

        name = values[1]
        while name in names:
            Unicast("Conflict", datalink, droid)
            droid, values = Receive(datalink)
            action = values[0]
            while action != "Joined":
                Unicast("TRUE", datalink, droid)
                droid, values = Receive(datalink)
                action = values[0]
            name = values[1]

        Unicast("Success", datalink, droid)
        print(action, name)

        # Add player instance to list
        players.append(Player(droid, name))

        Unicast("Wait", datalink, droid)

        # Notify dealer of joining player
        Unicast("Joining:" + name + ":" + str(quantityOne + 1),
                datalink, dealerDroid)

        # Increment number of players joined
        # quantityZero += 1 # should not be necessary at all at this point
        quantityOne += 1

    # Notify all players that all players have joined
    players[0].broadcast("All", datalink)

    # Wait for dealer to provide ordered player list
    while action != "Order":
        droid, values = Receive(datalink)
        action = values[0]
    # Import string to list converter
    from json import loads
    # Each element of string list must be enclosed
    # in double quotes for json.loads
    values[1] = values[1].replace(
                "['", '["').replace("']", '"]').replace("', '", '", "')
    # Extract player order
    playerOrder = loads(values[1])
    print(action, playerOrder)

    # Reorder the player instances list using the given order
    # Iterate through the player order
    for index, name in enumerate(playerOrder):
        # Iterate through the player instances list
        for player in players:
            # Find the player instance that matches the next player in the order
            if player.name == name:
                # Overwrite the name of the player with the
                # corresponding player instance
                playerOrder[index] = player
                # For increasingly faster performance, remove the
                # player instance from the player instances list,
                # thus making that list shorter
                players.remove(player)

    # Notify all players that round is ready to start
    playerOrder[0].broadcast("Ready", datalink)

    # Begin round
    Play(playerOrder, datalink, rule)


Setup("v2u3", import_module)
