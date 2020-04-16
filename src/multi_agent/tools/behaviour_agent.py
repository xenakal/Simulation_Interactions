import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
import random
from sklearn.decomposition import PCA

import src.multi_agent.elements.mobile_camera as mobileCam
from src import constants
from src.multi_agent.elements.target import TargetType
from src.my_utils.my_math.line import Line, distance_btw_two_point
from src.my_utils.my_math.potential_field_method import compute_potential_gradient, \
    convert_target_list_to_potential_field_input


class Angle_configuration:
    PARALLEL_TO_COMPUTED_DIRECTION = 0
    PERPENDICULAR_TO_COMPUTED_DIRECTION = 1
    AUTO = 2


class PCA_track_points_possibilites:
    MEANS_POINTS = "mean points"
    MEDIAN_POINTS = "median points"


def born(val, val_min, val_max):
    val = min(val, val_max)
    val = max(val, val_min)
    return val


class Configuration:
    def __init__(self, x, y, alpha, beta, virtual):
        self.x = x
        self.y = y
        self.alpha = alpha
        self.beta = beta
        self.virtual = virtual
        self.track_target_list = []
        self.vector_field_x = None
        self.vector_field_y = None

    def compute_vector_field_for_current_position(self, camera_xc, camera_yc, ):
        if not self.track_target_list is None:
            list_objectives = [(self.x, self.y, 0)]
            self.vector_field_x, self.vector_field_y = compute_potential_gradient(camera_xc, camera_yc, list_objectives,
                                                                                  convert_target_list_to_potential_field_input(
                                                                                      self.track_target_list))
            # self.vector_field_x, self.vector_field_y = compute_potential_gradient(camera_xc, camera_yc, list_objectives,self.track_target_list)
        else:
            print("The target list is none")

    def born_to_camera_limitation(self, camera):
        self.x = born(self.x, camera.xc_min, camera.xc_max)
        self.y = born(self.y, camera.yc_min, camera.yc_max)
        self.beta = born(self.beta, camera.beta_min, camera.beta_max)

    def to_string(self):
        print("config x: %.02f y: %.02f alpha: %.02f beta: %.02f" % (self.x, self.y, self.alpha, self.beta))


