import math
import re
from src import constants
from src.multi_agent.agent.agent import AgentRepresentation
from src.multi_agent.elements.target import TargetRepresentation


def is_corresponding_TargetEstimator(agent_id, target_id, targetEstimator):
    """
        :param
            1. (int) agent_id                    -- attributes from the desire TargetEstimator
            2. (int) target_id                   -- attributes from the desire TargeEstimator
            3. (TargetEstimator) TargetEstimator -- object

        :return / modify vector
            1. (bool) condition      -- true if the target estimator is found

    """

    return targetEstimator[0] == agent_id and targetEstimator[1] == target_id


def is_in_list_TargetEstimator(list_TargetEstimator, targetEstimator):
    """
        :param
            1. (list) list_TargetEstimator           -- list of targetEstimator
            2. (TargetEstimator) TargetEstimator     -- targetEstimator we want to find

        :return / modify vector
            1. (bool) condition      -- true if the target estimator is found

    """
    for estimator in list_TargetEstimator:
        if estimator == targetEstimator:
            return True
    return False



class ItemEstimationType:
    keys_string_names = ["target_estimation", "agent_estimation"]
    values_class_names = [TargetRepresentation, AgentRepresentation]
    dictionary_item_types = dict(zip(keys_string_names, values_class_names))



class ItemEstimation:
    """
           Class TargetEstimator.

           Description : Conserve the data relative to a agent and a target for a given time

               :param
                  1. (int) time_stamp           -- time to which the estimator is created
                  2. (int) agent_id             -- numerical value to identify the agent
                  3. (int) agent_signature      -- numerical value to identify the agent


               :attibutes
                  1. (int) time_stamp           -- time to which the estimator is created
                  2. (int) agent_id             -- numerical value to identify the agent
                  3. (int) agent_signature      -- numerical value to identify the agent

               :notes
                   fells free to write some comments.
    """

    def __init__(self, time_stamp=None, agent_id=None, owner_agent_signature=None, item = None):
        "Time information"
        self.time_stamp = time_stamp
        self.time_to_compare_to_simulated_data = constants.time_when_target_are_moved

        "Agent - Target link"
        self.owner_id = agent_id
        self.owner_signature = owner_agent_signature

        self.item = item
        for key,value in ItemEstimationType.dictionary_item_types.items():
            if isinstance(self.item,value):
                self.item_type = key

    def to_string(self):
        """
            :return / modify vector
                1. (string) s0+s1 -- description of the targetRepresentation

        """
        s1 = "#Timestamp: " + str(self.time_stamp) + " #Time_to_compare: " + str(self.time_to_compare_to_simulated_data) + "\n"
        s2 = "#Owner_id: " + str(self.owner_id) + " #Owner_signature: " + str(self.owner_signature) + "\n"
        s3 = "#Item_type: " +  str(self.item_type) + " #Item: " + str(self.item)
        return str("\n" + s1 + s2 + s3 + "\n")



    def parse_string(self, s):
        """
            :params
                1.(string) s -- string representing a TargetEstimator, use the method to_string().

             :return / modify vector
                1. Set all the attributes from self to the values described in the sting representation.

        """
        s = s.replace("\n", "")
        s = s.replace(" ", "")
        attribute = re.split("#Timestamp:|#Time_to_compare:|#Owner_id:|#Owner_signature:|#Item_type:|#Item:",s)

        self.time_stamp = float(attribute[1])
        self.time_to_compare_to_simulated_data = float(attribute[2])
        self.owner_id = int(attribute[3])
        self.owner_signature = int(attribute[4])
        self.item_type = attribute[5]

        new_item = ItemEstimationType.dictionary_item_types[self.item_type]()
        new_item.parse_string(attribute[6])
        self.item = new_item


    #TODO - REFAIRE CA PLUS TARD
    '''
    def to_csv(self):
        """
            :return / modify vector
                1. easy representation to save data in cvs file
        """
        csv_format = {'time_to_compare': self.time_to_compare_to_simulated_data, 'time_stamp': self.time_stamp,
                      'agent_id': self.owner_id, 'agent_signature': self.owner_signature,
                      'target_id': self.item_id, 'target_signature': self.item_signature,
                      'target_type': self.item_type,
                      'target_x': self.item_position[0], 'target_y': self.item_position[1],
                      'target_vx': self.item_speeds[0], 'target_vy': self.item_speeds[1],
                      'target_ax': self.item_acceleration[0], 'target_ay': self.item_acceleration[1]}
        return csv_format
        
          def to_csv(self):
        """
            :return / modify vector
                1. easy representation to save data in cvs file
        """
        csv_format = {'time_to_compare': self.time_to_compare_to_simulated_data, 'time_stamp': self.time_stamp,
                      'agent_id': self.agent_id, 'agent_signature': self.agent_signature,
                      'target_id': self.item_id, 'target_signature': self.item_signature,
                      'target_type': self.item_type,
                      'target_x': self.item_position[0], 'target_y': self.item_position[1],
                      'target_vx': self.item_speeds[0], 'target_vy': self.item_speeds[1],
                      'target_ax': self.item_acceleration[0], 'target_ay': self.item_acceleration[1],
                      'target_radius': self.target_radius, 'target_alpha': self.alpha}
        return csv_format
        
            def to_csv(self):
        """
            :return / modify vector
                1. easy representation to save data in cvs file
        """
        csv_format = {'time_to_compare': self.time_to_compare_to_simulated_data, 'time_stamp': self.time_stamp,
                      'agent_id': self.agent_id, 'agent_signature': self.agent_signature,
                      'camera_id': self.item_id, 'camera_signature': self.item_signature,
                      'camera_type': self.item_type,
                      'camera_x': self.item_position[0], 'camera_y': self.item_position[1],
                      'camera_vx': self.item_speeds[0], 'camera_vy': self.item_speeds[1],
                      'camera_ax': self.item_acceleration[0], 'camera_ay': self.item_acceleration[1],
                      'alpha': self.alpha, 'beta': self.beta,'field_depth':self.field_depth,
                      'is_agent_active': self.is_agent_active,'is_camera_active':self.is_camera_active}
        return csv_format

    '''

    def check_if_same_time(self,other):
        return self.time_stamp == other.time_stamp

    def __eq__(self, other):
        cdt1 = self.time_stamp == other.time_stamp
        cdt2 = self.owner_id == other.agent_id
        cdt3 = self.owner_signature == other.agent_signature
        return cdt1 and cdt2 and cdt3

    def __lt__(self, other):
        return self.time_stamp < other.time_stamp

    def __gt__(self, other):
        return self.time_stamp > other.time_stamp

    def __str__(self):
        return self.to_string()

