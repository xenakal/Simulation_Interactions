import re
import warnings

from src import constants
from src.multi_agent.agent.agent import AgentRepresentation
from src.my_utils.item import Item
from src.multi_agent.elements.target import TargetRepresentation


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
    ItemEstimation = "item_estimation"
    AgentEstimation = "agent_estimation"
    TargetEstimation = "target_estimation"

    keys_string_names = [ItemEstimation, TargetEstimation, AgentEstimation]
    values_class_names = [Item, TargetRepresentation, AgentRepresentation]
    dictionary_item_types = dict(zip(keys_string_names, values_class_names))

# TODO: to_csv in ItemEstimation
# TODO: dans add_estimation de ItemEstimationsList
# TODO: mettre des timestamp dans Item
# TODO: enlever les fonctions get_itemEstimation
#       et remplacer leurs appels par get_itemEstimation_for_target(target_id = -1)
# TODO: improve to_string() if needed


class ItemEstimation:
    """
    Estimation of some items' state.

    Description : Data structure to hold the estimated state of an item.

        :params/attributes
           1. (int) time_stamp               -- time at which the estimation is created
           2. (int) owner_id                 -- id of the owner holding the estimation
           3. (int) owner_signature          -- signature of the owner holding the estimation
           4. (Item) item                    -- item that is estimated
           5. (ItemEstimationType) item_type -- type of item that is estimated

    """

    def __init__(self, time_stamp=None, owner_id=None, owner_agent_signature=None, item=None):
        # Time information
        self.time_stamp = time_stamp
        self.time_to_compare_to_simulated_data = constants.time_when_target_are_moved

        self.owner_id = owner_id
        self.owner_signature = owner_agent_signature

        self.item = item
        self.item_type = None
        for key, value in ItemEstimationType.dictionary_item_types.items():
            if isinstance(self.item, value):
                self.item_type = key

    def to_string(self):
        """
            :return / modify vector
                1. (string) s0+s1 -- description of the targetRepresentation

        """
        s1 = "#ITEM_Timestamp: " + str(self.time_stamp) + " #ITEM_Time_to_compare: " + str(
            self.time_to_compare_to_simulated_data) + "\n"
        s2 = "#ITEM_Owner_id: " + str(self.owner_id) + " #ITEM_Owner_signature: " + str(self.owner_signature) + "\n"
        s3 = "#ITEM_Item_type: " + str(self.item_type) + " #ITEM_Item: " + str(self.item.attributes_to_string())
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
        attribute = re.split(
            "#ITEM_Timestamp:|#ITEM_Time_to_compare:|#ITEM_Owner_id:|#ITEM_Owner_signature:|#ITEM_Item_type:|#ITEM_Item:",
            s)

        self.time_stamp = float(attribute[1])
        self.time_to_compare_to_simulated_data = float(attribute[2])
        self.owner_id = int(attribute[3])
        self.owner_signature = int(attribute[4])
        self.item_type = attribute[5]

        if self.item is None:
            for key, value in ItemEstimationType.dictionary_item_types.items():
                if self.item_type == key:
                    self.item = value()

        self.item.load_from_attributes_to_string(attribute[6])

    # TODO - REFAIRE CA PLUS TARD
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

    def check_if_same_time(self, other):
        return self.time_stamp == other.time_stamp

    def __eq__(self, other):
        cdt1 = self.time_stamp == other.time_stamp
        cdt2 = self.owner_id == other.owner_id
        cdt3 = self.owner_signature == other.owner_signature
        cdt4 = self.item.id == other.item.id
        cdt5 = self.item.signature == other.item.signature
        return cdt1 and cdt2 and cdt3 and cdt4 and cdt5

    def __lt__(self, other):
        return self.time_stamp < other.time_stamp

    def __gt__(self, other):
        return self.time_stamp > other.time_stamp

    def __str__(self):
        return self.to_string()


