import numpy
from elements.target import *
from multi_agent.agent_camera import *
from elements.camera import *
from elements.info_room_simu import *
import main

class Room_Description:
    def __init__(self,color):

        self.coord = numpy.array([0, 0, main.WIDTH_ROOM, main.LENGHT_ROOM])  # x y l h
        # target in the room
        self.targets = []
        # agentCam
        self.agentCams = []
        # time
        self.time = 0
        #color
        self.color = color

    def init(self,room):
        for target in room.info_simu.targets_SIMU:
            'commenter le if pour avoir tous les targets dans les représentations de chaque agent'
            if target.label == "fix":
                self.add_targetRepresentation_from_target(target)

        for agent in room.agentCams:
                self.agentCams.append(agent)

    def update_target_based_on_memory(self,fusionList):
        for target_detected_ID in fusionList.target_seen:
            is_in_room_representation = False
            targets_estimator = fusionList.get_target_list(target_detected_ID)
            target_estimator = targets_estimator[len(targets_estimator) - 1]

            for target in self.targets:
                if target.id == target_detected_ID:
                    is_in_room_representation = True
                    target.xc = target_estimator.position[0]
                    target.yc = target_estimator.position[1]
                    break

            if not is_in_room_representation:
               self.add_targetRepresentation(target_estimator.target_ID,target_estimator.position[0],target_estimator.position[1],
                                             target_estimator.target_size,target_estimator.target_label)


    def add_targetRepresentation_from_target(self,target):
        self.add_targetRepresentation(target.id,target.xc,target.yc,target.size,target.label)

    def add_targetRepresentation(self,id,x,y,size,label):
        self.targets.append(Target_representation(id,x,y,size,label,self.color))

    def getAgentsWithIDs(self, idList):
        """ Returns the list of agents with ids in the list provided in the argument. """
        return [agent for agent in self.agentCams if agent.id in idList]

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


class Target_representation():
    def __init__(self, id=-1, x=-1, y=-1,size = 5,label='fix',color = 0):
        self.id = id
        self.xc = x
        self.yc = y
        self.size = size
        self.label = label
        self.color = color

    def to_string(self):
        s0 = "target "+str(self.id)+"\n"
        s1 = "position x: "+str(self.xc)+" y: "+str(self.yc)+"\n"
        return s0 + s1