def get_configuration_based_on_seen_target(camera, target_representation_list,
                                           point_to_track_choice=PCA_track_points_possibilites.MEDIAN_POINTS,
                                           memory_objectives=None,
                                           memory_point_to_reach=None, virtual=False):
    """Default values"""
    xt = camera.xc
    yt = camera.yc
    alpha = camera.alpha
    beta = camera.beta
    angle_in_room_representation = 0

    distance_to_keep_to_target = camera.field_depth * constants.DISTANCE_TO_KEEP_FROM_TARGET
    y_to_compute_beta = 0

    point_to_be_close_x = camera.xc
    point_to_be_close_y = camera.yc

    placement_choice = None
    number_of_target = len(target_representation_list)

    if number_of_target < 0:
        """Should not append"""
        return (xt, yt, alpha, beta)

    if number_of_target == 1:
        "In this case PCA is not possible, we chose to focus on the target itself"
        target = target_representation_list[0]
        xt = target.xc
        yt = target.yc

        delta_y = camera.xc - yt
        delta_x = camera.yc - xt

        if target.type == TargetType.FIX or target.type == TargetType.SET_FIX:
            angle_in_room_representation = camera.alpha
        else:
            angle_in_room_representation = math.atan(delta_y / delta_x)

        y_to_compute_beta = target.radius
        placement_choice = Angle_configuration.PARALLEL_TO_COMPUTED_DIRECTION

    if number_of_target >= 2:
        "Principle Component Analysis"
        xt, yt, angle_in_room_representation, y_to_compute_beta, variance_min_ratio = get_angle_alpha_beta_PCA_method(
            target_representation_list,
            point_to_track_choice)
        placement_choice = Angle_configuration.PERPENDICULAR_TO_COMPUTED_DIRECTION

        if number_of_target == 3:
            "We want to be closer from the 3rd target"
            distance_max = -1
            distance_max_and_ids = (-1, [-1, -1])

            for targets in itertools.combinations(target_representation_list, 2):
                target1, target2 = targets
                distance_to_compute = distance_btw_two_point(target1.xc, target1.yc, target2.xc, target2.yc)
                if distance_max < distance_to_compute:
                    distance_max = distance_to_compute
                    distance_max_and_ids = (distance_max, [target1.id, target2.id])

            for target in target_representation_list:
                if target.id not in distance_max_and_ids[1]:
                    point_to_be_close_x = 2 * xt - math.fabs(target.xc)
                    point_to_be_close_y = 2 * yt - math.fabs(target.yc)

    angle_in_room_representation = modify_angle(angle_in_room_representation, placement_choice)

    """Camera has to moove in a different way"""
    if camera.camera_type == mobileCam.MobileCameraType.FIX or \
            camera.camera_type == mobileCam.MobileCameraType.ROTATIVE:
        _, _, alpha = define_xc_yc_alpha(camera, xt, yt, distance_to_keep_to_target, angle_in_room_representation,
                                         memory_objectives, memory_point_to_reach, virtual)
        xc = camera.xc
        yc = camera.yc
    elif camera.camera_type == mobileCam.MobileCameraType.RAIL:
        xc, yc, alpha = define_xc_yc_alpha(camera, xt, yt, distance_to_keep_to_target, angle_in_room_representation,
                                           memory_objectives, memory_point_to_reach, virtual)

    elif camera.camera_type == mobileCam.MobileCameraType.FREE:
        xc1, yc1, alpha1 = define_xc_yc_alpha(camera, xt, yt, distance_to_keep_to_target, angle_in_room_representation,
                                              memory_objectives, memory_point_to_reach, virtual)
        xc2, yc2, alpha2 = define_xc_yc_alpha(camera, xt, yt, distance_to_keep_to_target,
                                              angle_in_room_representation + math.pi,
                                              memory_objectives, memory_point_to_reach, virtual)

        distance1 = distance_btw_two_point(xc1, yc1, point_to_be_close_x, point_to_be_close_y)
        distance2 = distance_btw_two_point(xc2, yc2, point_to_be_close_x, point_to_be_close_y)

        if distance1 < distance2:
            xc = xc1
            yc = yc1
            alpha = alpha1
        else:
            xc = xc2
            yc = yc2
            alpha = alpha2
        if not virtual:
            memory_point_to_reach.append([(xc, yc, 0), (point_to_be_close_x, point_to_be_close_y, 0)])
    else:
        xc = -1
        yc = -1
        print("camera_type not recognize")

    distance_to_target = distance_btw_two_point(camera.xc, camera.yc, xt, yt)
    """Same computation for the beta for every case"""
    beta = define_beta(distance_to_target, y_to_compute_beta)
    """Create a new configuration and make it match with the camera limitation"""
    configuration = Configuration(xc, yc, alpha, beta, virtual)
    configuration.born_to_camera_limitation(camera)
    return configuration


def define_xc_yc_alpha(camera, xt, yt, distance_to_keep_to_target, angle_in_room_coordinate, memory_objectives=None,
                       memory_point_to_reach=None, virtual=False):
    """Finding were the camera should move in terms of its type, fix and rotative cannot move"""
    memory_objectives.append((xt, yt, angle_in_room_coordinate))
    xc, yc = (camera.default_xc, camera.default_yc)

    if camera.camera_type == mobileCam.MobileCameraType.RAIL:
        line_we_want_to_be_align_with = Line(xt, yt, xt + math.cos(angle_in_room_coordinate),
                                             yt + math.sin(angle_in_room_coordinate))

        index = camera.trajectory.trajectory_index
        (xi, yi, new_index) = camera.trajectory.find_closest_intersection(line_we_want_to_be_align_with, index)
        if virtual:
            xc = xi
            yc = yi
        else:
            xc, yc = camera.trajectory.compute_distance_for_point_x_y(xi, yi, new_index)
        "Save data"
        if not virtual:
            memory_point_to_reach.append([(xi, yi, new_index)])

    elif camera.camera_type == mobileCam.MobileCameraType.FREE:
        xc = xt + math.cos(angle_in_room_coordinate) * distance_to_keep_to_target
        yc = yt + math.sin(angle_in_room_coordinate) * distance_to_keep_to_target
        xc = born(xc, camera.xc_min, camera.xc_max)
        yc = born(yc, camera.yc_min, camera.yc_max)

    if virtual:
        alpha = math.atan2(yt - yc, xt - xc)
    else:
        alpha = math.atan2(yt - camera.yc, xt - camera.xc)

    return xc, yc, alpha


def define_beta(distance, radius):
    beta = constants.SECURITY_MARGIN_BETA * math.atan2(radius, distance)
    return beta


