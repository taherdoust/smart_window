import streamlit as st
import requests
import pandas as pd
import datetime

# Fetch Catalog API URLs
CATALOG_API_URL = "http://localhost:3002"

def fetch_api_urls():
    mqtt_settings = requests.get(f"{CATALOG_API_URL}/mqtt_settings").json()
    database_api_url = requests.get(f"{CATALOG_API_URL}/database_api_url").json()
    return mqtt_settings, database_api_url

# Fetching the API URLs
_, DATABASE_API = fetch_api_urls()
DATABASE_API_URL = DATABASE_API["url"]

# Fetching data from Catalog API
def get_projects():
    response = requests.get(f"{CATALOG_API_URL}/projects/")
    return response.json()

def add_project(project_id, room_ids, temp_threshold, hum_threshold):
    data = {
        "project_id": project_id,
        "room_ids": room_ids,
        "temperature_threshold": temp_threshold,
        "humidity_threshold": hum_threshold
    }
    response = requests.post(f"{CATALOG_API_URL}/add_project/", json=data)
    return response

def update_thresholds(project_id, room_id, temp_threshold, hum_threshold):
    data = {
        "temperature_threshold": temp_threshold,
        "humidity_threshold": hum_threshold
    }
    response = requests.put(f"{CATALOG_API_URL}/thresholds/{project_id}/{room_id}", json=data)
    return response

def get_thresholds(project_id, room_id):
    response = requests.get(f"{CATALOG_API_URL}/thresholds/{project_id}/{room_id}")
    return response.json()

def get_sensor_data(project_id, room_id, start_date, end_date):
    url = f"{DATABASE_API_URL}/sensor_data/{project_id}/{room_id}/range?start_date={start_date}&end_date={end_date}"
    response = requests.get(url)
    return response.json()

# Streamlit UI
st.title("Smart Window Automation Platform Dashboard")

# Section 1: Admin Panel - Display All Projects
st.header("Admin Panel - Display All Projects")
projects = get_projects()
st.write("Registered Projects:")
st.json(projects)

# Section 2: Add New Project
st.header("Add New Project")
new_project_id = st.text_input("Enter Project ID:")
new_room_ids = st.text_input("Enter Room IDs (comma separated):").split(',')
new_temp_threshold = st.number_input("Enter Temperature Threshold:", value=25.0)
new_hum_threshold = st.number_input("Enter Humidity Threshold:", value=50.0)

if st.button("Add Project"):
    response = add_project(new_project_id, new_room_ids, new_temp_threshold, new_hum_threshold)
    if response.status_code == 200:
        st.success("Project added successfully!")
    else:
        st.error(f"Failed to add project: {response.text}")

# Section 3: Set Telegram and ThingSpeak Tokens
st.header("Set Telegram and ThingSpeak Tokens")
telegram_token = st.text_input("Enter Telegram Token:")
thingspeak_key = st.text_input("Enter ThingSpeak API Key:")

if st.button("Update Tokens"):
    requests.post(f"{CATALOG_API_URL}/update_telegram_token/", json={"token": telegram_token})
    requests.post(f"{CATALOG_API_URL}/update_thingspeak_key/", json={"api_key": thingspeak_key})
    st.success("Tokens updated successfully!")

# Section 4: View and Modify Thresholds
st.header("View and Modify Thresholds")
selected_project = st.selectbox("Select Project", list(projects.keys()))
rooms = projects[selected_project]["rooms"]
selected_room = st.selectbox("Select Room", list(rooms.keys()))
current_thresholds = get_thresholds(selected_project, selected_room)

st.write(f"Current Thresholds for {selected_project} - {selected_room}:")
st.json(current_thresholds)

updated_temp_threshold = st.number_input("Update Temperature Threshold:", value=current_thresholds["temperature_threshold"])
updated_hum_threshold = st.number_input("Update Humidity Threshold:", value=current_thresholds["humidity_threshold"])

if st.button("Update Thresholds"):
    response = update_thresholds(selected_project, selected_room, updated_temp_threshold, updated_hum_threshold)
    if response.status_code == 200:
        st.success("Thresholds updated successfully!")
    else:
        st.error(f"Failed to update thresholds: {response.text}")

# Section 5: Data Visualization
st.header("Data Visualization")

selected_project_viz = st.selectbox(
    "Select Project for Visualization", list(projects.keys()), key="viz_project"
)


rooms_viz = projects[selected_project_viz]["rooms"]
selected_room_viz = st.selectbox(
    "Select Room for Visualization", list(rooms_viz.keys()), key="viz_room"
)

start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=7))
end_date = st.date_input("End Date", datetime.date.today())

if st.button("Show Data"):
    sensor_data = get_sensor_data(selected_project_viz, selected_room_viz, start_date, end_date)
    
    if sensor_data:
        df = pd.DataFrame(sensor_data)

        if {'temperature', 'humidity'}.issubset(df.columns):
            st.line_chart(df[['temperature', 'humidity']])
        else:
            st.write("Data retrieved does not contain temperature or humidity fields.")
    else:
        st.write("No data available for the selected date range.")