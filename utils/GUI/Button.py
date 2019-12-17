from utils.GUI.GUI import*
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
    def __init__(self,name,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.font = pygame.font.SysFont("monospace", 15)
        self.texte = name

        self.color_released = WHITE
        self.color_pressed = YELLOW
        self.color_mouse_on = BLUE
        self.color_label = BLACK

        self.pressed = False

    def draw(self,window):
            if self.pressed:
                pygame.draw.rect(window,self.color_pressed,Rect(self.x,self.y,self.w,self.h))
            else:
                pygame.draw.rect(window, self.color_released, Rect(self.x, self.y, self.w, self.h))

            label = self.font.render(self.texte, 10, BLACK)
            window.blit(label, (self.x -5+ self.h/2, self.y -5+ self.w/2))

    def check_mouse_pos(self,window,pos_x,pos_y):
        if (pos_x > self.x and pos_x < self.x+self.w) and (pos_y > self.y and pos_y < self.y+self.h):
            #pygame.draw.rect(window, self.color_mouse_on, Rect(self.x, self.y, self.w, self.h))
            return True
        return  False

    def check_click(self,window,pos_x,pos_y):
        if self.check_mouse_pos(window, pos_x, pos_y):
            self.pressed = not self.pressed
            self.draw(window)
            return True
        return False


class ButtonList():
    def __init__(self, names, delta_x, delta_y,x,y,w,h):
        self.list = []

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.delta_x = delta_x
        self.delta_y = delta_y


        self.add_button(names)

    def add_button(self, names):
        for name in names:
            self.list.append(Button(name,self.x,self.y,self.w,self.h))
            self.x = self.x + self.delta_x+self.w
            self.y = self.y + self.delta_y+self.h