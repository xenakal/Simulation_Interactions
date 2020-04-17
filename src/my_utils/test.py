import time

from src import constants


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
            old_agent_time.time = time.time()
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
        s = "item %.02f agent:"%self.item_id
        for elem in self.agentTime_list:
            s += "%.02f t: %.2f s "%(elem.agent_id,elem.time)

        return s+"\n"

    def __eq__(self, other):
        return self.item_id == other.item_id


class AgentTime():
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.time = time.time()

    def __eq__(self, other):
        return self.agent_id == other.agent_id


list_test = AllItemSendToAtTime()
print(list_test.to_string())
list_test.should_sent_item_to_agent(1,1,5)
print(list_test.to_string())
list_test.should_sent_item_to_agent(2,0,5)
print(list_test.to_string())
list_test.should_sent_item_to_agent(1,0,5)
time.sleep(1)
print(list_test.to_string())
list_test.sent_to_at_time(1,0)
print(list_test.to_string())