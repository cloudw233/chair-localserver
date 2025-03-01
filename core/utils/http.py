import httpx

from typing import Any


async def url_post(url: str, data: dict|str, headers: dict = None) -> Any:
    """
    :param url: 链接
    :param data: 数据
    :param headers: 请求头
    :return: 返回请求结果
    """
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post(url, data=data, follow_redirects=True)
        return response

async def url_get(url: str, headers: dict|str = None) -> Any:
    """
    :param url: 链接
    :param headers: 请求头
    :return: 返回请求结果
    """
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url, follow_redirects=True)
        return response
