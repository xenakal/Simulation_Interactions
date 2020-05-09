import copy
from warnings import warn

import src.multi_agent.elements.room as room
from src.multi_agent.agent.agent_interacting_room import *
from src.multi_agent.communication.message import *
from src.multi_agent.behaviour.behaviour_agent import PCA_track_points_possibilites, \
    get_configuration_based_on_seen_target
from src.multi_agent.behaviour.behaviour_detection import *
from src.multi_agent.tools.configuration import check_configuration_all_target_are_seen
from src.multi_agent.tools.link_target_camera import *
from src.multi_agent.tools.controller import CameraController
from src import constants
from src.constants import AgentCameraCommunicationBehaviour
import time
import src.multi_agent.elements.mobile_camera as mobCam
import src.multi_agent.elements.camera as cam
from src.multi_agent.tools.potential_field_method import compute_potential_field_cam, plot_potential_field


class MessageTypeAgentCameraInteractingWithRoom(MessageTypeAgentInteractingWithRoom):
    INFO_DKF = "info_DKF"
    TRACKING_TARGET = "tracking_target"
    LOSING_TARGET = "loosing_target"


class AgentCameraFSM:
    MOVE_CAMERA = "Move camera"
    TAKE_PICTURE = "Take picture"
    PROCESS_DATA = "Process Data"
    COMMUNICATION = "Communication"
    BUG = "Bug"


class InternalPriority:
    NOT_TRACKED = 2
    TRACKED = 5


