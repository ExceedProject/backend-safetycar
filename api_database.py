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
    collection_co_heat.insert_one(query_notify_status)
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
    try:
        if safety_car.sensor1 == 1 or safety_car.sensor2 == 1 or safety_car.sensor3 == 1 or safety_car.sensor4 == 1 or safety_car.sensor5 == 1 or safety_car.sensor6 == 1 or safety_car.sensor7 == 1:
            if safety_car.heat >= 39 or safety_car.carbon >= 380:
                query_warning = {
                    "warning": 1,
                    "time": datetime.datetime.now()
                }
                collection_warning.insert_one(query_warning)
    except:
        query_warning = {
            "warning": 0,
            "time": datetime.datetime.now()
        }
        collection_warning.insert_one(query_warning)
    return {
        "result": "success"
    }