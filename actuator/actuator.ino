#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>
#include <time.h> // Include the time library for NTP synchronization

// WiFi and MQTT settings
const char* ssid = "ali_Redmi";
const char* password = "taher3537";
const char* mqtt_server = "mqtt.eclipseprojects.io";
const char* mqtt_topic = "test1/commands/window";
const char* target_project_ID = "proj1";
const char* target_room_ID = "room1";

// Servo configuration
Servo myservo;
const int servoPin = 5;
bool window_open = false;

// WiFi and MQTT clients
WiFiClient espClient;
PubSubClient client(espClient);

// NTP Server settings for Italian time zone
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;           // GMT offset for Italy (CET is UTC+1)
const int   daylightOffset_sec = 3600;      // Daylight offset for CEST (adds 1 hour)

// Function to get and set time from NTP server
void setupTime() {
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.print("Waiting for NTP time sync...");
  while (!time(nullptr)) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println(" Time synchronized");
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

// Function to extract value from JSON string
String getValueFromJson(String json, String field) {
  int startIndex = json.indexOf("\"" + field + "\"");
  if (startIndex == -1) return "";

  startIndex = json.indexOf(":", startIndex);
  startIndex = json.indexOf("\"", startIndex) + 1;
  int endIndex = json.indexOf("\"", startIndex);

  if (startIndex == 0 || endIndex == -1) return "";
  return json.substring(startIndex, endIndex);
}

// MQTT callback for receiving commands
void callback(char* topic, byte* message, unsigned int length) {
  String payload = "";

  for (unsigned int i = 0; i < length; i++) {
    payload += (char)message[i];
  }

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(payload);

  String project_ID = getValueFromJson(payload, "project_ID");
  String room_ID = getValueFromJson(payload, "room_ID");
  String command = getValueFromJson(payload, "command");

  Serial.print("Parsed project_ID: ");
  Serial.println(project_ID);
  Serial.print("Parsed room_ID: ");
  Serial.println(room_ID);
  Serial.print("Parsed command: ");
  Serial.println(command);

  if (project_ID == target_project_ID && room_ID == target_room_ID) {
    if (command == "open" && !window_open) {
      myservo.write(90); 
      window_open = true;
      Serial.println("Window opened by command.");
    } else if (command == "close" && window_open) {
      myservo.write(0);  
      window_open = false;
      Serial.println("Window closed by command.");
    } else {
      Serial.println("Command already in desired state.");
    }

    // Log the current time
    time_t now = time(nullptr);
    struct tm* timeinfo = localtime(&now);
    Serial.printf("Action logged at: %02d:%02d:%02d, %04d-%02d-%02d\n",
                  timeinfo->tm_hour, timeinfo->tm_min, timeinfo->tm_sec,
                  timeinfo->tm_year + 1900, timeinfo->tm_mon + 1, timeinfo->tm_mday);
  } else {
    Serial.println("Command not intended for this actuator.");
  }
}

// Function to reconnect to the MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("ESP32WindowActuator")) {
      Serial.println("Connected to MQTT broker");
      client.subscribe(mqtt_topic);  
      Serial.print("Subscribed to topic: ");
      Serial.println(mqtt_topic);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  setupTime(); // Initialize time using NTP
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  myservo.attach(servoPin);
  myservo.write(0); 

  Serial.println("System ready for commands."); 
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
