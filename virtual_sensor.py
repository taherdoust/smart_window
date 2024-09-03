import paho.mqtt.client as mqtt
import random
import json
import time
import requests

# Fetch MQTT settings from catalog API
catalog_api_url = "http://localhost:3002/mqtt_settings"
mqtt_settings = requests.get(catalog_api_url).json()
PLATFORM_NAME = mqtt_settings["PLATFORM_NAME"]
MQTT_BROKER = mqtt_settings["mqtt"]["broker"]["address"]
MQTT_PORT = mqtt_settings["mqtt"]["broker"]["port"]
TOPIC = mqtt_settings["mqtt"]["topic"]

# Room and Project Details
PROJECT_ID = "proj2v"
ROOM_ID = "room1"

# MQTT Client Setup
client = mqtt.Client()

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    client.on_connect = on_connect
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

def publish_sensor_data():
    temperature = round(random.uniform(20.0, 30.0), 1)
    humidity = round(random.uniform(30.0, 60.0), 1)
    timestamp = time.strftime("%H:%M:%S")
    datestamp = time.strftime("%Y-%m-%d")

    payload = {
        "project_ID": PROJECT_ID,
        "room_ID": ROOM_ID,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": timestamp,
        "datestamp": datestamp
    }

    client.publish(TOPIC, json.dumps(payload))
    print("Publishing data:", payload)
    print(f"Data published to {TOPIC}")

if __name__ == "__main__":
    connect_mqtt()
    while True:
        publish_sensor_data()
        time.sleep(600)  # Simulate sensor data publishing every 10 min
