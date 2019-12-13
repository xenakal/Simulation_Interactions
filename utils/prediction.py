    '''
    En gros la prédiction doit se faire sur la classe memory
    
    Dans la classe memory il y a deux tableau
    1) self.memory_all_agent = TargetEstimatorList()
        contient toutes les données:
            - photo
            - estimatorTarget recu d'un autre agent 
            
    2)self.memory_agent = FusionEstimatorList()
        C'EST SUR CE VECTEUR QUE DOIT SE FAIRE LA PREDICTION 
        
        c'est un vecteur qui contient pour chaque target une position possible sur la carte.
        Cette position est calculée en fonction des différentes informations disponible dans le tableau 1)
        
        self.memory_agent.room.room_representation est un liste qui se présente sous cette forme
        [[target.id,[liste de estimatorTarget (ceux du target.id pour tous les temps)]] [target.id,[liste de estimatorTarget (ceux du target.id pour tous les temps)] ...]
        
        pour accéder la liste en question il est utile d'utiliser la fonction suivante
        get_target_list(TargetID)
        la liste retourné contient toutes les informations connues sur le target pour les temps allant de 0 au temps actuel
        (réprésentation par des petits points sur la carte
    '''

    def makePredictions(self):
        time = self.currentTime
        for targetInfosObj in self.info_room[-1]:
            target = targetInfosObj.target
            if self.isTargetDetected(time, target.id):
                self.predictedPositions[target] = self.predictedPositions[target] = self.nextPositions(target)


    def nextPositions(self, target):
        prevPos = self.getPrevPositions(target)
        predictedPos = [None] * NUMBER_PREDICTIONS
        #  We have access to the real speeds, but in the real application we won't, therefore we have to approximate
        currPos = [targetID.xc, targetID.yc]

        for i in range(NUMBER_PREDICTIONS):
            #  Estimate next position
            avgSpeed = avgSpeedFunc(prevPos)  # calculate average velocity
            avgDirection = avgDirectionFunc(prevPos)  # calculate average direction
            nextPos = calcNextPos(currPos, avgSpeed, avgDirection)  # estimate next position
            predictedPos[i] = nextPos
            #  Update needed values
            prevPos = prevPos[1:]
            prevPos.append(currPos)  # include new pos for next iteration
            currPos = nextPos

        return predictedPos

    ''' returns the previous positions '''
    def getPrevPositions(self, targetID):
        posList = []
        if len(self.info_room) > NUMBER_PREDICTIONS:
            adapted_info_room = self.info_room[-NUMBER_PREDICTIONS]
        else:  # in case info_room only contains few elements
            adapted_info_room = self.info_room

        # find position in each time recorded
        for infosList in adapted_info_room:
            for info in infosList:
                if targetID == info.targetID:
                    posList.append([target.xc, target.yc])
        return posList


def avgSpeedFunc(positions):
    if len(positions) <= 1:  # one position or less not enough to calculate speed
        return 0
    prevPos = positions[0]
    stepTime = 1  # TODO: see what the actual time increment is
    avgSpeed = 0.0
    for curPos in positions:
        stepDistance = distanceBtwTwoPoint(prevPos[0], prevPos[1], curPos[0], curPos[1])
        avgSpeed += stepDistance / stepTime
        prevPos = curPos

    avgSpeed = avgSpeed / (len(positions) - 1)
    return avgSpeed


# Returns direction as the angle (in degrees) between the horizontal and the line making the direction
def avgDirectionFunc(positions):
    if len(positions) <= 1:  # one position or less not enough to calculate direction
        return 0
    prevPos = positions[0]
    avgDir = 0
    counter = 0
    for curPos in positions[1:]:
        dy = curPos[1] - prevPos[1]
        dx = curPos[0] - prevPos[0]
        stepDirection = math.atan2(float(dy), float(dx))
        avgDir += stepDirection

        prevPos = curPos
        counter += 1

    avgDir = avgDir / counter
    #  print("avgDir " + str(avgDir))
    return avgDir


def calcNextPos(position, speed, direction):
    travelDistance = main.TIMESTEP * 4 * speed
    xPrediction = position[0] + math.cos(direction) * travelDistance
    yPrediction = position[1] + math.sin(direction) * travelDistance  # -: the coordinates are opposite to the cartesian
    return [int(xPrediction), int(yPrediction)]