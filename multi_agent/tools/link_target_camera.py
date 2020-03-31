import numpy as np
from multi_agent.elements.target import TargetType


class LinkTargetCamera():
    """
        Class Example.

        Description : This class gives a standart version for the layout of a file

            :param
                1. (RoomRepresentation) room                 -- RoomRepresentation object

            :attibutes
                1. (RoomRepresentation) room                 -- RoomRepresentation object
                2. (TargetAgentLink_list) link_camera_target -- list containing all the links

            :notes
                fells free to write some comments.
    """

    def __init__(self, room):
        self.room = room
        self.link_camera_target = []

    def update_link_camera_target(self):
        """
            :description
                Create a new AgentTargetLink for every target in the RoomRepresentation
        """
        for target in self.room.active_Target_list:
            is_in_list = False
            for targetAgentLink in self.link_camera_target:
                if targetAgentLink.target_id == target.id:
                    is_in_list = True
                    break

            if not is_in_list:
                self.link_camera_target.append(TargetAgentLink(target.id))

    def get_agent_in_charge(self, target_id):
        for targetAgentLink in self.link_camera_target:
            if targetAgentLink.target_id == target_id:
                return targetAgentLink.agent_id
        return -1

    def reset_agent_and_distance(self):
        """
            :description
               Reset the value from every AgentTargetLink in the list link_camera_target

            :note
                AgentTargetLink is not reset when locked
        """
        for targetAgentLink in self.link_camera_target:
            targetAgentLink.reset()

    def lock_targetAgentLink(self, target_id):
        """
            :description
               Lock the value from every AgentTargetLink in the list link_camera_target
        """
        for targetAgentLink in self.link_camera_target:
            if targetAgentLink.id == target_id:
                targetAgentLink.lock()

    def unlock_targetAgentLink(self, target_id):
        """
            :description
               UnlLock the value from every AgentTargetLink in the list link_camera_target
        """
        for targetAgentLink in self.link_camera_target:
            if targetAgentLink.id == target_id:
                targetAgentLink.unlock()

    def compute_link_camera_target(self):
        """
            :description
              1. Set for each target in the room the closest agent.
              2. Function upate_link_camera also included
        """

        self.reset_agent_and_distance()

        "For every target ..."
        for target in self.room.active_Target_list:
            "Not usefull to set link with object that are fix"
            if not target.type == TargetType.SET_FIX:
                is_in_list = False
                for targetAgentLink in self.link_camera_target:
                    "We find the corresponding targetAgentLink"
                    if target.id == targetAgentLink.target_id:

                        is_in_list = True

                        "Computing what agent has the best view for this target"
                        (agent_id, distance_min) = (-1, 100000)
                        for agent in self.room.active_AgentCams_list:
                            # TODO "calcul avec les prédictions au lieu des positions actuelles"

                            "Put target radius = 0 to consider only the centers"
                            cdt_in_field = agent.camera.is_x_y_radius_in_field_not_obstructed(target.xc, target.yc,
                                                                                              target.radius)
                            cdt_not_hidden = not agent.camera.is_x_y_in_hidden_zone_all_targets(target.xc, target.yc)
                            "Check is the camera can see the target for a given room geometry"
                            # if cdt_in_field and cdt_not_hidden and agent.camera.isActive:
                            # TODO - ici envoyer un message pour signaler une panne de camera ??
                            if cdt_in_field and cdt_not_hidden and agent.camera.isActive:

                                "Distance computation"
                                distance_to_target = np.power(np.power((agent.camera.xc - target.xc), 2)
                                                              + np.power((agent.camera.yc - target.yc), 2), 0.5)

                                if distance_to_target < distance_min:
                                    (agent_id, distance_min) = (agent.id, distance_to_target)

                        targetAgentLink.set(agent_id, distance_min)

                "If the target has no targetAgentLink, creation of a new object"
                if not is_in_list:
                    self.link_camera_target.append(TargetAgentLink(target.id))

    def is_in_charge(self, target_id, agent_id):
        """
            :description
                1.  !!! Before using this function, use compute_link_camera_target.
                2.  return True if the given agent is in charge for the given target.
        """
        for targetAgentLink in self.link_camera_target:
            if targetAgentLink.target_id == target_id and targetAgentLink.agent_id == agent_id:
                return True
        return False


class TargetAgentLink():
    """
        Class TargetAgentLink.

        Description : Object to create a link between a agent and a target

            :param
                1. (int) target_id -- to identify the target
                2. (int) agent_id  -- to identify the agent

            :attibutes
               1. (int) target_id -- to identify the target
                2. (int) agent_id  -- to identify the agent
                3. (int) distance  -- distance target - agent ( => camera)
                4. (bool) is_lock  -- if True values can't be modify


            :notes
                fells free to write some comments.
    """

    def __init__(self, target_id):
        self.target_id = target_id
        self.agent_id = -1
        self.distance = 10000000000
        self.is_lock = False

    def reset(self):
        """
            :description
                set to default values, if unlock
        """
        if not self.is_lock:
            self.agent_id = -1
            self.distance = 10000000000

    def set(self, agent_id, distance):
        """
            :description
                set the values to the param, if unlock

            :param
                1. (int) target_id -- to identify the target
                2. (int) agent_id  -- to identify the agents
        """
        if not self.is_lock:
            self.agent_id = agent_id
            self.distance = distance

    def lock(self):
        """
            :description
                to lock the object
        """
        self.is_lock = True

    def unlock(self):
        """
            :description
                to unlock the object
        """
        self.is_lock = False

    def to_string(self):
        """
            :description
                string description
        """
        return "target " + str(self.target_id) + "linked to " + str(self.agent_id) + ", locked = " + str(self.is_lock)
