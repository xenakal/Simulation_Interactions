import math
import numpy as np
from scipy.interpolate import griddata
import src.multi_agent.elements.camera as cam
from src import constants
from src.multi_agent.tools.potential_field_method import plot_potential_field_dynamic, compute_potential_gradient, \
    convert_target_list_to_potential_field_input, compute_potential_field_cam


def bound(val, val_min, val_max):
    val = min(val, val_max)
    val = max(val, val_min)
    return val


def check_configuration_all_target_are_seen(camera, room_representation):

    # check if this configuration covers all targets
    for targetRepresentation in room_representation.active_Target_list:
        in_field = cam.is_x_y_radius_in_field_not_obstructed(camera, targetRepresentation.xc,
                                                             targetRepresentation.yc,
                                                             targetRepresentation.radius)

        hidden = cam.is_x_y_in_hidden_zone_all_targets_based_on_camera(room_representation,
                                                                       camera,
                                                                       targetRepresentation.xc,
                                                                       targetRepresentation.yc)
        if hidden or not in_field:
            return False

    return True


class VariationOnConfiguration:
    Small_region = 0
    All_map = 1


class ValidConfigurationCriterion:
    ALL_TARGET_SEEN = True
    MAP_SCORE = True


class Configuration:
    def __init__(self, xt, yt, x, y, alpha, beta, field_depth, virtual):
        self.configuration_score = None
        self.virtual = virtual
        self.is_valid = True
        """Parameter fro the target"""
        self.xt = xt
        self.yt = yt
        self.track_target_list = []

        """Parameter from the cam"""
        self.x = x
        self.y = y
        self.alpha = alpha
        self.beta = beta
        self.field_depth = field_depth
        self.vector_field_x = None
        self.vector_field_y = None

    def is_configuration_valid(self,camera=None,room_representation=None,score_map_min = None):
        target_all_seen = True
        score_map = True

        if ValidConfigurationCriterion.ALL_TARGET_SEEN:
            target_all_seen = check_configuration_all_target_are_seen(camera,room_representation)

        if ValidConfigurationCriterion.MAP_SCORE:
            score_map = (self.configuration_score >= score_map_min)
        return target_all_seen and score_map

    def compute_configuration_score(self):
        score = None
        if self.track_target_list is not None:
            score = 0
            for target in self.track_target_list:
                (x_in_cam_frame, y_in_cam_frame) = self.coordinate_change_from_world_frame_to_camera_frame(target.xc,
                                                                                                           target.yc)
                X, Y, target_score = compute_potential_field_cam(x_in_cam_frame, y_in_cam_frame,
                                                                 len(self.track_target_list), self.beta,
                                                                 self.field_depth)
                score += target_score[0][0]
        self.configuration_score = score

    def compute_target_score(self, target_id):
        target = self.find_target_by_id(target_id)
        if target is None:
            return 0
        (x_in_cam_frame, y_in_cam_frame) = self.coordinate_change_from_world_frame_to_camera_frame(target.xc,
                                                                                                   target.yc)
        _, _, target_score = compute_potential_field_cam(x_in_cam_frame, y_in_cam_frame, len(self.track_target_list),
                                                         self.beta, self.field_depth)
        return target_score[0][0]

    def compute_vector_field_for_current_position(self, camera_xc, camera_yc):
        if self.track_target_list is not None:
            list_objectives = [(self.x, self.y, 0)]
            self.vector_field_x, self.vector_field_y = \
                compute_potential_gradient(camera_xc, camera_yc, list_objectives,
                                           convert_target_list_to_potential_field_input(self.track_target_list))
        else:
            print("The target list is none")

    def variation_on_configuration_found(self, camera, region=VariationOnConfiguration.Small_region):

        if self.track_target_list == []:
            return self

        new_configurations = []

        distance = 0.25
        n = 3
        n_interp = 5

        if region == VariationOnConfiguration.Small_region:
            x = np.linspace(self.x - distance, self.x + distance, n)
            y = np.linspace(self.y - distance, self.y + distance, n)
        elif region == VariationOnConfiguration.All_map:
            x = np.linspace(0, 8, n)
            y = np.linspace(0, 8, n)

        X_2D, Y_2D = np.meshgrid(x, y)
        X_1D = np.ravel(X_2D)
        Y_1D = np.ravel(Y_2D)

        all_alpha, all_beta, all_field_depth = self.evaluate_alpha_beta_field_depth(X_1D, Y_1D, camera)
        for x, y, alpha, beta, field_depth in zip(X_1D, Y_1D, all_alpha, all_beta, all_field_depth):
            new_configuration = Configuration(self.xt, self.yt, x, y, alpha, beta, field_depth, self.virtual)
            new_configuration.track_target_list = self.track_target_list
            new_configuration.compute_configuration_score()
            new_configurations.append(new_configuration)

        new_configurations_1D_score = [new_configuration.configuration_score for new_configuration in
                                       new_configurations]
        points = [(new_configuration.x, new_configuration.y) for new_configuration in new_configurations]

        if region == VariationOnConfiguration.Small_region:
            x = np.linspace(self.x - distance, self.x + distance, n_interp)
            y = np.linspace(self.y - distance, self.y + distance, n_interp)
        elif region == VariationOnConfiguration.All_map:
            x = np.linspace(0, 8, n_interp)
            y = np.linspace(0, 8, n_interp)

        X_2D_interp, Y_2D_interp = np.meshgrid(x, y)
        # method can be changed to cubic or linear or nearest
        interpolation = griddata(points, np.array(new_configurations_1D_score), (X_2D_interp, Y_2D_interp),
                                 method='cubic')

        plot_potential_field_dynamic(X_2D_interp, Y_2D_interp, interpolation)

        # find the configuration associated with the maximal value of the interpolation
        arg_max = np.argmax(interpolation)
        x_optimal = np.ravel(X_2D_interp)[arg_max]
        y_optimal = np.ravel(Y_2D_interp)[arg_max]
        alpha_optimal, beta_optimal, field_optimal = self.evaluate_alpha_beta_field_depth(x_optimal, y_optimal, camera)
        optimal_config = Configuration(self.xt, self.yt, x_optimal, y_optimal, alpha_optimal, beta_optimal,
                                       field_optimal, True)
        optimal_config.track_target_list = self.track_target_list
        return optimal_config

    def bound_to_camera_limitation(self, camera):
        self.x = bound(self.x, camera.xc_min, camera.xc_max)
        self.y = bound(self.y, camera.yc_min, camera.yc_max)
        self.beta = bound(self.beta, camera.beta_min, camera.beta_max)

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
        x_no_offset = x_in_room_frame - self.x
        y_no_offset = y_in_room_frame - self.y

        x_in_camera_frame = math.cos(self.alpha) * x_no_offset + math.sin(self.alpha) * y_no_offset
        y_in_camera_frame = -math.sin(self.alpha) * x_no_offset + math.cos(self.alpha) * y_no_offset
        return x_in_camera_frame, y_in_camera_frame

    def find_target_by_id(self, target_id):
        for target in self.track_target_list:
            if target.id == target_id:
                return target
        return None

    def evaluate_alpha_beta_field_depth(self, Xc, Yc, camera):
        delta_x = self.xt - Xc
        delta_y = self.yt - Yc
        all_alpha = np.arctan2(delta_y, delta_x)

        y_radius = self.field_depth * np.tan(self.beta)
        distance_to_target = np.sqrt(np.square(Xc) + np.square(Yc))
        all_beta = np.fabs(np.arctan2(y_radius, distance_to_target))

        delta = all_beta - self.beta
        all_field_depth = self.field_depth - delta * camera.coeff_field
        if isinstance(all_field_depth, float):
            field_depth = camera.bound(all_field_depth, constants.AGENT_CAMERA_FIELD_MIN * camera.default_field_depth,
                                       constants.AGENT_CAMERA_FIELD_MAX * camera.default_field_depth)
        else:
            for field_depth in all_field_depth:
                field_depth = camera.bound(field_depth, constants.AGENT_CAMERA_FIELD_MIN * camera.default_field_depth,
                                           constants.AGENT_CAMERA_FIELD_MAX * camera.default_field_depth)

        return all_alpha, all_beta, all_field_depth

    def to_string(self):
        print("config x: %.02f y: %.02f alpha: %.02f beta: %.02f" % (self.x, self.y, self.alpha, self.beta))
