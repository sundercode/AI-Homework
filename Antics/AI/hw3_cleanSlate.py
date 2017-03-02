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
        super(AIPlayer,self).__init__(inputPlayerId, "MiniMax Search copy")
        #the coordinates of the agent's food and tunnel will be stored in these
        #variables (see getMove() below)
        self.myFood = None
        self.myTunnel = None
        self.maxDepth = 3

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
        #make a move based on our recursive call
        selectedMove = self.recursiveMove(currentState, 0)
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
    # TODO:: add more metrics to evaluate, like threat level and protection level to the
    # weighted value. assign enemy playerID?
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

    # threatToQueen()
    #
    # takes the current state, queen ant, and looks for enemy ants
    #
    # The threat level increases by 1 the more enemies that are 1 move away.
    # threat level increases if the queen's health is not full AND enemies are close
    #
    def threatToQueen(self, currentState, playerId, queen):
        threatLevel = 0
        # eventually wrap this in big IF to make sure there are even these kinds of enemies
        #find enemy ants, find their approximate distance from the queen.
        for ant in getAntList(currentState, playerId, (SOLDIER,DRONE)):

            #If my health is full and no enemies are within 2, return 0
            if (queen.health == 8 and approxDist(ant.coords, queen.coords) > 2):
                threatLevel = 0
                return threatLevel

            #elif i do not have full health, increase threat by 1.
            elif (queen.health != 8 and approxDist(ant.coords, queen.coords) > 2):
                threatLevel += 1

            #else there are enemies near. threat up by 1.
            else:
                threatLevel += 1

        return threatLevel

    ##
    # bestNodeScore
    #
    # takes a list of state nodes and returns the best score
    # the best score should help the choice of next state.
    #
    # For HW 3, this takes the min or max score based on what players
    # turn it is
    #
    def bestNodeScore(self, nodeList, currentState, playerId):
        #take player IDs into account, take a min or max based on that fact
        me = currentState.whoseTurn ## should be 1
        enemy = (currentState.whoseTurn + 1) % 2 ##should be 0

        #make a list of just the scores from the nodes
        scoreList = [x["score"] for x in nodeList]

        if (playerId == me):
            return max(scoreList)
            #return some sort of tuple?
        else:
            return min(scoreList)
            #return some sort of tuple?

    ##
    # recursiveMove <!-- RECURSIVE -->
    #
    # This function generates our A* node tree to traverse.
    #
    # We recurse on the currentState object with the depth + 1
    # State nodes are represented by a python Dictionary
    #
    # TODO:: modify this so that it takes the opponents moves into account
    #
    def recursiveMove(self, currentState, currentDepth):

        me = currentState.whoseTurn ## should be 1
        enemy = (currentState.whoseTurn + 1) % 2 ##should be 0

        #generate list of all available moves. Leave out END TURN moves as a part of this
        moveList = listAllMovementMoves(currentState)

        #generate the list of all available nodes with a dictionary
        nodeList = [dict({'move': None, 'nextState': None, 'score':None}) for x in range(len(moveList))]
        for i, move in enumerate(moveList):
            #populate the generated empty dicts with the right stats
            nodeList[i]['move'] = move
            nodeList[i]['nextState'] = getNextStateAdversarial(currentState, move) #this switches the state!
            nodeList[i]['score'] = self.evaluateState(nodeList[i]['nextState'])

        if (len(nodeList) == 0):
            #if we can make no more moves, return an END_TURN move type
            nodeList = [dict({'move': Move(END, None, None), 'nextState': None, 'score': None})]
            #could call here with max == false, since that's the only time it gets set
            return nodeList[0]['move']

        #base case: return the state score
        if (currentDepth >= self.maxDepth):
            #max agent will want the max score, while the min agent wants the lowest
            return self.evaluateState(currentState)

        #if we are at the head of the tree, return best scored node's move, min or max
        elif (currentDepth == 0):
            currScore = self.bestNodeScore(nodeList, currentState, me) #highest score, we should only do this to prune?
            for node in nodeList:
                #find the node with this score, this does dfs by default i think
                if (node['score'] == currScore):
                    return node['move']

        #we are somewhere in the middle of the tree, recurse
        # else:
        #     #recursively call this on the state with the highest score
        #     currScore = self.bestNodeScore(nodeList) #highest score
        #     for node in nodeList:
        #         #find the node with this score
        #         if (node['score'] == currScore):
        #             return self.recursiveMove(node['nextState'], currentDepth + 1)
    ##
    #registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
