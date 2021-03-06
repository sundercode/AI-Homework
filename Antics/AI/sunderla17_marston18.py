import random
import sys
import math
import os.path
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
        super(AIPlayer,self).__init__(inputPlayerId, "TD Learning Agent")
        self.discountFactor = 0.83 #start with this and adjust
        self.learningRate = 0.90 #start with this and *0.90 each iteration
        self.utilityList = [] #initialize for now, change later, we want this to be (consolidatedState, utility)
        self.gameCount = 0 #count how many games we've played
        self.loadedList = []

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
            if os.path.isfile('sunderla17_marston18TD.txt'):
                print "we are using the saved utilities"
                self.loadedList = self.loadUtilList('sunderla17_marston18TD.txt')

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
        selectedMove = self.tdLearningEq(currentState)

        #initialize the utility with the rewards when they are first seen

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
    def shrinkState(self, currentState):
        me = currentState.whoseTurn
        myInv = currentState.inventories[me]
        currWorkers = getAntList(currentState, me, (WORKER,))
        stepsToAnthill = 0
        stepsToTunnel = 0

        for worker in currWorkers: #if we have more than one this is not going to really get accurate readings
            stepsToAnthill = stepsToReach(currentState, worker.coords, myInv.getAnthill().coords)
            stepsToTunnel = stepsToReach(currentState, worker.coords, myInv.getTunnels()[0].coords)

        #get the right params
        newState = ConsolidatedState(self.getReward(currentState), myInv.foodCount, stepsToTunnel, stepsToAnthill, currWorkers) #init the new object here

        return newState

    def learningRateMod(self, constant):
        if (constant < 1.0):
            return constant * constant #incrementally lower
    ##
    # getReward()
    #
    # Description: this function will take a gameState object and in turn generate a reward for it
    # 1 = we have collected food or returned to a structure with food, -1 we have lost or have no workers/more than one worker
    # -0.01 is every other state we encounter on the way.
    #
    # Return: the reward for that given state
    def getReward(self, currentState):
        #runningReward = 0 #the best reward we have seen so far?
        currReward = -0.01 #the current reward we are looking at... potentially move this to instance variables

        me = currentState.whoseTurn
        enemyInv = currentState.inventories[not me]
        myInv = currentState.inventories[me]
        currWorkers = getAntList(currentState, me, (WORKER,))
        publicFood = getConstrList(currentState, None, (FOOD,))
        myQueen = getAntList(currentState, me, (QUEEN,))[0]

        #when a worker is carrying and is on a tunnel or anthill, give this a 1.0 value
        for worker in currWorkers:
            if (worker.carrying):
                stepsToAnthill = approxDist(worker.coords, myInv.getAnthill().coords)
                stepsToTunnel = approxDist(worker.coords, myInv.getTunnels()[0].coords)
                currReward -= min(stepsToTunnel, stepsToAnthill)*0.01

                if (worker.coords == myInv.getAnthill().coords or worker.coords == myInv.getTunnels()[0].coords):
                    currReward += 3.0

                if (worker.coords == publicFood[0].coords or worker.coords == publicFood[1].coords):
                    currReward -= 1.0

            else:
                distToFood1 = stepsToReach(currentState, worker.coords, publicFood[0].coords)
                distToFood2 = stepsToReach(currentState, worker.coords, publicFood[1].coords)
                if (min(distToFood1,distToFood2) == 1):
                    currReward += -1.0
                elif(min(distToFood1,distToFood2) == 0):
                    currReward += 1.0
                currReward -= min(distToFood1,distToFood2)* 0.01

                if (worker.coords == publicFood[0].coords or worker.coords == publicFood[1].coords):
                    currReward += 2.0

        if (myQueen.coords != myInv.getAnthill().coords and myQueen.coords != myInv.getTunnels()[0].coords):
            if (myQueen.coords != publicFood[0].coords and myQueen.coords != publicFood[1].coords):
                currReward += 0.04

        #else just return -1, because we are somewhere in between these states
        foodDiff = myInv.foodCount - enemyInv.foodCount
        #subtract by food amount that enemy has
        currReward += (0.01*foodDiff)

        foodDiff2 = 11 - myInv.foodCount
        currReward -= 0.01*foodDiff2

        if (len(currWorkers) != 1):
            currReward -= 1.0

        return currReward

    ##
    # tdLearningEq
    #
    # calculates the utility of a given state given the use of the TD learning equation
    #
    # returns a utility number
    def tdLearningEq(self, currentState):
        # #initialize the utility with the rewards when they are first seen
        s1 = self.shrinkState(currentState)
        newUtility = 0
        moveList = listAllMovementMoves(currentState)
        nextStateList = []

        #all the possible next states here, use consolidated
        for move in moveList:
            nextStateList.append(getNextState(currentState, move))

        smallNextStates = list(map(self.shrinkState, nextStateList))

        #base case: a terminal state. Return the utility of this state
        #Terminal state is when there's no more moves
        if (len(nextStateList) == 0):
            return Move(END, None, None)

        #after a transition, update the current utility we have been keeping track of
        newUtilList = []
        randFloat = random.uniform(0.0, 0.0001)
        for i in range(len(nextStateList)):

            if len(self.loadedList) != 0:
                lengthDiff = len(nextStateList) - len(self.loadedList)
                smallNextStates[i].utility = self.loadedList[i]

                if (len(nextStateList) > len(self.loadedList)):
                    print "we have more states now than we did last time..."
                    nextStateList[lengthDiff:] = self.getReward(nextStateList[i])
                    list(map(self.shrinkState, nextStateList))

            newUtility = s1.utility + (self.learningRate*(self.getReward(currentState) + self.discountFactor*smallNextStates[i].utility - s1.utility))
            newUtility += randFloat
            newUtilList.append(newUtility)

        #get the max utility
        finalUtility = max(newUtilList)

        #find the index that we found it
        bestIndex = newUtilList.index(finalUtility)
        #print moveList[bestIndex]

        #this might be where we append utility values to save to a file
        s1.utility = finalUtility
        #find the index of the best utility in the next states, and return the move associated with it

        self.utilityList.append(s1.utility)
        #return the move with that best index!
        return moveList[bestIndex]


    ##
    # saveUtilList
    # save method to save current state-utility list to a file
    #
    # takes our utlity list and saves it to a hardcoded file name.
    #
    def saveUtilList(self, utilList):
        myFile = open('sunderla17_marston18TD.txt', 'w')

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
        #check if the file exists
    # if (os.path.isfile('./sunderla17TD.txt')):
    #     print "our file exists"
        with open(fname) as f:
            content = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            content = [float(x.strip('\n')) for x in content]

            return content

    ##
    #registerWin
    #
    # This agent does learn, we should let it know when it wins
    #
    def registerWin(self, hasWon):
        #print self.utilityList
        self.saveUtilList(self.utilityList) #at the end of a game, save the current state-utility list
        self.gameCount += 1

        if self.learningRate >= 0.01 and self.learningRate < 1.0:
            self.learningRate = 0.90/math.sqrt(self.gameCount)
            print str(self.learningRate) + " after changing the learning rate"
        if hasWon:
            print "we won!!"
            #save the utility list for sure?

        return hasWon

##
# ConsolidatedState
#
# class that defines a simpler game state for antics with much less information
# This class should just focus on food-related things
#
class ConsolidatedState(object):
    def __init__(self, inputUtility, inputFood, inputTunnelDist, inputHillDist, inputAnts):
        self.utility = inputUtility
        # self.state = inputState #have the class convert a full state?
        self.foodTotal = inputFood
        self.tunnelDist = inputTunnelDist
        self.hillDist = inputHillDist
        self.ants = inputAnts
        # self.move = inputMove
        #food count, worker count, inventories, queen ants.

    def learnUtility(self, currUtility):
        # nextState =
        #learningRateMod(learningRate) #shrink over time
        #the utility would be calculated in the AI player class
        return currUtility

    def getNextState(self, currentState, move):
        pass
