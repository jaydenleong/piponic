'''
File: control.py

Purpose: Classes to control pH and water level automatically

Authors: Han Xu, Lynes Chan, Jayden Leong 
Date: March 26, 2021

'''

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from threading import Thread
import RPi.GPIO as GPIO
import time
import src.pins as pins
import src.relay as relay
import src.water_level as water_level
import src.adc as adc

class pHController(Thread):
    """
    PH controlling class that executes in its own thread.
    The purpose of this class is to maintain the pH of the
    system within a healthy range
    """

    def __init__(self):
        super().__init__()
        
        # Get ADC sensors object to read pH
        self.adc_sensors = adc.adc_sensors()
        
        # sets the mode of the pins that connect to the relay. 
        # If your relay is active low, you want to be in Pull-up mode, otherwise pull-down mode. 
        self.relay_pullup = 1 
        
        # The pH to maintain the system at
        # TODO: update this value
        self.desired_pH = 7
    
    def run(self):
        self.pH_control_loop()

   #Control loop where pH is checked and if it is too low, pH-increasing solution (KOH, or CaOH) is added
    def pH_control_loop(self):
        print('pH control loop started...')

        # Initialize relay pins
        if(self.relay_pullup):
            relay.init_pullup(pins.peristaltic_pump)
        else:  
            relay.init(pins.peristaltic_pump)

        # start of loop    
        while True:
            time.sleep(2)
            print('pH control loop start')

            pH = self.adc_sensors.read_pH()
            if (pH<=self.desired_pH):	# desired_pH should be set as the minimum value you want your pH to be at.
                print('Peristalitic Pump started')
                ## Turn on peristaltic pump for 2 seconds
                #relay.on(pins.peristaltic_pump)
                #time.sleep(2)

                #relay.off(pins.peristaltic_pump)
                #time.sleep(2)

class waterLevelController(Thread): 
    """
    Water level controlling class that executes in its own thread.
    The purpose of this class is to maintain the water level of the
    system within a healthy range
    """

    def __init__(self):
        super().__init__()

        self.relay_pullup = 1

    def run(self):
        self.water_level_control_loop()

    def water_level_control_loop(self):

        # TODO decouple control?
        if(self.relay_pullup):
            relay.init_pullup(pins.Water_level_solenoid)
        else:  
            relay.init(pins.Water_level_solenoid)

        while True:
            print("Water level Loop!!!!!@")
            #TODO: double check Benny's water-level control algorithm recommendations

            #if the water level is low, turn on solenoid for 2 seconds
            #if(self.read_level==0):
            #    relay.on_pu(pins.Water_level_solenoid)
            #    time.sleep(2)

            #    relay.off_pu(pins.Water_level_solenoid)
            #    time.sleep(2)
            
            
            #print('valve opened')
            time.sleep(6)
