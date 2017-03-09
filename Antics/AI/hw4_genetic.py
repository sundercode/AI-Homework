import random
import sys
sys.path.append("..")  #so other modules can be found in parent dir
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import UNIT_STATS
from Move import Move
from GameState import *
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
        super(AIPlayer,self).__init__(inputPlayerId, "Genetic AI")
        #List of genes to be tested
        self.population = []

        #List of scores correlated to genes in population
        self.popFitness = []

        #Index for which gene to test
        self.geneIndex = 0

        #Size of the population of genes
        self.POP_SIZE = 10

        #Number of games played to test each gene
        self.NUM_GAMES = 10

        #best score we've seen so far
        self.bestScore = 0
        #save the best state
        self.bestState = None

        self.cState = None

        #Games played so far
        self.gamesPlayed = 0

        #Mutation Chance
        self.MUTATION_CHANCE = 10
        self.initPopulation()

    ##
    #initPopulation
    #Description: Initializes our population to random values
    #             And resets our popFitness scores to 0
    #
    #Parameters: None, this method just intializes instance variables
    ##
    def initPopulation(self):
        print "initializing population"
        gene = []
        self.popFitness = [0]*self.POP_SIZE
        #Create a gene for each member of the population
        for s in range(0, self.POP_SIZE):
            #Create random unique values for the first 11 slots
            #These will represent the palcement of grass and hill and tunnel
            for i in range(0, 11):
                placement = None
                while placement == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on our side of the board
                    y = random.randint(0, 3)
                    #Set the placement if this is a unique placement
                    if (x, y) not in gene:
                        placement = (x, y)
                gene.append(placement)
            #Create the first enemy food location
            x = random.randint(0, 9)
            y = random.randint(6, 9)
            placement = (x,y)
            gene.append(placement)


            #Create the second food placement, distinct from the first
            done = False
            while not done:
                x = random.randint(0, 9)
                #Choose any y location on enemy side of the board
                y = random.randint(6, 9)
                #Set the move if != to previous
                if (x, y) != placement:
                    placement = (x, y)
                    done = True

            gene.append(placement)

            self.population.append(gene)
            gene = []

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        print "placing new items"
        numToPlace = 0
        self.cState = currentState
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            #slice to index 11
            firstSlice = self.population[self.geneIndex][:11]
            #return the placement
            return firstSlice
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            secondSlice = self.population[self.geneIndex][11:]
            x = secondSlice[0][0]
            y = secondSlice[0][1]
            x2 = secondSlice[1][0]
            y2 = secondSlice[1][1]
            #while it's not empty....
            while (currentState.board[x][y].constr != None):
                #fix it
                x -= 1
            while (currentState.board[x2][y2].constr != None):
                x2 -= 1
            secondSlice[0] = (x,y)
            secondSlice[1] = (x2, y2)
            return secondSlice

        else:
            return [(0, 0)]

    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        moves = listAllLegalMoves(currentState)
        selectedMove = moves[random.randint(0,len(moves) - 1)];

        #don't do a build move if there are already 3+ ants
        numAnts = len(currentState.inventories[currentState.whoseTurn].ants)
        while (selectedMove.moveType == BUILD and numAnts >= 3):
            selectedMove = moves[random.randint(0,len(moves) - 1)];

        return selectedMove

    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:1
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy.
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]


    ##
    #registerWin
    #Description: Tells the player if they won or not
    #
    #Parameters:
    #   hasWon - True if the player won the game. False if they lost (Boolean)
    #
    def registerWin(self, hasWon):
        if hasWon:
            print "we won!!"
            self.popFitness[self.geneIndex] += 1
        self.gamesPlayed += 1

        #if we've reached our game limit for this gene, move to the next one
        if (self.gamesPlayed == self.NUM_GAMES):
            print self.popFitness[self.geneIndex]
            if (self.popFitness[self.geneIndex] > self.bestScore):
                self.bestScore = self.popFitness[self.geneIndex]
                self.bestState = self.cState
            self.geneIndex += 1
            self.gamesPlayed = 0

        #if we have gone through the whole population, create a new generation
        if (self.geneIndex == self.POP_SIZE):
            print "jumping to next generation in RegsiterWin"
            #output the best state to a file.
            if (self.bestState == None):
                self.bestState = self.cState
            original = sys.stdout
            sys.stdout = open('evidence382017.txt', 'a')
            asciiPrintState(self.bestState)
            sys.stdout = original

            self.geneIndex = 0
            self.bestState = None
            self.bestScore = 0
            self.popFitness = [0]*self.POP_SIZE
            self.createNextGeneration()

    ##
    #createNextGeneration
    #Description: creates the next generation of genes from the population of
    # parents using the fittest 4 genes to make another population.
    #
    # modifies the population instance variable with the newest generation
    #
    def createNextGeneration(self):
        scoredGenes = []
        #associate the scores with the right genes, sorted
        scoredGenes = zip(self.popFitness, self.population)
        scoredGenes = sorted(scoredGenes, key=lambda gene: gene[0])

        #variable for next generation
        nextGen = []
        kids = []

        #get the 2 top scoring genes, use them to create 10 more children
        best = scoredGenes[0][1]
        secondBest = scoredGenes[1][1]

        #HARD CODED for population 10
        for i in range(3):
            #mate 0 with 1, 2, 3
            kids = self.createChildren(best, scoredGenes[i+1][1])
            nextGen.append(kids[0])
            nextGen.append(kids[1])
        for i in range(2):
            #mate 1 with 2, 3
            kids = self.createChildren(secondBest, scoredGenes[i+2][1])
            nextGen.append(kids[0])
            nextGen.append(kids[1])
        #set the population for the next generation
        self.population = nextGen
    ##
    #createChildren
    #Description: helper method to createNextGeneration, creates 2 child genes
    # from 2 parents. swaps gene chunks at a random index with 10% to mutate.
    #
    #Parameters:
    #   parent1 - first parent gene
    #   parent2 - second parent gene
    #
    # Returns the list of 2 children
    #
    def createChildren(self,parent1, parent2):
        print "creating new children, mixing genes"
        children = []
        childA = []
        childB = []
        conflicts = True

        #Slicing and Conflict Management
        while(conflicts):
            conflicts = False
            pos1 = random.randint(1,10)
            pos2 = random.randint(pos1+1, 12)

            childA = parent1[:pos1] + parent2[pos1:pos2] + parent1[pos2:]

            childB = parent2[:pos1] + parent1[pos1:pos2] + parent2[pos2:]

            if(len(childA[:11]) != len(set(childA[:11])) or len(childB[:11]) != len(set(childB[:11]))):
                conflicts = True

            if(childA[11] == childA[12] or childB[11] == childB[12]):
                conflicts = True
                # childA = []
                # childB = []

        #Mutation
        if(random.randrange(100) < self.MUTATION_CHANCE):
            conflicts = True
            pos = random.randint(0,12)
            while conflicts:
                conflicts = False
                if pos == 11 or pos == 12:
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(6, 9)
                    childA[pos] = (x,y)
                    if(childA[11] == childA[12]):
                        conflicts = True

                else:
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    childA[pos] = (x,y)
                    if len(childA[:11]) != len(set(childA[:11])):
                        conflicts = True

        children.append(childA)
        children.append(childB)
        print children
        return children
