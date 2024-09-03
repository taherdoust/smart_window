import paho.mqtt.client as mqtt
import json
import requests

# Fetch MQTT settings from catalog API
catalog_api_url = "http://localhost:3002/mqtt_settings"
mqtt_settings = requests.get(catalog_api_url).json()
PLATFORM_NAME = mqtt_settings["PLATFORM_NAME"]
MQTT_BROKER = mqtt_settings["mqtt"]["broker"]["address"]
MQTT_PORT = mqtt_settings["mqtt"]["broker"]["port"]
TOPIC = f"{PLATFORM_NAME}/commands/window"

# Room and Project Details
PROJECT_ID = "proj2v"
ROOM_ID = "room2"

# MQTT Client Setup
client = mqtt.Client()

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    command = payload.get("command", "")
    project_id = payload.get("project_ID", "")
    room_id = payload.get("room_ID", "")

    if project_id == PROJECT_ID and room_id == ROOM_ID:
        if command == "open":
            print("Window opened by command.")
        elif command == "close":
            print("Window closed by command.")
        else:
            print("Unknown command received.")

def connect_mqtt():
    client.on_connect = lambda c, u, f, rc: print(f"Connected to MQTT Broker with result code {rc}")
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    client.subscribe(TOPIC)

if __name__ == "__main__":
    connect_mqtt()
    while True:
        # Keep the script running to listen for messages
        pass
