from configparser import ConfigParser

import requests
from requests import Response


class ApiHelper:
    response: Response

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
    
    def get_current_weather_by_city_name(self, city):
        url = f"{self.base_url}?q={city}&appid={self.api_key}&units=metric"
        self.response = requests.get(url)
        return self.response

    def extract_current_temp_and_feels_like(self):
        response_body = self.response.json()
        temperature = response_body["main"]["temp"]
        feels_like = response_body["main"]["feels_like"]
        return temperature, feels_like

    def get_current_weather_by_city_id(self, city_id):
        url = f"{self.base_url}?id={city_id}&appid={self.api_key}&units=metric"
        self.response = requests.get(url)
        return self.response

    def calculate_average_temperature(self):
        response_body = self.response.json()
        min_temp = response_body["main"]["temp_min"]
        max_temp = response_body["main"]["temp_max"]
        return (min_temp + max_temp) / 2