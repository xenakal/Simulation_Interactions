import random
import re
import math
import numpy as np

from src import constants
from src.multi_agent.elements.camera import Camera, CameraRepresentation
from src.my_utils import constant_class
from src.my_utils.my_math.bound import bound_angle_btw_minus_pi_plus_pi, bound
from src.my_utils.my_math.line import distance_btw_two_point, Line
from src.my_utils.string_operations import parse_list


class MobileCameraType:
    """
        Camera types
        dof = degree of freedom
        1) FIX         -- 1 dof  beta
        2) ROTATIVE    -- 2 dof  beta,alpha
        3) RAIL        -- 3 dof  beta,alpha,(x,y)=f(s)
        4) FREE        -- 4 dof beta,alpha,x,y
    """
    FIX = 0
    ROTATIVE = 1
    RAIL = 2
    FREE = 3


class MobileCameraRepresentation(CameraRepresentation):
    """
        Class MobileCameraRepresentation.

        Description :
        :param
            8. (MobileCameraType) camera_type           -- describe what feature the camera has
            9. (Trajectory) trajectory                  -- only used for RAIL camera

        :attibutes
            8. (MobileCameraType) camera_type           -- describe what feature the camera has
            9. (Trajectory) trajectory                  -- only used for RAIL camera

     """

    def __init__(self, id=None, xc=None, yc=None, alpha=None, beta=None, field_depth=None, type=None, color=None):
        CameraRepresentation.__init__(self, id, xc, yc, alpha, beta, field_depth, color)
        self.camera_type = type
        self.trajectory = TrajectoryPlaner([])

    def init_from_camera(self, camera):
        super().init_from_camera(camera)
        self.camera_type = camera.camera_type
        self.trajectory = TrajectoryPlaner(camera.trajectory.trajectory)