class AgentCamRepresentation(AgentInteractingWithRoomRepresentation):
    def __init__(self, id=None):
        super().__init__(id, AgentType.AGENT_CAM)
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

        self.log_execution = create_logger(constants.ResultsPath.LOG_AGENT, "Execution time", self.id)
        self.log_target_tracked = create_logger(constants.ResultsPath.LOG_AGENT, "Number of time a target is tracked",
                                                self.id)
        AgentCam.number_agentCam_created += 1

        # targets to be tracked by this agent
        self.targets_to_track = []
        # count how many times a target is tracked
        self.table_all_target_number_times_seen = AllTargetNUmberTimesSeen(self.id, self.log_target_tracked)

        # dictionnary to hold the internal priority of the targets (different from the target priority in
        # TargetEstimator). # This priority is used to modelize the fact that a target already tracked should be
        # prioritized compared to a target that just came into the field of vision.
        self.priority_dict = {}

        self.init_no_target_behaviour = False
        self.last_time_no_target_behaviour_init = constants.get_time()

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

            if state == AgentCameraFSM.TAKE_PICTURE:
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
                        if constants.INCLUDE_ERROR and not target.target_type == TargetType.SET_FIX:
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
                        target_representation = TargetRepresentation(target.id, target.xc + erreurPX, target.yc + erreurPY,
                                                                target.vx + erreurVX, target.vy + erreurVY,
                                                                target.ax + erreurAX, target.ay + erreurAY,
                                                                target.radius, target_type,target.color)

                        self.memory.add_create_target_estimator(constants.get_time(), self.id,
                                                                self.signature, target_representation)


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
                    if constants.AGENTS_MOVING:
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

            elif state == AgentCameraFSM.MOVE_CAMERA:
                if last_time_move is not None:

                    # find a configuration for the agent
                    # config = self.find_configuration_for_tracked_targets()
                    config = self.configuration_algorithm_choice(constants.AGENT_CHOICE_HOW_TO_FOLLOW_TARGET)

                    # move agent according to configuration found
                    last_time_move = self.move_based_on_config(config, last_time_move)

                else:
                    last_time_move = constants.get_time()

                """Create a new memory to save the """
                agent_representation = AgentCamRepresentation(self.id)
                agent_representation.update_from_agent(self)
                self.memory.add_create_agent_estimator_from_agent(constants.get_time(), self, agent_representation)
                if not self.camera.is_active or not self.is_active:
                    nextstate = AgentCameraFSM.BUG
                else:
                    nextstate = AgentCameraFSM.TAKE_PICTURE

            elif state == AgentCameraFSM.BUG:
                time.sleep(3)
                print("bug")
                if not self.camera.is_active or not self.is_active:
                    nextstate = AgentCameraFSM.BUG
                else:
                    nextstate = AgentCameraFSM.TAKE_PICTURE

            else:
                print("FSM not working proerly")
                self.log_execution.warning("FSM not working as expected")

        self.log_execution.info("Execution mean time : %.02f s", execution_mean_time / execution_loop_number)

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

        if len(self.memory.memory_agent_from_agent.get_item_list(self.id)) > 0:
            last_camera_estimation = self.memory.memory_agent_from_agent.get_item_list(self.id)[-1]
            #self.send_message_timed_itemEstimator(last_camera_estimation, constants.TIME_BTW_AGENT_ESTIMATOR)

        # self.log_target_tracked.info(self.table_all_target_number_times_seen.to_string(self.id))

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
            if not target.target_type == TargetType.SET_FIX:
                "Check if the target is moving,stopped or changing from one to the other state"
                (is_moving, is_stopped) = detect_target_motion(self.pick_data(constants.AGENT_DATA_TO_PROCESS),
                                                               target.id, 1, 5,
                                                               constants.POSITION_STD_ERROR,
                                                               constants.SPEED_MEAN_ERROR)

                "Check if the target is leaving the cam angle_of_view"
                (is_in, is_out) = is_target_leaving_cam_field(self.memory.memory_predictions_order_2_from_target,
                                                              self.camera, target.id, 0, 3)

                old_target_type = target.target_type
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
            if target.confidence[0] < constants.CONFIDENCE_THRESHOLD < target.confidence[1]:
                self.table_all_target_number_times_seen.update_tracked(target.id)
                self.send_message_track_loose_target(MessageTypeAgentCameraInteractingWithRoom.TRACKING_TARGET,
                                                     target.id)

            elif target.confidence[0] > constants.CONFIDENCE_THRESHOLD > target.confidence[1]:
                self.table_all_target_number_times_seen.update_lost(target.id)
                self.send_message_track_loose_target(MessageTypeAgentCameraInteractingWithRoom.LOSING_TARGET, target.id)


            if constants.DATA_TO_SEND == AgentCameraCommunicationBehaviour.DKF:
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
            """If the target is link to this agent then we send the message to the user"""
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

            """
                ----------------------------------------------------------------------------------------------
                update of target to tracklist:
                -----------------------------------------------------------------------------------------------
            """

            # start tracking targets that came into field of vision
            if target.id not in self.targets_to_track and target.confidence[1] > constants.CONFIDENCE_THRESHOLD:
                self.targets_to_track.append(target.id)
                self.priority_dict[target.id] = InternalPriority.NOT_TRACKED

            if target.id in self.targets_to_track and target.confidence[1] < constants.CONFIDENCE_THRESHOLD:
                self.targets_to_track.remove(target.id)
                self.priority_dict[target.id] = None

        """
           ----------------------------------------------------------------------------------------------
           Check if to cameras are to close:
           -----------------------------------------------------------------------------------------------
        """
        if constants.get_time() - self.last_time_no_target_behaviour_init > constants.TIME_STOP_INIT_BEHAVIOUR:
            self.init_no_target_behaviour = False

        for agent in self.room_representation.agentCams_representation_list:
            if agent.id < self.id and math.fabs(
                    agent.camera_representation.xc - self.camera.xc) < constants.MIN_DISTANCE_AGENTS and \
                    math.fabs(agent.camera_representation.yc - self.camera.yc) < constants.MIN_DISTANCE_AGENTS and \
                    math.fabs(agent.camera_representation.alpha - self.camera.alpha) < constants.MIN_ANGLE_DIFF_AGENTS:
                self.init_no_target_behaviour = True
                self.last_time_no_target_behaviour_init = constants.get_time()

    def configuration_algorithm_choice(self, choix):
        target_list = self.get_active_targets()
        real_configuration, virtual_configuration = self.compute_real_virtual_configuration_and_set_virtual_cam(
            target_list)

        if choix == constants.ConfigurationWaysToBeFound.CONFIUGRATION_WIHTOUT_CHECK:
            return real_configuration

        elif choix == constants.ConfigurationWaysToBeFound.CONFIUGRATION_WITH_TARGET_CHECK:
            if check_configuration_all_target_are_seen(camera=self.virtual_camera,
                                                       room_representation=self.room_representation):
                return real_configuration

        elif choix == constants.ConfigurationWaysToBeFound.CONFIUGRATION_WITH_SCORE_CHECK:
            if virtual_configuration.configuration_score >= constants.MIN_CONFIGURATION_SCORE:
                return real_configuration

        elif choix == constants.ConfigurationWaysToBeFound.MOVE_ONLY_IF_CONFIGURATION_IS_VALID:
            if virtual_configuration.is_configuration_valid(camera=self.virtual_camera,
                                                            room_representation=self.room_representation,
                                                            score_map_min=constants.MIN_CONFIGURATION_SCORE):
                return real_configuration

        elif choix == constants.ConfigurationWaysToBeFound.TRY_TO_FIND_VALID_CONFIG:
            return self.find_configuration_for_tracked_targets()

        return None

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
            x_command = x_controller.born_command(configuration.vector_field_x)
            y_command = y_controller.born_command(configuration.vector_field_y)
        else:
            print("error in move target, controller type not found")

        """Apply the command"""
        if constants.get_time() - last_time_move < 0:
            print("problem time < 0 : %.02f s" % constants.get_time())
            return last_time_move
        else:
            dt = constants.get_time() - last_time_move
            if dt > 0.2:
                # If the dt is to large, the controller can not handle it anymore, the solution is to decompose dt in
                # smaller values
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

        configuration = None
        while configuration is None or not configuration.is_valid:

            configuration = self.find_configuration_for_targets(tracked_targets)
            if configuration is None or not configuration.is_valid:
                self.remove_target_with_lowest_priority(tracked_targets, configuration)

        for target in self.targets_to_track:
            if target not in tracked_targets:
                # broadcast lost target
                self.priority_dict[target] = None

        for target in self.targets_to_track:
            self.priority_dict[target] = InternalPriority.TRACKED

        return configuration

    def find_configuration_for_targets(self, targets, used_for_movement=True):
        """
            :description:
                Checks if a configuration can be found where all targets are seen.
            :param targets: target representations
            :param used_for_movement: if False, don't do the last non-virtual "get_configuration"
            :return: Configuration object if exists, None otherwise
        """
        tracked_targets_room_representation = self.construct_room_representation_for_a_given_target_list(targets)
        virtual_configuration = \
            self.compute_virtual_configuration(tracked_targets_room_representation.active_Target_list)

        better_config_found = False
        self.virtual_camera = copy.deepcopy(self.camera)
        self.virtual_camera.set_configuration(virtual_configuration)

        if not check_configuration_all_target_are_seen(self.virtual_camera, tracked_targets_room_representation):
            self.log_main.debug(
                "Configuration not found at time %.02f, starting variation on this config" % constants.get_time())
            virtual_configuration.is_valid = False
            return virtual_configuration

        # configuration found, but bad score
        if virtual_configuration.configuration_score < constants.MIN_CONFIGURATION_SCORE:
            # Check around if there is a better config
            optimal_configuration = virtual_configuration.variation_on_configuration_found(self.virtual_camera)

            self.virtual_camera.set_configuration(optimal_configuration)
            if check_configuration_all_target_are_seen(self.virtual_camera, tracked_targets_room_representation):
                better_config_found = True

        # if the agent actually wants to move
        if used_for_movement:
            real_configuration = \
                get_configuration_based_on_seen_target(self.camera,
                                                       tracked_targets_room_representation.active_Target_list,
                                                       self.room_representation,
                                                       PCA_track_points_possibilites.MEANS_POINTS,
                                                       self.memory_of_objectives, self.memory_of_position_to_reach,
                                                       False)

            if better_config_found:
                real_configuration.x = optimal_configuration.x
                real_configuration.y = optimal_configuration.y
                real_configuration.is_valid = True
            return real_configuration

        # if the agent doesn't want to move
        if better_config_found:
            better_config = virtual_configuration.variation_on_configuration_found(self.virtual_camera)
            better_config.is_valid = True
            return better_config
        else:
            virtual_configuration.is_valid = True
            return virtual_configuration

    def remove_target_with_lowest_priority(self, target_list, configuration):
        """
        :description:
            Removes the target with the lowest total priority from target_list
        :param
            target_list: list of targets (not ids)
            configuration: configuration attempt for the targets in target_list
        :return: target_list minus the target with the lowest priority
        """
        if not target_list:
            return

        min_total_priority = 100000
        target_to_remove = -1
        for target_id in target_list:
            config_target_score = 0
            if configuration is not None:
                config_target_score = configuration.compute_target_score(target_id)
            target = self.room_representation.get_Target_with_id(target_id)
            target_total_priority = constants.USER_SET_PRIORITY_WEIGHT * target.priority_level + \
                                    constants.CAMERA_SET_PRIORITY_WEIGHT * self.priority_dict[target.id] + \
                                    constants.SCORE_WEIGHT * config_target_score

            if target_total_priority < min_total_priority:
                min_total_priority = target_total_priority
                target_to_remove = target.id

        target_list.remove(target_to_remove)

    def get_active_targets(self):
        return [target for target in self.room_representation.active_Target_list if
                target.confidence[1] >= constants.CONFIDENCE_THRESHOLD]

    def get_predictions(self, target_id_list):
        """
        :return: a list [[targetId, [predicted_position1, ...]], ...]
        """
        return self.memory.get_predictions(target_id_list)

    def compute_virtual_configuration(self, targets):
        virtual_configuration = \
            get_configuration_based_on_seen_target(self.camera, targets, self.room_representation,
                                                   PCA_track_points_possibilites.MEANS_POINTS,
                                                   self.memory_of_objectives, self.memory_of_position_to_reach,
                                                   True, self.init_no_target_behaviour)

        virtual_configuration.compute_configuration_score()
        return virtual_configuration

    def compute_real_virtual_configuration_and_set_virtual_cam(self, target_list):
        virtual_configuration = self.compute_virtual_configuration(target_list)
        self.virtual_camera = copy.deepcopy(self.camera)
        self.virtual_camera.set_configuration(virtual_configuration)

        real_configuration = virtual_configuration = \
            get_configuration_based_on_seen_target(self.camera, target_list, self.room_representation,
                                                   PCA_track_points_possibilites.MEANS_POINTS,
                                                   self.memory_of_objectives, self.memory_of_position_to_reach,
                                                   False, self.init_no_target_behaviour)

        return real_configuration, virtual_configuration

    def construct_room_representation_for_a_given_target_list(self, targets):
        target_target_estimator = self.pick_data(constants.AGENT_DATA_TO_PROCESS)

        # reconstruct the Target_TargetEstimator by flitering the targets
        new_target_targetEstimation = SingleOwnerMemories(self.id)
        for itemEstimationsList in target_target_estimator.items_estimations_lists:
            if itemEstimationsList.item_id in targets:
                new_target_targetEstimation.add_itemEstimationsList(itemEstimationsList)

        # find a configuration for these targets
        tracked_targets_room_representation = room.RoomRepresentation()
        tracked_targets_room_representation.update_target_based_on_memory(new_target_targetEstimation)
        return tracked_targets_room_representation

    def process_single_message(self, rec_mes):
        super().process_single_message(rec_mes)
        if rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.INFO_DKF:
            self.receive_message_DKF_info(rec_mes)
            self.info_message_received.del_message(rec_mes)
        elif rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.TRACKING_TARGET \
                or rec_mes.messageType == MessageTypeAgentCameraInteractingWithRoom.LOSING_TARGET:
            #self.receive_message_track_loose_target(rec_mes)
            self.info_message_received.del_message(rec_mes)

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
        self.broadcast_message(message, BroadcastTypes.AGENT_CAM)

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

    def send_message_track_loose_target(self, track_loose_choice, target_id):

        if track_loose_choice == MessageTypeAgentCameraInteractingWithRoom.TRACKING_TARGET or track_loose_choice == MessageTypeAgentCameraInteractingWithRoom.LOSING_TARGET:
            message = MessageCheckACKNACK(constants.get_time(), self.id, self.signature, track_loose_choice, "",
                                          target_id)
            self.log_target_tracked.info(message.to_string())
            self.broadcast_message(message, BroadcastTypes.AGENT_CAM)

    def receive_message_track_loose_target(self, message):
        self.log_target_tracked.info(message.to_string())
        if message.messageType == MessageTypeAgentCameraInteractingWithRoom.TRACKING_TARGET:
            self.table_all_target_number_times_seen.update_tracked(int(message.item_ref))
        elif message.messageType == MessageTypeAgentCameraInteractingWithRoom.LOSING_TARGET:
            self.table_all_target_number_times_seen.update_lost(int(message.item_ref))


