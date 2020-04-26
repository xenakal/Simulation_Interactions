import math
import re
from src import constants


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


class ItemEstimator:
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

               :notes
                   fells free to write some comments.
    """

    def __init__(self, time_stamp=None, agent_id=None, agent_signature=None, item_id=None, item_signature=None,
                 item_xc=None, item_yc=None, item_vx=None,
                 item_vy=None, item_ax=None, item_ay=None, item_type=None):
        "Time information"
        self.time_stamp = time_stamp
        self.time_to_compare_to_simulated_data = constants.time_when_target_are_moved

        "Agent - Target link"
        self.agent_id = agent_id
        self.agent_signature = agent_signature
        self.item_id = item_id
        self.item_signature = item_signature

        "Target information"
        self.item_position = [item_xc, item_yc]
        self.item_speeds = [item_vx, item_vy]
        self.item_acceleration = [item_ax, item_ay]
        self.item_type = item_type

    def to_string(self):
        """
            :return / modify vector
                1. (string) s0+s1 -- description of the targetRepresentation

        """
        s1 = "#Timestamp #" + str(self.time_stamp) + "\n"
        s2 = "#From #" + str(self.agent_id) + "#Sig_agent#" + str(self.agent_signature) + "\n"
        s3 = "#item_ID #" + str(self.item_id) + "#Sig_item#" + str(self.item_signature) + "\n"
        s4 = "#item_type #" + str(self.item_type) + "\n"
        s5 = "x: %.02f  y: %.02f" % (self.item_position[0], self.item_position[1]) + "\n"
        s6 = "vx: %.02f  vy: %.02f" % (self.item_speeds[0], self.item_speeds[1]) + "\n"
        s7 = "ax: %.02f  ay: %.02f" % (self.item_acceleration[0], self.item_acceleration[1]) + "\n"
        return str("\n" + s1 + s2 + s3 + s4 + s5 + s6 + s7)

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
            "#Timestamp#|#From#|#Sig_agent#|#item_ID#|#Sig_item#|#item_type#|x:|y:|vx:|vy:|ax:|ay:|#Radius:", s)

        self.time_stamp = float(attribute[1])
        self.agent_id = int(attribute[2])
        self.agent_signature = int(attribute[3])
        self.item_id = int(attribute[4])
        self.item_signature = int(attribute[5])
        self.item_type = int(float(attribute[6]))
        self.item_position = [float(attribute[7]), float(attribute[8])]
        self.item_speeds = [float(attribute[9]), float(attribute[10])]
        self.item_acceleration = [float(attribute[11]), float(attribute[12])]

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
                      'target_ax': self.item_acceleration[0], 'target_ay': self.item_acceleration[1]}
        return csv_format

    def __eq__(self, other):
        cdt1 = self.time_stamp == other.time_stamp
        cdt2 = self.agent_id == other.agent_id
        cdt3 = self.item_id == other.item_id
        cdt4 = self.item_signature == other.item_signature
        cdt5 = self.agent_signature == other.agent_signature
        return cdt1 and cdt2 and cdt3 and cdt4 and cdt5

    def __lt__(self, other):
        return self.time_stamp < other.time_stamp

    def __gt__(self, other):
        return self.time_stamp > other.time_stamp


class TargetEstimator(ItemEstimator):
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
                  9. (int) priority             -- relative priority of target

               :notes
                   fells free to write some comments.
    """

    def __init__(self, time_stamp=None, agent_id=None, agent_signature=None, target_id=None, target_signature=None,
                 target_xc=None, target_yc=None,
                 target_vx=None, target_vy=None, target_ax=None, target_ay=None, target_type=None, target_radius=None,
                 variance_on_estimation=None, priority=constants.TARGET_PRIORITY.MEDIUM):

        super().__init__(time_stamp, agent_id, agent_signature, target_id, target_signature, target_xc, target_yc,
                         target_vx, target_vy, target_ax, target_ay, target_type)
        self.target_radius = target_radius
        if target_vx is None or target_vy is None:
            self.alpha = None
        else:
            self.alpha = math.atan2(target_vy, target_vx)
        self.variance_on_estimation = variance_on_estimation

        # how important tracking this target is
        self.priority = priority

    def set_from_target(self, time_stamp, agent, target):
        "Time information"
        self.time_stamp = time_stamp
        self.time_to_compare_to_simulated_data = constants.time_when_target_are_moved

        "Agent - Target link"
        self.agent_id = agent.id
        self.agent_signature = agent.signature
        self.item_id = target.id
        self.item_signature = target.signature

        "Target information"
        self.item_position = [target.xc, target.yc]
        self.item_speeds = [target.vx, target.vy]
        self.item_acceleration = [target.ax, target.ay]
        self.item_type = target.type
        self.alpha = math.atan2(target.vy, target.vx)
        self.target_radius = target.radius
        self.variance_on_estimation = -1

    def to_string(self):
        """
            :return / modify vector
                1. (string) s0+s1 -- description of the targetRepresentation

        """
        s1 = "#Timestamp #" + str(self.time_stamp) + "\n"
        s2 = "#From #" + str(self.agent_id) + "#Sig_agent#" + str(self.agent_signature) + "\n"
        s3 = "#Target_ID #" + str(self.item_id) + "#Sig_target#" + str(self.item_signature) + "\n"
        s4 = "#Target_type #" + str(self.item_type) + "\n"
        s5 = "x: %.02f  y: %.02f" % (self.item_position[0], self.item_position[1]) + "\n"
        s6 = "vx: %.02f  vy: %.02f" % (self.item_speeds[0], self.item_speeds[1]) + "\n"
        s7 = "ax: %.02f  ay: %.02f" % (self.item_acceleration[0], self.item_acceleration[1]) + "\n"
        s8 = "#Radius: " + str(self.target_radius) + "#alpha: " + str(self.alpha) + "\n"

        return str("\n" + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8)

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
            "#Timestamp#|#From#|#Sig_agent#|#Target_ID#|#Sig_target#|#Target_type#|x:|y:|vx:|vy:|ax:|ay:|#Radius:|#alpha:",
            s)

        self.time_stamp = float(attribute[1])
        self.agent_id = int(attribute[2])
        self.agent_signature = int(attribute[3])
        self.item_id = int(attribute[4])
        self.item_signature = int(attribute[5])
        self.item_type = int(float(attribute[6]))
        self.item_position = [float(attribute[7]), float(attribute[8])]
        self.item_speeds = [float(attribute[9]), float(attribute[10])]
        self.item_acceleration = [float(attribute[11]), float(attribute[12])]
        self.target_radius = float(attribute[13])
        self.alpha = float(attribute[14])

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