class MobileCamera(Camera, MobileCameraRepresentation):
    """
            Class MobileCameraRepresentation.

            Description :
            :param


            :attibutes

    """

    def __init__(self, id=None, xc=None, yc=None, alpha=None, beta=None, trajectory=None, field_depth=None, color=None,
                 t_add=None, t_del=None, type=None, vx_vy_min=None, vx_vy_max=None, v_alpha_min=None, v_alpha_max=None,
                 delta_beta=None, v_beta_min=None, v_beta_max=None):

        Camera.__init__(self, id, xc, yc, alpha, beta, field_depth, color, t_add, t_del)
        camera_attributes_not_to_txt = self.attributes_not_to_txt
        MobileCameraRepresentation.__init__(self, id, xc, yc, alpha, beta, field_depth, type, color)
        self.attributes_not_to_txt += [elem for elem in camera_attributes_not_to_txt if
                                       elem not in self.attributes_not_to_txt]
        self.attributes_not_to_txt += ["coeff_field", "coeff_std_position", "coeff_std_speed", "coeff_std_acc",
                                       "swipe_angle_direction", "swipe_delta_alpha", "last_swipe_direction_change",
                                       "dt_next_swipe_direction_change", "last_swipe_configuration",
                                       "last_swipe_position_change","beta_min","beta_max"]

        """Limit the variation"""
        self.vx_vy_min = vx_vy_min
        self.vx_vy_max = vx_vy_max
        self.v_alpha_min = v_alpha_min
        self.v_alpha_max = v_alpha_max
        self.v_beta_min = v_beta_min
        self.v_beta_max = v_beta_max
        self.delta_beta = delta_beta


        """Zoom"""
        self.coeff_field = constants.COEFF_VARIATION_FROM_FIELD_DEPTH
        self.coeff_std_position = constants.COEFF_STD_VARIATION_MEASURMENT_ERROR_POSITION
        self.coeff_std_speed = constants.COEFF_STD_VARIATION_MEASURMENT_ERROR_SPEED
        self.coeff_std_acc = constants.COEFF_STD_VARIATION_MEASURMENT_ERROR_ACCELERATION

        """Trajectory"""
        self.trajectory = TrajectoryPlaner(trajectory)

        """Variables for the swipe"""
        self.swipe_angle_direction = 1
        self.swipe_delta_alpha = 0.2
        self.last_swipe_direction_change = constants.get_time()
        self.dt_next_swipe_direction_change = -10
        self.last_swipe_position_change = -10
        from src.multi_agent.tools.configuration import Configuration
        self.last_swipe_configuration = Configuration(None, None, random.uniform(0, constants.ROOM_DIMENSION_X),
                                                      random.uniform(0, constants.ROOM_DIMENSION_Y), 1, 1,
                                                      self.field_depth,
                                                      False)

        self.default_parameters()

    def default_parameters(self):
        """Default option"""
        if not self.camera_type == MobileCameraType.RAIL:
            self.trajectory = TrajectoryPlaner([])

        if self.camera_type == MobileCameraType.FIX or self.camera_type == MobileCameraType.ROTATIVE:
            self.vx_vy_min = 0
            self.vx_vy_max = 0
            if self.camera_type == MobileCameraType.FIX:
                self.v_alpha_min = 0
                self.v_alpha_max = 0

        if self.delta_beta is not None and self.beta is not None:
            self.beta_min = bound_angle_btw_minus_pi_plus_pi(self.beta - self.delta_beta)
            self.beta_max = bound_angle_btw_minus_pi_plus_pi(self.beta + self.delta_beta)
        else:
            self.beta_min = None
            self.beta_max = None


    def angle_degToRad(self):
        """
             :description
                  Transforms angle attribues to radians supposing it is in degree
        """
        super().angle_degToRad()
        if self.delta_beta is not None:
            self.delta_beta = math.radians(self.delta_beta)
        if self.beta_min is not None:
            self.beta_min = math.radians(self.beta_min)
        if self.beta_max is not None:
            self.beta_max = math.radians(self.beta_max)

        self.v_alpha_min = math.radians(self.v_alpha_min)
        self.v_alpha_max = math.radians(self.v_alpha_max)
        self.v_beta_min = math.radians(self.v_beta_min)
        self.v_beta_max = math.radians(self.v_beta_max)

    def angle_radToDeg(self):
        """
             :description
                   Transforms angle attribues to degrees supposing it is in radians
        """
        super().angle_radToDeg()
        if self.delta_beta is not None:
            self.delta_beta = math.degrees(self.delta_beta)
        if self.beta_min is not None:
            self.beta_min = math.degrees(self.beta_min)
        if self.beta_max is not None:
            self.beta_max = math.degrees(self.beta_max)

        self.v_alpha_min = math.degrees(self.v_alpha_min)
        self.v_alpha_max = math.degrees(self.v_alpha_max)
        self.v_beta_min = math.degrees(self.v_beta_min)
        self.v_beta_max = math.degrees(self.v_beta_max)

    def load_from_save_to_txt(self, s):
        """
            :description
                Load attributes for a txt string representation

            :param
                1. (string) s -- string description of the object, method save_to_txt.
        """
        super().load_from_save_to_txt(s)
        self.trajectory = TrajectoryPlaner(self.trajectory)
        self.default_parameters()



    def my_rand(self, bound):
        """
           :description
                Random function used in randomize

            :param
                1. ((int,int)) bound -- limit of the random variable that is created.
            :return
                1. (float) random value btw bound[0] and bound[1]
        """
        return random.uniform(bound[0], bound[1])

    def randomize(self, camera_type, beta_bound, delta_beta_bound, field_bound, v_xy_min_bound, v_xy_max_bound,
                  v_alpha_min_bound, v_alpha_max_bound, v_beta_min_bound, v_beta_max_bound):
        """
                   :description
                        Create a mobile camera  with random

                    :param
                        1.(MobileCameraType) camera_type               -- Camera type
                        2.((int,int))beta_bound - [degree]             -- random bound of beta
                        3.((int,int))delta_beta_bound - [degree]       -- random bound of delta_beta
                        4.((int,int))field_bound - [m]                 -- random bound of field_detph
                        5.((int,int))v_xx_min_bound -[m/s]             -- random bound of v_min in x and y axis
                        6.((int,int))v_xy_max_bound -[m/s]             -- random bound of v_max in x and y axis
                        7.((int,int))v_alpha_min_bound - [degree/s]    -- random bound of alpha min
                        8.((int,int))v_alpha_max_bound - [degree/s]    -- random bound of alpha max
                        9.((int,int))v_beta_min_bound - [degree/s]     -- random bound of beta min
                        10((int,int))v_beta_ùax_bound - [degree/s]     -- random bound of beta max

                    :return
                        set severals attributes to random values bounded btw parameters
        """
        self.xc = self.my_rand((0, constants.ROOM_DIMENSION_X))
        self.yc = self.my_rand((0, constants.ROOM_DIMENSION_Y))
        self.alpha = bound_angle_btw_minus_pi_plus_pi(self.my_rand((-math.pi, math.pi)))
        self.beta = self.my_rand(beta_bound)
        self.delta_beta = self.my_rand(delta_beta_bound)
        self.field_depth = self.my_rand(field_bound)

        self.t_add = [0]
        self.t_del = [1000]

        self.vx_vy_min = self.my_rand(v_xy_min_bound)
        self.vx_vy_max = self.my_rand(v_xy_max_bound)

        self.v_alpha_min = self.my_rand(v_alpha_min_bound)
        self.v_alpha_max = self.my_rand(v_alpha_max_bound)
        self.v_beta_min = self.my_rand(v_beta_min_bound)
        self.v_beta_max = self.my_rand(v_beta_max_bound)

        self.trajectory = TrajectoryPlaner([])
        self.camera_type = camera_type

        """Default values"""
        self.set_default_values(xc=self.xc, yc=self.yc, alpha=self.alpha, beta=self.beta, field_depth=self.field_depth)
        self.beta_min = self.beta - self.delta_beta
        self.beta_max = self.beta + self.delta_beta
        self.angle_degToRad()

    def compute_field_depth_variation_for_a_new_beta(self, new_beta):
        """
            :description
                the field depth is inversaly propotional to beta

            :param
               1. (float) new_beta - [radians]        -- new angle from the camera

            :return
                1. (float) field_depth - [m]          -- field depth corresponding to the new beta
        """
        delta = new_beta - self.beta
        field_depth = self.field_depth - delta * self.coeff_field
        field_depth = bound(field_depth, constants.AGENT_CAMERA_FIELD_MIN * self.default_field_depth,
                            constants.AGENT_CAMERA_FIELD_MAX * self.default_field_depth)
        return field_depth

    def zoom(self, speed, dt):
        """
           :description
                Modelize the zoom of a camera (modifies beta and field_depth)

                effects :
                    zoom in / zoom out
                    1) on the field geometry:
                         a. Increase/decrease beta
                         b. Decrease/increase the field depth

                    2) on the precision
                         c. Decrease/increase the std on the measure

                    self.coeff_speed  -- value > 0, defines the proportionality btw a. and b.
                    self.coeff_std   -- value > 0, defines the proportionality btw a. and c.

           :param
               1. (float) speed        -- going from -1 to 1, + to zoom out - to zoom
               2. (float) dt           -- time
        """

        sign = np.sign(speed)

        if self.beta_min <= self.beta <= self.beta_max:
            if speed == 0:
                delta = 0
            else:
                delta = sign * dt * (self.v_beta_min + math.fabs(speed) * (self.v_beta_max - self.v_beta_min))

        elif self.beta < self.beta_min or self.beta_max > 0:
            self.beta = bound(self.beta, self.beta_min, self.beta_max)
            delta = 0
        else:
            delta = 0
            print("problem in beta target")

        self.field_depth = self.compute_field_depth_variation_for_a_new_beta(self.beta + delta)
        self.beta += delta

        if constants.ERROR_VARIATION_ZOOM:
            self.std_measurement_error_position -= delta * self.coeff_std_position
            self.std_measurement_error_speed -= delta * self.coeff_std_speed
            self.std_measurement_error_acceleration -= delta * self.coeff_std_acc

            self.std_measurement_error_position = bound(self.std_measurement_error_position, 0,
                                                        self.std_measurement_error_position * 10)
            self.std_measurement_error_speed = bound(self.std_measurement_error_speed, 0,
                                                     self.std_measurement_error_speed * 10)
            self.std_measurement_error_acceleration = bound(self.std_measurement_error_acceleration, 0,
                                                            self.std_measurement_error_acceleration * 10)

    def rotate(self, speed, dt):
        """
           :description
               Rotate the camera in the room '(modifies angle alpha)

           :param
               1. (float) speed        -- going from -1 to 1
               2. (float) dt           -- time
        """

        if not self.camera_type == MobileCameraType.FIX:
            sign = np.sign(speed)
            if speed == 0:
                delta = 0
            else:
                delta = sign * dt * (self.v_alpha_min + math.fabs(speed) * (self.v_alpha_max - self.v_alpha_min))

            self.alpha += delta
            self.alpha = bound_angle_btw_minus_pi_plus_pi(self.alpha)

    def move(self, speed_x, speed_y, dt):
        """
             :description
                 Move the camera in the room (modifies xc and yc)

             :param
                 1. (float) speed_x        -- going from -1 to 1
                 1. (float) speed_y        -- going from -1 to 1
                 2. (float) dt             -- time
          """

        sign_x = np.sign(speed_x)
        sign_y = np.sign(speed_y)

        if speed_x == 0:
            delta_x = 0
        else:
            delta_x = sign_x * dt * (self.vx_vy_min + math.fabs(speed_x) * (self.vx_vy_max - self.vx_vy_min))

        if speed_y == 0:
            delta_y = 0
        else:
            delta_y = sign_y * dt * (self.vx_vy_min + math.fabs(speed_y) * (self.vx_vy_max - self.vx_vy_min))

        if self.camera_type == MobileCameraType.RAIL:
            "On the rail it is only 1 dimension"
            delta = delta_x
            x_new, y_new = self.trajectory.move_on_trajectory(self.xc, self.yc, delta)
            self.xc = x_new
            self.yc = y_new
        elif self.camera_type == MobileCameraType.FREE:
            self.xc += delta_x
            self.yc += delta_y

        self.xc = bound(self.xc, self.xc_min, self.xc_max)
        self.yc = bound(self.yc, self.yc_min, self.yc_max)

    def set_configuration(self, configuration):
        """
            :description
               Set the parameters thanks to a configuration
            :param
                1. (Configuration) configuration       --  group several parameters

        """
        self.xc = configuration.x
        self.yc = configuration.y
        self.alpha = configuration.alpha
        self.beta = configuration.beta
        self.field_depth = configuration.field_depth

    def get_edge_points_world_frame(self):
        """
              :description
                 #TODO - petite description

        """
        # angles of edge of field of view in cam frame
        angle_min, angle_max = -self.beta / 2, self.beta / 2
        # distance of depth field along these angles
        min_edge = (self.field_depth * math.cos(angle_min), self.field_depth * math.sin(angle_min))
        max_edge = (self.field_depth * math.sin(angle_max), self.field_depth * math.sin(angle_max))
        min_edge_world_frame = self.coordinate_change_from_camera_frame_to_world_frame(min_edge[0], min_edge[1])
        max_edge_world_frame = self.coordinate_change_from_camera_frame_to_world_frame(max_edge[0], max_edge[1])
        return min_edge_world_frame, max_edge_world_frame


