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


class SafetyCar(BaseModel):
    heat: float
    carbon: float
    heat_bool: bool
    carbon_bool: bool
    sensor1: bool
    sensor2: bool
    sensor3: bool
    sensor4: bool
    sensor5: bool
    sensor6: bool
    sensor7: bool


@app.post('/safety-car')
def post_hardware(safety_car: SafetyCar):
    query_co_heat = {
        "carbon": safety_car.carbon,
        "heat": safety_car.heat,
        "time": datetime.datetime.now()
    }
    collection_co_heat.insert_one(query_co_heat)
    query_notify_status = {
        "carbon_bool": safety_car.carbon_bool,
        "heat_bool": safety_car.heat_bool,
        "time": datetime.datetime.now()
    }
    collection_notify.insert_one(query_notify_status)
    query_sensor = {
        "sensor1": safety_car.sensor1,
        "sensor2": safety_car.sensor2,
        "sensor3": safety_car.sensor3,
        "sensor4": safety_car.sensor4,
        "sensor5": safety_car.sensor5,
        "sensor6": safety_car.sensor6,
        "sensor7": safety_car.sensor7,
        "time": datetime.datetime.now()
    }
    collection_sensor.insert_one(query_sensor)
    # check human has move?
    if safety_car.sensor1 == 1 or safety_car.sensor2 == 1 or safety_car.sensor3 == 1 or safety_car.sensor4 == 1 or safety_car.sensor5 == 1 or safety_car.sensor6 == 1 or safety_car.sensor7 == 1:
        # check environment is dangerous?
        if safety_car.heat >= 39 or safety_car.carbon >= 380:
            query_warning = {
                "warning": 1,
                "time": datetime.datetime.now()
            }
            collection_warning.insert_one(query_warning)
    return {
        "result": "success"
    }


@app.get('/safety-car/status')
def get_status():
    heat_co_status = list(collection_notify.find())
    heat_co_status = sorted(heat_co_status, key=lambda d: d['time'])
    sensor_status = list(collection_sensor.find())
    sensor_status = sorted(sensor_status, key=lambda d: d['time'])
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
        if data[-1]["time"] + datetime.timedelta(minutes=3) < datetime.datetime.now():
            return {
                "warning": 0,
            }
        #  if warning time less than 30 second
        if (data[-1]["time"] - data[-2]["time"]) <= datetime.timedelta(seconds=30):
            return {
                "warning": 1
            }
        else:
            return {
                "warning": 0
            }
    else:
        raise HTTPException(404, f"Couldn't find warning in database")

