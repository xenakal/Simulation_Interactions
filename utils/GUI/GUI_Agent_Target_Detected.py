from utils.GUI.GUI import*
import pygame


class GUI_Agent_Target_Detected:
    def __init__(self,screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

    def screenDetectedTarget(self, myRoom):
        x_off = 350
        y_off = 200
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