class TrajectoryPlaner:
    """
           Class TrajectoryPlaner.

           Description :
                This class modelize the displacement from a camrea on a rail.

           :param
               1. (list[(float,float)]) trajectory - [m]       --  List that contains the via points

           :attibutes
               1. (list[(float,float)]) trajectory - [m]       -- List that contains the via points
               2. (int) trajectory_index                       -- Current segment of the trajectory
               3. (float) distance - [m]                       -- Distance travelled by the camera on the rail
                                                                  (going forward increase the distance, going
                                                                    backwards decrease the distance => [0,length])

    """

    def __init__(self, trajectory):
        self.trajectory = trajectory
        self.trajectory_index = 0
        self.distance = 0

    def move_on_trajectory(self, x, y, delta):
        """
                 :description
                     x,y belong to the trajectory !!

                 :param
                     1. (float) x - [m]         -- x coordinate of the point in world frame
                     2. (float) y - [m]         -- y coordinate of the point in world frame
                     3. (float) delta - [m]     -- distance to travel

                :return
                    1. (float) x - [m]         -- x moved new coordinate of the point in world frame
                    2. (float) y - [m]         -- y moved new coordinate of the point in world frame
        """

        if len(self.trajectory) > 1:
            (xi, yi) = self.trajectory[self.trajectory_index]
            (xf, yf) = self.trajectory[self.trajectory_index + 1]

            (x_trajectory_frame, y_trajectory_frame) = self.from_world_frame_to_trajectory_frame(x, y)
            (xf_trajectory_frame, yf_trajectory_frame) = self.from_world_frame_to_trajectory_frame(xf, yf)

            """Check to make the transformatio is ok, y shoud be 0 a the frame is place on the x axis"""
            if y_trajectory_frame > 0.0001:
                print("problème in move_on_trajectory y = %.2f", y_trajectory_frame)

            "Variation"
            self.distance += delta
            x_trajectory_frame += delta

            if x_trajectory_frame > xf_trajectory_frame:
                "On the next segment"
                if self.trajectory_index < len(self.trajectory) - 2:
                    "Changing to next segment"
                    self.trajectory_index += 1
                    delta_new = (x_trajectory_frame - xf_trajectory_frame)
                    return self.move_on_trajectory(xf, yf, delta_new)
                else:
                    "Reaching the end point"
                    (self.distance, y) = self.compute_distance_for_point_x_y(xf, yf, self.trajectory_index)
                    return (xf, yf)

            elif x_trajectory_frame < 0:
                "On the previous segment"
                if self.trajectory_index > 0:
                    "Changing to previous segment"
                    self.trajectory_index -= 1
                    delta_new = x_trajectory_frame
                    return self.move_on_trajectory(xi, yi, delta_new)
                else:
                    "Reaching start point"
                    self.distance = 0
                    return (xi, yi)
            else:
                "The delta is on the same segment"
                return self.from_trajectory_frame_to_world_frame(x_trajectory_frame, y_trajectory_frame)
        else:
            return x, y

    def find_all_intersection(self, line):
        all_possible_intersection = []
        for index in range(len(self.trajectory) - 1):
            (xi, yi) = self.trajectory[index]
            (xf, yf) = self.trajectory[index + 1]

            segment = Line(xi, yi, xf, yf)
            x_intersection, y_intersection = segment.find_intersection_btw_two_line(line)

            x_intersection_in_trajecotry_frame, y_intersection_in_trajectory_frame = self.from_world_frame_to_trajectory_frame_for_a_given_segment(
                x_intersection, y_intersection, index)
            xf_in_trajectory_frame, yf_in_trajectory_frame = self.from_world_frame_to_trajectory_frame_for_a_given_segment(
                xf, yf, index)

            if y_intersection_in_trajectory_frame > 0.001:
                print(y_intersection)
                print("problème")

            elif 0 < x_intersection_in_trajecotry_frame < xf_in_trajectory_frame:
                all_possible_intersection.append((x_intersection, y_intersection, index))

        return all_possible_intersection

    def find_closest_intersection(self, line, index):
        if index < 0:
            return (0, 0, 0)
        elif index >= len(self.trajectory) - 1:
            return (self.trajectory[-1][0], self.trajectory[-1][1], len(self.trajectory) - 1)
        else:
            (xi, yi) = self.trajectory[index]
            (xf, yf) = self.trajectory[index + 1]
            segment = Line(xi, yi, xf, yf)
            x_intersection, y_intersection = segment.find_intersection_btw_two_line(line)

            x_intersection_in_trajecotry_frame, y_intersection_in_trajectory_frame = self.from_world_frame_to_trajectory_frame_for_a_given_segment(
                x_intersection, y_intersection, index)
            xf_in_trajectory_frame, yf_in_trajectory_frame = self.from_world_frame_to_trajectory_frame_for_a_given_segment(
                xf, yf, index)

            if y_intersection_in_trajectory_frame > 0.001:
                print("problème  in find closest intersection")
                return (None, None, None)
            elif x_intersection_in_trajecotry_frame > xf_in_trajectory_frame or x_intersection is None:
                return self.find_closest_intersection(line, index + 1)
            elif x_intersection_in_trajecotry_frame < xi:
                return self.find_closest_intersection(line, index - 1)
            else:
                return (x_intersection, y_intersection, index)

    def get_angle(self):
        (xi, yi) = self.trajectory[self.trajectory_index]
        (xf, yf) = self.trajectory[self.trajectory_index + 1]
        return math.atan2(yf - yi, xf - xi)

    def rotate_angle(self, angle, x, y):
        x_rotate = math.cos(angle) * x + math.sin(angle) * y
        y_rotate = -math.sin(angle) * x + math.cos(angle) * y
        return (x_rotate, y_rotate)

    def from_world_frame_to_trajectory_frame(self, x, y):
        (xi, yi) = self.trajectory[self.trajectory_index]
        angle = self.get_angle()
        x_no_offset = x - xi
        y_no_offset = y - yi
        return self.rotate_angle(angle, x_no_offset, y_no_offset)

    def compute_distance_for_point_x_y(self, x, y, i_index):
        sum = 0
        for n in range(i_index):
            (xi, yi) = self.trajectory[n]
            (xf, yf) = self.trajectory[n + 1]
            d = distance_btw_two_point(xi, yi, xf, yf)
            sum += d

        (xi, yi) = self.trajectory[i_index]
        d = distance_btw_two_point(xi, yi, x, y)
        sum += d
        return sum, 0

    def from_world_frame_to_trajectory_frame_for_a_given_segment(self, x, y, index):
        (xi, yi) = self.trajectory[index]
        (xf, yf) = self.trajectory[self.trajectory_index + 1]
        angle = math.atan2(yf - yi, xf - xi)
        x_no_offset = x - xi
        y_no_offset = y - yi
        return self.rotate_angle(angle, x_no_offset, y_no_offset)

    def from_trajectory_frame_to_world_frame(self, x, y):
        (xi, yi) = self.trajectory[self.trajectory_index]
        angle = self.get_angle()
        (x_rotate, y_rotate) = self.rotate_angle(-angle, x, y)
        return (x_rotate + xi, y_rotate + yi)

    def __str__(self):
        return str(self.trajectory)


if __name__ == "__main__":
    camera = MobileCameraRepresentation(0, 1, 1, 1, 1, 5, MobileCameraType.FIX, TrajectoryPlaner([]))
    print(camera.attributes_to_string())
    print(camera.save_to_txt())

    camera = MobileCamera(delta_beta=20)
    print(camera.attributes_to_string())
    s = camera.save_to_txt()
    print(s)
