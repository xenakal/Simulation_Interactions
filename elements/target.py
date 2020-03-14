# -*- coding: utf-8 -*-
import numpy
import math
import time
import random



class Target:
    def __init__(self, tar_id=-1, tar_x=-1, tar_y=-1, tar_vx=0, tar_vy=0, tar_traj='fix', trajectory = (0,[(0,0)]),
                 tar_label='fix', tar_size=5,t_add=-1,t_del=-1):
        # Label
        self.id = tar_id
        self.label = tar_label
        self.trajectory = tar_traj

        # time to appear and disappear
        if t_add == -1:
            self.t_add = [0]
            self.t_del = [1000]
        else:
            self.t_add = t_add
            self.t_del = t_del


        # color from the object
        r = random.randrange(20, 230, 1)
        g = random.randrange(20, 230, 1)
        b = random.randrange(20, 255, 1)
        self.color = (r, g, b)
        # Location on the map
        self.xc = tar_x
        self.yc = tar_y

        # Speed
        if tar_label == 'fix':
            self.vx = 0
            self.vy = 0
        else:
            self.vx = tar_vx
            self.vy = tar_vy


        (n,self.trajectory_position) = trajectory
        self.number_of_position_reached = 0
        # size
        self.size = tar_size
        # to rembember its position
        self.all_position = []


        '''use to thune the potential field method'''
        self.k_att = 5
        self.k_rep = 500000000
        self.d_rep = tar_size + math.ceil(0.5 * tar_size)

        self.F_att_max = 10
        self.vx_max = 1
        self.vy_max = 1

    ''' hash and eq used to have target object as dictionary in camera '''

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def save_position(self):
        self.all_position.append([self.xc, self.yc])

