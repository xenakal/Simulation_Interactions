from src.multi_agent.elements.target import *
import random
import math

from src.my_utils.my_math.bound import bound_angle_btw_minus_pi_plus_pi
from src.my_utils.my_math.line import Line, distance_btw_two_point
from src.my_utils.string_operations import parse_list


def get_camera_agentCam_vs_agentCamRepresentation(agent):
    """
            :description
                   AgentCam and AgentCamRepresentation use Camera and Camera_representation
                   This function dectect what type the camera.

            :param
                   1. (AgentCam or AgentCamRepresentation) agent        -- An agent or its representation

            :return / modify vector
                   1. (Camera or CameraRepresentation)                 -- Return the appropriate camera.
    """
    import src.multi_agent.agent.agent_interacting_room_camera as aCam
    camera = None
    if isinstance(agent, aCam.AgentCam):
        camera = agent.camera
    elif isinstance(agent, aCam.AgentCamRepresentation):
        camera = agent.camera_representation
    return camera


def find_cam_in_camera_representation(room_representation, camera_id):
    """
            :description
                 Return a camera associated to a given ID

            :param
                   1. (Room/Room_representation) agent        --   An agent or its representation
                   2 (int) camera_id                          --  id referring to a camera

            :return
                   1. (Camera or CameraRepresentation)        --   Return the appropriate camera.
    """
    for agentCam in room_representation.agentCams_representation_list:
        camera = get_camera_agentCam_vs_agentCamRepresentation(agentCam)
        if int(camera.id) == int(camera_id):
            return camera
    return None


def is_x_y_radius_in_field_not_obstructed(camera, x, y, r_target=0):
    """
            :description
                To check if the point x,y in room frame coordinate is in the triangle representing the camera's
                field of vision

                if r_target is not equal to 0, the point x,y represent the center of the circle with a radius r

                    a circle is consider in the field if one the point is tangent to the camera limits line.
                    -> set r to zero to consider only the center

            :param
                1  (CameraRepresentation)  -- Camera / CameraRepresentation containing information related to the cam
                2. (int) x                 -- x coordinate of a point in the room frame
                3. (int) y                 -- y coordinate of a point in the room frame
                4. (int) r_target          -- radius of a circle/Target

            :return / modify vector
                1. (bool)         -- True if (x,y) or circle limit point is between the limits
        """
    (x_target_in_camera_frame, y_target_in_camera_frame) = camera.coordinate_change_from_world_frame_to_camera_frame(x,
                                                                                                                     y)
    if x_target_in_camera_frame >= 0:

        line_camera_target = Line(0, 0, x_target_in_camera_frame, y_target_in_camera_frame)
        perpendicular_to_line_camera_target = line_camera_target.find_line_perp(x_target_in_camera_frame,
                                                                                y_target_in_camera_frame)

        target_limit_in_camera_frame = perpendicular_to_line_camera_target.find_intersection_btw_line_circle(r_target,
                                                                                                             x_target_in_camera_frame,
                                                                                                             y_target_in_camera_frame)

        y_min = min(target_limit_in_camera_frame[1], target_limit_in_camera_frame[3])
        y_max = max(target_limit_in_camera_frame[1], target_limit_in_camera_frame[3])

        beta_target_min = math.atan2(y_min, x_target_in_camera_frame)
        beta_target_max = math.atan2(y_max, x_target_in_camera_frame)

        margin_low = beta_target_max >= -(math.fabs(camera.beta / 2))
        margin_high = beta_target_min <= math.fabs(camera.beta / 2)

        distance = distance_btw_two_point(0, 0, x_target_in_camera_frame, y_target_in_camera_frame)
        distance_test = camera.field_depth > distance

        if margin_low and margin_high and distance_test:
            return True
        else:
            return False
    else:
        return False


