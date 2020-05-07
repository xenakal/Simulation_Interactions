# -*- coding: utf-8 -*-
import random
import re
import math
from src import constants
from src.multi_agent.elements.item import Item, evaluate_confidence
from src.my_utils.constant_class import ConfidenceFunction
from src.my_utils.my_math.line import Line


class TargetMotion:
    FIX = 0
    LINEAR = 1

class TargetType:
    SET_FIX = 0
    UNKNOWN = 2
    FIX = 1
    MOVING = 3


class TargetRepresentation(Item):
    """
                Class TargetRepresentation.

                Description : This class gives a representation of target

                    :param
                        1. (int) id                   -- numeric value to recognize the target easily
                        2. (int) signature            -- numeric value to identify the target
                        3. (int) xc                   -- x value of the center of the targetRepresentation
                        4. (int) yc                   -- y value of the center of the targetRepresentation
                        5. (int) size                 -- radius from the center
                        6. (TargetType) type          -- see class above, to make the difference
                                                          between known and unkown target
                        7. ((int),(int),(int)) color  -- color to represent the target on the maps,
                                                         if = 0 than random color selected

                    :attibutes
                        1. (int) id                   -- numeric value to recognize the target easily
                        2. (int) xc                   -- center of the targetRepresentation
                        3. (int) yc                   -- center of the targetRepresentation
                        4. (int) size                 -- radius from the center
                        5. (TargetType) type              -- TargetType see class,
                                                         to make the difference between known and unknown target
                        6. ((int),(int),(int)) color  -- color to represent the target on the maps, if = 0 than random
                                                         color selected

                    :notes
                        fells free to write some comments.
    """

    def __init__(self, id=None, x=None, y=None, vx=0, vy=0, ax=0, ay=0, radius=None, type=None, color=None):
        """Initialisation"""

        " Identification name (id) + number "
        super().__init__(id, int(random.random() * 10000000000000000) + 100)

        "TargetRepresentation description on the maps"
        "Position and Speeds"""
        self.xc = x
        self.yc = y
        self.vx = vx
        self.vy = vy
        self.ax = ax
        self.ay = ay
        self.alpha = 0

        "TargetRepresentation attributes"
        self.radius = radius
        self.type = type
        self.color = color
        self.variance_on_estimation = [0,0]
        self.confidence_pos = [-1,-1]

        self.priority_level = 0

        "Default values"
        if color is None:
            r = random.randrange(20, 230, 1)
            g = random.randrange(20, 230, 1)
            b = random.randrange(20, 255, 1)
            self.color = (r, g, b)


    def evaluate_target_confidence(self, error, delta_time):
        """Method to modify the value of the confidence based on severals parameters"""
        self.confidence_pos[0] = self.confidence_pos[1]
        self.confidence_pos[1] =  evaluate_confidence(error,delta_time)


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
                    1. (float) id                                   -- numerical value to recognize the target easily
                    2. (float) xc - [m]                             -- x value of the center of the
                                                                    targetRepresentation
                    3. (float) yc - [m]                             -- y value of the center of the
                                                                    targetRepresentation
                    4. (float) vx - [m/s]                           -- x speeds
                    5. (float) vy - [m/s]                           -- y speeds
                    6. (float) size - [m]                           -- radius from the center
                    7. (TargetType) type                            --  see class above, to make
                                                                      the difference between known and unkown target
                    8. ([(int,int),...]) trajectory_position        -- list [(x,y),...] from all the via point
                                        - ([m],[m])
                                                                     that the target should reach
                    9. (string) trajectory_type                     -- "fix","linear" choice for the target's way
                                                                     to moove
                   10. ([[int],...]) t_add - [s]                    -- list [[t1],[t2],...] from all the time where
                                                                     the target should appear in the room
                   11. ([[int],...]) t_del - [s]                    -- list [[t1],[t2],...] from all the time where
                                                                     the target should disappear in the room
                   12. (int) number_of_time_pa ssed                 -- keeps track of the apparition and disparition time
                   13. (bool) is_on_map                             -- True if the target is on the maps, False otherwise

                :attibutes
                    1. (float) vx - [m/time_btw_target_mvt]           -- x speeds
                    2. (float) vy - [m/time_btw_target_mvt]           -- y speeds
                    3. (float) vx_max - [m/time_btw_target_mvt]       -- x speeds max
                    4. (float) vy_max - [m/time_btw_target_mvt]       -- y speeds max
                    5. ([(float,float),...]) trajectory_position      -- list [(x,y),...] containing all the via points
                                                                        that the target should reach
                    6. ([[float,float],...]) all_position             -- list [[x,y],...] containing all the previous
                                         - ([m],[m])                     positions of the target
                    7. ([[float],...]) t_add -                        -- list [[t1],[t2],...] containing all the times at
                                                                         which the target should appear in the room
                    8. ([[float],...]) t_del                          -- list [[t1],[t2],...] containing all the times at
                                                                         which the target should disappear from the room
                    9. (string) traject  ory_type                     -- "fix","linear" choice for the target's way
                                                                          to move
                   10. (int) self.number_of_position_reached          -- keep track from how many via points are reached

                :notes
                    time_btw_target_mvt [s], see constants file
    """

    def __init__(self, id=None, x=None,y=None,trajectory_type=None,trajectory= None,type=None,
                 radius=5, t_add=None, t_del=None):
        # Initialisation
        super().__init__(id, x, y, radius, type, None)

        # Target description on the maps
        """!! Attention you responsability to get coherent speed and acceleration"""
        self.vx_max = self.vx
        self.vy_max = self.vy

        self.trajectory = trajectory
        self.all_position = []

        # Apparition and disparition times
        self.t_add = t_add
        self.t_del = t_del
        self.number_of_time_passed = 0
        self.is_on_the_map = False

        # Target attributes
        self.trajectory_type = trajectory_type
        self.number_of_position_reached = 0

        # Default values
        if type == TargetType.SET_FIX:
            self.vx = 0
            self.vy = 0
            self.vx_max = self.vx
            self.vy_max = self.vy

        if t_add == None or t_del == None :
           self.t_add = [0]
           self.t_del = [1000]

        if trajectory == None:
            self.trajectory = [(x, y)]

    def my_rand(self,bound):
        return random.uniform(bound[0],bound[1])

    def randomize(self,target_type,r_bound,v_bound,trajectory_number_of_points):
        self.type = target_type
        self.xc = self.my_rand((0, constants.ROOM_DIMENSION_X))
        self.yc = self.my_rand((0, constants.ROOM_DIMENSION_Y))
        self.radius = self.my_rand(r_bound)
        self.vx_max = self.my_rand(v_bound)
        self.vy_max = self.my_rand(v_bound)

        #TODO voir si on veut changer mais on bouge toujours de la même manière
        self.trajectory_type = TargetMotion.LINEAR
        self.trajectory = [(self.xc, self.yc)]
        for n in range(trajectory_number_of_points):
            x = random.uniform(0, constants.ROOM_DIMENSION_X)
            y = random.uniform(0, constants.ROOM_DIMENSION_Y)
            self.trajectory.append((x,y))

        self.t_add = [0]
        self.t_del = [1000]

    def save_position(self):
        """
            :params

            :return / modify vector
                1. append the actual position the array all_position

        """
        self.all_position.append([self.xc, self.yc])

    def save_target_to_txt(self):
        s0 = "x:%0.2f y:%0.2f vx:%0.2f vy:%0.2f r:%0.2f"%(self.xc,self.yc,self.vx_max,self.vy_max,self.radius)
        s1 = " target_type:%d tj_type:%d"%(self.type,1)
        s2 =" t_add:"+str(self.t_add)+" t_del:"+str(self.t_del)
        s3 =" trajectory:"+str(self.trajectory)
        return s0 + s1 + s2 + s3 + "\n"

    def load_from_txt(self,s):
        s = s.replace("\n", "")
        s = s.replace(" ", "")
        attribute = re.split("x:|y:|vx:|vy:|r:|target_type:|tj_type:|t_add:|t_del:|trajectory:", s)

        self.xc = float(attribute[1])
        self.yc = float(attribute[2])
        self.vx = float(attribute[3])
        self.vy = float(attribute[4])
        self.vx_max = self.vx * constants.SCALE_TIME
        self.vy_max = self.vy * constants.SCALE_TIME
        self.radius = float(attribute[5])
        self.type = float(attribute[6])
        self.trajectory_type = float(attribute[7])
        self.t_add = self.load_tadd_tdel(attribute[8])
        self.t_del = self.load_tadd_tdel(attribute[9])
        self.trajectory =self.load_trajcetory(attribute[10])

    def load_tadd_tdel(self, s):
        list = []
        s = s[1:-1]
        all_times = re.split(",",s)
        for time in all_times:
            list.append(float(time))
        return list

    def load_trajcetory(self,s):
        list = []
        s = s[2:-2]
        if not s == "":
            all_trajectories = re.split("\),\(",s)
            for trajectory in all_trajectories:
                xy = re.split(",",trajectory)
                if not xy == "":
                    list.append((float(xy[0]),float(xy[1])))
        return list
