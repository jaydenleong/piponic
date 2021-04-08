#!/usr/bin/env python
# Copyright 2017 Google Inc. All rights reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# File: device.py
# 
# Modified: Jayden Leong <jdleong58@gmail.com>
# 
# Date: February 7, 2021
#
# Purpose: Defines state class for the entire RPi device. 
#          Gives other modules the ability to access the device's
#          sensor readings, and configuration.
#         
#          Importantly, this class also has callbacks to handle 
#          events between Google Cloud IoT and the RPi over MQTT
#
#          Finally, this class is implemented as Singleton.
#          This allows global access to a single Device object

import paho.mqtt.client as mqtt
import argparse
import datetime
import json
import os
import ssl
import time

from gpiozero import LED
from threading import Lock
import RPi.GPIO as GPIO
import src.relay as relay
import src.adc as adc
import src.temp as temp
import src.pins as pins
import src.water_level as WL
import src.control as control

def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))

class Device(object):
    class __Device:
        """Represents the state of a single device. Including the variables in the system."""
        def __init__(self):
            # Initialise sensor readings
            self.temperature = 0
            self.temp = temp
            self.pH = 7
            self.leak = 0
            self.adc_sensors = adc.adc_sensors()
            self.water_level_sensor = WL.water_level()
            self.water_level = 0
            self.battery_voltage = 0
            self.internal_leak = 0
            
            # Since the configuration is updated from multiple threads
            # create a mutex to handle synchronisation
            self.config_lock = Lock() 

            # Initialise device configuration to default
            DEFAULT_DEVICE_CONFIG = {
              'max_ph': 10,
              'min_ph': 5,
              'max_temperature': 25,
              'min_temperature': 15,
              'target_ph': 7,
              'update_interval_minutes': 30,
              'low_battery_volts' : 1,
              'leak_threshold_volts' : 0.25,
            };        
            self.update_config(DEFAULT_DEVICE_CONFIG)
            
            # Is device connected
            self.connected = False
            
        def update_sensor_data(self):
            """Read Sensor Data
            """
            self.temperature = temp.read()
            try:
                self.pH =               self.adc_sensors.read_pH()
                self.leak =             self.adc_sensors.read_leak()
                self.battery_voltage =  self.adc_sensors.read_battery()
                self.internal_leak =    self.adc_sensors.read_internal_leak()

            except:
                print('Error ADC or I2C Error')
                self.exit()

            try:
                self.water_level =      self.water_level_sensor.read()
            except:
                print('Water Level not read correctly')
                self.exit()

            print('All sensors successfully read!')   

        def error_detected(self): 
            """Check if there are any errors with any of the sensor readings
            
            Returns:
                (bool) : whether the device has an error or not
            """
            # By default there are no errors detected
            error_detected = False

            # Get configuration for thresholds
            config = self.get_config()
            
            # Check leak sensors 
            if (self.leak > config['leak_threshold_volts'] or self.internal_leak > config['leak_threshold_volts']):
                print("[WARN] Leak detected")
                error_detected = True

            # Check pH value
            if (self.pH < config['min_ph'] or self.pH > config['max_ph']):
                print("[WARN] pH outside of healthy range")
                error_detected = True

            # Check temperature
            if (self.temperature < config['min_temperature'] or self.temperature > config['max_temperature'] ):
                print("[WARN] Temperature outside of healthy range") 
                error_detected = True
            
            # Check battery level
            if(self.battery_voltage < config['low_battery_volts'] ):
                print("[WARN] Low battery voltage detected")
                error_detected = True

            return error_detected

        def get_sensor_data(self):
            """Gets sensor data, formatted as JSON"""
            return json.dumps({'temperature': self.temperature,
                                'pH': self.pH,
                                'leak': self.leak,
                                'water_level': self.water_level, 
                                'battery_voltage': self.battery_voltage,
                                'internal_leak': self.internal_leak})

        def update_config(self, config):
            """Updates the device configuration in a Thread-safe manner

            Args:
                config (dictionary): the new configuration
            """
            self.config_lock.acquire()
            self.config = config
            print("Configuration updated to: ", self.config)
            self.config_lock.release()

        def get_config(self):
            """Gets device configuration in a Thread-safe manner"""
            self.config_lock.acquire()
            config = self.config
            self.config_lock.release()
            return config

        def exit(self): 
            GPIO.cleanup()

        def wait_for_connection(self, timeout):
            """Wait for the device to become connected."""
            total_time = 0
            while not self.connected and total_time < timeout:
                time.sleep(1)
                total_time += 1

            if not self.connected:
                raise RuntimeError('Could not connect to MQTT bridge.')

        def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
            """Callback for when a device connects."""
            print('Connection Result:', error_str(rc))
            self.connected = True

        def on_disconnect(self, unused_client, unused_userdata, rc):
            """Callback for when a device disconnects."""
            print('Disconnected:', error_str(rc))
            self.connected = False

        def on_publish(self, unused_client, unused_userdata, unused_mid):
            """Callback when the device receives a PUBACK from the MQTT bridge."""
            print('Published message acked.')

        def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                         granted_qos):
            """Callback when the device receives a SUBACK from the MQTT bridge."""
            print('Subscribed: ', granted_qos)
            if granted_qos[0] == 128:
                print('Subscription failed.')

        def on_message(self, unused_client, unused_userdata, message):
            """Callback when the device receives a message on a subscription."""
            payload = message.payload.decode('utf-8')

            # Print what message we recieved for debugging purposes
            print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
                payload, message.topic, str(message.qos)))

            # The device will receive its latest config when it subscribes to the
            # config topic. If there is no configuration for the device, the device
            # will receive a config with an empty payload.
            if not payload:
                return

            # The config is passed in the payload of the message. In this example,
            # the server sends a serialized JSON string.
            data = json.loads(payload)

            # Configuration message recieved
            if "config" in message.topic:
                new_config = self.get_config()

                # Update configuration settings
                for setting in data:
                    if setting in self.config: 
                        new_config[setting] = data[setting]

                # Save the updated device configuration
                self.update_config(new_config)
            # Command receieved
            elif "command" in message.topic:      
                # pH calibration command
                if( 'calibration_num' in data and 'ph' in data ):
                    if (data['calibration_num'] == 1):
                        self.adc_sensors.calibrate_ph_1(data['ph'])
                    elif (data['calibration_num'] == 2):
                        self.adc_sensors.calibrate_ph_2(data['ph'])
                    else:
                        print("[ERROR]: Invalid pH calibration number")
            else:
                print('Unrecognized message recieved')

    # The current singleton instance of __device
    instance = None

    # To ensure there is only one instance created across multiple threads
    instance_lock = Lock()

    def __init__(self):
        """
        Creates single instance of the __adc_sensors class.
        This ensures that there is only one object interfacing
        the adc in the application
        """
        Device.instance_lock.acquire()

        if Device.instance == None:
            Device.instance = Device.__Device()

        Device.instance_lock.release()

    def __getattr__(self, name):
        """
        Refers all parameters to be called on the instance
        Helps implement the Singleton design pattern
        """
        return getattr(self.instance, name)
