-- Create the Sensor Data table
CREATE TABLE IF NOT EXISTS sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    room_id TEXT NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL,
    timestamp TEXT NOT NULL,
    datestamp TEXT NOT NULL
);

-- Insert sample data if needed
INSERT INTO sensor_data (project_id, room_id, temperature, humidity, timestamp, datestamp)
VALUES ('proj1', 'room1', 27.5, 50.1, '17:16:41.307904', '2024-09-03');

-- For retrieving average temperature and humidity over a date range
CREATE VIEW IF NOT EXISTS average_sensor_data AS
SELECT project_id, room_id, AVG(temperature) AS avg_temperature, AVG(humidity) AS avg_humidity
FROM sensor_data
WHERE datestamp BETWEEN '2024-09-01' AND '2024-09-03'
GROUP BY project_id, room_id;