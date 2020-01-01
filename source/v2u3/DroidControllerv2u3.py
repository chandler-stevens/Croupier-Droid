# ##############################################################################
# Helpers
################################################################################


# Purpose: Determine if word should be plural or singular
# Parameters: Word (string), value (integer)
# Returns: Parsed word (string)
def AnalyzePlurality(word, value):
    if abs(int(value)) != 1:
        word += "s"
    return word


# Purpose: Validate player entered integer, valid equation, or 'x' cancel
# Parameters: Player input (string)
# Returns: Converted player input (integer) or raw player input (string),
#          validity (boolean)
def Validate(playerInput):
    # Remove all whitespace
    playerInput = "".join(playerInput.split())
    # Ensure input is not empty string or 'x' cancel
    if playerInput != "" and playerInput != "x":
        # Remove all thousand-separator commas
        playerInput = playerInput.replace(",", "")
        # Replace all 'x' characters with multiplication operator
        playerInput = playerInput.replace("x", "*")
        playerInput = playerInput.replace("X", "*")
        # Check if input is integer
        try:
            # Valid integer
            return int(playerInput), True
        except ValueError:
            # Check if input is valid equation
            for char in playerInput:
                # Valid equations only contain digits,
                # arithmetic operators, or decimal point
                if char not in "0123456789+-*/.":
                    return playerInput, False
            try:
                # Valid equation
                return int(eval(playerInput)), True
            except ValueError:
                # Catch-all of remaining possible invalid input
                return playerInput, False
    # Empty string and 'x' cancel are not valid integers
    return playerInput, False

# ##############################################################################
# Requests
################################################################################


# Purpose: Ask player for non-negative integer or 'x' cancel
# Parameters: Current funds (integer) or request type (string),
#             prompt for input (string),
#             extra value (integer or list of integers)
# Returns: Converted player input (integer) or 'x' cancel (string)
def Request(funds, message, value=0):
    # Ask until valid input given
    while True:
        # Ask player for valid input
        playerInput, valid = Validate(str(input(message)))
        # If input is integer
        if valid:
            # If input is positive integer
            if playerInput > 0:
                # Reject amount exceeding current funds
                if str(funds).isdigit() and playerInput > funds:
                    print("Insufficient Funds: You only have " + str(funds) +
                          " credits.")
                # Reject out of list bounds input for house rule
                elif funds == "rule" and playerInput > value:
                    print("Invalid Number: " +
                          "Please enter a valid house rule number.")
                # Reject invalid number of participating players
                elif funds == "players" and (
                        playerInput < 2 or playerInput > value):
                    print("Invalid Number: Please provide an integer\n" +
                          "\tfrom 2 up to " + str(value) + ".")
                # Reject nonexistent unordered player number
                elif (funds == "order" and playerInput not in value) or (
                        funds == "winner" and playerInput > value):
                    print("Invalid Player Number: " +
                          "Please enter a valid player number.")
                # Accept valid positive integer
                else:
                    return playerInput
            # Accept input of zero for current highest total bet
            elif funds == "highest" and playerInput == 0:
                return 0
        # Accept input of 'x' cancel unless request type is
        # for current highest total bet
        elif playerInput == "x" and funds != "highest":
            return "x"
        # Initialize rejected input message
        reject = "Invalid Input: Please enter a positive integer.\n"
        # Add 'x' cancel option to rejected input message unless request type is
        # for current highest total bet
        if funds != "highest":
            reject += "\tType (x) if you want to cancel."
        # Reject invalid input
        print(reject)


# Purpose: Notify player of connection failure
# Parameters: None
# Returns: None
def RequestUnconnected():
    return input("Wi-Fi Connection Error: Ensure that you are connected to\n" +
                 "\tWi-Fi and to the same Wi-Fi as the mainframe.\n" +
                 "\tPress 'Enter' when you are ready to retry.")


# Purpose: Clear startup console output and ask player for their name
# Parameters: Optional message (string)
# Returns: Player name (string)
def RequestJoin(message=""):
    from os import system, name
    # Clear console of any startup output
    system("cls" if name == "nt" else "clear")
    return input(message + "What is your name?\n\t")


# Purpose: Ask dealer for number of players for round
# Parameters: Maximum players allowed for house rule (integer)
# Returns: Number of players (integer)
def RequestPlayers(maximum):
    return Request("players", "How many total players, including yourself,\n" +
                              "are playing in this round?\n\t", maximum)


