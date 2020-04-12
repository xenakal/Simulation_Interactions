import math
import matplotlib.pyplot as plt
import numpy as np
import random
from sklearn.decomposition import PCA
import src.multi_agent.elements.mobile_camera as mobileCam
from src import constants
from src.multi_agent.elements.target import TargetType
from src.my_utils.my_math.line import Line, distance_btw_two_point



class PCA_track_points_possibilites:
    MEANS_POINTS = "mean points"
    MEDIAN_POINTS = "median points"


def use_pca_to_get_alpha_beta_xc_yc(memory_objectives, memory_point_to_reach, camera, target_representation_list,
                                    point_to_track_choice=PCA_track_points_possibilites.MEDIAN_POINTS):
    if len(target_representation_list) < 2:
        return
    sample = []
    all_x = []
    all_y = []
    for target_representation in target_representation_list:
        sample.append([target_representation.xc, target_representation.yc])
        if not int(target_representation.type) == int(TargetType.SET_FIX):
            all_x.append(target_representation.xc)
            all_y.append(target_representation.yc)

    pca = PCA(n_components=2)
    pca.fit(sample)

    if point_to_track_choice == PCA_track_points_possibilites.MEANS_POINTS:
        xt = np.mean(all_x)
        yt = np.mean(all_y)

        #xt = pca.mean_[0] #only on point taken into account by pca
        #yt = pca.mean_[1]
    elif point_to_track_choice == PCA_track_points_possibilites.MEDIAN_POINTS:
        xt = np.median(all_x)
        yt = np.median(all_y)
    else:
        print("pca method not defined")
        return (None,None,None,None)

    eigen_vector = pca.components_
    eigen_value_ = pca.explained_variance_

    lambda1 = eigen_value_[0]
    lambda2 = eigen_value_[1]
    if lambda1 < lambda2:
        vector = eigen_vector[0]
    else:
        vector = eigen_vector[1]

    angle = math.atan2(math.fabs(vector[1]), math.fabs(vector[0]))
    # TODO définir comment choisir l'ange que l'on veut choisir
    memory_objectives.append((xt, yt, angle))



    xc, yc = (camera.default_xc, camera.default_yc)
    if camera.camera_type == mobileCam.MobileCameraType.RAIL:
        line_we_want_to_be_align_with = Line(xt, yt, xt + math.cos(angle), yt + math.sin(angle))
        # memory_point_to_reach.append(camera.trajectory.find_all_intersection(line_we_want_to_be_align_with))
        index = camera.trajectory.trajectory_index
        (xi, yi, new_index) = camera.trajectory.find_closest_intersection(line_we_want_to_be_align_with, index)
        memory_point_to_reach.append([(xi, yi, new_index)])
        xc, yc = camera.trajectory.compute_distance_for_point_x_y(xi, yi, new_index)

    elif camera.camera_type == mobileCam.MobileCameraType.FREE:
        d = camera.field_depth*0.6
        xc = xt + math.cos(angle)*d
        yc = yt + math.sin(angle)*d

        if xc < 0:
            xc = 0
        elif xc > constants.LENGHT_ROOM:
            xc = constants.LENGHT_ROOM
        if yc < 0:
            yc = 0
        elif yc > constants.WIDTH_ROOM:
            yc = constants.WIDTH_ROOM

        memory_point_to_reach.append([(xc, yc, 0)])

    beta = 0
    if point_to_track_choice == PCA_track_points_possibilites.MEANS_POINTS:
        coeff_correcteur = 1.5
        distance_camera_xy_target = distance_btw_two_point(xc, yc, xt, yt)
        beta = math.atan2(coeff_correcteur *2* np.sqrt(max(lambda1, lambda2)), distance_camera_xy_target)
    elif point_to_track_choice == PCA_track_points_possibilites.MEDIAN_POINTS:
        #TODO ici si on sait qu'on ne prends de toute façon pas tous les points en prenant la mediane, peut être réapliquer les pca
        #TODO avec la moyenne pour obtenir l'orrientation et la variance maximale sur les targets qui sont réellement vus.
        coeff_correcteur = 1.5
        distance_camera_xy_target = distance_btw_two_point(xc, yc, xt, yt)
        beta = math.atan2(coeff_correcteur * 2 * np.sqrt(max(lambda1, lambda2)), distance_camera_xy_target)

    return xc, yc, get_angle_alpha_command_based_on_target_pos(camera, xt, yt), beta


def get_angle_zoom_based_on_target_representation(camera, target_representation):
    alpha = get_angle_alpha_command_based_on_target_pos(camera, target_representation.xc, target_representation.yc)
    beta = get_angle_beta_command_based_on_target_pos(target_representation.xc, target_representation.yc)


def get_angle_alpha_command_based_on_target_pos(camera, xt, yt):
    (xt_in_camera_frame, yt_in_camera_frame) = camera.coordinate_change_from_world_frame_to_camera_frame(xt, yt)
    rotation_in_camera_frame = math.atan2(yt_in_camera_frame, xt_in_camera_frame)
    return camera.alpha + rotation_in_camera_frame


def get_angle_beta_command_based_on_target_pos(camera, xt, yt, radius):
    (xt_in_camera_frame, yt_in_camera_frame) = camera.coordinate_change_from_world_frame_to_camera_frame(xt, yt)
    """We suppose we are centering on the target using get_angle_alpha_command_based_on_target_pos => 
    yt_in_camera_frame is almost = 0 """
    error_y = yt_in_camera_frame
    angle_beta = math.atan2((radius + error_y), xt_in_camera_frame)
    return 1.2 * angle_beta