def is_x_y_in_hidden_zone_one_target(camera, x, y, xt, yt, r_target):
    """
            :description
                To check if he point x,y is hidden by a target from the room

            :param
                1. (CameraRepresentation)  -- Camera / CameraRepresentation containing information related to the cam
                1. (int) x                 -- x coordinate of a point in the room frame
                2. (int) y                 -- y coordinate of a point in the room frame
                3. (int) xt                -- xt coordinate of the target in the room frame
                4. (int) yt                -- yt coordinate of the target int the room frame
                3. (int) r_target          -- radius of a circle/Target

            :return / modify vector
                1. (bool)         -- True if (x,y) is between hidden
        """

    "coordinate transfromation"
    (xcf, ycf) = camera.coordinate_change_from_world_frame_to_camera_frame(x, y)
    (xctf, yctf) = camera.coordinate_change_from_world_frame_to_camera_frame(xt, yt)

    "check to see if the target is in the field of view"
    if is_x_y_radius_in_field_not_obstructed(camera, xt, yt, r_target):
        "Computing limits"
        line_cam_target = Line(0, 0, xctf, yctf)
        line_perp_cam_target = line_cam_target.find_line_perp(xctf, yctf)
        idca = line_perp_cam_target.find_intersection_btw_line_circle(r_target, xctf, yctf)

        "Check if intersection exist"
        if not (idca[0] == idca[1] == idca[2] == idca[3] == 0):
            alpha1 = math.atan2(idca[1], idca[0])
            alpha2 = math.atan2(idca[3], idca[2])

            alpha_min = min(alpha1, alpha2)
            alpha_max = max(alpha1, alpha2)
            alphapt = math.atan2(ycf, xcf)

            "Condition to be hidden"
            if alpha_min <= alphapt <= alpha_max and xcf > xctf:
                return True
            else:
                return False

    return None


def is_x_y_in_hidden_zone_all_targets(room_representation, camera_id, x, y):
    """
            :description
                Extend the function is_x_y_in_hidden_zone_one_target,
                1.for every target in the room

            :param
                1. (RoomRepresentation) -- room description of the target and the cameras
                2. (int) camera_id      -- camera id to find it in the given room description
                1. (int) x              -- x coordinate of a point in the room frame
                2. (int) y              -- y coordinate of a point in the room frame

            :return / modify vector
                1. (bool)         -- True if the point is not hidden
        """

    camera = find_cam_in_camera_representation(room_representation, camera_id)
    if camera is None:
        return False

    for target in room_representation.target_representation_list:
        xt = target.xc
        yt = target.yc
        radius = target.radius
        if is_x_y_in_hidden_zone_one_target(camera, x, y, xt, yt, radius):
            return True

    return False


def is_x_y_in_hidden_zone_all_targets_based_on_camera(room_representation, camera, x, y):
    """
               :description
                   Extend the function is_x_y_in_hidden_zone_one_target,
                   1.for every target in the room

               :param
                   1. (RoomRepresentation)    -- room description of the target and the cameras
                   2. (CameraRepresentation)  -- camera, not in the room description
                   1. (int) x                 -- x coordinate of a point in the room frame
                   2. (int) y                 -- y coordinate of a point in the room frame

               :return / modify vector
                   1. (bool)         -- True if the point is not hidden

               :note
                If the camera is in the room description equivalent to use is_x_y_in_hidden_zone_all_targets
                with the id.
    """

    if camera is None:
        return False

    for target in room_representation.target_representation_list:
        xt = target.xc
        yt = target.yc
        radius = target.radius
        if is_x_y_in_hidden_zone_one_target(camera, x, y, xt, yt, radius):
            return True

    return False


