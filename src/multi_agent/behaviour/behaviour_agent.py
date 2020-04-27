import itertools
import math
import random
import warnings

import numpy as np
from scipy.interpolate import griddata
from sklearn.decomposition import PCA

import src.multi_agent.elements.mobile_camera as mobileCam
from src import constants
from src.multi_agent.elements.target import TargetType
from src.multi_agent.tools.configuration import Configuration, bound
from src.my_utils import constant_class
from src.my_utils.my_math.line import Line, distance_btw_two_point
from src.multi_agent.tools.potential_field_method import compute_potential_gradient, \
    convert_target_list_to_potential_field_input, compute_potential_field_cam, plot_potential_field_dynamic, HeatMaps


class Angle_configuration:
    PARALLEL_TO_COMPUTED_DIRECTION = 0
    PERPENDICULAR_TO_COMPUTED_DIRECTION = 1


class PCA_track_points_possibilites:
    MEANS_POINTS = "mean points"
    MEDIAN_POINTS = "median points"


def check_heat_maps(n_target, camera):
    if n_target == 1:
        return [HeatMaps.HEAT_MAP_ONE_TARGET_CENTER(camera.field_depth)]

    elif n_target == 2:
        return [HeatMaps.HEAT_MAP_TWO_TARGET_CENTER(camera.field_depth, camera.beta),
                HeatMaps.HEAT_MAP_TWO_TARGET_FAR(camera.field_depth, camera.field_depth, 1),
                HeatMaps.HEAT_MAP_TWO_TARGET_FAR(camera.field_depth, camera.field_depth, 2)]


def get_configuration_based_on_seen_target(camera, target_representation_list, room,
                                           point_to_track_choice=PCA_track_points_possibilites.MEDIAN_POINTS,
                                           memory_objectives=None,
                                           memory_point_to_reach=None, virtual=False, no_target_behaviour=False):
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

    all_fix = True
    are_target_fix = [target.type == TargetType.FIX for target in target_representation_list]
    for item in are_target_fix:
        if not item:
            all_fix = False

    if all_fix and target_representation_list:
        return Configuration(xt, yt, camera.xc, camera.yc, camera.alpha, camera.beta, camera.field_depth, virtual)

    """-----------------------------------------------------------------------------------------------------------------
       IN TERMS OF THE TARGET NUMBER
    -----------------------------------------------------------------------------------------------------------------"""

    if number_of_target < 0:
        warnings.warn("Agent ", camera.id, "sees a negative number of targets...")

    if number_of_target == 0 or no_target_behaviour:

        configuration = Configuration(camera.xc, camera.yc, camera.xc, camera.yc, camera.alpha,
                                      camera.beta, camera.field_depth, virtual)
        # all types rotate
        if camera.camera_type != mobileCam.MobileCameraType.FIX:
            no_targets_rotation_behaviour(configuration, camera)

        # rails and free cameras actually move
        if camera.camera_type == mobileCam.MobileCameraType.RAIL or \
                camera.camera_type == mobileCam.MobileCameraType.FREE:
            no_target_movement_behaviour(configuration, camera)

        return configuration

    elif number_of_target == 1:
        "In this case PCA is not possible, we chose to focus on the target itself"
        target = target_representation_list[0]
        xt = target.xc
        yt = target.yc

        delta_x = camera.xc - xt
        delta_y = camera.yc - yt

        if target.type == TargetType.FIX or target.type == TargetType.SET_FIX:
            angle_in_room_representation = camera.alpha
        else:
            angle_in_room_representation = math.atan(delta_y / delta_x)

        y_to_compute_beta = target.radius
        placement_choice = Angle_configuration.PARALLEL_TO_COMPUTED_DIRECTION

    elif number_of_target >= 2:
        "Principle Component Analysis"
        xt, yt, angle_in_room_representation, y_to_compute_beta, variance_min_ratio = get_angle_alpha_beta_PCA_method(
            target_representation_list,
            point_to_track_choice)

        placement_choice = Angle_configuration.PERPENDICULAR_TO_COMPUTED_DIRECTION

        if number_of_target == 2:
            target1 = target_representation_list[0]
            target2 = target_representation_list[1]
            distance = distance_btw_two_point(target1.xc, target1.yc, target2.xc, target2.yc)
            if distance > 2 * distance_to_keep_to_target * camera.field_depth * math.tan(beta / 2):
                placement_choice = Angle_configuration.PARALLEL_TO_COMPUTED_DIRECTION

        elif number_of_target == 3:
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

    """-----------------------------------------------------------------------------------------------------------------
    IN TERMS OF THE CAMERA TYPE
    -----------------------------------------------------------------------------------------------------------------"""
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
        delta_distance = distance1 - distance2
        chose_pt_1 = True
        if math.fabs(delta_distance) > 0.1 and delta_distance > 0:
            chose_pt_1 = False

        if chose_pt_1:
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

    """Same computation for the beta for every case"""
    distance_to_target = distance_btw_two_point(camera.xc, camera.yc, xt, yt)
    beta = define_beta(distance_to_target, y_to_compute_beta)
    field_depth = camera.compute_field_depth_variation_for_a_new_beta(beta)

    """Create a new configuration and make it match with the camera limitation"""
    configuration = Configuration(xt, yt, xc, yc, alpha, beta, field_depth, virtual)
    configuration.bound_to_camera_limitation(camera)
    configuration.track_target_list = target_representation_list
    configuration.compute_configuration_score()
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
        xc = bound(xc, camera.xc_min, camera.xc_max)
        yc = bound(yc, camera.yc_min, camera.yc_max)

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
            return None, None, None, None

        return xt, yt, pca.mean_, pca.explained_variance_, pca.explained_variance_ratio_, pca.components_
    else:
        print("no samples")
        return None, None, None, None


