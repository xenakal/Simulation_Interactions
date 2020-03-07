from my_utils.GUI.GUI import*
from my_utils.GUI.button import*
import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

CAMERA = (200, 0, 0)
PREDICTION = (100, 100, 100)

FIX = (200, 120, 0)
TARGET = (0, 250, 0)
OBSTRUCTION = (0, 50, 0)

class GUI_Agent_Target_Detected:
    def __init__(self,screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

    def screenDetectedTarget(self, myRoom):
        x_off = 400
        y_off = 60
        color = RED

        n = 0
        for camera in myRoom.cameras:
            label = self.font.render("camera " + str(camera.id), 10, WHITE)
            self.screen.blit(label, (x_off, y_off + n * 20))
            n = n + 1

        n = 0
        label = self.font.render("target ", 10, WHITE)
        self.screen.blit(label, (x_off, y_off - 20))
        for target in myRoom.targets:
            label = self.font.render(str(target.id), 10, WHITE)
            self.screen.blit(label, (x_off + 80 + n * 20, y_off - 20))
            n = n + 1

        m = 0
        for camera in myRoom.cameras:
            n = 0
            for target in myRoom.targets:
                color = RED
                for targetDetected in camera.targetDetectedList.copy():
                    if target == targetDetected[0]:
                        color = GREEN
                        break
                    else:
                        color = RED

                pygame.draw.circle(self.screen, color, (x_off + 88 + n * 20, y_off + 7 + m * 20), 5)
                n = n + 1
            m = m + 1