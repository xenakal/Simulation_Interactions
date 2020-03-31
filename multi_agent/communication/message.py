import numpy as np
import random
import re


class MessageType:
    ACK = "ack"
    NACK = "nack"


class Message:
    """
        Class Message.

        Description : This class describe a standart message use to communicate between targets

            :param
                1. (int) timestamp                   -- time at which the message is created
                2. (int) signature                   -- random number associated to every message
                3. (int) sender_id                   -- define which agent is sending the message
                4. (int) sender_signature            -- define which agent is sending the message
                5. (int) target_reference            -- target_id to know to which agent it refering to, -1 if it does
                                                        not refer to any particular target (ex : heartbeat)
                6. (string) message_type             -- string  to cleary and quickly identify the message
                                                        (ex "request","ack","nack","heartbeat","information", ...)
                7. (string) message                  -- string that can be send and contain a particular message
                                                        (ex: memory)

            :attibutes
                1. (int) timestamp                   -- time at which the message is created
                2. (int) signature                   -- random number associated to every message
                3. (int) sender_id                   -- define which agent is sending the message
                4. (int) sender_signature            -- define which agent is sending the message
                3. (list) receiver_id_and_signature  -- [[(int),(int)],...], define which agent will receive the message
                                                        , multiple agent can be set
                5. (list) remaining_receiver         --  [[(int),(int)],...] remaining receiver are the receiver
                                                        to which the message was not delivered.
                6. (int) target_reference            -- target_id to know to which agent it refering to, -1
                                                        if it does not refer to any particular target (ex : heartbeat)
                7. (string) message                  -- string that can be send and contain a particular message
                                                        (ex: memory)
                8. (string) message_type             -- string  to cleary and quickly identify the message
                                                        (ex "request","ack","nack","heartbeat","information", ...)
    """

    def __init__(self, timestamp, sender_id, sender_signature, message_type, message, target_id=-1):
        """Message informations"""
        self.timestamp = timestamp
        self.signature = int(random.random() * 10000000000000000)

        """Delivery informations"""
        self.sender_id = int(sender_id)
        self.sender_signature = int(sender_signature)
        self.receiver_id_and_signature = []
        self.remaining_receiver = []
        self.target_id = target_id

        """Content"""
        self.targetRef = target_id
        self.message = message
        self.messageType = message_type

    def get_receiver_number(self):
        """
        :return
            1. (int) -- number of receiver
        """
        return len(self.receiver_id_and_signature)

    def add_receiver(self, receiver_id, receiver_signature):
        """
        :param
            1.(int) receiver_id           -- agent's id
            2.(int) receiver_signature    -- agent's signature

        :return / modify vector
            - append information to receiver_id_and_signature and remaing_reiceiver list
        """

        if int(receiver_signature) >= 100:
            self.receiver_id_and_signature.append([int(receiver_id), int(receiver_signature)])
            self.remaining_receiver.append([receiver_id, receiver_signature])

    def clear_receiver(self):
        """
        :return / modify vector
            1. set list related to receiverd to empty list

        """
        self.receiver_id_and_signature = []
        self.remaining_receiver = []

    def notify_send_to(self, receiver_id, receiver_signature):
        """
        :param
            1.(int) receiver_id           -- agent's id
            2.(int) receiver_signature    -- agent's signature

        :return / modify vector
            1. suppress information from remaing_reiceiver list
        """

        for message in self.remaining_receiver:
            if message[0] == receiver_id and message[1] == receiver_signature:
                self.remaining_receiver.remove(message)

    def is_message_sent_to_every_receiver(self):
        """
        :param
            1.(int) receiver_id           -- agent's id
            2.(int) receiver_signature    -- agent's signature

        :return / modify vector
            1. True if the remaningReceiver list is empty, else false.
        """
        if len(self.remaining_receiver) == 0:
            return True
        else:
            return False

    """
    :param
        - s, message in a string form
    :effect 
        - modify every attribute of the self, to make it match with it string description.
          see class aboved description for detailed information  on each attribute
    """

    def parse_string(self, s):
        """
            :params
                1.(string) s -- string representing a Message, use the method to_string().

             :return / modify vector
                1. Set all the attributes from self to the values described in the sting representation.

        """

        try:
            self.clear_receiver()
            s = s.replace("\n", "")
            s = s.replace(" ", "")

            attribut = re.split("Timestamp:|message#:|From:|sender#|Receiverlist:|Type:|target:|Message:", s)
            self.timestamp = float(attribut[1])
            self.signature = int(attribut[2])
            self.sender_id = int(attribut[3])
            self.sender_signature = int(attribut[4])
            receivers = re.split("To:", attribut[5])
            for receiver in receivers:
                if not receiver == "":
                    try:
                        info = receiver.split("receiver#")
                        self.add_receiver(info[0], info[1])
                    except IndexError:
                        print("error message class in parse_string()")

            self.messageType = attribut[6]
            self.targetRef = attribut[7]
            self.message = attribut[8]

        except IndexError:
            print("erreur message class in parse_string()")

    def to_string(self):
        """
               :return / modify vector
                      1. (string)   -- description of the targetRepresentation
        """
        s1 = "Timestamp: " + str(self.timestamp) + ' message#:' + str(self.signature) + "\n"
        s2 = "From: " + str(self.sender_id) + " sender#" + str(self.sender_signature) + "\nReceiver list : \n"
        s3 = ""
        for receiver in self.receiver_id_and_signature:
            s3 = s3 + "To: " + str(receiver[0]) + " receiver#" + str(receiver[1]) + "\n"

        s4 = 'Type: ' + str(self.messageType) + " target: " + str(self.targetRef) + " Message: "
        base = s1 + s2 + s3 + s4
        return base + str(self.message) + "\n"

    def is_approved(self):
        # TODO: maybe check if ACK received, or not: think about that
        return True

