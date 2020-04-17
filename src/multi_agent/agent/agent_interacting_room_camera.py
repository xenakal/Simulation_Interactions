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
from src.my_utils.my_math.potential_field_method import compute_potential_gradient, \
    convert_target_list_to_potential_field_input
from src import constants
from src.constants import AgentCameraCommunicationBehaviour
import time
import src.multi_agent.elements.mobile_camera as mobCam
import src.multi_agent.elements.camera as cam


class MessageTypeAgentCameraInteractingWithRoom(MessageTypeAgentInteractingWithRoom):
    INFO_DKF = "info_DKF"
    UNTRACKABLE_TARGET = "untrackable"
    ACK_UNTRACKABLE_TARGET = "ack_untrackable"


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

    def to_string(self):
        print("config x: %.02f y: %.02f alpha: %.02f beta: %.02f" % (self.x, self.y, self.alpha, self.beta))


class InternalPriority:
    NOT_TRACKED = 2
    TRACKED = 5


CONFIDENCE_THRESHOLD = 50


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
        self.virtual_camera = None
        super().__init__(AgentCam.number_agentCam_created, AgentType.AGENT_CAM, t_add, t_del, camera.color)
        self.camera_controller = None
        self.link_target_agent = None
        self.memory_of_objectives = []
        self.memory_of_position_to_reach = []

        self.time_last_message_agentEstimtor_sent = constants.get_time()
        self.table_agent_agent_lastTimeSent = AllItemSendToAtTime()

        self.log_execution = create_logger(constants.ResultsPath.LOG_AGENT, "Execution time", self.id)
        AgentCam.number_agentCam_created += 1

        # targets to be tracked by this agent
        self.targets_to_track = []
        self.initialized_targets_to_track = False
        # targets in self.targets_to_track for which a configuration wasn't found
        self.untrackable_targets = []

        # dictionnary to hold the internal priority of the targets (different from the target priority in
        # TargetEstimator). # This priority is used to modelize the fact that a target already tracked should be
        # prioritized compared to a target that just came into the field of vision.
        self.priority_dict = {}

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
        self.camera_controller = CameraController(constants.AGENT_POS_KP, constants.AGENT_POS_KI,
                                                  constants.AGENT_ALPHA_KP, constants.AGENT_ALPHA_KI,
                                                  constants.AGENT_BETA_KP, constants.AGENT_BETA_KI)
        self.camera_controller.set_targets(self.camera.xc, self.camera.yc, self.camera.alpha, self.camera.beta)

        self.log_main.info("initialisation in agent_interacting_room__cam_done !")

    def init_targets_to_track(self, room):
        if constants.INIT_TARGET_LIST == constants.AgentCameraInitializeTargetList.ALL_SEEN:
            """ Initializes the targets to track as all targets seen by the agent at the time of initialization. """
            # initialize targets to track
            for target in self.room_representation.active_Target_list:
                self.targets_to_track.append(target.id)
                self.priority_dict[target.id] = InternalPriority.TRACKED
        elif constants.INIT_TARGET_LIST == constants.AgentCameraInitializeTargetList.ALL_IN_ROOM:
            # initialize targets to track
            self.targets_to_track = copy.copy(room.information_simulation.active_Target_list)
        else:
            warn("Invalid method for initializing targets to tracks, no target_list to be used.")

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

                # Assumption: at the beggining of the simulation, each target is seen by at least one camera. This could
                #             be done by putting cameras at the entry/exit point of the room. If some target is lost in
                #             the process (nobody able to track it), then it will be in the list of untracked targets.

                if last_time_move is not None:

                    # find a configuration for the agent
                    config = self.find_configuration_for_tracked_targets()
                    if config is not None:
                        last_not_None_configuration = config

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

                        # add the new information to the memory
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
                    self.init_targets_to_track(real_room)
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

    def move_based_on_config(self, configuration, last_time_move):

        if configuration is None:
            self.log_main.debug("no config to move at time %.02f" % constants.get_time())
            return constants.get_time()

        """Computing the vector field"""
        configuration.compute_vector_field_for_current_position(self.camera.xc, self.camera.yc)

        """Setting values to the PI controller"""
        self.camera_controller.set_targets(configuration.x, configuration.y, configuration.alpha, configuration.beta)

        """Define the values measured"""
        x_mes = self.camera.xc  # + error si on veut ajouter ici
        y_mes = self.camera.yc

        alpha_mes = self.camera_controller.alpha_controller.bound_alpha_btw_minus_pi_plus_pi(self.camera.alpha)
        beta_mes = self.camera.beta

        if self.camera.camera_type == mobCam.MobileCameraType.RAIL:
            "1 D"
            x_mes = self.camera.trajectory.sum_delta
            y_mes = 0

        """Find the command to apply"""
        (x_command, y_command, alpha_command, beta_command) = self.camera_controller.get_command(x_mes, y_mes,
                                                                                                 alpha_mes, beta_mes)

        if constants.AGENT_MOTION_CONTROLLER == constants.AgentCameraController.Controller_PI:
            "We keep it has computed above"
            pass
        elif constants.AGENT_MOTION_CONTROLLER == constants.AgentCameraController.Vector_Field_Method:
            "The position command is here adapted with the vector field"
            x_controller = self.camera_controller.position_controller.x_controller
            y_controller = self.camera_controller.position_controller.y_controller
            x_command = x_controller.born_command(configuration.vector_field_x * x_controller.kp)
            y_command = y_controller.born_command(configuration.vector_field_y * y_controller.kp)
        else:
            print("error in move target, controller type not found")

        # print("alpha_mes %.02f alpha_target %.02f command %.02f dt %.02f" % (
        # math.degrees(alpha_mes), math.degrees(configuration.alpha), alpha_command,constants.get_time() - last_time_move))

        """Apply the command"""
        if constants.get_time() - last_time_move < 0:
            print("problem time < 0 : %.02f s" % constants.get_time())
            return last_time_move
        else:
            dt = constants.get_time() - last_time_move
            if dt > 0.2:
                "If the dt is to large, the controller can not handle it anymore, the solution is to decompose dt in smaller values"
                self.camera.rotate(alpha_command, 0.2)
                self.camera.zoom(beta_command, 0.2)
                self.camera.move(x_command, y_command, 0.2)
                return self.move_based_on_config(configuration, last_time_move + 0.2)

            else:
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
        # self.targets_to_track = [target.id for target in self.room_representation.active_Target_list]
        # tracked_targets = copy.copy(self.room_representation.active_Target_list)
        # self.targets_to_track = self.room_representation.active_Target_list

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
                # update the list of untrackable targets
                self.untrackable_targets = self.targets_to_track.copy()
                # update the list of tracked targets
                self.targets_to_track = []
                # reset priority dict
                self.priority_dict = {}
                return None

            # remove the desired number of targets
            # TODO: maybe try different permutations as well ?
            for _ in range(number_targets_to_remove):
                self.remove_target_with_lowest_priority(tracked_targets)

            configuration = self.find_configuration_for_targets(tracked_targets)

        # update the list of untrackable targets
        self.untrackable_targets = [target for target in self.targets_to_track if target not in tracked_targets]
        self.targets_to_track = tracked_targets
        configuration.track_target_list = self.room_representation.get_multiple_target_with_id(tracked_targets)

        # update priority dict if some target was lost
        if self.untrackable_targets:
            self.priority_dict = {}
            for target_id in self.targets_to_track:
                self.priority_dict[target_id] = InternalPriority.TRACKED

        return configuration

    def find_configuration_for_targets(self, targets, used_for_movement=True):
        """
        :description:
            Checks if a configuration can be found where all targets are seen.
        :param targets: target representations
        :param used_for_movement: if False, don't do the last non-virtual "get_configuration"
        :return: Configuration object if exists, None otherwise
        """
        target_target_estimator = self.pick_data(constants.AGENT_DATA_TO_PROCESS)

        # reconstruct the Target_TargetEstimator by flitering the targets
        new_target_targetEstimator = Target_TargetEstimator()
        for (target_id, targetEstimator_list) in target_target_estimator.item_itemEstimator_list:
            if target_id in targets:
                new_target_targetEstimator.add_itemEstimator(targetEstimator_list[-1])

        # find a configuration for these targets
        tracked_targets_room_representation = room.RoomRepresentation()
        tracked_targets_room_representation.update_target_based_on_memory(new_target_targetEstimator)

        virtual_configuration = \
            get_configuration_based_on_seen_target(self.camera, tracked_targets_room_representation.active_Target_list,
                                                   PCA_track_points_possibilites.MEANS_POINTS,
                                                   self.memory_of_objectives, self.memory_of_position_to_reach, True)

        # check if this configuration covers all targets
        self.virtual_camera = copy.deepcopy(self.camera)
        self.virtual_camera.set_configuration(virtual_configuration)

        for targetRepresentation in tracked_targets_room_representation.active_Target_list:
            in_field = cam.is_x_y_radius_in_field_not_obstructed(self.virtual_camera, targetRepresentation.xc,
                                                                 targetRepresentation.yc,
                                                                 targetRepresentation.radius)

            hidden = cam.is_x_y_in_hidden_zone_all_targets_based_on_camera(tracked_targets_room_representation,
                                                                           self.virtual_camera,
                                                                           targetRepresentation.xc,
                                                                           targetRepresentation.yc)

            if hidden or not in_field:
                #print("pas de config lo")
                self.log_main.debug("no config at time %.02f" % constants.get_time())
                return None

        # if the agent actually wants to move
        if used_for_movement:
            real_configuration = \
                get_configuration_based_on_seen_target(self.camera,
                                                       tracked_targets_room_representation.active_Target_list,
                                                       PCA_track_points_possibilites.MEANS_POINTS,
                                                       self.memory_of_objectives, self.memory_of_position_to_reach,
                                                       False)
            return real_configuration

        # if the agent doesn't want to move
        return virtual_configuration

    def process_information_in_memory(self):
        """
            :description
                Process all the information obtained
        """

        '''Combination of data received and data observed'''
        self.memory.combine_data_agentCam()

        '''Modification from the room description'''
        self.room_representation.update_target_based_on_memory(self.pick_data(constants.AGENT_DATA_TO_PROCESS))
        self.room_representation.update_agent_based_on_memory(self.memory.memory_agent_from_agent)

        '''Computation of the camera that should give the best view, according to maps algorithm'''
        self.link_target_agent.update_link_camera_target()
        self.link_target_agent.compute_link_camera_target()

        """
            ----------------------------------------------------------------------------------------------
            Data to send other cam's agent, regarding this agent state
            -----------------------------------------------------------------------------------------------
        """
        last_camera_estimation = self.memory.memory_agent_from_agent.get_item_list(self.id)[-1]
        self.send_message_timed_itemEstimator(last_camera_estimation,constants.TIME_BTW_AGENT_ESTIMATOR)

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
                (is_moving, is_stopped) = detect_target_motion(self.pick_data(constants.AGENT_DATA_TO_PROCESS),
                                                               target.id, 1, 5,
                                                               constants.POSITION_STD_ERROR,
                                                               constants.SPEED_MEAN_ERROR)

                "Check if the target is leaving the cam angle_of_view"
                (is_in, is_out) = is_target_leaving_cam_field(self.memory.memory_predictions_order_2_from_target,
                                                              self.camera, target.id, 0, 3)

                if is_in and is_out:
                    pass
                    # print("target id: %d possible obstruction !"%target.id)

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
                target_estimator_to_send = self.pick_data(constants.AGENT_DATA_TO_PROCESS)
                if len(target_estimator_to_send.get_item_list(target.id)) > 0:
                    self.send_message_timed_itemEstimator(target_estimator_to_send.get_item_list(target.id)[-1],
                                                          constants.TIME_BTW_TARGET_ESTIMATOR)

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

                target_estimator_to_send = self.pick_data(constants.AGENT_DATA_TO_PROCESS)
                if len(target_estimator_to_send.get_item_list(target.id)) > 0:
                    self.send_message_timed_itemEstimator(target_estimator_to_send.get_item_list(target.id)[-1],
                                                              constants.TIME_BTW_TARGET_ESTIMATOR, receivers)

            # start tracking the target according to the priority levels
            if target.id not in self.targets_to_track and target.confidence_pos > CONFIDENCE_THRESHOLD:
                print("agent ", self.id, " sees: ", target.id)
                self.targets_to_track.append(target.id)
                self.priority_dict[target.id] = InternalPriority.NOT_TRACKED

    def process_single_message(self, rec_mes):
        super().process_single_message(rec_mes)
        if rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.INFO_DKF:
            self.receive_message_DKF_info(rec_mes)
            self.info_message_received.del_message(rec_mes)
        elif rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.UNTRACKABLE_TARGET:
            self.receive_message_untrackableTarget(rec_mes)
            self.info_message_received.del_message(rec_mes)
        elif rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.ACK_UNTRACKABLE_TARGET:
            self.receive_message_ack_untrackableTarget(rec_mes)
            self.info_message_received.del_message(rec_mes)

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
        self.broadcast_message(message)

        # add message to the list if not already inside
        cdt = self.info_message_to_send.is_message_with_same_message(message)
        if not cdt:
            self.info_message_to_send.add_message(message)

    def broadcast_untracked_targets(self):
        """
        :description
            Broadcast a message to notify other agents that a certain target can't be tracked by this agent anymore.
        """
        # inform the other agent of all targets this agent is not able to track
        for target_id in self.untrackable_targets:
            message = self.message_from_untrackable_target(target_id)

            # broadcast message
            self.broadcast_message(message)
            # remove target from targets to track (as this agent can't..)
            self.targets_to_track.remove(target_id)

        # empty the untrackable_targets list
        self.untrackable_targets = []

    def message_from_untrackable_target(self, target_id):
        message = Message(constants.get_time(), self.id, self.signature,
                          MessageTypeAgentCameraInteractingWithRoom.UNTRACKABLE_TARGET, "", target_id)
        return message

    def message_from_acked_target(self, target_id):
        message = Message(constants.get_time(), self.id, self.signature,
                          MessageTypeAgentCameraInteractingWithRoom.ACK_UNTRACKABLE_TARGET, "", target_id)
        return message

    def broadcast_message(self, message):
        """
        :description:
            Broadcasts the message to every other known agent.
        :param message: message of type MessageCheckACKNACK()
        """
        [message.add_receiver(agent.id, agent.signature) for agent in
         self.room_representation.agentCams_representation_list if not agent.id == self.id]
        for agent in self.room_representation.agentCams_representation_list:
            if not agent.id == self.id:
                message.add_receiver(agent.id, agent.signature)

            cdt1 = self.info_message_to_send.is_message_with_same_message(message)
            if not cdt1:
                self.info_message_to_send.add_message(message)

    def receive_message_untrackableTarget(self, message):
        """
        :description
            Checks if the target concerned can be covered by this agent. If so, sends an ACK to all other agents in the
            next loop.
        :param message: of type UNTRACKABLE_TARGET
        """
        # target the message is refering to
        target_id = int(message.item_ref)
        target_representation = self.room_representation.get_Target_with_id(target_id)

        # if the agent doesn't see the target, don't send an ACK
        if target_representation is None:
            return

        # check if the agent can position himself to track this target as well
        total_items_to_track = self.targets_to_track.copy()
        total_items_to_track.append(target_id)
        configuration = self.find_configuration_for_targets(total_items_to_track, False)
        # the agent can track the target: start tracking it and broadcast an ACK
        if configuration is not None:
            if target_id not in self.targets_to_track:
                self.targets_to_track.append(target_id)
            ack_message = self.message_from_acked_target(target_id)
            self.broadcast_message(ack_message)
        # the agent can't track the target

    def receive_message_ack_untrackableTarget(self, message):
        target_id = int(message.item_ref)
        pass

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

    def remove_target_with_lowest_priority(self, target_list):
        """
        :description:
            Removes the target with the lowest total priority from target_list
        :param target_list: list of targets (not ids)
        :return: target_list minus the target with the lowest priority
        """
        print("agent dic: ", self.priority_dict)
        min_total_priority = 100000
        target_to_remove = -1
        for target_id in target_list:
            target = self.room_representation.get_Target_with_id(target_id)
            target_total_priority = target.priority_level + self.priority_dict[target.id]
            if target_total_priority < min_total_priority:
                min_total_priority = target_total_priority
                target_to_remove = target.id

        target_list.remove(target_to_remove)

