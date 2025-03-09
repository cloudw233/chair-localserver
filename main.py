import orjson as json

import loguru, uvicorn, logging, httpx

from fastapi import FastAPI, WebSocket
from pydantic_core import from_json
from contextlib import asynccontextmanager

from core.database.models import User
from core.pydantic_models import *
from core.utils.ws_connect import recv_data
from core.database import init_db

global httpx_client

sensor_pool = {}
client_pool = {}
monitor_pool = {}

logger = loguru.logger


@asynccontextmanager
async def httpx_c(app: FastAPI):
    httpx_client = httpx.AsyncClient()
    await init_db()
    yield
    await httpx_client.aclose()


app = FastAPI(lifespan=httpx_c)


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
                sensor_pool[usrname] = websocket
                logger.debug(_sensor)
                await websocket.send_text(str(json.dumps({'ret_code': 0})))
                for connection in [client_pool, monitor_pool]:
                    if connection.get(usrname):
                        await client_pool[usrname].send_text(data)

        except Exception as e:
            logger.error(e)


@app.websocket("/client")
async def client(websocket: WebSocket):
    await recv_data(client_pool, websocket, logger, Account, User)


@app.websocket("/monitor")
async def monitor(websocket: WebSocket):
    await recv_data(monitor_pool, websocket, logger, Account, User)


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
        del client_pool
        del sensor_pool
        del monitor_pool
