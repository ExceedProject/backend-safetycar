from pymongo import MongoClient

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import datetime

client = MongoClient('mongodb://localhost', 27017)

db = client["safetycar"]

collection_notify = db["notify_status"]
collection_co_heat = db["carbon_heat"]
collection_sensor = db["sensor"]
collection_warning = db["warning"]

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/safety-car/status')
def get_status():
    heat_co_status = list(collection_notify.find())
    sensor_status = list(collection_sensor.find())
    query_status = {
        "heat_bool": heat_co_status[-1]["heat_bool"],
        "carbon_bool": heat_co_status[-1]["carbon_bool"],
        "sensor1": sensor_status[-1]["sensor1"],
        "sensor2": sensor_status[-1]["sensor2"],
        "sensor3": sensor_status[-1]["sensor3"],
        "sensor4": sensor_status[-1]["sensor4"],
        "sensor5": sensor_status[-1]["sensor5"],
        "sensor6": sensor_status[-1]["sensor6"],
        "sensor7": sensor_status[-1]["sensor7"]
    }
    return query_status


@app.get('/safety-car/graph')
def get_value_graph():
    """
    Returns:
        list of heat and carbon value
    """
    heat_co_value = list(collection_co_heat.find({}, {"_id": 0}))
    if len(heat_co_value) != 0:
        data = []
        for result in heat_co_value:
            data.append(result)
        return data
    else:
        raise HTTPException(404, f"Couldn't find heat and carbon value")


@app.get('/safety-car/warning')
def get_warning():
    list_warning = list(collection_warning.find({}, {"_id": 0}))
    if len(list_warning) != 0:
        data = []
        for result in list_warning:
            data.append(result)
        #  if warning time more than 30 second
        for i in range(len(data)):
            if abs(data[i-1]["time"] - data[i]["time"]) >= datetime.timedelta(seconds=30):
                return {
                    "warning": 1
                }
    else:
        raise HTTPException(404, f"Couldn't find warning in database")
