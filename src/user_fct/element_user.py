from src.multi_agent.elements.item import Item, create_item_from_string


class ItemUser(Item):
    def __init__(self,id=None):
        '''
            An item is a element used in the simulation and agent needs to exchange information about it
            By default it has an id and signature
        '''
        super().__init__(id)


        """
            Below you can define varibable for this item
        """
        self.user_variable1 = 1000
        self.user_variable2 = 2000
        self.user_variable3 = None

        self.user_not_sent_variable = 10
        self.user_attributes_not_send=['user_not_sent_variable']

        self.item = Item(1)

        """Do not modify below this line"""
        self.user_attributes_not_send += ['user_attributes_not_send']
        self.attributes_not_to_send += self.user_attributes_not_send


    def method1_for_user_item(self):
        self.user_variable1 = self.user_variable2 + self.user_variable3



if __name__ == "__main__":
    item1 = ItemUser(0)
    print(item1.attributes_to_string())
    item2 = create_item_from_string(item1.attributes_to_string())
    print(item2.attributes_to_string())
