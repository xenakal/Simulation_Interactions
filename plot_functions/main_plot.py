import constants
from plot_functions.plot_targetEstimator import *

"To plot a graph just put the agent id and run"

constants.ResultsPath.folder = "../results"
constants.ResultsPath.name_simulation = "My_new_map"


agent_id = 1
#analyser_memory_agent = Analyser_Target_TargetEstimator_FormatCSV(agent_id, constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT)
#analyser_memory_all_agent = Analyser_Target_TargetEstimator_FormatCSV(agent_id, constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_ALL_AGENT)
#analyser_kalman_global = Analyser_Target_TargetEstimator_FormatCSV(agent_id, constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL)
#analyser_prediction_t_plus_1 = Analyser_Target_TargetEstimator_FormatCSV(agent_id, constants.ResultsPath.SAVE_LOAD_DATA_PREDICTION_TPLUS1)
#analyser_prediction_t_plus_2 = Analyser_Target_TargetEstimator_FormatCSV(agent_id, constants.ResultsPath.SAVE_LOAD_DATA_PREDICTION_TPLUS2)

analyser_kalman_global = Analyser_Target_TargetEstimator_FormatCSV(agent_id,
                                                                   constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL,
                                                                   constants.ResultsPath.SAVE_LAOD_PLOT_KALMAN_GLOBAL)

target_id = 0
analyser_kalman_global.plot_position_target_simulated_data_collected_data()
#analyser_memory_agent.MSE_target_id(target_id)
#analyser_kalman_global.MSE_target_id(target_id)


plt.show()
