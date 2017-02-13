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

        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];

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
        #useful pointers.
        stateScore = 0.0
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
        myDrones = getAntList(currentState, me, (DRONE,))
        mySoldiers = getAntList(currentState, me, (SOLDIER,))

        enemyWorkers = getAntList(currentState, enemy,(WORKER,))
        enemyDrones = getAntList(currentState, enemy, (DRONE,))
        enemySoldiers = getAntList(currentState, enemy, (SOLDIER,))
        enemyRanged = getAntList(currentState, enemy, (R_SOLDIER,))

        # health of ants that each player has.
        # if an ant's health is not full, we can assume we are being threatened,
        # return a lower state score as a result
        # myTotalHealth = 0;
        # for ant in myAnts:
        #     myTotalHealth += ant.health
        #     if (ant.health < UNIT_STATS[ant.type][HEALTH]):
        #         print ant.type + "doesnt have full health"
        #         stateScore = 0.4
        #         return stateScore

        # How much food each player has
        myFood = myInv.foodCount
        enemyFood = enemyInv.foodCount
        foodDiff = myFood - enemyFood

        #if the difference in food counts is great
        if (foodDiff < 0):
            stateScore = abs(foodDiff) / 10
            return stateScore
        elif (myFood > 0):
            stateScore = foodDiff / 10
            return stateScore

        # how much food my workers are carrying.
        myCurrentFood = 0
        for worker in myWorkers:
            if (worker.carrying):
                myCurrentFood+=1

        if (myFood == 10):
            stateScore = 1.0
            return stateScore
        if(enemyFood == 10):
            stateScore = 0.0
            return stateScore

        # how threatened are each players queens?
        # If our queen is threatened the most, the stateScore gets decrimented
        # if our enemy is, the score would increase
        myQueen = getAntList(currentState, me, (QUEEN,))[0]
        enemyQueen = getAntList(currentState, enemy, (QUEEN,))[0]

        # #get MY threat level
        # if (self.threatToQueen(currentState, me, myQueen ) > 3):
        #     stateScore = 0.2
        #     return stateScore
        # # #get enemy threat level
        # if (self.threatToQueen(currentState, enemy, enemyQueen) > 3):
        #     #we are threatening the enemy, good job
        #     stateScore = 0.7
        #     return stateScore

        # # how well protected my anthill is.
        # # count grass nodes and get their proximity to the anthill.
        # if (self.protectionLevel(currentState, me) < 3):
        #     if (stateScore > 0):
        #         stateScore -= 0.1
        # else:
        #     if (stateScore < 10):
        #         stateScore += 0.1

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
    #
    def threatToQueen(self, currentState, playerId, queen):
        threatLevel = 0
        # eventually wrap this in big IF to make sure there are even these kinds of enemies
        #find enemy ants, find their approximate distance from the queen.
        for ant in getAntList(currentState, playerId, (SOLDIER,DRONE)):

            #If my health is full and no enemies are within 2, decrease threat
            if (queen.health == 8 and approxDist(ant.coords, queen.coords) > 2):
                if (threatLevel > 0):
                    threatLevel -= 1
            #elif i do not have full health, increase threat by 1.
            elif (queen.health != 8 and approxDist(ant.coords, queen.coords) > 2):
                threatLevel += 1
            #else there are enemies near. threat up by 1.
            else:
                threatLevel += 1

        return threatLevel

    def protectionLevel(self, currentState, playerId):
        protectionLevel = 0
        grass = getConstrList(currentState, playerId, (GRASS,))
        anthill = getConstrList(currentState, playerId, (ANTHILL,))[0]
        for grassNode in grass:
            dist = approxDist(grassNode.coords, anthill.coords)
            if (dist > 3):
                if (protectionLevel > 0):
                    protectionLevel -=1
            else:
                protectionLevel += 1
        return protectionLevel

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
