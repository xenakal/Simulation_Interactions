from multi_agent.estimator import *
from multi_agent.kalmanPrediction import KalmanPrediction


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

        ([[target.id, KalmanPrediction], ...]) predictors -- KalmanPrediction objects tracking the detected targets
    """

    def __init__(self, agentID, nTime=20, current_time=0):
        self.id = agentID
        self.time = current_time
        self.nTime = nTime
        self.memory_all_agent = Agent_Target_TargetEstimator()
        self.memory_agent = Target_TargetEstimator()
        self.predictors = []

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                    target_xc, target_yc, target_size):
        """
        Creates an estimator if it doesn't exist and adds it to the memory_all_agent list
        """

        self.memory_all_agent.add_create_target_estimator(time_from_estimation, agent_id, agent_signature, target_id,
                                                          target_signature, target_xc, target_yc, target_size)

        # TODO: voir un peu ce qu'on fait avec les messages: là on a un memory_all_agent qui est censé tout stocker,
        #  mais en réalité on a pas de messages echangés. Y réfléchir :)

        #  Create predictor if doesn't exist yet
        if target_id == self.id and not self.exists_predictor_for_target(target_id):
            self.create_predictor_for_target(target_id)

        # Incorporate new data in corresponding predictor
        if target_id == self.id:
            target_predictor = self.get_predictor_of_target(target_id)
            target_predictor.add_measurement([target_xc, target_yc])

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

    def get_predictions(self, target_id_List):
        """ Returns a list [[targetId, [predicted_position1, ...]], ...]"""
        predictions = []
        for target_id in target_id_List:
            prediction_for_target = self.get_target_prediction(target_id)
            predictions.append([target_id, prediction_for_target])
        return predictions

    def get_target_prediction(self, seeked_target_id):
        """ Returns the predicted positions for seeked_target_id """
        for (target_id, predictor) in self.predictors:
            if target_id == seeked_target_id:
                return predictor.get_predictions()

        return None

    def exists_predictor_for_target(self, seeked_target_id):
        """ Checks if a predictor for the target already exists """
        for (target_id, _) in self.predictors:
            if target_id == seeked_target_id:
                return True
        return False

    def create_predictor_for_target(self, target_id):
        """ Adds a predictor to the predictors list corresponding to the target in argument """
        self.predictors.append([target_id, KalmanPrediction()])

    def get_predictor_of_target(self, seeked_target_id):
        """ Returns the predictor associated with the target_id """
        for (target_id, predictor) in self.predictors:
            if target_id == seeked_target_id:
                return predictor
        return None
