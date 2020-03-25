import shutil
import os
import threading

from multi_agent.tools.link_target_camera import *
from multi_agent.tools.map_region_dyn import *
from multi_agent.tools.estimator import *
from my_utils.GUI.GUI import *
from my_utils.motion import *
from my_utils.my_IO.IO_map import *
from my_utils.my_IO.IO_data import *
from constants import *
from plot_functions.plot_targetEstimator import *


def clean_mailbox():
    shutil.rmtree("mailbox", ignore_errors=True)
    os.mkdir("mailbox")

class App:
    def __init__(self, fileName="My_new_map"):
        # Clean the file mailbox
        self.exact_data_target = Target_TargetEstimator()  # utilisé comme une simple liste, raison pour laquelle c'est une targetEstimator ?
        # TODO: check that
        clean_mailbox()

        #Path for logn data,plot ...
        constants.ResultsPath.name_simulation = fileName
        create_structur_to_save_data()

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
        if USE_GUI == 1:
            self.myGUI = GUI()

    def init(self):


        # Creation from the room with the given description
        self.room = Room()
        # Loading the map from a txt file, in map folder
        load_room_from_txt(self.filename + ".txt",self.room)


        # Adding one agent user
        self.room.init_AgentUser(1)
        for agent in self.room.agentCams_list:
            agent.init_and_set_room_description(self.room)
        for agent in self.room.agentUser_list:
            agent.init_and_set_room_description(self.room)

        self.room.add_del_target_timed()
        self.room.des_activate_camera_agentCam_timed()

        # Computing the vision in the room taking into account only fix objects
        self.static_region = MapRegionStatic(self.room)
        self.dynamic_region = MapRegionDynamic(self.room)

        if USE_static_analysis:
            self.static_region.init(STATIC_ANALYSIS_PRECISION)
            self.static_region.compute_all_map(STATIC_ANALYSIS_PRECISION)
        if USE_dynamic_analysis_simulated_room:
            self.dynamic_region.init(DYNAMIC_ANALYSIS_PRECISION)
        # Starting the multi_agent simulation
        if USE_agent:
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
            for target in self.room.active_Target_list:
                target.save_position()
                self.exact_data_target.add_create_target_estimator(self.room.time, -1, -1, target.id, target.signature,
                                                                   target.xc, target.yc, target.radius, target.type)
                move_Target(target, delta_time)
            time_old = time.time()


    def main(self):
        run = True
        reset = False

        # independent thread moving the targets
        targets_moving_thread = threading.Thread(target=self.move_all_targets_thread)
        targets_moving_thread.start()

        time_start = time.time()

        # Events loop
        while run:
            time.sleep(constants.TIME_BTW_FRAME)

            # To restart the simulation, press r
            if reset:
                self.room.time = 0
                if USE_agent:
                    for agent in self.room.agentCams_list:
                        agent.clear()
                    for agent in self.room.agentUser_list:
                        agent.clear()
                clean_mailbox()
                self.init()
                reset = False

            # adding/removing target to the room
            self.room.add_del_target_timed()
            self.room.des_activate_camera_agentCam_timed()

            #theoritical calculation
            self.link_agent_target.update_link_camera_target()
            self.link_agent_target.compute_link_camera_target()

            # Updating GUI interface
            if USE_GUI == 1:
                if USE_dynamic_analysis_simulated_room:
                    region = self.dynamic_region
                    region.init(DYNAMIC_ANALYSIS_PRECISION)
                    self.dynamic_region.compute_all_map(DYNAMIC_ANALYSIS_PRECISION)
                else:
                    region = self.static_region
                    self.static_region.compute_all_map(STATIC_ANALYSIS_PRECISION)

                self.myGUI.updateGUI(self.room, region, self.link_agent_target.link_camera_target)
                (run, reset) = self.myGUI.GUI_option.getGUI_Info()

            # Closing the simulation after a given time if not using GUI
            if self.room.time > constants.T_MAX and USE_GUI == 1:
                run = False
                pygame.quit()
            elif self.room.time > constants.T_MAX:
                run = False

            # Updating the time
            self.room.time = time.time()-time_start
            for agent in self.room.active_AgentCams_list:
                agent.room_representation.time = self.room.time

        for agent in self.room.agentCams_list:
            agent.clear()

        for agent in self.room.agentUser_list:
            agent.clear()

        self.targets_moving = False
        targets_moving_thread.join()

        # Clean mailbox
        clean_mailbox()

        # save data
        if constants.SAVE_DATA:
            print("Saving data : generated")
            save_in_csv_file_dictionnary(constants.ResultsPath.DATA_REFERENCE, self.exact_data_target.to_csv())
            print("Data saved !")

        # plot graph
        if constants.GENERATE_PLOT:
            print("Generating plots ...")
            for agent in self.room.agentCams_list:
                plot_agent_memory = Analyser_Target_TargetEstimator_FormatCSV(agent.id, constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT, self.filename)
                plot_agent_memory.plot_all_target_simulated_data_collected_data()

            for agent in self.room.agentUser_list:
                plot_agent_memory = Analyser_Target_TargetEstimator_FormatCSV(agent.id, constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT, self.filename)
                plot_agent_all_memory = Analyser_Agent_Target_TargetEstimator_FormatCSV(agent.id, constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_ALL_AGENT, self.filename)
                plot_agent_memory.plot_all_target_simulated_data_collected_data()
                plot_agent_memory.plot_position_target_simulated_data_collected_data()
                plot_agent_all_memory.plot_position_target_simulated_data_collected_data()
                for target in self.room.information_simulation.Target_list:
                    plot_agent_memory.plot_a_target_simulated_data_collected_data(target.id)

            print("Done !")


def execute():
    myApp = App()
    myApp.main()


if __name__ == "__main__":
    execute()
