import pygame
from my_utils.GUI.GUI import *

class GUI_Region:

    def __init__(self, screen, x_off, y_off, scaleX, scaleY):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.x_offset = x_off
        self.y_offset = y_off
        self.scale_x = scaleX
        self.scale_y = scaleY

    def draw_cam_region(self,room,region):
        x = region.xv
        y = region.yv
        (i_tot, j_tot) = region.minimum_id_in_view.shape
        for i in range(i_tot):
            for j in range(j_tot):
                for agent in room.active_AgentCams_list:
                    if agent.cam.id == region.minimum_id_in_view[i,j]:
                        pygame.draw.circle(self.screen,agent.cam.color,
                                       (self.x_offset + int(x[i,j]*self.scale_x),
                                        self.y_offset + int(y[i,j]*self.scale_y)), 1)
                        break

    def draw_cam_coverage(self,region):
        x = region.xv
        y = region.yv

        (i_tot, j_tot) = region.coverage.shape
        for i in range(i_tot):
            for j in range(j_tot):
                # il faut faire -1
                if region.coverage[i,j] == 1 :
                    pygame.draw.circle(self.screen,[150,0,0],
                                       (self.x_offset + int(x[i,j]*self.scale_x),
                                        self.y_offset + int(y[i,j]*self.scale_y)), 1)
                if region.coverage[i, j] == 2:
                    pygame.draw.circle(self.screen, [200, 75, 0],
                                       (self.x_offset + int(x[i, j] * self.scale_x),
                                        self.y_offset + int(y[i, j] * self.scale_y)), 1)
                if region.coverage[i, j] == 3:
                    pygame.draw.circle(self.screen, [200, 150, 0],
                                           (self.x_offset + int(x[i, j] * self.scale_x),
                                            self.y_offset + int(y[i, j] * self.scale_y)), 1)
                if region.coverage[i, j] == 4:
                    pygame.draw.circle(self.screen, [250, 200, 0],
                                       (self.x_offset + int(x[i, j] * self.scale_x),
                                        self.y_offset + int(y[i, j] * self.scale_y)), 1)
                if region.coverage[i, j] >= 5:
                    pygame.draw.circle(self.screen, [250, 250, 250],
                                       (self.x_offset + int(x[i, j] * self.scale_x),
                                        self.y_offset + int(y[i, j] * self.scale_y)), 1)
