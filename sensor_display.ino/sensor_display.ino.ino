#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <time.h>

// ── User settings ───────────────────────────────────────────────────────────────
const char* ssid       = "Vodafone-C02080026";
const char* password   = "MeE76EGLafbKX4b6";
const char* mqtt_server= "mqtt.eclipseprojects.io";
const char* mqtt_topic = "test1";
const char* project_ID = "proj1";
const char* room_ID    = "room1";

#define DHTPIN 17
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);

// LCD (I2C address 0x27 frequently used; change if your scanner shows different)
LiquidCrystal_I2C mylcd(0x27, 16, 2);

// Time (Europe/Rome DST rules)
const char* ntpServer = "pool.ntp.org";

// Reconnect cadence
unsigned long lastMqttAttempt = 0;
const unsigned long mqttRetryEveryMs = 5000;

// ── Helpers ─────────────────────────────────────────────────────────────────────
bool connectWifi(uint32_t timeoutMs = 15000) {
  Serial.printf("Connecting to %s\n", ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  unsigned long t0 = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - t0 < timeoutMs) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("WiFi OK, IP: "); Serial.println(WiFi.localIP());
    return true;
  } else {
    Serial.println("WiFi FAILED (timeout), continuing offline");
    return false;
  }
}

bool connectMqtt(uint32_t timeoutMs = 8000) {
  unsigned long t0 = millis();
  Serial.print("MQTT: connecting");
  while (millis() - t0 < timeoutMs) {
    if (client.connect("ESP32Sensor")) {
      Serial.println("\nMQTT OK");
      return true;
    }
    Serial.print(".");
    delay(500);
  }
  Serial.println("\nMQTT FAILED (timeout), will retry later");
  return false;
}

void publish_sensor_data(float temperature, float humidity) {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("No time yet; skipping timestamped publish");
    return;
  }

  char timeStamp[9];
  char dateStamp[11];
  strftime(timeStamp, sizeof(timeStamp), "%H:%M:%S", &timeinfo);
  strftime(dateStamp, sizeof(dateStamp), "%Y-%m-%d", &timeinfo);

  String payload = "{\"project_ID\":\"" + String(project_ID) + "\", \"room_ID\":\"" + String(room_ID) + "\", ";
  payload += "\"temperature\":" + String(temperature) + ", ";
  payload += "\"humidity\":" + String(humidity) + ", ";
  payload += "\"timestamp\":\"" + String(timeStamp) + "\", ";
  payload += "\"datestamp\":\"" + String(dateStamp) + "\"}";

  client.publish(mqtt_topic, payload.c_str());
  Serial.print("Published: ");
  Serial.println(payload);
}

// ── Arduino lifecycle ───────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(50);

  // I2C pins (ESP32 default is SDA=21, SCL=22; set explicitly for clarity)
  Wire.begin(21, 22);

  mylcd.init();
  mylcd.backlight();
  mylcd.clear();
  mylcd.setCursor(0, 0); mylcd.print("WiFi...");
  bool wifiOK = connectWifi();

  dht.begin();

  // Time zone for Italy with DST
  setenv("TZ", "CET-1CEST,M3.5.0/2,M10.5.0/3", 1); // Rome DST rules
  tzset();
  configTime(0, 0, ntpServer);

  client.setServer(mqtt_server, 1883);

  if (wifiOK) {
    mylcd.setCursor(0, 0); mylcd.print("MQTT...");
    connectMqtt(); // try once during setup, but don't block forever
  }

  // Show something meaningful on boot
  mylcd.clear();
  mylcd.setCursor(0, 0); mylcd.print("Init done");
  mylcd.setCursor(0, 1); mylcd.print("Reading in 3s");
  delay(3000);
}

void loop() {
  // Maintain MQTT only if connected; otherwise, retry occasionally without blocking UI
  if (WiFi.status() == WL_CONNECTED) {
    if (!client.connected()) {
      unsigned long now = millis();
      if (now - lastMqttAttempt > mqttRetryEveryMs) {
        lastMqttAttempt = now;
        connectMqtt();
      }
    } else {
      client.loop();
    }
  }

  // Read sensors & update LCD regardless of MQTT state
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  mylcd.clear();
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT read failed");
    mylcd.setCursor(0, 0); mylcd.print("Sensor Error");
  } else {
    Serial.printf("T: %.1fC  H: %.1f%%\n", temperature, humidity);
    mylcd.setCursor(0, 0); mylcd.print("Temp:");
    mylcd.setCursor(6, 0); mylcd.print(temperature, 1); mylcd.print("C");
    mylcd.setCursor(0, 1); mylcd.print("Hum :");
    mylcd.setCursor(6, 1); mylcd.print(humidity, 1); mylcd.print("%");

    if (client.connected())
      publish_sensor_data(temperature, humidity);
    else
      Serial.println("MQTT offline, skipped publish");
  }

  // Shorter delay while testing; set back to 900000 (15 min) later
  delay(5000);
}
