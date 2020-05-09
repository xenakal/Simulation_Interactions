import random
import re
import time

from src import constants
from src.multi_agent.elements.item import Item, create_item_from_string
from src.my_utils.confidence import evaluate_confidence
from src.my_utils.string_operations import parse_element


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
                        1. (int) id                           -- numeric value to recognize the target easily
                        2. (float) xc - [m]                   -- x value of the targetRepresentation center
                        3. (float) yc - [m]                   -- y value of the targetRepresentation center
                        4. (float) vx - [m/s]                 -- x value of the targetRepresentation speed
                        5. (float) vy - [m/s]                 -- y value of the targetRepresentation speed
                        6. (float) ax - [m/s^2]               -- x value of the targetRepresentation acceleration
                        7. (float) ay - [m/s^2]               -- y value of the targetRepresentation acceleration
                        8. (int) size - [m]                   -- radius from the center
                        9. ((int),(int),(int)) color          -- color to represent the target on the maps,
                                                                  if = None than random color selected

                    :attibutes
                        1. (type) item_type                        -- class type
                        2. (int) id                           -- numeric value to recognize the target easily
                        3. (int) signature                    -- numeric value to identify the target
                        4. (float) xc                         -- x value of the targetRepresentation center
                        5. (float) yc                         -- y value of the targetRepresentation center
                        6. (float) vx                         -- x value of the targetRepresentation speed
                        7. (float) vy                         -- y value of the targetRepresentation speed
                        8. (float) ax                         -- x value of the targetRepresentation acceleration
                        9. (float) ay                         -- y value of the targetRepresentation acceleration
                       10. (flaot) alpha                      -- target orientation, based on vx,vy
                       11. (int) size                         -- radius from the center
                       12. (TargetType) target_type           -- see class TargetType, differentiate target type.
                       13. ([int,int]) variance_on_estimation -- kalman_variance on the estimation, if not used = [-1,-1]
                       14. ([int,int]) confidence             -- confidence on the representation [t-1,t], if not used = [-1,1]
                                                                 confidence btw [constants.CONFIDENCE_MIN_VALUE,constants.CONFIDENCE_MAX_VALUE]
                       15. (int) priority_level               -- priority an agent should give to the representation.
                       16. ((int),(int),(int)) color           -- color to represent the target on the maps,
                                                                  if = None than random color selected

                    :notes
                        1. et 2. et 3. are parameters from Item
    """

    def __init__(self, id=None, xc=None, yc=None, vx=0, vy=0, ax=0, ay=0, radius=None, type=None, color=None):
        """Initialisation"""
        super().__init__(id)

        """Position and Speeds and accelaration"""
        self.xc = xc
        self.yc = yc
        self.vx = vx
        self.vy = vy
        self.ax = ax
        self.ay = ay
        self.alpha = 0

        """TargetRepresentation other attributes"""
        self.radius = radius
        self.target_type = type

        """Attributes used by agent"""
        self.variance_on_estimation = [-1, -1]
        self.confidence = [-1, -1]
        self.priority_level = 0

        """Attributes used for GUI"""
        self.color = color

        "Default values"
        if type == TargetType.SET_FIX:
            self.vx = 0
            self.vy = 0

        if color is None:
            r = random.randrange(20, 230, 1)
            g = random.randrange(20, 230, 1)
            b = random.randrange(20, 255, 1)
            self.color = (r, g, b)

    def evaluate_target_confidence(self, error, delta_time):
        """Method to modify the value of the confidence based on severals parameters, see evaluate confidence"""
        self.confidence[0] = self.confidence[1]
        self.confidence[1] = evaluate_confidence(error, delta_time)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id and self.signature == other.signature


class Target(TargetRepresentation):
    """"
       Class Target extend class target representation.

            Description : This class creates fake targets (data) to run the simulation, see class TargetRepresentation.

                :params
                   10. (TargetMotion) trajectory_type                -- See TargetMotion, multiple way to reach a via point
                   11. ([(int,int),...]) trajectory - [(m,m),...]    -- Tuple in a list containing all the via point (x,y) coordinate
                   12. (int) number_of_position_reached              -- Keeps track of which was the last via point

                   1. (string) trajectory_type                     -- "fix","linear" choice for the target's way
                                                                     to moove
                   20. ([[int],...]) t_add - [s]                    -- list [[t1],[t2],...] from all the time where
                                                                     the target should appear in the room
                   21. ([[int],...]) t_del - [s]                    -- list [[t1],[t2],...] from all the time where
                                                                     the target should disappear in the room
                   12. (int) number_of_time_passed                 -- keeps track of the apparition and disparition time
                   13. (bool) is_on_map                             -- True if the target is on the maps, False otherwise

                :attibutes
                   17. (float) vx_max - [m/time_btw_target_mvt]      -- x speeds max
                   18. (float) vy_max - [m/time_btw_target_mvt]      -- y speeds max

                   19. (TargetMotion) trajectory_type                -- See TargetMotion, multiple way to reach a via point
                   20. ([(int,int),...]) trajectory - [(m,m),...]    -- Tuple in a list containing all the via point (x,y) coordinate
                   21. (int) number_of_position_reached              -- Keeps track of which was the last via point


                    22. ([[float],...]) t_add -                      -- list [[t1],[t2],...] containing all the times at
                                                                         which the target should appear in the room
                    23. ([[float],...]) t_del                        -- list [[t1],[t2],...] containing all the times at
                                                                         which the target should disappear from the room
                    24. (int) number_of_time_passed                  -- keeps track of which was the last t_add/t_del
                    25. (bool) is_on_map                             -- True if the target is on the map

                    25. ([[float,float],...]) all_position            -- list [[x,y],...] containing all the previous
                                         - ([m],[m])                     positions of the target

                :notes
                    attributes 1. to 15. describe in the class TargetRepresentation.
    """

    def __init__(self, id=None, xc=None, yc=None, vx=0, vy=0, ax=0, ay=0, radius=None, type=None, color=None,
                 trajectory_type=None, trajectory=None, t_add=None, t_del=None):
        super().__init__(id, xc, yc, vx, vy, ax, ay, radius, type, color)

        """In function motion,  file motion.py, bound for the speeds"""
        self.vx_max = self.vx
        self.vy_max = self.vy

        """Simulation for a trajectory"""
        self.trajectory_type = trajectory_type
        self.trajectory = trajectory
        self.number_of_position_reached = 0

        """Simulation for a dynamic target apparition/disparition"""
        self.t_add = t_add
        self.t_del = t_del
        self.number_of_time_passed = 0
        self.is_on_the_map = False

        """Save each positon --> draw on the GUI"""
        self.all_position = []

        """Default values"""
        if type == TargetType.SET_FIX:
            self.vx_max = self.vx
            self.vy_max = self.vy

        if t_add == None or t_del == None:
            self.t_add = [0]
            self.t_del = [constants.TIME_STOP]

        if trajectory == None:
            self.trajectory = [(xc, yc)]

    def target_random_for_randomize(self, bound):
        """Method to modify easily the way randomize target is done"""
        return random.uniform(bound[0], bound[1])

    def randomize(self, target_type, r_bound, v_bound, trajectory_number_of_points):
        """
            :description
                fill the attributes with bounded random values

            :param
                1. (TargetType) target_type                    -- see class description
                2. ((min,max)) r_bound                         -- bound the radius
                3. ((min,max)) v_bound                         -- bound the speed
                4. ((min,max)) trajectory_number_of_points     -- number of trajectories

            :return / modify vector
                1. (type) name -- description
                2. (type) name -- description
        """

        """Positions and speeds"""
        self.xc = self.target_random_for_randomize((0, constants.ROOM_DIMENSION_X))
        self.yc = self.target_random_for_randomize((0, constants.ROOM_DIMENSION_Y))
        self.vx_max = self.target_random_for_randomize(v_bound)
        self.vy_max = self.target_random_for_randomize(v_bound)

        """Other attributes"""
        self.type = target_type
        self.radius = self.target_random_for_randomize(r_bound)

        """Trajectory"""
        self.trajectory_type = TargetMotion.LINEAR
        self.trajectory = [(self.xc, self.yc)]
        for n in range(trajectory_number_of_points):
            x = random.uniform(0, constants.ROOM_DIMENSION_X)
            y = random.uniform(0, constants.ROOM_DIMENSION_Y)
            self.trajectory.append((x, y))

        """Time attributes"""
        self.t_add = [0]
        self.t_del = [constants.TIME_STOP]

    def save_position(self):
        """Add the current position to a list"""
        self.all_position.append([self.xc, self.yc])

    def save_target_to_txt(self):
        """Return a string description from the target"""
        s0 = "xc:%0.2f yc:%0.2f vx:%0.2f vy:%0.2f r:%0.2f" % (self.xc, self.yc, self.vx_max, self.vy_max, self.radius)
        s1 = " target_type:%d tj_type:%d" % (self.target_type, 1)
        s2 = " t_add:" + str(self.t_add) + " t_del:" + str(self.t_del)
        s3 = " trajectory:" + str(self.trajectory)
        return s0 + s1 + s2 + s3 + "\n"

    def load_from_save_to_txt(self, s):
        """Load a target from based on a string description s, s is created by the function save_target_to_txt"""

        s = s.replace("\n", "")
        s = s.replace(" ", "")
        attribute = re.split("xc:|yc:|vx:|vy:|r:|target_type:|tj_type:|t_add:|t_del:|trajectory:", s)

        self.xc = float(attribute[1])
        self.yc = float(attribute[2])
        self.vx = float(attribute[3])
        self.vy = float(attribute[4])
        self.vx_max = self.vx * constants.SCALE_TIME
        self.vy_max = self.vy * constants.SCALE_TIME
        self.radius = float(attribute[5])
        self.target_type = float(attribute[6])
        self.trajectory_type = float(attribute[7])
        self.t_add = parse_element(attribute[8])
        self.t_del = parse_element(attribute[9])
        self.trajectory = parse_element(attribute[10])


if __name__ == "__main__":
    target = Target(0,1,2,0,0,0,0,0.3,TargetType.UNKNOWN,None,TargetMotion.LINEAR,[(0,0)],None,None)
    t_start  = time.time()
    '''
    print(target.attributes_to_string())
    print(target.save_target_to_txt())
    target2 = Target()
    target2.load_from_txt(target.save_target_to_txt())
    print(target2.save_target_to_txt())
    '''
    target3 = create_item_from_string(target.attributes_to_string())
    print("%.10f" % (time.time() - t_start))
    #print(target3.save_target_to_txt())
    #print(target3.attributes_to_string())