# Purpose: Ask dealer for next player in physical order
# Parameters: Most recently ordered player (string),
#             remaining unordered player names (list of strings),
#             remaining unordered player numbers (list of integers)
# Returns: Next player in physical order (integer)
def RequestOrder(player, playerList, numberOrder):
    # Display either the most recently ordered player or
    # the dealer's player name within prompt
    print("Please type the number of the player\n" +
          "that is sitting to the left of " + player + ":")
    # Display the remaining unordered players with their corresponding numbers
    for name in playerList:
        print("\t" + name)
    # Ask dealer for who the next player is in the physical ordering
    return Request("order", "\t", numberOrder)


# Purpose: Ask player for starting funds and
#          notify of remaining funds from last game
# Parameters: Funds left over from last game (integer)
# Returns: Starting funds (integer)
def RequestStart(lastFunds):
    # Ask player for starting funds and notify of previous funds
    return Request("start", "\nHow many credits are you starting with?\n" +
                   "Your previous game left you with " + str(lastFunds) +
                   AnalyzePlurality(" credit", lastFunds) + ".\n\t")


# Purpose: Ask player for chosen house rule
# Parameters: House rules (list)
# Returns: Index of chosen rule (integer)
def RequestRule(rulesList):
    # Initialize prompt for house rule
    prompt = "\nPlease type the number of your chosen house rule:\n"
    # Counter of house rules
    ruleCount = 0
    # Iterate through house rules list as one-based
    for index, rule in enumerate(rulesList, start=1):
        prompt += "\t" + rule[0] + " (" + str(index) + ")\n"
        # Increment counter of eligible house rules
        ruleCount += 1
    # Ensure eligibilty for at least one house rule
    if ruleCount > 0:
        # Ask user for chosen house rule
        choice = Request("rule", (prompt + "\t"), len(rulesList))
        # End game if input is 'x' cancel
        if choice == "x":
            RequestOver()
        # Send house rule index to model
        return choice - 1
    # End game
    else:
        RequestOver()


# Purpose: Ask player for chosen bet action
# Parameters: Current highest total bet (integer),
#             current player funds (integer)
# Returns: Chosen bet action to transmit to mainframe (string)
def RequestBetting(highestBet, funds):
    # Initialize betting options prompt
    message = "Please type the letter of your chosen bet:\n"
    options = ["f"]

    # If current funds is zero or no one has opened
    if funds == 0 or highestBet == 0:
        # Add pass option to prompt
        message += "\tPass/Check (p)\n"
        options.append("p")
        # If no one has opened and current funds greater than zero
        if highestBet == 0:
            # Add open option to prompt
            message += "\tOpen/Bet (o)\n"
            options.append("o")
    # If someone has opened and current funds greater than zero
    elif funds > 0 and highestBet > 0:
        # Add call and raise options to prompt
        message += "\tCall/See to " + str(highestBet) + " credits (c)\n"
        options.append("c")
        message += "\tRaise to " + str(highestBet + 1) + "+ credits (r)\n"
        options.append("r")
    # Add fold option to prompt
    message += "\tFold/Junk (f)\n\t"

    # Ask for chosen bet action
    choice = input(message).lower()
    while choice not in options:
        print("Invalid betting option: Please enter a valid letter.")
        choice = input(message).lower()

    if choice == "p":
        return "Pass"
    elif choice == "o":
        return "Open:" + str(RequestOpen(funds))
    elif choice == "c":
        return "Call"
    elif choice == "r":
        return "Raise:" + str(RequestRaise(funds, highestBet))
    return "Fold"


# Purpose: Ask player for amount to open betting cycle with
# Parameters: Current funds (integer)
# Returns: Open bet amount (integer) or 'x' cancel (string)
def RequestOpen(funds):
    return Request(funds, "How many credits would you like to open with?\n\t")


# Purpose: Ask player for amount to raise current highest total bet to
# Parameters: Current funds (integer), current highest total bet (integer)
# Returns: Raised total bet amount (integer) or 'x' cancel (string)
def RequestRaise(funds, highest):
    # Ask until valid input given
    while True:
        # Ask user for total raise amount
        bet = Request(funds, "How many credits would you like to raise\n" +
                             "\tthe current highest total bet to?\n\t")
        # Accept 'x' cancel
        if bet == "x":
            return "x"
        # Accept valid raise
        elif bet > highest:
            return bet
        # Reject invalid raise less than or equal to current highest total bet
        print("You must raise to at least " + str(highest + 1) + " credits.")


