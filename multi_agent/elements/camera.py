import numpy as np
from my_utils.line import *
from multi_agent.elements.target import *
import random


class Camera:
    def __init__(self, room, cam_id, cam_x, cam_y, cam_alpha, cam_beta, fix=1):
        # Label
        self.id = cam_id

        # Location on the map
        self.xc = cam_x
        self.yc = cam_y
        self.alpha = math.radians(cam_alpha)  # deg rotation
        self.beta = math.radians(cam_beta)  # deg view angle
        self.fix = fix

        # Detection
        self.target_in_field_list = []
        self.targetCameraDistance_list = []
        self.target_projection = []

        self.isActive = 1

        # color from the object
        r = 25 + 20 * random.randrange(0, 10, 1)
        g = 25 + 20 * random.randrange(0, 10, 1)
        b = 25 + 20 * random.randrange(0, 10, 1)

        self.color = (r, g, b)
        self.room = room


    def run(self):
        tab = []
        if self.isActive == 1:

            self.take_picture(self.room.active_Target_list,200)
        return tab

    def camDesactivate(self):
        self.isActive = 0

    def camActivate(self):
        self.isActive = 1

    def isActivate(self):
        if self.isActive == 1:
            return True
        else:
            return False

    def cam_rotate(self, step):
        if self.fix == 0:
            self.alpha = self.alpha + step

    def take_picture(self, target_list, length_projection):
        self.target_in_field_list = []
        self.targetCameraDistance_list = []
        "Detection of all the target viewed by the cam"
        for target in target_list:
            cdt_in_field = self.is_x_y_in_field_not_obstructed(target.xc, target.yc,target.size)
            cdt_not_hidden = not(self.is_in_hidden_zone_all_targets(target.xc, target.yc))
            if cdt_in_field and cdt_not_hidden:
                self.target_in_field_list.append(target)

        "Sorting the target in terms of distance to the cam"
        self.targetCameraDistance_list = self.sort_detected_target(self.target_in_field_list)
        "Computing the projections"
        self.target_projection = self.compute_projection(self.targetCameraDistance_list,200)

    def coordinate_change_from_world_frame_to_camera_frame(self, x, y):
        xi = x - self.xc
        yi = y - self.yc

        xf = math.cos(self.alpha) * xi + math.sin(self.alpha) * yi
        yf = -math.sin(self.alpha) * xi + math.cos(self.alpha) * yi
        return (xf, yf)

    def is_x_y_in_field_not_obstructed(self, x, y, r_target=0):
        ( x_target_in_camera_frame, y_target_in_camera_frame) = self.coordinate_change_from_world_frame_to_camera_frame(x, y)

        line_camera_target = Line(0, 0, x_target_in_camera_frame, y_target_in_camera_frame)
        perpendicular_to_line_camera_target = line_camera_target.linePerp(x_target_in_camera_frame,
                                                                          y_target_in_camera_frame)

        target_limit_in_camera_frame = perpendicular_to_line_camera_target.lineCircleIntersection(r_target,
                                                                                                  x_target_in_camera_frame,
                                                                                                  y_target_in_camera_frame)

        y_min = min(target_limit_in_camera_frame[1],target_limit_in_camera_frame[3])
        y_max = max(target_limit_in_camera_frame[1],target_limit_in_camera_frame[3])

        beta_target_min = math.atan2(y_min,x_target_in_camera_frame)
        beta_target_max = math.atan2(y_max,x_target_in_camera_frame)

        margin_low = beta_target_max >= -(math.fabs(self.beta/2))
        margin_high = beta_target_min <= math.fabs(self.beta/2)

        if margin_low and margin_high:
            return True
        else:
            return False

    def is_in_hidden_zone_one_target(self, x, y, xt, yt, r_target):
        # cam_map
        (xcf, ycf) = self.coordinate_change_from_world_frame_to_camera_frame(x, y)
        (xctf, yctf) = self.coordinate_change_from_world_frame_to_camera_frame(xt, yt)

        # line between target and cam
        line_cam_target = Line(0, 0, xctf, yctf)
        line_perp_cam_target = line_cam_target.linePerp(xctf, yctf)
        idca = line_perp_cam_target.lineCircleIntersection(r_target, xctf, yctf)

        if not (idca[0] == idca[1] == idca[2] == idca[3] == 0):  # if there is an intersection
            # angle
            alpha1 = math.atan2(idca[1], idca[0])
            alpha2 = math.atan2(idca[3], idca[2])
            alphapt = math.atan2(ycf, xcf)

            # condition to be hidden
            if alpha1 > alphapt and alpha2 < alphapt and xcf > xctf or alpha1 < alphapt and alpha2 > alphapt and xcf > xctf:
                return True

        else:
            return False

    def is_in_hidden_zone_one_target_matrix_x_y(self, result, x, y, xt, yt, r_target):
        (i_tot, j_tot) = result.shape

        # cam_map
        (xctf, yctf) = self.coordinate_change_from_world_frame_to_camera_frame(xt, yt)

        # line between target and cam
        line_cam_target = Line(0, 0, xctf, yctf)
        line_perp_cam_target = line_cam_target.linePerp(xctf, yctf)
        idca = line_perp_cam_target.lineCircleIntersection(r_target, xctf, yctf)

        if not (idca[0] == idca[1] == idca[2] == idca[3] == 0):  # if there is an intersection
            # angle
            alpha1 = math.atan2(idca[1], idca[0])
            alpha2 = math.atan2(idca[3], idca[2])

            for i in range(i_tot):
                for j in range(j_tot):
                    (xcf, ycf) = self.coordinate_change_from_world_frame_to_camera_frame(x[i, j], y[i, j])
                    alphapt = math.atan2(ycf, xcf)

                    # condition to be hidden
                    if alpha1 > alphapt and alpha2 < alphapt and xcf > xctf or alpha1 < alphapt and alpha2 > alphapt and xcf > xctf:
                        result[i, j] = 0
        return result

    def is_in_hidden_zone_all_targets(self, x, y):
        for target in self.room.active_Target_list:
            xt = target.xc
            yt = target.yc
            size = target.size
            if self.is_in_hidden_zone_one_target(x, y, xt, yt, size):
                return True
        return False

    def is_in_hidden_zone_fix_targets(self, x, y):
        for target in self.room.information_simulation.Target_list:
            if target.label == "fix":
                xt = target.xc
                yt = target.yc
                size = target.size
                if not (x == xt) and not (y == yt):
                    if self.is_in_hidden_zone_one_target(x, y, xt, yt, size):
                        return True
        return False

    def is_in_hidden_zone_mooving_targets(self, x, y):
        for target in self.room.active_Target_list:
            if target.type == "target" or target.type == "obstruction":
                xt = target.xc
                yt = target.yc
                size = target.size
                if self.is_in_hidden_zone_one_target(x, y, xt, yt, size):
                    return True
        return False

    def is_in_hidden_zone_all_targets_matrix_x_y(self, result, x, y):
        for target in self.room.active_Target_list:
            xt = target.xc
            yt = target.yc
            size = target.size

            result = self.is_in_hidden_zone_one_target_matrix_x_y(result, x, y, xt, yt, size)
        return result

    def is_in_hidden_zone_fix_targets_matrix_x_y(self, result, x, y):
        for target in self.room.information_simulation.Target_list:
            if target.type == "fix":
                xt = target.xc
                yt = target.yc
                size = target.size
                result = self.is_in_hidden_zone_one_target_matrix_x_y(result, x, y, xt, yt, size)
        return result

    def is_in_hidden_zone_mooving_targets_matrix_x_y(self, result, x, y):
        for target in self.room.active_Target_list:
            if target.type == "target" or target.type == "obstruction":
                xt = target.xc
                yt = target.yc
                size = target.size
                result = self.is_in_hidden_zone_one_target_matrix_x_y(result, x, y, xt, yt, size)
        return result

    def objectsInField(self, targetList):
        self.target_in_field_list = []
        targetInTriangle = []

        # checking for every target if it is in the vision field of the camera.
        for target in targetList:
            # Frame transformation from the world frame to the cam frame for each target
            (xcf, ycf) = self.coordinate_change_from_world_frame_to_camera_frame(target.xc, target.yc)
            d_cam_target = distance_btw_two_point(xcf, ycf, 0, 0)
            beta_target = math.atan2(target.size / 2, d_cam_target)  # between the center and the border of the target

            if self.is_x_y_in_field_not_obstructed(target.xc, target.yc, beta_target):
                targetInTriangle.append(target)

        return targetInTriangle.copy()


    def sort_detected_target(self, target_list):
        target_camera_distance_list = []

        for target in target_list:
            distance = math.ceil(distance_btw_two_point(self.xc, self.yc, target.xc, target.yc))
            target_camera_distance_list.append(TargetCameraDistance(target, distance))

        target_camera_distance_list.sort()
        return target_camera_distance_list

    def compute_projection(self, targetCameraDistance_list, length_projection=200):

        projection_list = []
        """Placing the view in the cam frame"""
        median_camera = Line(0, 0, 1, 0)
        projection_line = median_camera.linePerp(length_projection, 0)

        """Bound of the field camera"""
        limit_up_camera = Line(0, 0, math.cos(self.beta / 2), math.sin(self.beta / 2))
        limit_down_camera = Line(0, 0, math.cos(self.beta / 2), math.sin(-self.beta / 2))

        """Projection of the limit on the projection plane"""
        camera_limit_up_on_projection_line = limit_up_camera.lineIntersection(projection_line)[1]
        camera_limit_down_on_projection_line = limit_down_camera.lineIntersection(projection_line)[1]


        """Same but for every target now"""
        for element in targetCameraDistance_list:
            target = element.target
            """Coordinate change"""
            (x_target_in_camera_frame,
             y_target_in_camera_frame) = self.coordinate_change_from_world_frame_to_camera_frame(target.xc, target.yc)

            """Compute the value on the projection plane"""
            line_camera_target = Line(0, 0, x_target_in_camera_frame, y_target_in_camera_frame)
            perpendicular_to_line_camera_target = line_camera_target.linePerp(x_target_in_camera_frame,
                                                                              y_target_in_camera_frame)

            target_limit_in_camera_frame = perpendicular_to_line_camera_target.lineCircleIntersection(target.size,
                                                                                            x_target_in_camera_frame,
                                                                                            y_target_in_camera_frame)

            if not (target_limit_in_camera_frame[0] == target_limit_in_camera_frame[1] == target_limit_in_camera_frame[2] == target_limit_in_camera_frame[3] == 0):  # if there is an intersection

                if target_limit_in_camera_frame[1] < target_limit_in_camera_frame[3]:
                    target_limit_up = Line(0, 0, target_limit_in_camera_frame[0], target_limit_in_camera_frame[1])
                    target_limit_down = Line(0, 0, target_limit_in_camera_frame[2], target_limit_in_camera_frame[3])
                else:
                    target_limit_up = Line(0, 0, target_limit_in_camera_frame[0], target_limit_in_camera_frame[3])
                    target_limit_down = Line(0, 0, target_limit_in_camera_frame[2], target_limit_in_camera_frame[1])


                target_limit_up_projection = target_limit_up.lineIntersection(projection_line)[1]
                target_limit_down_projection = target_limit_down.lineIntersection(projection_line)[1]

                """Checkin limits are in the field"""
                if target_limit_down_projection < camera_limit_down_on_projection_line:
                    target_limit_down_projection = camera_limit_down_on_projection_line

                if target_limit_up_projection < camera_limit_down_on_projection_line:
                    target_limit_up_projection = camera_limit_down_on_projection_line

                if target_limit_down_projection > camera_limit_up_on_projection_line:
                    target_limit_down_projection = camera_limit_up_on_projection_line

                if target_limit_up_projection > camera_limit_up_on_projection_line:
                    target_limit_up_projection = camera_limit_up_on_projection_line

                projection_list.append((target_limit_down_projection, target_limit_up_projection))
                element.set_projection((target_limit_down_projection, target_limit_up_projection))

        projection_list.append((camera_limit_down_on_projection_line, camera_limit_up_on_projection_line))
        return projection_list


class TargetCameraDistance:

    def __init__(self, target, distance):
        self.target = target
        self.distance = distance
        self.projection = (-1,-1)

    def set_projection(self, projection):
        self.projection = projection

    def __eq__(self, other):
        return self.distance == other.distance

    def __lt__(self, other):
        return self.distance < other.distance

    def __gt__(self, other):
        return self.distance > other.distance
