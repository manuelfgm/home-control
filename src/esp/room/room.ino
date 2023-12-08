#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "config.h"

//#define DHTTYPE DHT11
#define DHTTYPE DHT22     // Sensor DHT22
#define DHTPIN D3         // DHT sensor pin
#define LED D4            // Built-in led
#define SLEEP_TIME_MIN 1 // sleep time in minutes 

DHT dht(DHTPIN, DHTTYPE);

void read_sensor() {  
  float h = dht.readHumidity();
  float t = dht.readTemperature(); 
  //--------Enviamos las lecturas por el puerto serial-------------
  Serial.print("Humedad: ");
  Serial.print(h);
  Serial.print(" %t");
  Serial.print(" Temperatura: ");
  Serial.print(t);
  Serial.print(" *C ");
  Serial.println();
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

  read_sensor();
  
  WiFi.disconnect();
  unsigned long current_time = millis();
  unsigned long elapsed_time = current_time - start_time;
  Serial.println(((SLEEP_TIME_MIN * 60000) - elapsed_time)* 1000);
  ESP.deepSleep(((SLEEP_TIME_MIN * 60000) - elapsed_time)* 1000);
}


void loop(){};
