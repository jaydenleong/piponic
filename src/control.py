#Python script to read analog voltage values from ADS1115 16bit ADC with PGA
#Author: Carson Berry 
#Date: February 2nd, 2021
#usage: 
#    python3
#    import src.adc as adc
#    sensors = adc.adc_sensors()
#    sensors.read_leak()
#    sensors.read_pH()
# Reference provided at: https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython


import RPi.GPIO as GPIO
import time
import board
import threading
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn



# Add timers for different outputs ex. ph_timer, water_level_timer, temp_timer

class adc_sensors(object):


    
  



    def init_i2c(self):
        #define i2c object
        i2c = busio.I2C(board.SCL, board.SDA)
        #create object
        self.ads = ADS.ADS1115(i2c) 

    def init_leak(self):
        self.leak_sensor= AnalogIn(self.ads,ADS.P0)
        
    def water_level_init(self):
        self.level = 0
        self.setup()
        self.read() # update level 
         
         
    def init_ph(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)
        
        
    def __init__(self):
    
        self.ads=0
        self.init_i2c()
        self.leak_sensor = 0
        self.init_leak()
        self.pH_sensor = 0
        self.init_ph()
       
    def read_leak(self):
        return self.leak_sensor.voltage

    def read_pH(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-14.7/10)*(-3.3) #formula adjusted for use with a voltage divider to map the 5 V output to 3.3V for use with a 3.3V ADC
        return pH
        
    def read_waterlevel(self):
        try:
            #self.level = GPIO.input(pins.WATER_LEVEL)
            self.level = GPIO.input(11)
            return self.level
        except:
            GPIO.cleanup()        
            return -1
        
    def pump_open(self):
        print ('pump opened')
        GPIO.output(9,GPIO.HIGH) #9 for the relay pin on pH pump
        time.sleep(1)
        GPIO.output(9,GPIO.LOW)
    #Here I add the function of the timer
    #This code here correspond update the data at default time
    #Using threading method
    def test_ph(self):
        while True:
            read_ph()
            if (int(read_ph()<= 11)):
                pump_open()
                time.sleep(10)
                
    def test_waterlevel(self):
        while True: 
            read_leak()
            if (read_waterlevel()== -1):
                GPIO.output(8,HIGH)
                time.sleep(1)
                GPIO.output(8,GPIO.LOW)
                time.sleep(20)
                 
 
thread1 = threading.Thread(target=adc_sensor.test_ph())
thread2 = threading.Thread(target=adc_sensor.test_waterlevel())
    
thread1.start()    
thread2.start()
