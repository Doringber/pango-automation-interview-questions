import pytest

from automation_framework.tests import BASE_URL, API_KEY, DB_NAME
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DatabaseHelper


@pytest.fixture(scope="module")
def api():
    return ApiHelper(BASE_URL, API_KEY)

@pytest.fixture(scope="module")
def db():
    return DatabaseHelper(DB_NAME)

@pytest.mark.parametrize("city", [
    "Tbilisi",
    "Kyiv",
    "Jerusalem"
])
def test_current_weather_temperature_and_feels_like(city, api, db):
    response = api.get_current_weather_by_city_name(city)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    temperature, feels_like = api.extract_current_temp_and_feels_like()
    db.update_or_insert_weather_data(city, temperature, feels_like)
    db_weather = db.get_weather_data(city)[0]
    assert db_weather[1] == temperature, f"Expected temperature {db_weather[1]} but got {temperature}"
    assert db_weather[2] == feels_like, f"Expected feels like {db_weather[2]} but got {feels_like}"

@pytest.mark.parametrize("city, city_id", [
    ("Tbilisi", 611717),
    ("Kyiv", 703448),
    ("Jerusalem", 6554238)
])
def test_current_weather_average_temperature(city, city_id, api, db):
    response = api.get_current_weather_by_city_id(city_id)
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    temperature, feels_like = api.extract_current_temp_and_feels_like()
    avg_temp = api.calculate_average_temperature()
    db.update_or_insert_weather_data(city, temperature, feels_like, avg_temp)
    db_weather = db.get_weather_data(city)[0]
    assert db_weather[3] == avg_temp, f"Expected temperature {db_weather[3]} but got {avg_temp}"
    highest_avg_temp = db.get_city_with_highest_avg_temp()
    print(f"City with the highest average temperature {round(highest_avg_temp[1], 1)} is {highest_avg_temp[0]}.")