# -*- coding: utf-8 -*-
import numpy
import math
import time
import random


class Target:
    def __init__(self, tar_id, tar_x, tar_y, tar_vx, tar_vy, tar_label, tar_size):
        # Label
        self.shape = "round"
        self.id = tar_id
        self.label = tar_label
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

        # size
        self.size = tar_size

    def moveTarget(self, time):
        # easy solution need to be investigated
        self.xc = self.xc + self.vx * time
        self.yc = self.yc + self.vy * time
