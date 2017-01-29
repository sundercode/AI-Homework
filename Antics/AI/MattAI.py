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
        super(AIPlayer,self).__init__(inputPlayerId, "MattAI")
        #the coordinates of the agent's food and tunnel will be stored in these
        #variables (see getMove() below)
        self.myFood = None
        self.myFood1 = None
        self.myFood2 = None
        self.myTunnel = None
        self.myAnthill = None
        self.enemyAnthill = None
        self.enemyTunnel = None
        #self.playerId = imputPlayerId

    ##
    #getPlacement
    #
    # The agent uses a hardcoded arrangement for phase 1 to provide maximum
    # protection to the queen.  Enemy food is placed randomly.
    #
    #



    #Adjust this to set some more optimal placement
    def getPlacement(self, currentState):
        self.myFood = None
        self.myFood1 = None
        self.myFood2 = None
        self.myTunnel = None
        self.enemyAnthill = None
        self.enemyTunnel = None
        self.constrCoords = None

        if (currentState.whoseTurn == PLAYER_TWO):
            #we are player 1
            enemy = 1
        else:
            enemy = 0

        if currentState.phase == SETUP_PHASE_1:
            return [(2,1), (7, 2),
                    (6,3), (5,3), (0,3), (1,3), \
                    (2,3), (3,3), (4,3), \
                    (5,0), (9,0) ];

        #set the enemy food to the least optimal places
        elif currentState.phase == SETUP_PHASE_2:
            self.enemyAnthill = getConstrList(currentState, enemy, (ANTHILL,))[0]
            self.enemyTunnel = getConstrList(currentState, enemy, (TUNNEL,))[0]
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):
                for j in range(0,9):
                    for k in range (6,9):
                        move = None
                        #while move == None:
                            #Find the farthest open space
                        if(((stepsToReach(currentState, (j,k), self.enemyTunnel.coords)) + (stepsToReach(currentState, (j,k), self.enemyAnthill.coords)))\
                                > ((stepsToReach(currentState, moves, self.enemyTunnel.coords)) + (stepsToReach(currentState, moves, self.enemyAnthill.coords)))):
                            #moves = (j,k)
                                #Set the move if this space is empty
                                if currentState.board[j][k].constr == None and (j, k) not in moves:
                                    move = (j, k)
                                    #Just need to make the space non-empty. So I threw whatever I felt like in there.
                                    currentState.board[j][k].constr == True
                                    moves.append(move)
            return moves


    ##
    #getMove
    #
    #
    #Adjust this to create more ants and start with a greater gathering force to get food faster
    #also try to adjust efficieny and opt for the best paths and ants for the gathering job
    ##
    def getMove(self, currentState):
        #Useful pointers
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn
        foods = getConstrList(currentState, None, (FOOD,))
        bestDistSoFar = 1000 #i.e., infinity
        bestDistSoFar2 = 1000 #i.e., infinity

        #if (me == 1)
        #    enemy = 2
        #else
        #    enemy = 1
        #the first time this method is called, the food and tunnel locations
        #need to be recorded in their respective instance variables
        if (self.myAnthill == None):
            self.myAnthill = getConstrList(currentState, me, (ANTHILL,))[0]
        if (self.myTunnel == None):
            self.myTunnel = getConstrList(currentState, me, (TUNNEL,))[0]
        if (self.myFood == None):
            foods = getConstrList(currentState, None, (FOOD,))
            self.myFood = foods[0]
            #find the food closest to the tunnel
            for food in foods:
                dist = stepsToReach(currentState, self.myTunnel.coords, food.coords)
                if (dist < bestDistSoFar):
                    self.myFood1 = food
                    bestDistSoFar = dist

            #find the closest to the anthill
            for food in foods:
                dist2 = stepsToReach(currentState, self.myAnthill.coords, food.coords)
                if (dist2 < bestDistSoFar2):
                    self.myFood2 = food
                    bestDistSoFar2 = dist2

            #if(self.myFood1 == None):
            #        self.myFood1 = foods[1]
            #    else:
            #        self.myFood1 = foods[0]
