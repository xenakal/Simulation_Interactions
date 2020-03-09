import numpy
from elements.target import *
from multi_agent.agent_camera import *
from elements.camera import *
from elements.info_room_simu import *
import main

class Room_Description:
    def __init__(self):
        # Room attributes
        self.coord = numpy.array([0, 0, main.WIDTH_ROOM, main.LENGHT_ROOM])  # x y l h
        # target in the room
        self.targets = []
        self.targetNumber = 0
        # agentCam
        self.agentCams = []
        self.agentCamNumber = 0
        # time
        self.time = 0

    def init(self,room):
        for target in room.info_simu.targets_SIMU:
            'commenter le if pour avoir tous les targets dans les représentations de chaque agent'
            #if target.label == "fix":
            self.targets.append(target)

        for agent in room.agentCams:
                self.agentCams.append(agent)

    def addTargets(self, tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size, t_add, t_del):
        self.targets.append(
            Target(self.targetNumber, tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size,
                   t_add, t_del))
        self.targetNumber += 1

    def delTargets(self, target):
        index = self.targets.index(target)
        del self.targets[index]

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



