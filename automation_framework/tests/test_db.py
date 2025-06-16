def test_connection_by_get_table(db_helper):
    table_data = db_helper.get_weather_data_table("weather_data")
    assert table_data is not None
    assert len(table_data) > 0 
    assert len(table_data) == 20



def test_data_by_city(db_helper):
    city_data = db_helper.get_weather_data_by_city("Accra")
    print(city_data)
    assert city_data is not None
    assert city_data[0][0] == "Accra"
