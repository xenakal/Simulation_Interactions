import logging
import math
import time
from src.my_utils.constant_class import *

"""
In this file you have the possibility to modify the settings 
"""

"""Options-----------------------------------------------------------------------------------------------------------"""


SAVE_DATA = True
GENERATE_PLOT = False
LOAD_DATA = LoadData.FROM_TXT_FILE

USE_GUI = True
USE_static_analysis = False
USE_dynamic_analysis_simulated_room = False

INCLUDE_ERROR = True
LOG_LEVEL = logging.INFO  #

"""Option GUI--------------------------------------------------------------------------------------------------------"""

"Push o to show or hide"
INIT_show_point_to_reach = False
"Push v to show or hide"
INIT_show_virtual_cam = False
"Push f to show or hide"
INIT_show_field_cam = True
"Push G to show or hide the grid"
INIT_show_grid = True

"""Options for Kalman Filter-----------------------------------------------------------------------------------------"""
DISTRIBUTED_KALMAN = False
KALMAN_MODEL_MEASUREMENT_DIM = 4
USE_TIMESTAMP_FOR_ASSIMILATION = True
KALMAN_VAR_COEFFICIENT = 5


"""Option for ROOM---------------------------------------------------------------------------------------------------"""
ROOM_DIMENSION_X = 10  # [m]
ROOM_DIMENSION_Y = 10  # [m]


"""Number of data----------------------------------------------------------------------------------------------------"""
NUMBER_OF_POINT_SIMULATED_DATA = 10  # per m for a speed of 1 m/s
NUMBER_OF_POINT_STATIC_ANALYSIS = 15  # number of point per m
NUMBER_OF_POINT_DYNAMIC_ANALYSIS = 5  # number of point per m

"""Time--------------------------------------------------------------------------------------------------------------"""
"""global parameter for the simulation"""
SCALE_TIME = 1
TIME_START = time.time()
TIME_STOP = 10  # s
"""when mooving a target"""
TIME_BTW_FRAME = .05
TIME_BTW_TARGET_MOVEMENT = 1 / (NUMBER_OF_POINT_SIMULATED_DATA)
"Agent-Cam"
TIME_PICTURE = (2* TIME_BTW_TARGET_MOVEMENT)
TIME_SEND_READ_MESSAGE = (0.3 * TIME_BTW_TARGET_MOVEMENT)
MAX_TIME_MESSAGE_IN_LIST = 3   # s
TRESH_TIME_TO_SEND_MEMORY = 100  #
"""Agent"""
TIME_BTW_HEARTBEAT = 1
TIME_MAX_BTW_HEARTBEAT = 3
TIME_BTW_AGENT_ESTIMATOR = 0.5
TIME_BTW_TARGET_ESTIMATOR = TIME_PICTURE
"Agent-User"
TIME_TO_SLOW_DOWN = 0.05

"""Error on mesure---------------------------------------------------------------------------------------------------"""
STD_MEASURMENT_ERROR_POSITION = .2
STD_MEASURMENT_ERROR_SPEED = .1
STD_MEASURMENT_ERROR_ACCCELERATION = 0.00001

ERROR_VARIATION_ZOOM = True
COEFF_STD_VARIATION_MEASURMENT_ERROR_POSITION = 0.05 * STD_MEASURMENT_ERROR_POSITION
COEFF_STD_VARIATION_MEASURMENT_ERROR_SPEED = 0.01 * STD_MEASURMENT_ERROR_SPEED
COEFF_STD_VARIATION_MEASURMENT_ERROR_ACCELERATION = 0.001 * STD_MEASURMENT_ERROR_ACCCELERATION

"""Communication - message option------------------------------------------------------------------------------------"""
NAME_MAILBOX = "mailbox/MailBox_Agent"
STD_RECEIVED = 0
SEUIL_RECEIVED = 10

ITEM_START_MARKER = "ITEM_START-"
ITEM_END_MARKER = "-ITEM_END"
ITEM_CONSTANT_TAG_MARKER = "tag#"

"""Option for class predication--------------------------------------------------------------------------------------"""
NUMBER_PREDICTIONS = 3
PREVIOUS_POSITIONS_USED = 3  # number of previous positions used to make the prediction of the next positions

