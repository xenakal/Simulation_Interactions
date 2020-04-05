import logging
import time
#import multi_agent.agent.agent_interacting_room_camera as ac

"""
In this file you have the possibility to modify the settings 
"""

"""Options-----------------------------------------------------------------------------------------------------------"""
SAVE_DATA = False
GENERATE_PLOT = False

USE_GUI = True
USE_static_analysis = False
USE_dynamic_analysis_simulated_room = False

INCLUDE_ERROR = True
LOG_LEVEL = logging.DEBUG #logging.INFO  #

"""Options for Kalman Filter-----------------------------------------------------------------------------------------"""
DISTRIBUTED_KALMAN = False
KALMAN_MODEL_MEASUREMENT_DIM = 4

"""Agent - way to act------------------------------------------------------------------------------------------------"""
DATA_TO_SEND = "none" #ac.AgentCameraCommunicationBehaviour.NONE

"""Option for ROOM---------------------------------------------------------------------------------------------------"""
WIDTH_ROOM = 8  # [m]
LENGHT_ROOM = 8  # [m]

"""Number of data----------------------------------------------------------------------------------------------------"""
NUMBER_OF_POINT_SIMULATED_DATA = 20  # per m for a speed of 1 m/s
NUMBER_OF_POINT_STATIC_ANALYSIS = 5  # number of point per m
NUMBER_OF_POINT_DYNAMIC_ANALYSIS = 5 # number of point per m

"""Time--------------------------------------------------------------------------------------------------------------"""
"""global parameter for the simulation"""
SCALE_TIME = 1
TIME_START = time.time()
TIME_STOP = 10  # s
"""when mooving a target"""
TIME_BTW_FRAME = .1
TIME_BTW_TARGET_MOVEMENT = 1 / (NUMBER_OF_POINT_SIMULATED_DATA * SCALE_TIME)
"""Agent"""
TIME_BTW_HEARTBEAT = 1 / SCALE_TIME
TIME_MAX_BTW_HEARTBEAT = 3 / SCALE_TIME
"Agent-Cam"
TIME_PICTURE = (1.5 * TIME_BTW_TARGET_MOVEMENT) / SCALE_TIME
TIME_SEND_READ_MESSAGE = (0.3 * TIME_BTW_TARGET_MOVEMENT) / SCALE_TIME
MAX_TIME_MESSAGE_IN_LIST = 3  # s
TRESH_TIME_TO_SEND_MEMORY = 10  # s
"Agent-User"
TIME_TO_SLOW_DOWN = 0.15 / SCALE_TIME

"""Error on mesure---------------------------------------------------------------------------------------------------"""
STD_MEASURMENT_ERROR_POSITION = 0.2
STD_MEASURMENT_ERROR_SPEED = 0.1
STD_MEASURMENT_ERROR_ACCCELERATION = 0.00001

"""Communication - message option------------------------------------------------------------------------------------"""
NAME_MAILBOX = "mailbox/MailBox_Agent"
STD_RECEIVED = 0
SEUIL_RECEIVED = 10

"""Option for class predication--------------------------------------------------------------------------------------"""
NUMBER_PREDICTIONS = 3
PREVIOUS_POSITIONS_USED = 3  # number of previous positions used to make the prediction of the next positions

"""Option for GUI----------------------------------------------------------------------------------------------------"""
X_OFFSET = 180
Y_OFFSET = 100
X_SCALE = 60
Y_SCALE = 60

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

if STD_MEASURMENT_ERROR_POSITION == 0.0 and STD_MEASURMENT_ERROR_SPEED == 0.0\
                                        and STD_MEASURMENT_ERROR_ACCCELERATION == 0.0:
    STD_MEASURMENT_ERROR_POSITION = 0.00001
    STD_MEASURMENT_ERROR_SPEED = 0.00001
    STD_MEASURMENT_ERROR_ACCCELERATION = 0.00001


