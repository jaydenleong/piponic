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
from threading import Lock

class adc_sensors:
    """Class which interfaces with the sensors attached to the ADC. Includes: 

        - pH probe
        - leak sensors
        - battery level sensors
        
        This class is implemented using the Singleton Design pattern. This 
        allows global access to a single instance of this class. See here
        (https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html)
        for more details.
    """
    class __adc_sensors():
        def __init__(self):
            # Only allow one thread to access sensors at a time
            self.sensor_lock = Lock()

            # Init ADC communication via I2C
            self.ads=0
            self.init_i2c()
                        
            # Init battery sensor
            self.battery_sensor=0
            self.init_battery()

            # Init leak sensors
            self.internal_leak=0
            self.init_internal_leak()
            self.leak_sensor = 0
            self.init_leak()

            # Init pH
            self.pH_sensor = 0
            self.init_pH()

            # Default pH calibration values
            self.pH_intercept = 7
            self.pH_offset = 1.65
            self.pH_slope = -3.3 
            self.calibration_pH_1 = None
     
        def init_i2c(self):
            # Define i2c object
            i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(i2c) 
    
    ############# Initialize all the ADC pins ##################
    
        def init_leak(self):
            self.leak_sensor= AnalogIn(self.ads,ADS.P0)
             
        def init_pH(self):
            self.pH_sensor= AnalogIn(self.ads,ADS.P1)
            
        def init_battery(self):
            self.battery_sensor= AnalogIn(self.ads,ADS.P2)       
    
        def init_internal_leak(self):
            self.internal_leak= AnalogIn(self.ads,ADS.P3)     
    
    ############### READ functions ############################
        def read_leak(self):
            self.sensor_lock.acquire()
            leak = self.leak_sensor.voltage
            self.sensor_lock.release()
            return leak 

        def read_pH(self):
            self.sensor_lock.acquire()
            pH_voltage = self.pH_sensor.voltage
            pH = self.pH_intercept +(pH_voltage-self.pH_offset)*(self.pH_slope)
            self.sensor_lock.release()
            return pH

        def read_battery(self):
            self.sensor_lock.acquire()
            battery_voltage = self.battery_sensor.voltage
            self.sensor_lock.release()
            return battery_voltage
    
        def read_internal_leak(self):
            self.sensor_lock.acquire()
            internal_leak = self.internal_leak.voltage
            self.sensor_lock.release()
            return internal_leak

        def calibrate_ph_1(self, calibration_pH_1):
            
            # set the pH_offset to be the middle of the
            self.sensor_lock.acquire()
            self.pH_offset = self.pH_sensor.voltage # read the pH meter's voltage in the known solution 1
            self.calibration_pH_1 = calibration_pH_1
            self.sensor_lock.release()

        def calibrate_ph_2(self, calibration_pH_2):
            #this function constructs a linear function of the form:
            # y = m(x-offset)+b
            # or
            # pH = (slope)*(voltage-offset_voltage)+ pH_at_offset_voltage

            self.sensor_lock.acquire()

            v2 = self.pH_sensor.voltage # read the pH meter's voltage in the known solution 2

            #calculate slope of pH-voltage curve (should be negative)
            self.pH_slope = (self.calibration_pH_1-calibration_pH_2)/(self.pH_offset-v2)

            #pH curve 'intercept' anchored around first datapoint
            self.pH_intercept = self.calibration_pH_1

            self.sensor_lock.release()

    # The current singleton instance of __adc_sensors
    instance = None

    # To ensure there is only one instance created across multiple threads
    instance_lock = Lock()

    def __init__(self):
        """
        Creates single instance of the __adc_sensors class.
        This ensures that there is only one object interfacing
        the adc in the application
        """
        adc_sensors.instance_lock.acquire()
        if not adc_sensors.instance:
            adc_sensors.instance = adc_sensors.__adc_sensors()
        adc_sensors.instance_lock.release()

    def __getattr__(self, name):
        """
        Refers all parameters to be called on the instance
        Helps implement the Singleton design pattern
        """
        return getattr(self.instance, name)


