import sqlite3

class DatabaseHelper:
    def __init__(self, db_name="data.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        # Create tables if they don't exist
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                city TEXT PRIMARY KEY,
                temperature_web REAL,
                feels_like_web REAL,
                temperature_api REAL,
                feels_like_api REAL,
                avg_temperature REAL GENERATED ALWAYS AS (
                    (temperature_web + temperature_api) / 2.0
                ) STORED
            )''')

    def insert_weather_data(self, city, temperature_web, feels_like_web, temperature_api, feels_like_api):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                    INSERT INTO weather_data (city, temperature_web, feels_like_web, temperature_api, feels_like_api)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(city) DO UPDATE SET
                        temperature_web = excluded.temperature_web,
                        feels_like_web = excluded.feels_like_web,
                        temperature_api = excluded.temperature_api,
                        feels_like_api = excluded.feels_like_api
                    """, (city, temperature_web, feels_like_web,temperature_api,feels_like_api))
            self.conn.commit()


    def get_weather_data_of_city(self,city):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM weather_data WHERE city=?",city)
            row = cursor.fetchone()
            return row

    def get_weather_data_of_all_cities(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM weather_data")
            rows = cursor.fetchall()
            return rows