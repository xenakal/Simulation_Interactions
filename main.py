import shutil
import os
import pygame
from init import *
from my_utils.GUI.GUI import *
from my_utils.motion import *
from my_utils.map import *
from multi_agent.agent_region import *

def clean_mailbox():
    shutil.rmtree("mailbox", ignore_errors=True)
    os.mkdir("mailbox")

TIME_BTW_FRAMES = 0.1

'''Option for class main'''
USE_GUI = 1
USE_agent = 0
USE_static_analysis = 1
T_MAX = 10000

'''Option for class agent'''
NAME_LOG_PATH = "log/log_agent/Agent"
NAME_MAILBOX = "mailbox/MailBox_Agent"
NUMBER_OF_MESSAGE_RECEIVE = 1  # 1= all message receive, 100 = almost nothing is received

'''Option for class agentCamera'''
TIME_PICTURE = .5
TIME_SEND_READ_MESSAGE = .1
MULTI_THREAD = 0

'''Option for class estimator'''
INCLUDE_ERROR = True
STD_MEASURMENT_ERROR = 2

'''Option for class predication'''
NUMBER_PREDICTIONS = 5
PREVIOUS_POSITIONS_USED = 7  # number of previous positions used to make the prediction of the next positions

'''Option for class map'''
PATH_TO_SAVE_MAP = "map/"
SAVE_MAP_NAME = "My_new_map.txt"
PATH_TO_LOAD_MAP = "map/"
LOAD_MAP_NAME = "My_new_map.txt"

'''Option for GUI'''
''' 180,100,1.5,1.5 for a Room (300,300)'''
X_OFFSET = 180
Y_OFFSET = 100
X_SCALE  = 1.5
Y_SCALE  = 1.5

'''Option for ROOM'''
WIDTH_ROOM = 300
LENGHT_ROOM = 300


class App:
    def __init__(self,fileName = "My_new_map.txt"):
        # Clean the file mailbox
        clean_mailbox()

        '''Loading the room from the txt.file'''
        self.filename = fileName
        self.room_txt = Room_txt()
        self.room_txt.load_room_from_txt(fileName)
        self.myRoom = self.room_txt.init_room()
        self.static_region = AgentRegion(self.myRoom)

        if USE_agent:
            for agent in self.myRoom.agentCams:
                agent.run()

        if USE_GUI == 1:
            self.myGUI = GUI(self.room_txt)

    def init(self):
        self.room_txt = Room_txt()
        self.room_txt.load_room_from_txt(self.filename)
        self.myRoom = self.room_txt.init_room()

        if USE_static_analysis == 1:
            self.static_region = AgentRegion(self.myRoom)
            self.static_region.compute(4)

        if USE_agent:
            for agent in self.myRoom.agentCams:
                agent.run()


    def main(self):
        tmax = T_MAX
        run = True
        reset = False



        while run:  # Events loop
            if reset:
                self.myRoom.time = 0

                if USE_agent:
                    for agent in self.myRoom.agentCams:
                        agent.clear()

                clean_mailbox()

                self.init()

                reset = False

            time.sleep(TIME_BTW_FRAMES)  # so that the GUI doesn't go to quick

            #Check if object needs to appear or to disappear
            self.myRoom.add_del_target_timed()

            # Object are moving in the room
            for target in self.myRoom.targets:
                target.save_position()
                moveTarget(target, 1, self.myRoom)

            if USE_GUI == 1:
                self.myGUI.updateGUI(self.myRoom,self.static_region)
                (run, reset) = self.myGUI.GUI_option.getGUI_Info()


            if self.myRoom.time > tmax:
                run = False
                if USE_GUI == 1:
                    pygame.quit()

            self.myRoom.time = self.myRoom.time + 1

        for agent in self.myRoom.agentCams:
            agent.clear()

        # Clean mailbox
        clean_mailbox()


def execute():
    myApp = App()
    #myApp = App(1, "bug1.txt")
    myApp.main()


if __name__ == "__main__":
    execute()
