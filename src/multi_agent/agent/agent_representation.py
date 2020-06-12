from src import constants
from src.my_utils.confidence import evaluate_confidence
from src.my_utils.item import Item


class AgentType:
    AGENT_CAM = 0
    AGENT_USER = 100


class AgentRepresentation(Item):
    def __init__(self, id, type):
        if id is None:
            super().__init__(id)
        else:
            super().__init__(id+type)

        self.type = type
        self.is_active = False
        self.color = None
        self.confidence = -1

    def update_from_agent(self, agent):
        self.id = agent.id
        self.signature = agent.signature

        self.type = agent.type
        self.is_active = agent.is_active
        self.color = agent.color
        self.confidence = -1

    def evaluate_agent_confidence(self,error,delta_time):
        self.confidence = evaluate_confidence(error,delta_time)
        if not constants.AGENTS_MOVING:
            self.confidence = constants.CONFIDENCE_MAX_VALUE