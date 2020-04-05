from src.my_utils.GUI.button import ButtonList
from src.my_utils.GUI.GUI_simulation.GUI_predictions import *
from src.my_utils.GUI.GUI_simulation.GUI_room_representation import GUI_room_representation
from src.my_utils.GUI.GUI_simulation.GUI_agent_region import *
from src.multi_agent.agent.agent import AgentType


class GUI_user_output:
    def __init__(self, screen, GUI_option,x_offset,y_offset,scale_x,scale_y):
        pygame.init()
        self.screen = screen
        self.GUI_option = GUI_option


        self.button_simulation_1 = ButtonList(["prediction"], 10, -20, 0, 40, 100,20)
        self.button_simulation_2 = ButtonList(["0", "1", "2", "3", "4", "5", "6","7","8","9","10","11","12"], -35, 10, 700, 40, 35, 15)
        self.button_simulation_3 = ButtonList(["0", "1", "2", "3", "4", "5", "6","7","8","9","10","11","12"], -35, 10, 750, 40, 35, 15)

        self.GUI_room = GUI_room_representation(self.screen, self.GUI_option.agent_to_display, self.GUI_option.target_to_display, x_offset,y_offset, scale_x,scale_y)
        self.GUI_pred = GUI_predictions(self.screen, self.GUI_option.agent_to_display,self.GUI_option.target_to_display, x_offset,y_offset,scale_x, scale_y, 2)
        self.font = pygame.font.SysFont("monospace", 15)

    def run(self, room):
        self.display_simulation_button()
        self.GUI_room.draw_room(room.coordinate_room)
        self.GUI_room.draw_all_target_room_description(room, self.GUI_option.agent_to_display, AgentType.AGENT_CAM)
        self.GUI_room.draw_agentCam_room_description(room, self.GUI_option.agent_to_display, AgentType.AGENT_CAM,True)
        self.GUI_room.draw_link_cam_region_room_description(room, self.GUI_option.agent_to_display, AgentType.AGENT_CAM,True)

        if self.button_simulation_1.find_button_state("prediction"):
            self.GUI_pred.drawPredictions(room)

    def display_simulation_button(self):
        for button in self.button_simulation_1.list:
            self.GUI_option.check_button(button)

        for button in self.button_simulation_2.list:
            self.GUI_option.check_button(button)
            if button.pressed:
                self.GUI_option.option_add_agent(int(button.text))
            else:
                self.GUI_option.option_remove_agent(int(button.text))

        for button in self.button_simulation_3.list:
            self.GUI_option.check_button(button)
            if button.pressed:
                self.GUI_option.option_add_target(int(button.text))
            else:
                self.GUI_option.option_remove_target(int(button.text))


        self.button_simulation_1.draw(self.screen)
        self.button_simulation_2.draw(self.screen)
        self.button_simulation_3.draw(self.screen)