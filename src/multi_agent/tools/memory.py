from src.multi_agent.tools.estimator import *
from src.multi_agent.prediction.kalmanPrediction import KalmanPrediction
from src.my_utils.my_IO.IO_data import *

class CombineDataChoice:
    DATA_MEASURED_ONLY_SELF = "data measured only self"
    DATA_KALMAN = "data_kalman"
    DATA_PREDICTION_T_PLUS_1 = "data_preditiction_1"
    DATA_PREDICTION_T_PLUS_2 = "data_preditiction_2"

class Memory:
    """
    description:
        Class with multiple arrays that store information about target.

    params:
        agentID      -- agent to which the memory is associated
        current_time -- time to be updated so that the memory is on time with the room.
        nTime        -- number of memories over time that should be stored (not use yet)

        (Agent_Target_TargetEstimator) memory_all_agent -- list of all information the agent has (ie his reading +
                                                           reading other other agents sent). The function combine_data
                                                           uses memory_all_agent to create memory_agent.

        (Target_TargetEstimator) memory_agent -- list of combined information for each target.
                                                 Now, it only contains the information the agent himself has gathered.
                                                 In the future, a different approach may be implemented, where some
                                                 sort of mean is implemented to combine the information all agents
                                                 exchange.

        ([KalmanPrediction, ...]) predictors -- KalmanPrediction objects tracking the detected targets.

        (Target_TargetEstimator) best_estimation -- best estimation of actual position (ie removing the noise) of
                                                    each target.

        (Target_TargetEstimator) predictions_order_X -- predictions at order X.

    """

    def __init__(self, agent_id, nTime=20, current_time=0):
        self.id = agent_id
        self.time = current_time
        self.nTime = nTime

        self.memory_all_agent_from_agent = Agent_Agent_AgentEstimator()
        self.memory_agent_from_agent = Agent_AgentEstimator()

        self.memory_all_agent_from_target = Agent_Target_TargetEstimator()
        self.memory_agent_from_target = Target_TargetEstimator()

        self.memory_measured_from_target = Target_TargetEstimator()
        self.memory_best_estimations_from_target = Target_TargetEstimator()
        self.memory_predictions_order_1_from_target = Target_TargetEstimator()
        self.memory_predictions_order_2_from_target = Target_TargetEstimator()

        self.predictors = []

        "Logger to keep track of every send and received messages"
        self.log_memory = create_logger(constants.ResultsPath.LOG_MEMORY, "Memory", self.id)

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                             target_xc, target_yc,target_vx, target_vy, target_ax, target_ay, target_type,target_size):
        """
        :description
            Creates an estimator if it doesn't exist and adds it to the memory_all_agent list
        """
        self.log_memory.info("Add memory, from agent : " + str(agent_id) + " - target " + str(target_id))

        # update "global info" list
        self.memory_all_agent_from_target.add_create_target_estimator(time_from_estimation, agent_id, agent_signature, target_id,
                                                                      target_signature, target_xc, target_yc, target_vx, target_vy,
                                                                     target_ax, target_ay, target_type,target_size,-1)

        # add predictor if doesn't exist yet
        if not self.exists_predictor_for_target(target_id):
            self.create_predictor_for_target(agent_id, target_id, target_xc, target_yc, target_vx, target_vy, target_ax,
                                             target_ay, time_from_estimation)
        # inform predictor of new measurement
        target_predictor = self.get_target_predictor(target_id)
        state = [target_xc, target_yc, target_vx, target_vy, target_ax, target_ay]
        target_predictor.add_measurement(state, time_from_estimation)

        (new_estimate_current_pos,new_var) = target_predictor.get_current_position()
        self.update_best_estimation(time_from_estimation, agent_id, agent_signature, target_id,
                                    target_signature, new_estimate_current_pos[0], new_estimate_current_pos[1],
                                    target_vx, target_vy, target_ax, target_ay, target_size, target_type,(new_var[0][0],new_var[1][1]))

        self.update_predictions_lists(time_from_estimation, agent_id, agent_signature, target_id,
                                      target_signature, target_size, target_type)

    def add_target_estimator(self, estimator):
        self.log_memory.info(
            "Add memory, from agent : " + str(estimator.agent_id) + " - target " + str(estimator.item_id))
        self.memory_all_agent_from_target.add_itemEstimator(estimator)

    def add_create_agent_estimator_from_agent(self, time_from_estimation, agent,agent_observed):
        """
        :description
            Creates an estimator if it doesn't exist and adds it to the memory_all_agent list
        """
        self.log_memory.info("Add memory, from agent : " + str(agent.id) + " - agent " + str(agent_observed.id))

        # update "global info" list
        self.memory_all_agent_from_agent.add_create_agent_estimator_from_agent(time_from_estimation,agent,agent_observed)

    def add_create_agent_estimator(self, time_from_estimation, agent_id, agent_signature, agent_camera_id, agent_camera_signature,
                                   agent_camera_xc, agent_camera_yc, agent_camera_vx, agent_camera_vy,
                                   agent_camera_ax, agent_camera_ay, agent_camera_type,
                                   agent_camera_alpha, agent_camera_beta,agent_camera_field_depth,
                                   agent_camera_color, agent_camera_room, agent_camera_is_camera_active, agent_is_agent_active,
                                   agent_camera_trajectory):
        """
        :description
            Creates an estimator if it doesn't exist and adds it to the memory_all_agent list
        """
        self.log_memory.info("Add memory, from agent : " + str(agent_camera_id) + " - agent " + str(agent_camera_id))

        # update "global info" list
        self.memory_all_agent_from_agent.add_create_agent_estimator(time_from_estimation, agent_id, agent_signature,
                                                                      agent_camera_id,agent_camera_signature,
                                                                      agent_camera_xc, agent_camera_yc,
                                                                      agent_camera_vx,agent_camera_vy,
                                                                      agent_camera_ax, agent_camera_ay,
                                                                      agent_camera_type,agent_camera_alpha,
                                                                      agent_camera_beta,agent_camera_field_depth,
                                                                      agent_camera_color, agent_camera_room,
                                                                      agent_camera_is_camera_active, agent_is_agent_active,
                                                                      agent_camera_trajectory)

    def add_agent_estimator(self, estimator):
        self.log_memory.info(
            "Add memory, from agent : " + str(estimator.agent_id) + " - agent " + str(estimator.item_id))
        self.memory_all_agent_from_agent.add_itemEstimator(estimator)


    def set_current_time(self, current_time):
        self.time = current_time
        self.memory_all_agent_from_target.current_time = current_time
        self.memory_measured_from_target.current_time = current_time

    def combine_data_agentCam(self, choice):
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
        for (agent_id, target_id) in self.memory_all_agent_from_target.Agent_item_already_discovered_list:
            if agent_id == self.id:
                for estimateur in self.memory_all_agent_from_target.get_Agent_item_list(target_id, self.id):
                    if not is_in_list_TargetEstimator(self.memory_measured_from_target.get_item_list(target_id),estimateur):
                        self.log_memory.info("Combine data from agent : " + str(agent_id) + " - target " + str(target_id))
                        self.memory_measured_from_target.add_itemEstimator(estimateur)

        "Combine data related to target"
        if choice == CombineDataChoice.DATA_MEASURED_ONLY_SELF:
            self.memory_agent_from_target= self.memory_measured_from_target
        elif choice == CombineDataChoice.DATA_KALMAN:
            self.memory_agent_from_target = self.memory_best_estimations_from_target
        elif choice == CombineDataChoice.DATA_PREDICTION_T_PLUS_1:
            self.memory_agent_from_target = self.memory_predictions_order_1_from_target
        elif choice == CombineDataChoice.DATA_PREDICTION_T_PLUS_2:
            self.memory_agent_from_target = self.memory_predictions_order_2_from_target

        "Combine data related to agentCam"
        if True:
            for (agent_id, agent_observed_id) in self.memory_all_agent_from_agent.Agent_item_already_discovered_list:
                if agent_id == agent_observed_id:
                    for estimateur in self.memory_all_agent_from_agent.get_Agent_item_list(agent_id,agent_id):
                        self.log_memory.info("Combine data from agent : " + str(agent_id) + " - agent " + str(agent_observed_id))
                        if not is_in_list_TargetEstimator(self.memory_agent_from_agent.get_item_list(agent_id),estimateur):
                            self.log_memory.info("Combine data from agent : " + str(agent_id) + " - target " + str(agent_id))
                            self.memory_agent_from_agent.add_itemEstimator(estimateur)

    def combine_data_userCam(self, choice=1):
        if choice == 1:
            for (agent_id, target_id) in self.memory_all_agent_from_target.Agent_item_already_discovered_list:
                for estimateur in self.memory_all_agent_from_target.get_Agent_item_list(target_id, agent_id):
                    if not is_in_list_TargetEstimator(self.memory_measured_from_target.get_item_list(target_id), estimateur):
                        self.log_memory.info(
                            "Combine data, from agent : " + str(agent_id) + " - target " + str(target_id))
                        self.memory_measured_from_target.add_itemEstimator(estimateur)

    def get_previous_positions(self, targetID):
        return self.memory_measured_from_target.get_item_list(targetID)

    def getPreviousPositions_allMessages(self, targetID, agentID):
        return self.memory_all_agent_from_target.get_Agent_item_list(targetID, agentID)

    def to_string_memory_all(self):
        return self.memory_all_agent_from_target.to_string() + "\n" + self.memory_all_agent_from_agent.to_string()

    def statistic_to_string(self):
        return self.memory_all_agent_from_target.statistic_to_string()

    def get_predictions(self, seeked_target_id):
        """
        :return: a list [[targetId, [predicted_position1, ...]], ...]
        """
        predictions = []
        for target_id in seeked_target_id:
            target_prediction = self.get_target_predictions(target_id)
            if target_prediction is not None:
                predictions.append([target_id, target_prediction])

        """
            list_all_prediction = [list_predtion_tplus1 = Target_TargetEstimator(), list_predtion_t2 = Target_TargetEstimator()]
        """
        return predictions

    def get_target_predictions(self, seeked_target_id):
        """
        :description:
            Method used for the predictions of future positions.
        :return the predicted positions for targetId """
        predictor = self.get_target_predictor(seeked_target_id)
        if predictor is None:
            return []
        return predictor.get_predictions()

    def get_DKF_info_string(self, seeked_target_id):
        """
        :description:
            Method used for the communication of DKF messages. When an agent needs to send the DKF_info to the other
            agents, it get it through this method.
        :return the state/variance error info needed for the DKF
        """
        predictor = self.get_target_predictor(seeked_target_id)
        if predictor is None:
            return []
        return predictor.get_DKF_info_string()

    def process_DKF_info(self, seeked_target_id, dfk_info_string, timestamp):
        """
        :description:
            Method used for the communication of DKF messages. When an agent receives an DKF_info message, it calls
            this method to transmit this information to the DKF associated with the target.
        """
        predictor = self.get_target_predictor(seeked_target_id)
        if predictor is not None:
            predictor.assimilate(dfk_info_string, timestamp)

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

    def create_predictor_for_target(self, agent_id, target_id, x_init, y_init, vx_init, vy_init, ax_init, ay_init,
                                    timestamp):
        """ Creates an entry in self.predictors for this target """
        predictor = KalmanPrediction(agent_id, target_id, x_init, y_init, vx_init, vy_init, ax_init, ay_init, timestamp)
        self.predictors.append(predictor)

    # TODO: améliorer avec Kalman distribué
    def update_best_estimation(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                               pos_x, pos_y, v_x, v_y, a_x, a_y, target_size, target_type,variance_on_estimation):
        """
        :description
            Updates the estimation list for each target
        :param

        """
        self.memory_best_estimations_from_target.add_create_target_estimator(time_from_estimation, agent_id, agent_signature, target_id,
                                                                             target_signature, pos_x, pos_y, v_x, v_y, a_x, a_y,
                                                                             target_size, target_type, variance_on_estimation)

    def get_noiseless_estimations(self, seeked_target_id):
        """
        :return:
            if not found        -- []
            else                -- TargetEstimator list
        """
        return self.memory_best_estimations_from_target.get_item_list(seeked_target_id)

    def update_predictions_lists(self, time_from_estimation, agent_id, agent_signature, target_id, target_signature,
                                 target_size, target_type):

       # predictions_for_target = self.get_target_predictor(target_id).get_predictions()
        predictions_for_target = self.get_target_predictions(target_id)
        if len(predictions_for_target) < 2:  # No predictions made
            return

        predictions_order_1 = predictions_for_target[0]
        predictions_order_2 = predictions_for_target[1]

        prediction_1,variance1 = predictions_order_1
        prediction_2, variance2 = predictions_order_2


        predict_vx = 0
        predict_vy = 0
        predict_ax = 0
        predict_ay = 0
        self.memory_predictions_order_1_from_target.add_create_target_estimator(time_from_estimation, agent_id, agent_signature, target_id,
                                                                                target_signature, prediction_1[0],
                                                                                prediction_1[1], predict_vx, predict_vy, predict_ax,
                                                                                predict_ay, target_size, target_type, (variance1[0][0],variance1[1][1]))

        self.memory_predictions_order_2_from_target.add_create_target_estimator(time_from_estimation, agent_id, agent_signature, target_id,
                                                                                target_signature, prediction_2[0],
                                                                                prediction_2[1], predict_vx, predict_vy, predict_ax,
                                                                                predict_ay, target_size, target_type, (variance2[0][0],variance2[1][1]))
