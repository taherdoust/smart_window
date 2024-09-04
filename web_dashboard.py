import streamlit as st
import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt

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

# Function to fetch projects and rooms from the catalog API
def get_projects_and_rooms():
    try:
        response = requests.get(f"{CATALOG_API_URL}/projects/")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch projects and rooms: {e}")
        return {}

# Fetch projects and their rooms dynamically
projects = get_projects_and_rooms()

# Select project and room
selected_project_viz = st.selectbox("Select Project for Visualization", list(projects.keys()), key="viz_project")

# Ensure the correct room options are presented based on the selected project
if selected_project_viz:
    rooms = list(projects[selected_project_viz]["rooms"].keys())
    selected_room_viz = st.selectbox("Select Room for Visualization", rooms, key="viz_room")
else:
    st.error("No projects available")

# Select date range
start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=7))
end_date = st.date_input("End Date", datetime.date.today())

# Function to fetch sensor data for the selected date range
def get_sensor_data(project_ID, room_ID, start_date, end_date):
    response = requests.get(
        f"{DATABASE_API_URL}/sensor_data/{project_ID}/{room_ID}/range",
        params={"start_date": start_date, "end_date": end_date}
    )
    if response.status_code == 200:
        return response.json()["data"]
    else:
        st.error(f"Failed to retrieve data: {response.status_code}")
        return []

# Show data when button is clicked
if st.button("Show Data"):
    if selected_project_viz and selected_room_viz:
        sensor_data = get_sensor_data(selected_project_viz, selected_room_viz, start_date.isoformat(), end_date.isoformat())

        # Check if data is retrieved and contains the required fields
        if sensor_data:
            # Convert the data into a DataFrame
            df = pd.DataFrame(sensor_data)
            
            # Ensure the DataFrame contains the required columns before plotting
            if 'temperature' in df.columns and 'humidity' in df.columns and 'timestamp' in df.columns:
                # Correctly combine datestamp and timestamp into a proper datetime object
                df['datetime'] = pd.to_datetime(df['datestamp'] + ' ' + df['timestamp'], format='%Y-%m-%d %H:%M:%S')

                # Set up the plot
                fig, ax1 = plt.subplots(figsize=(10, 5))

                # Plot temperature on the left y-axis
                ax1.plot(df['datetime'], df['temperature'], 'r-', label='Temperature (°C)')
                ax1.set_xlabel('Date and Time')
                ax1.set_ylabel('Temperature (°C)', color='r')
                ax1.tick_params(axis='y', labelcolor='r')

                # Create a second y-axis for humidity
                ax2 = ax1.twinx()
                ax2.plot(df['datetime'], df['humidity'], 'b-', label='Humidity (%)')
                ax2.set_ylabel('Humidity (%)', color='b')
                ax2.tick_params(axis='y', labelcolor='b')

                # Format x-axis to show both date and time
                ax1.xaxis.set_major_formatter(plt.FixedFormatter(df['datetime'].dt.strftime('%Y-%m-%d %H:%M')))

                # Add legends and title
                fig.tight_layout()
                st.pyplot(fig)

                # Display the data in a table format below the chart
                st.subheader("Sensor Data")
                st.dataframe(df[['datetime', 'temperature', 'humidity']])

            else:
                st.error("Data retrieved does not contain temperature or humidity fields.")
        else:
            st.write("No data available for the selected date range.")
    else:
        st.error("Please select a valid project and room.")