  # -*- coding: latin-1 -*-
import random
import sys
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
        super(AIPlayer,self).__init__(inputPlayerId, "MiniMax Search")
        #the coordinates of the agent's food and tunnel will be stored in these
        #variables (see getMove() below)
        self.myFood = None
        self.myTunnel = None
        self.maxDepth = 2

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
    # This gets the move from the list of recursive moves generated
    # returns the selected move from that traversal
    ##
    def getMove(self, currentState):
        #recursively find moves, setting max to true as initial
        selectedMove = self.recursiveMove(currentState, 0, True)
        if (selectedMove == None):
            return Move(END, None, None)

        return selectedMove


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
    # 0.0 means the enemy has won the game. > 0.5 means you are currently winning
    #
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
        # types of ants each player has. Right now we simply care about workers
        myWorkers = getAntList(currentState, me,(WORKER,))

        # How much food each player has
        publicFood = getConstrList(currentState, None, (FOOD,))
        myFood = myInv.foodCount
        enemyFood = enemyInv.foodCount
        foodDiff = myFood - enemyFood

        foodScore = 0.0

        if (myFood != 0):
            foodScore = myFood/10.0

        #definite lose state
        if(enemyFood == 10):
            stateScore = 0.0
            return stateScore

        # give points if the workers are close to the tunnel/anthill with food
        bestDist = 0
        workerScore = 0
        if (len(myWorkers) == 0):
            stateScore = 0.1 #all of my workers are dead
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

        # Calculate a score for the queen. Take into account the threat level
        myQueen = getAntList(currentState, me, (QUEEN,))[0]
        queenScore = 0

        #get my queen off of the anthill
        stepsToAnthill = stepsToReach(currentState, myQueen.coords, myInv.getAnthill().coords)
        stepsToTunnel = stepsToReach(currentState, myQueen.coords, myInv.getTunnels()[0].coords)
        if (stepsToAnthill < 2 or stepsToTunnel < 2):
            if (queenScore > 0.2):
                queenScore -= 0.2
        else:
            # add threat level code here
            queenScore += 0.3

        #return the state score as a weighted average of the food and worker scores
        # based on whose turn it is, return this as a positive or negative score.
        stateScore = (foodScore * 0.95)+(avgWorkerScore*0.08)+(queenScore* 0.2)
        if (stateScore < (1 - 0.0001)):
            stateScore += randFloat
        return stateScore

    ##
    # recursiveMove <!-- RECURSIVE -->
    #
    # This function generates our MiniMax tree nodes
    #
    # We recurse on the currentState object with the depth + 1
    # State nodes are represented by a python Dictionary
    #
    # this method also performs a form of alpha/beta pruning.
    #
    def recursiveMove(self, currentState, currentDepth, max):
        me = currentState.whoseTurn
        enemy = (currentState.whoseTurn + 1) % 2

        #generate list of all available moves. Leave out END TURN moves as a part of this
        moveList = listAllMovementMoves(currentState)
        #generate the list of all available nodes with a dictionary
        nodeList = [dict({'move': None, 'nextState': None, 'score':None}) for x in range(len(moveList))]
        for i, move in enumerate(moveList):
            #populate the generated empty dicts with the right stats
            nodeList[i]['move'] = move
            nodeList[i]['nextState'] = getNextStateAdversarial(currentState, move)
            nodeList[i]['score'] = self.evaluateState(nodeList[i]['nextState'])

        if (len(nodeList) == 0):
            #if we can make no more moves, return an END_TURN move type
            endMove = Move(END, None, None)
            nextState = getNextStateAdversarial(currentState, endMove)
            #switch to the min player flag
            max = not max
            #recurse with this new player flag
            return self.recursiveMove(nextState, currentDepth, max)

        #base case: return the state score, regardless of player
        if (currentDepth >= self.maxDepth):
            #return the score
            return self.evaluateState(currentState)

        # if the depth is 0, we return the move with the best score that got us there
        elif (currentDepth == 0):
            bestMove = Move(END, None, None)
            bestScore = 0.0
            beta = 0.0
            for node in nodeList:
                #store the score as "best" minimax score
                currScore = self.recursiveMove(node['nextState'], currentDepth + 1, max) #returns a score for each node
                #compare current score to the best one that ive seen
                if (max):
                    if (currScore > bestScore):
                        bestScore = currScore
                        #take that move that got you there
                        bestMove = node['move']
                    elif (beta <= currScore): #we are out of the cutoff range
                        break
                else:
                    #set the beta value to the best possible thing
                    beta = 1.0
                    bestScore = min(currScore, beta)
                    break
            #return the best move
            return bestMove

        #we are somewhere in the middle of the tree, get the score
        else:
            bestScore = 0.0
            beta = 0.0
            for node in nodeList:
                #store the score as "best" minimax score
                currScore = self.recursiveMove(node['nextState'], currentDepth + 1, max) #returns a score for each node
                #compare current score to the best one that ive seen
                if (max):
                    if (currScore > bestScore):
                        bestScore = currScore
                    elif (beta <= currScore):
                        #break out, we should prune since we've passed cutoff
                        break
                else:
                    #prune anything outside of this range
                    beta = 1.0
                    bestScore = min(currScore, beta)
                    break
            #return the best score we can find
            return bestScore
    ##
    #registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
