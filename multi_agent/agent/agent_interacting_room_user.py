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
    """
        Class AgentUser extend AgentInteractingWithRoom.

        Description :

            :param
                1. (int) id                              -- numerical value to recognize the Agent
                2. (AgentType) type                      -- to distinguish the different agent
                3. ((int),(int),(int)) color             -- color representation for the GUI

            :attibutes
                -- IN AgentInteractingWithRoom
                1. (int) id                                     -- numerical value to recognize the Agent
                2. (int) signature                              -- numerical value to identify the Agent, random value
                3. (AgentType) type                             -- distinguish the different agent
                4. ((int),(int),(int)) color                    -- color representation for the GUI
                5. (ListMessage) info_message_sent              -- list containing all the messages sent
                6. (ListMessage) info_message_received          -- list containing all the messages received
                7. (ListMessage) info_message_to_send           -- list containing all the messages to send
                8. (AgentStatistic) message_statistic           -- object to compute how many messages are sent and
                                                                   received
                9. (Memory) memory                              -- object to deal with TargetEstimator
               10. (RoomRepresentation) room_representation     -- object to reconstruct the room
               11. (int) thread_is_running                      -- runnig if 1, else stop
               12. (thread) main_thread                         -- thread

            :notes
                fells free to write some comments.
    """
    number_agentUser_created = 0

    def __init__(self):
        super().__init__(AgentUser.number_agentUser_created, AgentType.AGENT_USER)
        AgentUser.number_agentUser_created +=1

    def thread_run(self):
        """
            :description
                FSM defining the agent's behaviour
        """

        state = "processData"
        nextstate = state
        last_heart_beat_sent = time.time()

        while self.thread_is_running == 1:
            state = nextstate
            if nextstate == "processData":
                '''Combination of data received and data observed'''
                self.memory.combine_data_userCam()
                '''Modification from the room description'''
                self.room_representation.update_target_based_on_memory(self.memory.memory_agent)
                '''Descision of the messages to send'''
                self.process_information_in_memory()
                nextstate = "communication"

            elif state == "communication":
                '''Suppression of unusefull messages in the list'''
                self.info_message_sent.remove_message_after_given_time(constants.get_time(), constants.MAX_TIME_MESSAGE_IN_LIST)
                self.info_message_received.remove_message_after_given_time(constants.get_time(), constants.MAX_TIME_MESSAGE_IN_LIST)

                "Send heart_beat to other agent"
                last_heart_beat_sent = self.send_message_heartbeat(last_heart_beat_sent, 1)

                '''Message are send (Mailbox)'''
                self.send_messages()
                '''Read messages received'''
                self.receive_messages()
                '''Prepare short answers'''
                self.process_message_received()
                '''Find if other agents reply to a previous message'''
                self.process_message_sent()

                self.log_room.info(self.memory.statistic_to_string() + self.message_statistic.to_string())
                time.sleep(constants.TIME_SEND_READ_MESSAGE)
                nextstate = "processData"
            else:
                print("FSM not working proerly")
