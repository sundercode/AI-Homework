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
        self.inputs = []
        self.targets = []
        self.hiddenNodes = [0]*20
        self.learningRate = 0.10
        self.maxDepth = 2

        self.learnedHiddenWeights = []
        self.learnedOutputWeights = []
        self.learnedScores = []

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
        self.mapping(currentState)

        selectedMove = self.recursiveMove(currentState, 0)
        if (selectedMove == None):
            return Move(END, None, None)

        return selectedMove

    # sigmoid function for backpropigation, generated from numpy
    def nonlin(self, x, deriv=False):
        if(deriv==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))

    ##
    # our back propigation function that takes and learns on a set of inputs from the game.
    #
    # from: http://python3.codes/neural-network-python-part-1-sigmoid-function-gradient-descent-backpropagation/
    #
    # This simulates a run of 60000 learnings from a single game using back propigation.
    # As this code is turned in, it has not been implemented to learn in antics w/o the evaluate state.
    #
    def backPropigate(self):
        pairArray = zip(self.inputs, self.targets)
        finalInput = np.array(self.inputs)
        finalTargets = np.array([x[1] for x in pairArray])
        
        #let's associate each input with one target
        inputLayerSize = 28
        hiddenLayerSize = 15
        outputLayerSize = 1

        weights_hidden = np.random.uniform(low=-1.0, high=1.0, size=(inputLayerSize, hiddenLayerSize))
        weights_output = np.random.uniform(low=-1.0, high=1.0, size=(hiddenLayerSize, outputLayerSize))

        #print weights
        for iter in xrange(60000):

            #forward propogation
            l1 = self.nonlin(np.dot(finalInput, weights_hidden))
            l2 = self.nonlin(np.dot(l1,weights_output))

            # how much did we miss the target value?
            l2_error = finalTargets - l2

            # were we really sure? if so, don't change too much.
            l2_delta = l2_error*self.nonlin(l2,deriv=True)

            if (iter% 10000) == 0:
                print "Error:" + str(np.mean(np.abs(l2_error)))
                print l2_delta.shape

            # how much did each l1 value contribute to the l2 error (according to the weights)?
            l1_error = l2_delta.dot(weights_output.T)

            # were we really sure? if so, don't change too much.
            l1_delta = l1_error * self.nonlin(l1,deriv=True)

            #update the weights
            weights_output += (l1.T.dot(l2_delta))*self.learningRate
            weights_hidden += (finalInput.T.dot(l1_delta))*self.learningRate

        #print l2
        self.learnedOutputWeights = weights_output
        self.learnedHiddenWeights = weights_hidden
        self.learnedScores = l2

    ##
    #getAttack
    #
    # This agent never attacks
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  #don't care


    def mapping(self, currentState):
        #Currently has 27 inputs. This might change with
        #Things that want to be added or the biases
        input = [0]*28
        me = currentState.whoseTurn
        enemy = (currentState.whoseTurn + 1) % 2
        myInv = currentState.inventories[me]
        enemyInv = currentState.inventories[not me]

        myFood = myInv.foodCount
        enemyFood = enemyInv.foodCount

        #This whole chunk adds a 1 to a spot that corresponds to a
        #certain food count. Increasing positive weight
        if(myFood == 0):
            input[0] = 1
            for x in range(10):
                input[x+1] = 0
        if(myFood == 1):
            input[1] = 1
            input[0] = 0
            for x in range(2,11):
                input[x] = 0
        if(myFood == 2):
            input[2] = 1
            for x in range(1):
                input[x] = 0
            for x in range(3,11):
                input[x] = 0
        if(myFood == 3):
            input[3] = 1
            for x in range(2):
                input[x] = 0
            for x in range(4,11):
                input[x] = 0
        if(myFood == 4):
            input[4] = 1
            for x in range(3):
                input[x] = 0
            for x in range(5,11):
                input[x] = 0
        if(myFood == 5):
            input[5] = 1
            for x in range(4):
                input[x] = 0
            for x in range(6,11):
                input[x] = 0
        if(myFood == 6):
            input[6] = 1
            for x in range(5):
                input[x] = 0
            for x in range(7,11):
                input[x] = 0
        if(myFood == 7):
            input[7] = 1
            for x in range(6):
                input[x] = 0
            for x in range(8,11):
                input[x] = 0
        if(myFood == 8):
            input[8] = 1
            for x in range(7):
                input[x] = 0
            for x in range(9,11):
                input[x] = 0
        if(myFood == 9):
            input[9] = 1
            for x in range(8):
                input[x] = 0
            for x in range(10,11):
                input[x] = 0
        if(myFood == 10):
            input[10] = 1
            for x in range(9):
                input[x] = 0
            input[11] = 0
        if(myFood == 11):
            input[11] = 1
            for x in range(10):
                input[x] = 0

        #Same as above, just with enemy food. Increasing negative weight
        if(enemyFood == 0):
            input[12] = 1
            for x in range(13,23):
                input[x] = 0
        if(enemyFood == 1):
            input[13] = 1
            input[12] = 0
            for x in range(14,23):
                input[x] = 0
        if(enemyFood == 2):
            input[14] = 1
            for x in range(12,13):
                input[x] = 0
            for x in range(15,23):
                input[x] = 0
        if(enemyFood == 3):
            input[15] = 1
            for x in range(12,14):
                input[x] = 0
            for x in range(16,23):
                input[x] = 0
        if(enemyFood == 4):
            input[16] = 1
            for x in range(12,15):
                input[x] = 0
            for x in range(17,23):
                input[x] = 0
        if(enemyFood == 5):
            input[17] = 1
            for x in range(12,16):
                input[x] = 0
            for x in range(18,23):
                input[x] = 0
        if(enemyFood == 6):
            input[18] = 1
            for x in range(12,17):
                input[x] = 0
            for x in range(19,23):
                input[x] = 0
        if(enemyFood == 7):
            input[19] = 1
            for x in range(12,18):
                input[x] = 0
            for x in range(20,23):
                input[x] = 0
        if(enemyFood == 8):
            input[20] = 1
            for x in range(12,19):
                input[x] = 0
            for x in range(21,23):
                input[x] = 0
        if(enemyFood == 9):
            input[21] = 1
            for x in range(12,20):
                input[x] = 0
            for x in range(22,23):
                input[x] = 0
        if(enemyFood == 10):
            input[22] = 1
            for x in range(12,21):
                input[x] = 0
            input[23] = 0
        if(enemyFood == 11):
            input[23] = 1
            for x in range(12,22):
                input[x] = 0

        myWorkers = getAntList(currentState, me,(WORKER,))
        #check to see if you have two or more workers. Should have positive weight
        if(len(myWorkers) >= 2):
            input[24] = 1
        else:
            input[24] = 0

        #Checks to see if you have less than two workers. Negative weight
        if(len(myWorkers) < 2):
            input[25] = 1
        else:
            input[25] = 0

        #checks if worker is carrying food. Positive value
        for worker in myWorkers:
            if (worker.carrying):
                input[26] = 1
            else:
                input[26] = 0

        myQueen = getAntList(currentState, me, (QUEEN,))[0]
        stepsToAnthill = stepsToReach(currentState, myQueen.coords, myInv.getAnthill().coords)
        stepsToTunnel = stepsToReach(currentState, myQueen.coords, myInv.getTunnels()[0].coords)
        if (stepsToAnthill > 2 or stepsToTunnel > 2):
            input[27] = 1
        else:
            input[27] = 0

        self.inputs.append(input)
        #print input
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
        self.targets.append([stateScore])
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
    # This agent does learn, we should let it know when it wins
    #
    def registerWin(self, hasWon):
        if hasWon:
            print "we won!!"
        self.backPropigate()
        return hasWon
