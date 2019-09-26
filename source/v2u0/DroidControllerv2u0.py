# Purpose: Determine if word should be plural or singular
# Parameters: Word (string), value (integer)
# Returns: Parsed word (string)
def AnalyzePlurality(word, value):
    if abs(int(value)) != 1:
        word += "s"
    return word

# Purpose: Validate player entered integer, valid equation, or 'x' cancel
# Parameters: Player input (string)
# Returns: Converted player input (integer) or raw player input (string), validity (boolean)
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
                # Valid equations only contain digits, arithmetic operators, or decimal point
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


# Purpose: Ask player for non-negative integer or 'x' cancel
# Parameters: Current funds (integer) or request type (string), prompt for input (string), house rules quantity (integer)
# Returns: Converted player input (integer) or 'x' cancel (string)
def Request(funds, message, rules=0):
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
                    print("Insufficient Funds: You only have " + str(funds) + " credits.")
                # Reject out of list bounds input for house rule
                elif funds == "rule" and playerInput > rules:
                    print("Invalid Number: Please enter a valid house rule number.")
                # Accept valid positive integer
                else:
                    return playerInput
            # Accept input of zero for current highest total bet
            elif funds == "highest" and playerInput == 0:
                return 0
        # Accept input of 'x' cancel unless request type is for current highest total bet
        elif playerInput == "x" and funds != "highest":
            return "x"
        # Initialize rejected input message
        reject = "Invalid Input: Please enter a positive integer.\n"
        # Add 'x' cancel option to rejected input message unless request type is for current highest total bet
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

# Purpose: Ask dealer for number of players for round
# Parameters: None
# Returns: Number of players (integer)
def RequestPlayers():
    return Request("players", "How many total players, including yourself,\n" +
                              "are playing in this round?\n\t")

# Purpose: Clear startup console output and ask player for their name
# Parameters: None
# Returns: Player name (string)
def RequestJoin():
    from os import system, name
    # Clear console of any startup output
    system("cls" if name == "nt" else "clear")
    return input("What is your name?\n\t")

# Purpose: Ask player for starting funds and notify of remaining funds from last game
# Parameters: Funds left over from last game (integer)
# Returns: Starting funds (integer)
def RequestStart(lastFunds):
    # Ask player for starting funds and notify of previous funds
    return Request("start", "\nHow many credits are you starting with?\nYour previous game left you with " + str(lastFunds) + AnalyzePlurality(" credit", lastFunds) + ".\n\t")

# Purpose: Ask player for chosen house rule
# Parameters: Current funds (integer), house rules (list)
# Returns: Title (string), Game Pot ante (integer), Sabacc Pot ante (integer), Phases ordering (integer list), Draw Phase fees (integer list)
def RequestRule(funds, rulesList):
    # Initialize prompt for house rule
    prompt = "\nPlease type the number of your chosen house rule:\n"
    # Counter of house rules with antes not exceeding current funds
    ruleCount = 0
    # Iterate through house rules list as one-based
    for index, rule in enumerate(rulesList, start=1):
        # Ensure that house rule ante does not exceed current funds
        if funds >= rule[1] + rule[2]:
            # Add house rule to prompt
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
        # Retrieve chosen house rule from zero-based list
        choice = rulesList[choice - 1]
        # Send house rule details to model
        return choice[0], choice[1], choice[2], choice[3], choice[4]
    # End game due to insufficient funds to ante in any house rule
    else:
        DisplayInsufficient(funds)
        RequestOver()

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
                    print("Invalid Number: Please enter a valid Draw Phase fee.")
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
                    print("Invalid Number: Please enter a valid Draw Phase fee.")
            # Reject invalid input
            except ValueError:
                print("Invalid Input: Please enter a positive integer.")
    # Accept valid fees
    return funds - gamePotFees - sabaccPotFees, gamePotFees, sabaccPotFees


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

# Purpose: Ask player for amount that opponents paid into Game Pot
# Parameters: None
# Returns: Opponents' Game Pot payments (integer) or 'x' cancel (string)
def RequestGamePot():
    return Request("game", "How many total credits did your\n" +
                           "\topponents pay into the\n" +
                           "\tGame Pot?\n\t")

# Purpose: Ask player for amount that opponents paid into Sabacc Pot
# Parameters: None
# Returns: Opponents' Sabacc Pot payments (integer) or 'x' cancel (string)
def RequestSabaccPot():
    return Request("sabacc", "How many total credits did your\n" +
                             "\topponents pay into the\n" +
                             "\tSabacc Pot?\n\t")

# Purpose: Ask player for current highest total bet amount
# Parameters: Total amount player has paid in current Betting Phase (integer)
# Returns: Current highest total bet amount (integer)
def RequestHighest(phaseSum):
    # Ask until valid input given
    while True:
        # Ask player for current highest total bet
        highest = Request("highest", "What is the current highest total bet?\n\t")
        # Accept highest bet greater then current player contribution
        if highest >= phaseSum:
            return highest
        # Reject invalid highest bet smaller than current player contribution
        print("The last highest bet was " + str(phaseSum) + AnalyzePlurality(" credit", phaseSum) + ".")


