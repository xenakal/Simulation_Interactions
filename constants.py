"""Option for class main"""
SAVE_DATA = False
GENERATE_PLOT = True
if GENERATE_PLOT:
    SAVE_DATA = True

USE_GUI = 1
USE_agent = 1
USE_static_analysis = 1
USE_dynamic_analysis_simulated_room = 0

T_MAX = 10000
TIME_BTW_FRAMES = .1
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
STD_MEASURMENT_ERROR = 3

"""Option for class predication"""
NUMBER_PREDICTIONS = 6
PREVIOUS_POSITIONS_USED = 10  # number of previous positions used to make the prediction of the next positions

"""Option for class map"""
PATH_TO_SAVE_MAP = "map/"
SAVE_MAP_NAME = "My_new_map.txt"
PATH_TO_LOAD_MAP = "map/"
LOAD_MAP_NAME = "My_new_map.txt"

"""Option for GUI"""
""" 180,100,1.5,1.5 for a Room (300,300)"""
X_OFFSET = 180
Y_OFFSET = 100
X_SCALE = 1.5
Y_SCALE = 1.5

"""Option for ROOM"""
WIDTH_ROOM = 300
LENGHT_ROOM = 300

"CSV_fieldNames"
TARGET_ESTIMATOR_CSV_FIELDNAMES = ['time_stamp', 'agent_id', 'agent_signature', 'target_id', 'target_signature',
                                   'target_type', 'target_x', 'target_y', 'target_radius']

"Path to save data and create plot"


def set_folder(fileName):
    SavePlotPath.MAIN_FOLDER = SavePlotPath.folder + "/data_saved - " + str(fileName)


class classproperty(object):

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class SavePlotPath:
    folder = "results"

    @classproperty
    def MAIN_FOLDER(cls):
        return SavePlotPath.folder + "/data_saved - " + str("standard")

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
    def SAVE_LOAD_DATA_MEMORY_AGENT(cls):
        return SavePlotPath.DATA_MEMORY_AGENT + "/agent-"

    @classproperty
    def SAVE_LOAD_DATA_MEMORY_ALL_AGENT(cls):
        return SavePlotPath.DATA_MEMORY_ALL_AGENT + "/agent-"

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

    """
    MAIN_FOLDER = folder + "/data_saved - " + str("standard")
    DATA_FOLDER = MAIN_FOLDER + "/data"
    PLOT_FOLDER = MAIN_FOLDER + "/plot"

    DATA_REFERENCE = DATA_FOLDER + "/simulated_data"
    DATA_MEMORY_AGENT = DATA_FOLDER + "/memory_agent"
    DATA_MEMORY_ALL_AGENT = DATA_FOLDER + "/memory_all_agent"
    SAVE_LOAD_DATA_MEMORY_AGENT = DATA_MEMORY_AGENT + "/agent-"
    SAVE_LOAD_DATA_MEMORY_ALL_AGENT = DATA_MEMORY_ALL_AGENT + "/agent-"

    PLOT_MEMORY_AGENT = PLOT_FOLDER + "/memory_agent"
    PLOT_MEMORY_ALL_AGENT = PLOT_FOLDER + "/memory_all_agent"
    SAVE_LOAD_PLOT_MEMORY_AGENT = PLOT_MEMORY_AGENT + "/agent-"
    SAVE_LOAD_PLOT_MEMORY_ALL_AGENT = PLOT_MEMORY_ALL_AGENT + "/agent-"
    """

