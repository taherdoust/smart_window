import paho.mqtt.client as mqtt
import requests
import json

# Fetch MQTT settings from catalog API
catalog_api_url = "http://localhost:3002/mqtt_settings/"
try:
    mqtt_settings = requests.get(catalog_api_url).json()
except requests.exceptions.RequestException as e:
    print(f"Failed to fetch MQTT settings: {e}")
    exit(1)

# Extract platform name and MQTT settings
PLATFORM_NAME = mqtt_settings.get("PLATFORM_NAME", "default_platform")
broker_info = mqtt_settings.get("broker", {})
MQTT_BROKER = broker_info.get("address", "mqtt.eclipseprojects.io")
MQTT_PORT = broker_info.get("port", 1883)
MQTT_TOPIC = mqtt_settings.get("topic", PLATFORM_NAME)

# Fetch Database API URL
try:
    database_api_url_response = requests.get("http://localhost:3002/database_api_url")
    DATABASE_API_URL = database_api_url_response.json().get("url", "http://localhost:3001")
except requests.exceptions.RequestException as e:
    print(f"Failed to fetch Database API URL: {e}")
    exit(1)

# MQTT client setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        project_id = data.get("project_ID")
        room_id = data.get("room_ID")
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        timestamp = data.get("timestamp")
        datestamp = data.get("datestamp")

        # Construct the data to send to the Database API
        sensor_data = {
            "project_ID": project_id,
            "room_ID": room_id,
            "temperature": temperature,
            "humidity": humidity,
            "timestamp": timestamp,
            "datestamp": datestamp
        }

        # Send data to the Database API
        response = requests.post(f"{DATABASE_API_URL}/sensor_data/", json=sensor_data)
        response.raise_for_status()  # Raise an error for bad responses
        print(f"Data sent to API: {sensor_data}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to process data: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
