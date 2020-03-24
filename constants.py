"""Option for class main"""
SAVE_DATA = True
GENERATE_PLOT = True
if GENERATE_PLOT:
    SAVE_DATA = True

USE_GUI = 1
USE_agent = 1
USE_static_analysis = 1
USE_dynamic_analysis_simulated_room = 0

T_MAX = 200
TIME_BTW_FRAME = .1
TIME_BTW_TARGET_MOVEMENT = .1


STATIC_ANALYSIS_PRECISION = 3  # best with 1 until map size
STATIC_ANALYSIS_PRECISION_simulated_room = 10

"""Option for class agent"""
NAME_LOG_PATH = "log/log_agent/Agent"
NAME_MAILBOX = "mailbox/MailBox_Agent"
STD_RECEIVED = 0
SEUIL_RECEIVED = 10

"""Option for class agentCamera"""
TIME_PICTURE = .5
TIME_SEND_READ_MESSAGE = .1
RUN_ON_A_THREAD = 1
DATA_TO_SEND = "behaviour"

"""Option for class estimator"""
INCLUDE_ERROR = True
STD_MEASURMENT_ERROR = 0.5

"""Option for class predication"""
NUMBER_PREDICTIONS = 2
PREVIOUS_POSITIONS_USED = 3  # number of previous positions used to make the prediction of the next positions

"""Option for class map"""
PATH_TO_SAVE_MAP = "map/"
SAVE_MAP_NAME = "My_new_map.txt"
PATH_TO_LOAD_MAP = "map/"
LOAD_MAP_NAME = "My_new_map.txt"

"""Option for GUI"""
""" 180,100,1.5,1.5 for a Room (300,300)"""
X_OFFSET = 180
Y_OFFSET = 100
X_SCALE = 60
Y_SCALE = 60

"""Option for ROOM"""
WIDTH_ROOM = 8 #[m]
LENGHT_ROOM = 8 #[m]

"CSV_fieldNames"
TARGET_ESTIMATOR_CSV_FIELDNAMES = ['time_stamp', 'agent_id', 'agent_signature', 'target_id', 'target_signature',
                                   'target_type', 'target_x', 'target_y', 'target_radius']

"""Path to save data and create plot"""


class classproperty(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class SavePlotPath:
    folder = "results"
    name_simulation = "standard"

    @classproperty
    def MAIN_FOLDER(cls):
        return SavePlotPath.folder + "/data_saved - " + SavePlotPath.name_simulation

    @classproperty
    def DATA_FOLDER(cls):
        return SavePlotPath.MAIN_FOLDER + "/data"

    @classproperty
    def PLOT_FOLDER(cls):
        return SavePlotPath.MAIN_FOLDER + "/plot"

    @classproperty
    def DATA_REFERENCE(cls):
        return SavePlotPath.DATA_FOLDER + "/simulated_data"

    @classproperty
    def DATA_MEMORY_AGENT(cls):
        return SavePlotPath.DATA_FOLDER + "/memory_agent"

    @classproperty
    def DATA_MEMORY_ALL_AGENT(cls):
        return SavePlotPath.DATA_FOLDER + "/memory_all_agent"

    @classproperty
    def DATA_PREDICTION(cls):
        return SavePlotPath.DATA_FOLDER + "/predictions"

    @classproperty
    def DATA_PREDICTION_TPLUS1(cls):
        return SavePlotPath.DATA_PREDICTION + "/t_plus_1"

    @classproperty
    def DATA_PREDICTION_TPLUS2(cls):
        return SavePlotPath.DATA_PREDICTION + "/t_plus_2"

    @classproperty
    def DATA_KALMAN(cls):
        return SavePlotPath.DATA_FOLDER + "/kalman"

    @classproperty
    def DATA_KALMAN_GLOBAL(cls):
        return SavePlotPath.DATA_KALMAN + "/kalman_global"

    @classproperty
    def DATA_KALMAN_DISTRIBUE(cls):
        return SavePlotPath.DATA_KALMAN + "/kalman_distribue"

    @classproperty
    def SAVE_LOAD_DATA_MEMORY_AGENT(cls):
        return SavePlotPath.DATA_MEMORY_AGENT + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_MEMORY_ALL_AGENT(cls):
        return SavePlotPath.DATA_MEMORY_ALL_AGENT + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_KALMAN_SIMPLE(cls):
        return SavePlotPath.DATA_KALMAN_DISTRIBUE + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_KALMAN_GLOBAL(cls):
        return SavePlotPath.DATA_KALMAN_GLOBAL + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_PREDICTION_TPLUS1(cls):
        return SavePlotPath.DATA_PREDICTION_TPLUS1+ "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_PREDICTION_TPLUS2(cls):
        return SavePlotPath.DATA_PREDICTION_TPLUS2 + "/agent-"

    @classproperty
    def PLOT_MEMORY_AGENT(cls):
        return SavePlotPath.PLOT_FOLDER + "/memory_agent"

    @classproperty
    def PLOT_MEMORY_ALL_AGENT(cls):
        return SavePlotPath.PLOT_FOLDER + "/memory_all_agent"

    @classproperty
    def SAVE_LOAD_PLOT_MEMORY_AGENT(cls):
        return SavePlotPath.PLOT_MEMORY_AGENT + "/agent-"

    @classproperty
    def SAVE_LOAD_PLOT_MEMORY_ALL_AGENT(cls):
        return SavePlotPath.PLOT_MEMORY_ALL_AGENT + "/agent-"

