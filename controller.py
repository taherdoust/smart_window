import paho.mqtt.client as mqtt
import requests
import json
import time

# Fetch MQTT settings from catalog API
catalog_api_url = "http://localhost:3002/mqtt_settings"
mqtt_settings = requests.get(catalog_api_url).json()
PLATFORM_NAME = mqtt_settings["PLATFORM_NAME"]
MQTT_BROKER = mqtt_settings["mqtt"]["broker"]["address"]
MQTT_PORT = mqtt_settings["mqtt"]["broker"]["port"]
TOPIC = mqtt_settings["mqtt"]["topic"]

# API URLs
DATABASE_API_URL = "http://localhost:3001/sensor_data/latest"
CATALOG_API_URL = "http://localhost:3002/thresholds"

# MQTT client
client = mqtt.Client()

def send_command(command, project_ID, room_ID):
    command_data = {
        "project_ID": project_ID,
        "room_ID": room_ID,
        "command": command
    }
    client.publish(TOPIC, json.dumps(command_data))
    print(f"Sent command: '{command}' to project: '{project_ID}', room: '{room_ID}'")

def check_conditions_and_control_window(project_ID, room_ID):
    try:
        # Get the latest sensor data
        response = requests.get(f"{DATABASE_API_URL}?project_ID={project_ID}&room_ID={room_ID}")
        response.raise_for_status()
        data = response.json()

        # Convert temperature and humidity to floats
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])

        # Get the thresholds from the catalog API
        thresholds_response = requests.get(f"{CATALOG_API_URL}/{project_ID}/{room_ID}")
        thresholds_response.raise_for_status()
        thresholds = thresholds_response.json()

        temp_threshold = float(thresholds["temperature_threshold"])
        hum_threshold = float(thresholds["humidity_threshold"])

        print(f"Temperature: {temperature}, Humidity: {humidity}")
        print(f"Temperature Threshold: {temp_threshold}, Humidity Threshold: {hum_threshold}")

        # Determine if the window should be opened or closed
        if temperature > temp_threshold or humidity > hum_threshold:
            send_command("open", project_ID, room_ID)
        else:
            send_command("close", project_ID, room_ID)

    except Exception as e:
        print(f"Failed to control window: {e}")

def setup_mqtt():
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

if __name__ == '__main__':
    setup_mqtt()
    project_ID = "proj2v"  # Set the project ID
    rooms = ["room1", "room2"]  # List of rooms in the project

    while True:
        for room_ID in rooms:
            check_conditions_and_control_window(project_ID, room_ID)
        time.sleep(60)  # Wait 60 seconds before checking again
