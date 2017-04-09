def mapping(self, currentState):
    #Currently has 27 inputs. This might change with
    #Things that want to be added or the biases
    input = np.zeros(27)
    me = currentState.whoseTurn
    enemy = (currentState.whoseTurn + 1) % 2
    myInv = currentState.inventories[me]
    enemyInv = currentState.inventories[not me]

    myFood = myInv.foodCount
    enemyFood = enemyInv.foodCount

    #This whole chunk adds a 1 to a spot that corresponds to a
    #certain food count. Increasing positive weight
    if(myFood == 0):
        input[0] = 1
        for x in range(10):
            input[x+1] = 0
    if(myFood == 1):
        input[1] = 1
        input[0] = 0
        for x in range(1,11):
            input[x] = 0
    if(myFood == 2):
        input[2] = 1
        for x in range(1):
            input[x] = 0
        for x in range(2,11):
            input[x] = 0
    if(myFood == 3):
        input[3] = 1
        for x in range(2):
            input[x] = 0
        for x in range(3,11):
            input[x] = 0
    if(myFood == 4):
        input[4] = 1
        for x in range(3):
            input[x] = 0
        for x in range(4,11):
            input[x] = 0
    if(myFood == 5):
        input[5] = 1
        for x in range(4):
            input[x] = 0
        for x in range(5,11):
            input[x] = 0
    if(myFood == 6):
        input[6] = 1
        for x in range(5):
            input[x] = 0
        for x in range(6,11):
            input[x] = 0
    if(myFood == 7):
        input[7] = 1
        for x in range(6):
            input[x] = 0
        for x in range(7,11):
            input[x] = 0
    if(myFood == 8):
        input[8] = 1
        for x in range(7):
            input[x] = 0
        for x in range(8,11):
            input[x] = 0
    if(myFood == 9):
        input[9] = 1
        for x in range(8):
            input[x] = 0
        for x in range(9,11):
            input[x] = 0
    if(myFood == 10):
        input[10] = 1
        for x in range(9):
            input[x] = 0
        for x in range(10,11):
            input[x] = 0
    if(myFood == 11):
        input[11] = 1
        for x in range(10):
            input[x] = 0

    #Same as above, just with enemy food. Increasing negative weight
    if(enemyFood == 0):
        input[12] = 1
        for x in range(12,23):
            input[x] = 0
    if(enemyFood == 1):
        input[13] = 1
        for x in range(11,12):
            input[x] = 0
        for x in range(13,23):
            input[x] = 0
    if(enemyFood == 2):
        input[14] = 1
        for x in range(11,13):
            input[x] = 0
        for x in range(14,23):
            input[x] = 0
    if(enemyFood == 3):
        input[15] = 1
        for x in range(11,14):
            input[x] = 0
        for x in range(15,23):
            input[x] = 0
    if(enemyFood == 4):
        input[16] = 1
        for x in range(11,15):
            input[x] = 0
        for x in range(16,23):
            input[x] = 0
    if(enemyFood == 5):
        input[17] = 1
        for x in range(11,16):
            input[x] = 0
        for x in range(17,23):
            input[x] = 0
    if(enemyFood == 6):
        input[18] = 1
        for x in range(11,17):
            input[x] = 0
        for x in range(18,23):
            input[x] = 0
    if(enemyFood == 7):
        input[19] = 1
        for x in range(11,18):
            input[x] = 0
        for x in range(19,23):
            input[x] = 0
    if(enemyFood == 8):
        input[20] = 1
        for x in range(11,19):
            input[x] = 0
        for x in range(20,23):
            input[x] = 0
    if(enemyFood == 9):
        input[21] = 1
        for x in range(11,20):
            input[x] = 0
        for x in range(21,23):
            input[x] = 0
    if(enemyFood == 10):
        input[22] = 1
        for x in range(11,21):
            input[x] = 0
        for x in range(22,23):
            input[x] = 0
    if(enemyFood == 11):
        input[23] = 1
        for x in range(11,22):
            input[x] = 0

    myWorkers = getAntList(currentState, me,(WORKER,))
    #check to see if you have two or more workers. Should have positive weight
    if(len(myWorkers) >= 2):
        input[24] = 1
    else:
        input[24] = 0

    #Checks to see if you have less than two workers. Negative weight
    if(len(myWorkers) < 2):
        input[25] = 1
    else:
        input[25] = 0

    #checks if worker is carrying food. Positive value
    for worker in myWorkers:
        if (worker.carrying):
            input[26] = 1
        else:
            input[26] = 0



    myQueen = getAntList(currentState, me, (QUEEN,))[0]
    stepsToAnthill = stepsToReach(currentState, myQueen.coords, myInv.getAnthill().coords)
    stepsToTunnel = stepsToReach(currentState, myQueen.coords, myInv.getTunnels()[0].coords)
    if (stepsToAnthill > 2 or stepsToTunnel > 2):
        input[27] = 1
    else:
        input[27] = 0
