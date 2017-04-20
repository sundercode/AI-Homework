import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
from ConsolidatedState import *
from AIPlayerUtils import *

##
# ConsolidatedState
#
# class that defines a simpler game state for antics with much less information
# This class should just focus on food-related things
#
class ConsolidatedState(object):
    def __init__(self, inputUtility, inputState):
        self.utility = inputUtility
        self.state = inputState

    def setUtility(self, utility):
        pass #method template, declare instance to override??

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class will implement
# a combination of various TD learning methods.
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
        super(AIPlayer,self).__init__(inputPlayerId, "HW 6 TD Learning Agent")
        self.discountFactor = 0.92 #start with this and adjust
        self.learningRate = 0.99 #start with this and *0.90 each iteration
        self.utilityList = [] #initialize for now, change later
        #policy: always take food whenever we can

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
        self.getReward(currentState)
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
    # Description: this function will take a current state of the game and assign it to a
    # consolidated state, and create a class based on it's information.
    #
    # Parameters: the current state of the game.
    #
    # Return: the consolidated version of the current state we are passed
    def consolidateStates(self, currentState):
        me = currentState.whoseTurn
        myInv = currentState.inventories[me]
        currWorkers = getAntList(currentState, me, (WORKER,))

        #get the right params that we want to take into account and then return them here,
        #give the state a utility??
        #return ConsolidatedState()

    ##
    # getReward()
    #
    # Description: this function will take a gameState object and in turn generate a reward for it
    # 1 = we have collected food, -1 we have lost, -0.01 is every other state we encounter on the way.
    #
    # Return: the reward for that given state
    def getReward(self, currentState):
        runningReward = 0 #the best reward we have seen so far?
        currReward = -0.01 #the current reward we are looking at... potentially move this to instance variables

        me = currentState.whoseTurn
        enemyInv = currentState.inventories[not me]
        myInv = currentState.inventories[me]
        currWorkers = getAntList(currentState, me, (WORKER,))
        publicFood = getConstrList(currentState, None, (FOOD,))

        #when a worker ant is on a food location, give that a 1.0 value
        for worker in currWorkers:
            if (worker.coords == publicFood[0].coords or worker.coords == publicFood[1].coords):
                currReward = 1.0
                #runningReward += currReward

        #when a worker is carrying and is on a tunnel or anthill, give this a 1.0 value
        for worker in currWorkers:
            if (worker.carrying):
                if (worker.coords == myInv.getAnthill().coords or worker.coords == myInv.getTunnels()[0].coords):
                    currReward = 1.0
                    #runningReward += currReward

        #else just return -1, because we are somewhere in between these states
        if (enemyInv.foodCount == 11):
            currReward = -1.0

        if (len(currWorkers) == 0):
            currReward = -1.0

        print str(currReward) + " is the reward"
        return currReward

    ##
    # saveUtilList
    # save method to save current state-utility list to a file
    #
    # takes our utlity list and saves it to a hardcoded file name.
    #
    def saveUtilList(self, utilList):
        myFile = open('sunderla17TD.txt', 'w')

        for item in utilList:
            myFile.write("%s\n" % item)

        myFile.close()

    ##
    # loadUtilList
    # load method to load state-utility list from a file
    #
    # takes our utility list that we've saved in the folder and loads it into
    # this instance of the TD learning.
    #
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
        # print self.getReward(currentState)
        if hasWon:
            print "we won!!"
            #self.saveUtilList(self.testList)
            #self.loadUtilList('sunderla17TD.txt')
        return hasWon
