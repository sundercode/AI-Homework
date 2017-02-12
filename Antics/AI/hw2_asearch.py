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
        #Useful pointers
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn

        self.evaluateState(currentState)

        #the first time this method is called, the food and tunnel locations
        #need to be recorded in their respective instance variables
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood == None):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            #find the food closest to the tunnel
            bestDistSoFar = 1000 #i.e., infinity
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFood = food
                    bestDistSoFar = dist

        #if I don't have a worker, give up.  QQ
        numAnts = len(myInv.ants)
        if (numAnts == 1):
            return Move(END, None, None)

        #if the worker has already moved, we're done
        myWorker = getAntList(currentState, me, (WORKER,))[0]
        if (myWorker.hasMoved):
            return Move(END, None, None)

        #if the queen is on the anthill move her
        myQueen = myInv.getQueen()
        if (myQueen.coords == myInv.getAnthill().coords):
            return Move(MOVE_ANT, [myInv.getQueen().coords, (1,0)], None)

        #if the hasn't moved, have her move in place so she will attack
        if (not myQueen.hasMoved):
            return Move(MOVE_ANT, [myQueen.coords], None)

        #if I have the foos and the anthill is unoccupied then
        #make a drone
        if (myInv.foodCount > 2):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], DRONE)

        #Move all my drones towards the enemy
        myDrones = getAntList(currentState, me, (DRONE,))
        for drone in myDrones:
            if not (drone.hasMoved):
                droneX = drone.coords[0]
                droneY = drone.coords[1]
                if (droneY < 9):
                    droneY += 1;
                else:
                    droneX += 1;
                if (droneX,droneY) in listReachableAdjacent(currentState, drone.coords, 3):
                    return Move(MOVE_ANT, [drone.coords, (droneX, droneY)], None)
                else:
                    return Move(MOVE_ANT, [drone.coords], None)

        #if the worker has food, move toward tunnel
        if (myWorker.carrying):
            path = createPathToward(currentState, myWorker.coords,
                                    self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)

        #if the worker has no food, move toward food
        else:
            path = createPathToward(currentState, myWorker.coords,
                                    self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
            return Move(MOVE_ANT, path, None)


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
        moveScore = 0.0
        me = currentState.whoseTurn
        enemy = (currentState.whoseTurn + 1) % 2

        myInv = getCurrPlayerInventory(currentState)
        enemyInv = []

        if (myInv.player != me):
            enemyInv = myInv

        #Metrics that are important to evaluate:
        # number of ants each player has
        myAntCount = len(getAntList(currentState, me,(QUEEN, WORKER, DRONE)))
        enemyAntCount = len(getAntList(currentState, enemy, (QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER)))

        # types of ants each player has. We assume that there's only one queen.
        # let's prioritize having more drones than anything else. At most 2 workers.
        # don't worry about my soldiers/ranged. we arent going to build these.
        myWorkers = getAntList(currentState, me,(WORKER,))
        myDrones = getAntList(currentState, me, (DRONE,))

        enemyWorkers = getAntList(currentState, enemy,(WORKER,))
        enemyDrones = getAntList(currentState, enemy, (DRONE,))
        enemySoldiers = getAntList(currentState, enemy, (SOLDIER,))
        enemyRanged = getAntList(currentState, enemy, (R_SOLDIER,))

        # health of ants that each player has.
        # just loop through each ant and access ant.health property
        # if an ant's health is not full, we can assume we are being threatened
        #full health we can assume that we are doing ok, and can up the move score.

        # How much food each player has
        myFood = myInv.foodCount
        enemyFood = enemyInv.foodCount

        # how much food each player's workers are carrying.
        myCurrentFood = 0
        for i, worker in myWorkers:
            if (worker.carrying):
                i+=1
        enemyCurrentFood = 0
        for enemyCurrentFood, worker in enemyWorkers:
            if (worker.carrying):
                j+=1

        # how threatened are each players queens? (proximity to enemy)
        # If our queen is threatened the most, the movescore gets decrimented (if > 0.0)
        # if our enemy is, the move score would increase. ++ 0.1? (if< 1.0)
        myQueen = getAntList(currentState, me, (QUEEN,))
        enemyQueen = getAntList(currentState, enemy, (QUEEN,))

        #get MY threat level
        if (self.threatToQueen(currentState, me, myQueen ) > 2):
            # only decrement the moveScore if we can. otherwise leave it as it is.
            if (moveScore > 0.0):
                moveScore -= 0.1
        #get enemy threat level
        if (self.threatToQueen(currentState, enemy, enemyQueen) > 2):
            #we are threatening the enemy, good job
            if (moveScore < 1.0):
                moveScore += 0.1

        # how well protected my anthill is.
        # count grass nodes and get their proximity to the anthill.

        return moveScore

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
            if (queen.health == 8 && approxDist(ant.coords, queen.coords) > 2):
                if (threatLevel > 0):
                    threatLevel -= 1
            #elif i do not have full health, increase threat by 1.
            elif (queen.health != 8 && approxDist(ant.coords, queen.coords) > 2):
                threatLevel += 1
            #else there are enemies near. threat up by 1.
            else
                threatLevel += 1

        return threatLevel

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
