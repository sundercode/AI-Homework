  # -*- coding: latin-1 -*-
import random
import sys
import numpy as np
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import addCoords
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
        super(AIPlayer,self).__init__(inputPlayerId, "Neural Networks")
        #the coordinates of the agent's food and tunnel will be stored in these
        self.inputs = np.array([[0,0,1,0,1,1,0,1,0,0,0,0,0,1],
                [0,1,1,0,1,1,0,1,0,0,0,0,0,1],
                [1,1,1,0,1,1,0,0,0,0,0,0,0,0],
                [1,0,1,0,1,1,0,1,1,0,0,0,0,0],])
        self.targets = np.array([[0.512, 0.2345, 0.7880, 0.4372]]).T
        self.maxDepth = 2;

    ##
    #getPlacement
    #
    # The agent uses a hardcoded arrangement for phase 1 to provide maximum
    # protection to the queen.  Enemy food is placed randomly.
    #
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
    #
    # This gets the move from the list of recursive moves generated for A* Search
    # returns the selected move from that traversal
    ##
    def getMove(self, currentState):
        self.evaluateState(currentState)
        self.backPropigate()

        selectedMove = self.recursiveMove(currentState, 0)
        if (selectedMove == None):
            return Move(END, None, None)

        return selectedMove

    # sigmoid function for backpropigation, generated from numpy
    def nonlin(self, x, deriv=False):
        if(deriv==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))

    def backPropigate(self):
        #seed random numbers for deterministic training?
        np.random.seed(1)
        #initialize random weights on all of our inputs, average is 0
        syn0 = 2*np.random.random((14,1)) - 1
        for iter in xrange(10):
            #forward propogation
            l0 = self.inputs ## this is currently empty, generated from our mapping function
            l1 = self.nonlin(np.dot(l0, syn0)) #should generate output?

            #error
            l1_error = self.targets - l1 #remember 1 output per 14 inputs

            #delta values ---> apply a new learning rate to mess with this?
            l1_delta = l1_error * self.nonlin(l1,True)
            print str(l1_delta) + " is our delta"

            #update weights ----> to be hardcoded later?
            syn0 += np.dot(l0.T,l1_delta)
        print "Outputs after training: "
        print l1

    ##
    #getAttack
    #
    # This agent never attacks
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  #don't care

    ##
    #evaluateState
    #
    # This function behaves as the heuristic evaluation for various states the agent can enter
    # returns a value from 0.0 - 1.0 to indicate how much of a "winning" move has been selected
    #
    # 0.0 means the enemy has won the game.
    # > 0.5 means you are currently winning
    #
    # Currently, this function operates solely on the basis of gathering food for simplicity
    # and time conservation.
    #
    # gets passed the current game state object.
    #
    def evaluateState(self, currentState):
        #useful pointers. Set state score to a default value since we interpret 0 as losing.
        stateScore = 0.0
        me = currentState.whoseTurn
        enemy = (currentState.whoseTurn + 1) % 2
        myInv = currentState.inventories[me]
        enemyInv = currentState.inventories[not me]
        randFloat = random.uniform(0.0, 0.0001)

        #Metrics that are important to evaluate:
        # number of ants each player has
        myAnts = getAntList(currentState, me,(QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER))
        myAntCount = len(getAntList(currentState, me,(QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER)))

        # types of ants each player has. Right now we simply care about workers
        myWorkers = getAntList(currentState, me,(WORKER,))

        #more than 2 workers is good
        if (len(myWorkers) >= 2 and len(myWorkers) < 4):
            stateScore = 0.9

        # How much food each player has
        publicFood = getConstrList(currentState, None, (FOOD,))
        myFood = myInv.foodCount
        enemyFood = enemyInv.foodCount
        foodDiff = myFood - enemyFood

        if (myFood != 0):
            foodScore = myFood/10.0

        #definite lose state
        if(enemyFood == 10):
            stateScore = 0.0
            #self.targets.append(stateScore)
            return stateScore

        # give points if the workers are close to the tunnel/anthill with food
        bestDist = 0
        workerScore = 0
        if (len(myWorkers) == 0):
            stateScore = 0.1 #all of my workers are dead
            #self.targets.append(stateScore)
            return stateScore

        for worker in myWorkers:
            stepsToAnthill = stepsToReach(currentState, worker.coords, myInv.getAnthill().coords)
            stepsToTunnel = stepsToReach(currentState, worker.coords, myInv.getTunnels()[0].coords)
            distToFood1 = stepsToReach(currentState, worker.coords, publicFood[0].coords)
            distToFood2 = stepsToReach(currentState, worker.coords, publicFood[1].coords)

            #if we are carrying, pick which construction is closer
            if (worker.carrying):
                bestDist = min([stepsToAnthill, stepsToTunnel])
                #as the distance gets smaller, the worker score should go up
                currentWorkerScore = (1.0/(bestDist+1.0)) * 0.5
                currentWorkerScore += 0.5
                workerScore += currentWorkerScore

            else:
                bestDist = min([distToFood1, distToFood2])
                #as the distance to the food gets smaller, the score goes up
                currentWorkerScore = (1.0/(bestDist+1.0)) * 0.5
                workerScore += currentWorkerScore

        avgWorkerScore = workerScore/len(myWorkers)

        # move my queen off of the anthill
        myQueen = getAntList(currentState, me, (QUEEN,))[0]
        queenScore = 0
        stepsToAnthill = stepsToReach(currentState, myQueen.coords, myInv.getAnthill().coords)
        stepsToTunnel = stepsToReach(currentState, myQueen.coords, myInv.getTunnels()[0].coords)
        if (stepsToAnthill < 2 or stepsToTunnel < 2):
            if (queenScore > 0.1):
                queenScore -= 0.2
        else:
            queenScore += 0.3

        #return the state score as a weighted average of the food and worker scores
        stateScore = (foodScore * 0.95)+(avgWorkerScore*0.08)+(queenScore* 0.2)
        if (stateScore < (1 - 0.0001)):
            stateScore += randFloat

        ##add this score to a list of "test scores" for our neural network to learn from
        #self.targets.append(stateScore)
        return stateScore
    ##
    # bestNodeScore
    #
    # takes a list of state nodes and returns the best score
    # the best score should help the choice of next state.
    #
    def bestNodeScore(self, nodeList):
        #make a list of just the scores from the nodes
        scoreList = [x["score"] for x in nodeList]

        #make sure list is non-empty
        for score in scoreList:
            if (max(scoreList) == score):
                return score
            else:
                return max(scoreList)

    ##
    # recursiveMove <!-- RECURSIVE -->
    #
    # This function generates our A* node tree to traverse.
    #
    # We recurse on the currentState object with the depth + 1
    # State nodes are represented by a python Dictionary
    #
    def recursiveMove(self, currentState, currentDepth):
        #generate list of all available moves. Leave out END TURN moves as a part of this
        moveList = listAllMovementMoves(currentState)

        #generate the list of all available nodes with a dictionary
        nodeList = [dict({'move': None, 'nextState': None, 'score':None}) for x in range(len(moveList))]
        for i, move in enumerate(moveList):
            #populate the generated empty dicts with the right stats
            nodeList[i]['move'] = move
            nodeList[i]['nextState'] = getNextState(currentState, move)
            nodeList[i]['score'] = self.evaluateState(nodeList[i]['nextState'])

        if (len(nodeList) == 0):
            #if we can make no more moves, return an END_TURN move type
            nodeList = [dict({'move': Move(END, None, None), 'nextState': None, 'score': None})]
            #could call here with max == false, since that's the only time it gets set
            return nodeList[0]['move']

        #base case: return the state score
        if (currentDepth >= self.maxDepth):
            return self.evaluateState(currentState)

        #if we are at the head of the tree, return best scored node's move
        elif (currentDepth == 0):
            currScore = self.bestNodeScore(nodeList) #highest score
            for node in nodeList:
                #find the node with this score
                if (node['score'] == currScore):
                    return node['move']
        #we are somewhere in the middle of the tree, recurse
        else:
            #recursively call this on the state with the highest score
            currScore = self.bestNodeScore(nodeList) #highest score
            for node in nodeList:
                #find the node with this score
                if (node['score'] == currScore):
                    return self.recursiveMove(node['nextState'], currentDepth + 1)
    ##
    #registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
