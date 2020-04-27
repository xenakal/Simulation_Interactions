import pygame
from src import  constants

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
                    if agent.camera.id == region.minimum_id_in_view[i,j]:
                        pygame.draw.circle(self.screen,agent.camera.color,
                                       (self.x_offset + int(x[i,j]*self.scale_x),
                                        self.y_offset + int((constants.ROOM_DIMENSION_Y-y[i, j])*self.scale_y)), 1)
                        break

    def draw_cam_coverage(self,region):
        x = region.xv
        y = region.yv

        (i_tot, j_tot) = region.coverage.shape
        for i in range(i_tot):
            for j in range(j_tot):
                # il faut faire -1
                color = None
                if region.coverage[i, j] == 1:
                    color = (150, 0, 0)
                elif region.coverage[i, j] == 2:
                    color = (200, 75, 0)
                elif region.coverage[i, j] == 3:
                    color = (200, 150, 0)
                elif region.coverage[i, j] == 4:
                    color = (250, 200, 0)
                elif region.coverage[i, j] >= 5:
                    color = (250, 250, 250)

                if color is not None:
                    pygame.draw.circle(self.screen, color,
                                   (self.x_offset + int(x[i, j] * self.scale_x),
                                    self.y_offset + int((constants.ROOM_DIMENSION_Y-y[i, j]) * self.scale_y)), 1)
