from multi_agent import room
from my_utils.GUI.Button import Button
from my_utils.GUI.Button import ButtonList
from my_utils.GUI.GUI_simulation import GUI_room
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
    def __init__(self, screen, GUI_option):

        self.screen = screen
        self.GUI_option = GUI_option
        self.my_new_room = room.Room()
        coord = self.my_new_room.coord

        self.GUI_room = GUI_room.GUI_room(self.screen, self.my_new_room.agentCams, self.my_new_room.targets, 200,
                                          100, 400, 400)

        self.button_create_map_1_name = ["Agent", "Camera","Trajectory","Clean","Save_map","Load_map"]
        self.button_create_map_2_name = ["Target", "Obstruction", "Fix"]
        self.button_target_vx_plus_moins_name = ["vx +", "vx -"]
        self.button_target_vy_plus_moins_name = ["vy +", "vy -"]
        self.button_target_size_plus_moins_name = ["size +", "size -"]
        self.button_target_traj_plus_moins_name = ["traj +", "traj -"]

        self.button_camera_alpha_plus_moins_name = ["alpha +", "alpha -"]
        self.button_camera_beta_plus_moins_name = ["beta +", "beta -"]

        self.button_create_map_1 = ButtonList(self.button_create_map_1_name, 10, -20, 0,40, 100,20)
        self.button_create_map_2 = ButtonList(self.button_create_map_2_name, 10, -20, 0, 65, 100, 20)
        self.button_target_vx_plus_moins = ButtonList( self.button_target_vx_plus_moins_name, 10, -20, 0, 100, 60, 20)
        self.button_target_vy_plus_moins = ButtonList( self.button_target_vy_plus_moins_name, 10, -20, 0, 125, 60, 20)
        self.button_target_size_plus_moins = ButtonList(self.button_target_size_plus_moins_name, 10, -20,0, 150, 60, 20)
        self.button_target_traj_plus_moins = ButtonList(self.button_target_traj_plus_moins_name, 10, -20, 0, 175, 60,20)
        self.button_camera_alpha_plus_moins = ButtonList(self.button_camera_alpha_plus_moins_name, 10, -20, 0, 100, 60,20)
        self.button_camera_beta_plus_moins = ButtonList(self.button_camera_beta_plus_moins_name, 10, -20, 0, 125, 60, 20)

        self.button_create_map_2.find_button(self.button_create_map_2_name[0]).set_button(True)

        self.vx_default = 0
        self.vy_default = 0
        self.size_default = 5
        self.traj_default =0

        self.alpha_default = 0
        self.beta_default = 60

        self.x_offset = 200
        self.y_offset = 100
        self.scale_x = 4/3
        self.scale_y = 4/3
        self.my_room_button = Button("room", coord[0] + self.x_offset, coord[1] + self.y_offset, coord[2] * self.scale_x,
                                     coord[3] * self.scale_y)


        self.x_target = []
        self.y_target = []
        self.vx_target = []
        self.vy_target = []
        self.trajectoire_target = []
        self.trajectoire_choice = []
        self.label_target = []
        self.size_target = []
        self.t_add = []
        self.t_del = []

        self.x_cam = []
        self.y_cam = []
        self.alpha_cam = []
        self.beta_cam =  []
        self.fix = []

        self.data_to_save = [self.x_target,self.y_target,self.vx_target,self.vy_target,self.trajectoire_target,self.trajectoire_choice,self.label_target,
                             self.size_target,self.t_add,self.t_del,self.x_cam,self.y_cam,self.alpha_cam,self.beta_cam,self.fix]

    def run(self):
        self.GUI_room.drawRoom(self.my_new_room.coord)
        self.GUI_room.drawTarget(self.my_new_room.targets, self.my_new_room.coord)
        self.GUI_room.drawCam(self.my_new_room)
        self.display_create_map_button()



    def display_create_map_button(self):
        self.GUI_option.check_list(self.button_create_map_1.list)
        self.button_create_map_1.draw(self.screen)

        (x, y) = self.GUI_option.check_button_get_pos(self.my_room_button)
        x_new = (x-self.x_offset)/self.scale_x
        y_new = (y-self.y_offset)/self.scale_y
        pygame.draw.circle(self.screen, [0, 0, 255], (x, y), 5)

        if self.button_create_map_1.find_button_state(self.button_create_map_1_name[0]):
            self.GUI_option.check_list(self.button_create_map_2.list)
            self.GUI_option.check_list(self.button_target_vx_plus_moins.list)
            self.GUI_option.check_list(self.button_target_vy_plus_moins.list)
            self.GUI_option.check_list(self.button_target_size_plus_moins.list)
            self.GUI_option.check_list(self.button_target_size_plus_moins.list)
            self.GUI_option.check_list(self.button_target_traj_plus_moins.list)


            self.button_create_map_2.draw(self.screen)
            self.button_target_vx_plus_moins.draw(self.screen)
            self.button_target_vy_plus_moins.draw(self.screen)
            self.button_target_size_plus_moins.draw(self.screen)
            self.button_target_traj_plus_moins.draw(self.screen)



            if self.button_target_vx_plus_moins.find_button_state(self.button_target_vx_plus_moins_name[0]):
                self.button_target_vx_plus_moins.find_button(self.button_target_vx_plus_moins_name[0]).set_button(False)
                self.vx_default = self.vx_default+1
            elif self.button_target_vx_plus_moins.find_button_state(self.button_target_vx_plus_moins_name[1]):
                self.vx_default = self.vx_default - 1
                if self.vx_default < 0:
                    self.vx_default = 0
                self.button_target_vx_plus_moins.find_button(self.button_target_vx_plus_moins_name[1]).set_button(False)


            if self.button_target_vy_plus_moins.find_button_state(self.button_target_vy_plus_moins_name[0]):
                self.button_target_vy_plus_moins.find_button(self.button_target_vy_plus_moins_name[0]).set_button(False)
                self.vy_default = self.vy_default + 1
            elif self.button_target_vy_plus_moins.find_button_state(self.button_target_vy_plus_moins_name[1]):
                self.vy_default = self.vy_default - 1
                if self.vy_default < 0 :
                    self.vy_default = 0
                self.button_target_vy_plus_moins.find_button(self.button_target_vy_plus_moins_name[1]).set_button(False)

            if self.button_target_size_plus_moins.find_button_state(self.button_target_size_plus_moins_name[0]):
                self.size_default = self.size_default + 1
                self.button_target_size_plus_moins.find_button(self.button_target_size_plus_moins_name[0]).set_button(False)
            elif self.button_target_size_plus_moins.find_button_state(self.button_target_size_plus_moins_name[1]):
                self.size_default = self.size_default - 1
                if self.size_default < 1 :
                    self.size_default = 1
                self.button_target_size_plus_moins.find_button(self.button_target_size_plus_moins_name[1]).set_button(False)

            if self.button_target_traj_plus_moins.find_button_state(self.button_target_traj_plus_moins_name[0]):
                self.traj_default = self.traj_default + 1
                self.button_target_traj_plus_moins.find_button(self.button_target_traj_plus_moins_name[0]).set_button(False)
            elif self.button_target_traj_plus_moins.find_button_state(self.button_target_traj_plus_moins_name[1]):
                self.traj_default = self.traj_default - 1
                if self.traj_default < 1 :
                    self.traj_default = 1
                self.button_target_traj_plus_moins.find_button(self.button_target_traj_plus_moins_name[1]).set_button(False)


            if self.checkk_add_in_the_room(x,y):
                label = None
                if self.button_create_map_2.find_button_state(self.button_create_map_2_name[0]):
                    label = 'target'
                elif self.button_create_map_2.find_button_state(self.button_create_map_2_name[1]):
                    label = 'obstruction'
                elif self.button_create_map_2.find_button_state(self.button_create_map_2_name[2]):
                    label = 'fix'

                self.my_new_room.addTargets(x_new, y_new, self.vx_default, self.vy_default, 'linear', self.traj_default, label, self.size_default, [0], [1000])

                self.x_target.append(x_new)
                self.y_target.append(y_new)
                self.vx_target.append(self.vx_default)
                self.vy_target.append(self.vy_default)
                self.trajectoire_target.append('linear')
                self.trajectoire_choice.append(self.traj_default)
                self.label_target.append(label)
                self.size_target.append(self.size_default)
                self.t_add.append([0])
                self.t_del.append([1000])

        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[1]):
            self.GUI_option.check_list(self.button_camera_alpha_plus_moins.list)
            self.GUI_option.check_list(self.button_camera_beta_plus_moins.list)

            self.button_camera_alpha_plus_moins.draw(self.screen)
            self.button_camera_beta_plus_moins.draw(self.screen)

            if self.button_camera_alpha_plus_moins.find_button_state(self.button_camera_alpha_plus_moins_name[0]):
                self.alpha_default = self.alpha_default + 5
                self.button_camera_alpha_plus_moins.find_button(self.button_camera_alpha_plus_moins_name[0]).set_button(
                    False)

            elif self.button_camera_alpha_plus_moins.find_button_state(self.button_camera_alpha_plus_moins_name[1]):
                self.alpha_default = self.alpha_default - 5
                self.button_camera_alpha_plus_moins.find_button(self.button_camera_alpha_plus_moins_name[1]).set_button(
                    False)

            if self.button_camera_beta_plus_moins.find_button_state(self.button_camera_beta_plus_moins_name[0]):
                self.button_camera_beta_plus_moins.find_button(self.button_camera_beta_plus_moins_name[0]).set_button(
                    False)
                self.beta_default = self.beta_default + 5
            elif self.button_camera_beta_plus_moins.find_button_state(self.button_camera_beta_plus_moins_name[1]):
                self.beta_default = self.beta_default - 5
                self.button_camera_beta_plus_moins.find_button(self.button_camera_beta_plus_moins_name[1]).set_button(
                    False)


            if self.checkk_add_in_the_room(x,y):
                self.my_new_room.addAgentCam(x_new, y_new, self.alpha_default, self.beta_default, 0, self.my_new_room)

                self.x_cam.append(x_new)
                self.y_cam.append(y_new)
                self.alpha_cam.append(self.alpha_default)
                self.beta_cam.append(self.beta_default)
                self.fix.append(0)

        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[2]):
            pass
        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[3]):
            self.clean()
            self.button_create_map_1.find_button("Clean").set_button(False)
        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[4]):
            self.save_map()
            self.button_create_map_1.find_button("Save_map").set_button(False)
        elif self.button_create_map_1.find_button_state(self.button_create_map_1_name[5]):
            self.load_map()
            self.button_create_map_1.find_button("Load_map").set_button(False)

    def checkk_add_in_the_room(self,x,y):
        if x == -1 and y == -1:
            return False
        else:
            return True

    def clean(self):
        self.my_new_room = room.Room()

        self.x_target = []
        self.y_target = []
        self.vx_target = []
        self.vy_target = []
        self.trajectoire_target = []
        self.trajectoire_choice = []
        self.label_target = []
        self.size_target = []
        self.t_add = []
        self.t_del = []

        self.x_cam = []
        self.y_cam = []
        self.alpha_cam = []
        self.beta_cam = []
        self.fix = []

        self.data_to_save = [self.x_target, self.y_target, self.vx_target, self.vy_target, self.trajectoire_target,
                             self.trajectoire_choice, self.label_target,
                             self.size_target, self.t_add, self.t_del, self.x_cam, self.y_cam, self.alpha_cam,
                             self.beta_cam, self.fix]

    def save_map(self):
        fichier = open("map.txt", "w")
        fichier.write("#New MAP \n")
        for element in self.data_to_save:
            for each in element:
                fichier.write(str(each) + str(","))

            fichier.write("\n")
        fichier.close()

    def load_map(self):
        fichier = open("map.txt","r")
        lines = fichier.readlines()
        fichier.close()

        self.clean()
        count = 0
        for line in lines:
            if not (line[0] == "#"):
                linesplit = re.split(",",line)
                for  elem in linesplit:
                    if not(elem == "\n"):
                        try:
                            self.data_to_save[count].append(math.ceil(float(elem)))
                        except ValueError:
                            self.data_to_save[count].append(elem)
                count = count + 1


        self.from_all_data_to_separate()
        self.my_new_room.init(self.x_target,self.y_target,self.vx_target,self.vy_target,self.trajectoire_target,self.trajectoire_choice,self.label_target,self.size_target,self.t_add,self.t_del)
        self.my_new_room.init_agentCam(self.x_cam,self.y_cam,self.alpha_cam,self.beta_cam,self.fix,self.my_new_room)
        self.my_new_room.targets = self.my_new_room.info_simu.targets_SIMU

    def from_all_data_to_separate(self):
        self.x_target = self.data_to_save[0]
        self.y_target = self.data_to_save[1]
        self.vx_target = self.data_to_save[2]
        self.vy_target = self.data_to_save[3]
        self.trajectoire_target = self.data_to_save[4]
        self.trajectoire_choice = self.data_to_save[5]
        self.label_target = self.data_to_save[6]
        self.size_target = self.data_to_save[7]
        self.t_add = self.data_to_save[8]
        self.t_del = self.data_to_save[9]

        self.x_cam = self.data_to_save[10]
        self.y_cam = self.data_to_save[11]
        self.alpha_cam = self.data_to_save[12]
        self.beta_cam = self.data_to_save[13]
        self.fix = self.data_to_save[14]



