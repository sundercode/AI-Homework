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
        super(AIPlayer,self).__init__(inputPlayerId, "A* Search")
        #the coordinates of the agent's food and tunnel will be stored in these
        #variables (see getMove() below)
        self.myFood = None
        self.myTunnel = None
        self.maxDepth = 1

    ##
    #getPlacement
    #
    # The agent uses a hardcoded arrangement for phase 1 to provide maximum
    # protection to the queen.  Enemy food is placed randomly.
    #
    def getPlacement(self, currentState):
        self.myFood = None
        self.myTunnel = None
        if currentState.phase == SETUP_PHASE_1:
            return [(0,0), (5, 1),
                    (0,3), (1,2), (2,1), (3,0), \
                    (0,2), (1,1), (2,0), \
                    (0,1), (1,0) ];
        elif currentState.phase == SETUP_PHASE_2:
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
            return None  #should never happen

    ##
    #getMove
    #
    # This agent simply gathers food as fast as it can with its worker.  It
    # never attacks and never builds more ants.  The queen is never moved.
    #
    ##
    def getMove(self, currentState):
        self.evaluateState(currentState)

        selectedMove = self.recursiveMove(currentState, self.maxDepth)

        #self.recursiveMove(currentState, 1)

        # moves = listAllLegalMoves(currentState)
        # selectedMove = moves[random.randint(0,len(moves) - 1)];
        #
        # #don't do a build move if there are already 3+ ants
        # numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        # while (selectedMove.moveType == BUILD and numAnts >= 3):
        #     selectedMove = moves[random.randint(0,len(moves) - 1)];

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
    # 0.0 means the enemy has won the game.
    # > 0.5 means you are currently winning
    #
    # gets passed the current game state object.
    #
    def evaluateState(self, currentState):
        #useful pointers. Set state score to a default value since we interpret 0 as losing.
        stateScore = 0.5
        me = currentState.whoseTurn
        enemy = (currentState.whoseTurn + 1) % 2
        myInv = currentState.inventories[me]
        enemyInv = currentState.inventories[not me]

        #Metrics that are important to evaluate:
        # number of ants each player has
        myAnts = getAntList(currentState, me,(QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER))
        enemyAnts = getAntList(currentState, enemy,(QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER))
        myAntCount = len(getAntList(currentState, me,(QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER)))
        enemyAntCount = len(getAntList(currentState, enemy, (QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER)))

        # types of ants each player has.
        myWorkers = getAntList(currentState, me,(WORKER,))

        #more than 2 workers is good
        if (len(myWorkers) >= 2 and len(myWorkers) < 4):
            stateScore = 0.7
            #print "I have 2+ workers"
            #return stateScore
        #less than 2 should indicate that the enemy has an advantage
        elif (len(myWorkers) < 2):
            stateScore = 0.4
            #print "I have less than 2 workers"
            #return stateScore

        enemyWorkers = getAntList(currentState, enemy,(WORKER,))
        enemyDrones = getAntList(currentState, enemy, (DRONE,))
        enemySoldiers = getAntList(currentState, enemy, (SOLDIER,))

        # How much food each player has
        myFood = myInv.foodCount
        enemyFood = enemyInv.foodCount
        foodDiff = myFood - enemyFood

        #if the difference in food counts is great
        if (foodDiff < 0):
            stateScore = 0.2
            #print "The enemy has more food than me"
            #return stateScore
        elif (foodDiff > 0):
            stateScore = 0.8
            #print "I have more food than my enemy"
            #return stateScore

        # how much food my workers are carrying.
        myCurrentFood = 0
        for worker in myWorkers:
            if (worker.carrying):
                myCurrentFood+=1

        if (myCurrentFood == len(myWorkers)):
            stateScore = 0.8
            #print "all of my workers are carrying food"
            #return stateScore
        #food metrics that determine a win/loss
        if (myFood == 10):
            stateScore = 1.0
            return stateScore
        if(enemyFood == 10):
            stateScore = 0.0
            return stateScore

        # give points if the workers are close to the tunnel/anthill with food
        goodWorkers = 0
        avg = 0
        for worker in myWorkers:
            if (worker.carrying and approxDist(worker.coords, myInv.getAnthill().coords) < 3):
                goodWorkers += 1
            elif (worker.carrying and approxDist(worker.coords, myInv.getTunnels()[0].coords) < 3):
                goodWorkers += 1
            elif (worker.carrying and approxDist(worker.coords, myInv.getAnthill().coords) > 3):
                stateScore = 0.4 #not moving towards the anthill
                #print "my workers are not moving to the anthill"
                #return stateScore
            elif (worker.carrying and approxDist(worker.coords, myInv.getTunnels()[0].coords) > 3):
                stateScore = 0.4 #not moving towards the tunnel
                #print "my workers are not moving to the tunnel"
                #return stateScore
        if (len(myWorkers) != 0):
            avg = goodWorkers/len(myWorkers)
            if (goodWorkers != 0 and avg != 0):
                #print "we have ants moving towards tunnels: " + str(avg)
                stateScore = avg
            if (avg == 1.0):
                stateScore = 0.9
                #print "all my workers are moving to the tunnel"
                #return stateScore
        else: #my workers are dead
            stateScore = 0.1
            #print "I have no workers"

        # how threatened are each players queens?
        myQueen = getAntList(currentState, me, (QUEEN,))[0]
        enemyQueen = getAntList(currentState, enemy, (QUEEN,))[0]

        # #get MY threat level
        self.threatToQueen(currentState, enemy, myQueen)
        self.threatToQueen(currentState, me, myQueen)

        self.protectionLevel(currentState, me)
        return stateScore
    ##
    # threatToQueen()
    #
    # takes the current state, queen ant, and looks for enemy ants
    #
    # The threat level increases by 1 the more enemies that are 1 move away.
    # threat level increases if the queen's health is not full AND enemies are close
    #
    # Threat level decreases when there are no close enemies
    #
    def threatToQueen(self, currentState, playerId, queen):
        threatLevel = 0
        # eventually wrap this in big IF to make sure there are even these kinds of enemies
        #find enemy ants, find their approximate distance from the queen.
        for ant in getAntList(currentState, playerId, (SOLDIER,DRONE)):

            #If my health is full and no enemies are within 2, return 0
            if (queen.health == 8 and approxDist(ant.coords, queen.coords) > 2):
                threatLevel = 0
                #print "no threat to queen found"
            #elif i do not have full health, increase threat by 1.
            elif (queen.health != 8 and approxDist(ant.coords, queen.coords) > 2):
                print "my queen is being threatened"
                threatLevel += 1
            #else there are enemies near. threat up by 1.
            else:
                threatLevel += 1
        return threatLevel
    ##
    # protectionLevel
    #
    # looks at the grass constructions and how well they protect the anthill.
    # returns an integer as a "protection score"
    #
    def protectionLevel(self, currentState, playerId):
        protectionLevel = 0
        grass = getConstrList(currentState, playerId, (GRASS,))
        anthill = getConstrList(currentState, playerId, (ANTHILL,))[0]
        for grassNode in grass:
            dist = approxDist(grassNode.coords, anthill.coords)
            if (dist > 3):
                if (protectionLevel > 0):
                    print "I am not very protected"
                    protectionLevel -=1
            else:
                print "I am fairly protected"
                protectionLevel += 1
        return protectionLevel

    ##
    # bestNodeScore
    #
    # takes a list of state nodes and returns the best score
    # the best score should help the choice of next state.
    #
    def bestNodeScore(self, nodeList):
        #make a list of just the scores from the nodes
        scoreList = [x["score"] for x in nodeList]

        for score in scoreList:
            if (max(scoreList) == score):
                return score
            else:
                return max(scoreList)

    def recursiveMove(self, currentState, currentDepth):
        #generate list of all available moves
        moveList = listAllMovementMoves(currentState)
        if (len(moveList) < 1):
            return None

        nodeList = [dict({'move': None, 'nextState': None, 'score':None}) for x in range(len(moveList))]
        for i, move in enumerate(moveList):
            nodeList[i]['move'] = move
            nodeList[i]['nextState'] = getNextState(currentState, move)
            nodeList[i]['score'] = self.evaluateState(nodeList[i]['nextState'])

        if (len(nodeList) == 0):
            #if we can make no more moves, return an END_TURN move type
            nodeList = [dict({'move': Move(END, None, None), 'nextState': None, 'score': None})]

        #base case: return the state score
        if (currentDepth > self.maxDepth):
            return self.evaluateState(currentState)
        #if we are at the head of the tree, return best scored node's move
        elif (currentDepth == 0):
            currScore = self.bestNodeScore(nodeList) #highest score
            for node in nodeList:
                #find the node with this score
                if (node['score'] == currScore):
                    return node['move']
        #if we are somewhere in the middle of the tree, recurse
        else:
            #recursively call this on the state with the highest score
            currScore = self.bestNodeScore(nodeList) #highest score
            for node in nodeList:
                #find the node with this score
                if (node['score'] == currScore):
                    return self.recursiveMove(node['nextState'], currentDepth + 1)


    ##
    # generateNode()
    #
    # takes the various parameters needed to create our state nodes and maps them
    # to their correct dictionary keys. helper function to create a list of all nodes.
    #
    def generateNode(self, move, nextState, score, children):
        currentNode = {"move": move, "next_state": nextState, "score": score}
        return currentNode

    ##
    #registerWin
    #
    # This agent doesn't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
