import constants
from plot_functions.plot_targetEstimator import *

"To plot a graph just put the agent id and run"

constants.SavePlotPath.folder = "../results"
constants.SavePlotPath.name_simulation = "My_new_map"

test = AnalyseMemoryAgent(100)
#test.plot_a_target_simulated_data_collected_data(3)
test.MSE_target_id(4)
plt.show()
