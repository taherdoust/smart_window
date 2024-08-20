from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Database connection function
def connect_db():
    conn = sqlite3.connect('ESB_Database.db')
    return conn

# Pydantic model for the sensor data
class SensorData(BaseModel):
    project_ID: str
    room_ID: str
    timestamp: str
    datestamp: str
    temperature: float
    humidity: float

# API endpoint to save sensor data to the database
@app.post("/sensor_data/")
async def save_sensor_data(data: SensorData):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO sensor_data (project_ID, room_ID, timestamp, datestamp, temperature, humidity)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.project_ID, data.room_ID, data.timestamp, data.datestamp, 
            data.temperature, data.humidity
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to save data") from e
    finally:
        conn.close()

    return {"status": "success"}

# API endpoint to retrieve the latest sensor data
@app.get("/sensor_data/latest")
async def get_latest_sensor_data(project_ID: str, room_ID: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM sensor_data 
        WHERE project_ID = ? AND room_ID = ?
        ORDER BY timestamp DESC LIMIT 1
    ''', (project_ID, room_ID))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "project_ID": row[1],
            "room_ID": row[2],
            "timestamp": row[3],
            "datestamp": row[4],
            "temperature": row[5],
            "humidity": row[6]
        }
    else:
        raise HTTPException(status_code=404, detail="No data found")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
