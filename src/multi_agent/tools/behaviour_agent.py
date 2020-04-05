import math

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