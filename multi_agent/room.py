import numpy
from elements.target import *
from multi_agent.agentCamera import *
from elements.camera import *


"Ici il faut un peu modifier pour pouvoir avec un pièce dynamique avec des objets qui peuvent rentrer et sortir"
class Room:
    def __init__(self):
        # Room attributes
        self.coord = numpy.array([0, 0, 300, 300])  # x y l h
        # target in the room
        self.targets = []
        self.targetNumber = 0
        # camera in the room
        self.cameras = []
        self.camerasNumber = 0
        # agentCam
        self.agentCam = []
        self.agentCamNumber = 0
        # time
        self.time = 0
        
    def createTargets(self, tar_x, tar_y, tar_vx, tar_vy, tar_traj,trajChoice_tar, tar_label, tar_size):
        for _ in tar_x:
            self.targets.append(Target(self.targetNumber, tar_x[self.targetNumber], tar_y[self.targetNumber],
                                       tar_vx[self.targetNumber], tar_vy[self.targetNumber],
                                       tar_traj[self.targetNumber],trajChoice_tar[self.targetNumber],
                                       tar_label[self.targetNumber]
                                       , tar_size[self.targetNumber]))
            self.targetNumber += 1

    def createCameras(self, cam_x, cam_y, cam_alpha, cam_beta, fix):
        for _ in cam_x:
            self.cameras.append(Camera(self.camerasNumber, cam_x[self.camerasNumber],
                                       cam_y[self.camerasNumber], cam_alpha[self.camerasNumber]
                                       , cam_beta[self.camerasNumber], fix[self.camerasNumber]))
            self.camerasNumber += 1

    def createAgentCam(self, cam_x, cam_y, cam_alpha, cam_beta, fix, myRoom):
        for _ in cam_x:
            camera = Camera(self.camerasNumber, cam_x[self.camerasNumber],
                            cam_y[self.camerasNumber], cam_alpha[self.camerasNumber]
                            , cam_beta[self.camerasNumber], fix[self.camerasNumber])
            self.cameras.append(camera)
            self.camerasNumber = self.camerasNumber + 1
        
        for camera in self.cameras:
            self.agentCam.append(AgentCam(self.agentCamNumber, camera, myRoom))
            self.agentCamNumber += 1
