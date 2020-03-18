import numpy as np


class LinkTargetCamera():
    """
        Class Example.

        Description : This class gives a standart version for the layout of a file

            :param
                1. (type) name -- description
                2. (type) name -- description
                3. (type) name -- description

            :attibutes
                1. (type) name -- description
                2. (type) name -- description
                3. (type) name -- description


            :notes
                fells free to write some comments.
    """

    def __init__(self, room):
        self.room = room
        self.link_camera_target = []

    def update_link_camera_target(self):
        for target in self.room.active_Target_list:
            is_in_list = False
            for targetAgentLink in self.link_camera_target:
                if targetAgentLink.target_id == target.id:
                    is_in_list = True
                    break

            if not is_in_list:
                self.link_camera_target.append(TargetAgentLink(target.id))

    def reset_agent_and_distance(self):
        for targetAgentLink in self.link_camera_target:
            targetAgentLink.reset()

    def lock_targetAgentLink(self, target_id):
        for targetAgentLink in self.link_camera_target:
            if targetAgentLink.id == target_id:
                targetAgentLink.lock()

    def unlock_targetAgentLink(self, target_id):
        for targetAgentLink in self.link_camera_target:
            if targetAgentLink.id == target_id:
                targetAgentLink.unlock()

    def compute_link_camera_target(self):
        self.reset_agent_and_distance()

        "For every target ..."
        for target in self.room.active_Target_list:
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
                        if cdt_in_field and cdt_not_hidden:

                            "Distance computation"
                            distance_to_target = np.power(np.power((agent.camera.xc - target.xc), 2)
                                                          + np.power((agent.camera.yc - target.yc), 2), 0.5)

                            if distance_to_target < distance_min:
                                (agent_id, distance_min) = (agent.id, distance_to_target)

                    targetAgentLink.set(agent_id,distance_min)

            "If the target has no targetAgentLink, creation of a new object"
            if not is_in_list:
                self.link_camera_target.append(TargetAgentLink(target.id))

    def is_in_charge(self, target_id, agent_id):
        for targetAgentLink in self.link_camera_target:
            if targetAgentLink.target_id == target_id and targetAgentLink.agent_id == agent_id:
                return True
        return False


class TargetAgentLink():
    def __init__(self, target_id):
        self.target_id = target_id
        self.agent_id = -1
        self.distance = 10000000000
        self.is_lock = False

    def reset(self):
        if not self.is_lock:
            self.agent_id = -1
            self.distance = 10000000000

    def set(self, agent_id, distance):
        if not self.is_lock:
            self.agent_id = agent_id
            self.distance = distance

    def lock(self):
        self.is_lock = True

    def unlock(self):
        self.is_lock = False

    def to_string(self):
        return "target " + str(self.target_id) + "linked to " + str(self.agent_id) + ", locked = " + str(self.is_lock)