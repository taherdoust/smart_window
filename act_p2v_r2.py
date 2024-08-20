import paho.mqtt.client as mqtt
import requests
import json  # Import the json module

# Fetch MQTT settings from catalog API
catalog_api_url = "http://localhost:3002/mqtt_settings"
mqtt_settings = requests.get(catalog_api_url).json()
PLATFORM_NAME = mqtt_settings["PLATFORM_NAME"]
MQTT_BROKER = mqtt_settings["mqtt"]["broker"]["address"]
MQTT_PORT = mqtt_settings["mqtt"]["broker"]["port"]
TOPIC = mqtt_settings["mqtt"]["topic"]

# Room configuration
room_ID = "room2"  

window_open = False

# MQTT client setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    global window_open
    command_data = json.loads(msg.payload.decode())
    
    if command_data["room_ID"] == room_ID:
        command = command_data.get("command")
        if command == "open" and not window_open:
            window_open = True
            print(f"Window opened in {room_ID}")
        elif command == "close" and window_open:
            window_open = False
            print(f"Window closed in {room_ID}")

def connect_mqtt():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

if __name__ == '__main__':
    connect_mqtt()
