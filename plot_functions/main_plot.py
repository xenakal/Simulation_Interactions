import constants
from plot_functions.plot_targetEstimator import *

"To plot a graph just put the agent id and run"

constants.SavePlotPath.folder = "../results"
constants.SavePlotPath.name_simulation = "My_new_map"


agent_id = 1
analyser_memory_agent = Analyser_Target_TargetEstimator_FormatCSV(agent_id,constants.SavePlotPath.SAVE_LOAD_DATA_MEMORY_AGENT)
analyser_memory_all_agent = Analyser_Target_TargetEstimator_FormatCSV(agent_id,constants.SavePlotPath.SAVE_LOAD_DATA_MEMORY_ALL_AGENT)
analyser_kalman_global = Analyser_Target_TargetEstimator_FormatCSV(agent_id,constants.SavePlotPath.SAVE_LOAD_DATA_KALMAN_GLOBAL)
analyser_prediction_t_plus_1 = Analyser_Target_TargetEstimator_FormatCSV(agent_id,constants.SavePlotPath.SAVE_LOAD_DATA_PREDICTION_TPLUS1)
analyser_prediction_t_plus_2 = Analyser_Target_TargetEstimator_FormatCSV(agent_id,constants.SavePlotPath.SAVE_LOAD_DATA_PREDICTION_TPLUS2)


target_id = 0
analyser_kalman_global.MSE_target_id(target_id)
analyser_memory_agent.MSE_target_id(target_id)


plt.show()