def modify_angle(angle_in_room_coordinate, alignement_choice=Angle_configuration.PERPENDICULAR_TO_COMPUTED_DIRECTION):
    """Modification from this angle to slightly improve the results"""
    if alignement_choice == Angle_configuration.PERPENDICULAR_TO_COMPUTED_DIRECTION:
        angle_in_room_coordinate = angle_in_room_coordinate + math.pi / 2

    elif alignement_choice == Angle_configuration.PARALLEL_TO_COMPUTED_DIRECTION:
        angle_in_room_coordinate = angle_in_room_coordinate  # angle_prec

    elif alignement_choice == Angle_configuration.AUTO:
        # TODO ici voir si on peut touver un configuration ok grâce à la VFM
        # TODO cas particulier avec un PI, se rapprocher fort de l'objet près du quel on se trouver et décaler la caméra d'un angle alpha entre la droite passant par les deux targets
        pass
    else:
        print("modify_angle in  behaviour_agent.py error, choice not found")
        angle_in_room_coordinate = 0

    return angle_in_room_coordinate


def get_angle_alpha_beta_PCA_method(target_representation_list,
                                    point_to_track_choice=PCA_track_points_possibilites.MEDIAN_POINTS):
    (xt, yt, mean, explained_variance_, explained_variance_ratio_, components_) = pca_methode_2D_plan(
        target_representation_list,
        point_to_track_choice)
    eigen_vector = components_
    eigen_value_ = explained_variance_
    eigen_value_ratio = explained_variance_ratio_

    """Finding highest highest value"""
    if eigen_value_[1] < eigen_value_[0]:
        vector = eigen_vector[0]
        lambda_min = eigen_value_[0]
        lambda_max = eigen_value_[1]
        coeff_corrector = eigen_value_ratio[0]
    else:
        vector = eigen_vector[1]
        lambda_min = eigen_value_[1]
        lambda_max = eigen_value_[0]
        coeff_corrector = eigen_value_ratio[1]

    """Angle to give to the camera to get a good orrientation"""
    angle_in_room_coordinate = math.atan(vector[1] / vector[0])

    """Angle beta - field opening"""
    radius_for_beta = 0
    if point_to_track_choice == PCA_track_points_possibilites.MEANS_POINTS:
        radius_for_beta = 2 * np.sqrt(max(eigen_value_[0], eigen_value_[1]))
    elif point_to_track_choice == PCA_track_points_possibilites.MEDIAN_POINTS:
        # TODO A CHANGER ici si on sait qu'on ne prends de toute façon pas tous les points en prenant la mediane, peut être réapliquer les pca
        # TODO avec la moyenne pour obtenir l'orrientation et la variance maximale sur les targets qui sont réellement vus.
        radius_for_beta = 2 * np.sqrt(max(eigen_value_[0], eigen_value_[1]))

    return xt, yt, angle_in_room_coordinate, radius_for_beta, coeff_corrector


def get_angle_beta_command_based_on_target_pos(camera, xt, yt, radius):
    (xt_in_camera_frame, yt_in_camera_frame) = camera.coordinate_change_from_world_frame_to_camera_frame(xt, yt)
    "We suppose we are centering on the target using get_angle_alpha_command_based_on_target_pos => yt_in_camera_frame is almost = 0 "
    error_y = yt_in_camera_frame
    angle_beta = math.atan2((radius + error_y), xt_in_camera_frame)
    return 1.2 * angle_beta


def pca_methode_2D_plan(target_representation_list, point_to_track_choice=PCA_track_points_possibilites.MEDIAN_POINTS):
    """"""

    """List used"""
    sample = []
    all_x = []
    all_y = []

    """Formating data to the method fit"""
    for target_representation in target_representation_list:
        sample.append([target_representation.xc, target_representation.yc])
        if not int(target_representation.type) == int(TargetType.SET_FIX):
            all_x.append(target_representation.xc)
            all_y.append(target_representation.yc)

    if len(sample) > 0:
        """Compute the PCA analysis"""
        pca = PCA(n_components=2)
        pca.fit(sample)

        """To possibilities to choose were to place the PCA origin"""
        if len(all_x) <= 0 or len(all_y) <= 0:
            xt = pca.mean_[0]
            yt = pca.mean_[1]
        elif point_to_track_choice == PCA_track_points_possibilites.MEANS_POINTS:
            xt = np.mean(all_x)
            yt = np.mean(all_y)
        elif point_to_track_choice == PCA_track_points_possibilites.MEDIAN_POINTS:
            xt = np.median(all_x)
            yt = np.median(all_y)
        else:
            print("pca method not defined")
            return (None, None, None, None)

        return (xt, yt, pca.mean_, pca.explained_variance_, pca.explained_variance_ratio_, pca.components_)
    else:
        print("no samples")
        return (None, None, None, None)
