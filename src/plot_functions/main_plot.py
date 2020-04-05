from src import constants

"To plot a graph just put the agent id and run"

constants.ResultsPath.folder = "../results"
constants.ResultsPath.name_simulation = "My_new_map"

def plot_res(room, filename):
    print("Generating plots ...")
    print("plot simulated_data")
    analyser_simulated_data = Analyser_Target_TargetEstimator_FormatCSV("",
                                                                        constants.ResultsPath.SAVE_LOAD_DATA_REFERENCE,
                                                                        constants.ResultsPath.SAVE_LAOD_PLOT_FOLDER,
                                                                        filename)
    analyser_simulated_data.plot_all_target_simulated_data_collected_data()
    for target in room.information_simulation.Target_list:
        analyser_simulated_data.plot_a_target_simulated_data_collected_data(target.id)

    "PLOT FOR AGENT CAM"
    for agent in room.agentCams_list:
        print("plot agent :" + str(agent.id))

        "Object to save data"
        analyser_agent_memory = Analyser_Target_TargetEstimator_FormatCSV(agent.id,
                                                                          constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT,
                                                                          constants.ResultsPath.SAVE_LOAD_PLOT_MEMORY_AGENT,
                                                                          filename)
        analyser_kalman_global = Analyser_Target_TargetEstimator_FormatCSV(agent.id,
                                                                           constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL_FILTER,
                                                                           constants.ResultsPath.SAVE_LAOD_PLOT_KALMAN_GLOBAL_FILTERED)

        analyser_kalman_prediction_t1 = Analyser_Target_TargetEstimator_FormatCSV(agent.id,
                                                                                  constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL_PREDICTION_TPLUS1,
                                                                                  constants.ResultsPath.SAVE_LAOD_PLOT_KALMAN_GLOBAL_PREDICTION_T_PLUS_1)

        analyser_kalman_prediction_t2 = Analyser_Target_TargetEstimator_FormatCSV(agent.id,
                                                                                  constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL_PREDICTION_TPLUS2,
                                                                                  constants.ResultsPath.SAVE_LAOD_PLOT_KALMAN_GLOBAL_PREDICTION_T_PLUS_2)
        "Graph to plot"
        """Including every target"""
        analyser_agent_memory.plot_all_target_simulated_data_collected_data()
        analyser_kalman_global.plot_position_target_simulated_data_collected_data()

        """Specific to each target"""
        for target in room.information_simulation.Target_list:
            analyser_agent_memory.plot_MSE_not_interpolate_target_id(target.id)
            analyser_kalman_global.plot_MSE_not_interpolate_target_id(target.id)
            analyser_kalman_global.plot_MSE_interpolate_target_id(target.id)
            analyser_kalman_prediction_t1.plot_MSE_prediction_1_target_id(target.id)
            analyser_kalman_prediction_t2.plot_MSE_prediction_2_target_id(target.id)

    "PLOT FOR AGENT USER"
    for agent in room.agentUser_list:
        print("plot agent :" + str(agent.id))

        "Object to save data"
        analyser_agent_memory = Analyser_Target_TargetEstimator_FormatCSV(agent.id,
                                                                          constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT,
                                                                          constants.ResultsPath.SAVE_LOAD_PLOT_MEMORY_AGENT,
                                                                          filename)
        analyser_agent_all_memory = Analyser_Agent_Target_TargetEstimator_FormatCSV(agent.id,
                                                                                    constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_ALL_AGENT,
                                                                                    constants.ResultsPath.SAVE_LOAD_PLOT_MEMORY_ALL_AGENT,
                                                                                    filename)

        "Graph to plot"
        """Including every target"""
        analyser_agent_memory.plot_all_target_simulated_data_collected_data()
        analyser_agent_memory.plot_position_target_simulated_data_collected_data()
        analyser_agent_all_memory.plot_position_target_simulated_data_collected_data()

        """Specific to each target"""
        for target in room.information_simulation.Target_list:
            analyser_agent_memory.plot_a_target_simulated_data_collected_data(target.id)
            # analyser_kalman_global.plot_a_target_simulated_data_collected_data(target.id)

    print("Done !")