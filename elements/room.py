import numpy
from elements.target import *
from elements.camera import *
#from multi_agent.agent_camera import *
#from multi_agent.agent_user import *
import multi_agent.agent_camera
import multi_agent.agent_user

import constants


class InformationRoomSimulation:
    def __init__(self):
        """Room size"""
        self.coordinate_room = numpy.array([0, 0, constants.LENGHT_ROOM, constants.WIDTH_ROOM])  # x y l h

        """Target that should appear in the room"""
        self.Target_list = []

        """Trajectories proposed to the targets"""
        self.trajectories = []
        self.trajectories_number = []

    def init_Target(self, x, y, vx, vy, trajectory_type, trajectory_choice, type, size, t_add, t_del):
        if len(x) > 0:
            for n in range(len(x)):
                self.add_Target(x[n], y[n], vx[n], vy[n], trajectory_type[n], trajectory_choice[n], type[n], size[n],
                                t_add[n], t_del[n])

    def add_Target(self, x, y, vx, vy, trajectory_type, trajectory_choice, type, size, t_add, t_del):
        if trajectory_choice in self.trajectories_number:
            index = self.trajectories_number.index(trajectory_choice)
            number_Target = len(self.Target_list)
            self.Target_list.append(Target(number_Target, x, y, vx, vy, trajectory_type,
                                           self.trajectories[index], type, size, t_add, t_del))
        else:
            print("fichier info_room_simu l27 : error while creating target, trajectory number not found")

    def init_trajectories(self, all_traj):
        for num_traj in all_traj:
            (num, traj) = num_traj
            self.trajectories.append(num_traj)
            self.trajectories_number.append(num)


class RoomRepresentation:
    def __init__(self, color=0):
        """Room size"""
        self.coordinate_room = numpy.array([0, 0, constants.LENGHT_ROOM, constants.WIDTH_ROOM])  # x y l h

        """Target informations"""
        self.active_Target_list = []
        self.active_Camera_list = []

        """Agent informations"""
        self.active_AgentCams_list = []
        self.active_AgentUser_list = []

        """Others attributes"""
        self.time = 0
        self.color = color

        '''Default values'''
        if color == 0:
            r = random.randrange(20, 230, 1)
            g = random.randrange(20, 230, 1)
            b = random.randrange(20, 255, 1)
            self.color = (r, g, b)

    def init_RoomRepresentation(self, room):
        for Target in room.info_simu.targets_SIMU:
            if Target.type == "fix":
                self.add_targetRepresentation_from_target(Target)

        for agent in room.agentCams:
            self.active_AgentCams_list.append(agent)

        for agent in room.agentUser:
            self.active_AgentUser_list.append(agent)

    def update_target_based_on_memory(self, Target_TargetEstimator):
        for Target_detected_id in Target_TargetEstimator.Target_already_discovered_list:
            is_in_RoomRepresentation = False
            all_TargetEstimator_for_target_id = Target_TargetEstimator.get_Target_list(Target_detected_id)
            last_TargetEstimator = all_TargetEstimator_for_target_id[len(all_TargetEstimator_for_target_id) - 1]

            for Target in self.active_Target_list:
                if Target.id == Target_detected_id:
                    is_in_RoomRepresentation = True
                    Target.xc = last_TargetEstimator.target_position[0]
                    Target.yc = last_TargetEstimator.target_position[1]
                    break

            if not is_in_RoomRepresentation:
                self.add_targetRepresentation(last_TargetEstimator.target_id, last_TargetEstimator.target_position[0],
                                              last_TargetEstimator.target_position[1],
                                              last_TargetEstimator.target_size, last_TargetEstimator.target_label)

    def add_targetRepresentation_from_target(self, target):
        self.add_targetRepresentation(target.id, target.xc, target.yc, target.size, target.type)

    def add_targetRepresentation(self, id, x, y, size, label):
        self.active_Target_list.append(TargetRepresentation(id, x, y, size, label, self.color))

    def get_multiple_Agent_with_id(self, idList, agentType):
        """ Returns the list of agents with ids in the list provided in the argument. """
        if agentType == "agentCam":
            return [agent for agent in self.active_AgentCams_list if agent.id in idList]
        elif agentType == "agentUser":
            return [agent for agent in self.active_AgentUser_list if agent.id in idList]

    def get_multiple_target_with_id(self, targetList):
        """ Returns the list of targets with ids in the list provided in the argument. """
        return [target for target in self.active_Target_list if target.id in targetList]

    def get_Target_with_id(self, targetID):
        for target in self.active_Target_list:
            if target.id == targetID:
                return target
        return None

    def get_Agent_with_id(self, agentID):
        for agent in self.active_AgentCams_list:
            if agent.id == agentID:
                return agent
        return None


class Room(RoomRepresentation):
    def __init__(self):
        super().__init__(0)
        self.info_simu = InformationRoomSimulation()
        self.cameras = []

    def init_room(self, x, y, vx, vy, trajectory_type, trajectory_choice, type, size, t_add, t_del):
        self.info_simu.init_Target(x, y, vx, vy, trajectory_type, trajectory_choice, type, size, t_add, t_del)

    "!!!!!!!!!!!!!!!!!  ici supprimer le myRoom et le remplacer par self ?? "
    def init_AgentCam(self, x, y, orrientation_alpha, field_opening_beta, fix, myRoom):
        for n in range(len(x)):
            self.add_AgentCam(x[n], y[n], orrientation_alpha[n], field_opening_beta[n], fix[n], myRoom)

    def init_AgentUser(self, number):
        for n in range(number):
            number_AgentUser = len(self.active_AgentUser_list)
            self.active_AgentUser_list.append(multi_agent.agent_user.AgentUser(number_AgentUser))

    def init_trajectories(self, all_traj):
        self.info_simu.init_trajectories(all_traj)

    def add_del_target_timed(self):
        for Target in self.info_simu.Target_list:
            if self.time in Target.t_add:
                self.active_Target_list.append(Target)
            elif self.time in Target.t_del:
                self.del_Target(Target)

    def add_Target(self, tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size, t_add, t_del):
        self.info_simu.add_Target(tar_x, tar_y, tar_vx, tar_vy, tar_traj, trajChoice_tar, tar_label, tar_size, t_add,
                                  t_del)

    def del_Target(self, target):
        index = self.active_Target_list.index(target)
        del self.active_Target_list[index]

    def add_AgentCam(self, cam_x, cam_y, cam_alpha, cam_beta, fix, myRoom):
        number_Camera = len(self.cameras)
        number_AgentCam = len(self.active_AgentCams_list)
        camera = Camera(myRoom, number_Camera, cam_x, cam_y, cam_alpha, cam_beta, fix)
        self.cameras.append(camera)
        self.active_AgentCams_list.append(multi_agent.agent_camera.AgentCam(number_AgentCam, camera))