def are_all_points_in_room(points_list):
    return all([is_point_in_room(point) for point in points_list])


def is_point_in_room(point):
    x_in_length = 0 <= point[0] <= constants.ROOM_DIMENSION_X
    y_in_width = 0 <= point[1] <= constants.ROOM_DIMENSION_Y
    return x_in_length and y_in_width


def intersection_fov_room(camera):
    """Finds the intersectino between the field of view of a camera with the edges of the room."""
    from src.my_utils.my_math.line import Line
    points_of_intersection = []
    corners_of_room = [(0, 0), (0, constants.ROOM_DIMENSION_Y), (constants.ROOM_DIMENSION_X, constants.ROOM_DIMENSION_Y),
                       (constants.ROOM_DIMENSION_X, 0), (0, 0)]
    for idx in range(len(corners_of_room) - 1):
        # define the 4 Lines of the room
        room_edge = Line(corners_of_room[idx][0], corners_of_room[idx][1],
                         corners_of_room[idx + 1][0], corners_of_room[idx + 1][1])
        # define the circle constructed from the field depth and the center of the camera & find intersections
        fov_intersection = room_edge.find_intersection_btw_line_circle(camera.field_depth, camera.xc, camera.yc)
        if fov_intersection is not None:
            x1, y1, x2, y2 = fov_intersection
            points_of_intersection.append((x1, y1))
            points_of_intersection.append((x2, y2))

    # return all intersections (if more than 2, there is a problem... sort of...)
    return points_of_intersection


def chose_point_of_intersection(intersection_points, rotation_direction):
    """From the intersection points, finds the one that will be touched if the points are outside of the room and
    the camera rotates in the rotation_dir direction."""
    # top of the room
    if intersection_points[0][1] == 0 or intersection_points[0][0] == 0:
        # rotating clockwise
        if rotation_direction > 0:
            return intersection_points[0]
        else:
            return intersection_points[1]
    elif intersection_points[0][1] == constants.ROOM_DIMENSION_Y or intersection_points[0][0] == constants.ROOM_DIMENSION_X:
        if rotation_direction > 0:
            return intersection_points[1]
        else:
            return intersection_points[0]


