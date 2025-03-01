from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal, Union

app = FastAPI()

class Account(BaseModel):
    username: str
    password: Union[str, int] = None
    action: Literal["login", "register", "data"]
    face_recognition_data: str = None

class Sensor(Account):
    DHT_T: str = None
    DHT_H: str = None
    power: str = None
    urgent_button: str = None
    tilt: bool = None
    heart_data: int = None
    smoke: dict = None
    seat: str = None


class Weather(BaseModel):
    city: str

class UI(BaseModel):
    seat: str