# -*- coding: utf-8 -*-
import numpy
import math
import time
import random


class TargetRepresentation:
    """
                Class TargetRepresentation.

                Description : This class gives a representation of target

                    :param
                        1. (int) id                   -- numeric value to recognize the target easily
                        2. (int) signature            -- numeric value to identify the target
                        3. (int) xc                   -- x value of the center of the targetRepresentation
                        4. (int) yc                   -- y value of the center of the targetRepresentation
                        5. (int) size                 -- radius from the center
                        6. (string) type              -- "fix","target", to make the difference between
                                                          known and unkown target
                        7. ((int),(int),(int)) color  -- color to represent the target on the map,
                                                         if = 0 than random color selected

                    :attibutes
                        1. (int) id                   -- numeric value to recognize the target easily
                        2. (int) xc                   -- center of the targetRepresentation
                        3. (int) yc                   -- center of the targetRepresentation
                        4. (int) size                 -- radius from the center
                        5. (string) type              -- "set_fix","fix","moving","unknown",
                                                         to make the difference between known and unkown target
                        6. ((int),(int),(int)) color  -- color to represent the target on the map, if = 0 than random
                                                         color selected

                    :notes
                        fells free to write some comments.
    """

    def __init__(self, id=-1, x=-1, y=-1, radius=5, type='fix', color=0):
        """ Identification name (id) + number """
        self.id = id
        self.signature = self.signature = int(random.random() * 10000000000000000) + 100  # always higher than 100

        """TargetRepresentation description on the map"""
        """Position and Speeds"""
        self.xc = x
        self.yc = y

        """TargetRepresentation attributes"""
        self.radius = radius
        self.type = type
        self.color = color

        """Default values"""
        if color == 0:
            r = random.randrange(20, 230, 1)
            g = random.randrange(20, 230, 1)
            b = random.randrange(20, 255, 1)
            self.color = (r, g, b)

    def to_string(self):
        """
               :return / modify vector
                      1. (string) s0+s1 -- description of the targetRepresentation

        """

        s0 = "target " + str(self.id) + "\n"
        s1 = "position x: " + str(self.xc) + " y: " + str(self.yc) + "\n"
        return s0 + s1

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id and self.signature == other.signature


class Target(TargetRepresentation):
    """"
           Class Target extend class target representation.

                Description : This class creates fake targets (data) to run the simulation, see class TargetRepresentation.

                    :params
                        1. (int) id                                   -- numeric value to recognize the target easily
                        2. (int) xc                                   -- x value of the center of the targetRepresentation
                        3. (int) yc                                   -- y value of the center of the targetRepresentation
                        4. (int) vx                                   -- x speeds
                        5. (int) vy                                   -- y speeds
                        6. (int) size                                 -- radius from the center
                        7. (string) type                              -- "fix","target", to make the difference between known and unkown target
                        8. ([(int,int),...]) trajectory_position      -- list [(x,y),...] from all the via point that the target should reach
                        9. (string) trajectory_type                   -- "fix","linear" choice for the target's way to moove
                       10. ([[int],...]) t_add                        -- list [[t1],[t2],...] from all the time where the target should appear in the room
                       11. ([[int],...]) t_del                        -- list [[t1],[t2],...] from all the time where the target should disappear in the room

                    :attibutes
                        1. (int) vx                                   -- x speeds
                        2. (int) vy                                   -- y speeds
                        3. (int) vx_max                               -- x speeds max
                        4. (int) vy_max                               -- y speeds max
                        5. ([(int,int),...]) trajectory_position      -- list [(x,y),...] from all the via point that the target should reach
                        6. ([[int,int],...]) all_position             -- list [[x,y],...] from all the position where the target was
                        7. ([[int],...]) t_add                        -- list [[t1],[t2],...] from all the time where the target should appear in the room
                        8. ([[int],...]) t_del                        -- list [[t1],[t2],...] from all the time where the target should disappear in the room
                        9. (string) trajectory_type                   -- "fix","linear" choice for the target's way to moove
                       10. (int) self.number_of_position_reached      -- keep track from how many via points are reached

                    :notes
                        fells free to write some comments.
    """

    def __init__(self, id=-1, x=-1, y=-1, vx=0, vy=0, trajectory_type='fix', trajectory=(0, [(0, 0)]), type='fix',
                 radius=5, t_add=-1, t_del=-1):

        super().__init__(id, x, y, radius, type, 0)

        """Target description on the map"""
        self.vx = vx
        self.vy = vy
        self.vx_max = vx
        self.vy_max = vy

        (n, self.trajectory_position) = trajectory
        self.all_position = []

        """Apparition and disparition times"""
        self.t_add = t_add
        self.t_del = t_del

        """Target attributes"""
        self.trajectory_type = trajectory_type
        self.number_of_position_reached = 0

        """Default values"""
        if type == 'fix':
            self.vx = 0
            self.vy = 0
            self.vx_max = vx
            self.vy_max = vy

        if t_add == -1:
            self.t_add = [0]
            self.t_del = [1000]


        """
        use to thune the potential field method
        self.k_att = 5
        self.k_rep = 500000000
        self.d_rep = tar_size + math.ceil(0.5 * tar_size)

        self.F_att_max = 10
        self.vx_max = 1
        self.vy_max = 1
        """

    """ hash and eq used to have target object as dictionary in camera """
    def save_position(self):
        """
            :params

            :return / modify vector
                1. append the actual position the array all_position

        """
        self.all_position.append([self.xc, self.yc])