#
#            if(self.myFood2 == None):
#                if(self.myFood1 == foods[0]):
#                    self.myFood2 = foods[1]
#                else:
#                    self.myFood2 = foods[0]
        #if the queen is on the anthill move her
        if (myInv.getQueen().coords == myInv.getAnthill().coords):
            path = createPathToward(currentState, myInv.getQueen().coords,
                                        (0,3), UNIT_STATS[QUEEN][MOVEMENT])
            return Move(MOVE_ANT, path, None)

        #Start with 2 Workers
        numAnts = len(myInv.ants)
        if (myInv.foodCount > 1 and numAnts < 5 and getAntAt(currentState, self.myAnthill.coords) == None):
            return Move(BUILD, [self.myAnthill.coords], WORKER)

        #Then 2 Drones
        #if (myInv.foodCount > 1 and numAnts < 5 and getAntAt(currentState, self.myAnthill.coords) == None):
        #    return Move(BUILD, [self.myAnthill.coords], DRONE)

        #Then Soldiers whenever we are able, if our opponent has any attacking units
        if (myInv.foodCount > 3 and numAnts > 5 and getAntAt(currentState, self.myAnthill.coords) == None):
            return Move(BUILD, [self.myAnthill.coords], SOLDIER)


       #WORKER Orders
        myWorkers = getAntList(currentState, me, (WORKER,))
        for index, worker in enumerate(myWorkers):
            if (worker.hasMoved): continue
            if(index == 0 or index == 2):
                constrCoords = self.myTunnel.coords
                targetFood = self.myFood1
            else:
                constrCoords = self.myAnthill.coords
                targetFood = self.myFood2


            #if the worker has food, move toward constr
            if (worker.carrying):
                path = createPathToward(currentState, worker.coords,
                                        constrCoords, UNIT_STATS[WORKER][MOVEMENT])
                if (path == [worker.coords]):
                        path = listAllMovementPaths(currentState,worker.coords, UNIT_STATS[WORKER][MOVEMENT])[0]
                return Move(MOVE_ANT, path, None)

            #if the worker has no food, move toward food
            else:
                path = createPathToward(currentState, worker.coords,
                                        targetFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                if (path == [worker.coords]):
                    path = listAllMovementPaths(currentState,worker.coords, UNIT_STATS[WORKER][MOVEMENT])[0]
                return Move(MOVE_ANT, path, None)

        #DRONE Orders
        myDrones = getAntList(currentState, me, (DRONE,))
        for i, drone in enumerate(myDrones):
            if (drone.hasMoved): continue
            if(i == 1):
                constrCoords = self.myAnthill.coords
                targetFood = self.myFood2
            else:
                constrCoords = self.myTunnel.coords
                targetFood = self.myFood1

            #if the drone has food, move toward tunnel
            if (drone.carrying):
                path = createPathToward(currentState, drone.coords,
                                        constrCoords, UNIT_STATS[DRONE][MOVEMENT])
                if (path == [drone.coords]):
                        path = listAllMovementPaths(currentState,drone.coords, UNIT_STATS[DRONE][MOVEMENT])[0]
                return Move(MOVE_ANT, path, None)

            #if the drone has no food, move toward food
            else:
                path = createPathToward(currentState, drone.coords,
                                        targetFood.coords, UNIT_STATS[DRONE][MOVEMENT])
                if (path == [drone.coords]):
                    path = listAllMovementPaths(currentState,drone.coords, UNIT_STATS[DRONE][MOVEMENT])[0]
                return Move(MOVE_ANT, path, None)
        return Move(END, None, None)
    ##
    #getAttack
    #
    # This agent never attacks
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        return enemyLocations[0]  #don't care

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
