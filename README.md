# Automatic Boiler
## Introduction
This project is created to turn on/off devices remotely. There are some systems that do not have OS, and they have to be turned on/off by hardware. This turn on/off system is MQTT distribuited. Although server and UI is running in the same hardware, the system is flexible enough to run everything in different hardwares. These are the system roles:
- MQTT server where the entire MQTT protocol runs
- MQTT main client where timing is controlled and options are saved to be sent when needed
- MQTT hardware clients: Clients that set power on/off of some device
- Web server where the UI is developed, with a MQTT client to send/receive values

And this is the real hardware devices of the system
- **Raspberry Pi** where MQTT server, main client and web server runs
- **ESP8266** connected to a relay that turn on/off hardware devices, where an MQTT client is running

## Supported devices
- Relay with Esp8266
 
## Dependencies
- Python 3
- Mosquitto
- Red Hat server
- Arduino ESP8266 libraries

## Instalation for developers
- Clone this repository
- Html folder: web page, javascript functions and CSS file
- Src folder:
	- esp_*device* where the source code of the esp of each device is
	- rpi where the raspberry pi main client python code is
- Everytime you change html you must copy this folder into the server home: */var/www/html*
- When main client start a new log file is created like this: *logs/log_YYYYMMDD_hhmmss.log*

## How to create this project from scratch
### MQTT server and RPi client
To run this project Mosquitto broker is used. To download it type:
```
sudo apt-get -y install mosquitto mosquitto-clients
```
Enable Mosquitto service in your system control:
```
sudo systemctl enable mosquitto.service
```
The broker is a service (also known as daemon for linux users). As a daemon, Mosquitto will start everytime system is turned on. For the first test, you have to enable to start working:
```
mosquitto -d
```
You need to know the IP address of the server to connect clients.

**Test your broker:**
- Subscribe to a topic: `mosquitto_sub -d -t testTopic`
- Open another console terminal.
- Publish a message of that topic: `mosquitto_pub -d -t testTopic -m "Hello world!"`
- You should see the published message in the terminal that subscribe to the topic.

**Install paho**
In order to get the Paho library of python: `pip3 install paho-mqtt`

### Web server
In order to have a web page as a UI available, an Apache server is needed:
```
sudo apt install apache2 -y
```
Try to connect to http://localhost/ from the RPi or http://xxx.xxx.x.xxx/ whatever the ip of the raspbery is. The webpage of apache server is in `/var/www/html/`. Everytime you need to apply changes in your server you must cp the `html` folder from the git repository to there:
```
cd automatic_boiler
cp -r html /var/www/
```

### Install ESP8266 in Arduino IDE
go to Preferences->URL manager
Fill the field with `http://arduino.esp8266.com/stable/package_esp8266com_index.json`
Install the library in the manager and choose "Generic ESP8266 module"
go to the library manager and install PubSubClient library
Install de driver of the programmer (with the programmer already connected): http://sparks.gogo.co.nz/assets/_site_/downloads/CH340_WINDOWS.zip

### MQTT hardware clients
```
crontab -e
@reboot sleep 30; cd /path_to_code/automatic_boiler/src/rpi; /usr/bin/python3 boiler.py

```
### MQTT javascript client
```
cd /etc/mosquitto/conf.d
sudo nano local.conf
listener 1883
protocol mqtt
listener 8080
protocol websockets
```