def is_x_y_in_hidden_zone_fix_targets(room_representation, camera_id, x, y):
    """
            :description
                Extend the function is_x_y_in_hidden_zone_one_target,
                1.for "fix" target in the room


            :param
                1. (RoomRepresentation) -- room description of the target and the cameras
                2. (int) camera_id      -- camera id to find it in the given room description
                1. (int) x              -- x coordinate of a point in the room frame
                2. (int) y              -- y coordinate of a point in the room frame

            :return / modify vector
                1. (bool)         -- True if the point is not hidden
    """
    camera = find_cam_in_camera_representation(room_representation, camera_id)
    if camera is None:
        return False

    for target in room_representation.information_simulation.Target_list:
        if target.label == TargetType.SET_FIX:
            xt = target.xc
            yt = target.yc
            radius = target.radius
            if not (x == xt) and not (y == yt):
                if is_x_y_in_hidden_zone_one_target(camera, x, y, xt, yt, radius):
                    return True
    return False


def is_xc_yc_radius_in_hidden_zone_all_targets(room_representation, camera_id, x, y, r=0):
    """
            :description
                Extend the function is_x_y_in_hidden_zone_one_target,
                1.for every target in the room

                2.if not r == 0, then x,y becomes the center of a circle with a radius r
                    a. check if the middle is seen
                    b. check if two extreme points are seen

                  else, same function as the function is_x_y_in_hidden_zone_fix_targets

            :param
                1. (RoomRepresentation) -- room description of the target and the cameras
                2. (int) camera_id      -- camera id to find it in the given room description
                1. (int) x              -- x coordinate of a point in the room frame
                2. (int) y              -- y coordinate of a point in the room frame

            :return / modify vector
                1. (bool)         -- True if the point is not hidden
    """
    camera = find_cam_in_camera_representation(room_representation, camera_id)
    if camera is None:
        return False

    cdt_middle = is_x_y_in_hidden_zone_all_targets(room_representation, camera.id, x, y)
    cdt_up = True
    cdt_down = True

    if not r == 0:
        line_camera_target = Line(camera.xc, camera.yc, x, y)
        perpendicular_to_line_camera_target = line_camera_target.find_line_perp(x, y)
        target_limit = perpendicular_to_line_camera_target.find_intersection_btw_line_circle(r + 0.01, x, y)
        cdt_up = is_x_y_in_hidden_zone_all_targets(room_representation, camera.id, target_limit[0], target_limit[1])
        cdt_down = is_x_y_in_hidden_zone_all_targets(room_representation, camera.id, target_limit[2], target_limit[3])

    if cdt_middle and cdt_down and cdt_up:
        return True
    else:
        return False


def is_in_hidden_zone_one_target_matrix_x_y(room_representation, camera_id, result, x, y, xt, yt, r_target):
    """
            :description
                Same as is_x_y_in_hidden_zone_one_target but for x,y list
                -> more efficient, number of computation reduced

          :param
                1. (RoomRepresentation) -- room description of the target and the cameras
                2. (int) camera_id      -- camera id to find it in the given room description
                3. (bool)         -- True if the point is not hidden
                4.  (np.array) result  -- array containing the results for every point
                5. (np.array) x        -- x coordinates of points in the room frame
                6. (np.array) y        -- y coordinates of points in the room frame
                7. (int) xt            -- xt coordinate of the target in the room frame
                8. (int) yt            -- yt coordinate of the target int the room frame
                9. (int) r_target      -- radius of a circle/Target

            :return / modify vector
                1. (np.array)         -- 0 if (x,y) is between hidden, else 1
        """

    camera = find_cam_in_camera_representation(room_representation, camera_id)
    if camera is None:
        return False

    "check to see if the target is in the field of view"
    if is_x_y_radius_in_field_not_obstructed(camera, xt, yt, r_target):
        (i_tot, j_tot) = result.shape

        "coordinate transformation"
        (xctf, yctf) = camera.coordinate_change_from_world_frame_to_camera_frame(xt, yt)

        "line between target and camera"
        line_cam_target = Line(0, 0, xctf, yctf)
        line_perp_cam_target = line_cam_target.find_line_perp(xctf, yctf)
        idca = line_perp_cam_target.find_intersection_btw_line_circle(r_target, xctf, yctf)

        "checking if there is an intersection "
        if not (idca[0] == idca[1] == idca[2] == idca[3] == 0):
            alpha1 = math.atan2(idca[1], idca[0])
            alpha2 = math.atan2(idca[3], idca[2])

            alpha_min = min(alpha1, alpha2)
            alpha_max = max(alpha1, alpha2)

            for i in range(i_tot):
                for j in range(j_tot):
                    (xcf, ycf) = camera.coordinate_change_from_world_frame_to_camera_frame(x[i, j], y[i, j])
                    alphapt = math.atan2(ycf, xcf)

                    "condition to be hidden"
                    if alpha_min < alphapt < alpha_max and xcf > xctf:
                        result[i, j] = 0
        else:
            print("error")
    return result


