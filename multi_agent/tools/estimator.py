import numpy as np
import random
import math
import re
import constants
from my_utils.line import *
from multi_agent.elements.target import TargetType


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


class TargetEstimator:
    """
           Class TargetEstimator.

           Description : Conserve the data relative to a agent and a target for a given time

               :param
                  1. (int) time_stamp           -- time to which the estimator is created
                  2. (int) agent_id             -- numerical value to identify the agent
                  3. (int) agent_signature      -- numerical value to identify the agent
                  4. (int) target_id            -- numerical value to identify the target
                  5. (int) target_signature     -- numerical value to identify the target
                  6. (int) target_xc            -- x value of the center of the targetRepresentation
                  7. (int) target_yc            -- y value of the center of the targetRepresentation
                  8. (int) target_size          -- radius from the center
                  9. (int) target_position      -- [x,y] values of the center of the targetRepresentation

               :attibutes
                  1. (int) time_stamp           -- time to which the estimator is created
                  2. (int) agent_id             -- numerical value to identify the agent
                  3. (int) agent_signature      -- numerical value to identify the agent
                  4. (int) target_id            -- numerical value to identify the target
                  5. (int) target_signature     -- numerical value to identify the target
                  6. (int) target_position      -- [x,y] values of the center of the targetRepresentation
                  7. (int) target_type          -- identification from the Target.type
                  8. (int) target_size          -- radius from the center

               :notes
                   fells free to write some comments.
    """

    def __init__(self, time_stamp, agent_id, agent_signature, target_id, target_signature, target_xc, target_yc,
                 target_radius, target_type=TargetType.UNKNOWN):
        "Time information"
        self.time_stamp = time_stamp

        "Agent - Target link"
        self.agent_id = agent_id
        self.agent_signature = agent_signature
        self.target_id = target_id
        self.target_signature = target_signature

        "Target information"
        self.target_position = [target_xc, target_yc]
        self.target_type = target_type
        self.target_radius = target_radius

    def to_string(self):
        """
            :return / modify vector
                1. (string) s0+s1 -- description of the targetRepresentation

        """
        s1 = "#Timestamp #" + str(self.time_stamp) + "\n"
        s2 = "#From #" + str(self.agent_id) + "#Sig_agent#" + str(self.agent_signature) + "\n"
        s3 = "#Target_ID #" + str(self.target_id) + "#Sig_target#" + str(self.target_signature) + "\n"
        s4 = "#Target_type #" + str(self.target_type) + "x: " + str(self.target_position[0]) + " y: " + str(
            self.target_position[1]) + "\n"
        s5 = "#Radius: " + str(self.target_radius) + "\n"
        return str("\n" + s1 + s2 + s3 + s4 + s5 + "\n")

    def to_csv(self):
        """
            :return / modify vector
                1. easy representation to save data in cvs file
        """
        csv_format = {'time_stamp': self.time_stamp, 'agent_id': self.agent_id,'agent_signature': self.agent_signature,
               'target_id': self.target_id,'target_signature': self.target_signature,'target_type': self.target_type,
               'target_x':self.target_position[0],'target_y':self.target_position[1],'target_radius':self.target_radius}
        return csv_format


    def parse_string(self, s):
        """
            :params
                1.(string) s -- string representing a TargetEstimator, use the method to_string().

             :return / modify vector
                1. Set all the attributes from self to the values described in the sting representation.

        """

        s = s.replace("\n", "")
        s = s.replace(" ", "")

        attribute = re.split("#Timestamp#|#From#|#Sig_agent#|#Target_ID#|#Sig_target#|#Target_type#|x:|y:|#Radius:", s)

        self.time_stamp = int(attribute[1])
        self.agent_id = int(attribute[2])
        self.agent_signature = int(attribute[3])
        self.target_id = int(attribute[4])
        self.target_signature = int(attribute[5])
        self.target_type = int(attribute[6])
        self.target_position = [float(attribute[7]), float(attribute[8])]
        self.target_radius = int(attribute[9])

    def __eq__(self, other):
        cdt1 = self.time_stamp == other.time_stamp
        cdt2 = self.agent_id == other.agent_id
        cdt3 = self.target_id == other.target_id
        cdt4 = self.target_signature == other.target_signature
        cdt5 = self.agent_signature == other.agent_signature
        return cdt1 and cdt2 and cdt3 and cdt4 and cdt5

    def __lt__(self, other):
        return self.time_stamp < other.time_stamp

    def __gt__(self, other):
        return self.time_stamp > other.time_stamp


