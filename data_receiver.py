import paho.mqtt.client as mqtt
import json
import requests
from datetime import datetime

# Fetch MQTT settings from catalog API
catalog_api_url = "http://localhost:3002/mqtt_settings"
mqtt_settings = requests.get(catalog_api_url).json()
PLATFORM_NAME = mqtt_settings["PLATFORM_NAME"]
MQTT_BROKER = mqtt_settings["mqtt"]["broker"]["address"]
MQTT_PORT = mqtt_settings["mqtt"]["broker"]["port"]
TOPIC = mqtt_settings["mqtt"]["topic"]

# Database API URL
DATABASE_API_URL = "http://localhost:3001/sensor_data/"

# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(TOPIC)

# MQTT on_message callback
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        # Add the timestamps
        data["timestamp"] = datetime.now().isoformat()
        data["datestamp"] = datetime.now().date().isoformat()

        # Send the data to the database API
        response = requests.post(DATABASE_API_URL, json=data)
        response.raise_for_status()
        print(f"Data sent to API: {data}")

    except Exception as e:
        print(f"Failed to process data: {e}")

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
