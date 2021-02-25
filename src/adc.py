'''

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

'''

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn



class adc_sensors(object):
    def __init__(self):
        self.ads=0
        self.init_i2c()
        self.leak_sensor = 0
        self.init_leak()
        self.pH_sensor = 0
        self.init_pH()
        self.battery_sensor=0
        self.init_battery()
        self.internal_leak=0
        self.init_internal_leak()

    def init_i2c(self):
        #define i2c object
        i2c = busio.I2C(board.SCL, board.SDA)
        #create object
        self.ads = ADS.ADS1115(i2c) 

############# Initialize all the ADC pins ##################

    def init_leak(self):
        self.leak_sensor= AnalogIn(self.ads,ADS.P0)
         
    def init_ph(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)

    def init_pH(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)

    def init_battery(self):
        self.battery_sensor= AnalogIn(self.ads,ADS.P2)       

    def init_internal_leak(self):
        self.internal_leak= AnalogIn(self.ads,ADS.P3)     


############### READ functions ############################
    def read_leak(self):
        return self.leak_sensor.voltage

    def read_pH(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-14.7/10)*(-3.3) #formula adjusted for use with a voltage divider to map the 5 V output to 3.3V for use with a 3.3V ADC
        return pH

    #test out an experimental quadratic formula
    def read_pH_ex(self):
        pH_voltage = self.pH_sensor.voltage
        #pH_voltage = pH_voltage*14.7/10 #voltage divider
        pH = -5.6732*pH_voltage**2+6.7868*pH_voltage+12.743
        return pH

    def read_ph(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-14.7/10)*(-3.3)
        return pH

    def read_battery(self):
        return self.battery_sensor.voltage

    def read_internal_leak(self):
        return self.internal_leak.voltage

