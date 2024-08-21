import streamlit as st
import requests
import json

catalog_api_url = "http://localhost:3002"

# Fetch the catalog data
def get_catalog_data():
    response = requests.get(f"{catalog_api_url}/projects/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch project data.")
        return []

# Fetch Telegram token
def get_telegram_token():
    response = requests.get(f"{catalog_api_url}/telegram_token/")
    if response.status_code == 200:
        return response.json()["token"]
    else:
        st.error("Failed to fetch Telegram token.")
        return ""

# Fetch ThingSpeak API key
def get_thingspeak_key():
    response = requests.get(f"{catalog_api_url}/thingspeak_key/")
    if response.status_code == 200:
        return response.json()["api_key"]
    else:
        st.error("Failed to fetch ThingSpeak API key.")
        return ""

# Update the catalog.json
def update_catalog(new_data):
    with open('catalog.json', 'r+') as file:
        catalog = json.load(file)
        catalog.update(new_data)
        file.seek(0)
        json.dump(catalog, file, indent=4)
        file.truncate()

# Admin Panel Section
st.sidebar.title("Admin Panel")

st.sidebar.subheader("View and Modify Tokens")
telegram_token = st.sidebar.text_input("Telegram Token", value=get_telegram_token())
thingspeak_key = st.sidebar.text_input("ThingSpeak API Key", value=get_thingspeak_key())

if st.sidebar.button("Update Tokens"):
    update_catalog({"telegram": {"token": telegram_token}, "thingspeak": {"api_key": thingspeak_key}})
    st.sidebar.success("Tokens updated successfully!")

# Main Dashboard Section
st.title("Smart Window Dashboard")

projects = get_catalog_data()
project_names = [project['projectName'] for project in projects]
selected_project = st.selectbox("Select Project", project_names)

if selected_project:
    selected_project_data = next(project for project in projects if project['projectName'] == selected_project)
    rooms = selected_project_data['rooms']
    room_ids = [room['room_ID'] for room in rooms]
    selected_room = st.selectbox("Select Room", room_ids)

    if selected_room:
        room_data = next(room for room in rooms if room['room_ID'] == selected_room)
        st.write(f"Temperature Threshold: {room_data['temperature_threshold']}")
        st.write(f"Humidity Threshold: {room_data['humidity_threshold']}")

        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")

        if st.button("Fetch Data"):
            # Fetch data for visualization
            st.write("Fetching data...")

# Add additional sections as needed...
