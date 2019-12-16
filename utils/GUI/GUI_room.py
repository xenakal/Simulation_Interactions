import pygame
from utils.GUI.GUI import*

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

class GUI_room:
    def __init__(self,screen):
        self.screen = screen
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

            # so that it is only target.yc drawn in the square
            if (tab[0] <= target.xc + target.size <= tab[0] + tab[
                2] and tab[1] <= target.yc + target.size <= tab[1] + tab[3]):  # target inside room
                # render the target.xct
                label = self.font.render(str(target.id), 10, color)
                self.screen.blit(label, (target.xc + target.size / 2 + 5, target.yc + target.size / 2 + 5))
                # render form
                pygame.draw.circle(self.screen, color, (target.xc, target.yc), target.size)
                if target.size >= 5:
                    pygame.draw.circle(self.screen, target.color, (target.xc, target.yc),
                                       math.floor(target.size - 0.5 * target.size))

    def drawCam(self, myRoom, color=0, l=100):
        for agent in myRoom.agentCam:
            camera = agent.cam
            # render text
            label = self.font.render(str(camera.id), 10, CAMERA)
            self.screen.blit(label, (camera.xc + 5, camera.yc + 5))
            # render form
            pygame.draw.circle(self.screen, agent.color, (camera.xc, camera.yc), 5)
            if camera.isActive == 1:
                pygame.draw.line(self.screen, BLACK, (camera.xc, camera.yc),
                                 (camera.xc + l * math.cos(camera.alpha),
                                  camera.yc + l * math.sin(camera.alpha)), 2)
                pygame.draw.line(self.screen, CAMERA, (camera.xc, camera.yc),
                                 (camera.xc + l * math.cos(camera.alpha - (camera.beta / 2)),
                                  camera.yc + l * math.sin(camera.alpha - (camera.beta / 2))), 2)
                pygame.draw.line(self.screen, CAMERA, (camera.xc, camera.yc),
                                 (camera.xc + l * math.cos(camera.alpha + (camera.beta / 2)),
                                  camera.yc + l * math.sin(camera.alpha + (camera.beta / 2))), 2)