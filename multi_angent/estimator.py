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

    def init_estimator_list(self, room):
        tab = []
        for agent in room.agentCam:
            for target in room.targets:
                tab.append([agent.id, target.id, []])
        self.estimator_list = tab

    def add_create_target_estimator(self, room, time_from_estimation, target_ID, agent_ID, seenByCam):
        for element in self.estimator_list:
            if element[0] == agent_ID and element[1] == target_ID:
                for target in room.targets:
                    if str(target.id) == str(target_ID):
                        estimator = TargetEstimator(time_from_estimation, agent_ID, target, seenByCam)
                        if not self.is_target_estimator(element[2], estimator):
                            element[2].append(estimator)

    def add_target_estimator(self, estimator):
        for element in self.estimator_list:
            if element[0] == estimator.agent_ID and element[1] == estimator.target_ID:
                if not self.is_target_estimator(element[2], estimator):
                    element[2].append(estimator)

    def is_target_estimator(self, myList, target_estimator):
        for estimator in myList:
            if estimator == target_estimator:
                return True
        return False

    def sort_memories(self):
        for element in self.estimator_list:
            element[2].sort()

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

    def set_current_time(self,current_time):
        self.currentTime = current_time

    def set_followedByCam(self, agentID, targetID, agentID_in_charge):
        for element in self.estimator_list:
            if element[0] == agentID and element[1] == targetID:
                element[3][len(element[3]-1)].followedByTarget = agentID_in_charge
                return True
        return False

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

    def sort(self):
        for element in self.room_representation:
            element[1].sort()

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

    def set_current_time(self,current_time):
        self.currentTime = current_time

#    def getCamInCharge(self, infoTime, targetID):
#      for info in self.get_Info_T(infoTime):
#            if info.target_ID == targetID:
#                return info.followedByCam

    def isTargetDetected(self, infoTime, targetID):
        for info in self.get_Info_T(infoTime):
            if info.target_ID == targetID:
                return info.seenByCam
        return False

