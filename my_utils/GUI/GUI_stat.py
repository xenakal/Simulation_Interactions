import pygame

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


class GUI_stat:
    def __init__(self, screen, x_off, y_off):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15)

        self.x_offset = x_off
        self.y_offset = y_off

    def draw_stat_message(self, room):
        pygame.draw.rect(self.screen, BLACK, (0, 30, 800, 600))
        self.draw_stat_message_sent(room)
        self.draw_stat_message_receive(room)

    def draw_stat_message_sent(self, room):
        pas = 50
        n = 1

        x_off = 40
        y_off = 40

        label = self.font.render("Message sent", 20, WHITE)
        self.screen.blit(label, (self.x_offset + x_off - 5, self.y_offset + y_off - 50))

        label = self.font.render("Sender", 20, RED)
        self.screen.blit(label, (self.x_offset + x_off, self.y_offset + y_off - 35))

        label = self.font.render("Receiver", 20, GREEN)
        self.screen.blit(label, (self.x_offset + x_off, self.y_offset + y_off - 20))

        for agent in room.agentCam:
            label1 = self.font.render(str(agent.id), 20, GREEN)
            label2 = self.font.render(str(agent.id), 20, RED)
            self.screen.blit(label1, (self.x_offset + x_off + n * pas, self.y_offset + y_off))
            self.screen.blit(label2, (self.x_offset + x_off, self.y_offset + n * pas + y_off))
            n = n + 1

        m = 1
        for agent in room.agentCam:
            n = 1
            for agent_receiver in room.agentCam:
                label = self.font.render(str(agent.message_stat.get_messageNumber_sent(agent_receiver)), 20, WHITE)
                self.screen.blit(label, (self.x_offset + x_off + n * pas, self.y_offset + y_off + m * pas))
                n = n + 1
            m = m + 1

    def draw_stat_message_receive(self, room):
        pas = 50
        n = 1

        x_off = 350
        y_off = 40

        label = self.font.render("Message received", 20, WHITE)
        self.screen.blit(label, (self.x_offset + x_off - 5, self.y_offset + y_off - 50))

        label = self.font.render("Sender", 20, RED)
        self.screen.blit(label, (self.x_offset + x_off, self.y_offset + y_off - 35))

        label = self.font.render("Receiver", 20, GREEN)
        self.screen.blit(label, (self.x_offset + x_off, self.y_offset + y_off - 20))

        for agent in room.agentCam:
            label1 = self.font.render(str(agent.id), 20, RED)
            label2 = self.font.render(str(agent.id), 20, GREEN)
            self.screen.blit(label1, (self.x_offset + x_off + n * pas, self.y_offset + y_off))
            self.screen.blit(label2, (self.x_offset + x_off, self.y_offset + n * pas + y_off))
            n = n + 1
            # print(agent.message_stat.to_string())

        m = 1
        for agent in room.agentCam:
            n = 1
            for agent_receiver in room.agentCam:
                label = self.font.render(str(agent.message_stat.get_messageNumber_received(agent_receiver)), 20, WHITE)
                self.screen.blit(label, (self.x_offset + x_off + m * pas, self.y_offset + y_off + n * pas))
                n = n + 1
            m = m + 1
