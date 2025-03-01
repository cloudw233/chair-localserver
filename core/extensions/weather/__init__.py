import orjson as json

from urllib.parse import quote
from core.utils.http import url_get
from core.config import config

key = config("qweather_api_key")

header = "X-QW-Api-Key: " + key

class QWeather:
    def __init__(self, city):
        self.__city_id = None
        self.__lon = None
        self.__lat = None
        self.city = city


    async def find_city(self):
        """
        通过城市名称查找城市ID，
        参见 https://dev.qweather.com/docs/api/geo/city-lookup/
        :return: 城市id
        """
        url = quote(f"https://geoapi.qweather.com/v2/city/lookup?location={self.city}")
        response = json.loads(await url_get(url, header))
        if response.get('code', 404) == "200":
            self.__city_id = response.get('location')[0].get('id')
            self.__lat = response.get('location')[0].get('lat')
            self.__lon = response.get('location')[0].get('lon')
        else:
            raise ValueError(f"City {self.city} not found.")
        return response.get('location')[0].get('id')


    async def get_7days(self, city_id=None):
        """
        获取未来7天的天气预报，
        参见 https://dev.qweather.com/docs/api/weather/weather-daily-forecast/
        :param city_id: 城市ID
        :return: 返回的7日天气
        """
        if city_id is None:
            await self.find_city()
        url = quote(f"https://devapi.qweather.com/v7/weather/7d?location={self.__city_id}")
        response = json.loads(await url_get(url,header))
        if response.get('code', 404) == "200":
            return response.get('daily')
        else:
            raise ValueError(f"City {self.city} not found.")

    async def get_index(self, city_id=None):
        """
        获取生活指数，
        参见 https://dev.qweather.com/docs/api/indices/indices1d/
        :param city_id: 城市ID
        :return: 返回的生活指数
        """
        if city_id is None:
            await self.find_city()
        url = quote(f"https://devapi.qweather.com/v7/indices/1d?type=0&location={self.__city_id}")
        response = json.loads(await url_get(url,header))
        if response.get('code', 404) == "200":
            return response.get('daily')
        else:
            raise ValueError(f"City {self.city} not found.")

    async def get_aqi(self, city_id="none"):
        """
        获取空气质量，
        参见 https://dev.qweather.com/docs/api/air/air-now/
        :param city_id: 城市ID
        :return: 返回的空气质量
        """
        if city_id is None:
            await self.find_city()
        url = quote(f"https://api.qweather.com/airquality/v1/current/{self.__lat}/{self.__lon}")
        response = json.loads(await url_get(url,header))
        if response.get('code', 404) == "200":
            return response.get('now')
        else:
            raise ValueError(f"City {self.city} not found.")
