#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <time.h>

// WiFi and MQTT settings
const char* ssid = "ali_Redmi";
const char* password = "taher3537";
const char* mqtt_server = "mqtt.eclipseprojects.io";
const char* mqtt_topic = "test1";
const char* project_ID = "proj1";
const char* room_ID = "room1";

// DHT sensor configuration
#define DHTPIN 17
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);

// LCD configuration
LiquidCrystal_I2C mylcd(0x27, 16, 2);

// Timezone for Italy
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = 3600; // GMT+1
const int daylightOffset_sec = 3600; // Daylight savings

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

void publish_sensor_data(float temperature, float humidity) {
  time_t now;
  struct tm timeinfo;
  if(!getLocalTime(&timeinfo)){
    Serial.println("Failed to obtain time");
    return;
  }

  char timeStamp[9];
  char dateStamp[11];
  
  // Format the timestamp and datestamp to ensure leading zeros
  strftime(timeStamp, sizeof(timeStamp), "%H:%M:%S", &timeinfo);
  strftime(dateStamp, sizeof(dateStamp), "%Y-%m-%d", &timeinfo);

  String payload = "{\"project_ID\":\"" + String(project_ID) + "\", \"room_ID\":\"" + String(room_ID) + "\", ";
  payload += "\"temperature\":" + String(temperature) + ", ";
  payload += "\"humidity\":" + String(humidity) + ", ";
  payload += "\"timestamp\":\"" + String(timeStamp) + "\", ";
  payload += "\"datestamp\":\"" + String(dateStamp) + "\"}";

  client.publish(mqtt_topic, payload.c_str());
  Serial.print("Publishing data: ");
  Serial.println(payload);
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);

  dht.begin();

  // Initialize LCD
  mylcd.init();
  mylcd.backlight();
  mylcd.setCursor(0, 0);
  mylcd.print("Initializing...");

  // Set up NTP for time synchronization
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    mylcd.setCursor(0, 0);
    mylcd.print("Sensor Error     ");
  } else {
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.print(" °C, Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");

    mylcd.setCursor(0, 0);
    mylcd.print("Temp: ");
    mylcd.print(temperature);
    mylcd.print(" C   ");

    mylcd.setCursor(0, 1);
    mylcd.print("Humidity: ");
    mylcd.print(humidity);
    mylcd.print(" %   ");

    publish_sensor_data(temperature, humidity);
  }

  delay(10000);
}