class AgentEstimator(ItemEstimator):
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

    def __init__(self, time_stamp=None, agent_id=None, agent_signature=None, agent_camera_id=None,
                 agent_camera_signature=None,
                 agent_camera_xc=None, agent_camera_yc=None, agent_camera_vx=None, agent_camera_vy=None,
                 agent_camera_ax=None,
                 agent_camera_ay=None, error_pos=None, error_speeds=None, error_acc=None, agent_camera_type=None,
                 alpha=None, beta=None,
                 field_depth=None, is_camera_active=None, is_agent_active=None):

        super().__init__(time_stamp, agent_id, agent_signature, agent_camera_id, agent_camera_signature,
                         agent_camera_xc, agent_camera_yc, agent_camera_vx, agent_camera_vy, agent_camera_ax,
                         agent_camera_ay, agent_camera_type)
        self.alpha = alpha
        self.beta = beta
        self.field_depth = field_depth
        self.error_pos = error_pos
        self.error_speed = error_speeds
        self.error_acc = error_acc
        self.is_camera_active = is_camera_active
        self.is_agent_active = is_agent_active

    def set_agent_agent_obeserved(self, time_stamp, agent, agent_to_observed):
        "Time information"
        self.time_stamp = time_stamp
        self.time_to_compare_to_simulated_data = constants.time_when_target_are_moved

        "Agent - Target link"
        self.agent_id = agent.id
        self.agent_signature = agent.signature
        self.item_id = agent_to_observed.id
        self.item_signature = agent_to_observed.signature

        self.is_agent_active = agent_to_observed.is_active
        self.item_type = agent_to_observed.type
        camera = agent_to_observed.camera

        self.item_position = [camera.xc, camera.yc]
        self.item_speeds = [0, 0]  # [ camera.vx,  camera.vy]
        self.item_acceleration = [0, 0]  # [ camera.ax,  camera.ay]

        self.alpha = camera.alpha
        self.beta = camera.beta
        self.field_depth = camera.field_depth
        self.error_pos = camera.std_measurment_error_position
        self.error_speed = camera.std_measurment_error_speed
        self.error_acc = camera.std_measurment_error_acceleration
        self.is_camera_active = camera.is_active

    def to_string(self):
        """
            :return / modify vector
                1. (string) s0+s1 -- description of the targetRepresentation

        """
        s1 = "#Timestamp " + str(self.time_stamp) + "\n"
        s2 = "#From " + str(self.agent_id) + "#Sig_agent_responsible " + str(self.agent_signature) + "\n"
        s3 = "#Agent_camera_ID " + str(self.item_id) + "#Sig_agent_camera " + str(self.item_signature) + "\n"
        s4 = "#Camera_type " + str(self.item_type) + "\n"
        s5 = "#x: %.02f  #y: %.02f #error_pos: %.02f " % (
        self.item_position[0], self.item_position[1], self.error_pos) + "\n"
        s6 = "# vx: %.02f  #vy: %.02f #error_speed: %.02f" % (
        self.item_speeds[0], self.item_speeds[1], self.error_speed) + "\n"
        s7 = "# ax: %.02f  #ay: %.02f #error_acc: %.02f" % (
        self.item_acceleration[0], self.item_acceleration[1], self.error_acc) + "\n"
        s8 = "# alpha: %.02f #beta: %.02f #field_depth: %.02f" % (self.alpha, self.beta, self.field_depth) + "\n"
        s9 = "# agent_is_active: " + str(self.is_agent_active) + " #camera_is_active: " + str(
            self.is_camera_active) + "\n"
        return str("\n" + s1 + s2 + s3 + s4 + s5 + s6 + s7 + s8 + s9)

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
            "#Timestamp|#From|#Sig_agent_responsible|#Agent_camera_ID|#Sig_agent_camera|#Camera_type|#x:|#y:|#error_pos:|#vx:|#vy:|#error_speed:|#ax:|#ay:|#error_acc:|#alpha:|#beta:|#field_depth:|#agent_is_active:|#camera_is_active:",
            s)

        self.time_stamp = float(attribute[1])
        self.agent_id = int(attribute[2])
        self.agent_signature = int(attribute[3])
        self.item_id = int(attribute[4])
        self.item_signature = int(attribute[5])
        self.item_type = int(float(attribute[6]))
        self.item_position = [float(attribute[7]), float(attribute[8])]
        self.error_pos = (float(attribute[9]))
        self.item_speeds = [float(attribute[10]), float(attribute[11])]
        self.error_speed = float(attribute[12])
        self.item_acceleration = [float(attribute[13]), float(attribute[14])]
        self.error_pos = (float(attribute[15]))
        self.alpha = float(attribute[16])
        self.beta = float(attribute[17])
        self.field_depth = float(attribute[18])

        if attribute[19] == "True":
            self.is_agent_active = True
        else:
            self.is_agent_active = False

        if attribute[20] == "True":
            self.is_camera_active = True
        else:
            self.is_camera_active = False

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


