#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

// WiFi and MQTT settings
const char* ssid = "ali_Redmi";
const char* password = "taher3537";
const char* mqtt_server = "mqtt.eclipseprojects.io";
const char* project_name = "test1";

// Servo configuration for window control
Servo myservo;
const int servoPin = 5;
bool window_open = false;

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

// MQTT callback for receiving commands
void callback(char* topic, byte* message, unsigned int length) {
  String command;
  for (int i = 0; i < length; i++) {
    command += (char)message[i];
  }

  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(command);

  if (String(topic) == String(project_name) + "/commands/window") {
    if (command == "open" && !window_open) {
      myservo.write(90);  // Open the window
      window_open = true;
      Serial.println("Window opened by command.");
    } else if (command == "close" && window_open) {
      myservo.write(0);  // Close the window
      window_open = false;
      Serial.println("Window closed by command.");
    }
  }
}

// Function to reconnect to the MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32WindowActuator")) {
      Serial.println("connected");
      client.subscribe((String(project_name) + "/commands/window").c_str());
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(9600);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // Initialize the servo motor
  myservo.attach(servoPin);
  myservo.write(0);  // Ensure window is closed initially
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
