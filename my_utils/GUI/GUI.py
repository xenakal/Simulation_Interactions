from my_utils.GUI.Button import *
##from my_utils.GUI.Button import ButtonList
from my_utils.GUI.GUI_option import *
from my_utils.GUI.GUI_simulation.GUI_simulation import *
from my_utils.GUI.Gui_projection import *
from my_utils.GUI.GUI_stat import *
from my_utils.GUI.GUI_draw_map import *
from my_utils.GUI.GUI_simulation.GUI_room import *



WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

BACKGROUND = RED

class GUI:
    def __init__(self):
        pygame.init()

        # define the windows
        self.w = 800
        self.h = 600
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.RESIZABLE)

        self.button_menu = ButtonList(["Simulation", "Camera", "Stat","Create Map","Option"], 10, -30, 0, 0, 100, 30)
        self.button_menu.set_buttons_state("Simulation", True)

        self.GUI_option = GUI_option(self.screen)
        self.GUI_projection = GUI_projection(self.screen)
        self.GUI_stat = GUI_stat(self.screen, 0, 50)
        self.GUI_create_map = GUI_create_map(self.screen,self.GUI_option)
        self.GUI_simu = GUI_simulation(self.screen, self.GUI_option)

        pygame.display.set_caption("Camera simulation")
        self.font = pygame.font.SysFont("monospace", 15)

    def refresh(self):
        pygame.draw.rect(self.screen, BLACK, (0, 0, self.w, self.h))

    def display_menu(self):
        self.GUI_option.check_list(self.button_menu.list)
        self.button_menu.draw(self.screen)

    def updateGUI(self, myRoom):
        self.refresh()
        self.display_menu()

        if self.button_menu.find_button_state("Simulation"):
            self.GUI_simu.run(myRoom)

        elif self.button_menu.find_button_state("Camera"):
            self.GUI_projection.drawProjection(myRoom)
            self.GUI_simu.GUI_ATD.screenDetectedTarget(myRoom)

        elif self.button_menu.find_button_state("Stat"):
            self.GUI_stat.draw_stat_message(myRoom)

        elif self.button_menu.find_button_state("Create Map"):
            self.GUI_create_map.run()

        elif self.button_menu.find_button_state("Option"):
            pass

        self.GUI_option.reset_mouse_list()
        pygame.display.update()