if DISTRIBUTED_KALMAN:
    DATA_TO_SEND = "dkf"

"Variable use in multiple classes"
time_when_target_are_moved = 0

"CSV_fieldNames"
TARGET_ESTIMATOR_CSV_FIELDNAMES = ['time_to_compare', 'time_stamp',
                                   'agent_id', 'agent_signature', 'target_id', 'target_signature',
                                   'target_type', 'target_x', 'target_y', 'target_vx', 'target_vy',
                                   'target_ax', 'target_ay', 'target_radius']

CAMERA_ESTIMATOR_CSV_FIELDNAMES = ['time_to_compare', 'time_stamp','agent_id','agent_signature','camera_id',
                                   'camera_signature','camera_type','camera_x','camera_y', 'camera_vx', 'camera_vy',
                                    'camera_ax', 'camera_ay','alpha', 'beta']

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
    folder = "../results"
    name_simulation = "standard"

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
    def DATA_SCREENSHOT(cls):
        return ResultsPath.MAIN_FOLDER + "/screenshot"

    @classproperty
    def DATA_FOLDER(cls):
        return ResultsPath.MAIN_FOLDER + "/data"

    @classproperty
    def DATA_IDEAL(cls):
        return ResultsPath.DATA_FOLDER + "/ideal"

    @classproperty
    def DATA_STATIC_REGION(cls):
        return ResultsPath.DATA_IDEAL + "/static_region"

    @classproperty
    def DATA_MEMORY_AGENT(cls):
        return ResultsPath.DATA_FOLDER + "/memory_agent"

    @classproperty
    def DATA_MEMORY_ALL_AGENT(cls):
        return ResultsPath.DATA_FOLDER + "/memory_all_agent"

    @classproperty
    def DATA_KALMAN(cls):
        return ResultsPath.DATA_FOLDER + "/kalman"

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
    def DATA_KALMAN_GLOBAL_PREDICTION_TPLUS1(cls):
        return ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION + "/t_plus_1"

    @classproperty
    def DATA_KALMAN_GLOBAL_PREDICTION_TPLUS2(cls):
        return ResultsPath.DATA_KALMAN_GLOBAL_PREDICTION + "/t_plus_2"

    @classproperty
    def DATA_KALMAN_DISTRIBUE(cls):
        return ResultsPath.DATA_KALMAN + "/kalman_distribue"

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
        return ResultsPath.DATA_MEMORY_AGENT + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_MEMORY_ALL_AGENT(cls):
        return ResultsPath.DATA_MEMORY_ALL_AGENT + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_KALMAN_GLOBAL_FILTER(cls):
        return ResultsPath.DATA_KALMAN_FILTER + "/agent-"

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
    def PLOT_MEMORY_AGENT(cls):
        return ResultsPath.PLOT_FOLDER + "/memory_agent"

    @classproperty
    def PLOT_MEMORY_ALL_AGENT(cls):
        return ResultsPath.PLOT_FOLDER + "/memory_all_agent"

    @classproperty
    def PLOT_KALMAN(cls):
        return ResultsPath.PLOT_FOLDER + "/kalman"

    @classproperty
    def PLOT_KALMAN_GLOBAL(cls):
        return ResultsPath.PLOT_KALMAN + "/kalman_global"

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
    def PLOT_KALMAN_DISTRIBUE(cls):
        return ResultsPath.PLOT_KALMAN + "/kalman_distribue"

    @classproperty
    def SAVE_LAOD_PLOT_FOLDER(cls):
        return ResultsPath.PLOT_FOLDER + "/"

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
    def SAVE_LOAD_PLOT_MEMORY_AGENT(cls):
        return ResultsPath.PLOT_MEMORY_AGENT + "/"

    @classproperty
    def SAVE_LOAD_PLOT_MEMORY_ALL_AGENT(cls):
        return ResultsPath.PLOT_MEMORY_ALL_AGENT + "/"
