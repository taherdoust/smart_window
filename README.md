### **Smart Window Automation Platform**

**Description:**
The Smart Window Automation Platform is a modular and scalable system designed to automate the control of windows based on environmental conditions such as temperature and humidity. The platform collects sensor data from various rooms across different projects, compares the data against predefined thresholds, and sends commands to actuators to control the windows. The system also integrates with external services like ThingSpeak and Telegram to provide real-time monitoring and control.

### **Platform Modules and Their Tasks:**

1. **Catalog API (`catalog_api.py`)**:
   - **Task:** Serves as the central configuration manager for the platform. It provides access to MQTT settings, project details, thresholds, Telegram bot tokens, and ThingSpeak API keys. Other modules fetch their required configuration data from this API.
   - **Endpoint Examples:**
     - `/mqtt_settings/`: Provides MQTT broker details and topic information.
     - `/projects/`: Lists all registered projects and their details.
     - `/thresholds/{project_name}/{room_id}`: Provides the temperature and humidity thresholds for a specific room.
     - `/telegram_token/`: Retrieves the Telegram bot token.
     - `/thingspeak_key/`: Retrieves the ThingSpeak API key.

2. **Database API (`database_api.py`)**:
   - **Task:** Manages the storage and retrieval of sensor data. It provides RESTful endpoints to store new sensor data and retrieve historical data for analysis.
   - **Endpoint Examples:**
     - `POST /sensor_data/`: Stores new sensor data.
     - `GET /sensor_data/{project_ID}/{room_ID}/latest`: Retrieves the latest sensor data for a specific room.
     - `GET /sensor_data/{project_ID}/{room_ID}/range`: Retrieves sensor data within a specified date range.

3. **Data Receiver (`data_receiver.py`)**:
   - **Task:** Subscribes to the MQTT topic to receive sensor data from all rooms and projects. It processes the data, fetches the relevant thresholds from the Catalog API, and sends the processed data to the Database API for storage.

4. **Controller (`controller.py`)**:
   - **Task:** Periodically checks the latest sensor data from the Database API and compares it against the thresholds fetched from the Catalog API. If the temperature or humidity exceeds the thresholds, it sends control commands (e.g., open or close the window) to the actuator via MQTT.

5. **Sensor Module (`sensor.py` for each project/room)**:
   - **Task:** Collects real-time sensor data (temperature and humidity) and publishes it to the MQTT broker. In a virtual setup, this module simulates sensor readings with random values.
   - **Example:** `sens_proj2v_r1.py` for room1 of project2v.

6. **Actuator Module (`actuator.py` for each project/room)**:
   - **Task:** Listens for control commands via MQTT and controls the window actuator accordingly (e.g., opening or closing the window).
   - **Example:** `actuator_proj2v_r1.py` for room1 of project2v.

7. **ThingSpeak Integration (`thingspeak.py`)**:
   - **Task:** Retrieves sensor data from the Database API and sends it to ThingSpeak for visualization and monitoring. The ThingSpeak API key is fetched from the Catalog API.

8. **Telegram Bot (`telegram_bot.py`)**:
   - **Task:** Provides a Telegram bot interface for users to query sensor data. The bot token is fetched from the Catalog API, and users can request historical data for specific projects and rooms.

9. **Streamlit Dashboard (`streamlit_dashboard.py`)**:
   - **Task:** Provides a web-based user interface for administrators and users. The admin panel allows the management of Telegram tokens and ThingSpeak API keys. Users can view and modify thresholds, monitor sensor data, and visualize trends over time.

### **How to Run the Platform**

1. **Start the Catalog API**:
   - The Catalog API should be started first as it provides configuration details required by other modules.
   - **Command:** `python catalog_api.py`
   
2. **Start the Database API**:
   - The Database API manages data storage and retrieval. It must be running to store sensor data and retrieve it for analysis.
   - **Command:** `python database_api.py`

3. **Start the Data Receiver**:
   - The Data Receiver subscribes to the MQTT topic and forwards sensor data to the Database API.
   - **Command:** `python data_receiver.py`

4. **Start the Controller**:
   - The Controller monitors sensor data and sends control commands to the actuators.
   - **Command:** `python controller.py`

5. **Deploy Sensor and Actuator Modules**:
   - Deploy the sensor and actuator scripts for each room in each project.
   - **Sensor Example:** `python sens_proj2v_r1.py`
   - **Actuator Example:** `python actuator_proj2v_r1.py`

6. **Run ThingSpeak Integration** (Optional):
   - If ThingSpeak integration is required, run the ThingSpeak script to push data to ThingSpeak.
   - **Command:** `python thingspeak.py`

7. **Run the Telegram Bot** (Optional):
   - Start the Telegram bot to allow users to query sensor data through Telegram.
   - **Command:** `python telegram_bot.py`

8. **Launch the Streamlit Dashboard** (Optional):
   - The Streamlit dashboard provides a web interface for monitoring and managing the platform.
   - **Command:** `streamlit run streamlit_dashboard.py`

By following these steps, you will have the complete Smart Window Automation Platform running, allowing for automated control, real-time monitoring, and user interaction through various interfaces.