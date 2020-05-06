import threading
# from elements.room import*
from src.multi_agent.agent.agent import *
from src.multi_agent.behaviour.memory import *
from src.multi_agent.communication.message import *
from src import constants

import src.multi_agent.elements.room

class BroadcastTypes:
    ALL = "all"
    AGENT_CAM = "agentCams"
    AGENT_USER = "agentUser"

class MessageTypeAgentInteractingWithRoom(MessageType):
    HEARTBEAT = "heartbeat"
    AGENT_ESTIMATOR = "agentEstimator"
    TARGET_ESTIMATOR = "targetEstimator"


class AgentInteractingWithRoomRepresentation(AgentRepresentation):
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


        "Create his own thread"
        self.thread_is_running = 1
        self.main_thread = None

        self.table_target_agent_lastTimeSent = AllItemSendToAtTime()
        self.table_agent_agent_lastTimeSent = AllItemSendToAtTime()
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
        self.main_thread = threading.Thread(target=self.thread_run, args=[room])

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

    def clear(self,reset=False):
        """
            :description
                1. Function to call to stop the agent
        """
        "Save data"
        if constants.SAVE_DATA and not reset:
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
            save_in_csv_file_dictionnary(
                constants.ResultsPath.SAVE_LOAD_DATA_AGENT_ESTIMATOR+str(self.id),
                self.memory.memory_agent_from_agent.to_csv())
            self.log_main.info("Data saved !")


        "Clear"
        self.thread_is_running = 0
        while self.main_thread.is_alive():
            pass
        mbox = mailbox.mbox(constants.NAME_MAILBOX + str(self.id))
        mbox.close()
        self.log_main.info("Agent cleared \n")

    def pick_data(self, choice):
        if choice == constants.AgentDataToWorkWith.Data_measured:
            return self.memory.memory_measured_from_target
        if choice == constants.AgentDataToWorkWith.Best_estimation:
            return self.memory.memory_best_estimations_from_target
        elif choice == constants.AgentDataToWorkWith.Prediction_t_1:
            return self.memory.memory_predictions_order_1_from_target
        elif choice == constants.AgentDataToWorkWith.Prediction_t_2:
            return self.memory.memory_predictions_order_2_from_target

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
        if rec_mes.messageType == MessageTypeAgentInteractingWithRoom.TARGET_ESTIMATOR or rec_mes.messageType == MessageTypeAgentInteractingWithRoom.AGENT_ESTIMATOR:
            self.received_message_itemEstimator(rec_mes)
            self.info_message_received.del_message(rec_mes)
        elif rec_mes.messageType == MessageType.ACK or rec_mes.messageType == MessageType.NACK:
            self.received_message_ack_nack(rec_mes)
            self.info_message_received.del_message(rec_mes)
        elif rec_mes.messageType == MessageTypeAgentInteractingWithRoom.HEARTBEAT:
            self.received_message_heartbeat(rec_mes)
            self.info_message_received.del_message(rec_mes)

    def broadcast_message(self, message,broadcast_choice=None,receivers = None):
        """
        :description:
            Broadcasts the message to every other known agent.
        :param message: message of type MessageCheckACKNACK()
        """

        if receivers is None:
            receivers = []

        if broadcast_choice == BroadcastTypes.AGENT_CAM :
            broadcast_list = self.room_representation.agentCams_representation_list
        elif broadcast_choice == BroadcastTypes.AGENT_USER:
            broadcast_list = self.room_representation.agentUser_representation_list
        elif broadcast_choice == BroadcastTypes.ALL:
            broadcast_list = self.room_representation.agentCams_representation_list+\
                             self.room_representation.agentUser_representation_list
        else:
            print("can't find the right list to broadcast")
            broadcast_list = []

        if len(receivers) == 0:
            for agent in broadcast_list:
                if agent.id != self.id:
                    message.add_receiver(agent.id, agent.signature)
        else:
            for receiver in receivers:
                message.add_receiver(receiver[0], receiver[1])

        cdt1 = self.info_message_to_send.is_message_with_same_message(message)
        if not cdt1:
               self.info_message_to_send.add_message(message)

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
                    self.log_main.info("Agent : " + str(
                        agent_to_suppress.id) + "at:  %.02fs is not connected anymore, last heartbeat : %.02f s" %
                                       (constants.get_time(), heartbeat.heartbeat_list[-1]))

    def send_message_heartbeat(self):
        """
            :description
                1. Message without meaning, used to inform other agents that the agent is alive
        """

        delta_time = constants.get_time() - self.time_last_heartbeat_sent
        if delta_time > constants.TIME_BTW_HEARTBEAT:
            m = MessageCheckACKNACK(constants.get_time(), self.id, self.signature, "heartbeat", "Hi there !")

            "Message send to every agent define in the room"
            self.broadcast_message(m,BroadcastTypes.ALL)
            self.time_last_heartbeat_sent = constants.get_time()

    def received_message_heartbeat(self, message):
        """
            :description
                defines what to do when receive a heartbeat
        """
        list_to_check = self.room_representation.agentCams_representation_list\
        + self.room_representation.agentUser_representation_list

        for agent in list_to_check:
            if agent.id != self.id:
                cdt1 = message.sender_id == agent.id and message.sender_signature == agent.signature
                cdt2 = (agent.is_active == False)

                if cdt1 and cdt2:
                    agent.is_active = True

                    import src.multi_agent.agent.agent_interacting_room_camera as agentCamRep
                    import src.multi_agent.agent.agent_interacting_room_user as agentUserRep
                    if isinstance(agent,agentCamRep.AgentCamRepresentation):
                        self.log_main.info("Found someone ! agent cam :" + str(agent.id))
                        agent.camera_representation.is_active = True
                    elif isinstance(agent,agentUserRep.AgentUserRepresentation):
                        self.log_main.info("Found someone ! agent user :" + str(agent.id))


                    self.log_main.debug(self.room_representation.agentCams_representation_list)
                    break

        """Add heartbeart"""
        self.hearbeat_tracker.add_heartbeat(message, self.log_main)

    def send_message_itemEstimator(self, itemEstimation, receivers=None):
        """
                  :description
                      1. Create a message based on a TargetEstimator
                      2. Place it in the list message_to_send

                  :param
                      1. (TargetEstimator) targetEstimator -- TargetEstimator, see the class
                      2. (list) receivers                  -- [[receiver_id,receiver_signature], ... ], data to
                                                              tell to whom to send the message.

              """

        s = itemEstimation.to_string()
        s = s.replace("\n", "")
        s = s.replace(" ", "")

        message_type = itemEstimation.item_type
        reference_to_target = itemEstimation.item.id

        m = MessageCheckACKNACK(constants.get_time(), self.id, self.signature, message_type, s, reference_to_target)
        self.broadcast_message(m,BroadcastTypes.AGENT_CAM,receivers)

    def send_message_timed_itemEstimator(self, item_estimator, delta_time, receivers=None):


        cdt_message_not_to_old = ((constants.get_time() - item_estimator.time_stamp) <= constants.TRESH_TIME_TO_SEND_MEMORY)
        if cdt_message_not_to_old:

            table_time_sent = None
            if item_estimator.item_type == ItemEstimationType.TargetEstimation:
                table_time_sent = self.table_target_agent_lastTimeSent
            elif item_estimator.item_type == ItemEstimationType.AgentEstimation:
                table_time_sent = self.table_agent_agent_lastTimeSent

            send_message_to_agent = []
            if receivers is None:
                receivers = []

            if len(receivers) == 0:
                for agent in self.room_representation.agentCams_representation_list:
                    if agent.id != self.id:
                        if table_time_sent.should_sent_item_to_agent(item_estimator.item_id, agent.id, delta_time):
                            table_time_sent.sent_to_at_time(item_estimator.item_id, agent.id)
                            send_message_to_agent.append((agent.id, agent.signature))
            else:
                for receiver in receivers:
                    if table_time_sent.should_sent_item_to_agent(item_estimator.item_id, receiver[0], delta_time):
                        table_time_sent.sent_to_at_time(item_estimator.item_id, receiver[0])
                        send_message_to_agent.append((receiver[0], receiver[1]))

            if len(send_message_to_agent) > 0:
                self.send_message_itemEstimator(item_estimator, send_message_to_agent)

    def received_message_itemEstimator(self, message):
        """
            :description
                1. Create a new TargetEstimator from the string description received
                2. Add the new TargetEstimator in the memory

            :param
                1. (Message) message  -- Message received

        """
        s = message.message
        if not (s == ""):
            if message.messageType == ItemEstimationType.TargetEstimation:
                estimator =ItemEstimation()
                estimator.parse_string(s)
                self.memory.add_target_estimator(estimator)
            elif message.messageType == ItemEstimationType.AgentEstimation:
                estimator = ItemEstimation()
                estimator.parse_string(s)
                self.memory.add_agent_estimator(estimator)

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
            new_heartbeat_counter = HeartbeatCounter(m.sender_id, m.sender_signature, self.max_delay)

            try:
                old_heartbeat_counter_index = self.agent_heartbeat_list.index(new_heartbeat_counter)
                old_heartbeat_counter = self.agent_heartbeat_list[old_heartbeat_counter_index]
                old_heartbeat_counter.add_heartbeat(m)
                log.debug("Receive heartbeat from agent: %d at time %.02f "%(m.sender_id,constants.get_time()))

            except ValueError:
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

    def __eq__(self, other):
        return self.agent_id == other.agent_id and self.agent_signature == other.agent_signature

