from utilities.json_helper import JsonCreator
from pages.pages_object import ObjectPages
from utilities.report_creator import ReportCreator
from utilities.logger_helper import setup_logger
logger = setup_logger()


def test_open_url_title(driver):
    pagesObjects = ObjectPages(driver)
    title = pagesObjects.weather_page.get_title_name()
    assert title == "World Temperatures — Weather Around The World"




