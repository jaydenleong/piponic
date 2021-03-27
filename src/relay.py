'''
Controlling the 4 relay channels with the raspberry pi zero w
RPi is connected to 4 relay channels on GPIO26, GPIO19, GPIO13, GPIO06 (in this order)


Author: Carson Berry
Date: February 2, 2021

Inputs: null 

Outputs: zero if successfull 

Usage: 
import relay
relay.init(src.pins.RELAY1)
relay.on(src.pins.RELAY1)
relay.off(src.pins.RELAY1)

'''

import RPi.GPIO as GPIO
import time
import src.pins


# set all the pins to output pins

GPIO.setmode(GPIO.BCM) # GPIO Assign mode so that the numbers below are the GPIO assigned names


#Default pull up configuration
def init(pin):
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin,False) #set normally low

# if your relay block is active LOW (you'll be pulling down the output), you'll need to init to high (pull-up default)
def init_pullup(pin):
    GPIO.setup(pin, GPIO.OUT ) #confusing, but we turn on the pull-up resistor, so that the default value is high. 
    GPIO.output(pin, True)


#example function of turning on relay 1.

def on(pin):
    try:
        GPIO.output(pin,True)

    except KeyboardInterrupt:
        GPIO.cleanup()
        return -1
    
def off(pin):
    try:
        GPIO.output(pin,False)

    except KeyboardInterrupt:
        GPIO.cleanup()
        return -1

def on_pu(pin):
    try:
        GPIO.output(pin,False)

    except KeyboardInterrupt:
        GPIO.cleanup()
        return -1
    
def off_pu(pin):
    try:
        GPIO.output(pin,True)

    except KeyboardInterrupt:
        GPIO.cleanup()
        return -1




#Demo function to verify that the relay works and that ll your connections are good
#note: listen for the satisfying cockroach clickitty clack but don't wear out the relays!

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



