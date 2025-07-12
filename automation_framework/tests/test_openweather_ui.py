import pytest
from ..utilities.ui_helpers import UiHelper
from ..test_data.cities_with_countries import cities_with_countries_dict

@pytest.fixture(scope="module")
def ui():
    return UiHelper()

# Tests getting weather temp and feels like from ui using real city name
def test_get_weather_from_web(ui):
    city = 'Nairobi'
    temp_and_feels_like = ui.get_weather_from_web(city,cities_with_countries_dict.get(city))
    # assert that all values are not none
    assert all(temp_and_feels_like) , 'Temp or/and feels like list were not returned'


# Tests getting weather temp and feels like from ui using fake city name
def test_get_weather_unfound(ui):
    city = 'blah'
    # Ignore error from get_weather_from_web as it's meant to be thrown
    temp_and_feels_like = ui.get_weather_from_web(city,cities_with_countries_dict.get(city))
    # assert that all values are not none
    assert not all(temp_and_feels_like) , 'Temp or/and feels like list were returned'