class Agent_Target_TargetEstimator:
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

    def __init__(self, n_times=20, current_time=0):
        self.times = n_times
        self.current_time = current_time
        self.Agent_Target_already_discovered_list = []
        self.Agent_Target_TargetEstimator_list = []  # tableau de taille #agents*#targets

    def update_estimator_list(self, agent_id, target_id):
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

        if not ((agent_id, target_id) in self.Agent_Target_already_discovered_list):
            self.Agent_Target_already_discovered_list.append((agent_id, target_id))
            self.Agent_Target_TargetEstimator_list.append([agent_id, target_id, []])

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                    target_xc, target_yc, target_size, target_type):
        """
            :description
                Creates an estimator and adds it to the list if doesn't exist yet.

            :param
                 1. (int) time_stamp           -- time to which the estimator is created
                 2. (int) agent_id             -- numeric value to identify the agent
                 3. (int) agent_signature      -- numeric value to identify the agent
                 4. (int) target_id            -- numeric value to identify the target
                 5. (int) target_id            -- numeric value to identify the target
                 6. (int) target_xc            -- x value of the center of the targetRepresentation
                 7. (int) target_yc            -- y value of the center of the targetRepresentation
                 8. (int) target_size          -- radius from the center

            :return / modify vector
                fills the list  Agent_Target_TargetEstimator_list with a new TargetEstimator for the Target and Agent given

        """

        new_targetEstimator = TargetEstimator(time_from_estimation, agent_id, agent_signature, target_id,
                                              target_signature, target_xc, target_yc, target_size, target_type)
        self.add_target_estimator(new_targetEstimator)

    def add_target_estimator(self, targetEstimator_to_add):
        """
            :description
                Adds it to the list if doesn't exist yet.

            :param
                1. (int) time_stamp           -- time to which the estimator is created

            :return / modify vector
                fills the list  Agent_Target_TargetEstimator_list with a new TargetEstimator for the Target and Agent given
        """

        self.update_estimator_list(targetEstimator_to_add.agent_id, targetEstimator_to_add.target_id)

        for element in self.Agent_Target_TargetEstimator_list:
            if is_corresponding_TargetEstimator(targetEstimator_to_add.agent_id, targetEstimator_to_add.target_id,
                                                element):
                if targetEstimator_to_add not in element[2]:
                    element[2].append(targetEstimator_to_add)

    def sort_TargetEstimator(self):
        """
            :description
                  sort all TargetEstimator based on time_stamp

        """
        for element in self.Agent_Target_TargetEstimator_list:
            element[2].sort()

    def get_Agent_Target_list(self, target_id, agent_id):
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
        for element in self.Agent_Target_TargetEstimator_list:
            if element[0] == agent_id and element[1] == target_id:
                return element[2]
        return []

    def get_TargetEstimator_time_t(self, time):
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
        for element in self.Agent_Target_TargetEstimator_list:
            for estimator in element[2]:
                if estimator.timeStamp == time:
                    TargetEstimator_list_time_t.append(estimator)
        return TargetEstimator_list_time_t

    def get_TargetEstimator_time_Target_Agent(self, time, target_id, agent_id):
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
        for element in self.Agent_Target_TargetEstimator_list:
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

    def get_Agent_Target_stat(self, target_id, agent_id):
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

        for element in self.Agent_Target_TargetEstimator_list:
            if element[0] == agent_id and element[1] == target_id:
                return len(element[2])
        return -1

    def to_string(self):
        """
            :return / modify vector
                1. (string) s -- description of the  self.Agent_Target_TargetEstimator_list

        """

        s = "Memory \n"
        for element in self.Agent_Target_TargetEstimator_list:
            for estimator in element[2]:
                s = s + estimator.to_string()
        return s

    def to_csv(self):
        """
             :description
                fill a table with all the memory.to_csv

         """
        csv_fieldnames = constants.TARGET_ESTIMATOR_CSV_FIELDNAMES

        data_to_save = []
        for combination_agent_target in self.Agent_Target_TargetEstimator_list:
            for targetEstimator in combination_agent_target[2]:
                data_to_save.append(targetEstimator.to_csv())

        return [csv_fieldnames,data_to_save]

    def statistic_to_string(self):
        """
            :return / modify vector
                1. (string) s -- description of the  self.Agent_Target_TargetEstimator_list

        """

        s = "Memory " + str(self.current_time) + "\n"
        for element in self.Agent_Target_TargetEstimator_list:
            s = s + "Agent : " + str(element[0]) + " Target :" + str(element[1]) + "# memories " + str(
                len(element[2])) + "\n"
        return s