def is_in_hidden_zone_all_targets_matrix_x_y(room_representation, camera_id, result, x, y):
    """
            :description
               Extend the function is_in_hidden_zone_one_target_matrix_x_y,
                1. to every target in the room

            :param
                1. (RoomRepresentation) -- room description of the target and the cameras
                2. (int) camera_id      -- camera id to find it in the given room description
                3.  (np.array) result  -- array containing the results for every point
                4. (np.array) x        -- x coordinates of points in the room frame
                5. (np.array) y        -- y coordinates of points in the room frame

            :return / modify vector
                1. (np.array)         -- 0 if (x,y) is between hidden, else 1
        """

    camera = find_cam_in_camera_representation(room_representation, camera_id)
    if camera is None:
        return False

    for target in room_representation.target_representation_list:
        xt = target.xc
        yt = target.yc
        radius = target.radius

        result = is_in_hidden_zone_one_target_matrix_x_y(room_representation, camera.id, result, x, y, xt, yt, radius)
    return result


def is_in_hidden_zone_fix_targets_matrix_x_y(room_representation, camera_id, result, x, y):
    """
            :description
               Extend the function is_in_hidden_zone_one_target_matrix_x_y,
                1. to "fix" target in the room

            :param
                1. (RoomRepresentation) -- room description of the target and the cameras
                2. (int) camera_id      -- camera id to find it in the given room description
                3.  (np.array) result  -- array containing the results for every point
                4. (np.array) x        -- x coordinates of points in the room frame
                5. (np.array) y        -- y coordinates of points in the room frame

            :return / modify vector
                1. (np.array)         -- 0 if (x,y) is between hidden, else 1
        """
    camera = find_cam_in_camera_representation(room_representation, camera_id)
    if camera is None:
        return False

    for target in room_representation.information_simulation.target_list:
        if target.type == TargetType.SET_FIX:
            xt = target.xc
            yt = target.yc
            radius = target.radius
            result = is_in_hidden_zone_one_target_matrix_x_y(room_representation, camera.id, result, x, y, xt, yt,
                                                             radius)
    return result


