from time import sleep
from machine import Pin
import network
from umqttsimple import MQTTClient

# GPIO
ON = 0
OFF = 1
relay = Pin(0, Pin.OUT, value = OFF)
led = Pin(2, Pin.OUT, value = OFF)
global relay_value, send_flag
relay_value = OFF
send_flag = True

# Configuration
global IP, GATEWAY, SUBNET, WIFI_ID, WIFI_PSSWD, MQTT_SERVER, MQTT_PORT
IP = "xxx.xxx.x.x"
GATEWAY = "xxx.xxx.x.x"
SUBNET = "xxx.xxx.x.x"
WIFI_ID = "your wifi"
WIFI_PSSWD  = "your password"
MQTT_SERVER = "your server"
MQTT_PORT = 1883

# Connects to wlan, led blinks during connection
def wlan_connect():
    led.value(OFF)
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.ifconfig((IP, SUBNET, GATEWAY, 'xxx.xxx.xxx.xxx'))
    print('connecting to network...')
    if not wlan.isconnected():
        wlan.connect(WIFI_ID, WIFI_PSSWD)
        while not wlan.isconnected():
            sleep(0.5)
            led.value(not led.value())
    print('network config:', wlan.ifconfig())
    led.value(ON)

# Connects and subscribe to MQTT server and topics
def mqtt_connect():
    topic_sub = b"home/relay/#"
    client = MQTTClient(client_id = 'BoilerRelay',
                        server = MQTT_SERVER,
                        port = MQTT_PORT)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker' , MQTT_SERVER)
    print('subscribed to %s topic' % topic_sub)
    client.publish('home/relay/status', 'Alive')
    return client

# MQTT callback
def sub_cb(topic, msg):
    global relay_value
    print(topic, msg)

    if topic == b"home/relay/set":
        if msg == b'1':
            relay_value = ON
        elif msg == b'0':
            relay_value = OFF
        relay.value(relay_value)
    
    if (topic == b"home/relay/set") or (topic == b"home/relay/get"):
        global send_flag
        send_flag = True

# Restarts and connect
def restart_and_reconnect():
  print('Failed to connect to Wifi or MQTT server. Reconnecting...')
  sleep(5)
  machine.reset()

# Main
def main():
    global relay_value, send_flag
    while True:
        try:
            # Connects
            wlan_connect()
            client = mqtt_connect()
            while True:
                # Wait for messages
                client.wait_msg()
                
                # If it has to send something (set in callback)
                if send_flag == True:
                    if relay_value == ON:
                        client.publish('home/relay/status', 'ON')
                    elif relay_value == OFF:
                        client.publish('home/relay/status', 'OFF')
                    send_flag = False
        except:
            print("Exception")

if __name__ == "__main__":
    main()
