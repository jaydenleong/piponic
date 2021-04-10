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

import src.device as dev 
import src.relay as relay
import src.adc as adc
import src.temp as temp
import src.pins as pins
import src.water_level as WL
import src.control as control

CONTROL_LOOPS_ENABLED=False #disable multithreaded control loops 

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

    device = dev.Device()
       
    # Callbacks for when MQTT events occur
    client.on_connect = device.on_connect
    client.on_publish = device.on_publish
    client.on_disconnect = device.on_disconnect
    client.on_subscribe = device.on_subscribe
    client.on_message = device.on_message

    # Connect and start the MQTT client
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

    if CONTROL_LOOPS_ENABLED:
        # Start controller to maintain pH in a healthy range
        pH_control_thread = control.pHController()
        pH_control_thread.start()

        # Start controller to maintain water level
        wl_control_thread = control.waterLevelController()
        wl_control_thread.start()

    #temporary control fix - initialize the peristaltic pump here
    relay.init_pullup(pins.peristaltic_pump)
    relay.init_pullup(pins.Water_level_solenoid)
    min_pH_accuracy = 0.5

    # Start main application loop
    while True:
        try:
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
                
                #pH control moved to here because multi-threading with control throws tricky error
                if(abs(device.pH-float(device_config['target_ph']))>min_pH_accuracy):
                        #turn on peristaltic pump
                        relay.on_pu(pins.peristaltic_pump)
                        time.sleep(1)
                        relay.off_pu(pins.peristaltic_pump)

                if(device.water_level == 0): #if water level is low
                        #relay.on_pu(pins.Water_level_solenoid)
                        #time.sleep(1)
                        #relay.off_pu(pins.Water_level_solenoid)


                time.sleep(60) # Sleep for a minute
        except:
            break # Exit main loop if there is an error so we can clean up

    print("Killed main sensor loop")
    
    # Kill control threads if main loop exits    
    print("Killing control loops... May take up to 30 seconds...") 
    if CONTROL_LOOPS_ENABLED:
        pH_control_thread.kill()
        wl_control_thread.kill()
        pH_control_thread.join()
        wl_control_thread.join()

    # Disconnect and clean up MQTT client
    client.disconnect()
    client.loop_stop()
    print("PiPonic application exited");

if __name__ == '__main__':
    main()
