def test_get_weather_200(api):
    city_data = api.get_current_weather("Madrid")
    assert city_data.status_code == 200


def test_get_weather_attributes(api):
    city_data = api.get_current_weather("Madrid")
    city_data_json = city_data.json()
    assert "temp" in city_data_json["main"]
    assert "feels_like" in city_data_json["main"]
