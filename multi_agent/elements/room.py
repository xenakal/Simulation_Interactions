from multi_agent.elements.camera import *
# from multi_agent.agent_camera import *
# from multi_agent.agent_user import *
import multi_agent.agent.agent_interacting_room_camera
import multi_agent.agent.agent_interacting_room_user
import constants


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
        self.coordinate_room = numpy.array([0, 0, constants.LENGHT_ROOM, constants.WIDTH_ROOM])  # x y l h

        "Target that should appear in the room"
        self.Target_list = []

        "Trajectories proposed to the targets"
        self.trajectories = []
        self.trajectories_number = []

    def init_Target(self, x, y, vx, vy, trajectory_type, trajectory_choice, type, radius, t_add, t_del):
        """"
            :param
                1. (int_list) x                               -- x values of the center
                2. (int_list) y                               -- y values of the center
                3. (int_list) vx                              -- vx speeds
                4. (int_list) vy                              -- vy speeds
                5. (string_list) trajectory_type              -- "fix","linear" choice for the target's way to moove
                6. (int_list) trajectory_choice               -- will bound the target to the given trajectory
                                                                in InformationRoomSimulation
                7. (int_list) radius                            -- radius from the center
                8. (string_list) type                         -- "fix","target", to make the difference between known
                                                                 and unkown target
                9. ([[[int],...],...]) t_add                  -- list of all the times where the target should appear
                                                                 in the room
               10. ([[[int],...],...]) t_del                  -- list of all the times where the target should disappear
                                                                 in the room

            :notes
                 fells free to write some comments.
           """
        if len(x) > 0:
            for n in range(len(x)):
                self.add_Target(x[n], y[n], vx[n], vy[n], trajectory_type[n], trajectory_choice[n], type[n], radius[n],
                                t_add[n], t_del[n])

    def add_Target(self, x, y, vx, vy, trajectory_type, trajectory_choice, type, radius, t_add, t_del):
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
        if trajectory_choice in self.trajectories_number:
            index = self.trajectories_number.index(trajectory_choice)
            number_Target = len(self.Target_list)
            self.Target_list.append(Target(number_Target, x, y, vx, vy, trajectory_type,
                                           self.trajectories[index], type, radius, t_add, t_del))
        else:
            print("fichier info_room_simu l27 : error while creating target, trajectory number not found")

    def init_trajectories(self, all_trajectories_loaded):
        """"
            :param
                 1. (list) all_trajectories_loaded  -- [(trajectory_number,trajectory),(int, [(int,int),...]),]

            :notes
                 fells free to write some comments.
        """
        for num_traj in all_trajectories_loaded:
            (num, traj) = num_traj
            self.trajectories.append(num_traj)
            self.trajectories_number.append(num)


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
                2. (list) active_Target_list      -- targets active in the room
                3. (list) active_AgentCams_list   -- agentCams active in the room
                4. (list) active_AgentUser_list   -- agentUsers active in the room
                5. (int) time                     -- actuall time
                6. ((int),(int),(int) color       -- color to represent all the targets.

            :notes
                fells free to write some comments.
    """

    def __init__(self, color=0):
        """Room radius"""
        self.coordinate_room = numpy.array([0, 0, constants.LENGHT_ROOM, constants.WIDTH_ROOM])  # x y l h

        """Target informations"""
        self.active_Target_list = []

        """Agent informations"""
        self.active_AgentCams_list = []
        self.active_AgentUser_list = []

        """Others attributes"""
        self.time = 0
        self.color = color

        """Default values"""
        if color == 0:
            r = random.randrange(20, 230, 1)
            g = random.randrange(20, 230, 1)
            b = random.randrange(20, 255, 1)
            self.color = (r, g, b)

    def init_RoomRepresentation(self, room):
        """
            :description
               Use a finer description with an object room, to set the RoomRepresentation

            :param
                1. (Room) room -- object
        """
        for target in room.information_simulation.Target_list:
            if target.type == "fix":
                self.add_targetRepresentation_from_target(target)

        for agent in room.active_AgentCams_list:
            self.active_AgentCams_list.append(agent)

        for agent in room.active_AgentUser_list:
            self.active_AgentUser_list.append(agent)

    def update_target_based_on_memory(self, Target_TargetEstimator):
        """
              :description
                 Use agent's TargetEstimator to modify the RoomRepresentation

              :param
                  1. (list) Target_TargetEstimator -- see file memory, class Target_TargetEstimator
         """
        for Target_detected_id in Target_TargetEstimator.Target_already_discovered_list:
            is_in_RoomRepresentation = False
            all_TargetEstimator_for_target_id = Target_TargetEstimator.get_Target_list(Target_detected_id)
            last_TargetEstimator = all_TargetEstimator_for_target_id[len(all_TargetEstimator_for_target_id) - 1]

            for target in self.active_Target_list:
                if target.id == Target_detected_id:
                    is_in_RoomRepresentation = True
                    target.xc = last_TargetEstimator.target_position[0]
                    target.yc = last_TargetEstimator.target_position[1]
                    break

            if not is_in_RoomRepresentation:
                self.add_targetRepresentation(last_TargetEstimator.target_id, last_TargetEstimator.target_position[0],
                                              last_TargetEstimator.target_position[1],
                                              last_TargetEstimator.target_radius, last_TargetEstimator.target_label)

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
        self.active_Target_list.append(TargetRepresentation(id, x, y, radius, label, self.color))

    def get_multiple_Agent_with_id(self, id_list, agent_type):
        """
            :param
                 1. (list) id_list                  -- list from id we want to get
                 2. (string) agent_type               -- "agentCam" or "agentUser"

            :return
                1. list of agents with ids in the list provided in the argument

        """

        if agent_type == "agentCam":
            return [agent for agent in self.active_AgentCams_list if agent.id in id_list]
        elif agent_type == "agentUser":
            return [agent for agent in self.active_AgentUser_list if agent.id in id_list]

    def get_multiple_target_with_id(self, id_list):
        """
            :param
                 1. (list) id_list   -- list from id we want to get
            :return
                1. list of targets with ids in the list provided in the argument

        """
        return [target for target in self.active_Target_list if target.id in id_list]

    def get_Target_with_id(self, target_id):
        """
            :param
                 1. (int) target_id  -- target's id
            :return
                1. None if not found
                2. Target else

        """
        for target in self.active_Target_list:
            if target.id == target_id:
                return target
        return None

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


class Room(RoomRepresentation):
    """
        Class Room extend RoomRepresentation.

        Description : creation of a fake room for simulation's needs

            :attibutes
                1. (numpy.array) coordinate_room     -- numpy.array([0, 0, constants.LENGHT_ROOM, constants.WIDTH_ROOM])
                                                        give the corner in the room (0,0),...
                2. (list) active_Target_list                           -- targets active in the room
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
        self.information_simulation = InformationRoomSimulation()
        self.active_Camera_list = []

    def init_room(self, x, y, vx, vy, trajectory_type, trajectory_choice, type, radius, t_add, t_del):
        """
            :param
                1. (int_list) x                               -- x values of the center
                2. (int_list) y                               -- y values of the center
                3. (int_list) vx                              -- vx speeds
                4. (int_list) vy                              -- vy speeds
                5. (string_list) trajectory_type              -- "fix","linear" choice for the target's way to moove
                6. (int_list) trajectory_choice               -- will bound the target to the given trajectory in InformationRoomSimulation
                7. (int_list) radius                            -- radius from the center
                8. (string_list) type                         -- "fix","target", to make the difference between known and unkown target
                9. ([[[int],...],...]) t_add                  -- list of all the times where the target should appear in the room
               10. ([[[int],...],...]) t_del                  -- list of all the times where the target should disappear in the room

            :notes
                 it will fill the information_simulation
           """

        self.information_simulation.init_Target(x, y, vx, vy, trajectory_type, trajectory_choice, type, radius, t_add,
                                                t_del)

    def init_AgentCam(self, x, y, orientation_alpha, field_opening_beta, is_fix):
        """
            :description
                Create and add AgentCam to the room

            :param
                1. (int_list) x                               -- x values of the center
                2. (int_list) y                               -- y values of the center
                3. (int_list) orientation_alpha               -- alpha, orientation from the camera, -180 to 180 degrees
                4. (int_list) field_opening_beta              -- beta, field from the camera, 0 to 180 degrees
                5. (int_list) is_fix                          -- 0 = camera can rotate, 1 = cam orientation is fix
        """
        for n in range(len(x)):
            self.add_AgentCam(x[n], y[n], orientation_alpha[n], field_opening_beta[n], is_fix[n], self)

    def add_AgentCam(self, cam_x, cam_y, cam_alpha, cam_beta, fix, myRoom):
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
        number_Camera = len(self.active_Camera_list)
        number_AgentCam = len(self.active_AgentCams_list)
        camera = Camera(myRoom, number_Camera, cam_x, cam_y, cam_alpha, cam_beta, fix)
        self.active_Camera_list.append(camera)
        self.active_AgentCams_list.append(
            multi_agent.agent.agent_interacting_room_camera.AgentCam(number_AgentCam, camera))

    def init_AgentUser(self, number=1):
        """
            :description
                Create and add AgentUser to the room

            :param
                1. (int) number -- number of agent to be created, by default 1
        """
        for n in range(number):
            number_AgentUser = len(self.active_AgentUser_list)
            self.active_AgentUser_list.append(multi_agent.agent.agent_interacting_room_user.AgentUser(number_AgentUser))

    def init_trajectories(self, all_trajectories_loaded):
        """
            :description
                Add fake trajectories to the room

             :param
                1. (list) all_trajectories_loaded  -- [(trajectory_number,trajectory),(int, [(int,int),...]),]
         """
        self.information_simulation.init_trajectories(all_trajectories_loaded)

    def add_del_target_timed(self):
        """
            :description
                Add and remove target from active_Target_list for given time
        """

        for target in self.information_simulation.Target_list:
            if self.time in target.t_add:
                self.active_Target_list.append(target)
            elif self.time in target.t_del:
                index = self.active_Target_list.index(target)
                del self.active_Target_list[index]

    def add_Target(self, x, y, vx, vy, trajectory_type, trajectory_choice, type, radius, t_add, t_del):
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
                    !!! No effect on active_Target_list
        """
        self.information_simulation.add_Target(x, y, vx, vy, trajectory_type, trajectory_choice, type, radius, t_add,
                                               t_del)
