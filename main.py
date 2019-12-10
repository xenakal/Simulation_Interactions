import shutil
import os
from elements.room import *
from utils.GUI import *


TIMESTEP = 0.5
TIMEPAUSE = 0.2

USE_AGENT = 1


class App:
    def __init__(self, useGUI=1, scenario=0):
        #clean the file mailbox
        shutil.rmtree("mailbox", ignore_errors = True)
        os.mkdir("mailbox")

        # Here by changing only the vectors it is possible to create as many scenario as we want !
        if scenario == -1:
            self.x_tar = numpy.array([55])
            self.y_tar = numpy.array([55])
            self.vx_tar = numpy.array([4])
            self.vy_tar = numpy.array([4])
            self.traj_tar = numpy.array(["linear"])
            self.trajChoice_tar = numpy.array([0])
            self.size_tar = numpy.array([5])
            self.label_tar = numpy.array(['target'])
            # Options for the cameras
            self.x_cam = numpy.array([10])
            self.y_cam = numpy.array([10])
            self.angle_cam = numpy.array([75])
            self.angle_view_cam = numpy.array([60])
            self.fix_cam = [1]

        elif scenario == 0:
            # Options for the target
            self.x_tar = numpy.array([55, 200, 40, 150])
            self.y_tar = numpy.array([55, 140, 280, 150])
            self.vx_tar = numpy.array([0, 4, 0, 0])
            self.vy_tar = numpy.array([0, 0, 0, 0])
            self.traj_tar = numpy.array(['linear', 'linear', 'linear', 'potential_field'])
            self.trajChoice_tar = numpy.array([0,0,0,0])
            self.size_tar = numpy.array([5, 5, 5, 5])
            self.label_tar = numpy.array(['fix', 'fix', 'obstruction', 'fix'])
            # Options for the cameras
            self.x_cam = numpy.array([10, 310, 10, 310, ])
            self.y_cam = numpy.array([10, 10, 310, 310])
            self.angle_cam = numpy.array([45, 135, 315, 225])
            self.angle_view_cam = numpy.array([60, 60, 60, 60])
            self.fix_cam = [1, 1, 1, 1]

        elif scenario == 1:
            # Options for the target
            self.x_tar = numpy.array([155, 155, 200, 50])
            self.y_tar = numpy.array([155, 260, 170, 250])
            self.vx_tar = numpy.array([0, 0, 5, 0])
            self.vy_tar = numpy.array([0, 0, 0, 0])
            self.traj_tar = numpy.array(['linear', 'linear', 'potential_field', 'linear'])
            self.trajChoice_tar = numpy.array([0,0,0,0])
            self.size_tar = numpy.array([35, 35, 5, 20])
            self.label_tar = numpy.array(['fix', "fix", "target", "fix"])
            # Options for the cameras
            self.x_cam = numpy.array([10, 310, 10, 310, ])
            self.y_cam = numpy.array([10, 10, 310, 310])
            self.angle_cam = numpy.array([45, 135, 315, 225])
            self.angle_view_cam = numpy.array([60, 60, 60, 60])
            self.fix_cam = [1, 1, 1, 1]

        elif scenario == 2:
            # Options for the target
            self.x_tar = numpy.array([250, 200, 150, 100, 50, 50, 50, 50, 50, 100, 150, 200, 250, 250, 250, 250])
            self.y_tar = numpy.array([50, 50, 50, 50, 50, 100, 150, 200, 250, 250, 250, 250, 250, 200, 150, 100])
            self.trajChoice_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.vx_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.vy_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.traj_tar = numpy.array(
                ['linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear',
                 'linear', 'linear'
                    , 'linear', 'linear', 'linear', 'linear'])
            self.size_tar = numpy.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10])
            self.label_tar = numpy.array(['fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix',
                                          'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix'])
            # Options for the cameras
            self.x_cam = numpy.array([150])
            self.y_cam = numpy.array([150])
            self.angle_cam = numpy.array([90])
            self.angle_view_cam = numpy.array([60])
            self.fix_cam = [0]

        elif scenario == 3:
            # Options for the target
            self.x_tar = numpy.array([250, 200, 150, 100, 50, 50, 50, 50, 50, 100, 150, 200, 250, 250, 250, 250])
            self.y_tar = numpy.array([50, 50, 50, 50, 50, 100, 150, 200, 250, 250, 250, 250, 250, 200, 150, 100])
            self.vx_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.vy_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.traj_tar = numpy.array(
                ['linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear', 'linear',
                 'linear', 'linear', 'linear', 'linear', 'linear', 'linear'])
            self.trajChoice_tar = numpy.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.size_tar = numpy.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10])
            self.label_tar = numpy.array(['fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix',
                                          'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix', 'fix'])
            # Options for the cameras
            self.x_cam = numpy.array([150])
            self.y_cam = numpy.array([150])
            self.angle_cam = numpy.array([90])
            self.angle_view_cam = numpy.array([10])
            self.fix_cam = [0]

        elif scenario == 4:
            # Options for the target
            self.x_tar = numpy.array([30, 40, 45, 30, 120, 200])
            self.y_tar = numpy.array([30, 40, 30, 60, 155, 20])
            self.vx_tar = numpy.array([0, 0, 0, 0, 0, 0])
            self.vy_tar = numpy.array([0, 0, 0, 0, 0, 5])
            self.traj_tar = numpy.array(['linear', 'linear', 'linear', 'linear', 'linear', 'linear'])
            self.trajChoice_tar = numpy.array([0, 0, 0, 0, 0, 5])
            self.size_tar = numpy.array([5, 5, 5, 10, 20, 5])
            self.label_tar = numpy.array(['fix', 'fix', 'fix', 'fix', 'fix', 'target'])
            # Options for the cameras
            self.x_cam = numpy.array([150, 20, 20])
            self.y_cam = numpy.array([150, 20, 250])
            self.angle_cam = numpy.array([0, 45, -45])
            self.angle_view_cam = numpy.array([60, 60, 60])
            self.fix_cam = [1, 1, 1]

        elif scenario == 5:
            # Options for the target
            self.x_tar = numpy.array([155, 20])
            self.y_tar = numpy.array([155, 20])
            self.vx_tar = numpy.array([0, 0])
            self.vy_tar = numpy.array([0, 0])
            self.traj_tar = numpy.array(['linear', 'linear'])
            self.trajChoice_tar = numpy.array([0, 1])
            self.size_tar = numpy.array([20, 5, 6])
            self.label_tar = numpy.array(['fix', 'target'])
            # Options for the cameras
            self.x_cam = numpy.array([10, 310])
            self.y_cam = numpy.array([155, 155])
            self.angle_cam = numpy.array([0, 180])
            self.angle_view_cam = numpy.array([60, 60])
            self.fix_cam = [1, 1, 1]
        
        elif scenario == 6:
            # Options for the target
            self.x_tar = numpy.array([155, 20])
            self.y_tar = numpy.array([155, 20])
            self.vx_tar = numpy.array([0, 0])
            self.vy_tar = numpy.array([0, 0])
            self.traj_tar = numpy.array(['linear','fix'])
            self.trajChoice_tar = numpy.array([0, 1])
            self.size_tar = numpy.array([20, 5, 6])
            self.label_tar = numpy.array(['fix', 'target'])
            # Options for the cameras
            self.x_cam = numpy.array([10, 310, 155])
            self.y_cam = numpy.array([155, 155, 10])
            self.angle_cam = numpy.array([0, 180, 90])
            self.angle_view_cam = numpy.array([60, 60 ,30])
            self.fix_cam = [1, 1, 1]

        else:
            print("this scenario number doesn't exist, sorry...")
            return

        # Creating the room, the target and the camera
        self.myRoom = Room()
        self.myRoom.createTargets(self.x_tar, self.y_tar, self.vx_tar, self.vy_tar, self.traj_tar,self.trajChoice_tar, self.label_tar,
                                  self.size_tar)
        if USE_AGENT == 0:
            self.myRoom.createCameras(self.x_cam, self.y_cam, self.angle_cam, self.angle_view_cam, self.fix_cam)
        elif USE_AGENT == 1:
            self.myRoom.createAgentCam(self.x_cam, self.y_cam, self.angle_cam, self.angle_view_cam, self.fix_cam,self.myRoom)
            
            for agent in self.myRoom.agentCam:
                agent.run()
        # The program can also run completely with out the GUI interface
        self.useGUI = useGUI
        if useGUI == 1:
            # setting the GUI interface
            self.myGUI = GUI()
            self.updateGUI()

    def main(self):
        t = 0
        tmax = 1000
        run = True
        while run:  # Events loop
            
            if USE_AGENT == 0:
                # camera is taking a picture
                for camera in self.myRoom.cameras:
                    camera.run(self.myRoom)

            # Object are moving in the room
            for target in self.myRoom.targets:
                target.moveTarget(1, self.myRoom)

            if self.useGUI == 1:
                time.sleep(TIMEPAUSE)  # so that the GUI doesn't go to quick
                self.updateGUI()
                run = getGUI_Info()

            if t > tmax:
                run = False
                if self.useGUI == 1:
                    pygame.quit()

            self.myRoom.time = self.myRoom.time + 1
    
        for agent in self.myRoom.agentCam:
            agent.clear()
        
        shutil.rmtree("mailbox", ignore_errors=True)
        os.mkdir("mailbox")
        
    def updateGUI(self):
        self.myGUI.drawRoom(self.myRoom.coord)
        self.myGUI.drawTarget(self.myRoom.targets, self.myRoom.coord)
        self.myGUI.drawCam(self.myRoom.cameras)
        self.myGUI.drawProjection(self.myRoom)
        self.myGUI.screenDetectedTarget(self.myRoom)
        self.myGUI.drawPredictions(self.myRoom)
        self.myGUI.drawTargetFollowedByCam(self.myRoom)
        updateScreen()


if __name__ == "__main__":
    # execute only if run as a script
    myApp = App(1, 5)
    myApp.main()
