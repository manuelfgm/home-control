
# Imports
import logging
from controller import *
import Adafruit_DHT
from datetime import datetime
import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import os
import psycopg2
import pytz

POSTGRES_HOST=os.getenv('POSTGRES_HOST', default='localhost')
POSTGRES_PORT=os.getenv('POSTGRES_PORT', default=5432)
POSTGRES_DB  =os.getenv('POSTGRES_DB'  , default='home')
POSTGRES_USER=os.getenv('POSTGRES_USER', default='default_user')
POSTGRES_PSSW=os.getenv('POSTGRES_PSSW', default='default_pssw')
POSTGRES_TABL=os.getenv('POSTGRES_TABL', default='temperature')
POSTGRES_ROOM=os.getenv('POSTGRES_ROOM', default='bedroom')

with open('conf.json', 'r') as f:
    dic = json.load(f)
    f.close()

controller = Controller.fromdict(dic)

def on_message(client, userdata, message):
    set_flag = False
    if message.topic == "home/params/set/start_time":
        param = str(message.payload.decode("utf-8"))
        client.publish("home/params/status/start_time", param)
        start = datetime.strptime(param, "%H:%M")
        controller.set_time_start(start.time())
        logging.info("Set Param Time Start: " + param + "h")
        dic["time_start"] = param
        set_flag = True
    elif message.topic == "home/params/set/stop_time":
        param = str(message.payload.decode("utf-8"))
        client.publish("home/params/status/stop_time", param)
        stop = datetime.strptime(param, "%H:%M")
        controller.set_time_stop(stop.time())
        logging.info("Set Param Time Stop: " + param + "h")
        dic["time_stop"] = param
        set_flag = True
    elif message.topic == "home/params/set/user_temp":
        param = float(message.payload.decode("utf-8"))
        client.publish("home/params/status/user_temp", param)
        controller.set_user_temp(param)
        logging.info("Set Param User Temp: " + str(param) + "ºC")
        dic["user_temp"] = param
        set_flag = True
    elif message.topic == "home/params/set/back_temp":
        param = float(message.payload.decode("utf-8"))
        client.publish("home/params/status/back_temp", param)
        controller.set_back_temp(param)
        logging.info("Set Param Back Temp: " + str(param) + "ºC")
        dic["back_temp"] = param
        set_flag = True
    elif message.topic == "home/params/get":
        client.publish("home/params/status/curr_temp", "{0:0.1f}".format(temperature))
        client.publish("home/params/status/start_time", controller.get_time_start().strftime("%H:%M"))
        client.publish("home/params/status/stop_time", controller.get_time_stop().strftime("%H:%M"))
        client.publish("home/params/status/user_temp", controller.get_user_temp())
        client.publish("home/params/status/back_temp", controller.get_back_temp())
    elif message.topic == "home/relay/status":
        logging.info("Boiler Feedback: " + str(message.payload.decode("utf-8")))
    elif message.topic == "home/room/status":
        msg = message.payload.decode("utf-8")
        logging.info("Room Status: " + str(msg))
        data = json.loads(msg)
        try:
            cursor = conn.cursor()
            now_sql2 = datetime.now(pytz.timezone('UTC'))
            now_str2 = now_sql2.strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO " + POSTGRES_ROOM + \
                        "(temperature, humidity, timestamp)" + \
                        "VALUES (" + str(round(data["temp"],1)) + "," + str(round(data["hum"],1)) + \
                        ",\'" + now_str2 + "\'" ");"
            cur.execute(query)
        except Exception as e:
            log_str += " DBError"
            print(e)

    if set_flag == True:
        conf_str = json.dumps(dic, indent=4)
        with open('conf.json', 'w') as f:
            f.write(conf_str)
            f.close()

print("**************** Automatic Boiler program ***************")

# Configuration
UPDATE_MINUTE = 2
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN_DATA = 4
DHT_PIN_POWER = 27
client = mqtt.Client("RPi")
client.connect("localhost")
client.subscribe("home/relay/status")
client.subscribe("home/params/set/#")
client.subscribe("home/params/get")
client.subscribe("home/room/status")
client.on_message = on_message
client.loop_start()

# Initialization
GPIO.setmode(GPIO.BCM)
GPIO.setup(DHT_PIN_POWER, GPIO.OUT)
GPIO.output(DHT_PIN_POWER, GPIO.HIGH)

# Log file
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
now = datetime.now()
now_str = now.strftime("%Y%m%d_%H%M%S")
log_file = "../../logs/boiler_" + now_str + ".log"
logging.basicConfig(filename = log_file, level = logging.INFO)
print("- File " + log_file + " created")

# DB
conn = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PSSW)
conn.autocommit = True
boiler_st = None

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
        signal = controller.control(temperature, now.time())
        log_str += " Target={0:0.1f}ºC".format(controller.get_target_temp())
        client.publish("home/params/status/curr_temp", "{0:0.1f}".format(temperature))
        if signal == ControlResult.TURN_ON:
            client.publish("home/relay/set", 1)
            log_str += " ON"
            boiler_st = True
        elif signal == ControlResult.TURN_OFF:
            client.publish("home/relay/set", 0)
            log_str += " OFF"
            boiler_st = False

        # Postgres
        try:
            cur = conn.cursor()
            now_sql = datetime.now(pytz.timezone('UTC'))
            now_str = now_sql.strftime('%Y-%m-%d %H:%M:%S')
            sql_query = "INSERT INTO " + POSTGRES_TABL + \
                        "(temperature, humidity, timestamp, boiler)" + \
                        "VALUES (" + str(round(temperature,1)) + "," + str(round(humidity,1)) + \
                        ",\'" + now_str + "\'," + str(boiler_st) + ");"
            cur.execute(sql_query)
        except Exception as e:
            log_str += " DBError"
            print(e)
    else:
        log_str += " Failed to retrieve data from sensor"

    # Print
    logging.info(log_str)

    # Wait
    GPIO.output(DHT_PIN_POWER, GPIO.LOW)

    while True:
        time.sleep(1)
        now = datetime.now()
        if ((now.minute % 10) == UPDATE_MINUTE) and (now.second == 0):
            break

