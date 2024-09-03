from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

app = FastAPI()

# Load catalog data
def load_catalog():
    with open('catalog.json', 'r') as file:
        return json.load(file)

# Save catalog data
def save_catalog(catalog):
    with open('catalog.json', 'w') as file:
        json.dump(catalog, file, indent=4)

# Data models
class Project(BaseModel):
    project_ID: str
    rooms: dict

class Thresholds(BaseModel):
    temperature_threshold: float
    humidity_threshold: float

class TokenUpdate(BaseModel):
    telegram_token: str = None
    thingspeak_api_key: str = None

@app.get("/mqtt_settings/")
def get_mqtt_settings():
    catalog = load_catalog()
    return {
        "PLATFORM_NAME": catalog.get("PLATFORM_NAME"),
        "mqtt": catalog.get("mqtt")
    }

# Fetch DATABASE API URL
@app.get("/database_api_url/")
def get_database_api_url():
    catalog = load_catalog()
    api_settings = catalog.get("api", {})
    host = api_settings.get("host", "localhost")
    port = api_settings.get("port", 3001)
    return {"url": f"http://{host}:{port}/"}

@app.get("/projects/")
def get_projects():
    catalog = load_catalog()
    return catalog["projects"]

@app.get("/thresholds/{project_ID}/{room_ID}")
def get_thresholds(project_ID: str, room_ID: str):
    catalog = load_catalog()
    try:
        return catalog["projects"][project_ID]["rooms"][room_ID]
    except KeyError:
        raise HTTPException(status_code=404, detail="Project or room not found")

@app.post("/projects/")
def add_project(project: Project):
    catalog = load_catalog()
    if project.project_ID in catalog["projects"]:
        raise HTTPException(status_code=400, detail="Project already exists")
    catalog["projects"][project.project_ID] = {"rooms": project.rooms}
    save_catalog(catalog)
    return {"message": "Project added successfully"}

@app.put("/thresholds/{project_ID}/{room_ID}")
def update_thresholds(project_ID: str, room_ID: str, thresholds: Thresholds):
    catalog = load_catalog()
    try:
        catalog["projects"][project_ID]["rooms"][room_ID]["temperature_threshold"] = thresholds.temperature_threshold
        catalog["projects"][project_ID]["rooms"][room_ID]["humidity_threshold"] = thresholds.humidity_threshold
        save_catalog(catalog)
        return {"message": "Thresholds updated successfully"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Project or room not found")

@app.put("/update_tokens/")
def update_tokens(tokens: TokenUpdate):
    catalog = load_catalog()
    if tokens.telegram_token:
        catalog["telegram"]["token"] = tokens.telegram_token
    if tokens.thingspeak_api_key:
        catalog["thingspeak"]["api_key"] = tokens.thingspeak_api_key
    save_catalog(catalog)
    return {"message": "Tokens updated successfully"}

@app.get("/telegram_token/")
def get_telegram_token():
    catalog = load_catalog()
    telegram_token = catalog.get("telegram", {}).get("token")
    if not telegram_token:
        raise HTTPException(status_code=404, detail="Telegram token not found")
    return {"token": telegram_token}

@app.get("/thingspeak_key/proj1/room1")
def get_thingspeak_key():
    catalog = load_catalog()
    thingspeak_key = catalog.get("thingspeak", {}).get("api_key")
    if not thingspeak_key:
        raise HTTPException(status_code=404, detail="ThingSpeak API key not found")
    return {"api_key": thingspeak_key}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
