import requests

class ApiHelper:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    API_KEY = "f88d54cd8eddb5d1f23ff82a80b95fec"
    
    def get_current_weather(self, city):
        url = f"{self.BASE_URL}?q={city}&appid={self.API_KEY}"
        print(url)
        response = requests.get(url)
        print(response)
        return response

    def get_weather_variables(self,city):
        try:
            response = ApiHelper().get_current_weather(city).json()
            temp_api = float(response['main']['temp'])
            feels_like_api = float(response['main']['feels_like'])
        except Exception as e:
            print(f"No temp found for {city}: {e}")
            return None, None

        return temp_api, feels_like_api
