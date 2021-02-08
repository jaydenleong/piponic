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

def init_i2c():
   #define i2c object
    i2c = busio.I2C(board.SCL, board.SDA)
    #create object
    ads = ADS.ADS1115(i2c) 
    return ads

class adc_sensors(object):
    def __init__(self):
        self.ads=init_i2c()
        self.leak_sensor = init_leak(self.ads)
        self.pH_sensor = init_pH(self.ads)

    def init_leak(ads):
        chan = AnalogIn(ads,ADS.P0)
        return chan

    def init_ph(ads):
        chan= AnalogIn(ads,ADS.P1)
        return chan

    def init_pH(ads):
        chan= AnalogIn(ads,ADS.P1)
        return chan
       
    def read_leak(self):
        return self.leak_sensor.voltage

    def read_pH(self):
        return calc_pH(self.pH_sensor.voltage)

    def read_ph(self):
        return self.calc_pH(self.pH_sensor.voltage)

    def calc_pH(pH_voltage):
        pH = 7.7 +(pH_voltage-1.65)*(-5.5)
        print('pH:',pH)
        return pH


# def init_leak(ads):
#     #ads = init_i2c()
#     #single channel read
#     chan = AnalogIn(ads,ADS.P0)
#     return chan

# def init_ph(ads):
#     #ads = init_i2c()
#     chan= AnalogIn(ads,ADS.P1)
#     return chan



# #def read_leak():
#     #chan = init_leak()
# #    print('leak voltage', chan.voltage)
# #    return chan.voltage

# def calc_pH(pH_voltage):

#     #formula found at https://raspberrypi.stackexchange.com/questions/96653/ph-4502c-ph-sensor-calibration-and-adc-using-mcp3008-pcf8591-and-ads1115 and adjusted to match east vancouver's tap water pH of 7.7
#     pH = 7.7 +(pH_voltage-1.65)*(-5.5)
#     print('pH:',pH)
#     return pH

# def read_ph():
#     chan = init_pH()
#     print('pH voltage:',chan.voltage)
#     pH = calc_pH(chan.voltage)
#     return pH

# def read_pH():
#     chan = init_pH()
#     print('pH voltage:',chan.voltage)
#     pH = calc_pH(chan.voltage)
#     return pH