# Purpose: Ask player for Draw Phase fee
# Parameters: Current funds (integer), valid fees (list of 2 lists)
# Returns: Incurred Draw Phase fee (integer)
def RequestFee(funds, drawFees):
    # Initialize both fee amounts to zero
    gamePotFees = 0
    sabaccPotFees = 0
    # Check if any fees exist for Game Pot
    if len(drawFees[0]) > 0:
        # Initialize valid fee given to False
        valid = False
        # Ask until valid input given 
        while not valid:
            # Initialize Game Pot fee prompt
            print("\nHow much of a fee did you pay into the\n" +
                  "\tGame Pot during the Draw Phase?")
            # Add each eligible fee in house rule fee list to prompt
            for amount in drawFees[0]:
                # Only include fees not exceeding current funds
                if amount <= funds:
                    print("\t" + str(amount) + " credits (" + str(amount) + ")")
            # Ask player for selected Draw Phase fee
            fee = input("\t")
            # Ensure input is integer
            try:
                fee = int(fee)
                # Ensure input is available fee
                if fee in drawFees[0]:
                    gamePotFees = fee
                    valid = True
                # Reject invalid fee input
                else:
                    print("Invalid Number: " +
                          "Please enter a valid Draw Phase fee.")
            # Reject invalid input
            except ValueError:
                print("Invalid Input: Please enter a positive integer.")
    # Check if any fees exist for Sabacc Pot
    if len(drawFees[1]) > 0:
        # Initialize valid fee given to False
        valid = False
        # Ask until valid input given 
        while not valid:
            # Initialize Sabacc Pot fee prompt
            print("\nHow much of a fee did you pay into the\n" +
                  "\tSabacc Pot during the Draw Phase?")
            # Add each eligible fee in house rule fee list to prompt
            for amount in drawFees[1]:
                # Only include fees not exceeding current funds
                if amount <= funds:
                    print("\t" + str(amount) + " credits (" + str(amount) + ")")
            # Ask player for selected Draw Phase fee
            fee = input("\t")
            # Ensure input is integer
            try:
                fee = int(fee)
                # Ensure input is available fee
                if fee in drawFees[1]:
                    sabaccPotFees = fee
                    valid = True
                # Reject invalid fee input
                else:
                    print("Invalid Number: " +
                          "Please enter a valid Draw Phase fee.")
            # Reject invalid input
            except ValueError:
                print("Invalid Input: Please enter a positive integer.")
    # Accept valid fees
    return funds - gamePotFees - sabaccPotFees, gamePotFees, sabaccPotFees


# Purpose: Ask player for winner
# Parameters: List of potential winners (string),
#             number of potential winners (integer)
# Returns: Winner (string)
def RequestWinner(playerList, numPlayers):
    return Request("winner",
                   "\nPlease type the number of the winning player:\n" +
                   playerList + "\t", numPlayers) - 1


# Purpose: Ask player for winning hand
# Parameters: None
# Returns: Winning hand (string)
def RequestHand():
    hand = ""
    while hand != "s" and hand != "n":
        hand = (input("\nPlease type the letter of the winning hand:\n" +
                      "\tSabacc (s)\n" +
                      "\tNulrhek (n)\n\t")).lower()
    return hand


# Purpose: Ask player on how to proceed after Nulrhek win
# Parameters: None
# Returns: Action to proceed to (string)
def RequestProceed():
    action = ""
    while action != "n" and action != "s":
        action = (input("\nPlease type the letter of the chosen action:\n" +
                        "\tNext Round (n)\n" +
                        "\tSingle Blind Card Draw (s)\n\t")).lower()
    return action


# Purpose: Notify player that game is over without immediately closing program 
# Parameters: None
# Returns: None
def RequestOver():
    # Wait for player to acknowledge game is over
    input("Game Over.")
    # Close program
    exit()

# ##############################################################################
# Display
################################################################################


# Purpose: Notify player they are the designated dealer
# Parameters: None
# Returns: None
def DisplayDealer():
    print("You have been designated as the dealer for this round.")


# Purpose: Notify player of waiting for more players
# Parameters: None
# Returns: None
def DisplayWait():
    print("Waiting for other players to join.")


