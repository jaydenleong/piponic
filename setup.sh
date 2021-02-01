#!/bin/bash
# File: setup.bash
#
# Author: Jayden Leong <jdleong58@gmail.com>
#
# Date: January 31, 2021
#
# Purpose: install dependencies for piponic project on Raspberry Pi Zero W V1.1
#
# Usage: sudo ./setup.bash

# Install OS dependencies
apt-get install -yy vim git python3 python3-pip

# Install python3 dependencies
pip3 install -r requirements.txt

# Create RSA keys for Google Cloud Communication
openssl genpkey -algorithm RSA -out rsa_private.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -in rsa_private.pem -pubout -out rsa_public.pem

# Download google root CA
# See here for details https://cloud.google.com/iot/docs/how-tos/mqtt-bridge
curl https://pki.goog/roots.pem --output roots.pem
