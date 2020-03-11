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
        # trajectories
        # trajectories
        self.trajectories = []
        self.traj_num = []

    def init_targets(self, tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size,t_add,t_del):
        for item in tar_x:
            if trajChoice_tar[self.targetNumber] in  self.traj_num:
                index = self.traj_num.index(trajChoice_tar[self.targetNumber])
                self.targets_SIMU.append(Target(self.targetNumber, tar_x[self.targetNumber], tar_y[self.targetNumber],
                                       tar_vx[self.targetNumber], tar_vy[self.targetNumber],tar_traj[self.targetNumber],
                                                self.trajectories[index],tar_label[self.targetNumber]
                                       , tar_size[self.targetNumber],t_add[self.targetNumber],t_del[self.targetNumber]))
            else:
                print("fichier info_room_simu l27 : error while creating target, trajectory number not found")

            self.targetNumber += 1

    def addTargets(self, tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size, t_add, t_del):
        if trajChoice_tar in self.traj_num:
            index = self.traj_num.index(trajChoice_tar)
            self.targets_SIMU.append(Target(self.targetNumber, tar_x,tar_y,tar_vx,tar_vy,tar_traj,
                                            self.trajectories[index], tar_label, tar_size, t_add,t_del))
            self.targetNumber += 1
        else:
            print("fichier info_room_simu l27 : error while creating target, trajectory number not found")

    def init_trajectories(self,all_traj):
        for num_traj in all_traj:
            (num,traj) = num_traj
            self.trajectories.append(num_traj)
            self.traj_num.append(num)