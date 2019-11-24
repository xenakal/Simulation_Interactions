from elements.room import *
from utils.GUI import *


class App:
    def __init__(self, useGUI=1, scenario=0):

        # Here by changing only the vectors it is possible to create as many scenario as we want !
        if scenario == 0:
            # Options for the target
            self.x_tar = numpy.array([55, 200, 40, 150])
            self.y_tar = numpy.array([55, 140, 280, 150])
            self.vx_tar = numpy.array([0, 1, 0, 0])
            self.vy_tar = numpy.array([0, 0, 0, 0])
            self.size_tar = numpy.array([5, 5, 5, 5])
            self.label_tar = numpy.array(['fix', 'target', 'obstruction', 'fix'])
            # Options for the cameras
            self.x_cam = numpy.array([10, 310, 10, 310, ])
            self.y_cam = numpy.array([10, 10, 310, 310])
            self.angle_cam = numpy.array([45, 135, 315, 225])
            self.angle_view_cam = numpy.array([60, 60, 60, 60])
        elif scenario == 1:
            # Options for the target
            self.x_tar = numpy.array([150])
            self.y_tar = numpy.array([150])
            self.vx_tar = numpy.array([0])
            self.vy_tar = numpy.array([0])
            self.size_tar = numpy.array([20])
            self.label_tar = numpy.array(['fix'])
            # Options for the cameras
            self.x_cam = numpy.array([10, 310, 10, 310, ])
            self.y_cam = numpy.array([10, 10, 310, 310])
            self.angle_cam = numpy.array([45, 135, 315, 225])
            self.angle_view_cam = numpy.array([60, 60, 60, 60])
        elif scenario == 2:
            # Options for the target
            self.x_tar = numpy.array([150, 20, 50, 110])
            self.y_tar = numpy.array([40, 20, 250, 280])
            self.vx_tar = numpy.array([0, 0, 0, 0])
            self.vy_tar = numpy.array([0, 0, 0, 0])
            self.size_tar = numpy.array([30, 10, 10, 15])
            self.label_tar = numpy.array(['fix', 'fix', 'fix', 'fix'])
            # Options for the cameras
            self.x_cam = numpy.array([150])
            self.y_cam = numpy.array([150])
            self.angle_cam = numpy.array([120])
            self.angle_view_cam = numpy.array([60])

        # Creating the room, the target and the camera
        self.myRoom = Room()
        self.myRoom.createTargets(self.x_tar, self.y_tar, self.vx_tar, self.vy_tar, self.label_tar, self.size_tar)
        self.myRoom.createCameras(self.x_cam, self.y_cam, self.angle_cam, self.angle_view_cam)

        # The program can also run completely with out the GUI interface
        self.useGUI = useGUI
        if useGUI == 1:
            # setting the GUI interface
            self.myGUI = GUI()
            self.updateGUI()

    def main(self):
        while True:  # events loop
            # camera is taking a picture
            for camera in self.myRoom.cameras:
                camera.takePicture(self.myRoom.targets)

            # Object are moving in the room
            for target in self.myRoom.targets:
                target.moveTarget(1)

            if self.useGUI == 1:
                # time.sleep(1) #so that the GUI does go to quick
                self.updateGUI()

        pygame.quit()

    def updateGUI(self):
        self.myGUI.drawRoom(self.myRoom.coord)

        for target in self.myRoom.targets:
            self.myGUI.drawTarget(target.xc, target.yc, target.size, target.id, target.label, self.myRoom.coord)

        for camera in self.myRoom.cameras:
            self.myGUI.drawCam(camera.xc, camera.yc, camera.alpha, camera.beta, camera.id)

        self.myGUI.drawProjection(self.myRoom)
        self.myGUI.screenDetectedTarget(self.myRoom)
        self.myGUI.updateScreen()


if __name__ == "__main__":
    # execute only if run as a script
    myApp = App(1, 0)
    myApp.main()