# Purpose: Ask player for chosen bet action
# Parameters: Betting Phase state (integer), current highest total bet (integer), ability to directly end current Betting Phase (boolean)
# Returns: Chosen bet action (string)
def RequestBetting(state, highest, end):
    # Initialize betting options prompt
    message = "Please type the letter of your chosen bet:\n"
    # If able to directly end current Betting Phase
    if end:
        # Add end option to prompt
        message += "\tEnd Betting Phase (e)\n"
    # If current funds is zero or no one has opened
    if state == 0 or state == 1:
        # Add pass option to prompt
        message += "\tPass/Check (p)\n"
        # If no one has opened and current funds greater than zero
        if state == 1:
            # add open option to prompt
            message += "\tOpen/Bet (o)\n"
    # If someone has opened and current funds greater than zero
    elif state == 2:
        # Add call and raise options to prompt
        message += "\tCall/See to " + str(highest) + " credits (c)\n"
        message += "\tRaise to " + str(highest + 1) + "+ credits (r)\n"
    # Add fold option to prompt
    message += "\tFold/Junk (f)\n\t"
    # Ask for chosen bet action
    return input(message).lower()

# Purpose: Ask player for winner
# Parameters: None
# Returns: Winner (string)
def RequestWinner():
    return (input("\nPlease type the letter of the round result:\n" +
                  "\tYou Won (y)\n" +
                  "\tOpponent Won (o)\n\t")).lower()

# Purpose: Ask player for winning hand
# Parameters: None
# Returns: Winning hand (string)
def RequestHand():
    return (input("\nPlease type the letter of the winning hand:\n" +
                  "\tSabacc (s)\n" +
                  "\tNulrhek (n)\n\t")).lower()

# Purpose: Ask player on how to proceed after Nulrhek win
# Parameters: None
# Returns: Action to proceed to (string)
def RequestProceed():
    return (input("\nPlease type the letter of the chosen action:\n" +
                  "\tNext Round (n)\n" +
                  "\tSingle Blind Card Draw (s)\n\t")).lower()

# Purpose: Notify player that game is over without immediately closing program 
# Parameters: None
# Returns: None
def RequestOver():
    # Wait for player to acknowledge game is over
    input("Game Over.")
    # Close program
    exit()


# Purpose: Notify player with message
# Parameters: Message (string)
# Returns: None
def DisplayMessage(message):
    print(message)

# Purpose: Notify player that they provided an invalid selection
# Parameters: None
# Returns: None
def DisplaySelection():
    print("Invalid Selection: Please select\n\tan available option.")

# Purpose: Notify player that they have insufficient funds available
# Parameters: Current funds (integer)
# Returns: None
def DisplayInsufficient(funds):
    print("Insufficient Funds: You only have " + str(funds) + AnalyzePlurality(" credit", funds) + ".")

# Purpose: Notify player that they bought in with the corresponding ante
# Parameters: Game Pot ante (integer), Sabacc Pot ante (integer)
# Returns: None
def DisplayAnte(gamePotAnte, sabaccPotAnte):
    print("Buying in with an ante of\n\t" + str(gamePotAnte) + AnalyzePlurality(" credit", gamePotAnte) + " into the Game Pot and\n\t" + str(sabaccPotAnte) + AnalyzePlurality(" credit", sabaccPotAnte) + " into the Sabacc Pot.")

# Purpose: Notify player of current turn
# Parameters: Current turn (integer)
# Returns: None
def DisplayTurn(turn):
    print("\nStarting Turn # " + str(turn))

# Purpose: Notify player of current funds
# Parameters: Current funds (integer)
# Returns: None
def DisplayFunds(funds):
    print("You now have " + str(funds) + AnalyzePlurality(" credit", funds) + ".")

# Purpose: Notify player of the amount they paid into the Game Pot
# Parameters: Incurred Game Pot payments (integer)
# Returns: None
def DisplayGamePot(gamePot):
    print("Notify the winner that you paid\n\t" + str(gamePot) + AnalyzePlurality(" credit", gamePot) +  " into the\n\tGame Pot.")

# Purpose: Notify player of the amount they paid into the Sabacc Pot
# Parameters: Incurred Sabacc Pot payments (integer)
# Returns: None
def DisplaySabaccPot(sabaccPot):
    print("Notify the winner that you paid\n\t" + str(sabaccPot) + AnalyzePlurality(" credit", sabaccPot) + " into the\n\tSabacc Pot.")

# Purpose: Notify player they have been eliminated from the game
# Parameters: None
# Returns: None
def DisplayEliminated():
    print("You have been eliminated from the game and\n" +
          "\tcleaned out of all your credits!")
