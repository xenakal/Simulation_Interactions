import numpy as np
import random
import re
import math
import numpy as np
from my_utils.line import *


def isCorrespondingEstimator(agentID, targetID, targetEstimator):
    return targetEstimator[0] == agentID and targetEstimator[1] == targetID


def is_target_estimator(myList, target_estimator):
    for estimator in myList:
        if estimator == target_estimator:
            return True
    return False


class TargetEstimatorList:
    """
    Class to keep track of multiple TargetEstimator from multiple agents

    Param:
        times         -- number of values kept in memory
        current_time  -- time in the room
        agent_target  -- link between target and agent already created
        estimatorList -- [[agent.id, target.id, [TargetEstimator]], ...]
    """

    def __init__(self, nTime=20, current_time=0):
        self.times = nTime
        self.currentTime = current_time
        self.agent_target = []  # TODO: elle sert vraiment à qqch celle là ?
        self.estimator_list = []  # tableau de taille #agents*#targets

    def update_estimator_list(self, agentID, targetID):
        """Register the target - agent combination in the memory"""
        if not ((agentID, targetID) in self.agent_target):
            self.agent_target.append((agentID, targetID))
            self.estimator_list.append([agentID, targetID, []])

    def add_create_target_estimator(self, time_from_estimation, target_ID, agent_ID, target_xc, target_yc, target_size):
        """ Creates an estimator and adds it to the list if doesn't exist yet. """
        self.update_estimator_list(agent_ID, target_ID)

        for estimatorElem in self.estimator_list:
            if isCorrespondingEstimator(agent_ID, target_ID, estimatorElem):
                newTargetEstimator = TargetEstimator(time_from_estimation, agent_ID, target_ID, target_xc, target_yc,
                                                     target_size)
                if newTargetEstimator not in estimatorElem[2]:
                    estimatorElem[2].append(newTargetEstimator)
            else:
                """create a new estimator either for a new taget or for a new agent"""
                pass

    def add_target_estimator(self, targetEstimator):
        """ Adds the TargetEstimator in argument to the corresponding place in the list. """
        self.update_estimator_list(targetEstimator.agent_ID, targetEstimator.target_ID)

        for estimatorElem in self.estimator_list:
            if isCorrespondingEstimator(targetEstimator.agent_ID, targetEstimator.target_ID, estimatorElem):
                estimatorElem[2].append(targetEstimator)

    def sort_memories(self):
        for element in self.estimator_list:
            element[2].sort()

    def get_agent_target_list(self, target_ID, agent_ID):
        for element in self.estimator_list:
            if element[0] == agent_ID and element[1] == target_ID:
                return element[2]
        return []

    def get_agent_target_stat(self, target_ID, agent_ID):
        for element in self.estimator_list:
            if element[0] == agent_ID and element[1] == target_ID:
                return len(element[2])
        return -1

    def get_estimator_time_t(self, time):
        estimator_list_time_t = []
        for element in self.estimator_list:
            for estimator in element[2]:
                if estimator.timeStamp == time:
                    estimator_list_time_t.append(estimator)
        return estimator_list_time_t

    def get_estimator_time_target_agent(self, time, target_ID, agent_ID):
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

    def set_current_time(self, current_time):
        self.currentTime = current_time

    def set_followedByCam(self, agentID, targetID, agentID_in_charge):
        for element in self.estimator_list:
            if element[0] == agentID and element[1] == targetID:
                element[3][len(element[3] - 1)].followedByTarget = agentID_in_charge
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
            s = s + "Agent : " + str(element[0]) + " Target :" + str(element[1]) + "# memories " + str(
                len(element[2])) + "\n"
        return s


class FusionEstimatorList:
    """
    Class to keep track of multiple TargetEstimators from only one agent.

    Attributes:
        times               -- number of values kept in memory
        current_time        -- time in the room
        target_seen         -- target already seen by the cameras
        room_representation -- [[target.id, [TargetEstimator]], ...]
    """

    def __init__(self, nTime=5, currentTime=0):
        self.times = nTime
        self.currentTime = currentTime
        self.target_seen = []
        self.memories_fusion = []

    def sort(self):
        for element in self.memories_fusion:
            element[1].sort()

    def get_target_list(self, target_ID):
        """ Returns the list of TargetEstimators for the target provided in the argument. """
        for element in self.memories_fusion:
            if element[0] == target_ID:
                return element[1]
        return []

    def get_agent_target_stat(self, target_ID):
        for element in self.memories_fusion:
            if element[0] == target_ID:
                return len(element[1])
        return -1

    def add_target_estimator(self, estimator):
        self.update_estimator_list(estimator.target_ID)

        for element in self.memories_fusion:
            if element[0] == estimator.target_ID:
                if not is_target_estimator(element[1], estimator):
                    element[1].append(estimator)

    def update_estimator_list(self, targetID):
        '''Register the target - agent combination in the memory'''
        if not targetID in self.target_seen:
            self.target_seen.append(targetID)
            self.memories_fusion.append([targetID, []])

    def set_current_time(self, current_time):
        self.currentTime = current_time


class TargetEstimator:
    """
    Class representing a target as viewed by an agent (ie with an estimated position).

    Args:
        timestamp -- time at which the estimation is done.
        agentID   -- ID of the agent who makes the estimation.
        target    -- target on which the estimation is done.

    Args not used yet:
        seenByCam -- maybe should be suppress
        followedByCam -- cam who has the best view on the target for now
    """

    def __init__(self, timeStamp, agentID, targetID, target_xc, target_yc, target_size):
        self.timeStamp = timeStamp
        self.agent_ID = agentID
        self.target_ID = targetID
        self.target_label = "target"
        self.position = [target_xc, target_yc]
        self.target_size = target_size

    def copy_targetEstimator_new_time(self, time, target):
        return TargetEstimator(time, self.agent_ID, target)

    def to_string(self):
        s1 = "#Timestamp #" + str(self.timeStamp) + "\n"
        s2 = "#From #" + str(self.agent_ID) + "\n"
        s3 = "#Target_ID #" + str(self.target_ID) + " #Target_label #" + str(self.target_label) + "\n"
        s4 = "x: " + str(self.position[0]) + " y: " + str(self.position[1]) + "\n"
        s5 = "#Size: " + str(self.target_size) + "\n"
        return str("\n" + s1 + s2 + s3 + s4 + s5 + "\n")

    def parse_string(self, s):
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        attribute = re.split(
            "#Timestamp#|#From#|#Target_ID#|#Target_label#|x:|y:|#Size:", s)
        self.timeStamp = int(attribute[1])
        self.agent_ID = int(attribute[2])
        self.target_ID = int(attribute[3])
        self.target_label = attribute[4]
        self.position = [float(attribute[5]), float(attribute[6])]
        self.target_size = int(attribute[7])

    def __eq__(self, other):
        cdt1 = self.timeStamp == other.timeStamp
        cdt2 = self.agent_ID == other.agent_ID
        cdt3 = self.target_ID == other.target_ID
        return cdt1 and cdt2 and cdt3

    def __lt__(self, other):
        return self.timeStamp < other.timeStamp

    def __gt__(self, other):
        return self.timeStamp > other.timeStamp
