from utilities.base_page import BasePage
from selenium.webdriver.common.by import By
import re

class WeatherCityPage(BasePage):

    CITY_TEMP = (By.XPATH,"//*[@id='qlook']/div[2]")
    CITY_FEELS_LIKE = (By.XPATH,"//*[@id='wt-48']/tbody/tr[4]/td[1]")

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver
        
        
        
    def get_weather_main_info(self):
        
        data_city_weather = self.get_element_text(self.CITY_TEMP)
        temp =data_city_weather.split("°")[0].strip()
        if re.match(r"^-?\d+$", temp):
            return int(temp)
        else:
            print(f"Cannot extract the number temperature: {temp}")
        return

    def get_weather_feels_like(self):
        data_city_weather = self.get_element_text(self.CITY_FEELS_LIKE)
        temp = data_city_weather.split("°")[0].strip()
        if re.match(r"^-?\d+$", temp):
            return int(temp)
        else:
            print(f"Cannot extract the number temperature: {temp}")
        return