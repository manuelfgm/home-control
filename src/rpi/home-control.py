# Imports
import logging
from boiler import *
import Adafruit_DHT
from datetime import datetime
import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json

BOILER_MSG = 'home/boiler/'
PARAMS_MSG = 'home/params/'

with open('conf.json') as f:
    dic = json.load(f)

boiler = Boiler.fromdict(dic["boiler"])

def on_message(client, userdata, message):
    global set_flag
    if message.topic == BOILER_MSG + "set/start_time":
        param = str(message.payload.decode("utf-8"))
        client.publish(BOILER_MSG + "status/start_time", param)
        start = datetime.strptime(param, "%H:%M")
        boiler.set_time_start(start.time())
        logging.info("Set Param Time Start: " + param + "h")
        set_flag = True
    elif message.topic == BOILER_MSG + "set/stop_time":
        param = str(message.payload.decode("utf-8"))
        client.publish(BOILER_MSG + "status/stop_time", param)
        stop = datetime.strptime(param, "%H:%M")
        boiler.set_time_stop(stop.time())
        logging.info("Set Param Time Stop: " + param + "h")
        set_flag = True
    elif message.topic == BOILER_MSG + "set/user_temp":
        param = float(message.payload.decode("utf-8"))
        client.publish(BOILER_MSG + "status/user_temp", param)
        boiler.set_user_temp(param)
        logging.info("Set Param User Temp: " + str(param) + "ºC")
        set_flag = True
    elif message.topic == BOILER_MSG + "set/back_temp":
        param = float(message.payload.decode("utf-8"))
        client.publish(BOILER_MSG + "status/back_temp", param)
        boiler.set_back_temp(param)
        logging.info("Set Param Back Temp: " + str(param) + "ºC")
        set_flag = True
    elif message.topic == PARAMS_MSG + "get":
        client.publish(PARAMS_MSG + "status/curr_temp", "{0:0.1f}".format(temperature))
        client.publish(BOILER_MSG + "status/start_time", boiler.get_time_start().strftime("%H:%M"))
        client.publish(BOILER_MSG + "status/stop_time", boiler.get_time_stop().strftime("%H:%M"))
        client.publish(BOILER_MSG + "status/user_temp", boiler.get_user_temp())
        client.publish(BOILER_MSG + "status/back_temp", boiler.get_back_temp())
    elif message.topic == "home/relay/status":
        logging.info("Boiler Feedback: " + str(message.payload.decode("utf-8")))


print("**************** Home Control ***************")

# Configuration
INTERVAL_SECS = 595

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN_DATA = 4
DHT_PIN_POWER = 27

client = mqtt.Client("RPi")
client.connect("localhost")
client.subscribe(BOILER_MSG + "status")
client.subscribe(BOILER_MSG + "set/#")
client.subscribe(PARAMS_MSG + "get")
client.on_message = on_message
client.loop_start()

global set_flag
set_flag = False

# Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setup(DHT_PIN_POWER, GPIO.OUT)
GPIO.output(DHT_PIN_POWER, GPIO.HIGH)

# Log file
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
now = datetime.now()
now_str = now.strftime("%Y%m%d_%H%M%S")
log_file = "../../logs/log_" + now_str + ".log"
logging.basicConfig(filename = log_file, level = logging.INFO)
print("- File " + log_file + " created")

# Main loop
while True:
    GPIO.output(DHT_PIN_POWER, GPIO.HIGH)

    # First read is deprecated
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN_DATA)

    # Read sensor and time
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN_DATA)
    now = datetime.now()
    log_str = now.strftime("%Y/%m/%d_%H:%M:%S")

    # Control
    if humidity is not None and temperature is not None:
        log_str += " Temp={0:0.1f}ºC Hum={1:0.1f}%".format(temperature, humidity)
        log_str += " Target={0:0.1f}ºC".format(boiler.get_target_temp())
        signal = boiler.control(temperature, now.time())
        client.publish(PARAMS_MSG + "status/curr_temp", "{0:0.1f}".format(temperature))
        if signal == ControlResult.TURN_ON:
            client.publish("home/relay/set", 1)
            log_str += " ON"
        elif signal == ControlResult.TURN_OFF:
            client.publish("home/relay/set", 0)
            log_str += " OFF"
    else:
        log_str += " Failed to retrieve data from sensor"

    # Print
    logging.info(log_str)

    # Wait
    i = 0
    GPIO.output(DHT_PIN_POWER, GPIO.LOW)

    while True:
        time.sleep(1)
        i += 1
        if i >= INTERVAL_SECS or set_flag:
            set_flag = 0
            break

