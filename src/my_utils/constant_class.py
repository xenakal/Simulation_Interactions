""""""
class LoadData:
     FROM_TXT_FILE = "from_txt_file"
     CREATE_RANDOM_DATA = "random_data"



"""Agent - way to act------------------------------------------------------------------------------------------------"""
class AgentDataToWorkWith:
    Data_measured = "Data_measured"
    Best_estimation = "Best_estimation"
    Prediction_t_1 = "Prediction t+1"
    Prediction_t_2 = "Prediction t+2"

class ConfigurationWaysToBeFound:
    CONFIUGRATION_WIHTOUT_CHECK = "config_wihtout_check"
    CONFIUGRATION_WITH_TARGET_CHECK = "config_target_check"
    CONFIUGRATION_WITH_SCORE_CHECK = "config_score_check"
    MOVE_ONLY_IF_CONFIGURATION_IS_VALID = "change_config_only_if_valid"
    TRY_TO_FIND_VALID_CONFIG = "try_to_find_valid_config"

class AgentCameraCommunicationBehaviour:
    ALL = "all"
    DKF = "dkf"
    NONE = "none"


class AgentCameraInitializeTargetList:
    ALL_IN_ROOM = "all_in_room"
    ALL_SEEN = "all_seen"


class AgentCameraController:
    Controller_PI = "PI"
    Vector_Field_Method = "VFM"


class TARGET_PRIORITY:
    LOW = 0
    MEDIUM = 1
    MEDIUM_HIGH = 3
    HIGH = 5
    IMPERATIVE = 1000000


"""Potential field --------------------------------------------------------------------------------------------------"""
class PotentialBarrier:
    Not_use = "not_use"
    Smooth = "smooth"
    Combine = "combine"
    Hard = "hard"

"""Behaviour détector------------------------------------------------------------------------------------------------"""
class BehaviourDetectorType:
    Use_speed_and_position = "Speed and position"
    Use_speed_only = "Speed"
    Use_position_only  = "Position"