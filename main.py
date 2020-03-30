import shutil
import os
import threading
import sys

from multi_agent.tools.link_target_camera import *
from multi_agent.tools.map_region_dyn import *
from multi_agent.tools.estimator import *
from my_utils.GUI.GUI import *
from my_utils.motion import *
from my_utils.my_IO.IO_map import *
from my_utils.my_IO.IO_data import *
from constants import *
from plot_functions.plot_targetEstimator import *

import multi_agent.agent.agent_interacting_room_camera
import multi_agent.agent.agent_interacting_room_user


def clean_mailbox():
    shutil.rmtree("mailbox", ignore_errors=True)
    os.mkdir("mailbox")


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


class App:
    def __init__(self, fileName="My_new_map"):
        constants.TIME_START = time.time()

        # Clean the file mailbox
        self.exact_data_target = Target_TargetEstimator()  # utilisé comme une simple liste, raison pour laquelle c'est une targetEstimator ?
        # TODO: check that
        clean_mailbox()

        # Path for logn data,plot ...
        constants.ResultsPath.name_simulation = fileName
        create_structur_to_save_data()
        shutil.copy("map/" + fileName + ".txt", constants.ResultsPath.MAIN_FOLDER)

        """Loading the room from the txt.file"""
        self.filename = fileName

        """CAREFULL: all that depends on my room needs to be initialized again in init
        because my room is first initialized after room_txt.load_room_from_file"""
        self.room = Room()
        self.static_region = MapRegionStatic(self.room)
        self.dynamic_region = MapRegionDynamic(self.room)
        self.link_agent_target = LinkTargetCamera(self.room)

        # Used by the thread that moves the targets
        self.targets_moving = True

        self.init()
        if USE_GUI:
            self.myGUI = GUI()

    def init(self):

        # Creation from the room with the given description
        self.room = Room()
        # Loading the map from a txt file, in map folder
        load_room_from_txt(self.filename + ".txt", self.room)

        # Adding one agent user
        self.room.init_AgentUser(1)
        for agent in self.room.agentCams_list:
            agent.init_and_set_room_description(self.room)
        for agent in self.room.agentUser_list:
            agent.init_and_set_room_description(self.room)

        self.room.add_del_target_timed()
        self.room.des_activate_agentCam_timed()
        self.room.des_activate_camera_agentCam_timed()

        # Computing the vision in the room taking into account only fix objects
        self.static_region = MapRegionStatic(self.room)
        self.dynamic_region = MapRegionDynamic(self.room)

        if USE_static_analysis:
            self.static_region.init(NUMBER_OF_POINT_STATIC_ANALYSIS, True)
            self.static_region.compute_all_map(NUMBER_OF_POINT_STATIC_ANALYSIS, True)
        if USE_dynamic_analysis_simulated_room:
            self.dynamic_region.init(NUMBER_OF_POINT_DYNAMIC_ANALYSIS)
        # Starting the multi_agent simulation
        for agent in self.room.active_AgentCams_list:
            agent.run()
        for agent in self.room.agentUser_list:
            agent.run()

        self.link_agent_target = LinkTargetCamera(self.room)
        self.link_agent_target.update_link_camera_target()

    def move_all_targets_thread(self):
        time_old = time.time()
        while self.targets_moving:

            time.sleep(TIME_BTW_TARGET_MOVEMENT)
            delta_time = time.time() - time_old

            self.link_agent_target.update_link_camera_target()
            self.link_agent_target.compute_link_camera_target()

            for target in self.room.active_Target_list:
                target.save_position()
                constants.time_when_target_are_moved = constants.get_time()
                self.exact_data_target.add_create_target_estimator(constants.time_when_target_are_moved,
                                                                   self.link_agent_target.get_agent_in_charge(
                                                                       target.id), -1, target.id, target.signature,
                                                                   target.xc, target.yc, target.vx, target.vy,
                                                                   target.ax, target.ay,
                                                                   target.radius, target.type)
                move_Target(target, delta_time)

                # theoritical calculation

            time_old = time.time()

    def main(self):
        run = True
        reset = False

        # independent thread moving the targets
        targets_moving_thread = threading.Thread(target=self.move_all_targets_thread)
        targets_moving_thread.start()

        # Events loop
        while run:
            time.sleep(constants.TIME_BTW_FRAME)

            # To restart the simulation, press r
            if reset:
                multi_agent.agent.agent_interacting_room_camera.AgentCam.number_agentCam_created = 0
                multi_agent.agent.agent_interacting_room_user.AgentUser.number_agentUser_created = 0
                constants.TIME_START = time.time()
                for agent in self.room.agentCams_list:
                    agent.clear()
                for agent in self.room.agentUser_list:
                    agent.clear()
                clean_mailbox()
                self.init()
                reset = False

            # adding/removing target to the room
            self.room.add_del_target_timed()
            self.room.des_activate_agentCam_timed()
            self.room.des_activate_camera_agentCam_timed()

            # Updating GUI interface
            if USE_GUI:
                if USE_dynamic_analysis_simulated_room:
                    region = self.dynamic_region
                    region.init(NUMBER_OF_POINT_DYNAMIC_ANALYSIS)
                    self.dynamic_region.compute_all_map(NUMBER_OF_POINT_DYNAMIC_ANALYSIS)
                else:
                    region = self.static_region
                    self.static_region.compute_all_map(NUMBER_OF_POINT_STATIC_ANALYSIS, True)

                self.myGUI.updateGUI(self.room, region, self.link_agent_target.link_camera_target)
                (run, reset) = self.myGUI.GUI_option.getGUI_Info()

            # Closing the simulation after a given time if not using GUI
            if constants.get_time() > constants.TIME_STOP and USE_GUI:
                run = False
                pygame.quit()
            elif constants.get_time() > constants.TIME_STOP:
                run = False

        self.targets_moving = False
        for agent in self.room.agentCams_list:
            agent.clear()

        for agent in self.room.agentUser_list:
            agent.clear()

        targets_moving_thread.join()

        # Clean mailbox
        clean_mailbox()

        # save data
        if constants.SAVE_DATA:
            print("Saving data : generated")
            save_in_csv_file_dictionnary(constants.ResultsPath.SAVE_LOAD_DATA_REFERENCE,
                                         self.exact_data_target.to_csv())
            print("Data saved !")

        # plot graph
        if constants.GENERATE_PLOT:
            plot_res(self.room, self.filename)


def execute():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "My_new_map"
    myApp = App(filename)
    myApp.main()


if __name__ == "__main__":
    execute()
