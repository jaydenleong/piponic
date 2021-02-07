# piponic
IoT Monitoring and Control for Aquaponic and Hydroponic Systems Using Raspberry Pi.

## Install

To install this project on the Raspberry Pi and have it run on boot,
please run the following:

```
sudo ./install.sh <DEVICE-ID> <REGISTRY-ID> <PROJECT-ID>
```

Note that the parameters are as follows:

- `<DEVICE-ID>` string name to call the device (you choose)
- `<REGISTRY-ID>` string name of the Google IoT Registry (can be new or pre-existing)
- `<PROJECT-ID>` string name of the Google Cloud Project

Example:

```
sudo ./install.sh JaydenPi RaspberryPis piponics 
```

**Important Notes:**

- Please create a Google Cloud Project before running this script and enable the
  Google Cloud IoT Core API.
- The install will prompt you to login into your Google Account associated 
  with your Google Cloud Project halfway through the process. Please follow the 
  link and sign in
- The install process may take around 20 minutes  

## Checking Installed Software Status 

The install script causes the `piponic.py` script to run when the raspberry pi
boots. To do this, it uses a [systemd service](https://www.raspberrypi.org/documentation/linux/usage/systemd.md). In order to check on the status of the software (running or not, etc), run
this command: 

```
sudo systemctl status piponic.service
```

Note that the `systemctl` program manages systemd services like our `piponic.service`.
So, to stop, start and restart our code from running, try the following commands:

```
sudo systemctl stop piponic.service
sudo systemctl start piponic.service
sudo systemctl restart piponic.service
```

Additionally, when testing, view logs using `journalctl`. Here is an example:

```
sudo journalctl -u piponic.service
```

## Code Documentation

For use of sensor and control modules, the use follows: 

```
import src.adc as adc
import src.temp as temp
import src.relay as relay

relay.init_one()
relay.on1()
relay.off1()

temp.read()

adc.read_pH()
adc.read_leak()
```
