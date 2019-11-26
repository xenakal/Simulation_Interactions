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

        #PathPlanning
        self.xgoal = 0
        self.ygoal = 0
        self.k_att = 1
        self.k_rep = 2
        self.d_rep = tar_size + 20
        
        # size
        self.size = tar_size
        

    def moveTarget(self,delta_time,myRoom,type_mvt):
         #easy solution need to be investeagted
         if type_mvt == 'linear':
             self.xc = self.xc + self.vx * delta_time
             self.yc = self.yc + self.vy * delta_time
         if type_mvt =='circular':
             pass
         if type_mvt =='elliptic':
             pass
         if type_mvt == 'path_planning':
             self.pathPlanning(delta_time,myRoom)
            
    
    def pathPlanning(self,delta_time,myRoom):
        F_att_x = -self.k_att*(self.xgoal - self.xc)
        F_att_y = -self.k_att*(self.ygoal - self.yc)
        
        F_rep_x = 0
        F_rep_y = 0
        
        for target in myRoom.targets:
            if(target != self):
                dx = (self.xc-target.xc)
                dy = (self.yc-target.yc)
                d = math.pow(dx*dx+dy*dy,0.5)
                
                if(d < target.d_rep):
                    F_rep_x = F_rep_x + self.k_rep*((1/target.d_rep)-(1/dx))*(1/(dx*dx))
                    F_rep_y = F_rep_y + self.k_rep*((1/target.d_rep)-(1/dy))*(1/(dy*dy))
        
        Fx = -F_att_x + F_rep_x
        Fy = -F_att_y + F_rep_y
        
        if (self.label != 'fix'):
            self.vx = 0.1 * Fx
            self.vy = 0.1 * Fy
            self.xc = math.ceil(self.xc + self.vx * delta_time)
            self.yc = math.ceil(self.yc + self.vy * delta_time)
