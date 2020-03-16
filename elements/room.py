import numpy
from elements.target import *
from multi_agent.agent_camera import *
from elements.camera import *
from elements.info_room_simu import *
from multi_agent.agent_user import AgentUser
from multi_agent.room_description import *
import main


class Room:
    def __init__(self):
        # Info just for the simulation, should be in practice replace by video input
        self.info_simu = Info_simu()
        # Room attributes
        self.coord = numpy.array([0, 0, main.WIDTH_ROOM, main.LENGHT_ROOM])  # x y l h
        # target in the room
        self.targets = []
        self.targetNumber = 0
        # camera in the room
        self.cameras = []
        self.camerasNumber = 0
        # Agent User
        self.agentUser = []
        self.agentUserNumber = 100
        # agentCam
        self.agentCams = []
        self.agentCamNumber = 0
        # time
        self.time = 0

    def init_room(self, tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size, t_add, t_del):
        self.info_simu.init_targets(tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size, t_add,
                                    t_del)
        self.targetNumber = self.info_simu.targetNumber

    def init_agentCam(self, cam_x, cam_y, cam_alpha, cam_beta, fix, myRoom):
        for _ in cam_x:
            camera = Camera(myRoom, self.camerasNumber, cam_x[self.camerasNumber],
                            cam_y[self.camerasNumber], cam_alpha[self.camerasNumber]
                            , cam_beta[self.camerasNumber], fix[self.camerasNumber])
            self.cameras.append(camera)
            self.camerasNumber = self.camerasNumber + 1

        for camera in self.cameras:
            self.agentCams.append(AgentCam(self.agentCamNumber, camera))
            self.agentCamNumber += 1

    def init_agentUser(self, number):
        for n in range(number):
            self.agentUser.append(AgentUser(self.agentUserNumber))
            self.agentUserNumber = self.agentUserNumber + 1

    def init_trajectories(self, all_traj):
        self.info_simu.init_trajectories(all_traj)

    def add_del_target_timed(self):
        for target in self.info_simu.targets_SIMU:
            if self.time in target.t_add:
                self.addTarget_alreadyCreated(target)
            elif self.time in target.t_del:
                self.delTargets(target)

    def addTarget_alreadyCreated(self, Target):
        self.targets.append(Target)
        self.targetNumber = self.info_simu.targetNumber

    def addTargets(self, tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size, t_add, t_del):
        self.info_simu.addTargets(tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size, t_add,
                                  t_del)

    def delTargets(self, target):
        index = self.targets.index(target)
        del self.targets[index]

    def addAgentCam(self, cam_x, cam_y, cam_alpha, cam_beta, fix, myRoom):
        camera = Camera(myRoom, self.camerasNumber, cam_x, cam_y, cam_alpha, cam_beta, fix)
        self.cameras.append(camera)
        self.camerasNumber = self.camerasNumber + 1
        self.agentCams.append(AgentCam(self.agentCamNumber, camera))
        self.agentCamNumber += 1

    def getAgentsWithIDs(self, idList, agentType):
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
