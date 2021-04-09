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
import src.device as dev

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
        
        # Amount of time before checking the pH
        self.pH_check_interval_secs = 30

        # Amount of time for pH pump to be on at a time
        self.pH_pump_on_time_secs = 2

        # Sets the mode of the pins that connect to the relay. 
        # If your relay is active low, you want to be in Pull-up mode, otherwise pull-down mode. 
        self.is_relay_active_low = True
        if(self.is_relay_active_low):
            relay.init_pullup(pins.peristaltic_pump)
        else:  
            relay.init(pins.peristaltic_pump)

        # Set the peristaltic pump to initially be OFF
        relay.off(pins.peristaltic_pump)

        # The pH to maintain the system at
        self.device = dev.Device()
        self.desired_pH = self.device.get_config()['target_ph']

        # Check whether to kill thread
        self.killThread = False
    
    def run(self):
        print("Starting pH control loop...")

        # Control loop where pH is checked and if it is too low, pH-increasing solution (KOH, or CaOH) is added
        while not self.killThread:
            try:
                # Get current pH value
                pH = self.adc_sensors.read_pH()

                # Update desired pH based on device configuration
                self.desired_pH = self.device.get_config()['target_ph']

                # desired_pH should be set as the minimum value you want your pH to be at.
                if (pH<=self.desired_pH):	                
                    print('Peristalitic Pump started')
                    # Turn on peristaltic pump
                    relay.on(pins.peristaltic_pump)
                    time.sleep(self.pH_pump_on_time_secs)
                    relay.off(pins.peristaltic_pump)
                
                time.sleep(self.pH_check_interval_secs)
            except:
                print("[ERROR] Exeception on pH control thread, killing thread.")
                break
        
        # Ensure the pump is OFF before exiting
        try:
            relay.off(pins.peristaltic_pump)
        except:
            print("[ERROR] Failed to turn off pH pump when closing")

        print("Killed pH control loop")
        return

    def kill(self):
        self.killThread = True

class waterLevelController(Thread):
    """
    Water level controlling class that executes in its own thread.
    The purpose of this class is to maintain the water level of the
    system within a healthy range
    """

    def __init__(self):
        super().__init__()
        
        # Check if water level is healthy this often
        self.water_level_check_interval_secs = 30

        # If water level is low, turn on solenoid for this long
        self.water_level_on_time_secs = 2

        # Variable to check if we should kill the Thread
        self.killThread = False
        
        # Initalize pin for water level control
        self.is_relay_active_low = True
        if(self.is_relay_active_low):
            relay.init_pullup(pins.Water_level_solenoid)
        else:  
            relay.init(pins.Water_level_solenoid)

        # Make sure water solenoid is OFF at start
        # TODO: What is the difference between off_pu() and regular off()???
        relay.off_pu(pins.Water_level_solenoid)

        # Initialize water level sensor
        self.water_level_sensor = water_level.water_level()

    def kill(self):
        self.killThread = True

    def run(self):
        print("Starting water level control loop")

        # Loop that turns on the water level solenoid if water level is too low
        while not self.killThread:
            try:
                #TODO: double check Benny's water-level control algorithm recommendations

                # If the water level is low, turn on solenoid             
                # TODO: is this always a binary variable for water level??? Should it be threshold?
                # TODO: if leak happens, we keep pumping water!!?
                if(self.water_level_sensor.read() == 0):
                    print("Started water level solenoid")
                    relay.on_pu(pins.Water_level_solenoid)
                    time.sleep(self.water_level_on_time_secs)
                    relay.off_pu(pins.Water_level_solenoid)
                
                # Wait to check again
                time.sleep(self.water_level_check_interval_secs)
            except: 
                print("[ERROR] Exception on water level control thread, killing it")
                break
            
        # Turn off water level solenoid before exiting
        try:
            relay.off_pu(pins.Water_level_solenoid)
        except:
            print("[ERROR] Failed to turn off water level solenoid")

        print("Killed water level control loop")
        return
