import re
import numpy as np
import random

from src.multi_agent.agent.agent_interacting_room_camera_representation import AgentCamRepresentation
from src.multi_agent.agent.agent_interacting_room_user_representation import AgentUserRepresentation
from src.multi_agent.agent.agent_representation import AgentType
from src.multi_agent.elements.mobile_camera import MobileCamera, MobileCameraType
from src.multi_agent.elements.target import TargetType, TargetRepresentation, Target
import src.multi_agent.agent.agent_interacting_room_camera as aCam
import src.multi_agent.agent.agent_interacting_room_user as aUser
from src import constants


class InformationRoomSimulation:
    """
        Class Example.

        Description : Contains all the elements necessary to simulate the environment

            :attibutes
                1. (numpy.array) coordinate_room  -- numpy.array([0, 0, constants.LENGHT_ROOM, constants.WIDTH_ROOM])
                give the corner in the room (0,0),...
                2. (list) Target_list             -- [Target,...] all the target that should appear in the room
                3. (list) trajectories            -- [[(int,int),...],[(int,int),...],...] all the trajectories
                4. (list) trajectories_number     -- [int,int,...] all the references to the trajecotries

            :notes
                fells free to write some comments.
    """

    def __init__(self):
        """Initialisation"""

        "Room radius"
        self.coordinate_room = np.array([0, 0, constants.ROOM_DIMENSION_X, constants.ROOM_DIMENSION_Y])  # x y l h

        "Target with their time of apparition and disparition "
        self.target_list = []
        self.agentCams_list = []
        self.agentUser_list = []

    def generate_n_m_unkown_set_fix_target(self, n, m):
        for n in range(n):
            target = Target()
            target.randomize(target_type=TargetType.UNKNOWN, r_bound=constants.RANDOM_TARGET_RADIUS_BOUND,
                             v_bound=constants.RANDOM_TARGET_V_BOUND,
                             trajectory_number_of_points=constants.TARGET_NUMBER_OF_POINTS_GENERATED_FOR_A_TRAJECTORY)
            self.add_Target(target)

        for m in range(m):
            target = Target()
            target.randomize(target_type=TargetType.SET_FIX, r_bound=constants.RANDOM_TARGET_RADIUS_BOUND,
                             v_bound=constants.RANDOM_TARGET_V_BOUND,
                             trajectory_number_of_points=constants.TARGET_NUMBER_OF_POINTS_GENERATED_FOR_A_TRAJECTORY)
            self.add_Target(target)

    def generate_n_m_p_k_fix_rotative_rail_free_camera(self, n, m, p, k):
        for n in range(n):
            camera = MobileCamera(id=-1, xc=0, yc=0, alpha=0, beta=0, trajectory=[], field_depth=0)
            camera.randomize(camera_type=MobileCameraType.FIX, beta_bound=constants.RANDOM_CAMERA_BETA_BOUND,
                             delta_beta_bound=constants.RANDOM_CAMERA_DELTA_BETA_BOUND,
                             field_bound=constants.RANDOM_CAMERA_FIELD_DEPTH_BOUND,
                             v_xy_min_bound=constants.RANDOM_CAMERA_V_XY_MIN_BOUND,
                             v_xy_max_bound=constants.RANDOM_CAMERA_V_XY_MAX_BOUND,
                             v_alpha_min_bound=constants.RANDOM_CAMERA_V_ALPHA_MIN_BOUND,
                             v_alpha_max_bound=constants.RANDOM_CAMERA_V_ALPHA_MAX_BOUND,
                             v_beta_min_bound=constants.RANDOM_CAMERA_V_BETA_MIN_BOUND,
                             v_beta_max_bound=constants.RANDOM_CAMERA_V_BETA_MAX_BOUND)

            agentCam = aCam.AgentCam(camera, -1, -1)
            agentCam.camera.id = agentCam.id
            self.agentCams_list.append(agentCam)

        for m in range(m):
            camera = MobileCamera(id=-1, xc=0, yc=0, alpha=0, beta=0, trajectory=[], field_depth=0)
            camera.randomize(camera_type=MobileCameraType.ROTATIVE, beta_bound=constants.RANDOM_CAMERA_BETA_BOUND,
                             delta_beta_bound=constants.RANDOM_CAMERA_DELTA_BETA_BOUND,
                             field_bound=constants.RANDOM_CAMERA_FIELD_DEPTH_BOUND,
                             v_xy_min_bound=constants.RANDOM_CAMERA_V_XY_MIN_BOUND,
                             v_xy_max_bound=constants.RANDOM_CAMERA_V_XY_MAX_BOUND,
                             v_alpha_min_bound=constants.RANDOM_CAMERA_V_ALPHA_MIN_BOUND,
                             v_alpha_max_bound=constants.RANDOM_CAMERA_V_ALPHA_MAX_BOUND,
                             v_beta_min_bound=constants.RANDOM_CAMERA_V_BETA_MIN_BOUND,
                             v_beta_max_bound=constants.RANDOM_CAMERA_V_BETA_MAX_BOUND)

            agentCam = aCam.AgentCam(camera, -1, -1)
            agentCam.camera.id = agentCam.id
            self.agentCams_list.append(agentCam)

        for p in range(p):
            camera = MobileCamera(id=-1, xc=0, yc=0, alpha=0, beta=0, trajectory=[], field_depth=0)
            camera.randomize(camera_type=MobileCameraType.RAIL, beta_bound=constants.RANDOM_CAMERA_BETA_BOUND,
                             delta_beta_bound=constants.RANDOM_CAMERA_DELTA_BETA_BOUND,
                             field_bound=constants.RANDOM_CAMERA_FIELD_DEPTH_BOUND,
                             v_xy_min_bound=constants.RANDOM_CAMERA_V_XY_MIN_BOUND,
                             v_xy_max_bound=constants.RANDOM_CAMERA_V_XY_MAX_BOUND,
                             v_alpha_min_bound=constants.RANDOM_CAMERA_V_ALPHA_MIN_BOUND,
                             v_alpha_max_bound=constants.RANDOM_CAMERA_V_ALPHA_MAX_BOUND,
                             v_beta_min_bound=constants.RANDOM_CAMERA_V_BETA_MIN_BOUND,
                             v_beta_max_bound=constants.RANDOM_CAMERA_V_BETA_MAX_BOUND)

            agentCam = aCam.AgentCam(camera, -1, -1)
            agentCam.camera.id = agentCam.id
            self.agentCams_list.append(agentCam)

        for k in range(k):
            camera = MobileCamera(id=-1, xc=0, yc=0, alpha=0, beta=0, trajectory=[], field_depth=0)
            camera.randomize(camera_type=MobileCameraType.FREE, beta_bound=constants.RANDOM_CAMERA_BETA_BOUND,
                             delta_beta_bound=constants.RANDOM_CAMERA_DELTA_BETA_BOUND,
                             field_bound=constants.RANDOM_CAMERA_FIELD_DEPTH_BOUND,
                             v_xy_min_bound=constants.RANDOM_CAMERA_V_XY_MIN_BOUND,
                             v_xy_max_bound=constants.RANDOM_CAMERA_V_XY_MAX_BOUND,
                             v_alpha_min_bound=constants.RANDOM_CAMERA_V_ALPHA_MIN_BOUND,
                             v_alpha_max_bound=constants.RANDOM_CAMERA_V_ALPHA_MAX_BOUND,
                             v_beta_min_bound=constants.RANDOM_CAMERA_V_BETA_MIN_BOUND,
                             v_beta_max_bound=constants.RANDOM_CAMERA_V_BETA_MAX_BOUND)

            agentCam = aCam.AgentCam(camera, -1, -1)
            agentCam.camera.id = agentCam.id
            self.agentCams_list.append(agentCam)

    def add_create_Target(self, x, y, vx, vy, ax, ay, trajectory_type, trajectory, type, radius, t_add, t_del):
        """"
               :param
                   1. (int) x                               -- x value of the center
                   2. (int) y                               -- y value of the center
                   3. (int) vx                              -- vx speed
                   4. (int) vy                              -- vy speed
                   5. (string) trajectory_type              -- "fix","linear" choice for the target's way to moove
                   6. (int) trajectory_choice               -- will bound the target to the given trajectory in
                                                               InformationRoomSimulation
                   7. (int) radius                            -- radius from the center
                   8. (string) type                         -- "fix","target", to make the difference between known
                                                                and unkown target
                   9. ([[int],...]) t_add                   -- list of all the times where the target should appear
                                                               in the room
                  10. ([[int],...]) t_del                   -- list of all the times where the target should disappear
                                                               in the room

                :notes
                        fells free to write some comments.
        """
        target = Target(id=-1, xc=x, yc=y, vx=vx, vy=vy, ax=ax, ay = ay, radius= radius, type=type, color=None,
                        trajectory_type=trajectory_type, trajectory= trajectory, t_add=t_add, t_del=t_del)
        self.add_Target(target)

    def add_create_AgentCam(self, x, y, alpha, beta, trajectory, field_depth=None, color=0,
                            t_add=-1, t_del=-1, type=None, vx_vy_min=None, vx_vy_max=None, v_alpha_min=None,
                            v_alpha_max=None, delta_beta=None, v_beta_min=None, v_beta_max=None):
        """"
               :param
                   1. (int) x                               -- x value of the center
                   2. (int) y                               -- y value of the center
                   3. (int) vx                              -- vx speed
                   4. (int) vy                              -- vy speed
                   5. (string) trajectory_type              -- "fix","linear" choice for the target's way to moove
                   6. (int) trajectory_choice               -- will bound the target to the given trajectory in
                                                               InformationRoomSimulation
                   7. (int) radius                            -- radius from the center
                   8. (string) type                         -- "fix","target", to make the difference between known
                                                                and unkown target
                   9. ([[int],...]) t_add                   -- list of all the times where the target should appear
                                                               in the room
                  10. ([[int],...]) t_del                   -- list of all the times where the target should disappear
                                                               in the room

                :notes
                        fells free to write some comments.
        """
        camera = MobileCamera(-1, x, y, alpha, beta, trajectory, field_depth, color, t_add, t_del, type, vx_vy_min,
                              vx_vy_max, v_alpha_min, v_alpha_max, delta_beta, v_beta_min, v_beta_max)
        agentCam = aCam.AgentCam(camera, t_add, t_del)
        agentCam.camera.id = agentCam.id
        self.agentCams_list.append(agentCam)

    def add_Target(self, target):
        """"
               :param
                   1. (Target) target  -- a target object

                :notes
                        fells free to write some comments.
        """
        number_of_target = len(self.target_list)
        target.id = number_of_target
        self.target_list.append(target)


