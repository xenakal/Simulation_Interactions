import shutil
import os
from multi_agent.elements.room import *
from multi_agent.tools.link_target_camera import *
from multi_agent.tools.map_region_dyn import *
from multi_agent.tools.estimator import *
from my_utils.GUI.GUI import *
from my_utils.motion import *
from my_utils.map_from_to_txt import *
from my_utils.to_csv import *
from constants import *
from plot_functions.plot_targetEstimator import *


def clean_mailbox():
    shutil.rmtree("mailbox", ignore_errors=True)
    os.mkdir("mailbox")


def create_structur_to_save_data():
    shutil.rmtree(constants.SavePlotPath.MAIN_FOLDER, ignore_errors=True)
    "Folder where the data and plot are save"
    os.mkdir(constants.SavePlotPath.MAIN_FOLDER)
    "Save data"
    os.mkdir(constants.SavePlotPath.DATA_FOLDER)
    os.mkdir(constants.SavePlotPath.DATA_MEMORY_AGENT)
    os.mkdir(constants.SavePlotPath.DATA_MEMORY_ALL_AGENT)
    "Save plot"
    os.mkdir(constants.SavePlotPath.PLOT_FOLDER)
    os.mkdir(constants.SavePlotPath.PLOT_MEMORY_AGENT)
    os.mkdir(constants.SavePlotPath.PLOT_MEMORY_ALL_AGENT)


class App:
    def __init__(self, fileName="My_new_map"):
        # Clean the file mailbox
        clean_mailbox()

        '''Loading the room from the txt.file'''
        self.filename = fileName
        self.room_txt = Room_txt()

        '''ATTENTION all that depends on my room needs to be initialized again in init
        because my room is first initialized after room_txt.load_room_from_file'''
        self.room = Room()
        self.static_region = MapRegionStatic(self.room)
        self.dynamic_region = MapRegionDynamic(self.room)
        self.link_agent_target = LinkTargetCamera(self.room)

        self.init()
        if USE_GUI == 1:
            self.myGUI = GUI(self.room_txt)

    def init(self):
        """Loading the map from a txt file, in map folder"""
        self.room_txt = Room_txt()
        self.room_txt.load_room_from_txt(self.filename + ".txt")
        self.exact_data_target = Target_TargetEstimator()
        '''Creation from the room with the given description'''
        self.room = self.room_txt.init_room()
        '''Adding one agent user'''
        self.room.init_AgentUser(1)
        for agent in self.room.active_AgentCams_list:
            agent.init_and_set_room_description(self.room)
        for agent in self.room.active_AgentUser_list:
            agent.init_and_set_room_description(self.room)
        '''Computing the vision in the room taking in to account only fix object'''
        self.static_region = MapRegionStatic(self.room)
        self.dynamic_region = MapRegionDynamic(self.room)
        if USE_static_analysis:
            self.static_region.init(STATIC_ANALYSIS_PRECISION)
            self.static_region.compute_all_map(STATIC_ANALYSIS_PRECISION)
        if USE_dynamic_analysis_simulated_room:
            self.dynamic_region.init(STATIC_ANALYSIS_PRECISION_simulated_room)
        '''Starting the multi_agent simulation'''
        if USE_agent:
            if RUN_ON_A_THREAD == 1:
                for agent in self.room.active_AgentCams_list:
                    agent.run()
                for agent in self.room.active_AgentUser_list:
                    agent.run()

        self.link_agent_target = LinkTargetCamera(self.room)
        self.link_agent_target.update_link_camera_target()

        "to save the data"

        if constants.SAVE_DATA:
            constants.set_folder(self.filename)
            create_structur_to_save_data()
            pass

    def main(self):
        run = True
        reset = False

        while run:  # Events loop

            '''To restart the simulation, push r'''
            if reset:
                self.room.time = 0
                if USE_agent:
                    for agent in self.room.active_AgentCams_list:
                        agent.clear()
                    for agent in self.room.active_AgentUser_list:
                        agent.clear()
                clean_mailbox()
                self.init()
                reset = False

            '''adding/removing target to the room'''
            self.room.add_del_target_timed()
            # Object are moving in the room
            for target in self.room.active_Target_list:
                target.save_position()
                self.exact_data_target.add_create_target_estimator(self.room.time, -1, -1, target.id, target.signature,
                                                                   target.xc, target.yc, target.radius, target.type)
                move_Target(target, 1, self.room)

            '''
            RUN_ON_THREAD = 0, sequential approach, every agent are call one after the other
            RUN_ON_THREAD = 1, process executed in the same time, every agent is a thread
            '''
            if RUN_ON_A_THREAD == 0:
                random_order = self.room.active_AgentCams_list
                # random.shuffle(random_order,random)
                for agent in random_order:
                    agent.run()

                for agent in self.room.active_AgentUser_list:
                    agent.run()
            else:
                '''to slow donw the main thread in comparaison to agent thread'''
                time.sleep(TIME_BTW_FRAMES)

            self.link_agent_target.update_link_camera_target()
            self.link_agent_target.compute_link_camera_target()

            '''Updating GUI interface'''
            if USE_GUI == 1:
                if USE_dynamic_analysis_simulated_room:
                    region = self.dynamic_region
                    self.dynamic_region.compute_all_map(STATIC_ANALYSIS_PRECISION_simulated_room)
                else:
                    region = self.static_region

                self.myGUI.updateGUI(self.room, region, self.link_agent_target.link_camera_target)
                (run, reset) = self.myGUI.GUI_option.getGUI_Info()

            '''Closing the simulation after a given time if not using GUI'''
            if self.room.time > constants.T_MAX and USE_GUI == 1:
                run = False
                pygame.quit()
            elif self.room.time > constants.T_MAX:
                run = False

            '''Updating the time'''
            self.room.time = self.room.time + 1
            for agent in self.room.active_AgentCams_list:
                agent.room_representation.time = agent.room_representation.time + 1

        for agent in self.room.active_AgentCams_list:
            agent.clear()

        for agent in self.room.active_AgentUser_list:
            agent.clear()

        # Clean mailbox
        clean_mailbox()

        # save data
        if constants.SAVE_DATA:
            print("Saving data : generated")
            save_in_csv_file_dictionnary(constants.SavePlotPath.DATA_REFERENCE, self.exact_data_target.to_csv())
            print("Data saved !")

        # plot graph
        if constants.GENERATE_PLOT:
            print("Generating plots ...")
            for agent in self.room.active_AgentCams_list:
                plot_agent_memory = AnalyseMemoryAgent(agent.id, self.filename)
                plot_agent_memory.plot_all_target_simulated_data_collected_data()

            for agent in self.room.active_AgentUser_list:
                plot_agent_memory = AnalyseMemoryAgent(agent.id, self.filename)
                plot_agent_all_memory = AnalyseAllMemoryAgent(agent.id, self.filename)
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
