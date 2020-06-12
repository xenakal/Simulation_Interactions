import numpy as np
import src.multi_agent.elements.camera as cam
from src import constants
from src.multi_agent.elements.target import TargetType


class LinkTargetCamera:
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

    def __init__(self, room, is_room_representation=False):
        self.room = room
        self.is_room_representation = is_room_representation
        self.link_camera_target = []

    def update_link_camera_target(self):
        """
            :description
                Create a new AgentTargetLink for every target in the RoomRepresentation
        """
        for target in self.room.target_representation_list:
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
                return targetAgentLink.agentDistance_list
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

        "For every target ... Not usefull to set link with object that are fix"

        targets = [target for target in self.room.target_representation_list if not target.target_type == TargetType.SET_FIX]
        for target in targets:
                "check if we already saw it"
                is_in_list = False

                "We find the corresponding targetAgentLink"
                targetAgentLink_list = [targetAgentLink for targetAgentLink in self.link_camera_target if target.id == targetAgentLink.target_id]
                if len(targetAgentLink_list) > 0:
                    targetAgentLink = targetAgentLink_list[0]
                    is_in_list = True

                    "Computing what agent has the best view for this target"
                    for agent in self.room.agentCams_representation_list:
                        # TODO "calcul avec les prédictions au lieu des positions actuelles"
                            if not self.is_room_representation:
                                camera = agent.camera
                            else:
                                camera = agent.camera_representation

                            "Put target radius = 0 to consider only the centers"
                            if isinstance(target.radius,float):
                                cdt_in_field = cam.is_x_y_radius_in_field_not_obstructed(camera,target.xc, target.yc,target.radius)
                                cdt_not_hidden = not cam.is_x_y_in_hidden_zone_all_targets(self.room, camera.id, target.xc, target.yc)
                                cdt_condifdence_high_enough = target.confidence[1] > constants.CONFIDENCE_THRESHOLD or target.confidence == [-1,-1]

                                "Check is the camera can see the target for a given room geometry"

                                if cdt_in_field and cdt_not_hidden and camera.is_active and cdt_condifdence_high_enough and agent.is_active:
                                    "Distance computation"
                                    distance_to_target = np.power(np.power((camera.xc - target.xc), 2)
                                                                  + np.power((camera.yc - target.yc), 2), 0.5)


                                    targetAgentLink.set(agent.id, distance_to_target)


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
            for elem in targetAgentLink.agentDistance_list:
                if targetAgentLink.target_id == target_id and elem.agent_id == agent_id:
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
        self.agentDistance_list = []
        self.number_agent_max = constants.TARGET_NUMBER_OF_AGENT_SHOULD_TRACK
        self.is_lock = False

    def reset(self):
        """
            :description
                set to default values, if unlock
        """
        if not self.is_lock:
            self.agentDistance_list = []

    def set(self, agent_id, distance):
        """
            :description
                set the values to the param, if unlock

            :param
                1. (int) target_id -- to identify the target
                2. (int) agent_id  -- to identify the agents
        """
        if not self.is_lock:
            is_in_list = False
            for elem in self.agentDistance_list:
                is_in_list =  elem.agent_id == agent_id
                if is_in_list:
                    elem.distance = distance
                    list.sort(self.agentDistance_list)
                    break

            if not is_in_list:
                if len(self.agentDistance_list) < self.number_agent_max:
                    self.agentDistance_list.append(AgentDistance(agent_id, distance))
                    list.sort(self.agentDistance_list)

                elif len(self.agentDistance_list) >= self.number_agent_max and self.agentDistance_list[-1].distance > distance:
                        target_to_remove = self.agentDistance_list[-1]
                        self.agentDistance_list.remove(target_to_remove)
                        self.agentDistance_list.append(AgentDistance(agent_id, distance))
                        list.sort(self.agentDistance_list)



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
        return "target " + str(self.target_id) + "linked to " + str([str(elem) for elem in self.agentDistance_list]) + ", locked = " + str(self.is_lock)


class AgentDistance:
    def __init__(self,agent_id,distance):
        self.agent_id = agent_id
        self.distance = distance

    def __eq__(self, other):
        return self.distance == other.distance

    def __lt__(self, other):
        return self.distance < other.distance

    def __gt__(self, other):
        return self.distance > other.distance

    def __str__(self):
        return str(self.agent_id)