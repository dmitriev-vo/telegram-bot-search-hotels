"""Модуль содержит функции: запросы к базе данных hotel.com API"""

from config_data import config
import requests
import json
from typing import List, Tuple
import datetime


def search_cities(name_city: str) -> List:
    """Функция - запрос hotel API. По названию города выводит список городов, которые совпадают с названием города

    :parameters
    name_city: str

    :return
    cities: List -> ['name_city', 'name_city']
    """
    cities = []
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": f"{name_city}"}
    headers = {"X-RapidAPI-Key": config.RAPID_API_KEY, "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    if response.status_code == 200:
        data = json.loads(response.text)
        for sr in data["sr"]:
            if sr["type"] == "CITY":
                cities.append(sr['regionNames']['fullName'])
        return cities


def search_city_coordinates(name_city: str) -> Tuple:
    """Функция - запрос hotel API. По названию города выводит кортеж из координат города и его ID

    :parameters
    name_city: str

    :return
    coordinates: tuple = ((lat, long), ID), (lat, long), ID))
    """
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": f"{name_city}"}
    headers = {"X-RapidAPI-Key": config.RAPID_API_KEY, "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
    if response.status_code == 200:
        data = json.loads(response.text)
        for sr in data["sr"]:
            if sr["type"] == "CITY":
                return sr['coordinates'], sr["gaiaId"]


def search_hotels_in_city(coordinates: Tuple, command: str, date_in, date_out, count_hotels: int = 3) -> List:
    """Функция - запрос hotel API. По координатам и ID города ищет заданное количество отелей
    по умолчанию count_hotels = 3

    :parameters
    coordinates: tuple = ((lat, long), ID), (lat, long), ID))
    command: str
    date_in: class datatime
    date_out: class datatime
    count_hotels: int

    :return
    hotels: list = [(name, id, distance_to_centre, price),(name, id, distance_to_centre, price)]
    """
    date_in = str(date_in).split('-')
    date_out = str(date_out).split('-')
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    hotels = list()
    payload = {"destination": {"coordinates": {"latitude": float(coordinates[0]["lat"]),
                                               "longitude": float(coordinates[0]["long"])},
                               "regionId": coordinates[1]},
               "checkInDate": {"day": int(date_in[2]),
                               "month": int(date_in[1]),
                               "year": int(date_in[0])},
               "checkOutDate": {"day": int(date_out[2]),
                                "month": int(date_out[1]),
                                "year": int(date_out[0])},
               "rooms": [{"adults": 2, "children": [{"age": 5}, {"age": 7}]}],
               "resultsStartingIndex": 0,
               "resultsSize": 200,
               "sort": 'PRICE_LOW_TO_HIGH'}
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        for hotel in data["data"]["propertySearch"]["properties"]:
            hotels.append((hotel["name"],
                           hotel["id"],
                           hotel["destinationInfo"]["distanceFromDestination"]['value'],
                           hotel["price"]["lead"]['amount']))

    # Очистка от нулевых цен
    i = 0
    while i < len(hotels):
        if hotels[i][3] == 0:
            hotels.pop(i)
            i -= 1
        i += 1

    # Сортировка в зависимости от команды
    if command == 'lowprice':
        hotels_sorted = sorted(hotels, key=lambda elem: elem[3])
    elif command == 'highprice':
        hotels_sorted = sorted(hotels, key=lambda elem: elem[3], reverse=True)
    else:
        hotels_sorted = hotels
    return hotels_sorted[:count_hotels]


def search_hotels_in_city_with_price_and_distance(coordinates: Tuple,
                                                  command: str,
                                                  date_in,
                                                  date_out,
                                                  start_cost: int,
                                                  stop_cost: int,
                                                  start_distance: int,
                                                  stop_distance: int,
                                                  count_hotels: int = 3) -> List:
    """Функция - запрос hotel API. По координатам, ID города, диапазону дат, диапазону дистанции до центра ищет
    заданное количество отелей, по умолчанию count_hotels = 3

    :parameters
    coordinates: tuple = ((lat, long), ID), (lat, long), ID))
    command: str
    date_in: class datatime
    date_out: class datatime
    start_cost: int,
    stop_cost: int,
    start_distance: int,
    stop_distance: int,
    count_hotels: int

    :return
    hotels: list = [(name, id, distance_to_centre, price),(name, id, distance_to_centre, price)]
    """

    date_in = str(date_in).split('-')
    date_out = str(date_out).split('-')
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    hotels = list()
    payload = {"destination": {
        "coordinates": {"latitude": float(coordinates[0]["lat"]),
                        "longitude": float(coordinates[0]["long"])},
        "regionId": coordinates[1]},
               "checkInDate": {"day": int(date_in[2]),
                               "month": int(date_in[1]),
                               "year": int(date_in[0])},
               "checkOutDate": {"day": int(date_out[2]),
                                "month": int(date_out[1]),
                                "year": int(date_out[0])},
               "rooms": [{"adults": 2,
                          "children": [{"age": 5}, {"age": 7}]}],
               "resultsStartingIndex": 0,
               "resultsSize": 200,
               "sort": 'DISTANCE',
               "filters": {"price": {"max": stop_cost,
                                     "min": start_cost}}}
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    response = requests.request("POST", url, json=payload, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        for hotel in data["data"]["propertySearch"]["properties"]:
            hotels.append((hotel["name"],
                           hotel["id"],
                           hotel["destinationInfo"]["distanceFromDestination"]['value'],
                           hotel["price"]["lead"]['amount']))
    # Очистка от нулевых цен
    i = 0
    while i < len(hotels):
        if hotels[i][3] == 0:
            hotels.pop(i)
            i -= 1
        i += 1
    # Сортировка в зависимости от команды
    hotels_filter = filter(lambda hotel: start_distance <= hotel[2] <= stop_distance, hotels)
    hotels_sorted = sorted(hotels_filter, key=lambda elem: (elem[2] + elem[3]))

    return hotels_sorted[:count_hotels]


def find_photo(hotels: List, count_photo: int = 3) -> List:
    """Генератор списков с url фотограций отеля. Проходит по каждому отелю списка hotels и по ID отеля генерирует url
    адрес фотографий

    :parameters
    hotels: list = [(name, id, distance_to_centre), (name, id, distance_to_centre)]
    count_photo: int = 3

    :yield
    images_hotel: list = ('url_photo', 'url_photo')
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    images_hotels = [[] for _ in range(len(hotels))]
    for i_hotel, hotel in enumerate(hotels):
        images_hotel = []
        payload = {"propertyId": hotel[1]}
        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            for images in data["data"]["propertyInfo"]["propertyGallery"]["images"]:
                images_hotel.append(images["image"]["url"])
        images_hotels[i_hotel].append(images_hotel[:count_photo])
        yield images_hotel[:count_photo]


def find_details_hotel(hotels: List):
    """Функция - запрос hotel API. По каждому отелю списка hotels ищет название, описание и адрес.

    :parameters
    hotels: list = ((name, id, distance_to_centre), (name, id, distance_to_centre))

    :return
    details_hotels: List = [(name, description, address), (name, description, address)]
    """
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": config.RAPID_API_KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
    details_hotels = []
    for i_hotel, hotel in enumerate(hotels):
        payload = {"propertyId": hotel[1]}
        response = requests.request("POST", url, json=payload, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            name = data["data"]["propertyInfo"]["summary"]["name"]
            description = data["data"]["propertyInfo"]["summary"]["location"]["whatsAround"]["editorial"]["content"][0]
            address = data["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]
            details_hotels.append((name, description, address))
    return details_hotels
