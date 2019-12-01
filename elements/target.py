# -*- coding: utf-8 -*-
import numpy
import math
import time
import random


def limitToValueMax(valueMax, value):
    if value > valueMax:
        return valueMax
    elif value < -valueMax:
        return -valueMax
    else:
        return value


class Target:
    def __init__(self, tar_id=-1, tar_x=-1, tar_y=-1, tar_vx=0, tar_vy=0,tar_traj='fix',tar_trajChoice = 0,tar_label='fix', tar_size = 5):
        # Label
        self.shape = "round"
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
            pass
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

    def moveTarget(self, delta_time, myRoom):
        type_mvt = self.trajectory
        # easy solution need to be investeagted
        if type_mvt == 'fix':
            pass
        if type_mvt == 'line':
            self.xc = self.xc + math.ceil(self.vx * delta_time)
            self.yc = self.yc + math.ceil(self.vy * delta_time)
        elif type_mvt == 'linear':
            self.rectiligneTrajectory(delta_time, myRoom)
        elif type_mvt == 'circular':
            pass
        elif type_mvt == 'elliptic':
            pass
        elif type_mvt == 'potential_field':
            self.potentialField(delta_time, myRoom)
        else:
            print("planning method not recognize")
            
    def rectiligneTrajectory(self, delta_time, myRoom):
        
        if self.label != 'fix':
            
            if math.fabs(self.xc - self.xgoal[0]) <= 10 and math.fabs(self.yc - self.ygoal[0]) <= 10 and len(
                    self.xgoal) > 1:
                del self.xgoal[0]
                del self.ygoal[0]
            
            xgoal = self.xgoal[0]
            ygoal = self.ygoal[0]
                   
            if(self.xc - xgoal != 0):
                v_x = -self.vx_max * (self.xc - xgoal)/math.fabs((self.xc - xgoal))
            else:
                v_x = 0
                
            if(self.yc - ygoal != 0):
                v_y = -self.vy_max* (self.yc - ygoal)/math.fabs((self.yc - ygoal))
            else:
                v_y = 0
            
        
            self.xc = self.xc + math.ceil(v_x * delta_time)
            self.yc = self.yc + math.ceil(v_y * delta_time)
            

    def potentialField(self, delta_time, myRoom):

        if self.label != 'fix':
            if math.fabs(self.xc - self.xgoal[0]) <= 20 and math.fabs(self.yc - self.ygoal[0]) <= 20 and len(
                    self.xgoal) > 1:
                del self.xgoal[0]
                del self.ygoal[0]

            xgoal = self.xgoal[0]
            ygoal = self.ygoal[0]

            F_att_x = -self.k_att * (self.xc - xgoal)
            F_att_y = -self.k_att * (self.yc - ygoal)

            limitToValueMax(self.F_att_max, F_att_x)
            limitToValueMax(self.F_att_max, F_att_y)

            F_rep_x = 0
            F_rep_y = 0

            for target in myRoom.targets:
                if target != self:
                    dx = (self.xc - target.xc)
                    dy = (self.yc - target.yc)
                    d = math.pow(dx * dx + dy * dy, 0.5)

                    if d < target.d_rep:
                        # print("target : " + str( target.id))
                        if dx == 0:
                            pass
                        else:
                            F_rep_x = F_rep_x + self.k_rep * ((1 / d) - (1 / target.d_rep)) * (1 / (d * d * d)) * dx
                        if dy == 0:
                            pass
                        else:
                            F_rep_y = F_rep_y + self.k_rep * ((1 / d) - (1 / target.d_rep)) * (1 / (d * d * d)) * dy

                        # print(dx)
                        # print(dy)
                        # print("Frep x : " +str(F_rep_x))
                        # print("Frep y : " +str( F_rep_y))

            Fx = F_att_x + F_rep_x
            Fy = F_att_y + F_rep_y

            self.vx = 0.01 * Fx
            self.vy = 0.01 * Fy
            limitToValueMax(self.vx_max, self.vx)
            limitToValueMax(self.vy_max, self.vy)
            # print("===============")
            self.xc = self.xc + math.ceil(self.vx * delta_time)
            self.yc = self.yc + math.ceil(self.vy * delta_time)
