from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

# Load catalog data
def load_catalog():
    with open('catalog.json', 'r') as f:
        return json.load(f)

# API endpoint to get the platform name and MQTT settings
@app.get("/mqtt_settings/")
async def get_mqtt_settings():
    catalog = load_catalog()
    return {
        "PLATFORM_NAME": catalog["PLATFORM_NAME"],
        "mqtt": catalog["mqtt"]
    }

# API endpoint to get all projects
@app.get("/projects/")
async def get_projects():
    catalog = load_catalog()
    return catalog["projects"]

# API endpoint to get thresholds for a specific project and room
@app.get("/thresholds/{project_name}/{room_id}")
async def get_thresholds(project_name: str, room_id: str):
    catalog = load_catalog()
    for project in catalog["projects"]:
        if project["projectName"] == project_name:
            for room in project["rooms"]:
                if room["room_ID"] == room_id:
                    return {
                        "temperature_threshold": room.get("temperature_threshold", 28.0),
                        "humidity_threshold": room.get("humidity_threshold", 50.0)
                    }
    raise HTTPException(status_code=404, detail="Project or Room not found")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
