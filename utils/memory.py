from utils.infoAgentCamera import*

class Memory:
    def __init__(self, nTime=20, current_time=0):
            self.time= current_time
            self.nTime = nTime
            self.memory_all_agent = TargetEstimatorList()
            self.memory_agent = FusionEstimatorList()

    def init_memory(self,room):
        self.memory_all_agent.init_estimator_list(room)
        self.memory_agent.init_estimator_list(room)


