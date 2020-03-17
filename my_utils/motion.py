import math
def limitToValueMax(valueMax, value):
    if value > valueMax:
        return valueMax
    elif value < -valueMax:
        return -valueMax
    else:
        return value

def moveTarget(Target, delta_time, room):
    """
            :param
                1.(Target) target   -- object (Target)
                2.(int) delta_time  -- to compute an artifical displacement with a given velocity
                3. (Room) room:     -- object(Room)

            :return
                1. modify the position of the target (xc,yc)
    """

    type_mvt = Target.trajectory_type
    # easy solution need to be investeagted
    if type_mvt == 'fix':
        pass
    elif type_mvt == 'line':
        Target.xc = Target.xc + math.ceil(Target.vx * delta_time)
        Target.yc = Target.yc + math.ceil(Target.vy * delta_time)
    elif type_mvt == 'linear':
        rectiligneTrajectory(Target, 10, delta_time)
    elif type_mvt == 'potential_field':
        potentialField(Target, delta_time, room)
    else:
        print("planning method not recognize")


def rectiligneTrajectory(Target, dist_min, delta_time):
    """
            :param
                1.(Target) target   --  object, get target trajectory with target.trajectory and to modify its position
                2.(int) delta_time  -- compute an artifical displacement with a given velocity

            :return
                moove the target according to a predifined path, the motion beetwen two position are linear.
                it does not avoid obstacle.
    """

    if Target.type != 'fix':
        (x_goal,y_goal) = Target.trajectory_position[Target.number_of_position_reached]
        '''Updating the postion we want to reach when close enough '''
        if math.fabs(Target.xc - x_goal) <= dist_min and math.fabs(Target.yc - y_goal) <= dist_min and Target.number_of_position_reached < len(Target.trajectory_position)-1:
            Target.number_of_position_reached +=  1

        '''computing the spped to reach the goal'''
        if (Target.xc - x_goal!= 0):
            v_x = -Target.vx_max * (Target.xc - x_goal) / math.fabs((Target.xc - x_goal))
        else:
            v_x = 0

        if (Target.yc - y_goal != 0):
            v_y = -Target.vy_max * (Target.yc - y_goal) / math.fabs((Target.yc - y_goal))
        else:
            v_y = 0

        '''Modifying the position in the target object, always in (int)'''
        Target.xc = Target.xc + math.ceil(v_x * delta_time)
        Target.yc = Target.yc + math.ceil(v_y * delta_time)


"""
        !!! NOT WORKING NEED THE CONSTANT NEED TO BE ADJUSTED!!!


        :param 
        -target:  object (Target), use to choose the target trajectory with target.trajectory and to modify its position
        -delta_time : (Int), to compute an artifical displacement with a given velocity

        :return
        -None

        moove the target according to a predifined path, the motion beetwen two position are not-linear.
        it does avoid obstacle
"""
def potentialField(target, delta_time, myRoom):
    if target.label != 'fix':

        (x_goal, y_goal) = target.trajectory_position[target.number_of_position_reached]
        '''Updating the postion we want to reach when close enough '''
        if math.fabs(target.xc - x_goal) <= dist_min and math.fabs(target.yc - y_goal) <= dist_min and len(
                target.trajectory_position) > 1:
            target.number_of_position_reached += 1
        xgoal = x_goal[0]
        ygoal = y_goal[0]

        F_att_x = -target.k_att * (target.xc - xgoal)
        F_att_y = -target.k_att * (target.yc - ygoal)

        limitToValueMax(target.F_att_max, F_att_x)
        limitToValueMax(target.F_att_max, F_att_y)

        F_rep_x = 0
        F_rep_y = 0

        for target in myRoom.targets:
            if target != target:
                dx = (target.xc - target.xc)
                dy = (target.yc - target.yc)
                d = math.pow(dx * dx + dy * dy, 0.5)

                if d < target.d_rep:
                    # print("target : " + str( target.id))
                    if dx == 0:
                        pass
                    else:
                        F_rep_x = F_rep_x + target.k_rep * ((1 / d) - (1 / target.d_rep)) * (1 / (d * d * d)) * dx
                    if dy == 0:
                        pass
                    else:
                        F_rep_y = F_rep_y + target.k_rep * ((1 / d) - (1 / target.d_rep)) * (1 / (d * d * d)) * dy

                    # print(dx)
                    # print(dy)
                    # print("Frep x : " +str(F_rep_x))
                    # print("Frep y : " +str( F_rep_y))

        Fx = F_att_x + F_rep_x
        Fy = F_att_y + F_rep_y

        target.vx = 0.01 * Fx
        target.vy = 0.01 * Fy
        limitToValueMax(target.vx_max, target.vx)
        limitToValueMax(target.vy_max, target.vy)
        # print("===============")
        target.xc = target.xc + math.ceil(target.vx * delta_time)
        target.yc = target.yc + math.ceil(target.vy * delta_time)
