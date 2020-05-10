from src.multi_agent.agent.agent_interacting_room_representation import AgentInteractingWithRoomRepresentation, \
    MessageTypeAgentInteractingWithRoom
from src.multi_agent.agent.agent_representation import AgentType
from src.multi_agent.elements.mobile_camera import MobileCameraRepresentation


class MessageTypeAgentCameraInteractingWithRoom(MessageTypeAgentInteractingWithRoom):
    INFO_DKF = "info_DKF"
    TRACKING_TARGET = "tracking_target"
    LOSING_TARGET = "loosing_target"


class AgentCameraFSM:
    MOVE_CAMERA = "Move camera"
    TAKE_PICTURE = "Take picture"
    PROCESS_DATA = "Process Data"
    COMMUNICATION = "Communication"
    BUG = "Bug"


class InternalPriority:
    NOT_TRACKED = 2
    TRACKED = 5


class AgentCamRepresentation(AgentInteractingWithRoomRepresentation):
    def __init__(self, id=None):
        super().__init__(id, AgentType.AGENT_CAM)
        self.camera_representation = MobileCameraRepresentation(0, 0, 0, 0, 0, 0, 0, 0)

    def update_from_agent(self, agent):
        super().update_from_agent(agent)
        self.camera_representation.init_from_camera(agent.camera)

