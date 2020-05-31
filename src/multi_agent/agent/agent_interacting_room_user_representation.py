from src.multi_agent.agent.agent_interacting_room_representation import AgentInteractingWithRoomRepresentation
from src.multi_agent.agent.agent_representation import AgentType


class AgentUserRepresentation(AgentInteractingWithRoomRepresentation):
    def __init__(self, id):
        super().__init__(id, AgentType.AGENT_USER)

    def update_from_agent(self, agent):
        super().update_from_agent(agent)