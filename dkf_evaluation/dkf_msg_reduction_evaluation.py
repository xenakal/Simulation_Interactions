import src.app as simulation
from src.plot_functions.plot_messages import MessagePlot, get_num_dkf_messages_percentage
from src.plot_functions.plot_targetEstimator import Analyser_Target_TargetEstimator_FormatCSV
import src.my_utils.my_IO.IO_data as log
import matplotlib.pyplot as plt
import numpy as np

############### TOOLS ################

# init logger
output_filepath = "./"
logger = log.create_kf_logger(output_filepath, "MSE_vs_INNOVATION_LOWER_BOUND2_continuation")
logger.info("--------------------------------------------------------------")
logger.info("----  MSE & #messages function of INNOVATION LOWER BOUND  ----")
logger.info("--------------------------------------------------------------")

####### PERFORMANCE EVALUATION ########

# constants
number_of_iterations = 15
distributed_filtering = True
observations_dimention = 4
stop_time = 35  # seconds
scale_time = 1

# parameters used for each scenario
map_used = "dkf_test_4_targets"
#innovation_bounds = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.7, 0.8]
innovation_bounds = [0.8]#, 0.45, 0.50, 0.55, 0.6, 0.7, 0.8]



# wrapper function for running the simulation
def run_simulation():
    # run simulation
    simulation.App(map_used, distributed_filtering, observations_dimention, stop_time, scale_time).main()
    # init plotter (not actually used to plot here)
    target_analyser_global = Analyser_Target_TargetEstimator_FormatCSV(0, dkf_data_path, dkf_plot_path)
    target_analyser_local = Analyser_Target_TargetEstimator_FormatCSV(0, local_data_path, local_plot_path)
    # get mse for last execution
    mse_dkf = target_analyser_global.get_MSE(target_id=0)
    mse_local = target_analyser_local.get_MSE(target_id=0)
    number_dkf_messages = get_num_dkf_messages_percentage(0)

    # log mse
    # print("local = % f, global = %f" % (mse_local, mse_dkf))
    logger.info("\t\tlocal mse = %f" % mse_local)
    logger.info("\t\tglobal mse = %f" % mse_dkf)
    logger.info("\t\tpercentage of dkf messages = %.2f" % number_dkf_messages)


# run simulation for each scenario
for innovation_bound in innovation_bounds:
    # update the validation bounds and other constant variables
    f = open("../innovation_bound", "w")
    f.write(str(innovation_bound))
    f.close()
    from src import constants
    constants.ResultsPath.folder = "../results"
    constants.ResultsPath.name_simulation = map_used
    dkf_data_path = constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL_FILTER
    dkf_plot_path = constants.ResultsPath.SAVE_LAOD_PLOT_KALMAN_GLOBAL_FILTERED
    local_data_path = constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_LOCAL_FILTER
    local_plot_path = constants.ResultsPath.SAVE_LAOD_PLOT_KALMAN_LOCAL_FILTERED

    # run simulation 10 times for each scenario
    logger.info("SCENARIO: INNOVATION BOUND = %.2f" % innovation_bound)
    for iteration in range(number_of_iterations):
        logger.info("\tITERATION %d" % iteration)
        run_simulation()


