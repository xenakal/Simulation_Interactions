import re
import math
import numpy as np
from src.multi_agent.elements.camera import Camera, CameraRepresentation


class MobileCameraType:
    FIX = 0
    ROTATIVE = 1
    RAIL = 2
    FREE = 3


class MobileCameraRepresentation(CameraRepresentation):
    def __init__(self,room,id, xc, yc, alpha, beta, d_max, type):
        super().__init__(room,id, xc, yc, alpha, beta, d_max)
        super().__init__(room,id, xc, yc, alpha, beta, d_max)
        self.camera_type = type
        self.trajectory = TrajectoryPlaner([])


    def init_from_camera(self, camera):
        super().init_from_camera(camera)
        self.camera_type = camera.camera_type
        new_trajectory = TrajectoryPlaner([])
        new_trajectory.trajectory = camera.trajectory.trajectory
        self.trajectory = new_trajectory

    def init_from_values_extend(self,id,signature,xc,yc,alpha,beta,field_depth,error_pos,error_speed,error_acc,color,room,is_active,camera_type,trajectory):
        super().init_from_values(id,signature,xc,yc,alpha,beta,field_depth,error_pos,error_speed,error_acc,color,room,is_active)
        self.camera_type = camera_type
        self.trajectory = trajectory



class MobileCamera(Camera,MobileCameraRepresentation):
    def __init__(self, room, id, xc, yc, alpha, beta, trajectory, d_max, color=0, t_add=-1, t_del=-1,
                 type=MobileCameraType.RAIL, vx_vy_min=0, vx_vy_max=1, v_alpha_min=0, v_alpha_max=1,
                 delta_beta=55, v_beta_min=0, v_beta_max=1):

        super().__init__(room,id, xc, yc, alpha, beta, d_max, color,t_add,t_del)
        self.camera_type = type
        "Limit the variation"
        self.vx_vy_min = vx_vy_min
        self.vx_vy_max = vx_vy_max
        self.v_alpha_min = v_alpha_min
        self.v_alpha_max = v_alpha_max
        "Zoom"
        self.delta_beta = math.radians(delta_beta)
        self.beta_min = self.beta - self.delta_beta
        self.beta_max = self.beta + self.delta_beta

        self.v_beta_min = v_beta_min
        self.v_beta_max = v_beta_max
        self.coeff_field = 2
        self.coeff_std_position = 0.05 * self.std_measurment_error_position
        self.coeff_std_speed = 0.01 * self.std_measurment_error_speed
        self.coeff_std_acc = 0.1 * self.std_measurment_error_acceleration


        self.trajectory = TrajectoryPlaner(trajectory)

        """Default option"""
        if not self.camera_type == MobileCameraType.RAIL:
            self.trajectory = TrajectoryPlaner([])

        if self.camera_type == MobileCameraType.FIX or self.camera_type == MobileCameraType.ROTATIVE:
            self.vx_vy_min = 0
            self.vx_vy_max = 0
            if self.camera_type == MobileCameraType.FIX:
                self.v_alpha_min = 0
                self.v_alpha_max = 0

    def save_target_to_txt(self):
        s0 = "x:%0.2f y:%0.2f alpha:%0.2f beta:%0.2f field_depth:%0.2f" % (
            self.xc, self.yc, math.degrees(self.alpha), math.degrees(self.beta), self.field_depth)
        s1 = " t_add:" + str(self.t_add) + " t_del:" + str(self.t_del)
        s2 = " vx_vy_min:%.02f vx_vy_max:%.02f" % (self.vx_vy_min, self.vx_vy_max)
        s3 = " v_alpha_min:%.02f v_alpha_max:%.02f" % (self.v_alpha_min, self.v_alpha_max)
        s4 = " v_beta_min:%.02f v_beta_max:%.02f" % (self.v_beta_min, self.v_beta_max)
        s5 = " traj: " + str(self.trajectory.trajectory)
        return s0 + s1 + s2 + s3 + s4 + s5 + "\n"

    def load_from_txt(self, s):
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        attribute = re.split(
            "x:|y:|alpha:|beta:|field_depth:|t_add:|t_del:|vx_vy_min:|vx_vy_max:|v_alpha_min:|v_alpha_max:|v_beta_min:|v_beta_max:|traj:",
            s)

        self.xc = float(attribute[1])
        self.yc = float(attribute[2])
        self.alpha = math.radians(float(attribute[3]))
        self.beta = math.radians(float(attribute[4]))
        self.field_depth = float(attribute[5])
        self.t_add = self.load_tadd_tdel(attribute[6])
        self.t_del = self.load_tadd_tdel(attribute[7])
        self.vx_vy_min = float(attribute[8])
        self.vx_vy_max = float(attribute[9])
        self.v_alpha_min = float(attribute[10])
        self.v_alpha_max = float(attribute[11])
        self.v_beta_min = float(attribute[12])
        self.v_beta_max = float(attribute[13])
        self.trajectory = TrajectoryPlaner([])

        self.trajectory.load_trajcetory(attribute[14])
        self.beta_min = self.beta - self.delta_beta
        self.beta_max = self.beta + self.delta_beta

    def zoom(self, speed, dt):
        """
           :description
                Modelize the zoom of a camera

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
            delta = sign * dt * (self.v_beta_min + math.fabs(speed) * (self.v_beta_max - self.v_beta_min))
        else:
            delta = 0

        self.beta += delta
        self.field_depth -= delta * self.coeff_field
        self.std_measurment_error_position -= delta * self.coeff_std_position
        self.std_measurment_error_speed -= delta * self.coeff_std_speed
        self.std_measurment_error_acceleration -= delta * self.coeff_std_acc

    def rotate(self, speed, dt):
        """
           :description
               Rotate the camera in the room

           :param
               1. (float) speed        -- going from -1 to 1
               2. (float) dt           -- time
        """

        if not self.camera_type == MobileCameraType.FIX:
            sign = np.sign(speed)
            delta = sign * dt * (self.v_alpha_min + math.fabs(speed) * (self.v_alpha_max - self.v_alpha_min))
            self.alpha += delta

    def move(self, speed_x, speed_y, dt):
        """
             :description
                 Rotate the camera in the room

             :param
                 1. (float) speed_x        -- going from -1 to 1
                 1. (float) speed_y        -- going from -1 to 1
                 2. (float) dt             -- time
          """

        sign_x = np.sign(speed_x)
        sign_y = np.sign(speed_y)
        delta_x = sign_x * dt * (self.vx_vy_min + math.fabs(speed_x) * (self.vx_vy_max - self.vx_vy_min))
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


class TrajectoryPlaner:
    def __init__(self, trajectory):
        self.trajectory = trajectory
        self.trajectory_index = 0
        self.sum_delta = 0

    def load_trajcetory(self, s):
        list = []
        s = s[2:-2]
        if not s == "":
            all_trajectories = re.split("\),\(", s)
            for trajectory in all_trajectories:
                xy = re.split(",", trajectory)
                if not xy == "":
                    list.append((float(xy[0]), float(xy[1])))

        self.trajectory = list

    def move_on_trajectory(self, x, y, delta):
        if len(self.trajectory) > 1:
            (xi, yi) = self.trajectory[self.trajectory_index]
            (xf, yf) = self.trajectory[self.trajectory_index + 1]
            (x_trajectory_frame, y_trajectory_frame) = self.from_world_frame_to_trajectory_frame(x, y)
            (xf_trajectory_frame, yf_trajectory_frame) = self.from_world_frame_to_trajectory_frame(xf, yf)

            "Variation"
            self.sum_delta += delta
            x_trajectory_frame += delta
            if y_trajectory_frame > 0.000001:
                print("problème in move_on_trajectory y = %.2f", y_trajectory_frame)

            if x_trajectory_frame > xf_trajectory_frame:
                "On the next segment"
                if self.trajectory_index < len(self.trajectory) - 2:
                    "Changing to next segment"
                    self.trajectory_index += 1
                    delta_new = (x_trajectory_frame - xf_trajectory_frame)
                    return self.move_on_trajectory(xf, yf, delta_new)
                else:
                    "Reaching the end point"
                    return self.from_trajectory_frame_to_world_frame(xf_trajectory_frame, yf_trajectory_frame)

            elif x_trajectory_frame < 0:
                "On the previous segment"
                if self.trajectory_index > 0:
                    "Changing to previous segment"
                    self.trajectory_index -= 1
                    delta_new = x_trajectory_frame
                    return self.move_on_trajectory(xi, yi, delta_new)
                else:
                    "Reaching start point"
                    return self.from_trajectory_frame_to_world_frame(0, 0)

            else:
                return self.from_trajectory_frame_to_world_frame(x_trajectory_frame, y_trajectory_frame)
        else:
            return x, y

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

    def from_trajectory_frame_to_world_frame(self, x, y):
        (xi, yi) = self.trajectory[self.trajectory_index]
        angle = self.get_angle()
        (x_rotate, y_rotate) = self.rotate_angle(-angle, x, y)
        return (x_rotate + xi, y_rotate + yi)
