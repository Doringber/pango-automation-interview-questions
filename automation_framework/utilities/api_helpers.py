import requests
import os
from dotenv import load_dotenv
load_dotenv('config/.env')

class ApiHelper:
    BASE_URL = os.getenv("API_BASE_URL")
    API_KEY = os.getenv("API_KEY")

    def get_current_weather(self, city):
        url = f"{self.BASE_URL}?q={city}&appid={self.API_KEY}"
        print(url)
        response = requests.get(url)
        print(response.json())
        return response


