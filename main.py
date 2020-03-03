import shutil
import os
import pygame
from init import *
from my_utils.GUI.GUI import *
from my_utils.motion import *


def clean_mailbox():
    shutil.rmtree("my_utils/mailbox", ignore_errors=True)
    os.mkdir("my_utils/mailbox")


INCLUDE_ERROR = True
T_MAX = 1000
TIME_BTW_FRAMES = 0.1



class App:
    def __init__(self, useGUI=1, scenario=0):
        # Clean the file mailbox
        clean_mailbox()

        # Creating the room, the target and the camera
        self.scenario = scenario
        self.myRoom = set_room(scenario)

        self.useGUI = useGUI
        if useGUI == 1:
            self.myGUI = GUI()

    def main(self):
        tmax = T_MAX
        run = True
        reset = False

        while run:  # Events loop
            if reset:
                self.myRoom.time = 0
                for agent in self.myRoom.agentCams:
                    agent.clear()
                clean_mailbox()
                self.myRoom = set_room(self.scenario)
                reset = False

            time.sleep(TIME_BTW_FRAMES)  # so that the GUI doesn't go to quick

            #Check if object needs to appear or to disappear
            self.myRoom.add_del_target_timed()

            # Object are moving in the room
            for target in self.myRoom.targets:
                target.save_position()
                moveTarget(target, 1, self.myRoom)

            if self.useGUI == 1:
                self.myGUI.updateGUI(self.myRoom)
                (run, reset) = self.myGUI.GUI_option.getGUI_Info()


            if self.myRoom.time > tmax:
                run = False
                if self.useGUI == 1:
                    pygame.quit()

            self.myRoom.time = self.myRoom.time + 1

        for agent in self.myRoom.agentCams:
            agent.clear()

        # Clean mailbox
        clean_mailbox()


def execute():
    myApp = App(1, 6)
    myApp.main()


if __name__ == "__main__":
    execute()
