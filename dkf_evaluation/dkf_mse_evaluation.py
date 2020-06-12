import src.app as simulation
from src.plot_functions.plot_targetEstimator import Analyser_Target_TargetEstimator_FormatCSV
import src.my_utils.my_IO.IO_data as log
import matplotlib.pyplot as plt
import numpy as np

############### TOOLS ################

# init logger
output_filepath = "./"
logger = log.create_kf_logger(output_filepath, "MSE_measurements22")
logger.info("-----------------------------------------------------------------------")
logger.info("----  MSE of filtered measurements for DKF performance evaluation  ----")
logger.info("-----------------------------------------------------------------------")

####### PERFORMANCE EVALUATION ########

# constants
number_of_iterations = 20
distributed_filtering = True
observations_dimention = 4
stop_time = 50  # seconds
scale_time = 1

# parameters used for each scenario
maps = ["dkf_test_2_target", "dkf_test_3_targets", "dkf_test_4_targets", "dkf_test_5_targets"]
nodal_validations = [8, 7, 7, 7]
internodal_validations = [6, 9, 12, 13]
number_agents = [2, 3, 4, 5]


# wrapper function for running the simulation
def run_simulation(map_used):
    # run simulation
    simulation.App(map_used, distributed_filtering, observations_dimention, stop_time, scale_time).main()
    # init plotter (not actually used to plot here)
    target_analyser_global = Analyser_Target_TargetEstimator_FormatCSV(0, dkf_data_path, dkf_plot_path)
    target_analyser_local = Analyser_Target_TargetEstimator_FormatCSV(0, local_data_path, local_plot_path)
    # get mse for last execution
    mse_dkf = target_analyser_global.get_MSE(target_id=0)
    mse_local = target_analyser_local.get_MSE(target_id=0)
    # log mse
    print("local = % f, global = %f" % (mse_local, mse_dkf))
    logger.info("\t\tlocal mse = %f" % mse_local)
    logger.info("\t\tglobal mse = %f" % mse_dkf)


# run simulation for each scenario
for scenario_number, map_scenario, nodal_validation, internodal_validation in \
        zip(number_agents, maps, nodal_validations, internodal_validations):
    # update the validation bounds and other constant variables
    f = open("../validation_bounds", "w")
    f.write(str(nodal_validation) + " " + str(internodal_validation))
    f.close()
    from src import constants

    constants.ResultsPath.folder = "../results"
    constants.ResultsPath.name_simulation = map_scenario
    dkf_data_path = constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL_FILTER
    dkf_plot_path = constants.ResultsPath.SAVE_LAOD_PLOT_KALMAN_GLOBAL_FILTERED
    local_data_path = constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_LOCAL_FILTER
    local_plot_path = constants.ResultsPath.SAVE_LAOD_PLOT_KALMAN_LOCAL_FILTERED

    # run simulation 10 times for each scenario
    logger.info("SCENARIO: RECTANGLE WITH %d AGENTS" % scenario_number)
    for iteration in range(number_of_iterations):
        logger.info("\tITERATION %d" % iteration)
        run_simulation(map_scenario)


