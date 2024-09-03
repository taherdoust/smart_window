import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from datetime import datetime

# Fetch the Telegram token from the catalog API
def fetch_telegram_token():
    response = requests.get("http://localhost:3002/telegram_token")
    if response.status_code == 200:
        return response.json()["token"]
    else:
        raise Exception("Failed to fetch Telegram token from catalog")

# Fetch the database API URL from the catalog API
def fetch_database_api_url():
    response = requests.get("http://localhost:3002/database_api_url/")
    if response.status_code == 200:
        return response.json()["url"]
    else:
        raise Exception("Failed to fetch database API URL from catalog")

# Global variable for the database API URL
DATABASE_API_URL = fetch_database_api_url()

# Command to start the bot
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Hello! Use /query command to get sensor data.\n'
        'Usage: /query <projectID> <roomID> <start_date> <end_date>\n'
        'Dates should be in YYYY-MM-DD format.'
    )

# Command to query average sensor data
def query(update: Update, context: CallbackContext):
    args = context.args
    if len(args) != 4:
        update.message.reply_text('Usage: /query <projectID> <roomID> <start_date> <end_date>')
        return

    project_ID = args[0]
    room_ID = args[1]
    start_date = args[2]
    end_date = args[3]

    # Validate date format
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        update.message.reply_text('Error: Invalid date format. Please use YYYY-MM-DD.')
        return

    # Construct the URL to request average data
    url = f"{DATABASE_API_URL}sensor_data/{project_ID}/{room_ID}/average?start_date={start_date}&end_date={end_date}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Extract average temperature and humidity
        avg_temp = data.get('average_temperature', 'N/A')
        avg_hum = data.get('average_humidity', 'N/A')

        # Respond with the average data
        message = (
            f"Average Temperature: {avg_temp} °C\n"
            f"Average Humidity: {avg_hum} %"
        )
        update.message.reply_text(message)

    except requests.exceptions.RequestException as e:
        update.message.reply_text(f"Error fetching data: {e}")

def main():
    # Fetch the Telegram token from the catalog API
    token = fetch_telegram_token()

    # Initialize the bot with the fetched token
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("query", query))

    # Start polling updates
    updater.start_polling()
    print("Bot is running...")  

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