class CameraRepresentation(Item):
    """
        Class CameraRepresentation.

        Description : This class contains parameter to describe a camera
        :param
            1. (int) id                                     -- numerical value to recognize the camera easily

            2. (int) xc-[m]                                 -- x value of the center of the camera
            3. (int) yc-[m]                                 -- y value of the center of the camera
            4. (int) alpha-[radian]                         -- orientation angle of the camera
            5. (string) beta-[radian]                       -- opening field of the camera
            6. (int) field_depth-[m]                        -- depth field from the camera, upon this distance camera  does not detect anymore.

            7. ((int),(int),(int)) color                    -- color to represent the camera

        :attributes
            1. (int) id                                     -- numerical value to recognize the camera easily
            2. (int) signature                              -- numerical value to identify the camera

            3. (int) xc-[m]                                 -- x value of the center of the camera
            4. (int) yc-[m]                                 -- y value of the center of the camera
            5. (int) alpha-[radian]                         -- orientation angle of the camera
            6. (string) beta-[radian]                       -- opening field of the camera
            7. (int) field_depth-[m]                        -- depth field from the camera, upon this distance camera  does not detect anymore.

            8. (float) std_measurement_error_position       -- error for position measures
            9. (float) std_measurement_error_speed          -- error for speed measures
           10. (float) std_measurement_error_acceleration   -- error for acceleration measures

           11. (bool) is_active                             -- True if the camera can take pictures

           12. ((int),(int),(int)) color                    -- color to represent the camera
           13. (list) attributes_not_to_txt                 -- to enable a choice of the attributes to save

        :notes
            attributes 1., 2. and 13. are from coming from Item class
       """

    def __init__(self, id=None, xc=None, yc=None, alpha=None, beta=None, field_depth=None, color=None):
        super().__init__(id)

        "Camera description on the maps"
        self.xc = xc
        self.yc = yc
        self.alpha = alpha
        self.beta = beta
        self.field_depth = field_depth

        "Error"
        self.std_measurement_error_position = constants.STD_MEASURMENT_ERROR_POSITION
        self.std_measurement_error_speed = constants.STD_MEASURMENT_ERROR_SPEED
        self.std_measurement_error_acceleration = constants.STD_MEASURMENT_ERROR_ACCCELERATION

        "Attibutes"
        self.is_active = False
        self.color = color

        self.attributes_not_to_txt += ["item_type", "signature", "std_measurment_error_position",
                                       "std_measurment_error_speed", "std_measurment_error_acceleration",
                                       "is_active", "color"]

        "Default values"
        if self.alpha is not None:
            self.alpha = bound_angle_btw_minus_pi_plus_pi(alpha)  # deg rotation
        if self.beta is not None:
            self.beta = bound_angle_btw_minus_pi_plus_pi(beta)  # deg view angle
        if color == None:
            r = 25 + 20 * random.randrange(0, 10, 1)
            g = 25 + 20 * random.randrange(0, 10, 1)
            b = 25 + 20 * random.randrange(0, 10, 1)
            self.color = (r, g, b)

    def init_from_camera(self, camera):
        self.id = camera.id
        self.signature = camera.signature
        self.xc = camera.xc
        self.yc = camera.yc
        self.alpha = bound_angle_btw_minus_pi_plus_pi(camera.alpha)
        self.beta = bound_angle_btw_minus_pi_plus_pi(camera.beta)
        self.field_depth = camera.field_depth
        self.std_measurement_error_position = camera.std_measurement_error_position
        self.std_measurement_error_speed = camera.std_measurement_error_speed
        self.std_measurement_error_acceleration = camera.std_measurement_error_acceleration
        self.color = camera.color
        self.is_active = camera.is_active

    def angle_degToRad(self):
        "Transforms angle attribues to radians supposing it is in degree"
        if self.alpha is not None:
            self.alpha = math.radians(self.alpha)
        if self.beta is not None:
            self.beta = math.radians(self.beta)

    def angle_radToDeg(self):
        "Transforms angle attribues to degree supposing it is in radian"
        if self.alpha is not None:
            self.alpha = math.degrees(self.alpha)

        if self.beta is not None:
            self.beta = math.degrees(self.beta)

    def save_to_txt(self):
        "Save the attributes that are not in self.attributes_not_to_txt, angles are saved in degrees"
        self.angle_radToDeg()
        s = super().save_to_txt()
        self.angle_degToRad()
        return s

    def load_from_save_to_txt(self, s):
        "Load attributes for a txt string representation"
        super().load_from_save_to_txt(s)
        self.angle_degToRad()

    def coordinate_change_from_world_frame_to_camera_frame(self, x_in_room_frame, y_in_room_frame):
        """
            :description
                To change the x_in_room_frame,y_in_room_frame coordinate in room frame
                to x_in_camera_frame,y_in_camera_frame

                 inverse transformation : coordinate_change_from_camera_frame_to_world_frame

            :param
                1. (int)  x_in_room_frame  -- x coordinate of a point in room frame
                2. (int) y_in_room_frame   -- y coordinate of a point in room frame

            :return / modify vector
                1. (int,int) (x_in_camera_frame, y_in_camera_frame) -- x,y point transformed in the camera's frame
        """
        x_no_offset = x_in_room_frame - self.xc
        y_no_offset = y_in_room_frame - self.yc

        x_in_camera_frame = math.cos(self.alpha) * x_no_offset + math.sin(self.alpha) * y_no_offset
        y_in_camera_frame = -math.sin(self.alpha) * x_no_offset + math.cos(self.alpha) * y_no_offset
        return x_in_camera_frame, y_in_camera_frame

    def coordinate_change_from_camera_frame_to_world_frame(self, x_in_cam_frame, y_in_cam_frame):
        """
                :description
                    To change the x_in_room_frame,y_in_room_frame coordinate in room frame
                    to x_in_camera_frame,y_in_camera_frame

                    inverse transformation : coordinate_change_from_world_frame_to_camera_frame

                :param
                    1. (int)  x_in_camera_frame  -- x coordinate from a point in camera frame
                    2. (int) y_in_camera_frame   -- y coordinate from a point in camera frame

                :return / modify vector
                    1. (int,int) (x_in_room_frame, y_in_room_frame) -- x,y point transformed in the room frame
        """
        # inverse rotation
        x_world_frame_no_offset = math.cos(-self.alpha) * x_in_cam_frame + math.sin(-self.alpha) * y_in_cam_frame
        y_world_frame_no_offset = -math.sin(-self.alpha) * x_in_cam_frame + math.cos(-self.alpha) * y_in_cam_frame

        # include the offset of camera relative to room origin
        x_with_offset = x_world_frame_no_offset + self.xc
        y_with_offset = y_world_frame_no_offset + self.yc

        return x_with_offset, y_with_offset


