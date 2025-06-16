import json
from datetime import datetime
import os


class JsonCreator:


    def __init__(self, logger):
        self.logger = logger

    def log_temperatures(self, arr_data, name):
        with open(name, "w", encoding="utf-8") as f:
            json.dump(arr_data, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Data save to {name} successfully")

    def load_json_file(self, file_path,):
        if not os.path.exists(file_path):
            self.logger.warning(f"File {file_path} does not exist")
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                self.logger.info(f"Data loaded from {file_path} successfully")
                return data
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding JSON from {file_path}: {e}")
                return None

    def get_full_data_from_jsons(self, json_web, json_api):

        if not json_web or not json_api:
            self.logger.warning("Verify that the JSON file exists and is not empty")
            return []

        full_cities_data = []
        for web_item in json_web:
            city_name = web_item["city"]
            api_item = next(
                (item for item in json_api if item["city"] == city_name), None)
            if api_item:
                combined_item = {
                    "city": city_name,
                    "temperature_web": web_item["temperature_web_C"],
                    "temperature_api": api_item["temperature_api_C"],
                    "average_temperature": (web_item["temperature_web_C"] + api_item["temperature_api_C"]) / 2,
                    "feels_like_web": web_item["feels_like_web_C"],
                    "feels_like_api": api_item["feels_like_api_C"],
                    "average_feels_like": (web_item["feels_like_web_C"] + api_item["feels_like_api_C"]) / 2,
                    "source": "combined"
                }
                full_cities_data.append(combined_item)

        return full_cities_data