class AllTargetNUmberTimesSeen:
    def __init__(self, agent_id, log):
        self.id = agent_id
        self.log_target_tracked = log
        self.tracker_list = []

    def update_tracked(self, target_id):
        new_tracker = TargetNumberTimesSeen(target_id)
        if new_tracker in self.tracker_list:
            old_tracker_index = self.tracker_list.index(new_tracker)
            old_tracker = self.tracker_list[old_tracker_index]
            old_tracker.update_tracked()
        else:
            new_tracker.update_tracked()
            self.tracker_list.append(new_tracker)

        self.log_target_tracked.info(self.to_string(self.id))

    def update_lost(self, target_id):
        new_tracker = TargetNumberTimesSeen(target_id)
        if new_tracker in self.tracker_list:
            old_tracker_index = self.tracker_list.index(new_tracker)
            old_tracker = self.tracker_list[old_tracker_index]
            old_tracker.update_lost()
        else:
            print("should not append")
            self.tracker_list.append(new_tracker)

        self.log_target_tracked.info(self.to_string(self.id))

    def to_string(self, agent_id):
        s = "agent %d time %.02f \n" % (agent_id, constants.get_time())
        for tracker in self.tracker_list:
            s += tracker.to_string()
        return s


class TargetNumberTimesSeen:
    def __init__(self, target_id):
        self.target_id = target_id
        self.n = 0

    def update_tracked(self):
        self.n += 1

    def update_lost(self):
        self.n -= 1
        if self.n < 0:
            print("error target seen -%d tiems" % self.n)

    def to_string(self):
        return "target %d is seen %d \n" % (self.target_id, self.n)

    def __eq__(self, other):
        return self.target_id == other.target_id