class MultipleOwnerMemories:
    """
          Class TargetEstimatorList.

          Description : List collecting all the infomations coming from every agentCam for every Target

              :params
                  1. (int) n_times        -- oldest time that we want to keep in the list
                  2. (int) current_time   -- reference time, to add estimator or clean the list


              :attibutes
                  1. (int) times                                 -- oldest time that we want to keep in the list
                  2. (int) current_times                         -- reference time, to add estimator or clean the list (here time in the room)
                  3. (list) Agent_Target_already_discovered_list -- [(agent.id,target.id),...], link between target and agent already created
                  4. (list) Agent_Target_TargetEstimator_list    -- [[agent.id, target.id, [TargetEstimator]], ...]

              :notes
                  fells free to write some comments.
      """

    def __init__(self, current_time=0):
        self.current_time = current_time
        self.Agent_item_already_discovered_list = []
        self.Agent_item_itemEstimator_list = []  # tableau de taille #agents*#targets

    def update_estimator_list(self, agent_id, item_id):
        """
            :description
                add every combination Agent-Target in the Agent_Target_list

            :param
                1. (int) agent_id  -- id of the agent
                2. (int) target_id -- id of the target

            :return / modify vector
                if    already in the list no action
                else  add the combination in Agent_Target_list and create a new cell in Agent_Target_TargetEstimator_list
        """

        if not ((agent_id, item_id) in self.Agent_item_already_discovered_list):
            self.Agent_item_already_discovered_list.append((agent_id, item_id))
            self.Agent_item_itemEstimator_list.append([agent_id, item_id, []])

    def add_itemEstimator(self, itemEstimator_to_add):
        """
            :description
                Adds it to the list if doesn't exist yet.

            :param
                1. (int) time_stamp           -- time to which the estimator is created

            :return / modify vector
                fills the list  Agent_Target_TargetEstimator_list with a new TargetEstimator for the Target and Agent given
        """

        self.update_estimator_list(itemEstimator_to_add.agent_id, itemEstimator_to_add.item_id)

        for element in self.Agent_item_itemEstimator_list:
            if is_corresponding_TargetEstimator(itemEstimator_to_add.agent_id, itemEstimator_to_add.item_id,
                                                element):
                if itemEstimator_to_add not in element[2]:
                    element[2].append(itemEstimator_to_add)

    def sort_itemEstimator(self):
        """
            :description
                  sort all TargetEstimator based on time_stamp

        """
        for element in self.Agent_item_itemEstimator_list:
            element[2].sort()

    def get_Agent_item_list(self, target_id, agent_id):
        """
            :description
               acess the TargetEstimator_list for a given Target-Agent combination

            :param
                1. (int) agent_id         -- numeric value to identify the agent
                2. (int) target_id        -- numeric value to identify the target

            :return / modify vector
                if not found              -- empty list
                else                      -- TargetEstimator list

        """
        for element in self.Agent_item_itemEstimator_list:
            if element[0] == agent_id and element[1] == target_id:
                return element[2]
        return []

    def get_itemEstimator_time_t(self, time):
        """
             :description
                   retrun the TargetEstimator list for a given time

            :param
                1. (int) time         --  time_stamp from the TargetEstimator to be found

            :return / modify vector
                if not found              -- empty list
                else                      -- TargetEstimator list

        """
        TargetEstimator_list_time_t = []
        for element in self.Agent_item_itemEstimator_list:
            for estimator in element[2]:
                if estimator.timeStamp == time:
                    TargetEstimator_list_time_t.append(estimator)
        return TargetEstimator_list_time_t

    def get_TargetEstimator_time_item_Agent(self, time, target_id, agent_id):
        """
            :description
               to get a TargetEstimator list for a given time, Agent and Target

            :param
                1. (int) time         --  time_stamp from the TargetEstimator to be found
                2. (int) agent_id     -- numeric value to identify the agent
                3. (int) target_id    -- numeric value to identify the target

            :return / modify vector
                if not found              -- empty list
                else                      -- TargetEstimator list

        """
        TargetEstimator_search = []
        cdt0 = cdt1 = cdt2 = True
        for element in self.Agent_item_itemEstimator_list:
            if target_id != -1:
                cdt0 = element[0] == agent_id
            if agent_id != -1:
                cdt1 = element[1] == target_id

            for estimator in element[2]:
                if time != -1:
                    cdt2 = estimator.timeStamp == time
                if cdt0 and cdt1 and cdt2:
                    TargetEstimator_search.append(estimator)
        return TargetEstimator_search

    def get_Agent_item_stat(self, target_id, agent_id):
        """
            :description
                to know how many targetEstimator are stored for a given Agent and Target

            :param
                1. (int) agent_id     -- numeric value to identify the agent
                2. (int) target_id    -- numeric value to identify the target

            :return / modify vector
                if not found              -- -1
                else                      -- length of the TargetEstimator list
        """

        for element in self.Agent_item_itemEstimator_list:
            if element[0] == agent_id and element[1] == target_id:
                return len(element[2])
        return -1

    def to_string(self):
        """
            :return / modify vector
                1. (string) s -- description of the  self.Agent_Target_TargetEstimator_list

        """

        s = "Memory \n"
        for element in self.Agent_item_itemEstimator_list:
            for estimator in element[2]:
                s = s + estimator.to_string()
        return s

    def statistic_to_string(self):
        """
            :return / modify vector
                1. (string) s -- description of the  self.Agent_Target_TargetEstimator_list

        """

        s = "Memory " + str(self.current_time) + "\n"
        for element in self.Agent_item_itemEstimator_list:
            s = s + "Agent : " + str(element[0]) + " Target :" + str(element[1]) + "# memories " + str(
                len(element[2])) + "\n"
        return s