"""Option for GUI----------------------------------------------------------------------------------------------------"""
X_OFFSET = 180
Y_OFFSET = 100
X_SCALE = 60
Y_SCALE = 60

"""Agent - way to act------------------------------------------------------------------------------------------------"""
INIT_TARGET_LIST = AgentCameraInitializeTargetList.ALL_SEEN
"""If you want to set all the agent fixed set to false"""
AGENTS_MOVING = True
TARGET_NUMBER_OF_AGENT_SHOULD_TRACK = 1
"""
Refers to what data agent should use to analyse the room 
"""
AGENT_DATA_TO_PROCESS = AgentDataToWorkWith.Best_estimation
AGENT_CHOICE_HOW_TO_FOLLOW_TARGET = ConfigurationWaysToBeFound.TRY_TO_FIND_VALID_CONFIG

"""
Refers to what data should be exchanged between agent
- "none" = agent do not exchange messages about targets
- "dkf" = message exchange only message for distributed kalman
"""
DATA_TO_SEND = "dkf"

"""
Refers to the type of controller we use to bring the target to reference point
"""
AGENT_MOTION_CONTROLLER = AgentCameraController.Vector_Field_Method
AGENT_POS_KP = 0.4
AGENT_POS_KI = 0.0
AGENT_ALPHA_KP = 4
AGENT_ALPHA_KI = 0
AGENT_BETA_KP = 2
AGENT_BETA_KI = 0.0

MIN_CONFIGURATION_SCORE = 0.05

"""Refers to the min and max field in terms of the default field"""
AGENT_CAMERA_FIELD_MIN = 0.8
AGENT_CAMERA_FIELD_MAX = 1.2

"""Linear coefficient from the inverse relation btw beta and field depth"""
COEFF_VARIATION_FROM_FIELD_DEPTH = 1.5
"""
Behaviour target estimation
"""
BEHAVIOUR_DETECTION_TYPE = BehaviourDetectorType.Use_speed_and_position
POSITION_STD_ERROR = 0.2
SPEED_MEAN_ERROR = 0.1
"""
New configuration parameter
"""
SECURITY_MARGIN_BETA = 5
DISTANCE_TO_KEEP_FROM_TARGET = 0.5  # relative to field depth

"""
Weights on types of priorities
"""
USER_SET_PRIORITY_WEIGHT = 4
CAMERA_SET_PRIORITY_WEIGHT = 2
SCORE_WEIGHT = 1

"""
Behaviour of mobile cameras when no targets are seen
"""
BEHAVIOUR_NO_TARGETS_SEEN = BEHAVIOUR_NO_TARGETS_SEEN.RANDOM_MOVEMENT_POSITION

DELTA_TIME_CHANGE_POSITION_RANDOM_MOVEMENT = 3
DELTA_POS_CHANGE_POSITION_RANDOM_MOVEMENT = 0.3

# used when two agents are too close
TIME_STOP_INIT_BEHAVIOUR = 3

"""
Margins for initiating swipe when two agents are too close
"""
MIN_DISTANCE_AGENTS = 1.5
MIN_ANGLE_DIFF_AGENTS = 0.4
"""Target_representation--------------------------------------------------------------------------------------------"""
CONFIDENCE_MAX_VALUE = 100
CONFIDENCE_MIN_VALUE = 0
CONFIDENCE_TIME_TO_REACH_MIN_VALUE = 2.5
CONFIDENCE_THRESHOLD = 50
CONFIDENCE_FUNCTION_CHOICE = ConfidenceFunction.LINEAR_DECAY


"""Potential Field Camera--------------------------------------------------------------------------------------------"""
"""
Use Xi to set the force of attractfive potential and eta the force of repulsive potential
If XI = 0 => Attractive potentials have no effects
If ETA = 0 => Repulsive potentials have no effects

Parameters has to be set to appropriate values by trials and errors    
"""
XI = 5
ETA = 50
COEFF_RADIUS = 10
"""Barrier"""
BARRIER_TYPE = PotentialBarrier.Combine_attract

"""In the smooth mode it defines how circle are deformed to become elliptical shapes"""
COEFF_VAR_X = 100
COEFF_VAR_Y = 2