def no_targets_rotation_behaviour(configuration, camera):
    # points located at the intersection of the arc defining the end of the field of view and the
    # two lines at +- beta/2 defining the width of the field of view
    field_edge_points = camera.get_edge_points_world_frame()
    # time constraint to give time for the camera to move back in the room
    dt = constants.get_time() - camera.last_swipe_direction_change

    in_room = are_all_points_in_room(field_edge_points)
    if in_room:
        configuration.alpha += camera.swipe_angle_direction * camera.swipe_delta_alpha
        return

    if dt > camera.dt_next_swipe_direction_change:
        # change direction
        camera.swipe_angle_direction *= -1
        camera.last_swipe_direction_change = constants.get_time()

        # find amount of time to turn before both edges get back in the room
        
        intersections_fov_with_room = intersection_fov_room(camera)
        # chose the correct point of intersection
        point_of_intersection = chose_point_of_intersection(intersections_fov_with_room, camera.swipe_angle_direction)
        # get angle from camera current position to intersection point found
        angle_intersection_point = -math.atan2(point_of_intersection[1] - camera.yc,
                                               point_of_intersection[0] - camera.xc)
        # calculate the lenght of the arc between furthest point and point of intersectionff
        angle_edge_intersection_len = math.fabs(angle_intersection_point - (camera.alpha - camera.beta / 2))
        camera.dt_next_swipe_direction_change = angle_edge_intersection_len / camera.v_alpha_max
    else:

        configuration.alpha += camera.swipe_angle_direction * camera.swipe_delta_alpha


def no_target_movement_behaviour(configuration, camera):
    if constants.BEHAVIOUR_NO_TARGETS_SEEN == constant_class.BEHAVIOUR_NO_TARGETS_SEEN.RANDOM_MOVEMENT_TIME:
        random_movement_behaviour_based_on_time(configuration, camera)
    elif constants.BEHAVIOUR_NO_TARGETS_SEEN == constant_class.BEHAVIOUR_NO_TARGETS_SEEN.RANDOM_MOVEMENT_POSITION:
        random_movement_behaviour_based_on_position(configuration, camera)
    elif constants.BEHAVIOUR_NO_TARGETS_SEEN == constant_class.BEHAVIOUR_NO_TARGETS_SEEN.AVOID_SEEN_REGIONS:
        avoid_seen_regions_behaviour(configuration, camera)


def random_movement_behaviour_based_on_time(configuration, camera):
    # if enough time has passed, randomly generate a new position
    delta_time = constants.get_time() - camera.last_swipe_position_change
    if delta_time > constants.DELTA_TIME_CHANGE_POSITION_RANDOM_MOVEMENT:
        configuration.x = random.uniform(0, constants.ROOM_DIMENSION_X)
        if camera.camera_type == mobileCam.MobileCameraType.FREE:
            configuration.y = random.uniform(0, constants.ROOM_DIMENSION_Y)
        camera.last_swipe_position_change = constants.get_time()
        camera.last_swipe_configuration = configuration
    else:
        configuration.x = camera.last_swipe_configuration.x
        if camera.camera_type == mobileCam.MobileCameraType.FREE:
            configuration.y = camera.last_swipe_configuration.y


def random_movement_behaviour_based_on_position(configuration, camera):
    # if the camera is close to the randomly generated position, generate a new one
    delta_x_square = math.pow(camera.xc - camera.last_swipe_configuration.x, 2)
    delta_y_square = math.pow(camera.yc - camera.last_swipe_configuration.y, 2)
    delta_position = math.pow(delta_x_square + delta_y_square, .5)
    if delta_position < constants.DELTA_POS_CHANGE_POSITION_RANDOM_MOVEMENT:
        configuration.x = random.uniform(0, constants.ROOM_DIMENSION_X)
        if camera.camera_type == mobileCam.MobileCameraType.FREE:
            configuration.y = random.uniform(0, constants.ROOM_DIMENSION_Y)
        camera.last_swipe_position_change = constants.get_time()
        camera.last_swipe_configuration = configuration
    else:
        configuration.x = camera.last_swipe_configuration.x
        if camera.camera_type == mobileCam.MobileCameraType.FREE:
            configuration.y = camera.last_swipe_configuration.y


def avoid_seen_regions_behaviour(configuration, camera):
    pass

