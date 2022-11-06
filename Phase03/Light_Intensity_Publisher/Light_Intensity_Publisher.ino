#include <ESP8266WiFi.h>
#include <PubSubClient.h>

//SET THIS THREE VALUES IF TESTING THE CODE
//const char* ssid = "TP-Link_2AD8";
//const char* password = "14730078";
//const char* mqtt_server = "192.168.0.158"

// Chilka: I'm testing this at home so just change this three lines if you want to test it too
const char* ssid = "EBOX-9994";
const char* password = "97479ec13d";
const char* mqtt_server = "192.168.1.110";
WiFiClient vanieriot;
PubSubClient client(vanieriot);

// light setup
const int pResistor = A0;
const int ledPin = 16; // equivalent D0
// Variables
int value;
char* ledStatus = "OFF";

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messagein;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messagein += (char)message[i];
  }

}
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("vanieriot")) {
      Serial.println("connected");

    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      // Wait 5 seconds before retrying
      delay(3000);
    }
  }
}
void setup() {

  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  Serial.println();
  pinMode(ledPin, OUTPUT);
  pinMode(pResistor, INPUT);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  if (!client.loop())
    client.connect("vanieriot");

// get value of the light intensity
  value = analogRead(pResistor);
  delay(10000);
  digitalWrite(ledPin, LOW);
  Serial.println("Light intensity is: ");
  Serial.println(value);

  if (value < 400) {
    digitalWrite(ledPin, HIGH);
    ledStatus = "ON";
    Serial.println("Led Status Activated: ");
    Serial.println(ledStatus);
    delay(3000);
  }
//  else {
//    digitalWrite(ledPin, LOW);
//    ledStatus = "OFF";
//  }
   //publish value
   char pResistorValue[8];
   dtostrf(value, 6,2, pResistorValue); 
    
   client.publish("esp/lightintensity", pResistorValue);
   client.publish("esp/lightswitch", ledStatus);
  
}