class MessageCheckACKNACK(Message):
    """
        Class MessagecheckACKNACK enxtend Message.

        Description : it adds a confirmation step (ack or nack) that refers to a message sent.

            :param
                1. (int) timestamp                   -- time at which the message is created
                2. (int) signature                   -- random number associated to every message
                3. (int) sender_id                   -- define which agent is sending the message
                4. (int) sender_signature            -- define which agent is sending the message
                5. (int) target_reference            -- target_id to know to which agent it refering to, -1
                                                        if it does not refer to any particular target (ex : heartbeat)
                6. (string) message_type             -- string  to cleary and quickly identify the message
                                                        (ex "request","ack","nack","heartbeat","information", ...)
                7. (string) message                  -- string that can be send and contain a particular message
                                                        (ex: memory)
                8. (list) ack                        -- ([Message_Check_ACK_NACK,...]), every ack associated
                                                        to a message can be added
                9. (list) nack                       -- ([Message_Check_ACK_NACK,...]), every  nack associated
                                                        to a message can be added

            :attibutes
                1. (int) timestamp                   -- time at which the message is created
                2. (int) signature                   -- random number associated to every message
                3. (int) sender_id                   -- define which agent is sending the message
                4. (int) sender_signature            -- define which agent is sending the message
                3. (list) receiver_id_and_signature  -- [[(int),(int)],...], define which agent will receive the message
                                                        , multiple agent can be set
                5. (list) remaining_receiver         --  [[(int),(int)],...] remaining receiver are the receiver
                                                        to which the message was not delivered.
                6. (int) target_reference            -- target_id to know to which agent it refering to, -1
                                                        if it does not refer to any particular target (ex : heartbeat)
                7. (string) message                  -- string that can be send and contain a particular message
                                                        (ex: memory)
                8. (string) message_type             -- string  to cleary and quickly identify the message
                                                        (ex "request","ack","nack","heartbeat","information", ...)


            :notes
                all that you need is:
                is_approved()  check is every receiver approved the message by sending a ack
                is_not_approved() check is at least one of the receiver sent a nack
    """

    def __init__(self, time_stamp, sender_id, sender_signature, message_type, message, target_id=-1):
        self.ack = []
        self.nack = []
        super().__init__(time_stamp, sender_id, sender_signature, message_type, message, target_id)

    def get_ack_number(self):
        """
          :return
              1. (int) -- give the number of ack received in respond to the message sent
        """
        return len(self.ack)

    def get_nack_number(self):
        """
          :return
            1.(int) --  give the number of nack received in respond to the message sent
        """
        return len(self.nack)

    def is_not_approved(self):
        """
          :return
              1.(bool) True is a nack was receive, then one of the agent does not agree with the message
              2.       False if no nack, but it does not mean every agent has agreed. (see is approved for this purpose)
        """
        if self.get_nack_number() > 0:
            return True
        else:
            return False

    def is_approved(self):
        """
          :return
              1.(bool) True is a acks received = the number of receiver, so that every receiver has agreed.
              2.       False otherwise
        """
        if int(self.get_ack_number()) >= int(self.get_receiver_number()):
            return True
        else:
            return False

    def add_ack_nack(self, rec_message):
        """
          :param
                1.(Messsage) rec_message -- message ack or nack type that should be link to self.
          :return
                1. return True if add succesfully, false otherwise
        """
        if rec_message.messageType == MessageType.ACK or rec_message.messageType == MessageType.NACK:
            if self.signature == int(rec_message.message):
                if rec_message.messageType == MessageType.ACK:
                    self.ack.append(rec_message)
                elif rec_message.messageType == MessageType.NACK:
                    self.nack.append(rec_message)
            return True
        else:
            return False

    def get_message_in_ack_nack(self):
        """
             :return
                 1. (string) -- describe every attribut in a string format.
        """
        if self.messageType == MessageType.ACK or self.messageType == MessageType.NACK:
            message_in = Message(0, 0, 0, 0, 0)
            message_in.parse_string(self.to_string())
        else:
            message_in = None
        return message_in


