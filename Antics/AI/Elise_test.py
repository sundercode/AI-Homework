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
        super(AIPlayer,self).__init__(inputPlayerId, "Offensive")
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
        numWorkers = len(getAntList(currentState, me, (WORKER,)))
        numSoldiers = len(getAntList(currentState, me, (SOLDIER,)))

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

        #if the queen is on the anthill move her
        if (myInv.getQueen().coords == myInv.getAnthill().coords):
            return Move(MOVE_ANT, [myInv.getQueen().coords, (1,0)], None)

        #if we have enough food, build a soldier? drone?
        if (myInv.foodCount > 3 and numSoldiers < 2):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], SOLDIER)

        #if I have enough food, build another worker to gather food.
        #Don't build more than 2 workers.
        if (myInv.foodCount > 1 and numWorkers < 2):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], WORKER)

        #if the worker has already moved, we're done
        #make sure to move all workers
        myWorkers = getAntList(currentState, me, (WORKER,))
        for worker in myWorkers:
            if (worker.hasMoved): continue

            #if the worker has food, move toward tunnel
            if (worker.carrying):
                path = createPathToward(currentState, worker.coords,
                                        self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])

                #if there is an ant in my way, find a different path
                for coord in listReachableAdjacent(currentState, worker.coords, 2):
                    if getAntAt(currentState, coord):
                        listAllLegalMoves(currentState)
                        #make arbitrary legal move to get out of the way
                        path = listAllLegalMoves(currentState)[0]
                return Move(MOVE_ANT, path, None)

            #if the worker has no food, move toward food
            else:
                path = createPathToward(currentState, worker.coords,
                                        self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, path, None)
            # reachable = listReachableAdjacent(currentState, worker.coords, 2)
            # for coord in reachable:
            #     if

        #move our soldiers. one to the enemy side and one that stays right on our border.
        mySoldiers = getAntList(currentState, me, (SOLDIER,))

        #move to the enemy side
        if (numSoldiers == 1):
            if not (mySoldiers[0].hasMoved):
                mySoldierX = mySoldiers[0].coords[0]
                mySoldierY = mySoldiers[0].coords[1]
                if (mySoldierY < 8): #if the y is less than 7, we havent reached the enemy's side
                    mySoldierY += 1
                else:
                    return Move(END, None, None) #end our movement forward for now
                    #getAttack(currentState, mySoldiers[0], enemyLocation1)
                if (mySoldierX,mySoldierY) in listReachableAdjacent(currentState, mySoldiers[0].coords, 2):
                    return Move(MOVE_ANT, [mySoldiers[0].coords, (mySoldierX, mySoldierY)], None)
                else:
                    return Move(MOVE_ANT, [mySoldiers[0].coords], None)

        #stay right on our border (is there a method to tell which is our territory?)
        #do we always assume that our grid has (0,0) on the bottom left?
        if (numSoldiers == 2):
            if not (mySoldiers[1].hasMoved):
                mySoldierX = mySoldiers[1].coords[0]
                mySoldierY = mySoldiers[1].coords[1]
                if (mySoldierY < 4): #if the y is less than 7, we havent reached the enemy's side
                    mySoldierY += 1
                elif (mySoldierX < 5):
                    mySoldierX += 1
                else:
                    return Move(END, None, None) #end our movement forward for now
                    #getAttack(currentState, mySoldiers[0], enemyLocation1)
                if (mySoldierX,mySoldierY) in listReachableAdjacent(currentState, mySoldiers[1].coords, 3):
                    return Move(MOVE_ANT, [mySoldiers[1].coords, (mySoldierX, mySoldierY)], None)
                else:
                    return Move(MOVE_ANT, [mySoldiers[1].coords], None)
        return Move(END, None, None)

    ##
    #getAttack
    #
    # get the attack that we want to perform on the enemy.
    # currentState - the game state
    # attackingAnt - the Ant object currently making the attack
    # enemyLocations - The Location objects of the Enemies that can be attacked
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #scan the surrounding area for an enemy
        #getAntList(currentState, !me, None) -> all enemy ants?
        #

        #if there is an enemy, attack until you cant attack anymore (aka die)

        #scan again. if there are no enemies, stay where you are
        return enemyLocations[0]  #don't care

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method templaste, not implemented
        pass
