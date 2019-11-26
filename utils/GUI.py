import pygame
from pygame.locals import *
from utils.line import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

CAMERA = (200, 0, 0)

FIX = (200, 120, 0)
TARGET = (0, 250, 0)
OBSTRUCTION = (0, 50, 0)


class GUI:
    def __init__(self):
        pygame.init()
        # pygame.display.init()
        self.screen = pygame.display.set_mode((1220, 960), pygame.RESIZABLE)
        pygame.display.set_caption("Camera simulation")
        self.font = pygame.font.SysFont("monospace", 15)

    def drawRoom(self, tab, color=0):
        pygame.draw.rect(self.screen, WHITE, (tab[0], tab[1], tab[2], tab[3]))

    def drawTarget(self, targets, tab):
        for target in targets:
            color = RED

            if target.label == "fix":
                color = FIX
            elif target.label == "target":
                color = TARGET
            elif target.label == "obstruction":
                color = OBSTRUCTION

            # so that it is onltarget.yc draw in the square
            if (tab[0] <= target.xc + target.size <= tab[0] + tab[
                2] and tab[1] <= target.yc + target.size <= tab[1] + tab[3]):
                # render tetarget.xct
                label = self.font.render(str(target.id), 10, color)
                self.screen.blit(label, (target.xc + target.size / 2 + 5, target.yc + target.size / 2 + 5))
                # render form
                pygame.draw.circle(self.screen, color, (target.xc, target.yc), target.size)
                if target.size >= 5:
                    pygame.draw.circle(self.screen, target.color, (target.xc, target.yc),
                                       math.floor(target.size - 0.5 * target.size))

    def drawCam(self, cameras, color=0, l=100):
        for camera in cameras:
            # render text
            label = self.font.render(str(camera.id), 10, CAMERA)
            self.screen.blit(label, (camera.xc + 5, camera.yc + 5))
            # render form
            pygame.draw.circle(self.screen, CAMERA, (camera.xc, camera.yc), 5)
            pygame.draw.line(self.screen, BLACK, (camera.xc, camera.yc),
                             (camera.xc + l * math.cos(camera.alpha),
                              camera.yc + l * math.sin(camera.alpha)), 2)
            pygame.draw.line(self.screen, CAMERA, (camera.xc, camera.yc),
                             (camera.xc + l * math.cos(camera.alpha - (camera.beta / 2)),
                              camera.yc + l * math.sin(camera.alpha - (camera.beta / 2))), 2)
            pygame.draw.line(self.screen, CAMERA, (camera.xc, camera.yc),
                             (camera.xc + l * math.cos(camera.alpha + (camera.beta / 2)),
                              camera.yc + l * math.sin(camera.alpha + (camera.beta / 2))), 2)

    def screenDetectedTarget(self, myRoom):

        x_off = 350
        y_off = 50
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

        n = 0
        m = 0
        for camera in myRoom.cameras:
            n = 0
            for target in myRoom.targets:
                for targetDetected in camera.targetDetectedList:
                    if target == targetDetected[0]:
                        color = GREEN
                        break
                    else:
                        color = RED

                pygame.draw.circle(self.screen, color, (x_off + 88 + n * 20, y_off + 7 + m * 20), 5)
                n = n + 1
            m = m + 1

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
            #detected.reverse()

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

    def updateScreen(self):
        pygame.display.update()

    def getGUI_Info(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == KEYDOWN:
                pygame.quit()
                return False
        return True