class SingleOwnerMemories:
    """
           Class FusionEstimatorList.

           Description : Simplification from Agent_Target_TargetEstimatorList to one Agent only.

               :params
                    1. (int) times                          -- oldest time that we want to keep in the list
                    2. (int) current_times                  -- reference time, to add estimator or clean the list (here time in the room)

               :attibutes
                    1. (int) times                           -- oldest time that we want to keep in the list
                    2. (int) current_times                   -- reference time, to add estimator or clean the list (here time in the room)
                    3. (list) Target_already_discovered_list -- [target.id,...], link between target and agent already created
                    4. (list) Target_TargetEstimator_list    -- [[target.id, [TargetEstimator]], ...]


               :notes
                   fells free to write some comments.
    """

    def __init__(self, current_time=0):
        self.current_time = current_time
        self.item_already_discovered_list = []
        self.item_itemEstimator_list = []

    def update_ItemEstimator_list(self, item_id):
        """
             :description
                 add every combination Target in the Target_list

             :param
                 1. (int) target_id -- id of the target

             :return / modify vector
                 if    already in the list no action
                 else  add the combination in Target_list and create a new cell in Target_TargetEstimator_list
         """

        if item_id not in self.item_already_discovered_list:
            self.item_already_discovered_list.append(item_id)
            self.item_itemEstimator_list.append([item_id, []])

    def add_itemEstimator(self, itemEstimator):
        """
            :description
               Adds it to the list if doesn't exist yet.

            :param
               1. (TargetEstimator) TargetEstimator           -- TargetEstimator to be added in the list

            :return / modify vector
                  if    already in the list no action
                 else  add TargetEstimator in Target_TargetEstimator_list
        """
        self.update_ItemEstimator_list(itemEstimator.item_id)

        for element in self.item_itemEstimator_list:
            if element[0] == itemEstimator.item_id:
                if not is_in_list_TargetEstimator(element[1], itemEstimator):
                    element[1].append(itemEstimator)

    def sort(self):
        """
            :description
                sort all TargetEstimator based on time_stamp

        """
        for element in self.item_itemEstimator_list:
            element[1].sort()

    def get_item_list(self, item_id):
        """
            :description
               to know how many targetEstimator are stored for a given Agent and Target

            :param
               1. (int) target_id    -- numeric value to identify the target

            :return / modify vector
                if not found              -- []
                else                      -- TargetEstimator list
       """

        """ Returns the list of TargetEstimators for the target provided in the argument. """
        for element in self.item_itemEstimator_list:
            if element[0] == item_id:
                return element[1]
        return []

    def get_item_stat(self, item_id):
        """
           :description
                to know how many targetEstimator are stored for a given Agent and Target

           :param
                1. (int) target_id    -- numeric value to identify the target

            :return / modify vector
               if not found              -- -1
               else                      --  lenght of TargetEstimator list
        """
        for element in self.item_itemEstimator_list:
            if element[0] == item_id:
                return len(element[1])
        return -1


