from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import sqlite3
from datetime import datetime

app = FastAPI()

DATABASE = "ESP_Database.db"

# Data models
class SensorData(BaseModel):
    project_ID: str
    room_ID: str
    temperature: float
    humidity: float
    timestamp: str
    datestamp: str

class DateRangeQuery(BaseModel):
    start_date: str
    end_date: str

def connect_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.post("/sensor_data/")
def add_sensor_data(data: SensorData):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO sensor_data (project_ID, room_ID, temperature, humidity, timestamp, datestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (data.project_ID, data.room_ID, data.temperature, data.humidity, data.timestamp, data.datestamp))
    conn.commit()
    conn.close()
    return {"message": "Sensor data added successfully"}

@app.get("/sensor_data/{project_ID}/{room_ID}/latest")
def get_latest_data(project_ID: str, room_ID: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sensor_data
        WHERE project_ID = ? AND room_ID = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (project_ID, room_ID))
    data = cursor.fetchone()
    conn.close()
    if data:
        return {
            "id": data[0],
            "project_ID": data[1],
            "room_ID": data[2],
            "temperature": data[3],
            "humidity": data[4],
            "timestamp": data[5],
            "datestamp": data[6]
        }
    else:
        raise HTTPException(status_code=404, detail="No data found")

@app.get("/sensor_data/{project_ID}/{room_ID}/range")
def get_data_range(project_ID: str, room_ID: str, start_date: str, end_date: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT temperature, humidity, timestamp, datestamp FROM sensor_data
        WHERE project_ID = ? AND room_ID = ? AND datestamp BETWEEN ? AND ?
    """, (project_ID, room_ID, start_date, end_date))
    data = cursor.fetchall()
    conn.close()
    
    # Return the data in a structured format
    response = []
    for row in data:
        response.append({
            "temperature": row[0],
            "humidity": row[1],
            "timestamp": row[2],
            "datestamp": row[3]
        })
    
    return {"data": response}


@app.get("/sensor_data/{project_ID}/{room_ID}/average")
def get_data_average(project_ID: str, room_ID: str, start_date: str, end_date: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(temperature), AVG(humidity) FROM sensor_data
        WHERE project_ID = ? AND room_ID = ? AND datestamp BETWEEN ? AND ?
    """, (project_ID, room_ID, start_date, end_date))
    data = cursor.fetchone()
    conn.close()
    if data:
        return {
            "average_temperature": data[0],
            "average_humidity": data[1]
        }
    else:
        raise HTTPException(status_code=404, detail="No data found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
