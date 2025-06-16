from pages.pages_object import ObjectPages
from .api_helpers import ApiHelper;

class WeatherDataExtractor():

    def __init__(self, driver, logger):
        self.driver = driver
        self.pages = ObjectPages(driver)
        self.logger = logger

    def get_weather_data_from_web(self, num):

        cities_elements = self.pages.weather_page.get_cities_list(num)
        self.logger.info(f"Total cities found: {len(cities_elements)}")
        weather_data = []
        for i in range(num):
            self.logger.info(f"Getting city index: {i + 1}")
            cities_elements = self.pages.weather_page.get_cities_list(num)

            if i >= len(cities_elements):
                break

            city_element = cities_elements[i]
            city_name = city_element.text.replace("*", "").strip()

            if not self.pages.weather_page.is_element_present_by_name(city_name):
                self.pages.weather_page.scroll_to_element_by_name(city_name)

            self.logger.info(f"Getting data from {city_name}:")
            self.pages.weather_page.click_element_by_name(city_name)
            weather_main_info = self.pages.weather_city_page.get_weather_main_info()
            weather_feels_like = self.pages.weather_city_page.get_weather_feels_like()
            weather_data.append({
                "city": city_name,
                "temperature_web_C": weather_main_info,
                "feels_like_web_C": weather_feels_like,
                "source": "web"
            })

            self.driver.back()
        return weather_data

    def get_weather_data_from_API(self,data):
        self.logger.info("Getting weather data from API")
        weather_data_api = []
        self.api_helper = ApiHelper()
        
        for i in range(len(data)):
            self.logger.info(f"Getting data from API for {data[i]['city']}")
            name = data[i]["city"]
            api_res = self.api_helper.get_current_weather(name)
            final_data = api_res.json()
            weather_data_api.append({
                "city": name,
                "temperature_api_C": final_data["main"]["temp"],
                "feels_like_api_C": final_data["main"]["feels_like"],
                "source": "api"
            })

        return weather_data_api
