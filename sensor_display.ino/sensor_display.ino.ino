#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <TimeLib.h>  // Ensure you have the Time library installed
#include <time.h>     // For NTP

// WiFi and MQTT settings
const char* ssid = "ali_Redmi";
const char* password = "taher3537";
const char* mqtt_server = "mqtt.eclipseprojects.io";  // MQTT broker address
const int mqtt_port = 1883;                           // MQTT broker port
const char* mqtt_topic = "test1";                     // MQTT topic
const char* project_ID = "proj1";                     // Project ID
const char* room_ID = "room1";                        // Room ID

// DHT sensor configuration
#define DHTPIN 17
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);

// LCD configuration
LiquidCrystal_I2C mylcd(0x27, 16, 2);  // LCD I2C address

// NTP Server settings
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 0;       // Offset from GMT in seconds
const int   daylightOffset_sec = 3600;  // Daylight offset (1 hour for most places)

// Function to get and set time from NTP server
void setupTime() {
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.print("Waiting for NTP time sync...");
  while (!time(nullptr)) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("Time synchronized");
}

// Function to connect to WiFi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// Function to reconnect to the MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Sensor")) {
      Serial.println("Connected to MQTT broker");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Try again in 5 seconds");
      delay(5000);
    }
  }
}

// Function to publish sensor data
void publish_sensor_data(float temperature, float humidity) {
  time_t now = time(nullptr);
  struct tm* timeinfo = localtime(&now);
  String timestamp = String(timeinfo->tm_hour) + ":" + String(timeinfo->tm_min) + ":" + String(timeinfo->tm_sec);
  String datestamp = String(timeinfo->tm_year + 1900) + "-" + String(timeinfo->tm_mon + 1) + "-" + String(timeinfo->tm_mday);

  String payload = "{\"project_ID\":\"" + String(project_ID) + "\", \"room_ID\":\"" + String(room_ID) + "\", ";
  payload += "\"temperature\":" + String(temperature) + ", ";
  payload += "\"humidity\":" + String(humidity) + ", ";
  payload += "\"timestamp\":\"" + timestamp + "\", ";
  payload += "\"datestamp\":\"" + datestamp + "\"}";

  client.publish(mqtt_topic, payload.c_str());
  Serial.print("Publishing data: ");
  Serial.println(payload);
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Initializing ESP32...");

  setup_wifi();
  setupTime();  // Initialize time using NTP
  client.setServer(mqtt_server, mqtt_port);

  // Initialize DHT sensor
  dht.begin();
  Serial.println("DHT sensor initialized.");

  // Initialize LCD
  mylcd.init();
  mylcd.backlight();
  mylcd.setCursor(0, 0);
  mylcd.print("Initializing...");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read sensor data
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    mylcd.setCursor(0, 0);
    mylcd.print("Sensor Error     ");
  } else {
    // Display data on the serial monitor
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" °C, Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");

    // Display temperature and humidity on LCD
    mylcd.setCursor(0, 0);
    mylcd.print("Temp: ");
    mylcd.print(temperature);
    mylcd.print(" C   ");

    mylcd.setCursor(0, 1);
    mylcd.print("Humidity: ");
    mylcd.print(humidity);
    mylcd.print(" %   ");

    // Publish sensor data
    publish_sensor_data(temperature, humidity);
  }

  delay(60000);  // Delay for 60 seconds before reading again
}
