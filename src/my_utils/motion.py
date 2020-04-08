from src.multi_agent.elements.target import *
import math


def limit_to_value_max(value_max, value):
    """
            :param
                1.(int) value_max    -- value that should not be exceed
                2.(int) value       -- actual value

            :return
                1. return a value in the given range bound with value_max
    """

    if value > value_max:
        return value_max
    elif value < -value_max:
        return -value_max
    else:
        return value


def move_Target(Target, delta_time):
    """
            :param
                1.(Target) target   -- object (Target)
                2.(int) delta_time  -- to compute an artifical displacement with a given velocity
                3. (Room) room:     -- object(Room)

            :return
                1. modify the position of the target (xc,yc)
    """
    type_mvt = 1  #int(float(Target.trajectory_type))
    # easy solution need to be investeagted
    if type_mvt == TargetMotion.FIX:
        pass
    elif type_mvt == TargetMotion.LINEAR:
        rectiligne_trajectory(Target, 0.30, delta_time)
    else:
        print("planning method not recognize")


def rectiligne_trajectory(target, dist_min, delta_time):
    """
            :param
                1.(Target) target   --  object, get target trajectory with target.trajectory and to modify its position
                2.(int) delta_time  -- compute an artificial displacement with a given velocity

            :return
                moove the target according to a predifined path, the motion between two position are linear.
                it does not avoid obstacle.
    """
    if  not target.type == TargetType.SET_FIX and len(target.trajectory)>0:
        (x_goal, y_goal) = target.trajectory[target.number_of_position_reached]

        '''Updating the postion we want to reach when close enough '''
        if target.trajectory and math.fabs(target.xc - x_goal) <= dist_min and math.fabs(
                target.yc - y_goal) <= dist_min and target.number_of_position_reached < len(
                target.trajectory) - 1:
            target.number_of_position_reached += 1

        '''computing the speeds to reach the goal'''
        if target.trajectory and math.fabs(x_goal - target.xc) > 0.05:
            v_x = -target.vx_max * (target.xc - x_goal) / math.fabs((target.xc - x_goal))
        else:
            v_x = 0

        if target.trajectory and math.fabs(y_goal - target.yc) > 0.05:
            v_y = -target.vy_max * (target.yc - y_goal) / math.fabs((target.yc - y_goal))
        else:
            v_y = 0


        '''Modifying the position in the target object, always in (int)'''
        target.ax = (v_x - target.vx)
        target.ay = (v_y - target.vy)
        target.vx = v_x
        target.vy = v_y

        target.alpha = math.atan2(v_y,v_x)

        """updating position"""
        target.xc = target.xc + v_x * delta_time
        target.yc = target.yc + v_y * delta_time
