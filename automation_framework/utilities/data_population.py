
from ..test_data.cities_with_countries import cities_with_countries_dict
from ..utilities.ui_helpers import UiHelper
from ..utilities.api_helpers import ApiHelper
from ..utilities.db_helpers import DatabaseHelper
from ..utilities.report import generate_report

def populate_db():
    db = DatabaseHelper()
    for city,country in cities_with_countries_dict.items():
        try:
            temp_web, feels_like_web = UiHelper().get_weather_from_web(city,country)
            temp_api, feels_like_api = ApiHelper().get_weather_variables(city)
            db.insert_weather_data(city, temp_web, feels_like_web, temp_api, feels_like_api)
        except Exception as e:
            print(f"Error processing {city}: {e}")
    generate_report()
