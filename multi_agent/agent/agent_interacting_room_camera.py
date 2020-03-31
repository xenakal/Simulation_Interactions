import threading
import mailbox
import logging
from multi_agent.elements.target import *
# from elements.room import*
import multi_agent.elements.room
from multi_agent.agent.agent_interacting_room import *
from multi_agent.tools.memory import *
from multi_agent.communication.message import *
from multi_agent.tools.behaviour_detection import *
from multi_agent.tools.link_target_camera import *
import constants


class MessageTypeAgentCameraInteractingWithRoom(MessageTypeAgentInteractingWithRoom):
    INFO_DKF = "info_DKF"


class AgentCameraCommunicationBehaviour:
    ALL = "all"
    DKF = "dkf"
    NONE = "none"


class AgentCam(AgentInteractingWithRoom):
    """
        Class AgentCam extend AgentInteractingWithRoom.

        Description :

            :param
                1. (int) id                              -- numerical value to recognize the Agent
                2. (string) type                         -- to distinguish the different agent
                3. ((int),(int),(int)) color             -- color representation for the GUI

            :attibutes
                -- IN AgentInteractingWithRoom
                1. (int) id                                     -- numerical value to recognize the Agent
                2. (int) signature                              -- numerical value to identify the Agent, random value
                3. (string) type                                -- to distinguish the different agent
                4. ((int),(int),(int)) color                    -- color representation for the GUI
                5. (ListMessage) info_message_sent              -- list containing all the messages sent
                6. (ListMessage) info_message_received          -- list containing all the messages received
                7. (ListMessage) info_message_to_send           -- list containing all the messages to send
                8. (AgentStatistic) message_statistic           -- object to compute how many messages are
                                                                    sent and received
                9. (Memory) memory                              -- object to deal with TargetEstimator
               10. (RoomRepresentation) room_representation     -- object to reconstruct the room
               11. (int) thread_is_running                      -- running if 1, else stop
               12. (thread) main_thread                         -- thread

               --New
               13. (Camera) camera                              -- Camera object, allows target to detect
                                                                   object in the room
               14. (TargetBehaviourAnalyser) behaviour_analyser -- TargetBehaviourAnalyser object,
                                                                    to detect some feature from the target
               15 (LinkTargetCamera) link_target_agent         -- LinkTargetCamera object, to tell the agent
                                                                   wich target to track taking into account the
                                                                   geometry from the room and the position of targets
            :notes
                fells free to write some comments.
    """
    number_agentCam_created = 0

    def __init__(self, camera, t_add=-1, t_del=-1):

        if t_add == -1 or t_del == -1:
            t_add = [0]
            t_del = [constants.TIME_STOP]

        self.camera = camera
        super().__init__(AgentCam.number_agentCam_created, AgentType.AGENT_CAM, t_add, t_del, camera.color)
        self.behaviour_analyser = TargetBehaviourAnalyser(self.memory)
        self.link_target_agent = LinkTargetCamera(self.room_representation)
        self.log_execution = create_logger(constants.ResultsPath.LOG_AGENT, "Execution time", self.id)
        AgentCam.number_agentCam_created += 1

    def init_and_set_room_description(self, room):
        """
            :description
                1. set the RoomDescription
                2. set the AgentStatistic
                3. set the LinkTargetCamera

            :param
                1. (Room) room  --  To set up the RoomDescription

        """
        self.log_main.info("starting initialisation in agent_interacting_room_agent_cam")
        super().init_and_set_room_description(room)
        self.link_target_agent = LinkTargetCamera(self.room_representation)
        self.log_main.info("initialisation in agent_interacting_room__cam_done !")

    def thread_run(self):
        """
            :description
                FSM defining the agent's behaviour
        """

        state = "takePicture"
        nextstate = state
        time_last_heartbeat_sent = constants.get_time()
        execution_loop_number = 0
        execution_time_start = 0
        execution_mean_time = 0

        while self.thread_is_running == 1:
            state = nextstate


            if state == "takePicture":
                execution_time_start = constants.get_time()
                self.log_execution.debug("Loop %d : at takePicture state after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

                "Input from the agent, here the fake room"
                picture = self.camera.run()
                time.sleep(constants.TIME_PICTURE)

                "Allows to simulate crash of the camera"
                if not self.camera.isActive:
                    nextstate = "takePicture"
                    time.sleep(0.3)
                else:
                    for targetCameraDistance in picture:
                        target = targetCameraDistance.target
                        "Simulation from noise on the target's position "
                        if constants.INCLUDE_ERROR and not target.type == TargetType.SET_FIX:
                            erreurPX = np.random.normal(scale=constants.STD_MEASURMENT_ERROR_POSITION, size=1)[0]
                            erreurPY = np.random.normal(scale=constants.STD_MEASURMENT_ERROR_POSITION, size=1)[0]
                            erreurVX = np.random.normal(scale=constants.STD_MEASURMENT_ERROR_SPEED, size=1)[0]
                            erreurVY = np.random.normal(scale=constants.STD_MEASURMENT_ERROR_SPEED, size=1)[0]
                            erreurAX = np.random.normal(scale=constants.STD_MEASURMENT_ERROR_ACCCELERATION, size=1)[0]
                            erreurAY = np.random.normal(scale=constants.STD_MEASURMENT_ERROR_ACCCELERATION, size=1)[0]
                        else:
                            erreurPX = 0
                            erreurPY = 0
                            erreurVX = 0
                            erreurVY = 0
                            erreurAX = 0
                            erreurAY = 0

                        target_type = TargetType.UNKNOWN
                        for target_representation in self.room_representation.active_Target_list:
                            if target_representation.id == target.id:
                                target_type = target_representation.type

                        self.memory.add_create_target_estimator(constants.get_time(), self.id,
                                                                self.signature, target.id, target.signature,
                                                                target.xc + erreurPX, target.yc + erreurPY,
                                                                target.vx + erreurVX, target.vy + erreurVY,
                                                                target.ax + erreurAX, target.ay + erreurAY,
                                                                target.radius, target_type)

                    nextstate = "processData"
                    self.log_execution.debug("Loop %d : takePicture state completed after : %.02f s" % (
                        execution_loop_number, constants.get_time() - execution_time_start))

            elif nextstate == "processData":
                self.log_execution.debug("Loop %d : at processData state after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

                self.memory.set_current_time(constants.get_time())
                self.process_information_in_memory()

                nextstate = "communication"
                self.log_execution.debug("Loop %d : processData state completed after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

            # TODO: pas mieux de mettre ca avant "processData" ?
            elif state == "communication":
                self.log_execution.debug("Loop %d : at communication state after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

                "Suppression of unusefull messages in the list"
                self.info_message_sent.remove_message_after_given_time(constants.get_time(),
                                                                       constants.MAX_TIME_MESSAGE_IN_LIST)
                self.info_message_received.remove_message_after_given_time(constants.get_time(),
                                                                           constants.MAX_TIME_MESSAGE_IN_LIST)

                "Send heart_beat to other agent"
                time_last_heartbeat_sent = self.handle_hearbeat(time_last_heartbeat_sent)

                "Message are send (Mailbox)"
                self.send_messages()
                "Read messages received"
                self.receive_messages()
                "Prepare short answers"
                self.process_message_received()
                "Find if other agents reply to a previous message"
                self.process_message_sent()

                time.sleep(constants.TIME_SEND_READ_MESSAGE)

                self.log_room.info(self.memory.statistic_to_string() + self.message_statistic.to_string())
                nextstate = "takePicture"

                self.log_execution.debug("Loop %d :communication state  executed after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))
                self.log_execution.info("time : %.02f s, loop %d : completed in : %.02f s" % (
                    constants.get_time(), execution_loop_number, constants.get_time() - execution_time_start))
                execution_loop_number += 1
                execution_mean_time += constants.get_time() - execution_time_start
            else:
                print("FSM not working proerly")
                self.log_execution.warning("FSM not working as expected")

        self.log_execution.info("Execution mean time : %.02f s", execution_mean_time / execution_loop_number)

    def process_information_in_memory(self):
        """
            :description
                Process all the information obtain
        """

        "Combination of data received and data observed"
        self.memory.combine_data_agentCam()

        "Modification from the room description"
        self.room_representation.update_target_based_on_memory(self.memory.memory_agent)

        "Computation of the camera that should give the best view, according to map algorithm"
        self.link_target_agent.update_link_camera_target()
        self.link_target_agent.compute_link_camera_target()

        for target in self.room_representation.active_Target_list:
            """
                ---------------------------------------------------------------------------------------------
                Memory analysis: 
                    -> Behaviour
                        - detection from moving, stop , changing state targest
                        - detection from target leaving the field of the camera
                ---------------------------------------------------------------------------------------------
            """
            is_target_changing_state = False
            if not target.type == TargetType.SET_FIX:
                "Check if the target is moving,stopped or changing from one to the other state"
                (is_moving, is_stopped) = self.behaviour_analyser.detect_target_motion(target.id, 1, 5,
                                                                                       constants.STD_MEASURMENT_ERROR_POSITION + 0.01)
                "Check if the target is leaving the cam angle_of_view"
                (is_in, is_out) = self.behaviour_analyser.is_target_leaving_cam_field(self.camera, target.id, 0, 3)

                old_target_type = target.type
                if is_moving:
                    target.type = TargetType.MOVING
                elif is_stopped:
                    target.type = TargetType.FIX
                else:
                    target.type = TargetType.UNKNOWN

                if not old_target_type == target.type:
                    is_target_changing_state = True
                    self.log_main.info("At %.02f Target %d change state from "%(constants.get_time(),target.id)+ str(old_target_type) + " to " + str(target.type))

            """
                ----------------------------------------------------------------------------------------------
                Data to send other cam's agent:
                -----------------------------------------------------------------------------------------------
            """
            "Send message to other agent"
            if constants.DATA_TO_SEND == AgentCameraCommunicationBehaviour.ALL:
                memories = self.memory.memory_agent.get_Target_list(target.id)
                if len(memories) > 0:
                    last_memory = memories[-1]
                    self.send_message_targetEstimator(last_memory)

            elif constants.DATA_TO_SEND == AgentCameraCommunicationBehaviour.DKF:
                self.send_message_DKF_info(target.id)

            elif constants.DATA_TO_SEND == AgentCameraCommunicationBehaviour.NONE:
                pass

            """
               ----------------------------------------------------------------------------------------------
               Data to send user's agent:
               -----------------------------------------------------------------------------------------------
            """
            "If the target is link to this agent then we send the message to the user"
            cdt_target_type_1 = not(target.type == TargetType.SET_FIX)
            cdt_target_type_2 = True #not(target.type == TargetType.FIX) or is_target_changing_state #to decrease the number of messages sent 
            cdt_agent_is_in_charge = self.link_target_agent.is_in_charge(target.id, self.id)

            memories = self.memory.memory_agent.get_Target_list(target.id)
            if len(memories) > 0:
                last_memory = memories[-1]
                cdt_message_not_to_old = ((constants.get_time() - last_memory.time_stamp) <= constants.TRESH_TIME_TO_SEND_MEMORY)

                if cdt_agent_is_in_charge and cdt_target_type_1  and cdt_target_type_2 and cdt_message_not_to_old :
                    receivers = []
                    for agent in self.room_representation.active_AgentUser_list:
                        receivers.append([agent.id, agent.signature])

                    self.send_message_targetEstimator(last_memory, receivers)

    def process_single_message(self, rec_mes):
        super().process_single_message(rec_mes)
        if rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.INFO_DKF:
            self.receive_message_DKF_info(rec_mes)

    def get_predictions(self, target_id_list):
        """
        :return: a list [[targetId, [predicted_position1, ...]], ...]
        """
        return self.memory.get_predictions(target_id_list)

    def send_message_DKF_info(self, target_id):
        """
        :description
            Send a message containing the information needed for the distribution of the Kalman Filter.
        :param (int) target_id  -- id of tracked target for which we're sending the info
        """

        dfk_info_string = self.memory.get_DKF_info_string(target_id)

        # message containing the DKF information to send
        message = Message(constants.get_time(), self.id, self.signature,
                          MessageTypeAgentCameraInteractingWithRoom.INFO_DKF, dfk_info_string, target_id)

        # send the message to every other agent
        for agent in self.room_representation.agentCams_list:
            if agent.id != self.id:
                message.add_receiver(agent.id, agent.signature)

        # add message to the list if not already inside
        cdt = self.info_message_to_send.is_message_with_same_message(message)
        if not cdt:
            self.info_message_to_send.add_message(message)

    def receive_message_DKF_info(self, message):
        """
        :description
            Receive a message contaning the information needed for the distribtion of the Kalman Filter.
            When received, the filter associated with the tracked target is informed and can assimilate the new data.
        :param message: instance of Message class.
        """
        info_string = message.message
        concerned_target_id = message.target_id

        if info_string:  # if message not empty
            self.memory.process_DKF_info(concerned_target_id, info_string, constants.get_time())

