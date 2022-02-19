from pymongo import MongoClient

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import datetime
import logging

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
    heat_bool: int
    carbon_bool: int
    sensor1: int
    sensor2: int
    sensor3: int
    sensor4: int
    sensor5: int
    sensor6: int
    sensor7: int
    sensor8: int
    sensor9: int
    sensor10: int
    sensor11: int
    sensor12: int
    sensor13: int
    sensor14: int


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.post('/safety-car')
def post_hardware(safety_car: SafetyCar):
    query_co_heat = {
        "carbon": float(safety_car.carbon),
        "heat": float(safety_car.heat),
        "time": datetime.datetime.now()
    }
    collection_co_heat.insert_one(query_co_heat)
    query_notify_status = {
        "carbon_bool": int(safety_car.carbon_bool),
        "heat_bool": int(safety_car.heat_bool),
        "time": datetime.datetime.now()
    }
    collection_notify.insert_one(query_notify_status)
    query_sensor = {
        "sensor1": int(safety_car.sensor1),
        "sensor2": int(safety_car.sensor2),
        "sensor3": int(safety_car.sensor3),
        "sensor4": int(safety_car.sensor4),
        "sensor5": int(safety_car.sensor5),
        "sensor6": int(safety_car.sensor6),
        "sensor7": int(safety_car.sensor7),
        "sensor8": int(safety_car.sensor8),
        "sensor9": int(safety_car.sensor9),
        "sensor10": int(safety_car.sensor10),
        "sensor11": int(safety_car.sensor11),
        "sensor12": int(safety_car.sensor12),
        "sensor13": int(safety_car.sensor13),
        "sensor14": int(safety_car.sensor14),
        "time": datetime.datetime.now()
    }
    collection_sensor.insert_one(query_sensor)
    # check human has move?
    if int(safety_car.sensor1) == 1 or int(safety_car.sensor2) == 1 or int(safety_car.sensor3) == 1 or \
            int(safety_car.sensor4) == 1 or int(safety_car.sensor5) == 1 or int(safety_car.sensor6) == 1 \
            or int(safety_car.sensor7) == 1 or int(safety_car.sensor8) == 1\
            or int(safety_car.sensor9) == 1 or int(safety_car.sensor10) == 1 or int(safety_car.sensor11) == 1 or \
            int(safety_car.sensor12) == 1 or int(safety_car.sensor13) == 1 or int(safety_car.sensor14) == 1:
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
        "sensor7": sensor_status[-1]["sensor7"],
        "sensor8": sensor_status[-1]["sensor8"],
        "sensor9": sensor_status[-1]["sensor9"],
        "sensor10": sensor_status[-1]["sensor10"],
        "sensor11": sensor_status[-1]["sensor11"],
        "sensor12": sensor_status[-1]["sensor12"],
        "sensor13": sensor_status[-1]["sensor13"],
        "sensor14": sensor_status[-1]["sensor14"]
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

