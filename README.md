# piponic
IoT Monitoring and Control for Aquaponic and Hydroponic Systems Using Raspberry Pi Zero W 

## Install

```
sudo ./setup.sh
```

Please contact Jayden for questions about connecting to Google Cloud IoT.

## Run

```
python3 cloudiot_pubsub_example_mqtt_device.py \               
    --project_id=piponics \
    --registry_id=RaspberryPis \
    --device_id=<DEVICE-ID> \
    --private_key_file=/home/pi/piponic/rsa_private.pem \
    --algorithm=RS256
```

Please contact Jayden for questions about device ID.
