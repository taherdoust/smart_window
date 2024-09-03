import paho.mqtt.client as mqtt
import requests
import json
import time

# Fetch MQTT settings from catalog API
catalog_api_url = "http://localhost:3002/mqtt_settings"
catalog_projects_url = "http://localhost:3002/projects"

try:
    mqtt_settings = requests.get(catalog_api_url).json()
    PLATFORM_NAME = mqtt_settings["PLATFORM_NAME"]
    MQTT_BROKER = mqtt_settings['mqtt']['broker']["address"]
    MQTT_PORT = mqtt_settings['mqtt']['broker']["port"]
except KeyError as e:
    print(f"Missing key in MQTT settings: {e}")
    exit(1)

TOPIC = f"{PLATFORM_NAME}/commands/window"

# Corrected API URLs
DATABASE_API_URL = "http://localhost:3001/sensor_data"
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

def parse_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"Error converting value to float: {value}")
        return None

def check_conditions_and_control_window(project_ID, room_ID):
    try:
        # Correct endpoint structure: include project_ID and room_ID in the path
        response = requests.get(f"{DATABASE_API_URL}/{project_ID}/{room_ID}/latest")
        response.raise_for_status()
        data = response.json()

        temperature = parse_float(data.get("temperature"))
        humidity = parse_float(data.get("humidity"))

        if temperature is None or humidity is None:
            print(f"Invalid sensor values: Temperature: {data.get('temperature')}, Humidity: {data.get('humidity')}")
            return

        thresholds_response = requests.get(f"{CATALOG_API_URL}/{project_ID}/{room_ID}")
        thresholds_response.raise_for_status()
        thresholds = thresholds_response.json()

        temp_threshold = float(thresholds.get("temperature_threshold", 0))
        hum_threshold = float(thresholds.get("humidity_threshold", 0))

        print(f"Temperature: {temperature}, Humidity: {humidity}")
        print(f"Temperature Threshold: {temp_threshold}, Humidity Threshold: {hum_threshold}")

        # Send "open" if either value is above its threshold, "close" only if both are below
        if temperature > temp_threshold or humidity > hum_threshold:
            send_command("open", project_ID, room_ID)
        else:
            send_command("close", project_ID, room_ID)

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as e:
        print(f"Failed to control window: {e}")

def setup_mqtt():
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

def get_projects_and_rooms():
    try:
        response = requests.get(catalog_projects_url)
        response.raise_for_status()
        projects = response.json()
        return {
            project_ID: list(project["rooms"].keys())
            for project_ID, project in projects.items()
        }
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch projects and rooms: {e}")
        return {}

if __name__ == '__main__':
    setup_mqtt()
    
    # Fetch projects and their rooms dynamically
    projects = get_projects_and_rooms()

    while True:
        for project_ID, rooms in projects.items():
            for room_ID in rooms:
                check_conditions_and_control_window(project_ID, room_ID)
        time.sleep(60)  # Check every 10 minutes
