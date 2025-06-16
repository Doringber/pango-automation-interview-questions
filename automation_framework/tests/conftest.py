import pytest
from utilities.base_page import BasePage
from selenium import webdriver
from automation_framework.utilities.db_helpers import DatabaseHelper
from automation_framework.utilities.json_helper import JsonCreator
from automation_framework.utilities.api_helpers import ApiHelper



@pytest.fixture(scope="module")
def driver():
    driver = webdriver.Chrome()
    base_page = BasePage(driver)
    base_page.open_url("https://www.timeanddate.com/weather/")
    yield driver
    driver.quit()


@pytest.fixture(scope="module")
def db_helper():
    yield DatabaseHelper()


@pytest.fixture(scope="module")
def api():
    yield ApiHelper()