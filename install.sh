#!/bin/bash
# File: install.bash
#
# Author: Jayden Leong <jdleong58@gmail.com>
#
# Date: January 31, 2021
#
# Purpose: install piponic project on Raspberry Pi Zero W V1.1

SHOW_HELP() {
  echo
  "Usage:
    sudo ./setup.sh <DEVICE-ID> <REGISTRY-ID> <PROJECT-ID>

  Example:
    sudo ./setup.sh JaydenPi RaspberryPis piponics
    
  Arguments:
    <DEVICE-ID> : Google Cloud Device ID of this Raspberry Pi
    <REGISTRY-ID> : Google Cloud Registry this device is part of
    <PROJECT-ID> : Google Cloud Project name
   
    Please consult the Google Cloud Console -> IoT Core to create
    a new device before running this script."
}

# Ensure correct arguments
if [ "$#" -ne 3 ]; then
    echo "Incorrect number of parameters"
    SHOW_HELP
    exit 1
fi

# Parse arguments
DEVICE_ID=$1
REGISTRY_ID=$2
PROJECT_ID=$3

# Get directory this script is in
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo ""
echo "----- INSTALLING APT PACKAGES -----"
echo ""

apt-get update
apt-get install -yy vim git python3 python3-pip python3-rpi.gpio

echo ""
echo "----- INSTALLING PYTHON DEPENDENCIES FROM REQUIREMENTS.TXT -----"
echo ""
pip3 install -r requirements.txt

if [ ! -f ${SCRIPT_DIR}/rsa_private.pem ]; then
    echo ""
    echo "----- GENERATING RSA KEYS FOR GOOGLE CLOUD COMMUNICATION -----"
    echo ""
    openssl genpkey -algorithm RSA -out rsa_private.pem -pkeyopt rsa_keygen_bits:2048
    openssl rsa -in rsa_private.pem -pubout -out rsa_public.pem
    chmod +r rsa_private.pem rsa_public.pem
fi 

# Download google root CA
# See here for details https://cloud.google.com/iot/docs/how-tos/mqtt-bridge
if [ ! -f ${SCRIPT_DIR}/roots.pem ]; then
    echo ""
    echo "----- DOWNLOADING GOOGLE ROOT RA -----"
    echo ""
    curl https://pki.goog/roots.pem --output roots.pem
fi

if ! command -v gcloud &> /dev/null
then 
    echo ""
    echo "----- INSTALLING GOOGLE CLOUD SDK -----"
    echo ""
    
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
    apt-get install -yy apt-transport-https ca-certificates gnupg
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
    apt-get install -yy google-cloud-sdk

    echo ""
    echo "----- PLEASE LOGIN TO THE GOOGLE CLOUD SDK -----"
    echo ""
    gcloud init --console-only
else 
    echo ""
    echo "----- PLEASE LOGIN TO THE GOOGLE CLOUD SDK -----"
    echo ""

    gcloud auth login
fi 

if ! gcloud projects list | grep -q ${PROJECT_ID} ; then
    echo ""
    echo "----- ERROR: Google Cloud project ${PROJECT_ID} not found... -----"
    echo "Please run this script again and enter a valid project name" 
    echo ""

    # Logout of gcloud for security purposes
    echo ""
    echo "----- LOGGING OUT OF GOOGLE CLOUD -----"
    echo ""
    gcloud auth revoke --all
    exit 1
fi
gcloud config set project ${PROJECT_ID}

# Create IoT Device registry if not exists
if gcloud iot registries list --project ${PROJECT_ID} --region us-central1 | grep -q $REGISTRY_ID
then
    echo ""
    echo "----- EXISTING GCLOUD REGISTRY ${REGISTRY_ID} FOUND, USING IT-----"
    echo ""
else
    echo ""
    echo "----- EXISTING GCLOUD IOT REGISTRY NOT FOUND, CREATING NEW CALLED ${REGISTRY_ID}-----"
    echo ""
    gcloud iot registries create ${REGISTRY_ID}\
    --project=${PROJECT_ID} \
    --region=us-central1 \
    --event-notification-config=topic=device-events
fi 

# Create Google Cloud Device if not exists
if gcloud iot devices list --project ${PROJECT_ID} --registry ${REGISTRY_ID} --region us-central1 | grep -q $DEVICE_ID
then
    echo ""
    echo "----- EXISTING GCLOUD IOT DEVICE ${DEVICE_ID} FOUND, USING IT-----"
    echo ""
else 
    echo ""
    echo "----- CREATING NEW GCLOUD IOT DEVICE ${DEVICE_ID} -----"
    echo ""
    gcloud iot devices create ${DEVICE_ID} \
        --project=${PROJECT_ID} \
        --region=us-central1 \
        --registry=${REGISTRY_ID} \
        --public-key path=rsa_public.pem,type=rsa-pem
fi

# Logout of gcloud for security purposes
echo ""
echo "----- LOGGING OUT OF GOOGLE CLOUD -----"
echo ""
gcloud auth revoke --all

# Create systemd service to execute our scripts on boot
echo ""
echo "----- INSTALLING PIPONIC SERVICE -----"
echo ""
echo "
[Unit]
Description=Runs Piponic Monitoring System
After=network.target

[Service]
ExecStart=/usr/bin/python3 piponic.py \
    --project_id=${PROJECT_ID} \
    --registry_id=${REGISTRY_ID} \
    --device_id=${DEVICE_ID} \
    --private_key_file=/home/pi/piponic/rsa_private.pem \
    --algorithm=RS256
WorkingDirectory=${SCRIPT_DIR}
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
" > piponic.service

# Install, start, and enable systemd service
mv piponic.service /etc/systemd/system/piponic.service
systemctl start piponic.service
systemctl enable piponic.service
systemctl daemon-reload

echo ""
echo "Installation complete. Piponic should now be running."
