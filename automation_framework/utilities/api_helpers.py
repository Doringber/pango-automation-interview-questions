import requests
import os

class ApiHelper:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    API_KEY = "f88d54cd8eddb5d1f23ff82a80b95fec"
    
    def get_current_weather(self, city):
        url = f"{self.BASE_URL}?q={city}&appid={self.API_KEY}"
        print(url)
        response = requests.get(url)
        print(response.json())
        return response
