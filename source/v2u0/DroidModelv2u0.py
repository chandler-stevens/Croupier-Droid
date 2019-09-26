# Purpose: Get player name
# Parameters: Controller (module)
# Returns: Player name (string)
def Join(controller):
    return controller.RequestJoin()


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


# Purpose: Wager a bet
# Parameters: Current funds (integer), total amount that player has paid in the current Betting Phase so far (integer), ability to directly end Betting Phase (boolean), controller (module)
# Returns: Current funds (integer), bet amount (integer), turn over (boolean), bet type (string)
def Bet(funds, phaseSum, end, controller):
    # Ask until valid input given
    while True:
        # Retrieve current highest total bet
        highest = controller.RequestHighest(phaseSum)
        # Check if ability to directly end Betting Phase exists
        if end:
            # Deny ability if current funds are insufficient
            if highest > phaseSum:
                end = False
            # Automatically end Betting Phase if betting cycle complete
            elif highest == phaseSum:
                return funds, 0, True, "Turn:"
        # Check if someone has opened
        if highest > 0:
            # If sufficient funds to match highest bet
            if funds >= highest:
                # Allow player to call, raise, fold, or end
                choice = controller.RequestBetting(2, highest, end)
                # Call
                if choice == "c":
                    # Bet amount is difference yet to be matched
                    bet = highest - phaseSum
                    # Automatically deduct funds upon call
                    return funds - bet, bet, False, "Call:"
                # Raise
                elif choice == "r":
                    # Bet amount is different yet to be paid
                    bet = controller.RequestRaise(funds, highest) - phaseSum
                    if bet != "x":
                        return funds - bet, bet, False, "Raise:"
                    # Ask again if 'x' cancel given
                    continue
                # Fold
                elif choice == "f":
                    return funds, -1, True, "Fold:"
                # End Betting Phase if able
                elif end and choice == "e":
                    return funds, 0, True, "Turn:"
            # If insufficient funds to match highest bet
            else:
                # Force player to fold
                return funds, -1, True, "Fold:"
        # Check if no one has opened
        elif highest == 0:
            # Check if current funds are greater than zero
            if funds > 0:
                # Allow player to pass, open, or fold
                choice = controller.RequestBetting(1, highest, False)
                if choice == "o":
                    bet = controller.RequestOpen(funds)
                    if bet != "x":
                        return funds - bet, bet, False, "Open:"
                    continue
            # Check if player is cleaned out of all credits
            else:
                # Allow player to pass or fold
                choice = controller.RequestBetting(0, highest, False)
            # Pass
            if choice == "p":
                return funds, 0, False, "Pass:"
            # Fold
            elif choice == "f":
                return funds, -1, True, "Fold:"
        # Reject invalid betting action choice
        controller.DisplaySelection()


# Purpose: Process results of round
# Parameters: Current funds (integer), amount player has paid into Game Pot (integer), amount player has paid into Sabacc Pot (integer), necessity to ask who won (boolean), controller (module)
# Returns: Current funds (integer), Sabacc Pot (integer), win type (string)
def Win(funds, gamePot, sabaccPot, bet, controller):
    # Ask until valid input given
    while True:
        # Initialize winner to opponent in case player folded
        winner = "o"
        # If player did not fold
        if bet != -1:
            # Retrieve winner
            winner = controller.RequestWinner()
        # Ensure valid winner given
        if winner == "y" or winner == "o":
            # Retrieve winning hand
            hand = controller.RequestHand()
            # Sabacc
            if hand == "s":
                # Player won
                if winner == "y":
                    # Retrieve opponents' Game Pot payments
                    gameWinnings = controller.RequestGamePot()
                    if gameWinnings != "x":
                        # Retrieve opponents' Sabacc Pot payments
                        sabaccWinnings = controller.RequestSabaccPot()
                        if sabaccWinnings != "x":
                            # Reward both pots to player and empty out Sabacc Pot
                            return (funds + gamePot + sabaccPot +
                                    gameWinnings + sabaccWinnings), 0, "Sabacc:"
                        # 'x' cancel winnings
                        continue
                    continue
                # Opponent won
                elif winner == "o":
                    # Notify player to tell winner payments to both pots
                    controller.DisplayGamePot(gamePot)
                    controller.DisplaySabaccPot(sabaccPot)
                    # Reward nothing additional and empty out Sabacc Pot
                    return funds, 0, "Sabacc:"
            # Nulrhek
            elif hand == "n":
                # Capture current funds to avoid overwriting
                newFunds = funds
                # Player won
                if winner == "y":
                    # Retrieve opponent's Game Pot payments
                    gameWinnings = controller.RequestGamePot()
                    if gameWinnings != "x":
                        # Reward Game Pot to player
                        newFunds += gamePot + gameWinnings
                    # 'x' cancel
                    else:
                        continue
                # Opponent Won
                elif winner == "o":
                    # notify player to tell winner payment to Game Pot
                    controller.DisplayGamePot(gamePot)
                # Reject invalid winner
                else:
                    controller.DisplaySelection()
                    continue
                # Retrieve decision to proceed from Nulrhek win
                proceed = controller.RequestProceed()
                # Next round
                if proceed == "n":
                    # Reward nothing additional and maintain Sabacc Pot
                    return newFunds, sabaccPot, "Nulrhek:"
                # Single Blind Card Draw (SBCD)
                elif proceed == "s":
                    # Retrieve SBCD winner
                    winner = controller.RequestWinner()
                    # Player won SBCD
                    if winner == "y":
                        # Retrieve opponents' Sabacc Pot payments
                        sabaccWinnings = controller.RequestSabaccPot()
                        if sabaccWinnings != "x":
                            # Reward Sabacc Pot to player and empty out Sabacc Pot
                            return newFunds + sabaccPot + sabaccWinnings, 0, "Sabacc:"
                        # 'x' cancel
                        continue
                    # Opponent won SBCD
                    elif winner == "o":
                        # Notify player to tell winner Sabacc Pot payments
                        controller.DisplaySabaccPot(sabaccPot)
                        # Reward nothing additional and empty out Sabacc Pot
                        return newFunds, 0, "Sabacc:"
        # Reject invalid input
        controller.DisplaySelection()


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
