import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# API URLs
CATALOG_API_URL = "http://localhost:3002"
DATABASE_API_URL = "http://localhost:3001"

st.title("Smart Window Dashboard")

# Section 1: Admin Panel
st.header("Admin Panel")
st.write("Registered Projects")
projects = requests.get(f"{CATALOG_API_URL}/projects/").json()
project_names = [proj['projectName'] for proj in projects]
st.write(project_names)

# Section 2: Add New Project
st.header("Add New Project")
new_project_name = st.text_input("New Project Name")
new_room_id = st.text_input("New Room ID")

if st.button("Add Project"):
    new_project = {
        "projectName": new_project_name,
        "rooms": [{"room_ID": new_room_id}]
    }
    response = requests.post(f"{CATALOG_API_URL}/projects/", json=new_project)
    st.success(response.json()["status"])

# Section 3: Modify Project Thresholds
st.header("Modify Project Thresholds")
selected_project = st.selectbox("Select Project", project_names)
selected_room = st.text_input("Room ID")

if selected_project and selected_room:
    thresholds = requests.get(f"{CATALOG_API_URL}/thresholds/{selected_project}/{selected_room}").json()
    new_temp_threshold = st.number_input("Temperature Threshold", value=thresholds["temperature_threshold"])
    new_hum_threshold = st.number_input("Humidity Threshold", value=thresholds["humidity_threshold"])

    if st.button("Update Thresholds"):
        update_data = {
            "temperature_threshold": new_temp_threshold,
            "humidity_threshold": new_hum_threshold
        }
        response = requests.put(f"{CATALOG_API_URL}/thresholds/{selected_project}/{selected_room}", json=update_data)
        st.success(response.json()["status"])

# Section 4: Data Visualization
st.header("Data Visualization")
selected_project_viz = st.selectbox("Select Project for Visualization", project_names, key="viz_project")
selected_room_viz = st.text_input("Room ID for Visualization", key="viz_room")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")

if st.button("Visualize Data"):
    sensor_data = requests.get(f"{DATABASE_API_URL}/sensor_data/{selected_project_viz}/{selected_room_viz}?start_date={start_date}&end_date={end_date}").json()
    if sensor_data:
        df = pd.DataFrame(sensor_data)

        # Temperature Visualization
        fig_temp = px.line(df, x="timestamp", y="temperature", title="Temperature Over Time")
        st.plotly_chart(fig_temp)

        # Humidity Visualization
        fig_hum = px.line(df, x="timestamp", y="humidity", title="Humidity Over Time")
        st.plotly_chart(fig_hum)
    else:
        st.error("No data available for the selected parameters.")
