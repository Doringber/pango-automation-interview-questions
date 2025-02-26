from configparser import ConfigParser
import os

config = ConfigParser()
config.read("../config/config.ini")

API_KEY = config.get("API", "API_KEY")
BASE_URL = config.get("API", "BASE_URL")
DB_NAME = config.get("DB", "DB_NAME")