class ListMessage:
    """
        Class ListMessage.

        Description : To deal with multiple messages

            :attributes
                1. (string) name       -- name for the file
                2. (list) list_message -- list containing all the message

            :notes
                Message  can be automatically removed from the list after a time t
                using remove_message_after_a_given_time
    """

    def __init__(self, name):
        self.name = name
        self.list_message = []

    def get_size(self):
        """
              :return
                  1. (int) -- number of messages in the list.
        """
        return len(self.list_message)

    def get_list(self):
        """
              :return
                  1. (list) -- a copy from the list.
        """
        return self.list_message.copy()

    def add_message(self, message):
        """
          :param
                1.(Message) message
          :return
                1. add a message in the list
        """
        self.list_message.append(message)

    def del_message(self, message):
        """
          :param
                1.(Message) message
          :return
                1. remove a message in the list
        """
        self.list_message.remove(message)

    def remove_message_after_given_time(self, time, delta_time):
        """
           :param
                 1.(int) time        -- actual time
                 2.(int) delta_time  -- difference time to sort the message to suppress
           :return
                 1. add a message in the list
         """
        for message in self.list_message:
            if message.timestamp + delta_time <= time:
                self.list_message.remove(message)

    def is_message_in_the_list(self, message_to_find):
        """
              :param
                    1.(int) time        -- actual time
                    2.(int) delta_time  -- difference time to sort the message to suppress
              :return
                    1. add a message in the list
        """
        for message in self.list_message:
            if message.signature == message_to_find.signature:
                return True
        return False

    def is_message_with_same_message(self, message_to_find):
        """
              :param
                    1.(Message) message_to_find
              :return
                    1. True if the Message fills the criteria
        """
        for message in self.list_message:
            if message.message == message_to_find.message:
                return True
        return False

    def is_message_with_same_type_same_agent_ref(self, message_to_find):
        """
              :param
                    1.(Message) message_to_find
              :return
                    1. True if the Message fills the criteria
        """
        for message in self.list_message:
            if message.targetRef == message_to_find.targetRef and message.messageType == message_to_find.messageType:
                return True
        return False

    def to_string(self):
        """
               :return / modify vector
                      1. (string)   -- description of the targetRepresentation
        """
        s = self.name + "\n"
        for message in self.list_message:
            s = s + message.to_string() + "\n"
        return s
