from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import requests
from datetime import datetime
import json

def load_catalog(file_path='catalog.json'):
    with open(file_path, 'r') as file:
        return json.load(file)

def get_token(catalog):
    return catalog.get("token")

def get_api_url(catalog):
    host = catalog["api"].get("host")
    port = catalog["api"].get("port")
    return f"http://{host}:{port}/"

class SensorBot:
    def __init__(self, catalog_file='catalog.json'):
        self.catalog = load_catalog(catalog_file)
        self.token = get_token(self.catalog)
        self.api_url = get_api_url(self.catalog)
        self.updater = Updater(self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def start(self, update: Update, context: CallbackContext):
        update.message.reply_text(
            'Hello! Use /query command to get sensor data.\n'
            'Please provide projectID, roomID, start_date, and end_date to get sensor readings.'
        )

    def query(self, update: Update, context: CallbackContext):
        args = context.args
        if len(args) < 4:
            update.message.reply_text('Usage: /query <projectID> <roomID> <start_date> <end_date>')
            return

        projectID = args[0]
        roomID = args[1]
        start_date = args[2]
        end_date = args[3]

        # Check date format
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            update.message.reply_text('Error: Invalid date format. Please use YYYY-MM-DD.')
            return

        result = self.query_sensors_api(projectID, roomID, start_date, end_date)

        if not result:
            update.message.reply_text('Error fetching data. Please try again later.')
            return

        # Extract temperature and humidity from the result
        avg_temp = result.get('avg_temp', 'N/A')
        avg_hum = result.get('avg_hum', 'N/A')

        message = (
            f"Average Temperature: {avg_temp}\n"
            f"Average Humidity: {avg_hum}\n"
        )
        update.message.reply_text(message)

    def query_sensors_api(self, projectID, roomID, start_date=None, end_date=None):
        url = f"{self.api_url}GET/{projectID}/{roomID}/range?start_date={start_date}&end_date={end_date}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}. Failed to fetch sensor data.")
            return None

    def run(self):
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('query', self.query))
        self.updater.start_polling()
        self.updater.idle()

if __name__ == '__main__':
    bot = SensorBot('catalog.json')
    bot.run()



