me = currentState.whoseTurn
    	myInv = currentState.inventories[me]
    	#myInv = getCurrPlayerInventory(currentState)
    	foodScore = 0.0
    	distanceScore = 0.0
    	foodScore = myInv.foodCount/10.0
    	foods = getConstrList(currentState,None, (FOOD,))
        if myInv.getTunnels() != None:
            tunnel = myInv.getTunnels()[0].coords
    	hill = myInv.getAnthill().coords
    	minFoodDistance = 25.0
    	distance = [25,25]
    	numWorkers = len(getAntList(currentState, me, (WORKER,)))
    	currScore = 0.0;
    	workerScoreSum = 0.0
        queenScore = 0
        # makes sure the queen moves away from everything
        for myWorker in getAntList(currentState, me, (QUEEN,)):

            distance[0] = stepsToReach(currentState, tunnel, myWorker.coords)
            distance[1] = stepsToReach(currentState, hill, myWorker.coords)
            averageDistance = (distance[0] + distance[1])/2
            queenScore = 1/(averageDistance+1)


    	#if you have workers then check to see ifyou move them in the right direction
        if numWorkers > 0:
            for myWorker in getAntList(currentState, me, (WORKER,)):
                if(myWorker.carrying):
                    distance[0] = stepsToReach(currentState, tunnel, myWorker.coords)
                    distance[1] = stepsToReach(currentState, hill, myWorker.coords)
                else:
                    distance[0]  = stepsToReach(currentState, myWorker.coords, foods[0].coords)
                    distance[1]  = stepsToReach(currentState, myWorker.coords, foods[1].coords)

            minDistance = min(distance)
			#used for scoring/weighing the "goodness" of worker positions
            currScore = (1.0/(minDistance+1.0))*.5
            if myWorker.carrying:
                currScore+=.5
            workerScoreSum += currScore
            distanceScore = workerScoreSum/numWorkers
        score = (foodScore*.94)+(distanceScore*.04)+(queenScore*.2)

        #add a random small number to the score to help make no equal scores
        if score<1-self.arbitrarySmall:
            score += random.uniform(0,self.arbitrarySmall)
        return score