class ItemEstimationsList:
    """
    List of ItemEstimation objects.

    Description: List to hold all estimations for a single item.

        :params/attributes
            1. (int) item_id            -- id of the item the Estimations are refering to
            2. (list) item_estimations  -- list containing the estimations for the item
    """

    def __init__(self, item_id):
        self.item_estimations = []
        self.item_id = item_id

    def add_estimation(self, item_estimation):
        # TODO: check if item_estimation already inside (use is_in_list_Target_estimator or whatnot)
        self.item_estimations.append(item_estimation)

    def sort(self):
        self.item_estimations.sort(key=lambda x: x.time_stamp, reverse=True)

    def get_itemEstimation_at_time(self, time):
        for estimation in self.item_estimations:
            if estimation.timeStamp == time:
                return estimation
        return None

    def __len__(self):
        return len(self.item_estimations)


class SingleOwnerMemories:
    """
    Stores previous Estimations for a number of items.

    Description : Data structure to hold the previous estimations of each recorded item. It is meant to be used by
    a single owner, to hold all the previous positions of all the targets he has seen.

        :params
             1. (int) init_time                       -- time of initialization

        :attibutes
             1. (int) current_time                    -- time of newest addition used as a reference when adding new
                                                         estimations or when cleaning the list
             2. (list) items_already_discovered       -- [item.id,...] list of items for which at least one entry exists
                                                         in
             3. (list) items_estimations_list         -- [ItemEstimationList, ...] list of itemEstimationsList
             4. (int) owner_id                        -- id of owner of the object
    """

    def __init__(self, owner_id, init_time=0):
        self.current_time = init_time
        self.items_discovered = []
        self.items_estimations_lists = []
        self.owner_id = owner_id

    def update_ItemEstimations_list(self, item_id):
        """
        :description
            Creates an ItemEstimationsList for the item item_id

        :params
            1. (int) target_id -- id of the item for which a list is created
         """

        if item_id not in self.items_discovered:
            self.items_discovered.append(item_id)
            self.items_estimations_lists.append(ItemEstimationsList(item_id))

    def add_create_itemEstimation(self, time_stamp, owner_id, owner_signature, item):
        new_ItemEstimation = ItemEstimation(time_stamp=time_stamp, owner_id=owner_id,
                                            owner_agent_signature=owner_signature, item=item)
        self.add_itemEstimation(new_ItemEstimation)

    def add_itemEstimation(self, item_estimation):
        """
        :description
           Adds the itemEstimation to the list if doesn't exist.

        :params
           1. (TargetEstimator) TargetEstimation           -- TargetEstimation to be added in the list

        :return/modify
              if    already in the list no action
             else  add TargetEstimation in to the correspoinding list
        """
        self.update_ItemEstimations_list(item_estimation.item.id)

        for item_estimation_list in self.items_estimations_lists:
            if item_estimation_list.item_id == item_estimation.item.id:
                item_estimation_list.add_estimation(item_estimation)

    def add_itemEstimationsList(self, itemEstimationsList):
        if itemEstimationsList.item_id in self.items_discovered:
            warnings.warn("Adding estimationsList for target already existing in SingleOwnerMemory()")
        self.items_estimations_lists.append(itemEstimationsList)

    def sort(self):
        """
        :description
            sort all TargetEstimator based on time_stamp
        """
        for item_estimations_list in self.items_estimations_lists:
            item_estimations_list.sort()

    def get_estimations_at_time(self, time):
        ret_estimations_list = []
        for estimation_list in self.items_estimations_lists:
            estimation = estimation_list.get_itemEstimation_at_time(time)
            if estimation: ret_estimations_list.append(estimation)
        return ret_estimations_list

    def get_estimation_at_time_for_target(self, time, target_id):
        for estimation_list in self.items_estimations_lists:
            if estimation_list.owner_id == target_id or target_id == -1:
                return estimation_list.get_itemEstimation_at_time(time)

    def get_item_list(self, item_id):
        """
        :description
            Get the ItemEstimationsList for a given item id.

        :param
           1. (int) target_id         -- id of item whose estimations list is needed

        :return/modify vector
            if not found              -- []
            else                      -- list of ItemEstimation
       """

        for item_estimations_list in self.items_estimations_lists:
            if item_estimations_list.item_id == item_id:
                return item_estimations_list.item_estimations
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
        for item_estimations_list in self.items_estimations_lists:
            if item_estimations_list.owner_id == item_id:
                return len(item_estimations_list.item_estimations)
        return -1

