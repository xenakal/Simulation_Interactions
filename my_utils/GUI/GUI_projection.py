from my_utils.GUI.GUI import*
from my_utils.my_math.line import *
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

class GUI_projection:
    def __init__(self,screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)


    def draw_projection(self,room):
        x_off = 20
        y_off = 40

        pygame.draw.rect(self.screen, BLACK, (x_off, y_off, 500, 200))

        n = 0
        for agent in room.active_AgentCams_list:
            camera = agent.camera
            if camera.isActive:
                label = self.font.render("camera " + str(camera.id), 10, WHITE)
                self.screen.blit(label, (x_off, y_off + n * 30))
                pygame.draw.circle(self.screen, CAMERA, (x_off + 85, y_off + 8 + n * 30), 5)

                m = 0
                detected = camera.targetCameraDistance_list.copy()
                (limit_donw,limit_up) = camera.target_projection[len(camera.target_projection)-1]


                try:
                    detected.reverse()
                except AttributeError:
                    print("Unable to resverse, cam : " + str(camera.id))

                for element in detected:
                    target = element.target
                    (d0,d1) = element.projection
                    pygame.draw.circle(self.screen, target.color, (x_off + 85 + int(limit_up) + int(d0), y_off + 8 + n * 30), 1)
                    pygame.draw.circle(self.screen, target.color, (x_off + 85 + int(limit_up) + int(d1), y_off + 8 + n * 30), 1)

                    pygame.draw.line(self.screen, target.color, (x_off + 85 + int(limit_up)+ int(d0), y_off + 9 + n * 30),
                                     (x_off + 85 + int(limit_up)+ int(d1), y_off + 9 + n * 30), 1)
                    label = self.font.render(str(math.floor(target.id)), 10, target.color)
                    self.screen.blit(label, (x_off + 85 + int(limit_up) +math.ceil((d0 + d1) / 2), y_off + 10 + n * 30))



                pygame.draw.circle(self.screen, WHITE, (x_off + 85 , y_off + 8 + n * 30), 5)
                pygame.draw.circle(self.screen, WHITE, (x_off + 85 +2*int(limit_up), y_off + 8 + n * 30), 5)
                n = n + 1

   