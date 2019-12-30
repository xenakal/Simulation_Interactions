import pygame
import math
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
    def __init__(self,screen,agent,target,x_off,y_off,x_max,y_max):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.agent_to_display = agent
        self.target_to_display = target

        self.x_offset = x_off
        self.y_offset = y_off
        self.x_max = x_max
        self.y_max = y_max

        self.scale_x = 0
        self.scale_y = 0

    def drawRoom(self, tab, color=0):

        self.scale_x = self.x_max/tab[2]
        self.scale_y = self.y_max/tab[3]

        pygame.draw.rect(self.screen, BLACK, (
            self.x_offset + tab[0] - 10, self.y_offset + tab[1] - 10, self.scale_x * tab[2] + 20,
            self.scale_y * tab[3] + 20))

        pygame.draw.rect(self.screen,WHITE , (
            self.x_offset + tab[0] - 6, self.y_offset + tab[1] - 6,self.scale_x * tab[2] + 12,
            self.scale_y * tab[3] + 12))

        pygame.draw.rect(self.screen, BLACK, (
        self.x_offset + tab[0], self.y_offset + tab[1], self.scale_x * tab[2],
        self.scale_y * tab[3]))


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
                self.screen.blit(label, (self.x_offset+int(target.xc * self.scale_x) + target.size / 2 + 5, self.y_offset+int(target.yc * self.scale_y) + target.size / 2 + 5))
                # render form
                pygame.draw.ellipse(self.screen, color, (
                self.x_offset + int(target.xc * self.scale_x) - self.scale_x * target.size,
                self.y_offset + int(target.yc * self.scale_y) - self.scale_y * target.size, self.scale_x * target.size * 2,
                self.scale_y * target.size * 2))

                if target.size >= 5:
                    pygame.draw.ellipse(self.screen, target.color, (self.x_offset + int(target.xc * self.scale_x)- self.scale_x * target.size/2,
                                                             self.y_offset + int(target.yc * self.scale_y) - self.scale_y * target.size/2,
                                                             self.scale_x * target.size,
                                                             self.scale_y * target.size))

    def drawTarget_all_postion(self,room):
        for target in room.targets:
            for id in self.target_to_display:
                if target.id == int(id):
                    for position in target.all_position:

                        pygame.draw.circle(self.screen, target.color, (self.x_offset+int(position[0]*self.scale_x), self.y_offset+int(position[1]*self.scale_y)), 1)


    def drawCam(self, myRoom, color=0, l=100):
        for agent in myRoom.agentCam:
            camera = agent.cam
            # render text
            label = self.font.render(str(camera.id), 10, CAMERA)
            self.screen.blit(label, (self.x_offset+int(camera.xc*self.scale_x) + 5,self.y_offset+int(camera.yc*self.scale_y) + 5))
            # render form
            pygame.draw.circle(self.screen, agent.color, (self.x_offset+int(camera.xc*self.scale_x),self.y_offset+int(camera.yc*self.scale_y)), 5)
            if camera.isActive == 1:
                pygame.draw.line(self.screen, WHITE, (self.x_offset+int(camera.xc*self.scale_x),self.y_offset+int(camera.yc*self.scale_y)),
                                 (self.x_offset+int(camera.xc*self.scale_x) + l * math.cos(camera.alpha),
                                  self.y_offset+int(camera.yc*self.scale_y) + l * math.sin(camera.alpha)), 2)
                pygame.draw.line(self.screen, CAMERA, (self.x_offset+int(camera.xc*self.scale_x),self.y_offset+int(camera.yc*self.scale_y)),
                                 (self.x_offset+int(camera.xc*self.scale_x)+ l * math.cos(camera.alpha - (camera.beta / 2)),
                                  self.y_offset+int(camera.yc*self.scale_y)+ l * math.sin(camera.alpha - (camera.beta / 2))), 2)
                pygame.draw.line(self.screen, CAMERA, (self.x_offset+int(camera.xc*self.scale_x),self.y_offset+int(camera.yc*self.scale_y)),
                                 (self.x_offset+int(camera.xc*self.scale_x) + l * math.cos(camera.alpha + (camera.beta / 2)),
                                  self.y_offset+int(camera.yc*self.scale_y) + l * math.sin(camera.alpha + (camera.beta / 2))), 2)