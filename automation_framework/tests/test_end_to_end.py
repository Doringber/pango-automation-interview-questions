from utilities.data_helper import WeatherDataExtractor
from utilities.json_helper import JsonCreator
from utilities.report_creator import ReportCreator
from pages.pages_object import ObjectPages
from utilities.db_helpers import DatabaseHelper
from utilities.logger_helper import setup_logger
logger = setup_logger()



def test_end_to_end(driver):
    weather_data_extractor = WeatherDataExtractor(driver, logger)
    json_helper = JsonCreator(logger)
    report_creator = ReportCreator()
    db_helper = DatabaseHelper(logger)

    logger.info("Starting end-to-end test...")
# Step 1
    weather_data_web = weather_data_extractor.get_weather_data_from_web(20)
    json_helper.log_temperatures(
        weather_data_web, "data/weather_data_web.json")
# Step 2
    weather_data_api = weather_data_extractor.get_weather_data_from_API(
        weather_data_web)
    json_helper.log_temperatures(
        weather_data_api, "data/weather_data_api.json")
# Step 3
    web_data_json = json_helper.load_json_file("data/weather_data_web.json")
    api_data_json = json_helper.load_json_file("data/weather_data_api.json")
    full_data = json_helper.get_full_data_from_jsons(
        web_data_json, api_data_json)
    json_helper.log_temperatures(full_data, "data/full_weather_data.json")
    full_data_for_report = json_helper.load_json_file(
        "data/full_weather_data.json")
# Step 4
    db_helper.insert_weather_data(full_data)
# Step 5
    report_creator.generate_html_weather_report(full_data_for_report)

    logger.info("End-to-end test completed successfully.")
