from my_utils.GUI.button import *
##from my_utils.GUI.Button import ButtonList
from my_utils.GUI.GUI_option import *
from my_utils.GUI.GUI_simulation.GUI_simulation import *
from my_utils.GUI.GUI_projection import *
from my_utils.GUI.GUI_stat import *
from my_utils.GUI.GUI_create_map import *
from my_utils.GUI.GUI_simulation.GUI_room import *
from my_utils.GUI.Gui_output_user import *
from my_utils.GUI.button import ButtonList
import main

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BACKGROUND = RED

class GUI:
    def __init__(self,room_to_txt):
        pygame.init()

        # define the windows
        self.w = 800
        self.h = 600

        x_offset = main.X_OFFSET
        y_offset = main.Y_OFFSET
        scale_x = main.X_SCALE
        scale_y = main.Y_SCALE

        self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)

        self.button_menu = ButtonList(["Simulation","User's output","Create Map", "Camera", "Stat",], 10, -30, 0, 0, 100, 30)
        self.button_menu.set_buttons_state("Simulation", True)

        self.GUI_option = GUI_option(self.screen)
        self.GUI_projection = GUI_projection(self.screen)
        self.GUI_stat = GUI_stat(self.screen, 0, 50)
        self.GUI_create_map = GUI_create_map(self.screen,self.GUI_option,room_to_txt,x_offset,y_offset,scale_x,scale_y)
        self.GUI_simu = GUI_simulation(self.screen, self.GUI_option,room_to_txt,x_offset,y_offset,scale_x,scale_y)
        self.GUI_output = GUI_user_output(self.screen, self.GUI_option,x_offset,y_offset,scale_x,scale_y)

        pygame.display.set_caption("Camera simulation")
        self.font = pygame.font.SysFont("monospace", 15)

    def refresh(self):
        pygame.draw.rect(self.screen, BLACK, (0, 0, self.w, self.h))

    def display_menu(self):
        self.GUI_option.check_list(self.button_menu.list)
        self.button_menu.draw(self.screen)

    def updateGUI(self, myRoom,region,link_camera_target):
        self.refresh()
        self.display_menu()

        if self.button_menu.find_button_state("Simulation"):
            self.GUI_simu.run(myRoom,region,link_camera_target)

        elif self.button_menu.find_button_state("Camera"):
            self.GUI_projection.drawProjection(myRoom)
            self.GUI_simu.GUI_ATD.screenDetectedTarget(myRoom)

        elif self.button_menu.find_button_state("Stat"):
            self.GUI_stat.draw_stat_message(myRoom)

        elif self.button_menu.find_button_state("Create Map"):
            self.GUI_create_map.run()

        elif self.button_menu.find_button_state("User's output"):
            self.GUI_output.run(myRoom,link_camera_target)

        self.GUI_option.reset_mouse_list()
        pygame.display.update()
