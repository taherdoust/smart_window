#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// WiFi and MQTT settings
const char* ssid = "ali_Redmi";
const char* password = "taher3537";
const char* mqtt_server = "mqtt.eclipseprojects.io";
const char* project_name = "test1";
const char* project_ID = "proj1";
const char* room_ID = "room1";

// DHT sensor configuration
#define DHTPIN 17
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);

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

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

// Function to reconnect to the MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Sensor")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

// Function to publish sensor data
void publish_sensor_data(float temperature, float humidity) {
  String payload = "{\"project_ID\":\"" + String(project_ID) + "\", \"room_ID\":\"" + String(room_ID) + "\", ";
  payload += "\"temperature\":" + String(temperature) + ", ";
  payload += "\"humidity\":" + String(humidity) + "}";

  client.publish((String(project_name) + "/sensors").c_str(), payload.c_str());
  Serial.print("Publishing data: ");
  Serial.println(payload);
}

void setup() {
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);

  // Initialize DHT sensor
  dht.begin();
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
  } else {
    // Publish sensor data
    publish_sensor_data(temperature, humidity);
  }

  delay(60000);  // Delay for 60 seconds before reading again
}
