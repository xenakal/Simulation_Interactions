import threading
# from elements.room import*
import src.multi_agent.elements.room
from src.multi_agent.agent.agent import *
from src.multi_agent.tools.memory import *
from src.multi_agent.communication.message import *
from src import constants


class MessageTypeAgentInteractingWithRoom(MessageType):
    HEARTBEAT = "heartbeat"
    TARGET_ESTIMATOR = "targetEstimator"


class  AgentInteractingWithRoomRepresentation(AgentRepresentation):
    def __init__(self, id, type):
        super().__init__(id, type)


class AgentInteractingWithRoom(Agent):
    """
        Class AgentInteractingWithRoom extend Agent.

        Description :

            :param
                1. (int) id                              -- numerical value to recognize the Agent
                2. (AgentType) type                      -- to distinguish the different agent
                3. ((int),(int),(int)) color             -- color representation for the GUI

            :attibutes
                -- IN Agent
                1. (int) id                                     -- numerical value to recognize the Agent
                2. (int) signature                              -- numerical value to identify the Agent, random value
                3. (AgentType) type                             -- to distinguish
                                                                    the different agent
                4. ((int),(int),(int)) color                    -- color representation for the GUI
                5. (ListMessage) info_message_sent              -- list containing all the messages sent
                6. (ListMessage) info_message_received          -- list containing all the messages received
                7. (ListMessage) info_message_to_send           -- list containing all the messages to send
                8. (AgentStatistic) message_statistic           -- object to compute how many messages are sent and
                                                                   received

                ---NEW
                9. (Memory) memory                              -- object to deal with TargetEstimator
               10. (RoomRepresentation) room_representation     -- object to reconstruct the room
               11. (int) thread_is_running                      -- runnig if 1, else stop
               12. (thread) main_thread                         -- thread

            :notes
                fells free to write some comments.
    """

    def __init__(self, id, type_agent, t_add, t_del, color=0):
        super().__init__(id, type_agent, t_add, t_del, color)
        "Attibutes"
        self.memory = Memory(self.id)
        self.room_representation = src.multi_agent.elements.room.RoomRepresentation(self.color)
        self.hearbeat_tracker = HeartbeatCounterAllAgent(self.id, self.signature, self.log_main)
        self.time_last_message_targetEstimtor_sent = constants.get_time()

        "Create his own thread"
        self.thread_is_running = 1
        self.main_thread = None

        self.time_last_heartbeat_sent = constants.get_time()
        self.log_room = create_logger(constants.ResultsPath.LOG_AGENT, "Room + memory", self.id)

    def init_and_set_room_description(self, room):
        """
            :description
                1. set the RoomDescription
                2. set the AgentStatistic

            :param
                1. (Room) room    -- To set up the RoomDescription

        """
        self.log_main.info("starting initialisation in agent_interacting_room")
        self.room_representation.init_RoomRepresentation(room)
        self.message_statistic.init_message_static(self.room_representation)
        self.main_thread = threading.Thread(target=self.thread_run,args=[room])

        self.log_main.info("initialisation in agent_interacting_room_done !")
        self.log_main.debug("see below the room representation ")
        self.log_main.debug("agentCams :" + str(self.room_representation.agentCams_representation_list))
        self.log_main.debug("active_agentCams :" + str(self.room_representation.agentCams_representation_list))
        self.log_main.debug("agentUser :" + str(self.room_representation.agentUser_representation_list))
        self.log_main.debug("active_agentUser :" + str(self.room_representation.agentUser_representation_list))
        self.log_main.debug("target :" + str(self.room_representation.active_Target_list))

    def run(self):
        """
            :description
                1. Function to call to run/start the agent
        """
        self.main_thread.start()


    def thread_run(self, room):
        pass


    def clear(self):
        """
            :description
                1. Function to call to stop the agent
        """
        "Save data"
        if constants.SAVE_DATA:
            print("Saving data: agent " + str(self.id))
            self.log_main.info("Saving data ...: agent " + str(self.id))
            save_in_csv_file_dictionnary(constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_AGENT + str(self.id),
                                         self.memory.memory_all_agent_from_target.to_csv())
            save_in_csv_file_dictionnary(constants.ResultsPath.SAVE_LOAD_DATA_MEMORY_ALL_AGENT + str(self.id),
                                         self.memory.memory_measured_from_target.to_csv())
            save_in_csv_file_dictionnary(constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL_FILTER + str(self.id),
                                         self.memory.memory_best_estimations_from_target.to_csv())
            save_in_csv_file_dictionnary(
                constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL_PREDICTION_TPLUS1 + str(self.id),
                self.memory.memory_predictions_order_1_from_target.to_csv())
            save_in_csv_file_dictionnary(
                constants.ResultsPath.SAVE_LOAD_DATA_KALMAN_GLOBAL_PREDICTION_TPLUS2 + str(self.id),
                self.memory.memory_predictions_order_2_from_target.to_csv())
            self.log_main.info("Data saved !")

        "Clear"
        self.thread_is_running = 0
        while self.main_thread.is_alive():
            pass
        mbox = mailbox.mbox(constants.NAME_MAILBOX + str(self.id))
        mbox.close()
        self.log_main.info("Agent cleared \n")



    def process_information_in_memory(self):
        """ interface """
        pass

    def process_message_sent(self):
        """
            :description
                1. Association from ack and nack received to sent messages
        """
        for message_sent in self.info_message_sent.get_list():
            if message_sent.is_approved():
                '''Do something'''
                self.info_message_sent.del_message(message_sent)
            elif message_sent.is_not_approved():
                self.info_message_sent.del_message(message_sent)

    def process_message_received(self):
        """
            :description
                1. Dispatsching to deal with multiple message given the type
        """
        for rec_mes in self.info_message_received.get_list():
            self.process_single_message(rec_mes)

    def process_single_message(self, rec_mes):
        if rec_mes.messageType == MessageTypeAgentInteractingWithRoom.TARGET_ESTIMATOR:
            self.received_message_targetEstimator(rec_mes)
        elif rec_mes.messageType == MessageType.ACK or rec_mes.messageType == MessageType.NACK:
            self.received_message_ack_nack(rec_mes)
        elif rec_mes.messageType == MessageTypeAgentInteractingWithRoom.HEARTBEAT:
            self.received_message_heartbeat(rec_mes)

        self.info_message_received.del_message(rec_mes)

    def handle_hearbeat(self):
        self.send_message_heartbeat()

        for heartbeat in self.hearbeat_tracker.agent_heartbeat_list:
            if heartbeat.is_to_late():
                agent_to_suppress = -1
                for agent in self.room_representation.agentCams_representation_list:
                    if agent.id == heartbeat.agent_id:
                        agent_to_suppress = agent
                        break
                if not agent_to_suppress == -1 and agent_to_suppress.is_active:
                   agent_to_suppress.is_active = False
                   self.log_main.info("Agent : " + str(agent_to_suppress.id) + "at:  %.02fs is not connected anymore, last heartbeat : %.02f s" %
                                      (constants.get_time(),heartbeat.heartbeat_list[-1]))






    def send_message_targetEstimator(self, targetEstimator, receivers=None):
        """
            :description
                1. Create a message based on a TargetEstimator
                2. Place it in the list message_to_send

            :param
                1. (TargetEstimator) targetEstimator -- TargetEstimator, see the class
                2. (list) receivers                  -- [[receiver_id,receiver_signature], ... ], data to
                                                        tell to whom to send the message.

        """
        if receivers is None:
            receivers = []
        s = targetEstimator.to_string()
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        m = MessageCheckACKNACK(constants.get_time(), self.id, self.signature,
                                MessageTypeAgentInteractingWithRoom.TARGET_ESTIMATOR, s,
                                targetEstimator.item_id)
        if len(receivers) == 0:
            for agent in self.room_representation.agentCams_representation_list:
                if agent.id != self.id:
                    m.add_receiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                m.add_receiver(receiver[0], receiver[1])

        cdt1 = self.info_message_to_send.is_message_with_same_message(m)
        if not cdt1:
            self.info_message_to_send.add_message(m)

    def send_message_timed_targetEstimator(self,target_id,receivers= None):
        delta_time = constants.get_time() - self.time_last_message_targetEstimtor_sent


        if delta_time > constants.TIME_BTW_TARGET_ESTIMATOR:
            #target_estimator_list = self.memory.memory_measured_from_target.get_item_list(target_id)
            target_estimator_list = self.memory.memory_predictions_order_2_from_target.get_item_list(target_id)

            if len(target_estimator_list) > 0:
                last_target_estimator = target_estimator_list[-1]
                cdt_message_not_to_old = ((constants.get_time() - last_target_estimator.time_stamp) <= constants.TRESH_TIME_TO_SEND_MEMORY)
                if cdt_message_not_to_old:
                    self.send_message_targetEstimator(last_target_estimator,receivers)
                    self.time_last_message_targetEstimtor_sent = constants.get_time()

    def send_message_ack_nack(self, message, type_message):
        """
            :description
                1. Reply to a mesage using a ack or a nack
                ack = OK, nack = not OK

            :param
                1. (Message) message      -- Response according this message
                2. (string) type_message  -- "ack","nack" either OK or not OK

        """
        m = MessageCheckACKNACK(constants.get_time(), self.id, self.signature, type_message,
                                message.signature,
                                message.targetRef)
        m.add_receiver(message.sender_id, message.sender_signature)
        self.info_message_to_send.add_message(m)

    def send_message_heartbeat(self):
        """
            :description
                1. Message without meaning, used to inform other agents that the agent is alive
        """

        delta_time = constants.get_time() - self.time_last_heartbeat_sent
        if delta_time > constants.TIME_BTW_HEARTBEAT:
            m = MessageCheckACKNACK(constants.get_time(), self.id, self.signature, "heartbeat", "Hi there !")

            "Message send to every agent define in the room"
            for agent in self.room_representation.agentCams_representation_list:
                if agent.id != self.id:
                    m.add_receiver(agent.id, agent.signature)

            for agent in self.room_representation.agentUser_representation_list:
                if agent.id != self.id:
                    m.add_receiver(agent.id, agent.signature)

            cdt1 = self.info_message_to_send.is_message_with_same_message(m)
            if not cdt1:
                self.info_message_to_send.add_message(m)

            self.time_last_heartbeat_sent = constants.get_time()

    def received_message_targetEstimator(self, message):
        """
            :description
                1. Create a new TargetEstimator from the string description received
                2. Add the new TargetEstimator in the memory

            :param
                1. (Message) message  -- Message received

        """
        s = message.message
        if not (s == ""):
            estimator = TargetEstimator()
            estimator.parse_string(s)
            self.memory.add_target_estimator(estimator)
            # TODO - ici est ce qu'on veut vraiment renvoyer un ack quand on reçoit un target estimator ??
            # TODO - On pourrait considérer l'envoie comme un conseil, si il n'arrive pas c'est comme si il n'était pas pris en compte
            # self.send_message_ack_nack(message, "ack")

    def received_message_ack_nack(self, message):
        """
            :description
                1. Create a new TargetEstimator from the string description received
                2. Add the new TargetEstimator in the memory

            :param
                1. (Message) message --  Message received

        """
        for sent_mes in self.info_message_sent.get_list():
            sent_mes.add_ack_nack(message)

    def received_message_heartbeat(self, message):
        """
            :description
                defines what to do when receive a heartbeat
        """
        for agent in self.room_representation.agentCams_representation_list:

            cdt1 = message.sender_id == agent.id and message.sender_signature == agent.signature
            cdt2 = agent.is_active == False

            if cdt1 and cdt2:
                self.log_main.info("Found someone ! agent cam :" + str(agent.id))
                agent.is_active = True
                agent.camera_representation.is_active = True
                self.log_main.debug(self.room_representation.agentCams_representation_list)
                break

        for agent in self.room_representation.agentUser_representation_list:
            cdt1 = message.sender_id == agent.id and message.sender_signature == agent.signature
            cdt2 = agent.is_active == False
            if cdt1 and not cdt2:
                self.log_main.info("Found someone ! agent user :" + str(agent.id))
                agent.is_active = True
                self.log_main.debug(self.room_representation.agentUser_representation_list)
                break

        """Add heartbeart"""
        self.hearbeat_tracker.add_heartbeat(message, self.log_main)


