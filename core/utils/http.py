import httpx

from typing import Any


async def url_post(client: httpx.AsyncClient, url: str, data: dict|str, headers: dict = None) -> Any:
    """
    :param client: httpx.AsyncClient
    :param url: 链接
    :param data: 数据
    :param headers: 请求头
    :return: 返回请求结果
    """
    response = await client.post(url, data=data, headers=headers, follow_redirects=True)
    return response

async def url_get(client: httpx.AsyncClient, url: str, headers: dict|str = None) -> Any:
    """
    :param client: httpx.AsyncClient
    :param url: 链接
    :param headers: 请求头
    :return: 返回请求结果
    """
    response = await client.get(url, headers=headers, follow_redirects=True)
    return response
