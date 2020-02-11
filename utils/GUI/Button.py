from utils.GUI.GUI import *
import pygame
from pygame.locals import *

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


class Button:
    def __init__(self, name, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.font = pygame.font.SysFont("monospace", 15)
        self.text = name

        self.color_released = WHITE
        self.color_pressed = YELLOW
        self.color_mouse_on = BLUE
        self.color_label = BLACK

        self.color = self.color_released  # actual color

        self.pressed = False

    def draw(self, window):
        pygame.draw.rect(window, self.color, Rect(self.x, self.y, self.w, self.h))

        label = self.font.render(self.text, 10, BLACK)
        window.blit(label, (self.x, self.y))

    def set_button(self, pressed):
        self.color = self.color_pressed if pressed else self.color_released
        self.pressed = pressed

    def is_mouse_on_button(self, pos_x, pos_y):
        """ Returns True if (pos_x, pos_y) is inside the button. """
        return (self.x < pos_x < self.x + self.w) and (self.y < pos_y < self.y + self.h)

    def check_click(self, window, pos_x, pos_y):
        """ Activates/deactivates the button and returns True if it's clicked. Returns False otherwise. """
        if self.is_mouse_on_button(pos_x, pos_y):
            self.set_button(not self.pressed)
            self.draw(window)
            return True
        return False


class ButtonList:
    def __init__(self, names, delta_x, delta_y, x, y, w, h):
        self.list = []

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.delta_x = delta_x
        self.delta_y = delta_y

        self.add_buttons(names)

    def draw(self, window):
        for button in self.list:
            button.draw(window)

    def add_buttons(self, names):
        for name in names:
            self.list.append(Button(name, self.x, self.y, self.w, self.h))
            self.x = self.x + self.delta_x + self.w
            self.y = self.y + self.delta_y + self.h

    def find_button(self, name):
        for button in self.list:
            if button.text == name:
                return button

    def find_button_state(self, name):
        for button in self.list:
            if button.text == name:
                return button.pressed

    def set_buttons_state(self, name, state):
        for button in self.list:
            if button.text == name:
                button.set_button(state)
