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
    #This agent will build 2 workers to gather food and build soldiers to
    #protect it's territory, while sending some into the enemy side.
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

        #if we have enough food, build a soldier
        if (myInv.foodCount > 3 and numSoldiers < 2):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], SOLDIER)

        #if I have enough food, build another worker to gather food.
        #Don't build more than 2 workers.
        if (myInv.foodCount > 1 and numWorkers < 3):
            if (getAntAt(currentState, myInv.getAnthill().coords) is None):
                return Move(BUILD, [myInv.getAnthill().coords], WORKER)

        ##USE MATTS MOVE WORKER METHOD
        myWorkers = getAntList(currentState, me, (WORKER,))
        for worker in myWorkers:
            if (worker.hasMoved): continue
            #if the worker has food, move toward tunnel
            if (worker.carrying):
                path = createPathToward(currentState, worker.coords,
                                        self.myTunnel.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, path, None)
            #if the worker has no food, move toward food
            else:
                path = createPathToward(currentState, worker.coords,
                                        self.myFood.coords, UNIT_STATS[WORKER][MOVEMENT])
                return Move(MOVE_ANT, path, None)
        ##USE MATT'S MOVE WORKER METHOD

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
    # get the attack that we want to perform on the enemy.
    # currentState - the game state
    # attackingAnt - the Ant object currently making the attack
    # enemyLocations - The Location objects of the Enemies that can be attacked
    #
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Useful pointers
        myInv = getCurrPlayerInventory(currentState)
        me = currentState.whoseTurn
        numWorkers = len(getAntList(currentState, me, (WORKER,)))
        numSoldiers = len(getAntList(currentState, me, (SOLDIER,)))

        #scan the surrounding area for an enemy
        print "I am trying to find an attack for my soldier"

        #if there is an enemy, attack until you cant attack anymore (aka die)

        #scan again. if there are no enemies, stay where you are
        return enemyLocations[0]  #don't care

    ##
    #registerWin
    #
    # This agent doens't learn
    #
    def registerWin(self, hasWon):
        #method template, not implemented
        pass
