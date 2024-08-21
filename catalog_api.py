from fastapi import FastAPI, HTTPException
import json

app = FastAPI()

# Load catalog data
def load_catalog():
    with open('catalog.json', 'r') as f:
        return json.load(f)

@app.get("/mqtt_settings/")
async def get_mqtt_settings():
    catalog = load_catalog()
    return {
        "PLATFORM_NAME": catalog["PLATFORM_NAME"],
        "mqtt": catalog["mqtt"]
    }

@app.get("/projects/")
async def get_projects():
    catalog = load_catalog()
    return catalog["projects"]

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

@app.get("/telegram_token/")
async def get_telegram_token():
    catalog = load_catalog()
    return {"token": catalog["telegram"]["token"]}

@app.get("/thingspeak_key/")
async def get_thingspeak_key():
    catalog = load_catalog()
    return {"api_key": catalog["thingspeak"]["api_key"]}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
