# -*- coding: utf-8 -*-
import numpy
import math
import time
import random

class Target:
    def __init__(self, tar_id=-1, tar_x=-1, tar_y=-1, tar_vx=0, tar_vy=0, tar_traj='fix', tar_trajChoice=0,
                 tar_label='fix', tar_size=5):
        # Label
        self.id = tar_id
        self.label = tar_label
        self.trajectory = tar_traj
        # color from the object
        r = random.randrange(20, 230, 1)
        g = random.randrange(20, 230, 1)
        b = random.randrange(20, 255, 1)
        self.color = (r, g, b)
        # Location on the map
        self.xc = tar_x
        self.yc = tar_y
        # Speeds
        if tar_label == 'fix':
            self.vx = 0
            self.vy = 0
        else:
            self.vx = tar_vx
            self.vy = tar_vy
        # PathPlanning
        if tar_trajChoice == 0:
            self.xgoal = [30, 250, 20]
            self.ygoal = [300, 30, 20]
        elif tar_trajChoice == 1:
            self.xgoal = [200, 200, 20]
            self.ygoal = [100, 180, 200]
        else:
            print("Trajectory choice not recognnize !")

        self.k_att = 5
        self.k_rep = 500000000
        self.d_rep = tar_size + math.ceil(0.5 * tar_size)

        self.F_att_max = 10
        self.vx_max = 5
        self.vy_max = 5
        # size
        self.size = tar_size

    ''' hash and eq used to have target object as dictionary in camera '''

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


