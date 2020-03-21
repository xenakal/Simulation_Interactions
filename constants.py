
"""Option for class main"""
SAVE_DATA = True
GENERATE_PLOT = True
USE_GUI = 1
USE_agent = 1
USE_static_analysis = 1
USE_dynamic_analysis_simulated_room = 0

T_MAX = 500
TIME_BTW_FRAMES = .1

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
STD_MEASURMENT_ERROR = 2

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
TARGET_ESTIMATOR_CSV_FIELDNAMES = ['time_stamp', 'agent_id','agent_signature','target_id','target_signature',
                                   'target_type','target_x','target_y','target_radius']