class RoomRepresentation:
    """
        Class RoomRepresentation.

        Description : This class gives a standart version for the layout of a file

            :param
                1. ((int),(int),(int) color       -- color to represent all the targets. If = 0,
                                                    the random color selected.

            :attibutes
                1. (numpy.array) coordinate_room  -- numpy.array([0, 0, constants.LENGHT_ROOM, constants.WIDTH_ROOM])
                                                     give the corner in the room (0,0),...
                2. (list) target_representation_list      -- targets active in the room
                3. (list) active_AgentCams_list   -- agentCams active in the room
                4. (list) active_AgentUser_list   -- agentUsers active in the room
                5. (int) time                     -- actuall time
                6. ((int),(int),(int) color       -- color to represent all the targets.

            :notes
                fells free to write some comments.
    """

    def __init__(self, color=0):
        """Room radius"""
        self.coordinate_room = np.array([0, 0, constants.ROOM_DIMENSION_X, constants.ROOM_DIMENSION_Y])  # x y l h

        """Target informations"""
        self.target_representation_list = []

        """Agent informations"""
        self.agentCams_representation_list = []
        self.agentUser_representation_list = []

        """Others attributes"""
        self.color = color

        """Default values"""
        if color == 0:
            r = random.randrange(20, 230, 1)
            g = random.randrange(20, 230, 1)
            b = random.randrange(20, 255, 1)
            self.color = (r, g, b)

    def save_to_txt(self):
        s = "dim_in_x: %0.2f dim_in_y: %0.2f"%(self.coordinate_room[2],self.coordinate_room[3])
        s1 = " x_offset:%0.2f y_offset:%0.2f scale_x:%0.2f scale_y:%0.2f"%(constants.X_OFFSET,constants.Y_OFFSET,constants.X_SCALE,constants.Y_SCALE)

        return s + s1 + "\n"

    def load_from_txt(self,s):
        s = s.replace("\n", "")
        s = s.replace(" ", "")
        attribute = re.split("dim_in_x:|dim_in_y:|x_offset:|y_offset:|scale_x:|scale_y:",s)
        self.coordinate_room = np.array([0, 0, float(attribute[1]),float(attribute[2])])
        constants.ROOM_DIMENSION_X = int(float(attribute[1]))
        constants.ROOM_DIMENSION_Y = int(float(attribute[2]))
        constants.X_OFFSET = int(float(attribute[3]))
        constants.Y_OFFSET = int(float(attribute[4]))
        constants.X_SCALE = int(float(attribute[5]))
        constants.Y_SCALE = int(float(attribute[6]))

    def init_RoomRepresentation(self, room):
        """
            :description
               Use a finer description with an object room, to set the RoomRepresentation

            :param
                1. (Room) room -- object
        """
        for target in room.information_simulation.target_list:
            if target.target_type == TargetType.SET_FIX:
                self.add_targetRepresentation_from_target(target)

        for agent in room.information_simulation.agentCams_list:
            agentCam_representation = AgentCamRepresentation(0)
            agentCam_representation.update_from_agent(agent)

            self.agentCams_representation_list.append(agentCam_representation)

        for agent in room.information_simulation.agentUser_list:
            agentUser_representation = AgentUserRepresentation(0)
            agentUser_representation.update_from_agent(agent)
            self.agentUser_representation_list.append(agentUser_representation)

    def update_target_based_on_memory(self, Target_TargetEstimator):
        """
              :description
                 Use agent's TargetEstimator to modify the RoomRepresentation

              :param
                  1. (list) Target_TargetEstimator -- see file memory, class Target_TargetEstimator
         """
        for target_detected_id in Target_TargetEstimator.items_discovered:
            is_in_RoomRepresentation = False
            all_TargetEstimator_for_target_id = Target_TargetEstimator.get_item_list(target_detected_id)
            last_TargetEstimator = all_TargetEstimator_for_target_id[-1]

            for target in self.target_representation_list:
                if target.id == target_detected_id:
                    is_in_RoomRepresentation = True
                    target.xc = last_TargetEstimator.item.xc
                    target.yc = last_TargetEstimator.item.yc


                    target.type = last_TargetEstimator.item.target_type
                    if not target.type == TargetType.FIX:
                        target.alpha = last_TargetEstimator.item.alpha

                    # TODO - replace variance on estimation
                    '''
                    target.variance_on_estimation = last_TargetEstimator.variance_on_estimation
                    if last_TargetEstimator.variance_on_estimation is not None:
                        norm_variance_pos = np.sqrt(
                            np.square(last_TargetEstimator.variance_on_estimation[0]) + np.square(
                                last_TargetEstimator.variance_on_estimation[1]))
                    else:
                        norm_variance_pos = 0.1
                    '''
                    target.evaluate_target_confidence(0.1,
                                                      constants.get_time() - last_TargetEstimator.time_stamp)
                    break

            if not is_in_RoomRepresentation:
                self.add_targetRepresentation(last_TargetEstimator.item.id, last_TargetEstimator.item.xc,
                                              last_TargetEstimator.item.yc,
                                              last_TargetEstimator.item.radius, last_TargetEstimator.item.target_type)

    def update_agent_based_on_memory(self, Agent_AgentEstimator):
        """
              :description
                 Use agent's TargetEstimator to modify the RoomRepresentation

              :param
                  1. (list) Target_TargetEstimator -- see file memory, class Target_TargetEstimator
         """

        for agent_detected_id in Agent_AgentEstimator.items_discovered:
            is_in_RoomRepresentation = False
            all_TargetEstimator_for_target_id = Agent_AgentEstimator.get_item_list(agent_detected_id)
            itemEstimation = all_TargetEstimator_for_target_id[-1]

            for agent in self.agentCams_representation_list:
                camera = agent.camera_representation

                if agent.id == agent_detected_id:
                    is_in_RoomRepresentation = True                
                    agent.is_active = itemEstimation.item.is_active
                    agent.evaluate_agent_confidence(0.001, constants.get_time() - itemEstimation.time_stamp)
                    camera.xc = itemEstimation.item.camera_representation.xc
                    camera.yc = itemEstimation.item.camera_representation.yc
                    # self.item_speeds = [0, 0]  # [ camera.vx,  camera.vy]
                    # self.item_acceleration = [0, 0]  # [ camera.ax,  camera.ay]
                    camera.type = itemEstimation.item.camera_representation.camera_type
                    camera.alpha = itemEstimation.item.camera_representation.alpha
                    camera.beta = itemEstimation.item.camera_representation.beta
                    camera.field_depth = itemEstimation.item.camera_representation.field_depth
                    camera.is_active = itemEstimation.item.camera_representation.is_active

                    break

            if not is_in_RoomRepresentation:
                self.agentCams_representation_list.append(itemEstimation.item)

    def add_targetRepresentation_from_target(self, target):
        """
            :description
                RoomRepresentation can only use TargetRepresentation, methods to convert a Target to a
                TargetRepresentation and added in the RoomRepresentation

                :param
                    1. (Target) target -- object, see class Target
        """
        self.add_targetRepresentation(target.id, target.xc, target.yc, target.radius, target.type)

    def add_targetRepresentation(self, id, x, y, radius, label):
        """
            :description
                 create and add a TargetRepresentation to the RoomRepresentation

            :param
                  1. (int) id                  -- numerical value to recognize the target easily
                  2. (int) x                   -- x value of the center of the targetRepresentation
                  3. (int) y                   -- y value of the center of the targetRepresentation
                  4. (int) radius                -- radius from the center
                  5. (string) type             -- "fix","target", to make the difference between known and unkown target
        """
        self.target_representation_list.append(TargetRepresentation(id, x, y, 0, 0, 0, 0, radius, label, self.color))


    def get_multiple_target_with_id(self, id_list):
        """
            :param
                 1. (list) id_list   -- list from id we want to get
            :return
                1. list of targets with ids in the list provided in the argument

        """
        return [target for target in self.target_representation_list if target.id in id_list]

    def get_Target_with_id(self, target_id):
        """
            :param
                 1. (int) target_id  -- target's id
            :return
                1. None if not found
                2. Target else

        """
        for target in self.target_representation_list:
            if target.id == target_id:
                return target
        return None


