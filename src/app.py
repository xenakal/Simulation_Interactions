import threading
import sys

import pygame

from src.multi_agent.elements.room import Room
from src.multi_agent.tools.link_target_camera import *
from src.multi_agent.tools.map_region_dyn import *
from src.multi_agent.tools.estimator import *
from src.my_utils.GUI.GUI import GUI
from src.my_utils.motion import move_Target
from src.my_utils.my_IO.IO_map import *
from src.my_utils.my_IO.IO_data import *
from src.constants import *

import src.multi_agent.agent.agent_interacting_room_camera
import src.multi_agent.agent.agent_interacting_room_user
from src.plot_functions.main_plot import plot_res


def clean_mailbox():
    shutil.rmtree("mailbox", ignore_errors=True)
    os.mkdir("mailbox")


class App:
    def __init__(self, file_name=None, is_kalman_distributed=None, kalman_type=None, t_stop=None,t_scale=None):
        """"""

        """ 
            Modification from the constant file to get the desired parameter once runing from main
            By default set to NONE, in this case the value taken is the one set by the constants.py file itself
        """
        if not (file_name is None):
            constants.ResultsPath.name_simulation = file_name
        if not (is_kalman_distributed is None):
            constants.DISTRIBUTED_KALMAN = is_kalman_distributed
        if not (kalman_type is None):
            constants.KALMAN_MODEL_MEASUREMENT_DIM = kalman_type
        if not (t_stop is None):
            constants.TIME_STOP = t_stop
        if not (t_scale is None):
            constants.SCALE_TIME = t_scale

        """
            Setting all the folders and cleaning mailboxes
        """
        # TODO: check mailbox (alex c'est toi qui a mis ça je pense on peut retirer ?)
        clean_mailbox()
        create_structur_to_save_data()
        shutil.copy(constants.MapPath.MAIN_FOLDER + file_name + ".txt", constants.ResultsPath.MAIN_FOLDER)


        """
            Creation of a logger to store every data
        """
        self.log_app = create_logger(constants.ResultsPath.LOG_FOLDER, "/Log_app", -1)
        self.log_app.info("app started")
        self.log_app.info("file name : " + str(file_name))
        self.log_app.info("Using distributed kalman : " + str(is_kalman_distributed))
        self.log_app.info("Kalman type: " + str(kalman_type))
        self.log_app.info("Simulation end in time : %.02f s", t_stop)
        self.log_app.info("Scaling time factor : %.02f s", t_scale)

        """
            Create a structure to save the generated data
        """
        self.exact_data_target = Target_TargetEstimator()  # utilisé comme une simple liste, raison pour laquelle c'est une targetEstimator ?

        """
            Create app variables
        """
        self.filename = file_name

        """
            All required object needed to create data, analyse ideal solutions 
        """
        self.room = None
        self.static_region = None
        self.dynamic_region = None
        self.link_agent_target = None
        self.targets_moving_thread = None

        self.init()
        if USE_GUI:
            self.myGUI = GUI()

    def init(self):
        """"""
        self.log_app.info("Starting init ...")
        clean_mailbox()

        """Reset the number of agent created"""
        src.multi_agent.agent.agent_interacting_room_camera.AgentCam.number_agentCam_created = 0
        src.multi_agent.agent.agent_interacting_room_user.AgentUser.number_agentUser_created = 0

        """Start the time"""
        constants.TIME_START = time.time()

        """Create a new room and load it from it representation in .txt file"""
        self.room = Room()
        load_room_from_txt(self.filename + ".txt", self.room)
        "Add one agent user to this room"
        self.room.init_AgentUser(1)

        """Set the room representation for every agent based the information given in the room,
         only agent position and set_fix target are here taken into account """
        for agent in self.room.information_simulation.agentCams_list:
            agent.init_and_set_room_description(self.room)

        for agent in self.room.information_simulation.agentUser_list:
            agent.init_and_set_room_description(self.room)

        self.room.add_del_target_timed()
        self.room.des_activate_agentCam_timed()
        self.room.des_activate_camera_agentCam_timed()

        """Creating tools to analyse the situation based on the created data  => it means the best solution we could have"""
        self.static_region = MapRegionStatic(self.room)
        self.dynamic_region = MapRegionDynamic(self.room)

        if USE_static_analysis:
            self.static_region.init(NUMBER_OF_POINT_STATIC_ANALYSIS, True)

        if USE_dynamic_analysis_simulated_room:
            self.dynamic_region.init(NUMBER_OF_POINT_DYNAMIC_ANALYSIS)


        self.link_agent_target = LinkTargetCamera(self.room)
        self.link_agent_target.update_link_camera_target()


        """Agents start to run"""
        for agent in self.room.information_simulation.agentCams_list:
            agent.run()

        for agent in self.room.information_simulation.agentUser_list:
           agent.run()


        """Target start to move"""
        self.targets_moving = True
        self.targets_moving_thread = threading.Thread(target=self.move_all_targets_thread)
        self.targets_moving_thread.start()

        self.log_app.info("Init done")

    def clear(self):

        self.log_app.info("Clear ...")

        "Stopping thread moving target"
        self.targets_moving = False
        self.targets_moving_thread.join()

        "Stopping each agent"
        for agent in self.room.information_simulation.agentCams_list:
            agent.clear()
        for agent in self.room.information_simulation.agentUser_list:
            agent.clear()

        "Clean mailbox"
        clean_mailbox()

        "Saving data"
        if constants.SAVE_DATA:
            self.log_app.info("Saving data : generated")
            print("Saving data : generated")
            save_in_csv_file_dictionnary(constants.ResultsPath.SAVE_LOAD_DATA_REFERENCE,self.exact_data_target.to_csv())

            self.log_app.info("Data saved !")
            print("Data saved !")

            # plot graph
            if constants.GENERATE_PLOT:
                self.log_app.info("Plotting data")
                plot_res(self.room, self.filename)
                self.log_app.info("Plotting done")

        self.log_app.info("App cleared !")

    def reset(self):
        self.log_app.info("Reset ...")
        self.clear()
        self.init()
        self.log_app.info("Reset done !")

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

        """Event loo^p"""
        while run:
            time.sleep(constants.TIME_BTW_FRAME)

            if reset:
                self.reset()
                reset = False

            """Events related to target agent ..."""
            self.room.add_del_target_timed()
            self.room.des_activate_agentCam_timed()
            self.room.des_activate_camera_agentCam_timed()

            """GUI related actions
                options - see GUI_option.py file
                
                push r - reset the simulatio from the start
                push s - to take a screen_shot from the window GUI
            """
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

            """Closing the simulation options"""
            if constants.get_time() > constants.TIME_STOP and USE_GUI:
                run = False
                pygame.quit()
            elif constants.get_time() > constants.TIME_STOP:
                run = False

        self.clear()


def execute():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "My_new_map"
    myApp = App(filename)
    myApp.main()


if __name__ == "__main__":
    execute()
