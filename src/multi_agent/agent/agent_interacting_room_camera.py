# from elements.room import*
import copy
from warnings import warn

import src.multi_agent.elements.room as room
from src.multi_agent.agent.agent_interacting_room import *
from src.multi_agent.communication.message import *
from src.multi_agent.tools.behaviour_agent import PCA_track_points_possibilites, get_configuration_based_on_seen_target
from src.multi_agent.tools.behaviour_detection import *
from src.multi_agent.tools.link_target_camera import *
from src.my_utils.controller import CameraController
from src import constants
from src.constants import AgentCameraCommunicationBehaviour
import time
import src.multi_agent.elements.mobile_camera as mobCam
import src.multi_agent.elements.camera as cam


class MessageTypeAgentCameraInteractingWithRoom(MessageTypeAgentInteractingWithRoom):
    INFO_DKF = "info_DKF"
    AGENT_ESTIMATOR = "agentEstimator"


class AgentCameraFSM:
    MOVE_CAMERA = "Move camera"
    TAKE_PICTURE = "Take picture"
    PROCESS_DATA = "Process Data"
    COMMUNICATION = "Communication"
    BUG = "Bug"


class Configuration:
    def __init__(self, x, y, alpha, beta):
        self.x = x
        self.y = y
        self.alpha = alpha
        self.beta = beta


