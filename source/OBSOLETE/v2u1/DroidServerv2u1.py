# TODO: Comments, Draw Phase Fees, Multiple Rounds, Optimization


# Class representing an instance of a player
class Player(object):
    # Member variables:
    #  droid: Tuple of socket address
    #  player: String of player's name
    #  funds: Integer of player's current funds remaining
    #  contribution: Integer of player's current total bet in the current betting phase
    #  folded: Boolean of whether or not player has folded in current round
    def __init__(self, droid=("", 2187), name="", funds=0, contribution=0, folded=False):
        # initialize member variables
        self.droid = droid
        self.name = name
        self.funds = funds
        self.contribution = contribution
        self.folded = folded

    # Class method for resetting all players' contributions back to zero
    def clear_contribution(self):
        import gc
        for instance in (obj for obj in gc.get_referrers(self.__class__) if isinstance(obj, self.__class__)):
            instance.contribution = 0

    # Class method for checking if the current Betting Cycle/Phase is complete
    def check_complete(self, highestBet):
        import gc
        for instance in (obj for obj in gc.get_referrers(self.__class__) if isinstance(obj, self.__class__)):
            if not instance.folded and instance.contribution != highestBet:
                return False
        return True

    # Class method for resetting all players' folded status back to false
    def unfold(self):
        import gc
        for instance in (obj for obj in gc.get_referrers(self.__class__) if isinstance(obj, self.__class__)):
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
        for instance in (obj for obj in gc.get_referrers(self.__class__) if isinstance(obj, self.__class__)):
            # Convert message to UTF-8 Bytes and transmit to all droids
            datalink.sendto(bytes(message, "utf-8"), instance.droid)


# Purpose: Transmit message to droid
# Parameters: Transmit message (string), datalink (socket), droid (address)
# Returns: None
def Unicast(message, datalink, droid):
    # Convert message to UTF-8 Bytes and transmit
    datalink.sendto(bytes(message, "utf-8"), droid)


# Purpose: Transmit message to specified connected droids
# Parameters: Transmit message (string), datalink (socket), included droids (list of addresses)
# Returns: None
def Multicast(message, datalink, included):
    # Iterate through each specified connected droid
    for droid in included:
        # Convert message to UTF-8 Bytes and transmit
        datalink.sendto(bytes(message, "utf-8"), droid)


# Purpose: Transmit message to all connected droids
# Parameters: Transmit message (string), datalink (socket), droids (list of addresses)
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
# Parameters: Players in order (list of Player instances), datalink (socket), house rule (list)
# Returns: None
def Play(players, datalink, rule):
    # Initialize both pots, current highest bet, and turn counter to zero
    gamePot = 0
    sabaccPot = 0
    highestBet = 0
    turn = 0

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

                if len(players) == 1:
                    players[0].unicast("You are the only remaining player left.", datalink)
                    exit(0)

                print("Elimination. Players remaining:", players)

        # Reject player attempting to join already filled session
        elif action == "Joined":
            Unicast("There are enough players for this round.", datalink, droid)
            print("Rejected extra player " + values[1])

    # Set all players to not folded status
    players[0].unfold()

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

            # Loop until end of phase
            while not over:
                player = players[index]
                player.unicast("Bet:" + str(highestBet) + ":" + str(player.funds), datalink)
                # Wait for message from client
                while droid != player.droid:
                    droid, values = Receive(datalink)
                action = values[0]

                # Process fold whether or not any player opened
                if action == "Fold":
                    # Denote that player folded
                    player.folded = True

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
                if cycled:
                    over = player.check_complete(highestBet)
                player.broadcast("Round:" + str(over) + ":" + player.name +
                                 ":" + action + ":" + str(highestBet),
                                 datalink)

                print(action, player.name, gamePot, highestBet)

        # Draw Phase fee
        elif section == 2:
            # Wait for message from client
            droid, values = Receive(datalink)
            action = values[0]
            gamePotFee = values[1]
            sabaccPotFee = values[2]
            # Determine player index
            player, index = Identify(droid, players)

            # Process Draw Phase Fee
            if action == "Fee":
                # Increment both pots by respective fee
                gamePot += gamePotFee
                sabaccPot += sabaccPotFee

                # Deduct fees from player funds
                player.funds -= (gamePotFee + sabaccPotFee)
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

    # Process Nulrhek win
    if values[2] == "n":
        # Transfer Game Pot to winner
        winner.funds += gamePot

        winner.unicast("You won " + str(gamePot) +
                       " credits with a Nulrhek!", datalink)

        included = []
        for player in players:
            if player.droid != winner.droid:
                included.append(player.droid)
        Multicast(winner.name + " won " + str(gamePot) +
                  " credits with a Nulrhek.", datalink, included)

        # Reset Game Pot
        gamePot = 0

        print("Nulrhek", winner.name)
    # Process Sabacc win
    elif values[2] == "s":
        # Transfer both pots to winner
        winner.funds += gamePot + sabaccPot

        winner.unicast("You won " + str(gamePot + sabaccPot) +
                       " credits with a Sabacc!", datalink)

        included = []
        for player in players:
            if player.droid != winner.droid:
                included.append(player.droid)
        Multicast(winner.name + " won " + str(gamePot + sabaccPot) +
                  " credits with a Sabacc.", datalink, included)

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
                Unicast("Another player already has that name.\nPlease provide a different name.\n", datalink, droid)
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
            Unicast("Waiting for other players to join.", datalink, droid)
    return queue, int(values[1])


