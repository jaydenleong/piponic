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
# File: piponic.py
# 
# Modified: Jayden Leong <jdleong58@gmail.com>
# 
# Date: February 7, 2021
#
# Purpose: Entry point to the piponic program. This program gathers
#          data from attached aquaponic/hydroponic sensors. It also
#          controls output devices attached to the Raspberry Pi.
#          It uses Google Cloud IoT in order to send sensor updates
#          and recieve commands from a mobile application.
#
#          This script was modified from an example given here:
#          https://github.com/GoogleCloudPlatform/python-docs-samples/
#
# Usage:
#          $ python3 piponic.py \
#               --project_id=my-project-id \
#               --registry_id=example-my-registry-id \
#               --device_id=my-device-id \
#               --private_key_file=rsa_private.pem \
#               --algorithm=RS256
#          
#          Only use this command if running manually. The install.sh
#          script installs this to run automatically when the Raspberry Pi boots.
#          Please see install.sh for more details.

import argparse
import datetime
import json
import os
import ssl
import time


import jwt
import paho.mqtt.client as mqtt

from gpiozero import LED
from threading import Lock

import src.relay as relay
import src.adc as adc
import src.temp as temp
import src.pins as pins
import src.water_level as WL
import src.control as control


def create_jwt(project_id, private_key_file, algorithm):
    """Create a JWT (https://jwt.io) to establish an MQTT connection."""
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'aud': project_id
    }
    with open(private_key_file, 'r') as f:
        private_key = f.read()
    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))
    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


class Device(object):
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
          'peristaltic_pump_on': False,
          'target_ph': 7,
          'update_interval_minutes': 30,
          'low_battery_volts' : 1,
          'leak_threshold_volts' : 0.25,
        };        
        self.update_config(DEFAULT_DEVICE_CONFIG)

        
        self.connected = False
        
        #test classes
        self.fan_on = False
        self.led = LED(17)
        self.led.off()
        
        #Control Devices
        self.relay=relay
        self.peristaltic_pump_on = False
        self.peristaltic_pump = self.relay
        self.peristaltic_pump.init(pins.RELAY1)


        self.water_solenoid_on = False
        self.water_solenoid = self.relay
        self.water_solenoid.init(pins.RELAY3) #TODO: change this to pins.RELAY2 for the model at Benny's 


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
            print('Config message recieved from Google Cloud IoT')
            
            # Respond to each configuration setting
            new_config = self.get_config()
            for setting in data:
                # Save configuration setting
                if setting in self.config: 
                    new_config[setting] = data[setting]

                # Respond to certain configuration updates, like turning
                # the pump on.
                if setting == 'peristaltic_pump_on': 
                    if data['peristaltic_pump_on'] != self.peristaltic_pump_on:
                        self.peristaltic_pump_on = data['peristaltic_pump_on']
                        if self.peristaltic_pump_on:
                            print('peristaltic_pump turned on.')
                            self.peristaltic_pump.on(pins.RELAY1)
                        else:
                            print('peristaltic_pump turned off.')
                            self.peristaltic_pump.off(pins.RELAY1)

            # Save the updated device configuration
            self.update_config(new_config)
        elif "command" in message.topic:      # Command receieved
            print('Command message recieved from Google Cloud IoT')

            # pH calibration command
            if( 'calibration_num' in data and 'ph' in data ):
                print("pH calibration recieved")
                print(data)
        else:
            print('Unrecognized message recieved')


def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Example Google Cloud IoT MQTT device connection code.')
    parser.add_argument(
        '--project_id',
        default=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        required=True,
        help='GCP cloud project name.')
    parser.add_argument(
        '--registry_id', required=True, help='Cloud IoT registry id')
    parser.add_argument(
        '--device_id',
        required=True,
        help='Cloud IoT device id')
    parser.add_argument(
        '--private_key_file', required=True, help='Path to private key file.')
    parser.add_argument(
        '--algorithm',
        choices=('RS256', 'ES256'),
        required=True,
        help='Which encryption algorithm to use to generate the JWT.')
    parser.add_argument(
        '--cloud_region', default='us-central1', help='GCP cloud region')
    parser.add_argument(
        '--ca_certs',
        default='roots.pem',
        help='CA root certificate. Get from https://pki.google.com/roots.pem')
    parser.add_argument(
        '--num_messages',
        type=int,
        default=100,
        help='Number of messages to publish.')
    parser.add_argument(
        '--mqtt_bridge_hostname',
        default='mqtt.googleapis.com',
        help='MQTT bridge hostname.')
    parser.add_argument(
        '--mqtt_bridge_port', type=int, default=8883, help='MQTT bridge port.')
    parser.add_argument(
        '--message_type', choices=('event', 'state'),
        default='event',
        help=('Indicates whether the message to be published is a '
              'telemetry event or a device state message.'))

    return parser.parse_args()


def main():
    args = parse_command_line_args()

    # Create the MQTT client and connect to Cloud IoT.
    client = mqtt.Client(
        client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(
            args.project_id,
            args.cloud_region,
            args.registry_id,
            args.device_id))
    client.username_pw_set(
        username='unused',
        password=create_jwt(
            args.project_id,
            args.private_key_file,
            args.algorithm))
    client.tls_set(ca_certs=args.ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    device = Device()

    client.on_connect = device.on_connect
    client.on_publish = device.on_publish
    client.on_disconnect = device.on_disconnect
    client.on_subscribe = device.on_subscribe
    client.on_message = device.on_message

    client.connect(args.mqtt_bridge_hostname, args.mqtt_bridge_port)

    client.loop_start()

    # This is the topic that the device will publish telemetry events
    # (temperature data) to.
    mqtt_telemetry_topic = '/devices/{}/events'.format(args.device_id)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(args.device_id)

    # This is the topic that the device will recieve commands from
    mqtt_command_topic = '/devices/{}/commands/#'.format(args.device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # Subscribe to the commands topic
    client.subscribe(mqtt_command_topic, qos=1)


    # Start controller to maintain pH in a healthy range
    pH_control_thread = control.pHController()
    pH_control_thread.start()

    # Start controller to maintain water level
    wl_control_thread = control.waterLevelController()
    wl_control_thread.start()

    # Start main application loop
    while True:
        # Get most recent device configuration
        device_config = device.get_config()

        # Update sensor measurements 
        device.update_sensor_data()

        # Fetch sensor data
        sensor_data = device.get_sensor_data()

        # Publish sensor readings
        print('Publishing sensor data: ', sensor_data)
        client.publish(mqtt_telemetry_topic, sensor_data, qos=1)

        # Loop that checks sensor readings every minute
        # If there are errors detected, we post an update
        # Otherwise, we just post updates at 'update_interval_minutes'
        for i in range(device_config['update_interval_minutes']):
            device.update_sensor_data()

            if device.error_detected():             
                print('[WARN] Unhealthy sensor readings detected. Publishing update early.')

                # Publish sensor readings
                sensor_data = device.get_sensor_data()
                print('Publishing sensor data: ', sensor_data)
                client.publish(mqtt_telemetry_topic, sensor_data, qos=1)

            time.sleep(60) # Sleep for a minute
    
    # End thread execution
    ph_control_thread.join()
    wl_control_thread.join()

    # Disconnect and clean up MQTT client
    client.disconnect()
    client.loop_stop()
    print("PiPonic application exited");

if __name__ == '__main__':
    main()
