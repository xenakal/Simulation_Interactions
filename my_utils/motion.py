import math


def limitToValueMax(valueMax, value):
    if value > valueMax:
        return valueMax
    elif value < -valueMax:
        return -valueMax
    else:
        return value


def moveTarget(target, delta_time, myRoom):
    type_mvt = target.trajectory
    # easy solution need to be investeagted
    if type_mvt == 'fix':
        pass
    elif type_mvt == 'line':
        target.xc = target.xc + math.ceil(target.vx * delta_time)
        target.yc = target.yc + math.ceil(target.vy * delta_time)
    elif type_mvt == 'linear':
        rectiligneTrajectory(target, delta_time, myRoom)
    elif type_mvt == 'circular':
        pass
    elif type_mvt == 'elliptic':
        pass
    elif type_mvt == 'potential_field':
        # print(target.id)
        potentialField(target, delta_time, myRoom)
    else:
        print("planning method not recognize")


def rectiligneTrajectory(target, delta_time, myRoom):
    if target.label != 'fix':
        if math.fabs(target.xc - target.xgoal[0]) <= 10 and math.fabs(target.yc - target.ygoal[0]) <= 10 and len(
                target.xgoal) > 1:
            del target.xgoal[0]
            del target.ygoal[0]

        xgoal = target.xgoal[0]
        ygoal = target.ygoal[0]

        if (target.xc - xgoal != 0):
            v_x = -target.vx_max * (target.xc - xgoal) / math.fabs((target.xc - xgoal))
        else:
            v_x = 0

        if (target.yc - ygoal != 0):
            v_y = -target.vy_max * (target.yc - ygoal) / math.fabs((target.yc - ygoal))
        else:
            v_y = 0

        target.xc = target.xc + math.ceil(v_x * delta_time)
        target.yc = target.yc + math.ceil(v_y * delta_time)


def potentialField(target, delta_time, myRoom):
    if target.label != 'fix':
        if math.fabs(target.xc - target.xgoal[0]) <= 20 and math.fabs(target.yc - target.ygoal[0]) <= 20 and len(
                target.xgoal) > 1:
            del target.xgoal[0]
            del target.ygoal[0]

        xgoal = target.xgoal[0]
        ygoal = target.ygoal[0]

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
