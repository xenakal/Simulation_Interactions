SIZE = 10

""" 
Class representing a FIFO queue as a list (so it is iterable).
Elements are enqueued in the end of the list and dequeued from the beginning.  
 """


class queueFIFO:

    def __init__(self):
        self.queue = [None] * SIZE
        self.oldestIndex = 0

    def enqueue(self, elem):
        self.queue[self.oldestIndex] = elem
        self.oldestIndex = (self.oldestIndex + 1) % (SIZE - 1)

    # returns the values held in the queue in chronological order from oldest to newest
    def getQueue(self):
        chronologicalOrder = []
        index = self.oldestIndex
        initialIndex = self.oldestIndex
        allElemsRead = False
        while not allElemsRead:
            chronologicalOrder.append(self.queue[index])
            index = (index + 1) % (SIZE - 1)
            if index == initialIndex:  # all values have been added in the list
                return chronologicalOrder