class Room(RoomRepresentation):
    """
        Class Room extend RoomRepresentation.

        Description : creation of a fake room for simulation's needs

            :attibutes
                1. (numpy.array) coordinate_room     -- numpy.array([0, 0, constants.LENGHT_ROOM, constants.WIDTH_ROOM])
                                                        give the corner in the room (0,0),...
                2. (list) target_representation_list                           -- targets active in the room
                3. (list) active_AgentCams_list                        -- agentCams active in the room
                4. (list) active_AgentUser_list                        -- agentUsers active in the room
                5. (int) time                                          -- actual time
                6. ((int),(int),(int) color                            -- color to represent all the targets.
                7. (InformationRoomSimulation) information_simulation  -- fake environment
                8. (list) active_Camera_list                           -- cameras active in the room

            :notes
                fells free to write some comments.
    """

    def __init__(self):
        super().__init__(0)
        self.active_AgentCams_list = []
        self.active_AgentUser_list = []
        self.information_simulation = InformationRoomSimulation()

    def add_del_target_timed(self):
        """
            :description
                Add and remove target from target_representation_list for given time
        """

        for target in self.information_simulation.target_list:
            if target.t_add[target.number_of_time_passed] <= constants.get_time() <= \
                    target.t_del[target.number_of_time_passed] and not target.is_on_the_map:
                target.is_on_the_map = True
                self.target_representation_list.append(target)

            elif constants.get_time() > target.t_del[target.number_of_time_passed] and target.is_on_the_map:
                if target.number_of_time_passed < len(target.t_add) - 1:
                    target.number_of_time_passed = target.number_of_time_passed + 1
                target.is_on_the_map = False
                self.target_representation_list.remove(target)

    def des_activate_camera_agentCam_timed(self):
        """
            :description
                Add and remove target from target_representation_list for given time
        """

        for agent in self.information_simulation.agentCams_list:
            camera = agent.camera
            if camera.t_add[camera.number_of_time_passed] <= constants.get_time() <= \
                    camera.t_del[camera.number_of_time_passed] and not camera.is_active:
                camera.is_active = True
                agent.log_main.info("camera of a agent %d is activated at %.02f s" % (agent.id, constants.get_time()))

            elif constants.get_time() > camera.t_del[camera.number_of_time_passed] and camera.is_active:
                if camera.number_of_time_passed < len(camera.t_add) - 1:
                    camera.number_of_time_passed = camera.number_of_time_passed + 1
                camera.is_active = False
                agent.log_main.info(
                    "camera of a agent %d is desactivated at %.02f s" % (agent.id, constants.get_time()))

    def des_activate_agentCam_timed(self):
        """
            :description
                Add and remove target from target_representation_list for given time
        """
        for agent in self.information_simulation.agentCams_list:
            if agent.t_add[agent.number_of_time_passed] <= constants.get_time() <= \
                    agent.t_del[agent.number_of_time_passed] and not agent.is_active:
                agent.is_active = True
                self.active_AgentCams_list.append(agent)
                self.agentCams_representation_list = self.active_AgentCams_list
                agent.log_main.info("Agent %d is activated at %.02f s" % (agent.id, constants.get_time()))

            elif constants.get_time() > agent.t_del[agent.number_of_time_passed] and agent.is_active:
                if agent.number_of_time_passed < len(agent.t_add) - 1:
                    agent.number_of_time_passed = agent.number_of_time_passed + 1
                agent.is_active = False
                self.active_AgentCams_list.remove(agent)
                self.agentCams_representation_list = self.active_AgentCams_list
                agent.log_main.info("Agent %d is desactivated at %.02f s" % (agent.id, constants.get_time()))

    def add_create_Target(self, x, y, vx, vy, trajectory_type, trajectory, type, radius, t_add, t_del):
        """"
               :param
                   1. (int) x                               -- x value of the center
                   2. (int) y                               -- y value of the center
                   3. (int) vx                              -- vx speed
                   4. (int) vy                              -- vy speed
                   5. (string) trajectory_type              -- "fix","linear" choice for the target's way to moove
                   6. (int) trajectory_choice               -- will bound the target to the given trajectory
                                                               in InformationRoomSimulation
                   7. (int) radius                          -- radius from the center
                   8. (string) type                         -- "fix","target", to make the difference between known
                                                                and unkown target
                   9. ([[int],...]) t_add                   -- list of all the times where the target should
                                                               appear in the room
                  10. ([[int],...]) t_del                   -- list of all the times where the target should
                                                               disappear in the room

                :notes
                    !!! No effect on target_representation_list
        """
        self.information_simulation.add_create_Target(x, y, vx, vy, 0, 0, trajectory_type, trajectory, type, radius,
                                                      t_add, t_del)

    def add_AgentCam(self, agent):
        """
            :description
                Create and add AgentCam to the room

            :param
                1. (int) x                               -- x values of the center
                2. (int) y                               -- y values of the center
                3. (int) orientation_alpha               -- alpha, orientation from the camera, -180 to 180 degrees
                4. (int) field_opening_beta              -- beta, field from the camera, 0 to 180 degrees
                5. (int) is_fix                          -- 0 = camera can rotate, 1 = cam orientation is fix
        """
        self.information_simulation.agentCams_list.append(agent)

    def add_create_AgentUser(self, number=1):
        """
            :description
                Create and add AgentUser to the room

            :param
                1. (int) number -- number of agent to be created, by default 1
        """
        for n in range(number):
            agent = aUser.AgentUser()
            self.information_simulation.agentUser_list.append(agent)
        self.active_AgentUser_list = self.information_simulation.agentUser_list
        self.agentUser_representation_list = self.active_AgentUser_list

    def add_Target(self, target):
        """"
               :param
                   1. (int) x                               -- x value of the center
                   2. (int) y                               -- y value of the center
                   3. (int) vx                              -- vx speed
                   4. (int) vy                              -- vy speed
                   5. (string) trajectory_type              -- "fix","linear" choice for the target's way to moove
                   6. (int) trajectory_choice               -- will bound the target to the given trajectory
                                                               in InformationRoomSimulation
                   7. (int) radius                          -- radius from the center
                   8. (string) type                         -- "fix","target", to make the difference between known
                                                                and unkown target
                   9. ([[int],...]) t_add                   -- list of all the times where the target should
                                                               appear in the room
                  10. ([[int],...]) t_del                   -- list of all the times where the target should
                                                               disappear in the room

                :notes
                    !!! No effect on target_representation_list
        """
        self.information_simulation.add_Target(target)

    def get_multiple_Agent_with_id(self, id_list, agent_type):
        """
            :param
                 1. (list) id_list                  -- list from id we want to get
                 2. (AgentType) agent_type          -- see class

            :return
                1. list of agents with ids in the list provided in the argument

        """

        if agent_type == AgentType.AGENT_CAM:
            return [agent for agent in self.active_AgentCams_list if agent.id in id_list]
        elif agent_type == AgentType.AGENT_USER:
            return [agent for agent in self.active_AgentUser_list if agent.id in id_list]

    def get_Agent_with_id(self, agent_id):
        """
            :param
                 1. (int) agent_id  -- target's id
            :return
                1. None if not found
                2. Agent else

        """
        for agent in self.active_AgentCams_list:
            if agent.id == agent_id:
                return agent
        return None
