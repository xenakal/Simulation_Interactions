from src.my_utils.my_IO.IO_map import save_room_to_txt
from src.my_utils.GUI.button import ButtonList
from src.my_utils.GUI.GUI_simulation.GUI_memories import GUI_memories
from src.my_utils.GUI.GUI_simulation.GUI_room_representation import GUI_room_representation
from src.my_utils.GUI.GUI_simulation.GUI_agent_target_detected import *
from src.my_utils.GUI.GUI_simulation.GUI_predictions import *
from src.my_utils.GUI.GUI_simulation.GUI_agent_region import *


class GUI_simulation:
    def __init__(self, screen, GUI_option,x_offset,y_offset,scale_x,scale_y):
        pygame.init()

        self.screen = screen
        self.GUI_option = GUI_option

        self.button_simulation_1 = ButtonList(["real T", "M agent","+ received","M all agent", "prediction"], 10, -20, 0, 40, 100,20)
        self.button_simulation_2 = ButtonList(["0", "1", "2", "3", "4", "5", "6","7","8","9","10","11","12"], -35, 10, 700, 40, 35, 15)
        self.button_simulation_3 = ButtonList(["0", "1", "2", "3", "4", "5", "6","7","8","9","10","11","12"], -35, 10, 750, 40, 35, 15)
        self.button_simulation_4 = ButtonList(["save to txt","Cam ROI","Cam COV","User's O"], -100, 10, 0, 100, 100, 20)

        self.GUI_room = GUI_room_representation(self.screen, self.GUI_option.agent_to_display, self.GUI_option.target_to_display, x_offset,y_offset, scale_x,scale_y,GUI_option)
        self.GUI_memories = GUI_memories(self.screen, self.GUI_option.agent_to_display,self.GUI_option.target_to_display,x_offset,y_offset, scale_x, scale_y)
        self.GUI_ATD = GUI_Agent_Target_Detected(self.screen)
        self.GUI_pred = GUI_predictions(self.screen, self.GUI_option.agent_to_display,self.GUI_option.target_to_display, x_offset,y_offset,scale_x, scale_y, 2)
        self.Gui_region = GUI_Region(self.screen,x_offset,y_offset ,scale_x,scale_y)

        self.font = pygame.font.SysFont("monospace", 15)

    def run(self, room, region, link_cam_to_target):
        self.display_simulation_button()
        self.GUI_room.draw_room(room.coordinate_room, True)



        if self.button_simulation_4.find_button_state("Cam ROI"):
            self.Gui_region.draw_cam_region(room, region)

        if self.button_simulation_4.find_button_state("Cam COV"):
            self.Gui_region.draw_cam_coverage(region)

        if self.button_simulation_1.find_button_state("real T"):
            self.GUI_room.draw_one_target_all_previous_position(room)

        if self.button_simulation_1.find_button_state("M agent"):
            self.GUI_memories.drawMemory(room)

        if self.button_simulation_1.find_button_state("M all agent"):
           self.GUI_memories.drawMemory(room, True)

        if self.button_simulation_1.find_button_state("+ received"):
            self.GUI_memories.draw_mesure_and_receiveMessages(room)

        if self.button_simulation_4.find_button_state("save to txt"):
            save_room_to_txt("Current_map.txt",room)
            self.button_simulation_4.find_button("save to txt").set_button(False)

        self.GUI_room.draw_all_target(room.active_Target_list, room.coordinate_room)
        self.GUI_room.draw_all_agentCam(room.agentCams_representation_list)
        self.GUI_room.draw_link_cam_region(room, link_cam_to_target)

        if self.button_simulation_4.find_button_state("User's O"):
            self.GUI_room.draw_all_target_room_description(room, self.GUI_option.agent_to_display, AgentType.AGENT_USER, True)

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

        for button in self.button_simulation_4.list:
            self.GUI_option.check_button(button)

        x_offset = 0
        y_offset = 500
        y_range = 15
        y_pas = 15

        s = "agent: "
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset + y_range))
        y_range = y_range + y_pas

        s = "list: " + str(self.GUI_option.agent_to_display)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset + y_range))
        y_range = y_range + y_pas

        s = "target: "
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset + y_range))
        y_range = y_range + y_pas

        s = "list: " + str(self.GUI_option.target_to_display)
        label = self.font.render(s, 10, WHITE)
        self.screen.blit(label, (x_offset, y_offset + y_range))

        self.button_simulation_1.draw(self.screen)
        self.button_simulation_2.draw(self.screen)
        self.button_simulation_3.draw(self.screen)
        self.button_simulation_4.draw(self.screen)
