import numpy

from multi_agent.agent_camera import *
from elements.camera import *
from elements.info_room_simu import *
from elements.target import TargetRepresentation
import main

class Room_Description:
    def __init__(self,color):

        self.coord = numpy.array([0, 0, main.WIDTH_ROOM, main.LENGHT_ROOM])  # x y l h
        # target in the room
        self.targets = []
        # agentCam
        self.agentCams = []
        # agentUser
        self.agentUser = []
        # time
        self.time = 0
        #color
        self.color = color

    def init(self,room):
        for target in room.info_simu.targets_SIMU:
            'commenter le if pour avoir tous les targets dans les représentations de chaque agent'
            if target.type == "fix":
                self.add_targetRepresentation_from_target(target)

        for agent in room.agentCams:
                self.agentCams.append(agent)

        for agent in room.agentUser:
                self.agentUser.append(agent)

    def update_target_based_on_memory(self,fusionList):
        for target_detected_ID in fusionList.Target_already_discovered_list:
            is_in_room_representation = False
            targets_estimator = fusionList.get_Target_list(target_detected_ID)
            target_estimator = targets_estimator[len(targets_estimator) - 1]

            for target in self.targets:
                if target.id == target_detected_ID:
                    is_in_room_representation = True
                    target.xc = target_estimator.target_position[0]
                    target.yc = target_estimator.target_position[1]
                    break

            if not is_in_room_representation:
               self.add_targetRepresentation(target_estimator.target_id,target_estimator.target_position[0],target_estimator.target_position[1],
                                             target_estimator.target_size,target_estimator.target_label)


    def add_targetRepresentation_from_target(self,target):
        self.add_targetRepresentation(target.id,target.xc,target.yc,target.size,target.type)

    def add_targetRepresentation(self,id,x,y,size,label):
        self.targets.append(TargetRepresentation(id,x,y,size,label,self.color))

    def getAgentsWithIDs(self,idList,agentType):
        """ Returns the list of agents with ids in the list provided in the argument. """
        if agentType == "agentCam":
            return [agent for agent in self.agentCams if agent.id in idList]
        elif agentType == "agentUser":
            return [agent for agent in self.agentUser if agent.id in idList]

    def getTargetsWithIDs(self, targetList):
        """ Returns the list of targets with ids in the list provided in the argument. """
        return [target for target in self.targets if target.id in targetList]

    def getTargetbyID(self, targetID):
        for target in self.targets:
            if target.id == targetID:
                return target
        return None

    def getAgentbyID(self, agentID):
        for agent in self.agentCams:
            if agent.id == agentID:
                return agent
        return None





