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
        numWorkers = len(getAntList(currentState, me, (WORKER,)))
        numSoldiers = len(getAntList(currentState, me, (SOLDIER,)))

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

        #if the queen is on the anthill move her
        if (myInv.getQueen().coords == myInv.getAnthill().coords):
            path = createPathToward(currentState, myInv.getQueen().coords,
                                        (0,3), UNIT_STATS[QUEEN][MOVEMENT])
            return Move(MOVE_ANT, path, None)

        #if I have enough food, build another worker to gather food.
        #Don't build more than 2 workers.
        if (myInv.foodCount > 1 and numWorkers < 3):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], WORKER)

        #Then Soldiers whenever we are able, if our opponent has any attacking units
        if (myInv.foodCount > 3 and numSoldiers < 2):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], SOLDIER)


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

        #move our soldiers. They all try to find the queen
        mySoldiers = getAntList(currentState, me, (SOLDIER,))
        for soldier in mySoldiers:
            if not (soldier.hasMoved):
                mySoldierX = soldier.coords[0]
                mySoldierY = soldier.coords[1]
                if (mySoldierY < 8): #move to enemy's side
                    mySoldierY += 1
                else:
                    mySoldierX += 1
                    #find the queen
                    enemyQueen = getAntList(currentState, None, (QUEEN,))
                    #create a path toward the queen
                    #print enemyQueen[0].coords
                    soldierPath = createPathToward(currentState, soldier.coords,
                                                 enemyQueen[0].coords, UNIT_STATS[SOLDIER][MOVEMENT])
                    Move(MOVE_ANT, soldierPath, None)
                if (mySoldierX,mySoldierY) in listReachableAdjacent(currentState, soldier.coords, 2):
                    return Move(MOVE_ANT, [soldier.coords, (mySoldierX, mySoldierY)], None)
                else:
                    return Move(MOVE_ANT, [soldier.coords], None)
        #If our move hasnt been ended, end our move here.
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
