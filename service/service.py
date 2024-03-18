import requests
from flask import abort


class YandexMapAPI:
    def __init__(self) -> None:
        self.urlGeoCode = 'http://geocode-maps.yandex.ru/1.x/'
        self.urlStaticMap = 'http://static-maps.yandex.ru/1.x/'
        self.paramsGeoCode = {
            'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
            'format': 'json'
        }
        self.paramsStaticMap = {
            'l': 'sat',
            'll': str(),
            'z': 12,
            'size': '400,400'
        }

    def __get_coord(self, findPlace: str) -> str:
        self.paramsGeoCode['geocode'] = findPlace
        with requests.get(self.urlGeoCode, params=self.paramsGeoCode) as response:
            return response.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']

    def link_photo_city(self, cityName: str) -> str:
        try:
            coordinates = self.__get_coord(findPlace=cityName)
            self.paramsStaticMap['ll'] = coordinates.replace(' ', ',')
            with requests.get(self.urlStaticMap, params=self.paramsStaticMap) as response:
                if response.status_code == 200:
                    return response.url
                abort(400)
        except IndexError:
            abort(400)