"""Combine is a ration beetwen hard and smooth mode"""
COMBINE_MODE_PROP = 0.1
"""Random map creation-----------------------------------------------------------------------------------------------"""
TARGET_NUMBER_SET_FIX = 0
TARGET_NUMBER_UNKOWN = 2
TARGET_NUMBER_OF_POINTS_GENERATED_FOR_A_TRAJECTORY = 20
RANDOM_TARGET_RADIUS_BOUND = (0.1,0.3)
RANDOM_TARGET_V_BOUND = (0.8,1.2)

CAMERA_NUMBER_FIX = 0
CAMERA_NUMBER_ROTATIVE = 0
CAMERA_NUMBER_RAIL = 0
CAMERA_NUMBER_FREE = 2

RANDOM_CAMERA_BETA_BOUND = (55,65)
RANDOM_CAMERA_DELTA_BETA_BOUND = (20,25)
RANDOM_CAMERA_FIELD_DEPTH_BOUND = (4,4)
RANDOM_CAMERA_V_XY_MIN_BOUND = (0,0)
RANDOM_CAMERA_V_XY_MAX_BOUND = (1,1)
RANDOM_CAMERA_V_BETA_MIN_BOUND = (0,0)
RANDOM_CAMERA_V_BETA_MAX_BOUND = (15,15)
RANDOM_CAMERA_V_ALPHA_MIN_BOUND = (0,0)
RANDOM_CAMERA_V_ALPHA_MAX_BOUND = (35,35)


"""---------------------------------------------------------------------------------------------------------------------
If you just want to change simulation's parameter you should not modify constant below this line 
 --------------------------------------------------------------------------------------------------------------------"""


def get_time():
    return (time.time() - TIME_START) * SCALE_TIME


"""default variable """
if GENERATE_PLOT:
    SAVE_DATA = True

if not INCLUDE_ERROR:
    STD_MEASURMENT_ERROR_POSITION = 0.00001
    STD_MEASURMENT_ERROR_SPEED = 0.00001
    STD_MEASURMENT_ERROR_ACCCELERATION = 0.00001

if STD_MEASURMENT_ERROR_POSITION == 0.0 and STD_MEASURMENT_ERROR_SPEED == 0.0 \
        and STD_MEASURMENT_ERROR_ACCCELERATION == 0.0:
    STD_MEASURMENT_ERROR_POSITION = 0.00001
    STD_MEASURMENT_ERROR_SPEED = 0.00001
    STD_MEASURMENT_ERROR_ACCCELERATION = 0.00001

if DISTRIBUTED_KALMAN:
    DATA_TO_SEND = "dkf"
else:
    DATA_TO_SEND = "none"

"Variable use in multiple classes"
time_when_target_are_moved = 0

"CSV_fieldNames"
TARGET_ESTIMATOR_CSV_FIELDNAMES = ['time_to_compare', 'time_stamp',
                                   'agent_id', 'agent_signature', 'target_id', 'target_signature',
                                   'target_type', 'target_x', 'target_y', 'target_vx', 'target_vy',
                                   'target_ax', 'target_ay', 'target_radius', 'target_alpha']

AGENT_ESTIMATOR_CSV_FIELDNAMES = ['time_to_compare', 'time_stamp', 'agent_id', 'agent_signature', 'camera_id',
                                   'camera_signature', 'camera_type', 'camera_x', 'camera_y', 'camera_vx', 'camera_vy',
                                   'camera_ax', 'camera_ay', 'alpha', 'beta','field_depth','is_agent_active','is_camera_active']

"""Path to save data and create plot"""


class classproperty(object):
    """
    Read-only descriptor (non-data descriptor) used for the class variables of the ResultsPath class to return the
    updated variables.
    """

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class MapPath:
    folder = "../maps"

    @classproperty
    def MAIN_FOLDER(cls):
        return MapPath.folder + "/"


