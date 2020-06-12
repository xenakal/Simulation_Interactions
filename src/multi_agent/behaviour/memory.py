from src.multi_agent.elements.target import TargetRepresentation
from src.multi_agent.tools.estimation import MultipleOwnerMemories, SingleOwnerMemories, is_in_list_TargetEstimator, \
    ItemEstimation
from src.multi_agent.prediction.kalmanPrediction import KalmanPrediction
from src.my_utils.my_IO.IO_data import *
import numpy as np


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

        self.memory_all_agent_from_agent = MultipleOwnerMemories()
        self.memory_agent_from_agent = SingleOwnerMemories(agent_id)

        self.memory_all_agent_from_target = MultipleOwnerMemories()
        self.memory_agent_from_target = SingleOwnerMemories(agent_id)

        self.memory_measured_from_target = SingleOwnerMemories(agent_id)
        self.memory_local_kf = SingleOwnerMemories(agent_id)
        self.memory_best_estimations_from_target = SingleOwnerMemories(agent_id)
        self.memory_predictions_order_1_from_target = SingleOwnerMemories(agent_id)
        self.memory_predictions_order_2_from_target = SingleOwnerMemories(agent_id)

        self.predictors = []

        "Logger to keep track of every send and received messages"
        self.log_memory = create_logger(constants.ResultsPath.LOG_MEMORY, "Memory", self.id)

    def add_create_target_estimator(self, time_from_estimation, agent_id, agent_signature, item):
        """
        :description
            Creates an estimator if it doesn't exist and adds it to the memory_all_agent list
        """
        self.log_memory.info("Add memory, from agent : " + str(agent_id) + " - target " + str(item.id))

        # update "global info" list
        self.memory_all_agent_from_target.add_create_itemEstimation(time_from_estimation, agent_id, agent_signature,
                                                                    item)

        # add predictor if doesn't exist yet

        if not self.exists_predictor_for_target(item.id):
            self.create_predictor_for_target(agent_id, item.id, item.xc, item.yc, item.vx, item.vy, item.ax,
                                             item.ay, time_from_estimation)
        # inform predictor of new measurement
        target_predictor = self.get_target_predictor(item.id)
        state = [item.xc, item.yc, item.vx, item.vy, item.ax, item.ay]
        target_predictor.add_measurement(state, time_from_estimation)

        (new_estimate_current_pos, new_var) = target_predictor.get_current_position()

        kalman_target_representation = TargetRepresentation(item.id, new_estimate_current_pos[0],
                                                            new_estimate_current_pos[1], new_estimate_current_pos[2],
                                                            new_estimate_current_pos[3], 0, 0,
                                                            item.radius, item.target_type, item.color)

        self.update_best_estimation(time_from_estimation, agent_id, agent_signature, kalman_target_representation)

        self.update_predictions_lists(time_from_estimation, agent_id, agent_signature, item)

    def add_target_estimator(self, estimator):
        self.log_memory.info(
            "Add memory, from agent : " + str(estimator.owner_id) + " - target " + str(estimator.item.id))
        self.memory_all_agent_from_target.add_itemEstimation(estimator)

    def add_create_agent_estimator_from_agent(self, time_from_estimation, agent, item):
        """
        :description
            Creates an estimator if it doesn't exist and adds it to the memory_all_agent list
        """
        self.log_memory.info("Add memory, from agent : " + str(agent.id) + " - agent " + str(item.id))

        # update "global info" list
        self.memory_all_agent_from_agent.add_create_itemEstimation(time_from_estimation, agent.id,
                                                                   agent.signature, item)

    def add_agent_estimator(self, estimator):
        self.log_memory.info(
            "Add memory, from agent : " + str(estimator.owner_id) + " - agent " + str(estimator.item.id))
        self.memory_all_agent_from_agent.add_itemEstimation(estimator)

    def set_current_time(self, current_time):
        self.time = current_time
        self.memory_all_agent_from_target.current_time = current_time
        self.memory_measured_from_target.current_time = current_time

    def combine_data_agentCam(self):
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
        for (agent_id, target_id) in self.memory_all_agent_from_target.agents_and_items_discovered:
            if agent_id == self.id:
                for estimateur in self.memory_all_agent_from_target.get_agent_item_list(target_id, self.id):
                    if not is_in_list_TargetEstimator(self.memory_measured_from_target.get_item_list(target_id),
                                                      estimateur):
                        self.log_memory.info(
                            "Combine data from agent : " + str(agent_id) + " - target " + str(target_id))
                        self.memory_measured_from_target.add_itemEstimation(estimateur)

        "Combine data related to agentCam"
        if True:
            for (agent_id, agent_observed_id) in self.memory_all_agent_from_agent.agents_and_items_discovered:
                if agent_id == agent_observed_id:
                    for estimateur in self.memory_all_agent_from_agent.get_agent_item_list(agent_id, agent_id):
                        self.log_memory.info(
                            "Combine data from agent : " + str(agent_id) + " - agent " + str(agent_observed_id))
                        if not is_in_list_TargetEstimator(self.memory_agent_from_agent.get_item_list(agent_id),
                                                          estimateur):
                            self.log_memory.info(
                                "Combine data from agent : " + str(agent_id) + " - target " + str(agent_id))
                            self.memory_agent_from_agent.add_itemEstimation(estimateur)

    def combine_data_userCam(self, choice=1):
        if choice == 1:
            for (agent_id, target_id) in self.memory_all_agent_from_target.agents_and_items_discovered:
                for estimateur in self.memory_all_agent_from_target.get_agent_item_list(target_id, agent_id):
                    if not is_in_list_TargetEstimator(self.memory_measured_from_target.get_item_list(target_id),
                                                      estimateur):
                        self.log_memory.info(
                            "Combine data, from agent : " + str(agent_id) + " - target " + str(target_id))
                        self.memory_measured_from_target.add_itemEstimation(estimateur)

        '''
            best_estimator = (-1,1000000000,10000000)
            target_id_list = []

        
            for (agent_id, target_id) in self.memory_all_agent_from_target.Agent_item_already_discovered_list:
                if target_id not in target_id_list:

                    target_id_list.append(target_id)
                    for (agent_id_to_check, target_id_to_check) in self.memory_all_agent_from_target.Agent_item_already_discovered_list:
                        if target_id == target_id_to_check:
                            estimator = self.memory_all_agent_from_target.get_Agent_item_list(target_id, agent_id)[-1]
                            norm_variance = np.sqrt(np.square(estimator.variance_on_estimation[0]) + np.square(estimator.variance_on_estimation[1]))
                            delta_t  = constants.get_time() - estimator.time_stamp
                            
                            if (not isinstance(best_estimator[0], TargetEstimation) or norm_variance < best_estimator[1]) and delta_t < best_estimator[2]:
                                best_estimator = (estimator,norm_variance,delta_t)


                    if isinstance(best_estimator[0], TargetEstimation) and not is_in_list_TargetEstimator(self.memory_measured_from_target.get_item_list(target_id), best_estimator[0]):
                        #self.log_memory.info("Combine data, from agent : " + str(agent_id) + " - target " + str(target_id))
                         self.memory_measured_from_target.add_itemEstimation(best_estimator[0])
            '''

    def get_previous_positions(self, targetID):
        return self.memory_measured_from_target.get_item_list(targetID)

    def getPreviousPositions_allMessages(self, targetID, agentID):
        return self.memory_all_agent_from_target.get_agent_item_list(targetID, agentID)

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
            (x, var) = predictor.get_current_position()
            last_target_estimation = self.memory_best_estimations_from_target.get_item_list(seeked_target_id)[0]
            kalman_target_representation = TargetRepresentation(seeked_target_id, x[0], x[1], x[2], x[3], 0, 0,
                                                                last_target_estimation.item.radius,
                                                                last_target_estimation.item.target_type,
                                                                last_target_estimation.item.color)

            new_ItemEstimation = ItemEstimation(time_stamp=timestamp, owner_id=self.id,
                                                owner_agent_signature=-1, item=kalman_target_representation)
            self.memory_best_estimations_from_target.update_last_itemEstimation(new_ItemEstimation)

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

    def update_best_estimation(self, time_from_estimation, agent_id, agent_signature, item):
        """
        :description
            Updates the estimation list for each target
        :param

        """
        self.memory_best_estimations_from_target.add_create_itemEstimation(time_from_estimation, agent_id,
                                                                           agent_signature, item)
        self.memory_local_kf.add_create_itemEstimation(time_from_estimation, agent_id,
                                                                           agent_signature, item)

    def get_noiseless_estimations(self, seeked_target_id):
        """
        :return:
            if not found        -- []
            else                -- TargetEstimator list
        """
        return self.memory_best_estimations_from_target.get_item_list(seeked_target_id)

    def get_local_kf(self, seeked_target_id):
        return self.memory_local_kf.get_item_list(seeked_target_id)

    def update_predictions_lists(self, time_from_estimation, agent_id, agent_signature, item):

        # predictions_for_target = self.get_target_predictor(target_id).get_predictions()
        predictions_for_target = self.get_target_predictions(item.id)
        if len(predictions_for_target) < 2:  # No predictions made
            return

        predictions_order_1 = predictions_for_target[0]
        predictions_order_2 = predictions_for_target[1]

        prediction_1, variance1 = predictions_order_1
        prediction_2, variance2 = predictions_order_2

        predict_vx = 0
        predict_vy = 0
        predict_ax = 0
        predict_ay = 0
        self.memory_predictions_order_1_from_target.add_create_itemEstimation(time_from_estimation, agent_id,
                                                                              agent_signature, item)

        self.memory_predictions_order_2_from_target.add_create_itemEstimation(time_from_estimation, agent_id,
                                                               agent_signature,item)

    def compute_obstruction_time(self,filename1,filename2,room):
        list = self.memory_measured_from_target
        for target in room.information_simulation.target_list:
            obstructed_time = [0,0,0,0,0]
            item_list = list.get_item_list(target.id)
            item_list.sort()
            for item1,item2 in zip(item_list[:-1],item_list[1:]):

                delta_t = item2.time_stamp - item1.time_stamp
                for n,time in enumerate(obstructed_time):
                    if delta_t < (n+1)*constants.TIME_BTW_TARGET_ESTIMATOR and 10 < item1.time_stamp < 70 :
                        #print("item1: %.02f item2: %.02f" % (item1.time_stamp, item2.time_stamp))
                        #print(delta_t)
                        obstructed_time[n] += delta_t
                        break
                    elif delta_t > 5*constants.TIME_BTW_TARGET_ESTIMATOR and 10 < item1.time_stamp < 70 :
                        obstructed_time[-1] += delta_t
                        break


            #fichier = open(filename1, "a")
            #fichier.write("%s \n" % obstructed_time)
            #fichier.close()
            #fichier = open(constants.MapPath.MAIN_FOLDER +filename2, "a")
            #fichier.write("%s \n"%obstructed_time)
            #fichier.close()

