# **Smart Window Automation Platform**

## **Description:**

The Smart Window Automation Platform is a modular and scalable system designed to automate the control of windows based on environmental conditions such as temperature and humidity. The platform collects sensor data from various rooms across different projects, compares the data against predefined thresholds, and sends commands to actuators to control the windows. The system also integrates with external services like ThingSpeak and Telegram to provide real-time monitoring and control.

## **Platform Modules and Their Tasks:**

### **Catalog API (`catalog_api.py`):**

- **Task:** Serves as the central configuration manager for the platform. It provides access to MQTT settings, project details, thresholds, Telegram bot tokens, and ThingSpeak API keys. Other modules fetch their required configuration data from this API.
- **Endpoints and Functions:**
  - **`/mqtt_settings/`**: Provides MQTT broker details and topic information.
  - **`/projects/`**: Lists all registered projects and their details.
  - **`/thresholds/{project_name}/{room_id}`**: Provides the temperature and humidity thresholds for a specific room.
  - **`/add_project/`**: Adds a new project with room details to the catalog.
  - **`/update_thresholds/{project_ID}/{room_ID}`**: Updates temperature and humidity thresholds for a specific room.
  - **`/update_tokens/`**: Updates Telegram bot token and ThingSpeak API key.

### **Database API (`database_api.py`):**

- **Task:** Manages the storage and retrieval of sensor data. It provides RESTful endpoints to store new sensor data and retrieve historical data for analysis.
- **Endpoints and Functions:**
  - **`POST /sensor_data/`**: Stores new sensor data in the database.
  - **`GET /sensor_data/{project_ID}/{room_ID}/latest`**: Retrieves the latest sensor data for a specific room.
  - **`GET /sensor_data/{project_ID}/{room_ID}/range`**: Retrieves sensor data within a specified date range.
  - **`GET /sensor_data/{project_ID}/{room_ID}/average`**: Retrieves the average temperature and humidity over a specified date range.

### **Data Receiver (`data_receiver.py`):**

- **Task:** Subscribes to the MQTT topic to receive sensor data from all rooms and projects. It processes the data, fetches the relevant thresholds from the Catalog API, and sends the processed data to the Database API for storage.
- **Functions:**
  - **MQTT Subscription**: Connects to the MQTT broker and subscribes to the specified topic to receive sensor data.
  - **Data Processing**: Parses received data, checks against the thresholds, and forwards it to the Database API.

### **Controller (`controller.py`):**

- **Task:** Periodically checks the latest sensor data from the Database API and compares it against the thresholds fetched from the Catalog API. If the temperature or humidity exceeds the thresholds, it sends control commands (e.g., open or close the window) to the actuator via MQTT.
- **Functions:**
  - **Check Conditions and Control**: Compares latest sensor readings with thresholds and decides whether to send open/close commands to actuators.
  - **MQTT Command Publisher**: Publishes control commands to the actuators based on the comparison results.

### **Sensor Module (`sensor_display.ino` and `virtual_sensor.py`):**

- **Task:** Collects real-time sensor data (temperature and humidity) and publishes it to the MQTT broker.
- **Functions:**
  - **`sensor_display.ino`**: Collects data from sensors like DHT11, displays it on an LCD, and publishes to MQTT.
  - **`virtual_sensor.py`**: Simulates sensor readings with random values and publishes them to MQTT.

### **Actuator Module (`actuator.ino` and `virtual_actuator.py`):**

- **Task:** Listens for control commands via MQTT and controls the window actuator accordingly (e.g., opening or closing the window).
- **Functions:**
  - **`actuator.ino`**: Controls a servo motor to open/close the window based on received MQTT commands.
  - **`virtual_actuator.py`**: Simulates the actuator's response and prints the status.

### **ThingSpeak Integration (`thingspeak.py`):**

- **Task:** Retrieves sensor data from the Database API and sends it to ThingSpeak for visualization and monitoring.
- **Functions:**
  - **Fetch and Send Data**: Retrieves data from the Database API and posts it to ThingSpeak using the API key from the Catalog API.

### **Telegram Bot (`telegram_bot.py`):**

- **Task:** Provides a Telegram bot interface for users to query average sensor data.
- **Functions:**
  - **Commands**:
    - **`/start`**: Provides an introduction to using the bot.
    - **`/query`**: Allows users to request average temperature and humidity for specific projects and rooms over a date range.

### **Streamlit Dashboard (`web_dashboard.py`):**

- **Task:** Provides a web-based user interface for administrators and users. The admin panel allows the management of Telegram tokens and ThingSpeak API keys. Users can view and modify thresholds, monitor sensor data, and visualize trends over time.
- **Features:**
  - **Admin Panel**: View and modify project settings, thresholds, and external service tokens.
  - **Threshold Management**: Allows users to view and modify temperature and humidity thresholds for each room.
  - **Data Visualization**: Displays historical temperature and humidity data using line charts.

## **How to Run the Platform**

### **Step 1: Start the Catalog API**
- **Purpose**: Provides configuration details required by other modules.
- **Command**:
  ```bash
  python catalog_api.py
  ```

### **Step 2: Start the Database API**
- **Purpose**: Manages data storage and retrieval.
- **Command**:
  ```bash
  python database_api.py
  ```

### **Step 3: Start the Data Receiver**
- **Purpose**: Subscribes to the MQTT topic and forwards sensor data to the Database API.
- **Command**:
  ```bash
  python data_receiver.py
  ```

### **Step 4: Start the Controller**
- **Purpose**: Monitors sensor data and sends control commands to the actuators.
- **Command**:
  ```bash
  python controller.py
  ```

### **Step 5: Deploy Sensor and Actuator Modules**
#### **For Physical Setup:**
- **Deploy `sensor_display.ino`** on the ESP32 that handles sensor data collection and display.
- **Deploy `actuator.ino`** on the ESP32 that handles window control using a servo motor.

#### **For Virtual Setup:**
- **Deploy Virtual Sensor and Actuator Scripts**:
  - **Sensor**:
    ```bash
    python virtual_sensor.py
    ```
  - **Actuator**:
    ```bash
    python virtual_actuator.py
    ```

### **Step 6: Run ThingSpeak Integration (Optional)**
- **Purpose**: Push data to ThingSpeak for visualization.
- **Command**:
  ```bash
  python thingspeak.py
  ```

### **Step 7: Run the Telegram Bot (Optional)**
- **Purpose**: Provides a Telegram bot interface for querying sensor data.
- **Command**:
  ```bash
  python telegram_bot.py
  ```

### **Step 8: Launch the Streamlit Dashboard (Optional)**
- **Purpose**: Provides a web interface for monitoring and managing the platform.
- **Command**:
  ```bash
  streamlit run web_dashboard.py
  ```

By following these steps, you will have the complete Smart Window Automation Platform running, allowing for automated control, real-time monitoring, and user interaction through various interfaces. The platform's modular design facilitates easy maintenance, scalability, and integration with additional sensors or actuators as needed.