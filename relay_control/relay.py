''' Controlling the 4 relay channels with the raspberry pi zero w RPi is connected to 4 relay channels on GPIO26, GPIO19, GPIO13, GPIO06 (in this order) 

Author: Carson Berry
Date: February 2, 2021

Inputs: null 

Outputs: zero if successfull 

Usage: 
import relay
relay.on1()
relay.off1()
relay.demo()


'''

import RPi.GPIO as GPIO
import time


# set all the pins to output pins

GPIO.setmode(GPIO.BCM) # GPIO Assign mode so that the numbers below are the GPIO assigned names
in1 = 26
in2 = 19
in3 = 13
in4 = 6


def init_one():
    GPIO.setup(in1, GPIO.OUT)
 #set normally low (relay off
    GPIO.output(in1,False)
def init_two():
    GPIO.setup(in2, GPIO.OUT)
    GPIO.output(in2,False)
def init_three():
    GPIO.setup(in3, GPIO.OUT)
    GPIO.output(in3,False)
def init_four():
    GPIO.setup(in4, GPIO.OUT)
    GPIO.output(in4,False)



#example function of turning on relay 1. Ti's almost too simple toi make a function for. We need to ahve a discussion about what this should look like...

def on1():
    try:
        GPIO.output(in1,True)
        return 0
    except KeyboardInterrupt:
        GPIO.cleanup()
        return -1

def off1():
    try:
        GPIO.output(in1,False)
        return 0

    except KeyboardInterrupt:
        GPIO.cleanup()
        return -1





#Demo function to verify that the relay works and that ll your connections are good
#note: listen for the satisfyuing cockroach clicktty clack but don't wear out the relays!

def demo():
    try:
        while True:
          for x in range(5):
                GPIO.output(in1, True)
                time.sleep(0.1)
                GPIO.output(in1, False)
                GPIO.output(in2, True)
                time.sleep(0.1)
                GPIO.output(in2, False)
          
          GPIO.output(in1,True)
          GPIO.output(in2,True)

          for x in range(4):
                GPIO.output(in1, True)
                time.sleep(0.05)
                GPIO.output(in1, False)
                time.sleep(0.05)
          GPIO.output(in1,True)

          for x in range(4):
                GPIO.output(in2, True)
                time.sleep(0.05)
                GPIO.output(in2, False)
                time.sleep(0.05)
          GPIO.output(in2,True)



    except KeyboardInterrupt:
        GPIO.cleanup()



