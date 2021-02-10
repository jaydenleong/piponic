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

import src.relay as relay
import src.adc as adc
import src.temp as temp
import src.pins as pins
import src.water_level as WL


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
        #sensors
        self.temperature = 0
        self.temp = temp
        self.pH = 7
        self.leak = 0
        self.adc_sensors = adc.adc_sensors()
        self.water_level_sensor = WL.water_level()
        self.water_level = 0
        
        
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
        self.water_solenoid.init(pins.RELAY3)


    def update_sensor_data(self):
        """Pretend to read the device's sensor data.
        If the fan is on, assume the temperature decreased one degree,
        otherwise assume that it increased one degree.
        """
        self.temperature = temp.read()
        try:
            self.pH = self.adc_sensors.read_pH()
            self.leak = self.adc_sensors.read_leak()
            self.water_level = self.water_level_sensor.read()
        except:
            print('Error ADC or I2C Error')

        print('All sensors successfully read!')   

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
        if data['peristaltic_pump_on'] != self.peristaltic_pump_on:
            # If changing the state of the fan, print a message and
            # update the internal state.
            self.peristaltic_pump_on = data['peristaltic_pump_on']
            if self.peristaltic_pump_on:
                print('peristaltic_pump turned on.')
                self.peristaltic_pump.on(pins.RELAY1)
            else:
                print('peristaltic_pump turned off.')
                self.peristaltic_pump.off(pins.RELAY1)



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

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # Update and publish temperature readings at a rate of one per second.
    for _ in range(args.num_messages):
        # In an actual device, this would read the device's sensors. Here,
        # you update the temperature based on whether the fan is on.
        device.update_sensor_data()
    
        # Report the device's temperature to the server by serializing it
        # as a JSON string.
        payload = json.dumps({'temperature': device.temperature,'pH': device.pH,'leak': device.leak,'water_level': device.water_level})
        print('Publishing payload', payload)
        client.publish(mqtt_telemetry_topic, payload, qos=1)
        # Send events every second.
        time.sleep(30)
     
    client.disconnect()
    client.loop_stop()
    print('Finished loop successfully. Goodbye!')


if __name__ == '__main__':
    main()
