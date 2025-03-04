import loguru
import orjson as json

from fastapi import WebSocket
from pydantic_core import from_json

async def recv_data(pool: dict, websocket: WebSocket, logger: loguru.logger, account, users) -> None:
    """
    接收和发送数据
    :param pool: 连接池
    :param websocket: ws连接类
    :param logger: 日志类
    :param account: 账户模型
    :param users: 用户数据库
    :return:
    """
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_text()
            _account = account.model_validate(from_json(data, allow_partial=True))
            usrname = _account.username
            action = _account.action
            if action == "login":
                user = await users.get_or_create(username=usrname)
                verified = await user[0].verify(_account.password)
                if verified:
                    pool[usrname] = websocket
                    resp = await websocket.receive_text()
                    logger.debug(resp)
                else:
                    await websocket.send_text(str(json.dumps({'ret_code': 1})))
                logger.info(data)
        except Exception as e:
            logger.error(e)