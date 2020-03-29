from my_utils.GUI.button import Button
from my_utils.GUI.button import ButtonList
from my_utils.GUI.GUI_simulation import GUI_room
from multi_agent.elements.camera import *
from multi_agent.elements.room import *
from my_utils.my_IO.IO_map import *
import pygame
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BACKGROUND = RED

class Button_name:
    "button title in the main menu"
    MAIN_OBJECT = "Object"
    MAIN_CAMERA = "Camera"
    MAIN_TRAJECTORY = "Trajectory"
    MAIN_CLEAN = "Clean"
    MAIN_LOAD = "Load map"
    MAIN_SAVE = "Save map"

    TRAJECTORY_SHOW = "Show Trajectory"
    TRAJECTORY_SAVE = "Save Trajectory"
    TRAJECTORY_ADD_POINT ="Add Point"
    TRAJECTORY_CLEAN = "Clean all"

    OBJECT_ADD = "Add"
    OBJECT_DEL = "Del"

class GUI_create_map:
    def __init__(self, screen,GUI_option,x_offset,y_offset,scale_x,scale_y):


        "Create a new room to load the data"
        self.new_room = Room()
        coord = self.new_room.coordinate_room

        "Windows to draw the GUI"
        self.screen = screen
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.scale_x = scale_x
        self.scale_y = scale_y

        "Other GUI"
        self.GUI_option = GUI_option
        self.GUI_room = GUI_room.GUI_room(self.screen, self.new_room.agentCams_list,
                                          self.new_room.information_simulation.Target_list, x_offset, y_offset, scale_x,
                                          scale_y)

        self.font = pygame.font.SysFont("monospace", 15)


        "Define every button name required"
        self.button_create_map_1_name = [Button_name.MAIN_OBJECT,Button_name.MAIN_CAMERA,Button_name.MAIN_TRAJECTORY,
                                         Button_name.MAIN_CLEAN, Button_name.MAIN_LOAD,Button_name.MAIN_SAVE]

        self.button_create_map_2_name = ["Unkown","Fix"]
        self.button_create_map_3_name = [Button_name.OBJECT_ADD,Button_name.OBJECT_DEL]

        self.button_target_scale_plus_moins_name = ["step +", "step -"]
        self.button_target_vx_plus_moins_name = ["vx +", "vx -"]
        self.button_target_vy_plus_moins_name = ["vy +", "vy -"]
        self.button_target_size_plus_moins_name = ["size +", "size -"]
        self.button_target_traj_plus_moins_name = ["traj +", "traj -"]

        self.button_camera_scale_plus_moins_name = ["step +", "step -"]
        self.button_camera_alpha_plus_moins_name = ["alpha +", "alpha -"]
        self.button_camera_beta_plus_moins_name = ["beta +", "beta -"]

        self.button_create_map_trajectoire_name = [Button_name.TRAJECTORY_SHOW,Button_name.TRAJECTORY_SAVE,Button_name.TRAJECTORY_ADD_POINT,
                                                   Button_name.TRAJECTORY_CLEAN]
        self.button_trajectoire_plus_moins_name = [" +", " -", "del"]


        "Define every button"
        self.button_create_map_trajectoire = ButtonList(self.button_create_map_trajectoire_name, -140, 10, 0, 125, 140, 20)
        self.button_create_map_trajectoire.find_button(Button_name.TRAJECTORY_ADD_POINT).set_button(True)
        self.button_trajectoire_plus_moins = ButtonList( self.button_trajectoire_plus_moins_name, 10, -20, 0, 280, 50,20)

        self.button_create_map_1 = ButtonList(self.button_create_map_1_name, 10, -20, 0,40, 100,20)
        self.button_create_map_2 = ButtonList(self.button_create_map_2_name, 10, -20, 0, 65, 100, 20)
        self.button_create_map_3 = ButtonList(self.button_create_map_3_name, 10, -20, 250, 65, 50, 20)
        self.button_create_map_4 = ButtonList(self.button_create_map_3_name, 10, -20, 0, 65, 50, 20)
        self.button_target_scale_plus_moins = ButtonList(self.button_target_scale_plus_moins_name, 10, -20, 0, 100, 60, 20)
        self.button_target_vx_plus_moins = ButtonList( self.button_target_vx_plus_moins_name, 10, -20, 0, 125, 60, 20)
        self.button_target_vy_plus_moins = ButtonList( self.button_target_vy_plus_moins_name, 10, -20, 0, 150, 60, 20)
        self.button_target_size_plus_moins = ButtonList(self.button_target_size_plus_moins_name, 10, -20,0, 175, 60, 20)
        self.button_target_traj_plus_moins = ButtonList(self.button_target_traj_plus_moins_name, 10, -20, 0, 200, 60,20)

        self.button_camera_scale_plus_moins = ButtonList(self.button_camera_scale_plus_moins_name, 10, -20, 0, 100, 60, 20)
        self.button_camera_alpha_plus_moins = ButtonList(self.button_camera_alpha_plus_moins_name, 10, -20, 0, 125, 60,20)
        self.button_camera_beta_plus_moins = ButtonList(self.button_camera_beta_plus_moins_name, 10, -20, 0, 150, 60, 20)

        self.button_create_map_2.find_button(self.button_create_map_2_name[0]).set_button(True)
        self.button_create_map_3.find_button(Button_name.OBJECT_ADD).set_button(True)
        self.button_create_map_4.find_button(Button_name.OBJECT_ADD).set_button(True)

        self.my_room_button = Button("room", coord[0] + self.x_offset-5, coord[1] + self.y_offset-5,
                                     coord[2]* self.scale_x+10,
                                     coord[3]* self.scale_y+10)

        self.button_round = Button("round", 10, 530, 100, 20)
        self.button_round.set_button(True)

        self.vx_default = 1
        self.vy_default = 1
        self.size_default = 0.3
        self.traj_default = 0
        self.target_scale = 0.05
        self.alpha_default = 0
        self.beta_default = 60
        self.camera_scale = 15

        self.create_trajectory = False
        self.trajectory_for_target = -1
        self.trajectory = []

    def run(self):
        self.GUI_room.drawRoom(self.new_room.coordinate_room)
        self.GUI_room.drawTarget(self.new_room.information_simulation.Target_list, self.new_room.coordinate_room)
        self.GUI_room.drawTarget(self.new_room.active_Target_list, self.new_room.coordinate_room)
        self.GUI_room.drawCam(self.new_room)
        self.display_create_map_button()

    def get_xy(self):
        (x, y, pressed, on) = self.GUI_option.check_button_get_pos(self.my_room_button)
        x_new = (x - self.x_offset) / self.scale_x
        y_new = (y - self.y_offset) / self.scale_y

        if self.button_round.pressed:
            x_new = int(x_new * 10) / 10
            y_new = int(y_new * 10) / 10

        if on:
            pygame.draw.circle(self.screen, [0, 0, 255], (x, y), 5)
            label = self.font.render("(%.02f,%.02f)" % (x_new, y_new), 10, WHITE)
            self.screen.blit(label, (x + 10, y + 10))
            self.screen.blit(label, (10, 550))

        return (x_new, y_new, pressed, on)

    def display_create_map_button(self):
        self.GUI_option.check_list(self.button_create_map_1.list)
        self.button_create_map_1.draw(self.screen)
        self.GUI_option.check_button(self.button_round)
        self.button_round.draw(self.screen)

        (x_new, y_new, pressed, on) = self.get_xy()

        if self.button_create_map_1.find_button_state(Button_name.MAIN_OBJECT):
            self.add_target_to_the_room(on,pressed,x_new,y_new)

        elif self.button_create_map_1.find_button_state(Button_name.MAIN_CAMERA):
            self.add_camera_to_the_room(on,pressed,x_new,y_new)

        elif self.button_create_map_1.find_button_state(Button_name.MAIN_TRAJECTORY):
           self.add_trajectories(x_new, y_new, pressed, on)

        elif self.button_create_map_1.find_button_state(Button_name.MAIN_CLEAN):
            self.new_room = Room()
            self.button_create_map_1.find_button(Button_name.MAIN_CLEAN).set_button(False)

        elif self.button_create_map_1.find_button_state(Button_name.MAIN_SAVE):
            save_room_to_txt("Created_map.txt",self.new_room)
            self.button_create_map_1.find_button(Button_name.MAIN_SAVE).set_button(False)

        elif self.button_create_map_1.find_button_state(Button_name.MAIN_LOAD):
            self.new_room = Room()
            load_room_from_txt("Created_map.txt",self.new_room)
            self.button_create_map_1.find_button(Button_name.MAIN_LOAD).set_button(False)


    def check_plus_or_minus_button(self,button,button_name_list,value_to_change,change,max = 1000,min = 0):
        if button.find_button_state(button_name_list[0]):
           button.find_button(button_name_list[0]).set_button(False)
           value_to_change = value_to_change+change

        elif button.find_button_state(button_name_list[1]):
            button.find_button(button_name_list[1]).set_button(False)
            value_to_change =value_to_change-change
            if value_to_change < min:
                value_to_change = min
            elif value_to_change > max:
                value_to_change = max

        return value_to_change


    def add_target_to_the_room(self,on,pressed,x_new,y_new):

        """Check if a button was clicked"""
        self.GUI_option.check_list(self.button_create_map_2.list)
        self.GUI_option.check_list(self.button_create_map_3.list)
        self.GUI_option.check_list(self.button_target_scale_plus_moins.list)
        self.GUI_option.check_list(self.button_target_vx_plus_moins.list)
        self.GUI_option.check_list(self.button_target_vy_plus_moins.list)
        self.GUI_option.check_list(self.button_target_size_plus_moins.list)


        """Draw button on the screen"""
        self.button_create_map_2.draw(self.screen)
        self.button_create_map_3.draw(self.screen)
        self.button_target_scale_plus_moins.draw(self.screen)
        self.button_target_vx_plus_moins.draw(self.screen)
        self.button_target_vy_plus_moins.draw(self.screen)
        self.button_target_size_plus_moins.draw(self.screen)

        """Check buttons"""
        self.target_scale = self.check_plus_or_minus_button(self.button_target_scale_plus_moins,self.button_target_scale_plus_moins_name,self.target_scale,0.02)

        self.vx_default=self.check_plus_or_minus_button(self.button_target_vx_plus_moins, self.button_target_vx_plus_moins_name,
                                    self.vx_default, 0.2)
        self.vy_default = self.check_plus_or_minus_button(self.button_target_vy_plus_moins, self.button_target_vy_plus_moins_name,
                                    self.vy_default, 0.2)
        self.size_default = self.check_plus_or_minus_button(self.button_target_size_plus_moins, self.button_target_size_plus_moins_name,
                                    self.size_default, self.target_scale)

        "draw values on the screen"
        label = self.font.render("%.02f"%self.target_scale, 10, WHITE)
        self.screen.blit(label, (135, 100))
        label = self.font.render("%.02f"%self.vx_default, 10, WHITE)
        self.screen.blit(label, (135, 125))
        label = self.font.render("%.02f"%self.vy_default, 10, WHITE)
        self.screen.blit(label, (135, 150))
        label = self.font.render("%.02f"%self.size_default, 10, WHITE)
        self.screen.blit(label, (135, 175))

        label = None
        if self.button_create_map_2.find_button_state(self.button_create_map_2_name[0]):
            label = TargetType.UNKNOWN
        elif self.button_create_map_2.find_button_state(self.button_create_map_2_name[1]):
            label = TargetType.SET_FIX

        "draw the target on the screen"

        if on and  self.button_create_map_3.find_button_state(Button_name.OBJECT_ADD):
            target = Target(-1, x_new, y_new, self.vx_default, self.vy_default,0,0, TargetMotion.LINEAR, (0, [(0, 0)]),
                            label, self.size_default, [0], [1000])
            self.GUI_room.draw_one_target(target, self.new_room.coordinate_room)

        "Add the target in the room"
        if pressed:
            if self.button_create_map_3.find_button_state(Button_name.OBJECT_ADD):
                self.new_room.add_create_Target(x_new, y_new, self.vx_default, self.vy_default,TargetMotion.LINEAR,
                                                self.trajectory, label, self.size_default, [0], [1000])

            elif self.button_create_map_3.find_button_state(Button_name.OBJECT_DEL):
                for target in self.new_room.information_simulation.Target_list:
                    if math.fabs(x_new - target.xc) < 0.2 and math.fabs(y_new - target.yc) < 0.2:
                        self.new_room.information_simulation.Target_list.remove(target)

    def add_camera_to_the_room(self,on,pressed,x_new,y_new):
        """Check if a button was clicked"""
        self.GUI_option.check_list(self.button_create_map_4.list)
        self.GUI_option.check_list(self.button_camera_scale_plus_moins.list)
        self.GUI_option.check_list(self.button_camera_alpha_plus_moins.list)
        self.GUI_option.check_list(self.button_camera_beta_plus_moins.list)

        """Draw button on the screen"""
        self.button_create_map_4.draw(self.screen)
        self.button_camera_scale_plus_moins.draw(self.screen)
        self.button_camera_alpha_plus_moins.draw(self.screen)
        self.button_camera_beta_plus_moins.draw(self.screen)

        """Check buttons"""
        self.camera_scale=self.check_plus_or_minus_button(self.button_camera_scale_plus_moins, self.button_camera_scale_plus_moins_name,
                                        self.camera_scale, 1)
        self.alpha_default=self.check_plus_or_minus_button(self.button_camera_alpha_plus_moins, self.button_camera_alpha_plus_moins_name,
                                        self.alpha_default, self.camera_scale,min = -180)
        self.beta_default = self.check_plus_or_minus_button(self.button_camera_beta_plus_moins, self.button_camera_beta_plus_moins_name,
                                        self.beta_default, self.camera_scale)
        "draw the values"
        label = self.font.render("%.0f"%self.camera_scale, 10, WHITE)
        self.screen.blit(label, (135, 100))
        label = self.font.render("%.0f"%self.alpha_default, 10, WHITE)
        self.screen.blit(label, (135, 125))
        label = self.font.render("%.0f"%self.beta_default, 10, WHITE)
        self.screen.blit(label, (135, 150))

        "draw the cam"
        if on and  self.button_create_map_4.find_button_state(Button_name.OBJECT_ADD):

            cam = Camera(self.new_room, 0, x_new, y_new, self.alpha_default, self.beta_default, 1)
            self.GUI_room.draw_one_Cam(cam)

        "add the cam to the room"
        if pressed:
            if self.button_create_map_4.find_button_state(Button_name.OBJECT_ADD):
                self.new_room.add_create_AgentCam(x_new, y_new, self.alpha_default, self.beta_default, 1)

            elif self.button_create_map_4.find_button_state(Button_name.OBJECT_DEL):
                for agent in self.new_room.agentCams_list:
                    if math.fabs(x_new - agent.camera.xc) < 0.2 and math.fabs(y_new - agent.camera.yc) < 0.2:
                        self.new_room.agentCams_list.remove(agent)

    def add_trajectories(self,x_new, y_new, pressed, on):

        self.GUI_option.check_list(self.button_create_map_trajectoire.list)
        self.button_create_map_trajectoire.draw(self.screen)

        self.GUI_room.drawTraj(self.trajectory)

        if self.create_trajectory == False:
            self.button_create_map_trajectoire.set_buttons_state(Button_name.TRAJECTORY_CLEAN, False)
            self.button_create_map_trajectoire.set_buttons_state(Button_name.TRAJECTORY_SAVE, False)
            for target in self.new_room.information_simulation.Target_list:
                if TargetType.UNKNOWN == target.type:
                    if math.fabs(x_new - target.xc) < 0.2 and math.fabs(y_new - target.yc) < 0.2:
                        if self.button_create_map_trajectoire.find_button_state(Button_name.TRAJECTORY_SHOW):
                            self.trajectory = target.trajectory_position
                            break

                        elif pressed:
                            self.button_create_map_trajectoire.set_buttons_state(Button_name.TRAJECTORY_ADD_POINT, True)
                            self.trajectory_for_target = target
                            self.create_trajectory = True
                            self.trajectory.append((target.xc,target.yc))
                            break
                    else:
                        self.trajectory = []

        else:
            x = self.trajectory_for_target.xc * self.scale_x + self.x_offset
            y = self.trajectory_for_target.yc * self.scale_y + self.y_offset
            pygame.draw.circle(self.screen, [0, 0, 255], (int(x),int(y)),10)
            if self.button_create_map_trajectoire.find_button_state(Button_name.TRAJECTORY_ADD_POINT):
                if pressed:
                    self.trajectory.append((x_new,y_new))
            elif self.button_create_map_trajectoire.find_button_state(Button_name.TRAJECTORY_CLEAN):
                self.button_create_map_trajectoire.set_buttons_state(Button_name.TRAJECTORY_CLEAN, False)
                self.trajectory = []
            elif self.button_create_map_trajectoire.find_button_state(Button_name.TRAJECTORY_SAVE):
                self.button_create_map_trajectoire.set_buttons_state(Button_name.TRAJECTORY_SAVE,False)
                self.create_trajectory = False
                self.trajectory_for_target.trajectory_position = self.trajectory
                self.trajectory = []








