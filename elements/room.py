from elements.target import *


class Room:
    def __init__(self):
        # Room attributes
        self.coord = numpy.array([10, 10, 300, 300])  # x y l h
        # target in the room
        self.targets = []
        self.targetNumber = 0
        # camera in the room
        self.cameras = []
        self.camerasNumber = 0

    def createTargets(self, tar_x, tar_y, tar_vx, tar_vy, tar_label, tar_size):
        for n in tar_x:
            self.targets.append(Target(self.targetNumber, tar_x[self.targetNumber], tar_y[self.targetNumber],
                                       tar_vx[self.targetNumber], tar_vy[self.targetNumber],
                                       tar_label[self.targetNumber]
                                       , tar_size[self.targetNumber]))
            self.targetNumber = self.targetNumber + 1

    def removeTarget(self):
        print('removed')

    def createCameras(self, cam_x, cam_y, cam_alpha, cam_beta):
        for n in cam_x:
            self.cameras.append(Camera(self.camerasNumber, cam_x[self.camerasNumber],
                                       cam_y[self.camerasNumber], cam_alpha[self.camerasNumber]
                                       , cam_beta[self.camerasNumber]))
            self.camerasNumber = self.camerasNumber + 1

    def removeCamera(self, cam_x, cam_y, cam_alpha, cam_beta):
        print('removed')