class HeartbeatCounterAllAgent:
    def __init__(self, agent_id, agent_signature, log=None):
        self.id = agent_id
        self.agent_signature = agent_signature
        self.max_delay = constants.TIME_BTW_HEARTBEAT * constants.TIME_MAX_BTW_HEARTBEAT
        if log is not None:
            log.info("Using hearbeat messages !")
            log.info("Time between two heartbeats of %.02f s", constants.TIME_BTW_HEARTBEAT)
            log.info("Time max between two heartbeats of %.02f s", self.max_delay)
        self.agent_heartbeat_list = []

    def add_heartbeat(self, m, log=None):
        if m.messageType == MessageTypeAgentInteractingWithRoom.HEARTBEAT:
            added = False
            for elem in self.agent_heartbeat_list:
                added = elem.add_heartbeat(m)
                if added:
                    break
            if not added:
                new_heartbeat_counter = HeartbeatCounter(m.sender_id, m.sender_signature, self.max_delay)
                new_heartbeat_counter.add_heartbeat(m)
                self.agent_heartbeat_list.append(new_heartbeat_counter)
                if log is not None:
                    log.info("Add a new heartbeat counter for agent: " + str(m.sender_id))


class HeartbeatCounter:
    def __init__(self, agent_id, agent_signature, max_delay):
        self.agent_id = agent_id
        self.agent_signature = agent_signature
        self.heartbeat_list = []
        self.max_delay = max_delay

    def add_heartbeat(self, m):
        cdt_id = m.sender_id == self.agent_id
        cdt_signature = m.sender_signature == self.agent_signature
        cdt_hearbeat = m.messageType == MessageTypeAgentInteractingWithRoom.HEARTBEAT
        if cdt_id and cdt_signature and cdt_hearbeat:
            self.heartbeat_list.append(m.timestamp)
            return True
        return False

    def is_to_late(self):
        delta = constants.get_time() - self.heartbeat_list[-1]
        return delta > self.max_delay
