import pygame
from pygame.locals import *
from src import constants

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


class GUI_option:
    """
    Class used to keep track of the different options the user can choose from.

    :param
        agent_to_display  -- list of agent IDs that are to be displayed in the GUI
        target_to_display -- list of target IDs that are to be displayed in the GUI
    """

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.position_mouse_all = []
        self.position_mouse_pressed = []

        self.agent_to_display = []
        self.target_to_display = []


    def reset_mouse_list(self):
        self.position_mouse_all = []
        self.position_mouse_pressed = []

    def check_button(self, button):
        """ Returns True if the button is pressed"""
        for position in self.position_mouse_pressed:
            (pos_x, pos_y) = position[0]
            if button.check_click(self.screen, pos_x, pos_y):
                self.position_mouse_pressed.remove(position)
                return True
        return False

    def check_button_get_pos(self, button):
        on = False
        pressed = False
        (pos_x, pos_y) = (-1,-1)

        for position in self.position_mouse_pressed:
            (pos_x, pos_y) = position[0]
            if button.check_click(self.screen,pos_x, pos_y):
                pressed = True
                self.position_mouse_pressed.remove(position)

        for position in self.position_mouse_all:
            (pos_x, pos_y) = position[0]
            if button.is_mouse_on_button(pos_x,pos_y):
                on = True
                self.position_mouse_all.remove(position)
        return (pos_x,pos_y,pressed,on)

    def check_list(self, buttons):
        for button in buttons:
            if self.check_button(button):
                for button_to_turn_off in buttons:
                    button_to_turn_off.set_button(False)
                button.set_button(True)

    def option_add_agent(self, agentID):
        try:
            self.agent_to_display.index(agentID)
        except ValueError:
            self.agent_to_display.append(agentID)

    def option_remove_agent(self, agentID):
        try:
            self.agent_to_display.index(agentID)
            self.agent_to_display.remove(agentID)
        except ValueError:
            pass

    def option_add_target(self, targetID):
        try:
            self.target_to_display.index(targetID)
        except ValueError:
            self.target_to_display.append(targetID)

    def option_remove_target(self, targetID):
        try:
            self.target_to_display.index(targetID)
            self.target_to_display.remove(targetID)
        except ValueError:
            pass

    def getGUI_Info(self):
        self.position_mouse_all.append([pygame.mouse.get_pos()])

        for event in pygame.event.get():
            type_event = event.type
            if type_event == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    return False, False
                if event.key == K_r:
                    return True, True
                if event.key == K_s:
                    print("screenshot")
                    pygame.image.save(self.screen, constants.ResultsPath.DATA_SCREENSHOT + "/screenshot_at_%.02fs.png" % constants.get_time())

            elif type_event == MOUSEMOTION and event.buttons[0] == 1:  # déplacement + boutton enfoncer
                pass
                # print("Déplacement") #pour utiliser des boutton

            elif type_event == MOUSEMOTION:
               pass
               #self.update_mouse_position()

            elif type_event == MOUSEBUTTONUP:
                self.position_mouse_pressed.append([pygame.mouse.get_pos()])

        return True, False
