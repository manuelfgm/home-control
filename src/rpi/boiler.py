# Imports
import logging
from controller import *
import Adafruit_DHT
from datetime import datetime
import time
import sys
import paho.mqtt.client as mqtt


controller = Controller()

def on_message(client, userdata, message):
    if message.topic == "home/params/set/time_start":
        param = str(message.payload.decode("utf-8"))
        client.publish("home/params/status/time_start", param)
        start = datetime.strptime(param, "%H:%M")
        controller.set_time_start(start.time())
        logging.info("Set Param Time Start: " + param + "h")
    elif message.topic == "home/params/set/time_stop":
        param = str(message.payload.decode("utf-8"))
        client.publish("home/params/status/time_stop", param)
        stop = datetime.strptime(param, "%H:%M")
        controller.set_time_stop(stop.time())
        logging.info("Set Param Time Stop: " + param + "h")
    elif message.topic == "home/params/set/user_temp":
        param = float(message.payload.decode("utf-8"))
        client.publish("home/params/status/user_temp", param)
        controller.set_user_temp(param)
        logging.info("Set Param User Temp: " + str(param) + "ºC")
    elif message.topic == "home/params/set/back_temp":
        param = float(message.payload.decode("utf-8"))
        client.publish("home/params/status/back_temp", param)
        controller.set_back_temp(param)
        logging.info("Set Param Back Temp: " + str(param) + "ºC")
    elif message.topic == "home/params/get":
        client.publish("home/params/status/time_start", controller.get_time_start().strftime("%H:%M"))
        client.publish("home/params/status/time_stop", controller.get_time_stop().strftime("%H:%M"))
        client.publish("home/params/status/user_temp", controller.get_user_temp())
        client.publish("home/params/status/back_temp", controller.get_back_temp())
    elif message.topic == "home/boiler/status":
        logging.info("Boiler Feedback: " + str(message.payload.decode("utf-8")))


print("**************** Automatic Boiler program ***************")

# Configuration
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
client = mqtt.Client("RPi")
client.connect("localhost")
client.subscribe("home/boiler/status")
client.subscribe("home/params/set/#")
client.subscribe("home/params/get")
client.on_message = on_message
client.loop_start()

# Log file
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
now = datetime.now()
now_str = now.strftime("%Y%m%d_%H%M%S")
log_file = "../../logs/boiler_" + now_str + ".log"
logging.basicConfig(filename = log_file, level = logging.INFO)
print("- File " + log_file + " created")

# First read is deprecated
humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

# Main loop
while True:

    # Read sensor and time
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    now = datetime.now()
    log_str = now.strftime("%Y/%m/%d_%H:%M:%S")

    # Control
    if humidity is not None and temperature is not None:
        log_str += " Temp={0:0.1f}ºC Hum={1:0.1f}%".format(temperature, humidity)
        signal = controller.control(temperature, now.time())
        log_str += " Target={0:0.1f}ºC".format(controller.get_target_temp())
        if signal == ControlResult.TURN_ON:
            client.publish("home/boiler/relay", 1)
            log_str += " ON"
        elif signal == ControlResult.TURN_OFF:
            client.publish("home/boiler/relay", 0)
            log_str += " OFF"
    else:
        log_str += " Failed to retrieve data from sensor"

    # Print
    logging.info(log_str)

    # Wait
    time.sleep(600)

