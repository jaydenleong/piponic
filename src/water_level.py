'''
water_level.py 

Author: Carson Berry
Date: February 9th, 2021

A function that reads from the SEN0204 non-contact liquid level sensor. Available from https://www.dfrobot.com/product-1493.html. 


Output:
    water_level object (0 is no water, 1 is water)

Usage: 
    import src.water_level as WL
    WL_sensor = WL.water_level()
    print(WL_sensor.read())

'''


import RPi.GPIO as GPIO
import src.pins as pins


class water_level(object):
    def __init__(self):
        self.level = 0
        self.setup()
        self.read() # update level 

    def setup(self):
        GPIO.setmode(GPIO.BCM) #read GPIO labels not pin numbers 

        #Enable input, pull-down resistor so GPIO pin is normally GND
        GPIO.setup(pins.WATER_LEVEL,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def read(self):
        try:
            self.level = GPIO.input(pins.WATER_LEVEL)
            return self.level
        except:
            GPIO.cleanup()        
            return -1

