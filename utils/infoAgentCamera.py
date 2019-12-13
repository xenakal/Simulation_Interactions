import numpy as np
import random
import re
import main
from utils.line import *
import math

NUMBER_PREDICTIONS = 3
class TargetEstimator:
    def __init__(self, timeStamp, agentID,target, seenByCam=False, followedByCam=-1):
        self.timeStamp = timeStamp
        self.agent_ID = agentID

        self.target_ID = target.id
        self.target_label = target.label
        erreur = 5
        erreurX = random.randrange(-erreur,erreur,1)
        erreurY = random.randrange(-erreur,erreur,1)
        self.position = [target.xc + erreurX, target.yc + erreurY]

        self.seenByCam = seenByCam
        self.followedByCam = followedByCam

        self.estimator = False


    def copyTargetInfo_newTime(self, time,target, seenByCam):
        return TargetEstimator(time,self.agent_ID, target, seenByCam, self.followedByCam)

    def setTimeStamp(self, time):
        self.timeStamp = time

    def setSeenByCam(self, setter):
        self.seenByCam = setter

    def to_string(self):
        s1 = "#Timestamp #"+str(self.timeStamp)+"\n"
        s2 = "#From #" + str(self.agent_ID) +"\n"
        s3 = "#Target_ID #" + str(self.target_ID) + " #Target_label #" + str(self.target_label)+"\n"
        s4 = "x: "+str(self.position[0]) + " y: "+str(self.position[1]) +"\n"
        s5 = "Seen by the agent: "+str(self.seenByCam) +" followed by agent: " +str(self.followedByCam)+"\n"
        s6 = "Estimation: "+str(self.estimator)
        return str("\n"+s1+s2+s3+s4+s5+s6+"\n")

    def parse_string(self,s):
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        attribute = re.split("#Timestamp#|#From#|#Target_ID#|#Target_label#|x:|y:|Seenbytheagent:|followedbyagent:|Estimation:", s)
        self.timeStamp = int(attribute[1])
        self.agent_ID = int(attribute[2])
        self.target_ID = int(attribute[3])
        self.target_label = attribute[4]
        self.position =  [float(attribute[5]),float(attribute[6])]
        self.seenByCam = bool(attribute[7]=="True")
        self.followedByCam = int(attribute[8])
        self.estimator = bool(attribute[9]=="True")

    def __eq__(self, other):
        cdt1 = self.timeStamp == other.timeStamp
        cdt2 = self.agent_ID == other.agent_ID
        cdt3 = self.target_ID == other.target_ID
        return cdt1 and cdt2 and cdt3

    def __lt__(self, other):
        return self.timeStamp < other.timeStamp

    def __gt__(self, other):
        return self.timeStamp > other.timeStamp
''' List of TargetEstimator'''
class TargetEstimatorList:
    def __init__(self, nTime=20, current_time=0):
        self.times = nTime
        self.currentTime = current_time
        self.estimator_list = []

    def set_current_time(self,current_time):
        self.currentTime = current_time

    def sort_memories(self):
        for element in self.estimator_list:
            element[2].sort()

    def init_estimator_list(self, room):
        tab = []
        for agent in room.agentCam:
            for target in room.targets:
                tab.append([agent.id, target.id,[]])
        self.estimator_list = tab

    def get_agent_target_list(self,target_ID,agent_ID):
        for element in self.estimator_list:
            if element[0] == agent_ID and element[1] == target_ID:
                return element[2]
        return []

    def get_agent_target_stat(self,target_ID,agent_ID):
        for element in self.estimator_list:
            if element[0] == agent_ID and element[1] == target_ID:
                return len(element[2])
        return -1

    def add_create_target_estimator(self,room,time_from_estimation,target_ID,agent_ID,seenByCam):
        for element in self.estimator_list:
            if element[0] == agent_ID and element[1] == target_ID:
                for target in room.targets:
                    if str(target.id) == str(target_ID):
                        estimator = TargetEstimator(time_from_estimation, agent_ID, target, seenByCam)
                        if not self.is_target_estimator(element[2], estimator):
                            element[2].append(estimator)

    def add_target_estimator(self,estimator):
        for element in self.estimator_list:
            if element[0] == estimator.agent_ID and element[1] ==estimator.target_ID:
                if not self.is_target_estimator(element[2], estimator):
                    element[2].append(estimator)

    def is_target_estimator(self,myList,target_estimator):
        for estimator in myList:
            if estimator == target_estimator:
                return True
        return False

    def get_estimator_time_t(self,time):
        estimator_list_time_t = []
        for element in self.estimator_list:
            for estimator in element[2]:
                if estimator.timeStamp == time:
                    estimator_list_time_t.append(estimator)
        return estimator_list_time_t

    def get_estimator_time_target_agent(self,time,target_ID,agent_ID):
        estimator_search = []
        cdt0 = cdt1 = cdt2 = True
        for element in self.estimator_list:
            if target_ID != -1:
                cdt0 = element[0] == agent_ID
            if agent_ID != -1:
                cdt1 = element[1] == target_ID

            for estimator in element[2]:
                if time != -1:
                    cdt2 = estimator.timeStamp == time
                if cdt0 and cdt1 and cdt2:
                    estimator_search.append(estimator)
        return estimator_search

    def to_string(self):
        s = "Memory \n"
        for element in self.estimator_list:
            for estimator in element[2]:
                s = s + estimator.to_string()
        return s

    def statistic_to_string(self):
        s = "Memory " + str(self.currentTime) + "\n"
        for element in self.estimator_list:
                s = s + "Agent : " + str(element[0]) + " Target :" + str(element[1]) + "# memories " + str(len(element[2])) + "\n"
        return s

