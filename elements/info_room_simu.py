import numpy
from elements.target import *
from multi_agent.agent_camera import *

class Info_simu:
    def __init__(self):
        # Room attributes
        self.coord_SIMU = numpy.array([0, 0, 300, 300])  # x y l h
        # target in the room
        self.targets_SIMU = []
        self.targetNumber = 0

    def init_targets(self, tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size,t_add,t_del):
        for _ in tar_x:
            self.targets_SIMU.append(Target(self.targetNumber, tar_x[self.targetNumber], tar_y[self.targetNumber],
                                       tar_vx[self.targetNumber], tar_vy[self.targetNumber],
                                       tar_traj[self.targetNumber], trajChoice_tar[self.targetNumber],
                                       tar_label[self.targetNumber]
                                       , tar_size[self.targetNumber],t_add[self.targetNumber],t_del[self.targetNumber]))
            self.targetNumber += 1

