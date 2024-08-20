import requests
import json

def load_catalog(file_path='catalog.json'):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_token(catalog):
    return catalog.get("api_key")

def get_api_url(catalog):
    host = catalog["api"].get("host")
    port = catalog["api"].get("port")
    return f"http://{host}:{port}/"

class SensorDataManager:
    def __init__(self, catalog_file='catalog.json'):
        self.catalog = load_catalog(catalog_file)
        self.token = get_token(self.catalog)
        self.api_url = get_api_url(self.catalog)

    def get_sensor_data(self, projectID, roomID, start_date, end_date):
        url = f"{self.api_url}GET/{projectID}/{roomID}/range?start_date={start_date}&end_date={end_date}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}. Failed to fetch sensor data.")
            return None

    def send_to_thingspeak(self, data):
        url = f'https://api.thingspeak.com/update?api_key={self.token}'
        payload = {
            'field1': data.get('intemp', 'N/A'),  # Default to 'N/A' if key doesn't exist
            'field2': data.get('inhum', 'N/A'),
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

    manager = SensorDataManager('catalog.json')
    projectID = input("Please enter the ProjectID: ")
    roomID = input("Please enter the RoomID: ")
    start_date = input("Please enter StartData (YYYY-MM-DD): ")
    end_date = input("Please enter EndData (YYYY-MM-DD): ")
    manager.process_and_send_data(projectID, roomID, start_date, end_date)


