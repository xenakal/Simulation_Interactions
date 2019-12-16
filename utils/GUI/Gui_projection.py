from utils.line import*
from elements.camera import*
from utils.GUI.GUI import*
import pygame

class GUI_projection:
    def __init__(self,screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

    def drawProjection(self, myRoom):
        x_off = 10
        y_off = 330

        pygame.draw.rect(self.screen, BLACK, (x_off, y_off, 500, 200))

        n = 0
        for camera in myRoom.cameras:
            label = self.font.render("camera " + str(camera.id), 10, WHITE)
            self.screen.blit(label, (x_off, y_off + n * 30))
            pygame.draw.circle(self.screen, CAMERA, (x_off + 85, y_off + 8 + n * 30), 5)

            m = 0
            ref = camera.limitProjection.copy()
            detected = camera.targetDetectedList.copy()
            try:
                detected.reverse()
            except AttributeError:
                print("Unable to resverse, cam : " + str(camera.id))

            for target in detected:
                projection = target[1]
                d0 = math.floor(distanceBtwTwoPoint(ref[0], ref[1], projection[0], projection[1]))
                d1 = math.floor(distanceBtwTwoPoint(ref[0], ref[1], projection[2], projection[3]))
                pygame.draw.circle(self.screen, target[0].color, (x_off + 85 + d0, y_off + 8 + n * 30), 5)
                pygame.draw.circle(self.screen, target[0].color, (x_off + 85 + d1, y_off + 8 + n * 30), 5)
                pygame.draw.line(self.screen, target[0].color, (x_off + 85 + d0, y_off + 8 + n * 30),
                                 (x_off + 85 + d1, y_off + 8 + n * 30), 2)
                label = self.font.render(str(math.floor(target[0].id)), 10, target[0].color)
                self.screen.blit(label, (x_off + 85 + math.ceil((d0 + d1) / 2), y_off + 10 + n * 30))

            if len(ref) > 0:
                dref = math.floor(distanceBtwTwoPoint(ref[0], ref[1], ref[2], ref[3]))
                pygame.draw.circle(self.screen, WHITE, (x_off + 85, y_off + 8 + n * 30), 5)
                pygame.draw.circle(self.screen, WHITE, (x_off + 85 + dref, y_off + 8 + n * 30), 5)
            n = n + 1
