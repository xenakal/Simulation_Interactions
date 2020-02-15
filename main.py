import shutil
import os
from init import *
from utils.GUI.GUI import *
from utils.motion import *


def clean_mailbox():
    shutil.rmtree("utils/mailbox", ignore_errors=True)
    os.mkdir("utils/mailbox")


INCLUDE_ERROR = False


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
        t = 0
        tmax = T_MAX
        run = True
        reset = False

        while run:  # Events loop
            if reset:
                t = 0
                for agent in self.myRoom.agentCams:
                    agent.clear()
                clean_mailbox()
                self.myRoom = set_room(self.scenario)
                reset = False

            time.sleep(TIME_BTW_FRAMES)  # so that the GUI doesn't go to quick

            # Object are moving in the room
            for target in self.myRoom.targets:
                target.save_position()
                moveTarget(target, 1, self.myRoom)

            if self.useGUI == 1:
                self.myGUI.updateGUI(self.myRoom)
                (run, reset) = self.myGUI.GUI_option.getGUI_Info()

            if t > tmax:
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