class AllItemSendToAtTime:
    def __init__(self):
        self.item_list = []

    def sent_to_at_time(self, target_id, agent_id):
        new_itemSendToAtTime = ItemSendToAtTime(target_id)
        try:
            old_itemSendToAtTime_index = self.item_list.index(new_itemSendToAtTime)
            old_itemSendToAtTime = self.item_list[old_itemSendToAtTime_index]
            old_itemSendToAtTime.sent_to_at_time(agent_id)

        except ValueError:
            new_itemSendToAtTime.sent_to_at_time(agent_id)
            self.item_list.append(new_itemSendToAtTime)

    def to_string(self):
        s = "Test \n"
        for elem in self.item_list:
            s += elem.to_string()
        return s

    def should_sent_item_to_agent(self, target_id, agent_id, delta_time):
        new_itemSendToAtTime = ItemSendToAtTime(target_id)
        try:
            old_itemSendToAtTime_index = self.item_list.index(new_itemSendToAtTime)
            old_itemSendToAtTime = self.item_list[old_itemSendToAtTime_index]
            return old_itemSendToAtTime.should_sent_agent(agent_id, delta_time)

        except ValueError:
            new_itemSendToAtTime.should_sent_agent(agent_id, delta_time)
            self.item_list.append(new_itemSendToAtTime)
            return True


