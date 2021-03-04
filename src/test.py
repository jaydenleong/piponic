from threading import Thread
import time

global cycle
cycle = 0.0

To use treading a new class is created Hello5Program this will be run in a new program thread. The class has three definitions. The __init__ definition initialises the class setting running parameter to true. The terminate definition is used to exit the class. The run definition is where the main class code is written. The global variable cycle is defined here again linking it to the main programs global variable.  

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
            print "5 Second Thread cycle+1.0 - ", cycle
            #Create Class
FiveSecond = Hello5Program()
#Create Thread
FiveSecondThread = Thread(target=FiveSecond.run) 
#Start Thread 
FiveSecondThread.start()

The rest of the main program has a loop increasing cycle by 0.1 and printing the result. When cycle is greater than 5 the program exits. As the program exits it must terminate the class by calling the terminate procedure. If the terminate procedure is not called the program will never exit.  

Exit = False #Exit flag
while Exit==False:
 cycle = cycle + 0.1 
 print "Main Program increases cycle+0.1 - ", cycle
 time.sleep(1) #One second delay
 if (cycle > 5): Exit = True #Exit Program

FiveSecond.terminate()
print "Goodbye :)"
