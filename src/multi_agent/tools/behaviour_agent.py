import math
import matplotlib.pyplot as plt
import numpy as np
import random
from sklearn.decomposition import PCA

from src.multi_agent.elements.target import TargetType
from src.my_utils.my_math.line import Line


def use_pca_to_get_alpha_beta_xc_yc(camera, target_representation_list):
    sample = []
    all_x = []
    all_y = []
    for target_representation in target_representation_list:
        sample.append([target_representation.xc, target_representation.yc])
        if not int(target_representation.type) == int(TargetType.SET_FIX):
            all_x.append(target_representation.xc)
            all_y.append(target_representation.yc)

    xt = np.mean(all_x)
    yt = np.mean(all_y)
    pca = PCA(n_components=2)
    pca.fit(sample)

    eigen_vector = pca.components_
    eigen_value_ratio = pca.explained_variance_ratio_

    lambda1 = eigen_value_ratio[0]
    lambda2 = eigen_value_ratio[1]
    if lambda1 < lambda2:
        vector = eigen_vector[0]
    else:
        vector = eigen_vector[1]

    line_we_want_to_be_align_with = Line(xt,yt,xt+vector[0],vector[1])

    traj_1 = camera.trajectory.trajectory[1:]
    traj_2 = camera.trajectory.trajectory[:-1]


    xc,yc = (camera.default_xc,camera.default_yc)
    for pt1,pt2 in zip(traj_1,traj_2):
        segment = Line(pt1[0],pt1[1],pt2[0],pt2[1])
        xi,yi = line_we_want_to_be_align_with.find_intersection_btw_two_line(segment)
        xc,yc = camera.trajectory.from_world_frame_to_trajectory_frame(xi,yi)

    return xc,yc,get_angle_alpha_command_based_on_target_pos(camera,xt,yt)


def get_angle_zoom_based_on_target_representation(camera,target_representation):
    alpha = get_angle_alpha_command_based_on_target_pos(camera,target_representation.xc,target_representation.yc)
    beta = get_angle_beta_command_based_on_target_pos(target_representation.xc,target_representation.yc)

def get_angle_alpha_command_based_on_target_pos(camera,xt,yt):
    (xt_in_camera_frame,yt_in_camera_frame) = camera.coordinate_change_from_world_frame_to_camera_frame(xt,yt)
    rotation_in_camera_frame = math.atan2(yt_in_camera_frame,xt_in_camera_frame)
    return camera.alpha + rotation_in_camera_frame

def get_angle_beta_command_based_on_target_pos(camera,xt,yt,radius):
    (xt_in_camera_frame,yt_in_camera_frame) = camera.coordinate_change_from_world_frame_to_camera_frame(xt,yt)
    "We suppose we are centering on the target using get_angle_alpha_command_based_on_target_pos => yt_in_camera_frame is almost = 0 "
    error_y = yt_in_camera_frame
    angle_beta = math.atan2((radius+error_y),xt_in_camera_frame)
    return 1.2*angle_beta