from threading import Thread
import time

global cycle
cycle = 0.0

class Hello5Program:  
    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  

    def run(self):
        global cycle
        while self._running:
            time.sleep(5) #Five second delay
            cycle = cycle + 1.0
            print ('5 Second Thread cycle+1.0 - ')

class Hello2Program:  
    def __init__(self):
        self._running = True

    def terminate(self):  
        self._running = False  

    def run(self):
        global cycle
        while self._running:
            time.sleep(2) #Five second delay
            cycle = cycle + 0.5
            print ('5 Second Thread cycle+1.0 - ')

#Create Class
FiveSecond = Hello5Program()
#Create Thread
FiveSecondThread = Thread(target=FiveSecond.run) 
#Start Thread 
FiveSecondThread.start()

#Create Class
TwoSecond = Hello2Program()
#Create Thread
TwoSecondThread = Thread(target=TwoSecond.run) 
#Start Thread 
TwoSecondThread.start()