class Camera(CameraRepresentation):
    """
                Class Camera.

                Description : This class create a camera,
                              can also be use to describe real camera in the room representation.

                    :param
                        8. (list) t_add-[s]                        -- Contains activation times
                        9. (list) t_del-[s]                        -- Contains desactivation times

                    :attibutes
                        14. (int) xc_min-[m]                        -- limit target position
                        15. (int) xc_max-[m]                        -- limit target position
                        16. (int) yc_min-[m]                        -- limit target position
                        17. (int) yc_max-[m]                        -- limit target position

                        17. (list[int]) t_add-[s]                   -- Contains activation times
                        18. (list[int]) t_del-[s]                   -- Contains desactivation times
                        19. (int) number_of_time_passed             -- Keeps at which time it is

                        20. (list[string]) attributes_not_to_txt    -- same as in CameraRepresentation

                        21. (list[Target]) target_in_field_list     -- List of the target in the field
                        22. (list[TargetCameraDistance])targetCameraDistance_list
                                                                    -- List of the target sort by distance
                        23  (list((int),(int))) target_projection   -- Target projection on a projection line



                    :notes
                        1. ! use the run() or method take_picture() to fill 11,12,13
                        2. For every function using a radius, radius >= 0
                        3. Camera is considered as active when the function run fills the vector 12.


    """

    def __init__(self, id=None, xc=None, yc=None, alpha=None, beta=None, filed_depth=None, color=None, t_add=None,
                 t_del=None):
        """Initialisation"""
        super().__init__(id, xc, yc, alpha, beta, filed_depth, color)

        self.xc_min = 0
        self.xc_max = constants.ROOM_DIMENSION_X
        self.yc_min = 0
        self.yc_max = constants.ROOM_DIMENSION_Y

        "Attibutes"
        self.t_add = t_add
        self.t_del = t_del
        self.number_of_time_passed = 0

        self.attributes_not_to_txt += ["xc_min", "xc_max", "yc_min", "yc_max", "number_of_time_passed",
                                       "target_in_field_list", "targetCameraDistance_list", "target_projection"]

        "Default values"
        if t_add == None or t_del == None:
            self.t_add = [0.0]
            self.t_del = [1000.0]

        "List to get target in the camera vision field"
        " !! use the metjod take picture to fill those list !! "
        self.target_in_field_list = []
        self.targetCameraDistance_list = []
        self.target_projection = []

    def run(self, room):
        """
            :description
               function to call to get a picture of the room in the simulation

            :return / modify vector
                1. (bool) if camemra is_active, self.targetCameraDistance_list -- [TargetCameraDistance, ...]
                                                                                 Contains 11, but sort by distances
                2.        else, empty list []
        """

        if self.is_active:  # we can take only picture in the real world
            self.take_picture(room, 200)
            return self.targetCameraDistance_list
        else:
            return []

    def take_picture(self, room, length_projection):
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

        target_list = room.target_representation_list

        "1. Detection of all the target viewed by the cam"
        for target in target_list:
            cdt_in_field = is_x_y_radius_in_field_not_obstructed(self, target.xc, target.yc, target.radius)
            cdt_not_hidden = not is_xc_yc_radius_in_hidden_zone_all_targets(room, self.id, target.xc, target.yc,
                                                                            target.radius)

            if cdt_in_field and cdt_not_hidden:
                self.target_in_field_list.append(target)

        "2. Sorting the target in terms of distance to the cam"
        self.targetCameraDistance_list = self.sort_detected_target(self.target_in_field_list)
        "3. Computing the projections"
        self.target_projection = self.compute_projection(self.targetCameraDistance_list, length_projection)

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
            distance = distance_btw_two_point(self.xc, self.yc, target.xc, target.yc)
            target_camera_distance_list.append(TargetCameraDistance(target, distance))

        target_camera_distance_list.sort()
        return target_camera_distance_list

    def compute_projection(self, targetCameraDistance_list, length_projection=100):
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
        projection_line = median_camera.find_line_perp(length_projection, 0)

        """Bound of the field camera"""
        limit_up_camera = Line(0, 0, math.cos(self.beta / 2), math.sin(self.beta / 2))
        limit_down_camera = Line(0, 0, math.cos(self.beta / 2), math.sin(-self.beta / 2))

        """Projection of the limit on the projection plane"""
        camera_limit_up_on_projection_line = limit_up_camera.find_intersection_btw_two_line(projection_line)[1]
        camera_limit_down_on_projection_line = limit_down_camera.find_intersection_btw_two_line(projection_line)[1]

        """Same but for every target now"""
        for element in targetCameraDistance_list:

            target = element.target
            """Coordinate change"""
            (x_target_in_camera_frame,
             y_target_in_camera_frame) = self.coordinate_change_from_world_frame_to_camera_frame(target.xc, target.yc)
            """Compute the value on the projection plane"""
            line_camera_target = Line(0, 0, x_target_in_camera_frame, y_target_in_camera_frame)
            perpendicular_to_line_camera_target = line_camera_target.find_line_perp(x_target_in_camera_frame,

                                                                                    y_target_in_camera_frame)

            target_limit_in_camera_frame = perpendicular_to_line_camera_target.find_intersection_btw_line_circle(
                target.radius,
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

                target_limit_up_projection = target_limit_up.find_intersection_btw_two_line(projection_line)[1]
                target_limit_down_projection = target_limit_down.find_intersection_btw_two_line(projection_line)[1]

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


if __name__ == "__main__":
    camera = Camera(0, 1, 1, 1, 1, 5, None, [0], [100])
    camera1 = Camera()
    t_start = time.time()
    print(camera.attributes_to_string())
    print(camera.save_to_txt())
    camera1.load_from_save_to_txt(camera.save_to_txt())
    print(camera1.save_to_txt())
