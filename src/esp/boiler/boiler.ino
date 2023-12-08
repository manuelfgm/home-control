#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "config.h"

//**********************************************************
// config.h must be something like this:
// const char* WIFI_ID = "YourWifiName";
// const char* WIFI_PSSWD  = "Your Password";
// const char* MQTT_SERVER = "URL of the MQTT server";
// const int MQTT_SERVER_PORT = 1883;
//**********************************************************

#define RELAY 0
#define LED 2

IPAddress ip(000,000,0,000);     
IPAddress gateway(000,000,0,0);   
IPAddress subnet(255,255,255,0);

WiFiClient espClient;
PubSubClient client(espClient);

void configureWifi()
{
  delay(5);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.print(WIFI_ID);

  // Static IP
  WiFi.mode(WIFI_STA);
  WiFi.config(ip, gateway, subnet);
  WiFi.begin(WIFI_ID, WIFI_PSSWD);

  // Connect
  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
    digitalWrite(LED, !digitalRead(LED));
  }
  digitalWrite(LED, LOW);
  Serial.println();
  Serial.println("WiFi connected");
}

void setup() {
  Serial.begin(9600);
  delay(10);

  // GPIO
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
  pinMode(RELAY, OUTPUT);
  digitalWrite(RELAY, HIGH);

  // WiFi
  configureWifi();

  // MQTT comm
  client.setServer(MQTT_SERVER, MQTT_SERVER_PORT);
  client.setCallback(callback);
}

void callback(char* topic, byte* payload, unsigned int length)
{
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  if (strcmp(topic, "home/relay/set") == 0){
    // Switch on the LED if an 1 was received as first character
    if ((char)payload[0] == '1') {
      digitalWrite(RELAY, LOW); 
    } else if ((char)payload[0] == '0'){
      digitalWrite(RELAY, HIGH); 
    }
  }
  if(digitalRead(RELAY) == LOW){
    client.publish("home/relay/status", "ON");
  } else{
    client.publish("home/relay/status", "OFF");
  }
}
 
void reconnect()
{
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");
      // Once connected, publish an announcement...
      client.publish("home/relay/status", "(Re)Connected");
      // ... and resubscribe
      client.subscribe("home/relay/set");
      client.subscribe("home/relay/get");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      for(int i = 0; i < 10; ++i)
      {
        digitalWrite(LED, !digitalRead(LED));
        delay(500);
      }
    }
  }
  digitalWrite(LED, LOW);
}
 
void loop() 
{
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
