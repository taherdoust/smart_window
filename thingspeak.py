import requests
import paho.mqtt.client as mqtt
import json
import time

# URLs for fetching settings from the catalog API
CATALOG_API_URL = "http://localhost:3002"
THING_SPEAK_KEY_URL = f"{CATALOG_API_URL}/thingspeak_key/proj1/room1"
DATABASE_API_URL = f"{CATALOG_API_URL}/database_api_url"
MQTT_SETTINGS_URL = f"{CATALOG_API_URL}/mqtt_settings"

# Fetch ThingSpeak API key for proj1_room1
def get_thingspeak_key():
    response = requests.get(THING_SPEAK_KEY_URL)
    if response.status_code == 200:
        return response.json()["api_key"]
    else:
        raise Exception("Failed to fetch ThingSpeak API key")

# Fetch Database API URL
def get_database_api_url():
    response = requests.get(DATABASE_API_URL)
    if response.status_code == 200:
        return response.json()["url"]
    else:
        raise Exception("Failed to fetch Database API URL")

# Fetch MQTT settings from catalog API
def get_mqtt_settings():
    response = requests.get(MQTT_SETTINGS_URL)
    if response.status_code == 200:
        settings = response.json()
        return settings['mqtt']['broker']['address'], settings['mqtt']['broker']['port'], settings['mqtt']['topic']
    else:
        raise Exception("Failed to fetch MQTT settings")

# Send data to ThingSpeak
def send_to_thingspeak(api_key, temperature, humidity):
    thingspeak_url = f'https://api.thingspeak.com/update'
    payload = {
        'api_key': api_key,
        'field1': temperature,
        'field2': humidity
    }
    response = requests.post(thingspeak_url, data=payload)
    if response.status_code == 200:
        print('Data sent to ThingSpeak successfully.')
    else:
        print('Failed to send data to ThingSpeak:', response.text)

# MQTT callback for when a message is received
def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    try:
        data = json.loads(msg.payload)
        project_ID = data.get("project_ID")
        room_ID = data.get("room_ID")
        temperature = data.get("temperature")
        humidity = data.get("humidity")

        # Check if data is for the specific project and room
        if project_ID == "proj1" and room_ID == "room1":
            print(f"Sending Temperature: {temperature}, Humidity: {humidity} to ThingSpeak")
            send_to_thingspeak(thingspeak_key, temperature, humidity)
        else:
            print("Data not for the targeted project and room.")

    except json.JSONDecodeError:
        print("Failed to decode MQTT message.")

def main():
    try:
        # Fetch settings from catalog API
        global thingspeak_key
        thingspeak_key = get_thingspeak_key()
        mqtt_broker, mqtt_port, mqtt_topic = get_mqtt_settings()

        # Set up MQTT client
        client = mqtt.Client()
        client.on_message = on_message

        # Connect to MQTT broker
        client.connect(mqtt_broker, mqtt_port, 60)

        # Subscribe to the MQTT topic
        client.subscribe(mqtt_topic)

        print(f"Subscribed to MQTT topic: {mqtt_topic}")

        # Start the MQTT client loop
        client.loop_forever()

    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