class ItemSendToAtTime:
    def __init__(self, item_id):
        self.item_id = item_id
        self.agentTime_list = []

    def sent_to_at_time(self, agent_id):
        new_agent_time = AgentTime(agent_id)
        try:
            old_agent_time_index = self.agentTime_list.index(new_agent_time)
            old_agent_time = self.agentTime_list[old_agent_time_index]
            old_agent_time.time = constants.get_time()
        except ValueError:
            self.agentTime_list.append(new_agent_time)

    def should_sent_agent(self, agent_id, delta_time):
        new_agent_time = AgentTime(agent_id)
        try:
            old_agent_time_index = self.agentTime_list.index(new_agent_time)
            old_agent_time = self.agentTime_list[old_agent_time_index]
            return new_agent_time.time - old_agent_time.time > delta_time

        except ValueError:
            self.agentTime_list.append(new_agent_time)
            return True

    def to_string(self):
        s = "item %.02f agent:" % self.item_id
        for elem in self.agentTime_list:
            s += "%.02f t: %.2f s " % (elem.agent_id, elem.time)

        return s + "\n"

    def __eq__(self, other):
        return self.item_id == other.item_id


class AgentTime():
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.time = constants.get_time()

    def __eq__(self, other):
        return self.agent_id == other.agent_id