class MultipleOwnerMemories:
    """
          Stores previous estimations for a number of agents and a number of targets.

          Description: Data structure that holds a SingleOwnerMemories per recorded owner.

              :params
                  1. (int) current_time   -- reference time, to add estimator or clean the list


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
        self.agents_and_items_discovered = [] # TODO: voir si on a besoin de ca
        self.single_owners_list = []

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

        if not ((agent_id, item_id) in self.agents_and_items_discovered):
            self.agents_and_items_discovered.append((agent_id, item_id))
            for single_owner_list in self.single_owners_list:
                if single_owner_list.owner_id == agent_id:
                    single_owner_list.update_estimations_list(item_id)
                    return

            new_single_owner = SingleOwnerMemories(agent_id)
            new_single_owner.update_ItemEstimations_list(item_id)
            self.single_owners_list.append(new_single_owner)

    def add_create_itemEstimation(self, time_stamp, owner_id, owner_signature, item):
        new_ItemEstimation = ItemEstimation(time_stamp, owner_id, owner_signature, item)
        self.add_itemEstimation(new_ItemEstimation)

    def add_itemEstimation(self, itemEstimation_to_add):
        """
        :description
            Adds the itemEstimation to the corresponding single owner.

        :param
            1. (ItemEstimation) itemEstimation_to_add       -- itemEstimation to be added.
        """
        self.update_estimator_list(itemEstimation_to_add.owner_id, itemEstimation_to_add.item.id)
        for single_owner_list in self.single_owners_list:
            if single_owner_list.owner_id == itemEstimation_to_add.owner_id:
                single_owner_list.add_itemEstimation(itemEstimation_to_add)

    def sort(self):
        """
        :description
              sort all single owners based on time_stamp
        """
        for element in self.single_owners_list:
            element.sort()

    def get_agent_item_list(self, target_id, agent_id):
        """
        :description
           acess the ItemEstimationList for a given Target-Agent combination

        :param
            1. (int) agent_id         -- numeric value to identify the agent
            2. (int) target_id        -- numeric value to identify the target
        """
        for element in self.single_owners_list:
            if element.owner_id == agent_id:
                return element.get_item_list(target_id)

    def get_itemEstimations_time_t(self, time):
        """
         :description
               retrun the TargetEstimator list for a given time

        :param
            1. (int) time         --  time_stamp from the TargetEstimator to be found

        :return / modify vector
            if not found              -- empty list
            else                      -- TargetEstimator list
        """
        ret_estimations_list = []
        for single_owner_list in self.single_owners_list:
            ret_estimations_list += single_owner_list.get_estimations_at_time(time)
        return ret_estimations_list

    def get_itemEstimation_time_item_agent(self, time, target_id, agent_id):
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
                  4. (list) Agent_Target_TargetEstimator_list    -- [[agent.id, target.id, [TargetEstimator]], ...]
        """
        ret_estimations_list = []
        for single_owner_list in self.single_owners_list:
            if agent_id == -1 or agent_id == single_owner_list.owner_id:
                ret_estimations_list += single_owner_list.get_estimations_at_time_for_target(time, target_id)
        return ret_estimations_list

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
        for single_owner_list in self.single_owners_list:
            if single_owner_list.owner_id == agent_id:
                return single_owner_list.get_item_stat(target_id)
        return -1

    def to_string(self):
        """
        :return / modify vector
            1. (string) s -- description of the  self.Agent_Target_TargetEstimator_list
        """
        s = "Memory \n"
        for single_owner in self.single_owners_list:
            for estimation_list in single_owner.items_estimations_lists:
                for estimation in estimation_list:
                    s += estimation.to_string()
        return s

    def statistic_to_string(self):
        """
        :return / modify vector
            1. (string) s -- description of the  self.Agent_Target_TargetEstimator_list
        """
        s = "Memory " + str(self.current_time) + "\n"
        for single_owner in self.single_owners_list:
            s += "Owner: " + str(single_owner.owner_id)
            for estimation_list in single_owner.items_estimations_lists:
                s += "Item: " + str(estimation_list.item_id) + "#memories" + str(len(estimation_list))
        return s

