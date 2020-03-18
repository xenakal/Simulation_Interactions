import threading
import mailbox
import logging
from multi_agent.elements.target import *
import multi_agent.elements.room
from multi_agent.agent.agent_interacting_room import *
from multi_agent.communication.message import *
from multi_agent.tools.behaviour_detection import *
from multi_agent.tools.link_target_camera import *
from multi_agent.tools.memory import *
import constants

class AgentUser(AgentInteractingWithRoom):

    def __init__(self, idAgent):
        super().__init__(100+idAgent,"user")


    def thread_run(self):
        state = "processData"
        nextstate = state

        while self.threadRun == 1:
            state = nextstate
            if nextstate == "processData":
                '''Combination of data received and data observed'''
                self.memory.combine_data_userCam()
                '''Modification from the room description'''
                self.room_representation.update_target_based_on_memory(self.memory.memory_agent)
                '''Descision of the messages to send'''
                self.process_InfoMemory(self.room_representation)
                nextstate = "communication"

            elif state == "communication":
                '''Suppression of unusefull messages in the list'''
                self.info_messageSent.remove_message_after_given_time(self.room_representation.time, 30)
                self.info_messageReceived.remove_message_after_given_time(self.room_representation.time, 30)

                '''Message are send (Mailbox)'''
                self.sendAllMessage()
                '''Read messages received'''
                self.recAllMess()
                '''Prepare short answers'''
                self.process_Message_received()
                '''Find if other agents reply to a previous message'''
                self.process_Message_sent()

                self.log_room.info(self.memory.statistic_to_string() + self.message_stat.to_string())
                time.sleep(constants.TIME_SEND_READ_MESSAGE)
                nextstate = "processData"
            else:
                print("FSM not working proerly")
