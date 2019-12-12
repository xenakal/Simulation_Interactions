import numpy as np
import random
import main
from utils.line import *
import math

NUMBER_PREDICTIONS = 3

class TargetEstimator():
    def __init__(self, timeStamp, target, seenByCam=False, followedByCam=-1, distance=-1,):
        self.timeStamp = timeStamp
        self.target = target
        self.seenByCam = seenByCam
        self.distance = distance
        self.followedByCam = followedByCam
        Erreur = 0
        erreurX = Erreur*random.random()
        erreurY = Erreur * random.random()
        self.position = [target.xc + erreurX , target.yc + erreurY]

    def copyTargetInfo_newTime(self, time, seenByCam):
        return TargetEstimator(time, self.target, seenByCam, self.followedByCam, self.distance)

    def setTimeStamp(self, time):
        self.timeStamp = time

    def setSeenByCam(self, setter):
        self.seenByCam = setter


''' List of TargetEstimator'''
class InformationMemory:
    def __init__(self, nTime=5, currentTime=0):
        self.times = nTime
        self.currentTime = currentTime
        self.info_room = []  #  [[TargetInfo],[TargetInfo]...]
        self.predictedPositions = dict()

    def get_Info_T(self, infoTime):
        for info in self.info_room:
            if len(info)>0:
                 if info[0].timeStamp == infoTime:
                    return info
            else:
                return info
        return []

    def addNewTime(self, time):
        self.currentTime = time
        n = len(self.info_room)
        timeTab = []
        if n > 0:
            for element in self.info_room[n - 1]:
                timeTab.append(element.copyTargetInfo_newTime(time, False))
        if n > self.times - 1:
            del self.info_room[0]
        self.info_room.append(timeTab)

    def addTarget(self, infoTime, target):
        infos = self.get_Info_T(infoTime)
        for element in infos:
            if element.target.id == target.id:
                return False  # if already in the list
        infos.append(TargetEstimator(infoTime, target))
        return True  # otherwise add it

    def addTargetFromID(self, infoTime, targetID, myRoom):
         for target in myRoom.targets:
             if (str(target.id) == str(targetID)):
                    return self.addTarget(infoTime, target)
         return False

    def updateTarget(self, infoTime, target, camInCharge, camera, distance):
        for info in self.get_Info_T(infoTime):
            if (info.target.id == target.id):
                info.seenByCam = camera
                info.distance = distance
                info.followedByCam = camInCharge
                break

    def setSeenByCam(self, infoTime, target, setter):
        for info in self.get_Info_T(infoTime):
            if info.target.id == target.id:
                info.setSeenByCam(True)
                return True
        return False

    def setfollowedByCam(self, infoTime, targetID, agentID):
        for info in self.get_Info_T(infoTime):
            if str(info.target.id) == str(targetID):
                info.followedByCam = agentID
                return True
        return False

    def isTargetDetected(self, infoTime, targetID):
        for info in self.get_Info_T(infoTime):
            if info.target.id == targetID:
                return info.seenByCam
        return False

    def getCamInCharge(self, infoTime, target):
        for info in self.get_Info_T(infoTime):
            if info.target.id == target.id:
                return info.followedByCam

    def memoryToString(self):
        s = "Memory \n"
        for timeStamp in self.info_room:
            for info in timeStamp:
                s1 = "time : " + str(info.timeStamp) + " target " + str(info.target.id)
                s2 = " seen : " + str(info.seenByCam) + " lock : " + str(info.followedByCam) + "\n"
                s = s + s1 + s2

        return s

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
        currPos = [target.xc, target.yc]

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
    def getPrevPositions(self, target):
        posList = []
        if len(self.info_room) > NUMBER_PREDICTIONS:
            adapted_info_room = self.info_room[-NUMBER_PREDICTIONS]
        else:  # in case info_room only contains few elements
            adapted_info_room = self.info_room

        # find position in each time recorded
        for infosList in adapted_info_room:
            for info in infosList:
                if target == info.target:
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

