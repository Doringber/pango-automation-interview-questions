from pages.whaether_main_page import WeatherPage
from pages.whaether_city_page import WeatherCityPage

class ObjectPages:
    
        
    def __init__(self, driver):
        self.weather_page = WeatherPage(driver)
        self.weather_city_page = WeatherCityPage(driver)
