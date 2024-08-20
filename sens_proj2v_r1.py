import paho.mqtt.client as mqtt
import json
import random
import time
import requests

# Fetch MQTT settings from catalog API
catalog_api_url = "http://localhost:3002/mqtt_settings"
mqtt_settings = requests.get(catalog_api_url).json()

# Debugging: Print the API response
print(mqtt_settings)

# Now try to access the keys
try:
    PLATFORM_NAME = mqtt_settings["PLATFORM_NAME"]
    MQTT_BROKER = mqtt_settings["mqtt"]["broker"]["address"]
    MQTT_PORT = mqtt_settings["mqtt"]["broker"]["port"]
    TOPIC = mqtt_settings["mqtt"]["topic"]
except KeyError as e:
    print(f"Key error: {e}")
    raise

# Room configuration
project_ID = "proj2v"
room_ID = "room1"

# MQTT client setup
client = mqtt.Client()

def connect_mqtt():
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

def publish_sensor_data():
    while True:
        temperature = round(random.uniform(20, 30), 2)
        humidity = round(random.uniform(40, 70), 2)
        data = {
            "project_ID": project_ID,
            "room_ID": room_ID,
            "temperature": temperature,
            "humidity": humidity
        }
        client.publish(TOPIC, json.dumps(data))
        print(f"Published data: {data}")
        time.sleep(60)  # Publish data every 60 seconds

if __name__ == '__main__':
    connect_mqtt()
    publish_sensor_data()