class FusionEstimatorList:
    def __init__(self, nTime=5, currentTime=0):
        self.times = nTime
        self.currentTime = currentTime
        self.room_representation = []  #  [[TargetInfo],[TargetInfo]...]

    def init_estimator_list(self, room):
        tab = []
        for target in room.targets:
                tab.append([target.id,[]])
        self.room_representation = tab

    def get_target_list(self, target_ID):
        for element in self.room_representation:
            if element[0] == target_ID:
                return element[1]
        return []

    def get_agent_target_stat(self, target_ID, agent_ID):
        for element in self.room_representation:
            if element[0] == target_ID:
                return len(element[1])
        return -1

    def add_target_estimator(self, estimator):
        for element in self.room_representation:
            if element[0] == estimator.target_ID:
                if not self.is_target_estimator(element[1], estimator):
                    element[1].append(estimator)

    def is_target_estimator(self, myList, target_estimator):
        for estimator in myList:
            if estimator == target_estimator:
                return True
        return False




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
    def addNewTime(self, time,room):
        self.currentTime = time
        n = len(self.info_room)
        timeTab = []
        if n > 0:
            for element in self.info_room[n - 1]:
                for target in room.targets:
                    if target.id == element.target_ID:
                        timeTab.append(element.copyTargetInfo_newTime(time,target, False))
        if n > self.times - 1:
            del self.info_room[0]
        self.info_room.append(timeTab)
    def addTargetEstimator(self,infoTime,agentID, target):
        infos = self.get_Info_T(infoTime)
        for element in infos:
            if element.target_ID == target.id:
                return False  # if already in the list
        infos.append(TargetEstimator(infoTime,agentID,target))
        return True  # otherwise add it
    def addTargetEstimatorFromID(self, infoTime,agentID, targetID, myRoom):
         for target in myRoom.targets:
             if str(target.id) == str(targetID):
                    return self.addTargetEstimator(infoTime,agentID,target)
         return False
    def updateTarget(self, infoTime, targetID, camInCharge, camera, distance):
        for info in self.get_Info_T(infoTime):
            if info.targetID == targetID:
                info.seenByCam = camera
                info.distance = distance
                info.followedByCam = camInCharge
                break
    def setSeenByCam(self, infoTime, targetID, setter):
        for info in self.get_Info_T(infoTime):
            if info.target_ID == targetID:
                info.setSeenByCam(True)
                return True
        return False

    def setfollowedByCam(self, infoTime, targetID, agentID):
        for info in self.get_Info_T(infoTime):
            if str(info.target_ID) == str(targetID):
                info.followedByCam = agentID
                return True
        return False

    def isTargetDetected(self, infoTime, targetID):
        for info in self.get_Info_T(infoTime):
            if info.target_ID == targetID:
                return info.seenByCam
        return False

    def getCamInCharge(self, infoTime, targetID):
        for info in self.get_Info_T(infoTime):
            if info.target_ID == targetID:
                return info.followedByCam

    def memoryToString(self):
        s = "Memory \n"
        for timeStamp in self.info_room:
            for info in timeStamp:
                s = s + info.to_string()
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
