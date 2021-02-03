'''

Python script to read analog voltage values from ADS1115 16bit ADC with PGA
Author: Carson Berry 
Date: February 2nd, 2021


usage: 
    python3 adc.read_leak()

Reference provided at: https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython

'''

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

def read_leak():

    #define i2c object
    i2c = busio.I2C(board.SCL, board.SDA)
    #create object
    ads = ADS.ADS1115(i2c)

    #single channel read
    chan = AnalogIn(ads,ADS.P0)
    print(chan.value, chan.voltage)
    return chan.voltage
