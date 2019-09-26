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
# Returns: Starting funds (integer), bet amount (integer), turn over (boolean)
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
                return funds, 0, True
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
                    return funds - bet, bet, False
                # Raise
                elif choice == "r":
                    # Bet amount is different yet to be paid
                    bet = controller.RequestRaise(funds, highest) - phaseSum
                    if bet != "x":
                        return funds - bet, bet, False
                    # Ask again if 'x' cancel given
                    continue
                # Fold
                elif choice == "f":
                    return funds, -1, True
                # End Betting Phase if able
                elif end and choice == "e":
                    return funds, 0, True
            # If insufficient funds to match highest bet
            else:
                # Force player to fold
                return funds, -1, True
        # Check if no one has opened
        elif highest == 0:
            # Check if current funds are greater than zero
            if funds > 0:
                # Allow player to pass, open, or fold
                choice = controller.RequestBetting(1, highest, False)
                if choice == "o":
                    bet = controller.RequestOpen(funds)
                    if bet != "x":
                        return funds - bet, bet, False
                    continue
            # Check if player is cleaned out of all credits
            else:
                # Allow player to pass or fold
                choice = controller.RequestBetting(0, highest, False)
            # Pass
            if choice == "p":
                return funds, 0, False
            # Fold
            elif choice == "f":
                return funds, -1, True
        # Reject invalid betting action choice
        controller.DisplaySelection()


# Purpose: Process results of round
# Parameters: Current funds (integer), amount player has paid into Game Pot (integer), amount player has paid into Sabacc Pot (integer), necessity to ask who won (boolean), controller (module)
# Returns: Starting funds (integer), Sabacc Pot (integer)
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
                                    gameWinnings + sabaccWinnings), 0
                    # 'x' cancel winnings
                        continue
                    continue
                # Opponent won
                elif winner == "o":
                    # Notify player to tell winner payments to both pots
                    controller.DisplayGamePot(gamePot)
                    controller.DisplaySabaccPot(sabaccPot)
                    # Reward nothing additional and empty out Sabacc Pot
                    return funds, 0
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
                    return newFunds, sabaccPot
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
                            return newFunds + sabaccPot + sabaccWinnings, 0
                        # 'x' cancel
                        continue
                    # Opponent won SBCD
                    elif winner == "o":
                        # Notify player to tell winner Sabacc Pot payments
                        controller.DisplaySabaccPot(sabaccPot)
                        # Reward nothing additional and empty out Sabacc Pot
                        return newFunds, 0
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


# Purpose: Play round
# Parameters: Program version (string), import_module (module)
# Returns: None
def Play(version, import_module):
    # Import controller
    controller = import_module("DroidController" + version)
    
    # Import CFG parser
    from configparser import ConfigParser
    # Initialize CFG parser
    parser = ConfigParser()
    
    # Import parent directory name
    from os.path import dirname
    # Locate CFG
    saveFile = dirname(__file__) + "/Save.cfg"
    
    # Retrieve starting funds
    funds = Start(parser, saveFile, controller)
    
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
        
        # Reset Game Pot to Game Pot ante
        gamePot = gamePotAnte
        # Increment Sabacc Pot by Sabacc Pot ante
        sabaccPot += sabaccPotAnte
        
        # Notify player of available funds and update CFG
        controller.DisplayFunds(funds)
        UpdateSave(funds, parser, saveFile)
        
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
                    funds, bet, turnOver = Bet(funds, phaseSum, end, controller)

                    # If not folded
                    if bet != -1:
                        # Increment player contribution by bet amount
                        phaseSum += bet
                        # Increment Game Pot by bet amount
                        gamePot += bet
                        
                        # Notify player of available funds and update CFG
                        controller.DisplayFunds(funds)
                        UpdateSave(funds, parser, saveFile)
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

                # Increment both pots by fees
                gamePot += gamePotFees
                sabaccPot += sabaccPotFees
                
                # Notify player of available funds and update CFG
                controller.DisplayFunds(funds)
                UpdateSave(funds, parser, saveFile)
        # Retrieve win results affecting current funds and Sabacc Pot
        funds, sabaccPot = Win(funds, gamePot, sabaccPot, bet, controller)
        
        # Notify player of available funds and update CFG
        controller.DisplayFunds(funds)
        UpdateSave(funds, parser, saveFile)
        
        # Check if player was cleaned out
        if funds <= 0:
            # Notify player of elimination and end game
            controller.DisplayEliminated()
            controller.RequestOver()
            
        # Retrieve next house rule
        title, gamePotAnte, sabaccPotAnte, order, drawFees = controller.RequestRule(funds, houseRules.rulesList)
