""""""

"""Agent - way to act------------------------------------------------------------------------------------------------"""
class AgentDataToWorkWith:
    Data_measured = "Data_measured"
    Best_estimation = "Best_estimation"
    Prediction_t_1 = "Prediction t+1"
    Prediction_t_2 = "Prediction t+2"


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