class Agent_item_itemEstimator:
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


class Agent_Target_TargetEstimator(Agent_item_itemEstimator):

    def __init__(self):
        super().__init__()

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                    target_xc, target_yc, target_vx, target_vy, target_ax, target_ay, target_type,
                                    target_size, variance_on_estimation=-1):
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
                                              target_signature, target_xc, target_yc, target_vx, target_vy,
                                              target_ax, target_ay, target_type, target_size, variance_on_estimation)
        self.add_itemEstimator(new_targetEstimator)

    def to_csv(self):
        """
             :description
                fill a table with all the memory.to_csv

         """
        csv_fieldnames = constants.TARGET_ESTIMATOR_CSV_FIELDNAMES

        data_to_save = []
        for combination_agent_target in self.Agent_item_itemEstimator_list:
            for targetEstimator in combination_agent_target[2]:
                data_to_save.append(targetEstimator.to_csv())

        return [csv_fieldnames, data_to_save]


class Agent_Agent_AgentEstimator(Agent_item_itemEstimator):
    def __init__(self):
        super().__init__()

    def add_create_agent_estimator(self, time_stamp, agent_id, agent_signature, agent_camera_id, agent_camera_signature,
                                   agent_camera_xc, agent_camera_yc, agent_camera_vx, agent_camera_vy,
                                   agent_camera_ax, agent_camera_ay, error_pos, error_speed, error_acc,
                                   agent_camera_type, alpha, beta, field_depth,
                                   is_camera_active, is_agent_active):

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
        new_agentEstimator = AgentEstimator(time_stamp, agent_id, agent_signature, agent_camera_id,
                                            agent_camera_signature, agent_camera_xc,
                                            agent_camera_yc, agent_camera_vx, agent_camera_vy, agent_camera_ax,
                                            agent_camera_ay, error_pos, error_speed, error_acc, agent_camera_type,
                                            alpha, beta, field_depth,
                                            is_camera_active, is_agent_active)

        self.add_itemEstimator(new_agentEstimator)

    def add_create_agent_estimator_from_agent(self, time_from_estimation, agent, agent_observed):
        new_agentEstimator = AgentEstimator()
        new_agentEstimator.set_agent_agent_obeserved(time_from_estimation, agent, agent_observed)
        self.add_itemEstimator(new_agentEstimator)

    def to_csv(self):
        """
             :description
                fill a table with all the memory.to_csv

         """
        csv_fieldnames = constants.TARGET_ESTIMATOR_CSV_FIELDNAMES

        data_to_save = []
        for combination_agent_agent in self.Agent_item_itemEstimator_list:
            for agentEstimator in combination_agent_agent[2]:
                data_to_save.append(agentEstimator.to_csv())

        return [csv_fieldnames, data_to_save]


