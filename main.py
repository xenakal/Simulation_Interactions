import shutil
import os
from utils.GUI.GUI import *
from utils.motion import *
from init import *

TIMESTEP = 0.5
T_MAX = 1000
TIME_BTW_FRAMES = 0.1

class App:
    def __init__(self, useGUI=1, scenario=0):
        #clean the file mailbox
        shutil.rmtree("utils/mailbox", ignore_errors = True)
        os.mkdir("utils/mailbox")

        # Creating the room, the target and the camera
        self.myRoom = set_room(scenario)

        self.useGUI = useGUI
        if useGUI == 1:
            self.myGUI = GUI()

    def main(self):
        t = 0
        tmax = T_MAX
        run = True
        while run:  # Events loop
            time.sleep(TIME_BTW_FRAMES)  # so that the GUI doesn't go to quick

            # Object are moving in the room
            for target in self.myRoom.targets:
                target.save_position()
                moveTarget(target,1,self.myRoom)

            if self.useGUI == 1:
                self.myGUI.updateGUI(self.myRoom)
                run = self.myGUI.GUI_option.getGUI_Info()

            if t > tmax:
                run = False
                if self.useGUI == 1:
                    pygame.quit()

            self.myRoom.time = self.myRoom.time + 1
    
        for agent in self.myRoom.agentCam:
            agent.clear()
        
        shutil.rmtree("utils/mailbox", ignore_errors=True)
        os.mkdir("utils/mailbox")


if __name__ == "__main__":
    # execute only if run as a script
    myApp = App(1, 6)
    myApp.main()