class ResultsPath:
    folder = "/results"
    name_simulation = "My_new_map"

    @classproperty
    def MAIN_FOLDER(cls):
        return ResultsPath.folder + "/data_saved-" + ResultsPath.name_simulation

    @classproperty
    def LOG_FOLDER(cls):
        return ResultsPath.MAIN_FOLDER + "/log"

    @classproperty
    def LOG_AGENT(cls):
        return ResultsPath.LOG_FOLDER + "/log_agent/"

    @classproperty
    def LOG_MEMORY(cls):
        return ResultsPath.LOG_FOLDER + "/log_memory/"

    @classproperty
    def LOG_KALMAN(cls):
        return ResultsPath.LOG_FOLDER + "/log_kalman/"

    @classproperty
    def DATA_SCREENSHOT(cls):
        return ResultsPath.MAIN_FOLDER + "/screenshot"

    @classproperty
    def DATA_FOLDER(cls):
        return ResultsPath.MAIN_FOLDER + "/data"

    @classproperty
    def DATA_MESSAGES(cls):
        return ResultsPath.DATA_FOLDER +"/messages"

    @classproperty
    def DATA_IDEAL(cls):
        return ResultsPath.DATA_FOLDER + "/Data-ideal"

    @classproperty
    def DATA_MEMORY_RELATED_TO_TARGET(cls):
        return ResultsPath.DATA_FOLDER + "/Data-related-to-target"

    @classproperty
    def DATA_MEMORY_RELATED_TO_AGENT(cls):
        return ResultsPath.DATA_FOLDER + "/Data-related-to-agent"

    @classproperty
    def DATA_STATIC_REGION(cls):
        return ResultsPath.DATA_IDEAL + "/static_region"

    @classproperty
    def DATA_MEMORY_AGENT_TARGET(cls):
        return ResultsPath.DATA_MEMORY_RELATED_TO_TARGET + "/memory_agent"

    @classproperty
    def DATA_MEMORY_ALL_AGENT_TARGET(cls):
        return ResultsPath.DATA_MEMORY_RELATED_TO_TARGET + "/memory_all_agent"

    @classproperty
    def DATA_KALMAN(cls):
        return ResultsPath.DATA_MEMORY_RELATED_TO_TARGET + "/kalman"

    @classproperty
    def DATA_KALMAN_GLOBAL(cls):
        return ResultsPath.DATA_KALMAN + "/kalman_global"

    @classproperty
    def DATA_KALMAN_FILTER(cls):
        return ResultsPath.DATA_KALMAN_GLOBAL + "/filtered_data"

    @classproperty
    def DATA_KALMAN_GLOBAL_PREDICTION(cls):
        return ResultsPath.DATA_KALMAN_GLOBAL + "/predictions"

    @classproperty
    def DATA_KALMAN_LOCAL(cls):
        return ResultsPath.DATA_KALMAN + "/kalman_local"

    @classproperty
    def DATA_KALMAN_FILTER_LOCAL(cls):
        return ResultsPath.DATA_KALMAN_LOCAL + "/filtered_data"

    @classproperty
    def DATA_KALMAN_GLOBAL_PREDICTION_TPLUS1(cls):
        return ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION + "/t_plus_1"

    @classproperty
    def DATA_KALMAN_GLOBAL_PREDICTION_TPLUS2(cls):
        return ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION + "/t_plus_2"

    @classproperty
    def SAVE_LOAD_DATA_AGENT_ESTIMATOR(cls):
        return ResultsPath.DATA_MEMORY_RELATED_TO_AGENT + "/"

    @classproperty
    def SAVE_LOAD_DATA_STATIC_REGION(cls):
        return ResultsPath.DATA_STATIC_REGION + "/static-cut-"

    @classproperty
    def SAVE_LOAD_DATA_FOLDER(cls):
        return ResultsPath.DATA_FOLDER + "/"

    @classproperty
    def SAVE_LOAD_DATA_REFERENCE(cls):
        return ResultsPath.DATA_IDEAL + "/simulated_data"

    @classproperty
    def SAVE_LOAD_DATA_MEMORY_AGENT(cls):
        return ResultsPath.DATA_MEMORY_AGENT_TARGET + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_MEMORY_ALL_AGENT(cls):
        return ResultsPath.DATA_MEMORY_ALL_AGENT_TARGET + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_KALMAN_GLOBAL_FILTER(cls):
        return ResultsPath.DATA_KALMAN_FILTER + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_KALMAN_LOCAL_FILTER(cls):
        return ResultsPath.DATA_KALMAN_FILTER_LOCAL + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_KALMAN_GLOBAL_PREDICTION_TPLUS1(cls):
        return ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION_TPLUS1 + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_KALMAN_GLOBAL_PREDICTION_TPLUS2(cls):
        return ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION_TPLUS2 + "/agent-"

    @classproperty
    def PLOT_FOLDER(cls):
        return ResultsPath.MAIN_FOLDER + "/plot"

    @classproperty
    def PLOT_AGENT_ESTIMATOR(cls):
        return ResultsPath.PLOT_FOLDER +"/agent_estimator"

    @classproperty
    def PLOT_MEMORY_AGENT(cls):
        return ResultsPath.PLOT_FOLDER + "/memory_agent"

    @classproperty
    def PLOT_MEMORY_ALL_AGENT(cls):
        return ResultsPath.PLOT_FOLDER + "/memory_all_agent"

    @classproperty
    def PLOT_KALMAN(cls):
        return ResultsPath.PLOT_FOLDER + "/kalman"

    @classproperty
    def PLOT_KALMAN_LOCAL(cls):
        return ResultsPath.PLOT_KALMAN + "/kalman_local"

    @classproperty
    def PLOT_KALMAN_GLOBAL(cls):
        return ResultsPath.PLOT_KALMAN + "/kalman_global"

    @classproperty
    def PLOT_KALMAN_LOCAL_FILTERED(cls):
        return ResultsPath.PLOT_KALMAN_LOCAL + "/kalman_filtered"

    @classproperty
    def PLOT_KALMAN_GLOBAL_FILTERED(cls):
        return ResultsPath.PLOT_KALMAN_GLOBAL + "/kalman_filtered"

    @classproperty
    def PLOT_KALMAN_PREDICTION(cls):
        return ResultsPath.PLOT_KALMAN_GLOBAL + "/kalman_prediction"

    @classproperty
    def PLOT_KALMAN_PREDICTION_T_PLUS_1(cls):
        return ResultsPath.PLOT_KALMAN_PREDICTION + "/prediction_t_plus_1"

    @classproperty
    def PLOT_KALMAN_PREDICTION_T_PLUS_2(cls):
        return ResultsPath.PLOT_KALMAN_PREDICTION + "/prediction_t_plus_2"

    @classproperty
    def PLOT_MESSAGE(cls):
        return ResultsPath.PLOT_FOLDER + "/messages"

    @classproperty
    def SAVE_LAOD_PLOT_FOLDER(cls):
        return ResultsPath.PLOT_FOLDER + "/"

    @classproperty
    def SAVE_LAOD_PLOT_KALMAN_LOCAL_FILTERED(cls):
        return ResultsPath.PLOT_KALMAN_LOCAL_FILTERED + "/"

    @classproperty
    def SAVE_LAOD_PLOT_KALMAN_GLOBAL_FILTERED(cls):
        return ResultsPath.PLOT_KALMAN_GLOBAL_FILTERED + "/"

    @classproperty
    def SAVE_LAOD_PLOT_KALMAN_GLOBAL_PREDICTION_T_PLUS_1(cls):
        return ResultsPath.PLOT_KALMAN_PREDICTION_T_PLUS_1 + "/"

    @classproperty
    def SAVE_LAOD_PLOT_KALMAN_GLOBAL_PREDICTION_T_PLUS_2(cls):
        return ResultsPath.PLOT_KALMAN_PREDICTION_T_PLUS_2 + "/"

    @classproperty
    def SAVE_LAOD_PLOT_KALMAN_GLOBAL(cls):
        return ResultsPath.PLOT_KALMAN_GLOBAL + "/"

    @classproperty
    def SAVE_LAOD_PLOT_KALMAN_LOCAL(cls):
        return ResultsPath.PLOT_KALMAN_LOCAL + "/"

    @classproperty
    def SAVE_LOAD_PLOT_MEMORY_AGENT(cls):
        return ResultsPath.PLOT_MEMORY_AGENT + "/"

    @classproperty
    def SAVE_LOAD_PLOT_MEMORY_ALL_AGENT(cls):
        return ResultsPath.PLOT_MEMORY_ALL_AGENT + "/"
