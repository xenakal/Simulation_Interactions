from multi_agent.tools.estimator import *
from multi_agent.prediction.kalmanPrediction import KalmanPrediction


class Memory:
    """
    description:
        Class with multiple arrays that store information about target.

    params:
        agentID      -- agent to which the memory is associated
        current_time -- time to be updated so that the memory is on time with the room.
        nTime        -- number of memories over time that should be stored (not use yet)

        ([[agent.id, target.id, [TargetEstimator]],...]) memory_all_agent -- list of all information the agent
                                                                             has (ie his reading + reading other other
                                                                             agents sent). The function combine_data
                                                                             uses memory_all_agent to create memory_agent

        ([[target.id,[TargetEstimator]],...]) memory_agent -- list of positions

        ([KalmanPrediction, ...]) predictors -- KalmanPrediction objects tracking the detected targets

        ([[target.id, [pos, ...], ...]) best_estimation -- best estimation of actual position (ie removing the noise) of
                                                           each target.
    """

    def __init__(self, agentID, nTime=20, current_time=0):
        self.id = agentID
        self.time = current_time
        self.nTime = nTime
        self.memory_all_agent = Agent_Target_TargetEstimator()
        self.memory_agent = Target_TargetEstimator()
        self.predictors = []
        self.best_estimations = []

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                    target_xc, target_yc, target_size, target_type):
        """
        :description
            Creates an estimator if it doesn't exist and adds it to the memory_all_agent list
        """
        # update "global info" list
        self.memory_all_agent.add_create_target_estimator(time_from_estimation, agent_id, agent_signature, target_id,
                                                          target_signature, target_xc, target_yc, target_size,
                                                          target_type)

        # add predictor if doesn't exist yet
        if not self.exists_predictor_for_target(target_id):
            self.create_predictor_for_target(target_id, target_xc, target_yc)
        else:
            # inform predictor of new measurement
            target_predictor = self.get_target_predictor(target_id)
            state = [target_xc, target_yc]
            target_predictor.add_measurement(state)
            new_estimate_current_pos = target_predictor.get_current_position()
            self.update_best_estimation(new_estimate_current_pos, target_id)

    def add_target_estimator(self, estimator):
        self.memory_all_agent.add_target_estimator(estimator)

    def set_current_time(self, current_time):
        self.time = current_time
        self.memory_all_agent.current_time = current_time
        self.memory_agent.current_time = current_time

    def combine_data_agentCam(self, choice=1):
        """
        :description
            Creates the memory_agent list from the memory_all_agent list
        :param
            (int) choice -- method used to create memory_agent list
                                =1 -> simply keep info read by agent whose memory this is

        :note
            In the future, a different method could be added, where the information from all agents is combined (for
            example using some kind of mean) to create the memory_agent list.
        """
        if choice == 1:
            # find the targets known by all agents
            for (agentID, targetID) in self.memory_all_agent.Agent_Target_already_discovered_list:
                # keep the ones known by the agents whose memory this is
                if agentID == self.id:
                    for estimateur in self.memory_all_agent.get_Agent_Target_list(targetID, self.id):
                        if not is_in_list_TargetEstimator(self.memory_agent.get_Target_list(targetID), estimateur):
                            self.memory_agent.add_TargetEstimator(estimateur)

    def combine_data_userCam(self, choice=1):
        if choice == 1:
            for (agentID, targetID) in self.memory_all_agent.Agent_Target_already_discovered_list:
                for estimateur in self.memory_all_agent.get_Agent_Target_list(targetID, agentID):
                    if not is_in_list_TargetEstimator(self.memory_agent.get_Target_list(targetID), estimateur):
                        self.memory_agent.add_TargetEstimator(estimateur)

    def get_previous_positions(self, targetID):
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

    # TODO: améliorer avec Kalman distribué
    def update_best_estimation(self, current_best_estimation, seeked_target_id):
        """
        :description
            Updates the estimation list for each target
        :param
            1) ([float, float]) current_best_estimation  -- estimated position
            2) (int) seeked_target_id   -- target id for which the position is added to the best_estimation list
        """
        estimation_added = self.add_estimation_if_target_in_estimation_list(seeked_target_id, current_best_estimation)
        if estimation_added:  # the target was already in the list, which is now updated
            return
        else:  # have to add the entry for the target
            self.best_estimations.append([seeked_target_id, [current_best_estimation]])

    def add_estimation_if_target_in_estimation_list(self, seeked_target_id, estimation):
        """
        :description
            If the estimated noiseless positions list has an entry for this target id, append the estimation to it.
            Otherwise, do nothing.
        :param
            1) (int) seeked_target_id   -- id of target for which the estimation is to be added
            2) (position) estimation    -- noiseless position to be added in the best_estimation list
        """
        for (target_id, pos_list) in self.best_estimations:
            if target_id == seeked_target_id:
                pos_list.append(estimation)
                return True
        return False

    def get_noiseless_estimations(self, seeked_target_id):
        for (target_id, pos_list) in self.best_estimations:
            if target_id == seeked_target_id:
                return pos_list
        return None
