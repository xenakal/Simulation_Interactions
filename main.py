import shutil
import os
from elements.room import *
from multi_agent.link_target_camera import *
from multi_agent.map_region_dyn import *
from my_utils.GUI.GUI import *
from my_utils.motion import *
from my_utils.map_from_to_txt import *
from constants import *

def clean_mailbox():
    shutil.rmtree("mailbox", ignore_errors=True)
    os.mkdir("mailbox")




class App:
    def __init__(self, fileName="map_lele.txt"):
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
        self.room_txt.load_room_from_txt(self.filename)
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

    def main(self):
        tmax = T_MAX
        run = True
        reset = False

        while run:  # Events loop

            '''To restart the simulation, push r'''
            if reset:
                self.room.time = 0
                if USE_agent:
                    for agent in self.room.active_Target_list:
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
            if self.room.time > tmax and USE_GUI == 1:
                run = False
                pygame.quit()

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


def execute():
    myApp = App()
    myApp.main()


if __name__ == "__main__":
    execute()
