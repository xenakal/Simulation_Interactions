from src.multi_agent.agent.agent import AgentRepresentation
from src.multi_agent.communication.message import MessageType


class BroadcastTypes:
    ALL = "all"
    AGENT_CAM = "agentCams"
    AGENT_USER = "agentUser"


class MessageTypeAgentInteractingWithRoom(MessageType):
    HEARTBEAT = "heartbeat"
    AGENT_ESTIMATION = "agentEstimation"
    TARGET_ESTIMATION = "targetEstimation"
    ITEM_ESTIMATION = "itemEstimation"


class AgentInteractingWithRoomRepresentation(AgentRepresentation):
    def __init__(self, id, type):
        super().__init__(id, type)
