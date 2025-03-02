import loguru, uvicorn

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from pydantic_core import from_json
from typing import Literal, Union

app = FastAPI()

connect_pool = {}
CONNECTIONS = 2

logger = loguru.logger()

class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(strict=True)


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
    seat: float | int


@app.websocket("/sensor")
async def sensor(websocket: WebSocket):
    await websocket.accept()
    connect_pool['sensor'] = websocket
    while True:
        data = await websocket.receive_text()
        logger.info(data)
        try:
            _sensor = Sensor.model_validate(from_json(data, allow_partial=True))
            logger.info(_sensor)
            if len(connect_pool.keys()) == CONNECTIONS:
                await connect_pool['client'].send_text(data)

        except Exception as e:
            print(e)


@app.websocket("/client")
async def client(websocket: WebSocket):
    await websocket.accept()
    connect_pool['client'] = websocket
    while True:
        data = await websocket.receive_text()
        try:
            logger.info(data)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    # 运行fastapi程序
    uvicorn.run(app="run:app", host="0.0.0.0", port=55433)