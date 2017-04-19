import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from AIPlayerUtils import *

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "TD Learning Agent")
        self.foodStates = 11*[None] # 11 different states for food
        self.testList = [10, 23, 34920, 3949, 12, 11111, 234]

    ##
    #getPlacement
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]

    ##
    #getMove
    #Description: Gets the next move from the Player.
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        self.consolidateStates(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];

        return selectedMove

    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]

    ##
    #consolidateStates
    #
    # Description: this function will take a current state of the game and assign it to a predesignated state
    # This is so we do not end up with tens of thousands of states by the end of an antics game
    #
    # Parameters: the current state of the game.
    #
    # Return: the corresponding "state group" that the current state belongs to.
    #
    def consolidateStates(self, currentState):
        me = currentState.whoseTurn
        myInv = currentState.inventories[me]
        currWorkers = getAntList(currentState, me, (WORKER,))
        #look at this current state and see if all workers are carrying?

        #food count, aka no matter where the ants are located the # of food is the main factor in states
        #we sould only change this if the food count changes
        for x in range(11):
            if (myInv.foodCount == x):
                self.foodStates[x] = currentState
                print "x is the same as the food count, " + str(myInv.foodCount)

        #build upon food states with where ants are?
    #Write save method to save current state-utility list to a file
    def saveUtilList(self, utilList):
        myFile = open('utilList418.txt', 'w')

        for item in utilList:
            myFile.write("%s\n" % item)

        myFile.close()

    #Write load method to load state-utility list from a file, the
    # one named in the save method
    def loadUtilList(self, fname):
        with open(fname) as f:
            content = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            content = [int(x.strip('\n')) for x in content]

            return content

    ##
    #registerWin
    #
    # This agent does learn, we should let it know when it wins
    #
    def registerWin(self, hasWon):
        if hasWon:
            print "we won!!"
            print self.testList
            #self.saveUtilList(self.testList)
            print self.loadUtilList('utilList418.txt')
        return hasWon
