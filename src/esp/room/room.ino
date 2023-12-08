#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include "config.h"

//**********************************************************
// config.h must be something like this:
// const char* WIFI_ID = "YourWifiName";
// const char* WIFI_PSSWD  = "Your Password";
// const char* MQTT_SERVER = "URL of the MQTT server";
// const int MQTT_SERVER_PORT = 1883;
//**********************************************************

//#define DHTTYPE DHT11
#define DHTTYPE DHT22     // Sensor DHT22
#define DHTPIN D3         // DHT sensor pin
#define LED D4            // Built-in led
#define SLEEP_TIME_MIN 10 // sleep time in minutes 

DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);

void read_sensor() {  
  float h = dht.readHumidity();
  float t = dht.readTemperature(); 
  //--------Serial-------------
  Serial.print("Humedad: ");
  Serial.print(h);
  Serial.print(" %t");
  Serial.print(" Temperatura: ");
  Serial.print(t);
  Serial.print(" *C ");
  Serial.println();

  // ---- MQTT send ----
  StaticJsonDocument<256> doc;
  doc["temp"] = t;
  doc["hum"] = h;
  char msg[40];
  int b = serializeJson(doc, msg);
  client.publish("home/room/status", msg);
}

void configureWifi()
{
  WiFi.begin(WIFI_ID, WIFI_PSSWD);

  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
    digitalWrite(LED, !digitalRead(LED));
  }
  Serial.println();
  Serial.print("Connected, IP: ");
  Serial.println(WiFi.localIP());
  digitalWrite(LED, LOW);
}

void callback(char* topic, byte* payload, unsigned int length)
{
}

void setup() {
  unsigned long start_time = millis();
  dht.begin();

  // hardware
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);

  // serial port
  Serial.begin(115200);
  Serial.println();

  // WiFi
  configureWifi();
  
  // MQTT comm
  client.setServer(MQTT_SERVER, MQTT_SERVER_PORT);
  client.setCallback(callback);
  client.connect("RoomClient");

  read_sensor();

  client.disconnect();
  WiFi.disconnect();
  unsigned long current_time = millis();
  unsigned long elapsed_time = current_time - start_time;
  Serial.println(((SLEEP_TIME_MIN * 60000) - elapsed_time)* 1000);
  ESP.deepSleep(((SLEEP_TIME_MIN * 60000) - elapsed_time)* 1000);
}


void loop(){};
