SIZE = 10

""" 
Class representing a FIFO queue as a list (so it is iterable).
Elements are enqueued in the end of the list and dequeued from the beginning (only when queue already full).  
 """


class QueueFIFO:

    def __init__(self):
        self.queue = [None] * SIZE
        self.nextItemIndex = 0
        self.firstItemIndex = 0
        self.empty = True
        self.full = False

    def enqueue(self, elem):
        self.empty = False
        self.queue[self.nextItemIndex] = elem
        self.nextItemIndex = (self.nextItemIndex + 1) % SIZE  # start filling from the beginning when queue full
        if self.nextItemIndex <= self.firstItemIndex:  # will happen when the queue is full
            self.full = True
            self.firstItemIndex = (self.firstItemIndex + 1) % SIZE  # from there on: first == next

    # returns the values held in the queue in chronological order from oldest to newest
    def getQueue(self):
        chronologicalOrder = []
        if self.empty:
            return chronologicalOrder

        index = self.firstItemIndex
        chronologicalOrder.append(self.queue[index])
        index = (index + 1) % SIZE
        while not index == self.nextItemIndex:
            chronologicalOrder.append(self.queue[index])
            index = (index + 1) % SIZE

        return chronologicalOrder

    def isEmpty(self):
        return self.empty
