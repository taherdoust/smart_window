import requests

# Fetch ThingSpeak API key from catalog API
catalog_api_url = "http://localhost:3002/thingspeak_key/"
key_response = requests.get(catalog_api_url).json()
THINGSPEAK_API_KEY = key_response["api_key"]

# Fetch API URL from catalog API
api_url = "http://localhost:3002/mqtt_settings/"
mqtt_settings = requests.get(api_url).json()
API_URL = f"http://{mqtt_settings['api']['host']}:{mqtt_settings['api']['port']}/"

class SensorDataManager:
    def __init__(self):
        self.api_url = API_URL

    def get_sensor_data(self, projectID, roomID, start_date, end_date):
        url = f"{self.api_url}GET/{projectID}/{roomID}/range?start_date={start_date}&end_date={end_date}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}. Failed to fetch sensor data.")
            return None

    def send_to_thingspeak(self, data):
        url = f'https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}'
        payload = {
            'field1': data.get('temperature', 'N/A'),
            'field2': data.get('humidity', 'N/A'),
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            if response.status_code == 200:
                print('Data sent to ThingSpeak successfully.')
            else:
                print('Failed to send data to ThingSpeak:', response.text)
        except requests.exceptions.RequestException as e:
            print(f'Error sending data to ThingSpeak: {e}')

    def process_and_send_data(self, projectID, roomID, start_date, end_date):
        data = self.get_sensor_data(projectID, roomID, start_date, end_date)
        if data:
            self.send_to_thingspeak(data)

if __name__ == '__main__':
    manager = SensorDataManager()
    projectID = input("Please enter the ProjectID: ")
    roomID = input("Please enter the RoomID: ")
    start_date = input("Please enter Start Date (YYYY-MM-DD): ")
    end_date = input("Please enter End Date (YYYY-MM-DD): ")
    manager.process_and_send_data(projectID, roomID, start_date, end_date)
