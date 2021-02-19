
Python script to read analog voltage values from ADS1115 16bit ADC with PGA
Author: Carson Berry 
Date: February 2nd, 2021
usage: 
    python3
    import src.adc as adc
    sensors = adc.adc_sensors()
    sensors.read_leak()
    sensors.read_pH()
Reference provided at: https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython


import RPi.GPIO as GPIO
import time
import board
import threading
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn



# Add timers for different outputs ex. ph_timer, water_level_timer, temp_timer

class adc_sensors(object):


    
    

    def __init__(self):
    
        self.ads=0
        self.init_i2c()
        self.leak_sensor = 0
        self.init_leak()
        self.pH_sensor = 0
        self.init_pH()

    def init_i2c(self):
        #define i2c object
        i2c = busio.I2C(board.SCL, board.SDA)
        #create object
        self.ads = ADS.ADS1115(i2c) 

    def init_leak(self):
        self.leak_sensor= AnalogIn(self.ads,ADS.P0)
         
    def init_ph(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)

    def init_pH(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)
       
    def read_leak(self):
        return self.leak_sensor.voltage

    def read_pH(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-1.65)*(-3.3)
        return pH

    def read_ph(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-1.65)*(-3.3)
        return pH
        
    def pump_open():
        print 'pump opened'
        GPIO.output(9,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(9,GPIO.LOW)
    #Here I add the function of the timer
    #This code here correspond update the data at default time
    #Using threading method
    def test_ph():
        while True:
            read_ph()
            if (int(read_ph()<= 6)):
                pump_open()
                
        
    thread = threading.Thread(target=test_ph)
    thread.start()    
        
  
            
    
        
