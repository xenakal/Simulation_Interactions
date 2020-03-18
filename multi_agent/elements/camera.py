import numpy as np
from my_utils.line import *
from multi_agent.elements.target import *
import random


class Camera:
    """
                Class Camera.

                Description : This class create a camera,
                              can also be use to describe real camera in the room representation.

                    :param
                        1. (Room)room                          -- Room object, see class Room
                        2. (int) id                            -- numerical value to recognize the camera easily
                        3. (int) xc                            -- x value of the center of the camera
                        4. (int) yc                            -- y value of the center of the camera
                        5. (int) alpha                         -- orientation angel of the camera
                        6. (string) beta                       -- opening field of the camera
                        7. (int) is_fix                        -- 1 if the camera can rotate, else 0
                        8. ((int),(int),(int)) color           -- color to represent the camera
1
                    :attibutes
                         1. (int) id                           -- numerical value to recognize the camera easily
                        2. (int) signature                     -- numerical value to identify the camera
                        3. (int) xc                            -- x value of the center of the camera
                        4. (int) yc                            -- y value of the center of the camera
                        5. (int) alpha                         -- orientation angel of the camera
                        6. (string) beta                       -- opening field of the camera
                        7. (int) is_fix                        -- 1 if the camera can rotate, else 0
                        8. (int) is_active                     -- 1 if the camera is active, else 0
                        9. ((int),(int),(int)) color           -- color to represent the camera
                       10. (Room)room                          -- Room object, see class Room
                       11. (list) target_in_field_list         -- [Target, ...] Contains every target
                                                                  (not hidden by an other one)
                                                                  in the triangle field of vue
                       12. (list) targetCameraDistance_list    -- [TargetCameraDistance, ...] Contains 11, but
                                                                  sort in terms of distance to cam
                       13. (list) target_projection            -- [(y_down,y_up),...,(limite_fied_down,limit_field_up)],
                                                                  uses 12 to create a representation of the 2D field
                                                                  in 1D

                    :notes
                        1. ! use the run() or method take_picture() to fill 11,12,13
                        2. For every function using a radius, radius >= 0
                        3. Camera is considered as active when the function run fills the vector 12.


    """

    def __init__(self, room, id, xc, yc, alpha, beta, is_fix=1, color=0):
        """ Identification name (id) + number """
        self.id = id
        self.signature = self.signature = int(random.random() * 10000000000000000) + 100  # always higher than 100

        """Camera description on the map"""
        self.xc = xc
        self.yc = yc
        self.alpha = math.radians(alpha)  # deg rotation
        self.beta = math.radians(beta)  # deg view angle

        """Attibutes"""
        self.is_fix = is_fix
        self.isActive = 1
        self.color = color
        self.room = room

        """Default values"""
        if color == 0:
            r = 25 + 20 * random.randrange(0, 10, 1)
            g = 25 + 20 * random.randrange(0, 10, 1)
            b = 25 + 20 * random.randrange(0, 10, 1)
            self.color = (r, g, b)

        """List to get target in the camera vision field"""
        """ !! use the metjod take picture to fill those list !! """
        self.target_in_field_list = []
        self.targetCameraDistance_list = []
        self.target_projection = []

    def run(self):
        """
            :description
               function to call to get a picture of the room in the simulation

            :return / modify vector
                1. (bool) if camemra is_active, self.targetCameraDistance_list -- [TargetCameraDistance, ...]
                                                                                 Contains 11, but sort by distances
                2.        else, empty list []
        """

        if self.is_camera_active():
            self.take_picture(self.room.active_Target_list, 400)
            return self.targetCameraDistance_list
        else:
            return []

    def activate_camera(self):
        """
            :description
                 modifies the state of the camera
        """
        self.isActive = 1

    def desactivate_camera(self):
        """
            :description
                 modifies the state of the camera
        """
        self.isActive = 0

    def is_camera_active(self):
        """
            :return
                1. (bool) -- True is the camera is active, else False
        """
        if self.isActive == 1:
            return True
        else:
            return False

    def cam_rotate(self, delta_angle):
        """
            :description
                To modify alpha from step

            :param
                1. (int) delta_angle -- orientation change in degree
        """
        if self.is_fix == 0:
            self.alpha = self.alpha + math.radians(delta_angle)

    def take_picture(self, target_list, length_projection):
        """
            :description
                Function to call in order to fill 11,12,13 in the class description.

                From target_list below it:
                    1. Find the target seen by the camera in a given Room
                    2. Sort the target seen in terms of distances
                    3. Compute the projection to create a fake loose of information from 2D to 1D
                       (x_target_in_room_frame,y_target_in_room_frame) coordinate becomes y_target_in_camera_frame

            :param
                1. (Target_list) target_list     -- a list of Target
                2. (int) > 0 length_projection   -- distance in camera frame to which we want to build the projection
        """

        self.target_in_field_list = []
        self.targetCameraDistance_list = []
        "1. Detection of all the target viewed by the cam"
        for target in target_list:
            cdt_in_field = self.is_x_y_radius_in_field_not_obstructed(target.xc, target.yc, target.radius)
            cdt_not_hidden = not (self.is_xc_yc_radius_in_hidden_zone_all_targets(target.xc, target.yc, target.radius))

            if cdt_in_field and cdt_not_hidden:
                self.target_in_field_list.append(target)

        "2. Sorting the target in terms of distance to the cam"
        self.targetCameraDistance_list = self.sort_detected_target(self.target_in_field_list)
        "3. Computing the projections"
        self.target_projection = self.compute_projection(self.targetCameraDistance_list, length_projection)

    def coordinate_change_from_world_frame_to_camera_frame(self, x_in_room_frame, y_in_room_frame):
        """
            :description
                To change the x_in_room_frame,y_in_room_frame coordinate in room frame
                to x_in_camera_frame,y_in_camera_frame

            :param
                1. (int)  x_in_camera_frame  -- x coordinate from a point in room frame
                2. (int) y_in_camera_frame   -- y coordinate from a point in camera frame

            :return / modify vector
                1. (int,int) (x_in_camera_frame, y_in_camera_frame) -- x,y point transformed in the camera's frame
        """
        x_no_offset = x_in_room_frame - self.xc
        y_no_offset = y_in_room_frame - self.yc

        x_in_camera_frame = math.cos(self.alpha) * x_no_offset + math.sin(self.alpha) * y_no_offset
        y_in_camera_frame = -math.sin(self.alpha) * x_no_offset + math.cos(self.alpha) * y_no_offset
        return x_in_camera_frame, y_in_camera_frame

    def sort_detected_target(self, target_list):
        """
            :description
               Function to sort a target list in terms of distances

            :param
                1. (Target_list) target_list     -- a list of Target
            :return
                1. (TargetCameraDistance_list)   -- a list of TargetCameraDistance sorted by distances
        """
        target_camera_distance_list = []
        for target in target_list:
            distance = math.ceil(distance_btw_two_point(self.xc, self.yc, target.xc, target.yc))
            target_camera_distance_list.append(TargetCameraDistance(target, distance))

        target_camera_distance_list.sort()
        return target_camera_distance_list

    def compute_projection(self, targetCameraDistance_list, length_projection=200):
        """
            :description
               Create the lost of information when using a camera.

            :param
                1.(TargetCameraDistance_list) targetCameraDistance_list    -- a list of Target

            :return
                1. ([(int,int),...]) projection_list       -- [(y_down,y_up),...,(limite_fied_down,limit_field_up)]
                                                                a list of TargetCameraDistance sorted by distances
        """

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

            target_limit_in_camera_frame = perpendicular_to_line_camera_target.lineCircleIntersection(target.radius,
                                                                                            x_target_in_camera_frame,
                                                                                            y_target_in_camera_frame)
            "Cheking if there is an intersection"
            if not (target_limit_in_camera_frame[0] == target_limit_in_camera_frame[1] == target_limit_in_camera_frame[
                2] == target_limit_in_camera_frame[3] == 0):

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

    def is_x_y_radius_in_field_not_obstructed(self, x, y, r_target=0):
        """
            :description
                To check if the point x,y in room frame coordinate is in the triangle representing the camera's
                field of vision

                if r_target is not equal to 0, the point x,y represent the center of the circle with a radius r

                    a circle is consider in the field if one the point is tangent to the camera limits line.
                    -> set r to zero to consider only the center

            :param
                1. (int) x        -- x coordinate of a point in the room frame
                2. (int) y        -- y coordinate of a point in the room frame
                3. (int) r_target -- radius of a circle/Target

            :return / modify vector
                1. (bool)         -- True if (x,y) or circle limit point is between the limits
        """
        (x_target_in_camera_frame, y_target_in_camera_frame) = self.coordinate_change_from_world_frame_to_camera_frame(
            x, y)

        line_camera_target = Line(0, 0, x_target_in_camera_frame, y_target_in_camera_frame)
        perpendicular_to_line_camera_target = line_camera_target.linePerp(x_target_in_camera_frame,
                                                                          y_target_in_camera_frame)

        target_limit_in_camera_frame = perpendicular_to_line_camera_target.lineCircleIntersection(r_target,
                                                                                            x_target_in_camera_frame,
                                                                                            y_target_in_camera_frame)

        y_min = min(target_limit_in_camera_frame[1], target_limit_in_camera_frame[3])
        y_max = max(target_limit_in_camera_frame[1], target_limit_in_camera_frame[3])

        beta_target_min = math.atan2(y_min, x_target_in_camera_frame)
        beta_target_max = math.atan2(y_max, x_target_in_camera_frame)

        margin_low = beta_target_max >= -(math.fabs(self.beta / 2))
        margin_high = beta_target_min <= math.fabs(self.beta / 2)

        if margin_low and margin_high:
            return True
        else:
            return False

    def is_x_y_in_hidden_zone_one_target(self, x, y, xt, yt, r_target):
        """
            :description
                To check if he point x,y is hidden by a target from the room

            :param
                1. (int) x        -- x coordinate of a point in the room frame
                2. (int) y        -- y coordinate of a point in the room frame
                3. (int) xt       -- xt coordinate of the target in the room frame
                4. (int) yt       -- yt coordinate of the target int the room frame
                3. (int) r_target -- radius of a circle/Target

            :return / modify vector
                1. (bool)         -- True if (x,y) is between hidden
        """

        "coordinate transfromation"
        (xcf, ycf) = self.coordinate_change_from_world_frame_to_camera_frame(x, y)
        (xctf, yctf) = self.coordinate_change_from_world_frame_to_camera_frame(xt, yt)

        "Computing limits"
        line_cam_target = Line(0, 0, xctf, yctf)
        line_perp_cam_target = line_cam_target.linePerp(xctf, yctf)
        idca = line_perp_cam_target.lineCircleIntersection(r_target, xctf, yctf)

        "Check if intersection exist"
        if not (idca[0] == idca[1] == idca[2] == idca[3] == 0):
            alpha1 = math.atan2(idca[1], idca[0])
            alpha2 = math.atan2(idca[3], idca[2])
            alphapt = math.atan2(ycf, xcf)

            "Condition to be hidden"
            if alpha1 > alphapt > alpha2 and xcf > xctf or alpha1 < alphapt < alpha2 and xcf > xctf:
                return True
            else:
                return False

        else:
            return False

    def is_x_y_in_hidden_zone_all_targets(self, x, y):
        """
            :description
                Extend the function is_x_y_in_hidden_zone_one_target,
                1.for every target in the room

            :param
                1. (int) x        -- x coordinate of a point in the room frame
                2. (int) y        -- y coordinate of a point in the room frame

            :return / modify vector
                1. (bool)         -- True if the point is not hidden
        """
        for target in self.room.active_Target_list:
            xt = target.xc
            yt = target.yc
            radius = target.radius
            if self.is_x_y_in_hidden_zone_one_target(x, y, xt, yt, radius):
                return True
        return False

    def is_x_y_in_hidden_zone_fix_targets(self, x, y):
        """
            :description
                Extend the function is_x_y_in_hidden_zone_one_target,
                1.for "fix" target in the room

            :param
                1. (int) x        -- x coordinate of a point in the room frame
                2. (int) y        -- y coordinate of a point in the room frame

            :return / modify vector
                1. (bool)         -- True if the point is not hidden
        """

        for target in self.room.information_simulation.Target_list:
            if target.label == "fix":
                xt = target.xc
                yt = target.yc
                radius = target.radius
                if not (x == xt) and not (y == yt):
                    if self.is_x_y_in_hidden_zone_one_target(x, y, xt, yt, radius):
                        return True
        return False

    def is_x_y_in_hidden_zone_mooving_targets(self, x, y):
        """
            :description
                Extend the function is_x_y_in_hidden_zone_one_target,
                1.for "target" and "obstruction" target in the room

            :param
                1. (int) x        -- x coordinate of a point in the room frame
                2. (int) y        -- y coordinate of a point in the room frame

            :return / modify vector
                1. (bool)         -- True if the point is not hidden
        """

        for target in self.room.active_Target_list:
            if target.type == "target" or target.type == "obstruction":
                xt = target.xc
                yt = target.yc
                radius = target.radius
                if self.is_x_y_in_hidden_zone_one_target(x, y, xt, yt, radius):
                    return True
        return False

    def is_xc_yc_radius_in_hidden_zone_all_targets(self, x, y, r=0):
        """
            :description
                Extend the function is_x_y_in_hidden_zone_one_target,
                1.for every target in the room

                2.if not r == 0, then x,y becomes the center of a circle with a radius r
                    a. check if the middle is seen
                    b. check if two extreme points are seen

                  else, same function as the function is_x_y_in_hidden_zone_fix_targets


            :param
                1. (int) x        -- x coordinate of a point in the room frame
                2. (int) y        -- y coordinate of a point in the room frame

            :return / modify vector
                1. (bool)         -- True if the point is not hidden
        """
        cdt_middle = self.is_x_y_in_hidden_zone_all_targets(x, y)
        cdt_up = True
        cdt_down = True

        if not r == 0:
            line_camera_target = Line(self.xc, self.yc, x, y)
            perpendicular_to_line_camera_target = line_camera_target.linePerp(x, y)
            target_limit = perpendicular_to_line_camera_target.lineCircleIntersection(r, x, y)
            cdt_up = self.is_x_y_in_hidden_zone_all_targets(target_limit[0], target_limit[1])
            cdt_down = self.is_x_y_in_hidden_zone_all_targets(target_limit[2], target_limit[3])

        if cdt_middle and cdt_down and cdt_up:
            return True
        else:
            return False

    def is_in_hidden_zone_one_target_matrix_x_y(self, result, x, y, xt, yt, r_target):
        """
            :description
                Same as is_x_y_in_hidden_zone_one_target but for x,y list
                -> more efficient

            :param
                1.  (np.array) result  -- array containing the results for every point
                2. (np.array) x        -- x coordinates of points in the room frame
                3. (np.array) y        -- y coordinates of points in the room frame
                4. (int) xt            -- xt coordinate of the target in the room frame
                5. (int) yt            -- yt coordinate of the target int the room frame
                6. (int) r_target      -- radius of a circle/Target

            :return / modify vector
                1. (np.array)         -- 0 if (x,y) is between hidden, else 1
        """

        (i_tot, j_tot) = result.shape

        "coordinate transformation"
        (xctf, yctf) = self.coordinate_change_from_world_frame_to_camera_frame(xt, yt)

        "line between target and camera"
        line_cam_target = Line(0, 0, xctf, yctf)
        line_perp_cam_target = line_cam_target.linePerp(xctf, yctf)
        idca = line_perp_cam_target.lineCircleIntersection(r_target, xctf, yctf)

        "checking if there is an intersection "
        if not (idca[0] == idca[1] == idca[2] == idca[3] == 0):
            alpha1 = math.atan2(idca[1], idca[0])
            alpha2 = math.atan2(idca[3], idca[2])

            for i in range(i_tot):
                for j in range(j_tot):
                    (xcf, ycf) = self.coordinate_change_from_world_frame_to_camera_frame(x[i, j], y[i, j])
                    alphapt = math.atan2(ycf, xcf)

                    "condition to be hidden"
                    if alpha1 > alphapt > alpha2 and xcf > xctf or alpha1 < alphapt < alpha2 and xcf > xctf:
                        result[i, j] = 0
        return result

    def is_in_hidden_zone_all_targets_matrix_x_y(self, result, x, y):
        """
            :description
               Extend the function is_in_hidden_zone_one_target_matrix_x_y,
                1. to every target in the room

            :param
                1.  (np.array) result  -- array containing the results for every point
                2. (np.array) x        -- x coordinates of points in the room frame
                3. (np.array) y        -- y coordinates of points in the room frame

            :return / modify vector
                1. (np.array)         -- 0 if (x,y) is between hidden, else 1
        """
        for target in self.room.active_Target_list:
            xt = target.xc
            yt = target.yc
            radius = target.radius

            result = self.is_in_hidden_zone_one_target_matrix_x_y(result, x, y, xt, yt, radius)
        return result

    def is_in_hidden_zone_fix_targets_matrix_x_y(self, result, x, y):
        """
            :description
               Extend the function is_in_hidden_zone_one_target_matrix_x_y,
                1. to "fix" target in the room

            :param
                1.  (np.array) result  -- array containing the results for every point
                2. (np.array) x        -- x coordinates of points in the room frame
                3. (np.array) y        -- y coordinates of points in the room frame

            :return / modify vector
                1. (np.array)         -- 0 if (x,y) is between hidden, else 1
        """
        for target in self.room.information_simulation.Target_list:
            if target.type == "fix":
                xt = target.xc
                yt = target.yc
                radius = target.radius
                result = self.is_in_hidden_zone_one_target_matrix_x_y(result, x, y, xt, yt, radius)
        return result

    def is_in_hidden_zone_mooving_targets_matrix_x_y(self, result, x, y):
        """
            :description
               Extend the function is_in_hidden_zone_one_target_matrix_x_y,
                1. to every "target" and "obstrcution" in the room

            :param
                1.  (np.array) result  -- array containing the results for every point
                2. (np.array) x        -- x coordinates of points in the room frame
                3. (np.array) y        -- y coordinates of points in the room frame

            :return / modify vector
                1. (np.array)         -- 0 if (x,y) is between hidden, else 1
        """
        for target in self.room.active_Target_list:
            if target.type == "target" or target.type == "obstruction":
                xt = target.xc
                yt = target.yc
                radius = target.radius
                result = self.is_in_hidden_zone_one_target_matrix_x_y(result, x, y, xt, yt, radius)
        return result


class TargetCameraDistance:
    """"
           Class TargetTargetCameraDistance.

                Description :
                    :params
                        1. (Target) target           -- a Target
                        2. (int) distance            -- distance from the camera to a target
                        3. ((int,int)) projection    -- projection 1D of the target

                    :attibutes
                        1. (Target) target           -- a Target
                        2. (int) distance            -- distance from the camera to a target

                    :notes
                        Only use to sort easily the target in the method sort from the class Camera.
    """

    def __init__(self, target, distance):
        self.target = target
        self.distance = distance
        self.projection = (-1, -1)

    def set_projection(self, projection):
        self.projection = projection

    def __eq__(self, other):
        return self.distance == other.distance

    def __lt__(self, other):
        return self.distance < other.distance

    def __gt__(self, other):
        return self.distance > other.distance
