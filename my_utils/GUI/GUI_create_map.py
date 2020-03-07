from multi_agent import room
from my_utils.GUI.button import Button
from my_utils.GUI.button import ButtonList
from my_utils.GUI.GUI_simulation import GUI_room
from my_utils.map import *
from elements.target import *
from elements.camera import *
import pygame
import re
import math
import numpy as np

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BACKGROUND = RED

class GUI_create_map:
    def __init__(self, screen,GUI_option,room_to_txt):

        self.screen = screen
        self.room_to_txt = room_to_txt
        self.GUI_option = GUI_option
        self.my_new_room = room.Room()
        coord = self.my_new_room.coord
        self.font = pygame.font.SysFont("monospace", 15)

        self.x_offset = 200
        self.y_offset = 100
        self.scale_x = 4 / 3
        self.scale_y = 4 / 3
        self.my_room_button = Button("room", coord[0] + self.x_offset, coord[1] + self.y_offset,
                                     coord[2] * self.scale_x,
                                     coord[3] * self.scale_y)

        self.GUI_room = GUI_room.GUI_room(self.screen, self.my_new_room.agentCams, self.my_new_room.targets, 200,
                                          100, 400, 400)

        self.button_create_map_1_name = ["Agent", "Camera","Trajectory","Clean","Save_map","Load_map"]
        self.button_create_map_2_name = ["Target", "Obstruction", "Fix"]
        self.button_target_scale_plus_moins_name = ["step +", "step -"]
        self.button_target_vx_plus_moins_name = ["vx +", "vx -"]
        self.button_target_vy_plus_moins_name = ["vy +", "vy -"]
        self.button_target_size_plus_moins_name = ["size +", "size -"]
        self.button_target_traj_plus_moins_name = ["traj +", "traj -"]

        self.button_camera_scale_plus_moins_name = ["step +", "step -"]
        self.button_camera_alpha_plus_moins_name = ["alpha +", "alpha -"]
        self.button_camera_beta_plus_moins_name = ["beta +", "beta -"]

        self.button_create_map_1 = ButtonList(self.button_create_map_1_name, 10, -20, 0,40, 100,20)
        self.button_create_map_2 = ButtonList(self.button_create_map_2_name, 10, -20, 0, 65, 100, 20)
        self.button_target_scale_plus_moins = ButtonList(self.button_target_scale_plus_moins_name, 10, -20, 0, 100, 60, 20)
        self.button_target_vx_plus_moins = ButtonList( self.button_target_vx_plus_moins_name, 10, -20, 0, 125, 60, 20)
        self.button_target_vy_plus_moins = ButtonList( self.button_target_vy_plus_moins_name, 10, -20, 0, 150, 60, 20)
        self.button_target_size_plus_moins = ButtonList(self.button_target_size_plus_moins_name, 10, -20,0, 175, 60, 20)
        self.button_target_traj_plus_moins = ButtonList(self.button_target_traj_plus_moins_name, 10, -20, 0, 200, 60,20)

        self.button_camera_scale_plus_moins = ButtonList(self.button_camera_scale_plus_moins_name, 10, -20, 0, 100, 60, 20)
        self.button_camera_alpha_plus_moins = ButtonList(self.button_camera_alpha_plus_moins_name, 10, -20, 0, 125, 60,20)
        self.button_camera_beta_plus_moins = ButtonList(self.button_camera_beta_plus_moins_name, 10, -20, 0, 150, 60, 20)

        self.button_create_map_2.find_button(self.button_create_map_2_name[0]).set_button(True)

        self.vx_default = 0
        self.vy_default = 0
        self.size_default = 5
        self.traj_default =0
        self.target_scale = 1

        self.alpha_default = 0
        self.beta_default = 60
        self.camera_scale = 10

    def run(self):
        self.GUI_room.drawRoom(self.my_new_room.coord)
        self.GUI_room.drawTarget(self.my_new_room.info_simu.targets_SIMU, self.my_new_room.coord)
        self.GUI_room.drawTarget(self.my_new_room.targets, self.my_new_room.coord)
        self.GUI_room.drawCam(self.my_new_room)
        self.display_create_map_button()

    def display_create_map_button(self):
        self.GUI_option.check_list(self.button_create_map_1.list)
        self.button_create_map_1.draw(self.screen)

        (x, y,pressed,on) = self.GUI_option.check_button_get_pos(self.my_room_button)
        x_new = (x-self.x_offset)/self.scale_x
        y_new = (y-self.y_offset)/self.scale_y

        x_new = math.ceil(x_new/10)*10
        y_new = math.ceil(y_new/10)*10

        if on:
            pygame.draw.circle(self.screen, [0, 0, 255], (x, y), 5)

        if self.button_create_map_1.find_button_state(self.button_create_map_1_name[0]):

            self.GUI_option.check_list(self.button_create_map_2.list)
            self.GUI_option.check_list(self.button_target_scale_plus_moins.list)
            self.GUI_option.check_list(self.button_target_vx_plus_moins.list)
            self.GUI_option.check_list(self.button_target_vy_plus_moins.list)
            self.GUI_option.check_list(self.button_target_size_plus_moins.list)
            self.GUI_option.check_list(self.button_target_traj_plus_moins.list)


            self.button_create_map_2.draw(self.screen)
            self.button_target_scale_plus_moins.draw(self.screen)
            self.button_target_vx_plus_moins.draw(self.screen)
            self.button_target_vy_plus_moins.draw(self.screen)
            self.button_target_size_plus_moins.draw(self.screen)
            self.button_target_traj_plus_moins.draw(self.screen)


            if self.button_target_scale_plus_moins.find_button_state(self.button_target_scale_plus_moins_name[0]):
                self.button_target_scale_plus_moins.find_button(self.button_target_scale_plus_moins_name[0]).set_button(False)
                self.target_scale = self.target_scale+1
            elif self.button_target_scale_plus_moins.find_button_state(self.button_target_scale_plus_moins_name[1]):
                self.target_scale = self.target_scale-1
                if self.target_scale < 0:
                    self.target_scale = 0
                self.button_target_scale_plus_moins.find_button(self.button_target_scale_plus_moins_name[1]).set_button(False)

            if self.button_target_vx_plus_moins.find_button_state(self.button_target_vx_plus_moins_name[0]):
                self.button_target_vx_plus_moins.find_button(self.button_target_vx_plus_moins_name[0]).set_button(False)
                self.vx_default = self.vx_default + self.target_scale
            elif self.button_target_vx_plus_moins.find_button_state(self.button_target_vx_plus_moins_name[1]):
                self.vx_default = self.vx_default - self.target_scale
                if self.vx_default < 0:
                    self.vx_default = 0
                self.button_target_vx_plus_moins.find_button(self.button_target_vx_plus_moins_name[1]).set_button(False)

            if self.button_target_vy_plus_moins.find_button_state(self.button_target_vy_plus_moins_name[0]):
                self.button_target_vy_plus_moins.find_button(self.button_target_vy_plus_moins_name[0]).set_button(False)
                self.vy_default = self.vy_default + self.target_scale
            elif self.button_target_vy_plus_moins.find_button_state(self.button_target_vy_plus_moins_name[1]):
                self.vy_default = self.vy_default - self.target_scale
                if self.vy_default < 0 :
                    self.vy_default = 0
                self.button_target_vy_plus_moins.find_button(self.button_target_vy_plus_moins_name[1]).set_button(False)

            if self.button_target_size_plus_moins.find_button_state(self.button_target_size_plus_moins_name[0]):
                self.size_default = self.size_default + self.target_scale
                self.button_target_size_plus_moins.find_button(self.button_target_size_plus_moins_name[0]).set_button(False)
            elif self.button_target_size_plus_moins.find_button_state(self.button_target_size_plus_moins_name[1]):
                self.size_default = self.size_default - self.target_scale
                if self.size_default < 1 :
                    self.size_default = 1
                self.button_target_size_plus_moins.find_button(self.button_target_size_plus_moins_name[1]).set_button(False)

            if self.button_target_traj_plus_moins.find_button_state(self.button_target_traj_plus_moins_name[0]):
                self.traj_default = self.traj_default + self.target_scale
                self.button_target_traj_plus_moins.find_button(self.button_target_traj_plus_moins_name[0]).set_button(False)
            elif self.button_target_traj_plus_moins.find_button_state(self.button_target_traj_plus_moins_name[1]):
                self.traj_default = self.traj_default - self.target_scale
                if self.traj_default < 1 :
                    self.traj_default = 1
                self.button_target_traj_plus_moins.find_button(self.button_target_traj_plus_moins_name[1]).set_button(False)

            label = self.font.render(str(self.target_scale), 10, WHITE)
            self.screen.blit(label, (140, 100))
            label = self.font.render(str(self.vx_default), 10, WHITE)
            self.screen.blit(label, (140, 125))
            label = self.font.render(str(self.vy_default), 10, WHITE)
            self.screen.blit(label, (140, 150))
            label = self.font.render(str(self.size_default), 10, WHITE)
            self.screen.blit(label, (140, 175))
            label = self.font.render(str(self.traj_default), 10, WHITE)
            self.screen.blit(label, (140, 200))

            label = None
            if self.button_create_map_2.find_button_state(self.button_create_map_2_name[0]):
                label = 'target'
            elif self.button_create_map_2.find_button_state(self.button_create_map_2_name[1]):
                label = 'obstruction'
            elif self.button_create_map_2.find_button_state(self.button_create_map_2_name[2]):
                label = 'fix'

            if on:
                target = Target(-1,x_new, y_new, self.vx_default, self.vy_default, 'linear', self.traj_default, label, self.size_default, [0], [1000])
                self.GUI_room.draw_one_target(target, self.my_new_room.coord)

            if pressed:
                self.my_new_room.addTargets(x_new, y_new, self.vx_default, self.vy_default, 'linear', self.traj_default, label, self.size_default, [0], [1000])
                self.room_to_txt.add_target(x_new, y_new, self.vx_default, self.vy_default, 'linear', self.traj_default, label, self.size_default, [0], [1000])

        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[1]):
            self.GUI_option.check_list(self.button_camera_scale_plus_moins.list)
            self.GUI_option.check_list(self.button_camera_alpha_plus_moins.list)
            self.GUI_option.check_list(self.button_camera_beta_plus_moins.list)

            self.button_camera_scale_plus_moins.draw(self.screen)
            self.button_camera_alpha_plus_moins.draw(self.screen)
            self.button_camera_beta_plus_moins.draw(self.screen)


            if self.button_camera_scale_plus_moins.find_button_state(self.button_camera_scale_plus_moins_name[0]):
                self.button_camera_scale_plus_moins.find_button(self.button_camera_scale_plus_moins_name[0]).set_button(False)
                self.camera_scale = self.camera_scale+1
            elif self.button_camera_scale_plus_moins.find_button_state(self.button_camera_scale_plus_moins_name[1]):
                self.camera_scale = self.camera_scale-1
                if self.camera_scale < 0:
                    self.camera_scale = 0
                self.button_camera_scale_plus_moins.find_button(self.button_camera_scale_plus_moins_name[1]).set_button(False)

            if self.button_camera_alpha_plus_moins.find_button_state(self.button_camera_alpha_plus_moins_name[0]):
                self.alpha_default = self.alpha_default + self.camera_scale
                self.button_camera_alpha_plus_moins.find_button(self.button_camera_alpha_plus_moins_name[0]).set_button(
                    False)
            elif self.button_camera_alpha_plus_moins.find_button_state(self.button_camera_alpha_plus_moins_name[1]):
                self.alpha_default = self.alpha_default - self.camera_scale
                self.button_camera_alpha_plus_moins.find_button(self.button_camera_alpha_plus_moins_name[1]).set_button(
                    False)

            if self.button_camera_beta_plus_moins.find_button_state(self.button_camera_beta_plus_moins_name[0]):
                self.button_camera_beta_plus_moins.find_button(self.button_camera_beta_plus_moins_name[0]).set_button(
                    False)
                self.beta_default = self.beta_default + self.camera_scale
            elif self.button_camera_beta_plus_moins.find_button_state(self.button_camera_beta_plus_moins_name[1]):
                self.beta_default = self.beta_default - self.camera_scale
                self.button_camera_beta_plus_moins.find_button(self.button_camera_beta_plus_moins_name[1]).set_button(
                    False)

            label = self.font.render(str(self.camera_scale), 10, WHITE)
            self.screen.blit(label, (140, 100))
            label = self.font.render(str(self. alpha_default), 10, WHITE)
            self.screen.blit(label, (140, 125))
            label = self.font.render(str(self.beta_default), 10, WHITE)
            self.screen.blit(label, (140, 150))


            if on:
                cam = Camera(0,x_new, y_new, self.alpha_default, self.beta_default, 1)
                self.GUI_room.draw_one_Cam(cam)

            if pressed:
                self.my_new_room.addAgentCam(x_new, y_new, self.alpha_default, self.beta_default, 0, self.my_new_room)
                self.room_to_txt.add_cam(x_new, y_new, self.alpha_default, self.beta_default, 0)


        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[2]):
            pass
        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[3]):
            self.room_to_txt.clean()
            self.my_new_room = self.room_to_txt.init_room()
            self.button_create_map_1.find_button("Clean").set_button(False)
        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[4]):
            self.room_to_txt.save_room_to_txt()
            self.button_create_map_1.find_button("Save_map").set_button(False)
        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[5]):
            self.room_to_txt.load_room_from_txt()
            self.my_new_room=self.room_to_txt.init_room()
            self.button_create_map_1.find_button("Load_map").set_button(False)