class Item_ItemEstimator:
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


class Target_TargetEstimator(Item_ItemEstimator):
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
        super().__init__(current_time)

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                    target_xc, target_yc, target_vx, target_vy, target_ax, target_ay, target_size,
                                    target_type, variance_on_estimation):
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
                                              target_signature, target_xc, target_yc, target_vx, target_vy,
                                              target_ax, target_ay, target_type, target_size, variance_on_estimation)
        self.add_itemEstimator(new_targetEstimator)

    def to_csv(self):
        csv_fieldnames = constants.TARGET_ESTIMATOR_CSV_FIELDNAMES
        data_to_save = []
        self.item_itemEstimator_list.sort()
        for combination_agent_target in self.item_itemEstimator_list:
            for targetEstimator in combination_agent_target[1]:
                data_to_save.append(targetEstimator.to_csv())

        return [csv_fieldnames, data_to_save]


class Agent_AgentEstimator(Item_ItemEstimator):
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
        super().__init__(current_time)

    def add_create_agent_estimator(self, time_stamp, agent_id, agent_signature, agent_camera_id, agent_camera_signature,
                                   agent_camera_xc, agent_camera_yc, agent_camera_vx, agent_camera_vy,
                                   agent_camera_ax, agent_camera_ay, error_pos, error_speed, error_acc,
                                   agent_camera_type, alpha, beta, field_depth,
                                   is_camera_active, is_agent_active):
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
        new_agentEstimator = AgentEstimator(time_stamp, agent_id, agent_signature, agent_camera_id,
                                            agent_camera_signature, agent_camera_xc,
                                            agent_camera_yc, agent_camera_vx, agent_camera_vy, agent_camera_ax,
                                            agent_camera_ay, error_pos, error_speed, error_acc, agent_camera_type,
                                            alpha, beta, field_depth, is_camera_active, is_agent_active)

        self.add_itemEstimator(new_agentEstimator)

    def add_create_agent_estimator_from_agent(self, time_from_estimation, agent, agent_observed):
        new_agentEstimator = AgentEstimator()
        new_agentEstimator.set_agent_agent_obeserved(time_from_estimation, agent, agent_observed)
        self.add_itemEstimator(new_agentEstimator)

    def to_csv(self):
        csv_fieldnames = constants.AGENT_ESTIMATOR_CSV_FIELDNAMES
        data_to_save = []
        self.item_itemEstimator_list.sort()
        for combination_agent_agent in self.item_itemEstimator_list:
            for agentEstimator in combination_agent_agent[1]:
                data_to_save.append(agentEstimator.to_csv())

        return [csv_fieldnames, data_to_save]