class Target_TargetEstimator:
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

    def __init__(self, n_times=5, current_time=0):
        self.times = n_times
        self.current_time = current_time
        self.Target_already_discovered_list = []
        self.Target_TargetEstimator_list = []

    def update_TargetEstimator_list(self, target_id):
        """
             :description
                 add every combination Target in the Target_list

             :param
                 1. (int) target_id -- id of the target

             :return / modify vector
                 if    already in the list no action
                 else  add the combination in Target_list and create a new cell in Target_TargetEstimator_list
         """

        if target_id not in self.Target_already_discovered_list:
            self.Target_already_discovered_list.append(target_id)
            self.Target_TargetEstimator_list.append([target_id, []])

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                    target_xc, target_yc, target_size, target_type):
        """
            :description
                Creates an estimator and adds it to the list if doesn't exist yet.

            :param
                 1. (int) time_stamp           -- time to which the estimator is created
                 2. (int) agent_id             -- numeric value to identify the agent
                 3. (int) agent_signature      -- numeric value to identify the agent
                 4. (int) target_id            -- numeric value to identify the target
                 5. (int) target_id            -- numeric value to identify the target
                 6. (int) target_xc            -- x value of the center of the targetRepresentation
                 7. (int) target_yc            -- y value of the center of the targetRepresentation
                 8. (int) target_size          -- radius from the center

            :return / modify vector
                fills the list  Agent_Target_TargetEstimator_list with a new TargetEstimator for the Target and Agent given

        """

        new_targetEstimator = TargetEstimator(time_from_estimation, agent_id, agent_signature, target_id,
                                              target_signature, target_xc, target_yc, target_size, target_type)
        self.add_TargetEstimator(new_targetEstimator)

    def add_TargetEstimator(self, targetEstimator):
        """
            :description
               Adds it to the list if doesn't exist yet.

            :param
               1. (TargetEstimator) TargetEstimator           -- TargetEstimator to be added in the list

            :return / modify vector
                  if    already in the list no action
                 else  add TargetEstimator in Target_TargetEstimator_list
        """
        self.update_TargetEstimator_list(targetEstimator.target_id)

        for element in self.Target_TargetEstimator_list:
            if element[0] == targetEstimator.target_id:
                if not is_in_list_TargetEstimator(element[1], targetEstimator):
                    element[1].append(targetEstimator)

    def sort(self):
        """
            :description
                sort all TargetEstimator based on time_stamp

        """
        for element in self.Target_TargetEstimator_list:
            element[1].sort()

    def get_Target_list(self, target_id):
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
        for element in self.Target_TargetEstimator_list:
            if element[0] == target_id:
                return element[1]
        return []

    def get_Target_stat(self, target_id):
        """
           :description
                to know how many targetEstimator are stored for a given Agent and Target

           :param
                1. (int) target_id    -- numeric value to identify the target

            :return / modify vector
               if not found              -- -1
               else                      --  lenght of TargetEstimator list
        """
        for element in self.Target_TargetEstimator_list:
            if element[0] == target_id:
                return len(element[1])
        return -1

    def to_csv(self):

        csv_fieldnames = constants.TARGET_ESTIMATOR_CSV_FIELDNAMES
        data_to_save = []
        self.Target_TargetEstimator_list.sort()
        for combination_agent_target in self.Target_TargetEstimator_list:
            for targetEstimator in combination_agent_target[1]:
                data_to_save.append(targetEstimator.to_csv())

        return [csv_fieldnames,data_to_save]