from multi_agent.estimator import *


class Memory:
    """
    Class with multiple arrays that store information about target.

    Params:
        agentID      -- agent to which the memory is associated
        current_time -- time to be updated so that the memory is on time with the room.
        nTime        -- number of memories over time that should be stored (not use yet)

        ([[agent.id, target.id, [TargetEstimator]],...]) memory_all_agent -- list of every information that the agent has (multiple position per target)
        - either gather on the picture with YOLO
        - or received from an other agent
        going from memory_all_agent to memory_agent with the function combine_data

        ([[target.id,[TargetEstimator]],...]) memory_agent -- estimation of the disposition in the room. (only one position per target)
        (now the agent keep just what he sees ! TO BE MODIFY with a Kalman filet for ex !)
        the prediction should be based on that information
    """

    def __init__(self, agentID, nTime=20, current_time=0):
        self.id = agentID
        self.time = current_time
        self.nTime = nTime
        self.memory_all_agent = TargetEstimatorList()
        self.memory_agent = FusionEstimatorList()

    def add_create_target_estimator(self, time_from_estimation, agent_ID, target_ID, target_xc, target_yc, target_size):
        self.memory_all_agent.add_create_target_estimator(time_from_estimation, target_ID, agent_ID, target_xc,
                                                          target_yc, target_size)

    def add_target_estimator(self, estimator):
        self.memory_all_agent.add_target_estimator(estimator)

    def set_current_time(self, current_time):
        self.time = current_time
        self.memory_all_agent.set_current_time(current_time)
        self.memory_agent.set_current_time(current_time)

    def combine_data_agentCam(self, choice=1):
        if choice == 1:
            for item in self.memory_all_agent.agent_target:
                (agentID, targetID) = item
                if agentID == self.id:
                    for estimateur in self.memory_all_agent.get_agent_target_list(targetID, self.id):
                        if not is_target_estimator(self.memory_agent.get_target_list(targetID), estimateur):
                            self.memory_agent.add_target_estimator(estimateur)

    def combine_data_userCam(self, choice=1):
        if choice == 1:
            for item in self.memory_all_agent.agent_target:
                (agentID, targetID) = item
                for estimateur in self.memory_all_agent.get_agent_target_list(targetID, agentID):
                    if not is_target_estimator(self.memory_agent.get_target_list(targetID), estimateur):
                        self.memory_agent.add_target_estimator(estimateur)

    def getPreviousPositions(self, targetID):
        return self.memory_agent.get_target_list(targetID)

    def getPreviousPositions_allMessages(self, targetID, agentID):
        return self.memory_all_agent.get_agent_target_list(targetID, agentID)

    def to_string_memory_all(self):
        return self.memory_all_agent.to_string()

    def to_string_memory(self):
        return self.memory_all_agent.to_string()

    def statistic_to_string(self):
        return self.memory_all_agent.statistic_to_string()
