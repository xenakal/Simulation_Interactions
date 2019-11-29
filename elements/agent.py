import logging
import threading
import time

class Agent:
    def __init__(self, idAgent):
        self.id = idAgent
        
        self.thread_pI = threading.Thread(target=self.thread_processImage)
        self.thread_rL = threading.Thread(target=self.thread_recLoop)
        
        self.thread_pI.start()
        self.thread_rL.start()
        

    def thread_processImage(self):
        print("hello here")
     
    def thread_recLoop(self):
        print("hello there")
  
if __name__ == "__main__":
    agent = Agent(0)
    
    