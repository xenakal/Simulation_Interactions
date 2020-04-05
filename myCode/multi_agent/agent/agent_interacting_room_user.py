from myCode.multi_agent.elements.target import *
from myCode.multi_agent.agent.agent_interacting_room import *
from myCode import constants
import time

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
        t_add = [0]
        t_del = [constants.TIME_STOP]
        super().__init__(AgentUser.number_agentUser_created, AgentType.AGENT_USER,t_add,t_del)
        self.log_execution = create_logger(constants.ResultsPath.LOG_AGENT, "Execution time", self.id)
        AgentUser.number_agentUser_created +=1

    def thread_run(self):
        """
            :description
                FSM defining the agent's behaviour
        """

        state = "processData"
        nextstate = state
        time_last_heartbeat_sent = constants.get_time()
        execution_loop_number = 0
        execution_time_start = 0
        execution_mean_time = 0

        while self.thread_is_running == 1:
            state = nextstate
            if nextstate == "processData":
                execution_time_start = constants.get_time()
                self.log_execution.debug("Loop %d : at processData state after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

                '''Combination of data received and data observed'''
                self.memory.combine_data_userCam()
                '''Modification from the room description'''
                self.room_representation.update_target_based_on_memory(self.memory.memory_agent)
                '''Descision of the messages to send'''
                self.process_information_in_memory()

                nextstate = "communication"
                self.log_execution.debug("Loop %d : processData state completed after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

            elif state == "communication":
                self.log_execution.debug("Loop %d : at communication state after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

                '''Suppression of unusefull messages in the list'''
                self.info_message_sent.remove_message_after_given_time(constants.get_time(), constants.MAX_TIME_MESSAGE_IN_LIST)
                self.info_message_received.remove_message_after_given_time(constants.get_time(), constants.MAX_TIME_MESSAGE_IN_LIST)

                "Send heart_beat to other agent"
                time_last_heartbeat_sent = self.handle_hearbeat(time_last_heartbeat_sent)

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

                self.log_execution.debug("Loop %d :communication state  executed after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))
                self.log_execution.info("time : %.02f s, loop %d : completed in : %.02f s" % (
                    constants.get_time(), execution_loop_number, constants.get_time() - execution_time_start))
                execution_loop_number += 1
                execution_mean_time += constants.get_time() - execution_time_start

                # sleep to avoid sending messages to quickly
                time.sleep(constants.TIME_TO_SLOW_DOWN)

            else:
                print("FSM not working proerly")
                self.log_execution.warning("FSM not working as expected")

        self.log_execution.info("Execution mean time : %.02f s", execution_mean_time / execution_loop_number)