# Purpose: Setup session
# Parameters: Program version (string), import_module (module)
# Returns: None
def Setup(version, import_module):
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
    Unicast("You have been designated as the dealer for this round.", datalink, dealerDroid)

    # Wait for dealer to input chosen house rule
    queue, value = QueueFilter(dealerName, dealerDroid, queue, datalink)

    # Set dealer input to house rule
    houseRules = import_module("HouseRules" + version)
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
        Unicast(name + " (Player #" + str(quantityOne + 1) +
                 ") has joined the game.", datalink, dealerDroid)

        print(action, name)

        # Increment number of players joined
        quantityZero += 1
        quantityOne += 1

    # Reject extra players in queue
    if quantityOne == total:
        # Iterate through extra players in queue
        while quantityOne <= len(queue):
            # Reject extra player
            Unicast("There are enough players for this round.", datalink, queue[quantityZero][1])
            print("Rejected extra player " + queue[quantityZero][0])

            # Increment counters
            quantityZero += 1
            quantityOne += 1

    # If still not enough players, wait for the rest to join
    while quantityOne < total:
        Unicast("Waiting for other players to join.", datalink, dealerDroid)
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
            Unicast("Another player already has that name.\nPlease provide a different name.\n", datalink, droid)
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

        Unicast("Waiting for other players to join.", datalink, droid)

        # Notify dealer of joining player
        Unicast(name + " (Player #" + str(quantityOne + 1) +
                 ") has joined the game.", datalink, dealerDroid)

        # Increment number of players joined
        # quantityZero += 1 # should not be necessary at all at this point
        quantityOne += 1

    # Notify all players that all players have joined
    players[0].broadcast("All players have joined.", datalink)

    # Wait for dealer to provide ordered player list
    while action != "Order":
        droid, values = Receive(datalink)
        action = values[0]
    # Import string to list converter
    from json import loads
    # Each element of string list must be enclosed in double quotes for json.loads
    values[1] = values[1].replace("['", '["').replace("']", '"]').replace("', '", '", "')
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
                # Overwrite the name of the player with the corresponding player instance
                playerOrder[index] = player
                # For increasingly faster performance, remove the player instance from the player instances list, thus making that list shorter
                players.remove(player)

    # Notify all players of house rule details including title, Game Pot ante, Sabacc Pot ante, and Draw Phase fees
    playerOrder[0].broadcast(rule[0] + ":" + str(rule[1]) + ":" + str(rule[2]) + ":" + str(rule[4]), datalink)

    # Begin round
    Play(playerOrder, datalink, rule)
