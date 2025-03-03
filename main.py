import orjson as json

import loguru, uvicorn, logging

from fastapi import FastAPI, WebSocket
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from pydantic_core import from_json
from typing import Literal, Union

app = FastAPI()

connect_pool = {}
CONNECTIONS = 2

logger = loguru.logger


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
    while True:
        data = await websocket.receive_text()
        logger.debug(data)
        try:
            _sensor = Sensor.model_validate(from_json(data, allow_partial=True))
            usrname = _sensor.username
            if _sensor.action == 'data':
                connect_pool[usrname] = websocket
                logger.debug(_sensor)
                await websocket.send_text(str(json.dumps({'ret_code': 0})))
                if connect_pool.get(usrname + '_client'):
                    await connect_pool['client'].send_text(data)

        except Exception as e:
            logger.error(e)


@app.websocket("/client")
async def client(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        try:
            logger.info(data)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    try:
        class InterceptHandler(logging.Handler):
            def emit(self, record):
                logger_opt = logger.opt(depth=6, exception=record.exc_info)
                logger_opt.log(record.levelno, record.getMessage())


        def init_logger():
            LOGGER_NAMES = ("uvicorn", "uvicorn.access",)
            for logger_name in LOGGER_NAMES:
                logging_logger = logging.getLogger(logger_name)
                logging_logger.handlers = [InterceptHandler()]


        config = uvicorn.Config(app, host="0.0.0.0", port=int(55433), access_log=True, workers=1)
        server = uvicorn.Server(config)
        init_logger()
        server.run()
    except KeyboardInterrupt:
        pass