class AgentCamRepresentation(AgentInteractingWithRoomRepresentation):
    def __init__(self, id, type):
        super().__init__(id, type)
        self.camera_representation = mobCam.MobileCameraRepresentation(0, 0, 0, 0, 0, 0, 0, 0)

    def update_from_agent(self, agent):
        super().update_from_agent(agent)
        self.camera_representation.init_from_camera(agent.camera)

    def update_from_agent_estimator(self, agent_estimator):
        self.id = agent_estimator.agent_id
        self.signature = agent_estimator.agent_signature  # always higher than 100
        self.type = agent_estimator.item_type
        self.is_active = agent_estimator.is_agent_active
        self.color = agent_estimator.color
        self.camera_representation.init_from_values_extend(agent_estimator.item_id, agent_estimator.item_signature,
                                                           agent_estimator.item_position[0],
                                                           agent_estimator.item_position[1],
                                                           agent_estimator.alpha, agent_estimator.beta,
                                                           agent_estimator.field_depth, agent_estimator.error_pos,
                                                           agent_estimator.error_speed, agent_estimator.error_acc,
                                                           agent_estimator.color, agent_estimator.is_camera_active,
                                                           agent_estimator.item_type, agent_estimator.trajectory)


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
        self.camera_controller = None
        self.link_target_agent = None
        self.memory_of_objectives = []
        self.memory_of_position_to_reach = []

        self.time_last_message_agentEstimtor_sent = constants.get_time()

        self.log_execution = create_logger(constants.ResultsPath.LOG_AGENT, "Execution time", self.id)
        AgentCam.number_agentCam_created += 1

        # targets to be tracked by this agent
        self.targets_to_track = []
        self.initialized_targets_to_track = False
        # targets in self.targets_to_track for which a configuration wasn't found
        self.untrackable_targets = []

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
        self.link_target_agent = LinkTargetCamera(self.room_representation, True)
        self.camera_controller = CameraController(0.2, 0, 0.4, 0, 0.2, 0)
        self.camera_controller.set_targets(self.camera.xc, self.camera.yc, self.camera.alpha, self.camera.beta)

        self.log_main.info("initialisation in agent_interacting_room__cam_done !")

    def init_targets_to_track(self):
        if constants.INIT_TARGET_LIST == constants.AgentCameraInitializeTargetList.ALL_SEEN:
            self.init_targets_to_track_from_seen()
        else:
            warn("Invalid method for initializing targets to tracks, default will be used.")
            self.init_targets_to_track_from_seen()

    def init_targets_to_track_from_seen(self):
        """ Initializes the targets to track as all targets seen by the agent at the time of initialization. """
        self.targets_to_track = copy.copy(self.room_representation.active_Target_list)

    def thread_run(self, real_room):
        """
            :description
                FSM defining the agent's behaviour
        """

        if constants.AGENTS_MOVING:
            state = AgentCameraFSM.MOVE_CAMERA
        else:
            state = AgentCameraFSM.TAKE_PICTURE

        nextstate = state

        execution_loop_number = 1
        execution_time_start = 0
        execution_mean_time = 0

        last_time_move = None

        while self.thread_is_running == 1:
            state = nextstate
            last_not_None_configuration = None

            if state == AgentCameraFSM.MOVE_CAMERA:

                if last_time_move is not None:

                    # if agent sees untracked target: track it & broadcast IS_TRACKED message
                    #                                            --> untrack target if n ACKs received
                    self.track_seen_targets_and_ask()

                    # find a configuration for the agent
                    configuration = self.find_configuration_for_tracked_targets()
                    if configuration is not None:
                        last_not_None_configuration = configuration

                    # move agent according to configuration found
                    last_time_move = self.move_based_on_config(last_not_None_configuration, last_time_move)
                else:
                    last_time_move = constants.get_time()

                """Create a new memory to save the """
                self.memory.add_create_agent_estimator_from_agent(constants.get_time(), self, self)

                if not self.camera.is_active or not self.is_active:
                    nextstate = AgentCameraFSM.BUG
                else:
                    nextstate = AgentCameraFSM.TAKE_PICTURE

            elif state == AgentCameraFSM.TAKE_PICTURE:
                execution_time_start = constants.get_time()
                self.log_execution.debug("Loop %d : at takePicture state after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

                "Input from the agent, here the fake room"
                picture = self.camera.run(real_room)
                time.sleep(constants.TIME_PICTURE)

                "Allows to simulate crash of the camera"
                if not self.camera.is_active:
                    nextstate = AgentCameraFSM.PROCESS_DATA
                elif not self.is_active:
                    nextstate = AgentCameraFSM.BUG
                else:
                    for targetCameraDistance in picture:
                        target = targetCameraDistance.target
                        "Simulation from noise on the target's position "
                        if constants.INCLUDE_ERROR and not target.type == TargetType.SET_FIX:
                            erreurPX = np.random.normal(scale=self.camera.std_measurment_error_position, size=1)[0]
                            erreurPY = np.random.normal(scale=self.camera.std_measurment_error_position, size=1)[0]
                            erreurVX = np.random.normal(scale=self.camera.std_measurment_error_speed, size=1)[0]
                            erreurVY = np.random.normal(scale=self.camera.std_measurment_error_speed, size=1)[0]
                            erreurAX = np.random.normal(scale=self.camera.std_measurment_error_acceleration, size=1)[0]
                            erreurAY = np.random.normal(scale=self.camera.std_measurment_error_acceleration, size=1)[0]
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
                                                                target_type, target.radius)
                    nextstate = AgentCameraFSM.PROCESS_DATA
                    self.log_execution.debug("Loop %d : takePicture state completed after : %.02f s" % (
                        execution_loop_number, constants.get_time() - execution_time_start))

            elif nextstate == AgentCameraFSM.PROCESS_DATA:
                self.log_execution.debug("Loop %d : at processData state after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

                self.memory.set_current_time(constants.get_time())
                self.process_information_in_memory()

                if not self.is_active:
                    nextstate = AgentCameraFSM.BUG
                else:
                    nextstate = AgentCameraFSM.COMMUNICATION
                self.log_execution.debug("Loop %d : processData state completed after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

            elif state == AgentCameraFSM.COMMUNICATION:
                self.log_execution.debug("Loop %d : at communication state after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))

                "Suppression of unusefull messages in the list"
                self.info_message_sent.remove_message_after_given_time(constants.get_time(),
                                                                       constants.MAX_TIME_MESSAGE_IN_LIST)
                self.info_message_received.remove_message_after_given_time(constants.get_time(),
                                                                           constants.MAX_TIME_MESSAGE_IN_LIST)

                "Send heart_beat to other agent"
                self.handle_hearbeat()

                "Message are send (Mailbox)"
                self.send_messages()

                time.sleep(constants.TIME_SEND_READ_MESSAGE)

                "Read messages received"
                self.receive_messages()
                "Prepare short answers"
                self.process_message_received()
                "Find if other agents reply to a previous message"
                self.process_message_sent()

                self.log_room.info(self.memory.statistic_to_string() + self.message_statistic.to_string())

                if not self.initialized_targets_to_track:
                    self.init_targets_to_track()
                    self.initialized_targets_to_track = True

                if not self.is_active:
                    nextstate = AgentCameraFSM.BUG
                else:
                    if constants.AGENTS_MOVING:
                        nextstate = AgentCameraFSM.MOVE_CAMERA
                    else:
                        nextstate = AgentCameraFSM.TAKE_PICTURE

                self.log_execution.debug("Loop %d :communication state  executed after : %.02f s" % (
                    execution_loop_number, constants.get_time() - execution_time_start))
                self.log_execution.info("time : %.02f s, loop %d : completed in : %.02f s" % (
                    constants.get_time(), execution_loop_number, constants.get_time() - execution_time_start))
                execution_loop_number += 1
                execution_mean_time += constants.get_time() - execution_time_start

            elif state == AgentCameraFSM.BUG:
                time.sleep(3)
                print("bug")
                if not self.camera.is_active or not self.is_active:
                    nextstate = AgentCameraFSM.BUG
                else:
                    nextstate = AgentCameraFSM.MOVE_CAMERA
            else:
                print("FSM not working proerly")
                self.log_execution.warning("FSM not working as expected")

        self.log_execution.info("Execution mean time : %.02f s", execution_mean_time / execution_loop_number)

    def track_seen_targets_and_ask(self):
        """
        :description:
            Adds seen targets that are untracked by the agent and broadcasts a message to ask other agents if the target
            is already tracked. If so, it stops tracking the target.
        """
        for target in self.room_representation.active_Target_list:
            if target not in self.targets_to_track:
                self.targets_to_track.append(target)
        # TODO: send messages
        # TODO: remove target based on receive messages

    def move_based_on_config(self, configuration, last_time_move):

        if configuration is None:
            return

        self.camera_controller.set_targets(configuration.x, configuration.y, configuration.alpha, configuration.beta)

        """Define the values measured"""
        x_mes = self.camera.xc  # + error si on veut ajouter ici
        y_mes = self.camera.yc
        alpha_mes = self.camera.alpha
        beta_mes = self.camera.beta

        if self.camera.camera_type == mobCam.MobileCameraType.RAIL:
            "1 D"
            x_mes = self.camera.trajectory.sum_delta
            y_mes = 0

        """Find the command to apply"""
        (x_command, y_command, alpha_command, beta_command) = self.camera_controller.get_command(x_mes, y_mes,
                                                                                                 alpha_mes, beta_mes)

        """Apply the command"""
        if constants.get_time() - last_time_move < 0:
            print("problem time < 0 : %.02f s" % constants.get_time())
            return last_time_move
        else:
            dt = constants.get_time() - last_time_move
            if dt > 0.5 / constants.SCALE_TIME:
                dt = 0.5 / constants.SCALE_TIME
            self.camera.rotate(alpha_command, dt)
            self.camera.zoom(beta_command, dt)
            self.camera.move(x_command, y_command, dt)
            return constants.get_time()

    def find_configuration_for_tracked_targets(self):
        """
        :description:
            Updates self.untrackable_targets and returns a configuration for the targets the agent is able to track
        :return a configuration for the targets the agent is able to track, or None if he can't track any
        """

        # try to find a configuration covering all targets
        tracked_targets = copy.copy(self.targets_to_track)

        # do nothing if no targets need tracking
        if not tracked_targets:
            return None

        number_targets_to_remove = -1

        configuration = None
        while configuration is None:  # configuration not found

            # try to find configuration removing one more element if list not empty
            if tracked_targets:
                number_targets_to_remove += 1
                tracked_targets = copy.copy(self.targets_to_track)

            # if somehow couldn't find a configuration covering any of the elements
            if number_targets_to_remove >= len(tracked_targets):
                self.untrackable_targets = copy.copy(self.targets_to_track)
                return None

            # remove the desired number of targets
            # TODO: maybe try different permutations as well ?
            for _ in range(number_targets_to_remove):
                tracked_targets = self.remove_target_with_lowest_priority(tracked_targets)

            # print([target.id for target in tracked_targets])
            configuration = self.find_configuration_for_targets(tracked_targets)

        # update the list of untrackable targets
        self.untrackable_targets = [target for target in self.targets_to_track if target not in tracked_targets]
        #print("tracked_targets", [target.id for target in tracked_targets])
        #print("untrackable_targets", [target.id for target in self.untrackable_targets])
        return configuration

    def find_configuration_for_targets(self, targets):
        """
        :description:
            Checks if a configuration can be found where all targets are seen.
        :param targets: target representations
        :return: Configuration object if exists, None otherwise
        """
        target_target_estimator = self.pick_data(constants.AGENT_DATA_TO_PROCESS)

        # reconstruct the Target_TargetEstimator by flitering the targets
        new_target_targetEstimator = Target_TargetEstimator()
        for (target_id, targetEstimator_list) in target_target_estimator.item_itemEstimator_list:
            if target_id in [target.id for target in targets]:
                new_target_targetEstimator.add_itemEstimator(targetEstimator_list[-1])

        # find a configuration for these targets
        tracked_targets_room_representation = room.RoomRepresentation()
        tracked_targets_room_representation.update_target_based_on_memory(new_target_targetEstimator)

        x_target, y_target, alpha_target, beta_target = \
            get_configuration_based_on_seen_target(self.camera, tracked_targets_room_representation.active_Target_list,0.8,
                                                   PCA_track_points_possibilites.MEANS_POINTS,
                                                   self.memory_of_objectives, self.memory_of_position_to_reach, True)

        # check if this configuration covers all targets
        new_camera = copy.deepcopy(self.camera)
        new_camera.set_x_y_alpha_beta(x_target, y_target, alpha_target, beta_target, True)

        for targetRepresentation in tracked_targets_room_representation.active_Target_list:

            in_field = cam.is_x_y_radius_in_field_not_obstructed(new_camera, targetRepresentation.xc,
                                                                 targetRepresentation.yc,
                                                                 targetRepresentation.radius)

            hidden = cam.is_x_y_in_hidden_zone_all_targets_based_on_camera(tracked_targets_room_representation,
                                                                           new_camera,
                                                                           targetRepresentation.xc,
                                                                           targetRepresentation.yc)

            if hidden or not in_field:
                return None

        x_target, y_target, alpha_target, beta_target = get_configuration_based_on_seen_target(self.camera,
                                                                                               tracked_targets_room_representation.active_Target_list,0.8,
                                                                                               PCA_track_points_possibilites.MEANS_POINTS,
                                                                                               self.memory_of_objectives,
                                                                                               self.memory_of_position_to_reach,
                                                                                               False)

        configuration = Configuration(x_target, y_target, alpha_target, beta_target)
        print("in agent: ", alpha_target)
        return configuration

    def process_information_in_memory(self):
        """
            :description
                Process all the information obtain
        """

        "Combination of data received and data observed"
        self.memory.combine_data_agentCam()

        "Modification from the room description"
        self.room_representation.update_target_based_on_memory(self.pick_data(constants.AGENT_DATA_TO_PROCESS))
        self.room_representation.update_agent_based_on_memory(self.memory.memory_agent_from_agent)

        "Computation of the camera that should give the best view, according to maps algorithm"
        self.link_target_agent.update_link_camera_target()
        self.link_target_agent.compute_link_camera_target()

        """
            ----------------------------------------------------------------------------------------------
            Data to send other cam's agent, regarding this agent state
            -----------------------------------------------------------------------------------------------
        """
        self.send_message_timed_agentEstimator()

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
                (is_moving, is_stopped) = detect_target_motion(self.memory.memory_best_estimations_from_target,
                                                               target.id, 1, 5,
                                                               constants.STD_MEASURMENT_ERROR_POSITION + 0.01)
                "Check if the target is leaving the cam angle_of_view"
                (is_in, is_out) = is_target_leaving_cam_field(self.memory.memory_best_estimations_from_target,
                                                              self.camera, target.id, 0, 3)

                old_target_type = target.type
                if is_moving:
                    target.type = TargetType.MOVING
                elif is_stopped:
                    target.type = TargetType.FIX
                else:
                    target.type = TargetType.UNKNOWN

                if not old_target_type == target.type:
                    is_target_changing_state = True
                    self.log_main.debug(
                        "At %.02f Target %d change state from " % (constants.get_time(), target.id) + str(
                            old_target_type) + " to " + str(target.type))

            """
                ----------------------------------------------------------------------------------------------
                Data to send other cam's agent:
                -----------------------------------------------------------------------------------------------
            """
            "Send message to other agent"
            if constants.DATA_TO_SEND == AgentCameraCommunicationBehaviour.ALL:
                self.send_message_timed_targetEstimator(target.id)

            elif constants.DATA_TO_SEND == AgentCameraCommunicationBehaviour.DKF:
                self.send_message_DKF_info(target.id)

            elif constants.DATA_TO_SEND == AgentCameraCommunicationBehaviour.NONE:
                pass
            else:
                print("Wrong configuration found")

            """
               ----------------------------------------------------------------------------------------------
               Data to send user's agent:
               -----------------------------------------------------------------------------------------------
            """
            "If the target is link to this agent then we send the message to the user"
            cdt_target_type_1 = not (target.type == TargetType.SET_FIX)
            cdt_target_type_2 = True  # not(target.type == TargetType.FIX) or is_target_changing_state #to decrease the number of messages sent
            cdt_agent_is_in_charge = self.link_target_agent.is_in_charge(target.id, self.id)

            if cdt_agent_is_in_charge and cdt_target_type_1 and cdt_target_type_2:
                receivers = []
                for agent in self.room_representation.agentUser_representation_list:
                    receivers.append([agent.id, agent.signature])

                self.send_message_timed_targetEstimator(target.id, receivers)

    def process_single_message(self, rec_mes):
        super().process_single_message(rec_mes)
        if rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.INFO_DKF:
            self.receive_message_DKF_info(rec_mes)
        elif rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.AGENT_ESTIMATOR:
            self.received_message_agentEstimator(rec_mes)

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

        dkf_info_string = self.memory.get_DKF_info_string(target_id)
        # message containing the DKF information to send
        message = MessageCheckACKNACK(constants.get_time(), self.id, self.signature,
                                      MessageTypeAgentCameraInteractingWithRoom.INFO_DKF, dkf_info_string, target_id)

        # send the message to every other agent
        [message.add_receiver(agent.id, agent.signature) for agent in
         self.room_representation.agentCams_representation_list
         if not agent.id == self.id]

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
        concerned_target_id = int(message.item_ref)
        if info_string:  # if message not empty
            self.memory.process_DKF_info(concerned_target_id, info_string, constants.get_time())

    def send_message_agentEstimator(self, agentEstimator, receivers=None):
        """
                  :description
                      1. Create a message based on a TargetEstimator
                      2. Place it in the list message_to_send

                  :param
                      1. (TargetEstimator) targetEstimator -- TargetEstimator, see the class
                      2. (list) receivers                  -- [[receiver_id,receiver_signature], ... ], data to
                                                              tell to whom to send the message.

              """
        if receivers is None:
            receivers = []

        s = agentEstimator.to_string()
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        m = MessageCheckACKNACK(constants.get_time(), self.id, self.signature,
                                MessageTypeAgentCameraInteractingWithRoom.AGENT_ESTIMATOR, s,
                                agentEstimator.item_id)
        if len(receivers) == 0:
            for agent in self.room_representation.agentCams_representation_list:
                if agent.id != self.id:
                    m.add_receiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.add_receiver(receiver[0], receiver[1])

        cdt1 = self.info_message_to_send.is_message_with_same_message(m)
        if not cdt1:
            self.info_message_to_send.add_message(m)

    def received_message_agentEstimator(self, message):
        """
            :description
                1. Create a new TargetEstimator from the string description received
                2. Add the new TargetEstimator in the memory

            :param
                1. (Message) message  -- Message received

        """
        s = message.message
        if not (s == ""):
            estimator = AgentEstimator()
            estimator.parse_string(s)
            self.memory.add_agent_estimator(estimator)

            # self.send_message_ack_nack(message, "ack")

    def send_message_timed_agentEstimator(self):

        delta_time = constants.get_time() - self.time_last_message_agentEstimtor_sent
        if delta_time > constants.TIME_BTW_AGENT_ESTIMATOR:
            agent_estimator_list = self.memory.memory_agent_from_agent.get_item_list(self.id)

            if len(agent_estimator_list) > 0:
                last_agent_estimator = agent_estimator_list[-1]
                self.send_message_agentEstimator(last_agent_estimator)
                self.time_last_message_agentEstimtor_sent = constants.get_time()

    def remove_target_with_lowest_priority(self, target_list):
        """
        :description:
            Removes the target furthests to the agent from target_list
        :param target_list: list of targets (not ids)
        :return: target_list minus the target with the lowest priority
        """
        max_distance = -1
        target_to_remove = None
        for target in target_list:
            target_distance = cam.distance_btw_two_point(self.camera.xc, self.camera.yc, target.xc, target.yc)
            if target_distance > max_distance:
                max_distance = target_distance
                target_to_remove = target

        target_list.remove(target_to_remove)
        return target_list