# Purpose: Notify player of name conflict
# Parameters: None
# Returns: None
def DisplayConflict():
    print("Another player already has that name.\n" +
          "Please provide a different name.\n")


# Purpose: Notify player they cannot join filled-up game
# Parameters: None
# Returns: None
def DisplayRejection():
    print("There are enough players for this round.")


# Purpose: Notify player of all players joined
# Parameters: None
# Returns: None
def DisplayAllJoined():
    print("All players have joined the round.")


# Purpose: Notify player that they provided an invalid selection
# Parameters: None
# Returns: None
def DisplaySelection():
    print("Invalid Selection: Please select\n\tan available option.")


# Purpose: Notify player that they have insufficient funds available
# Parameters: Current funds (integer)
# Returns: None
def DisplayInsufficient(funds):
    print("Insufficient Funds: You only have " + str(funds) +
          AnalyzePlurality(" credit", funds) + ".")


# Purpose: Notify player that they bought in with the corresponding ante
# Parameters: Game Pot ante (integer), Sabacc Pot ante (integer)
# Returns: None
def DisplayAnte(gamePotAnte, sabaccPotAnte):
    print("Buying in with an ante of\n\t" + str(gamePotAnte) +
          AnalyzePlurality(" credit", gamePotAnte) +
          " into the Game Pot and\n\t" + str(sabaccPotAnte) +
          AnalyzePlurality(" credit", sabaccPotAnte) + " into the Sabacc Pot.")


# Purpose: Notify player they have been eliminated from the game due to ante
# Parameters: None
# Returns: None
def DisplayFailedAnte():
    print("You have been eliminated from the game since\n" +
          "you do not have enough credits to mee the ante.")


# Purpose: Notify player of house rule
# Parameters: House rule title (string)
# Returns: None
def DisplayRule(title):
    print("Starting a round under " + title + " house rules.")


# Purpose: Notify player of current turn
# Parameters: Current turn (integer)
# Returns: None
def DisplayTurn(turn):
    print("\nStarting Turn # " + str(turn))


# Purpose: Notify player of play made by an opposing player
# Parameters: Opposing player name (string),
#             betting action (string), current highest bet (integer)
# Returns: None
def DisplayOutcome(name, action, highestBet):
    if action == "Open":
        print(name + " opened with " + str(highestBet) +
              AnalyzePlurality(" credit", highestBet) + ".")
    elif action == "Raise":
        print(name + " raised to " + str(highestBet) +
              AnalyzePlurality(" credit", highestBet) + ".")
    else:
        print(name + " " + action.lower() + "ed.")


# Purpose: Notify player of current funds
# Parameters: Current funds (integer)
# Returns: None
def DisplayFunds(funds):
    print("You now have " + str(funds) +
          AnalyzePlurality(" credit", funds) + ".\n")


# Purpose: Notify player they have been eliminated from the game
# Parameters: None
# Returns: None
def DisplayEliminated():
    print("\nYou have been eliminated from the game\n" +
          "since you do not have enough credits to\n" +
          "call the highest bet.")


# Purpose: Notify player they have won since only player left
# Parameters: Winnings (integer), game over (boolean)
# Returns: None
def DisplayLastPlayerStanding(winnings, gameOver):
    if gameOver:
        print("\nAll your opponents have been eliminated from the game!\n" +
              "Therefore, you won " + str(winnings) + " credits\n" +
              "from both the Sabacc Pot and Game Pot!")
    else:
        print("\nAll your opponents have folded.\n" +
              "Therefore, you win this round and\n" +
              "won " + str(winnings) + " credits from the Game Pot!")


# Purpose: Notify player that an opponent won since everyone else folded
# Parameters: Winner name (string), winnings (integer)
# Returns: None
def DisplayOver(name, winnings):
    print("\n\nAll but one of your opponents have folded.\n" +
          "Therefore, " + name + " won this round and\n" +
          "won " + str(winnings) + " credits from the Game Pot.\n")


# Purpose: Notify player of win result
# Parameters: Won (boolean), winnings (integer),
#             hand ("s", "n", or "sbcd"), winner name (string)
# Returns: None
def DisplayWinResult(won, amount, hand, name="You"):
    message = " won " + str(amount) + " credits with a "

    if hand == "s":
        message += "Sabacc"
    elif hand == "n":
        message += "Nulrhek"
    elif hand == "sbcd":
        message += "Single Blind Card Draw"

    if won:
        message += "!"
    else:
        message += "."

    print(name + message)
