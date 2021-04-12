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


from threading import Lock

import RPi.GPIO as GPIO
import src.pins as pins
import src.relay as relay


class water_level(object):
    """Class that reads data from the water level

       Implemented using a Thread-safe Singleton"""

    class __water_level:
        def __init__(self):
            self.level = 0
            self.setup()
            self.read() # update level 

        def setup(self):
            try:
                GPIO.setmode(GPIO.BCM) #read GPIO labels not pin numbers 
                GPIO.setwarnings(False)
                #Enable input, pull-down resistor so GPIO pin is normally GND
                GPIO.setup(pins.WATER_LEVEL,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            except:
                print('GPIO setup issue')
                
        def read(self):
            try:
                self.level = GPIO.input(pins.WATER_LEVEL)
                return self.level
            except:
                GPIO.cleanup()        
                return -1

    # The current singleton instance of __water_level
    instance = None

    # To ensure there is only one instance created across multiple threads
    instance_lock = Lock()

    def __init__(self):
        """
        Creates single instance of the __water_level class.
        This ensures that there is only one object interfacing
        the adc in the application
        """
        water_level.instance_lock.acquire()

        if not water_level.instance:
            water_level.instance = water_level.__water_level()

        water_level.instance_lock.release()

    def __getattr__(self, name):
        """
        Refers all parameters to be called on the instance
        Helps implement the Singleton design pattern
        """
        return getattr(self.instance, name)
