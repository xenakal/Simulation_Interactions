from multi_agent.tools.estimator import *
from multi_agent.prediction.kalmanPrediction import KalmanPrediction


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

        ([KalmanPrediction, ...]) predictors -- KalmanPrediction objects tracking the detected targets
    """

    def __init__(self, agentID, nTime=20, current_time=0):
        self.id = agentID
        self.time = current_time
        self.nTime = nTime
        self.memory_all_agent = Agent_Target_TargetEstimator()
        self.memory_agent = Target_TargetEstimator()
        self.predictors = []

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                    target_xc, target_yc, target_size, target_type):
        """
        Creates an estimator if it doesn't exist and adds it to the memory_all_agent list
        """
        self.memory_all_agent.add_create_target_estimator(time_from_estimation, agent_id, agent_signature, target_id,
                                                          target_signature, target_xc, target_yc, target_size,
                                                          target_type)
        if not self.exists_predictor_for_target(target_id):
            # add predictor if doesn't exist yet
            self.create_predictor_for_target(target_id, target_xc, target_yc)
        else:
            # inform predictor of new measurement
            target_predictor = self.get_target_predictor(target_id)
            state = [target_xc, target_yc]
            target_predictor.add_measurement(state)
            # update current position list
            new_position_estimation = target_predictor.get_current_position()
            self.update_memory_agent(time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                     new_position_estimation[0], new_position_estimation[1], target_size)

    def add_target_estimator(self, estimator):
        self.memory_all_agent.add_target_estimator(estimator)

    def set_current_time(self, current_time):
        self.time = current_time
        self.memory_all_agent.current_time = current_time
        self.memory_agent.current_time = current_time

    def combine_data_agentCam(self, choice=1):
        if choice == 1:
            for item in self.memory_all_agent.Agent_Target_already_discovered_list:
                (agentID, targetID) = item
                if agentID == self.id:
                    for estimateur in self.memory_all_agent.get_Agent_Target_list(targetID, self.id):
                        if not is_in_list_TargetEstimator(self.memory_agent.get_Target_list(targetID), estimateur):
                            self.memory_agent.add_TargetEstimator(estimateur)

    def combine_data_userCam(self, choice=1):
        if choice == 1:
            for item in self.memory_all_agent.Agent_Target_already_discovered_list:
                (agentID, targetID) = item
                for estimateur in self.memory_all_agent.get_Agent_Target_list(targetID, agentID):
                    if not is_in_list_TargetEstimator(self.memory_agent.get_Target_list(targetID), estimateur):
                        self.memory_agent.add_TargetEstimator(estimateur)

    def getPreviousPositions(self, targetID):
        return self.memory_agent.get_Target_list(targetID)

    def getPreviousPositions_allMessages(self, targetID, agentID):
        return self.memory_all_agent.get_Agent_Target_list(targetID, agentID)

    def to_string_memory_all(self):
        return self.memory_all_agent.to_string()

    def to_string_memory(self):
        return self.memory_all_agent.to_string()

    def statistic_to_string(self):
        return self.memory_all_agent.statistic_to_string()

    def get_predictions(self, seeked_target_id):
        """
        :return: a list [[targetId, [predicted_position1, ...]], ...]
        """
        predictions = []
        for target_id in seeked_target_id:
            target_prediction = self.get_target_predictions(target_id)
            if target_prediction is not None:
                predictions.append([target_id, target_prediction])
        return predictions

    def get_target_predictions(self, seeked_target_id):
        """ :return the predicted positions for targetId """
        for predictor in self.predictors:
            if predictor.target_id == seeked_target_id:
                return predictor.get_predictions()
        return None

    def get_target_predictor(self, seeked_target_id):
        """ :return the Kalman Predictor associated with this target """
        for predictor in self.predictors:
            if predictor.target_id == seeked_target_id:
                return predictor
        return None

    def exists_predictor_for_target(self, seeked_target_id):
        """ Checks if a predictor for the given target exists """
        for predictor in self.predictors:
            if predictor.target_id == seeked_target_id:
                return True
        return False

    def create_predictor_for_target(self, target_id, x_init, y_init):
        """ Creates an entry in self.predictors for this target """
        predictor = KalmanPrediction(target_id, x_init, y_init)
        self.predictors.append(predictor)

    # TODO: retirer (pas utilisé car on utilise get_current_position du prédicteur direct)
    def get_current_position(self, target_id):
        """ :return the estimated current position as computed by the Kalman predictor """
        target_predictor = self.get_target_predictor(target_id)
        if target_predictor is None:
            return None
        return target_predictor.get_current_position()

    def update_memory_agent(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                            target_xc, target_yc, target_size):
        """
        Assumes the predictor corresponding to target_id has new information (doesn't check).
        Updates the memory_agent list for the target.
        """
        new_TargetEstimator = TargetEstimator(time_from_estimation, agent_id, agent_signature, target_id,
                                              target_signature,
                                              target_xc, target_yc, target_size)
        self.memory_agent.add_TargetEstimator(new_TargetEstimator)
