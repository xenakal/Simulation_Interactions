import threading
import mailbox
import logging
from multi_agent.elements.target import *
# from elements.room import*
import multi_agent.elements.room
from multi_agent.agent.agent_interacting_room import *
from multi_agent.tools.memory import *
from multi_agent.communication.message import *
from multi_agent.prediction.kalmanPredictionOld import *
from multi_agent.tools.behaviour_detection import *
from multi_agent.tools.link_target_camera import *
import constants


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

    def __init__(self, camera):
        self.camera = camera
        super().__init__(AgentCam.number_agentCam_created, AgentType.AGENT_CAM, camera.color)
        self.behaviour_analyser = TargetBehaviourAnalyser(self.memory)
        self.link_target_agent = LinkTargetCamera(self.room_representation)
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
        last_heart_beat_sent = time.time()

        while self.thread_is_running == 1:
            state = nextstate

            if state == "takePicture":

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
                        if constants.INCLUDE_ERROR and not (target.type == TargetType.SET_FIX):
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
                                                                target.vx + erreurVX, target.vy + erreurPY,
                                                                target.ax + erreurAX, target.ay + erreurAY,
                                                                target.radius, target_type)

                    nextstate = "processData"

            elif nextstate == "processData":
                self.memory.set_current_time(constants.get_time())
                self.process_information_in_memory()
                nextstate = "communication"

            # TODO: pas mieux de mettre ca avant "processData" ?
            elif state == "communication":
                "Suppression of unusefull messages in the list"
                self.info_message_sent.remove_message_after_given_time(constants.get_time(),
                                                                       constants.MAX_TIME_MESSAGE_IN_LIST)
                self.info_message_received.remove_message_after_given_time(constants.get_time(),
                                                                           constants.MAX_TIME_MESSAGE_IN_LIST)

                "Send heart_beat to other agent"
                last_heart_beat_sent = self.send_message_heartbeat(last_heart_beat_sent, 1)

                "Message are send (Mailbox)"
                self.send_messages()
                "Read messages received"
                self.receive_messages()
                "Prepare short answers"
                self.process_message_received()
                "Find if other agents reply to a previous message"
                self.process_message_sent()

                self.log_room.info(self.memory.statistic_to_string() + self.message_statistic.to_string())
                time.sleep(constants.TIME_SEND_READ_MESSAGE)
                nextstate = "takePicture"
            else:
                print("FSM not working proerly")

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
            if not target.type == TargetType.SET_FIX:
                "Check if the target is moving,stopped or changing from one to the other state"
                (is_moving, is_stopped) = self.behaviour_analyser.detect_target_motion(target.id, 1, 5,
                                                                                       constants.STD_MEASURMENT_ERROR_POSITION + 0.01)
                "Check if the target is leaving the cam angle_of_view"
                (is_in, is_out) = self.behaviour_analyser.is_target_leaving_cam_field(self.camera, target.id, 0, 3)

                if is_moving:
                    target.type = TargetType.MOVING
                elif is_stopped:
                    target.type = TargetType.FIX
                else:
                    target.type = TargetType.UNKNOWN

            """
                ----------------------------------------------------------------------------------------------
                Data to send other cam's agent:
                -----------------------------------------------------------------------------------------------
            """
            "Send message to other agent"
            if constants.DATA_TO_SEND == "all":
                memories = self.memory.memory_agent.get_Target_list(target.id)
                if len(memories) > 0:
                    last_memory = memories[len(memories) - 1]
                    self.send_message_targetEstimator(last_memory)

            elif constants.DATA_TO_SEND == "behaviour":
                "If the target stop is it because we loose it, or is the target outside from the range ? "
                pass
                "Demande de confirmation à un autre agent par exemple"

            """
               ----------------------------------------------------------------------------------------------
               Data to send user's agent:
               -----------------------------------------------------------------------------------------------
            """
            "If the target is link to this agent then we send the message to the user"
            if self.link_target_agent.is_in_charge(target.id, self.id):
                memories = self.memory.memory_agent.get_Target_list(target.id)
                if len(memories) > 0:
                    receivers = []

                    for agent in self.room_representation.active_AgentUser_list:
                        receivers.append([agent.id, agent.signature])
                    last_memory = memories[len(memories) - 1]

                    "If the message is to old we don't send it -> target lost"
                    thresh_time_to_send = 3
                    if constants.get_time() - last_memory.time_stamp <= thresh_time_to_send:
                        self.send_message_targetEstimator(last_memory, receivers)

    def get_predictions(self, target_id_list):
        """
        :return: a list [[targetId, [predicted_position1, ...]], ...]
        """
        return self.memory.get_predictions(target_id_list)
