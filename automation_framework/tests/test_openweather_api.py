import pytest
from ..utilities.api_helpers import ApiHelper
from ..test_data.cities_with_countries import cities_with_countries_dict

@pytest.fixture(scope="module")
def api():
    return ApiHelper()

# Test status code for api request of getting a city's temp and feels like
def test_get_weather_data_status_code(api):
    city = 'Tokyo'
    assert api.get_current_weather(cities_with_countries_dict.get(city)).status_code == 200

# Test values of temp and feels like if retrieved
def test_get_weather_data_values_retrieved(api):
    city = 'Tokyo'
    temp_and_feels_like = api.get_weather_variables(city)
    assert all(temp_and_feels_like) , 'Temp or/and feels like list were not returned'


# Test get weather request with fake city name
def test_get_weather_data_of_fake_city_name(api):
    city = 'blah'
    assert api.get_current_weather(cities_with_countries_dict.get(city))
