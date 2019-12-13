from utils.estimator import*

class Memory:
    def __init__(self, agentID,nTime=20, current_time=0):
            self.id =agentID
            self.time= current_time
            self.nTime = nTime
            self.memory_all_agent = TargetEstimatorList()
            self.memory_agent = FusionEstimatorList()

    def init_memory(self,room):
        self.memory_all_agent.init_estimator_list(room)
        self.memory_agent.init_estimator_list(room)

    def add_create_target_estimator(self,room, time_from_estimation, target_ID, agent_ID, seenByCam):
        self.memory_all_agent.add_create_target_estimator(room, time_from_estimation, target_ID, agent_ID, seenByCam)

    def add_target_estimator(self,estimator):
        self.memory_all_agent.add_target_estimator(estimator)

    def set_current_time(self,current_time):
        self.time =current_time
        self.memory_all_agent.set_current_time(current_time)
        self.memory_agent.set_current_time(current_time)

    def get_room_estimation(self,time):
        estimation_t = time
        self.memory_agent.sort()
        for element in self.memory_agent.room_representation:
            for estimateur in element[1]:
                if estimateur.timestamp == time:
                    estimation_t.append(estimateur)

        return estimation_t

    def combine_data(self,room):
        #SIMPLE MANIERE DE FAIRE A MODIFIER NE PREND EN COMPTE QUE CE QUE L'AGENT VOIT
        for target in room.targets:
            for estimateur in self.memory_all_agent.get_agent_target_list(target.id,self.id):
                if not self.memory_agent.is_target_estimator(self.memory_agent.get_target_list(target.id),estimateur):
                    self.memory_agent.add_target_estimator(estimateur)

    def to_string_memory_all(self):
        return self.memory_all_agent.to_string()

    def to_string_memory(self):
        return self.memory_all_agent.to_string()

    def statistic_to_string(self):
        return self.memory_all_agent.statistic_to_string()


