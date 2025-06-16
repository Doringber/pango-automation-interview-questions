import sqlite3

class DatabaseHelper:
    def __init__(self, logger, db_name="data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cur = self.conn.cursor()
        self.create_tables()
        self.logger = logger

    def create_tables(self):
        # Create tables if they don't exist
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                city TEXT PRIMARY KEY,
                temperature_web REAL,
                temperature_api REAL,
                AVG_temperature REAL,
                feels_like_web REAL,
                feels_like_api REAL,
                AVG_feels_like REAL
            )''')

        self.conn.commit()

    def insert_weather_data(self, full_data):
        self.logger.info("Inserting weather data into the database")
        with self.conn:
            for item in full_data:
                self.cur.execute('''INSERT OR REPLACE INTO weather_data 
                    (city, temperature_web, temperature_api, AVG_temperature, 
                     feels_like_web, feels_like_api, AVG_feels_like) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                                 (item['city'], item.get('temperature_web'), item.get('temperature_api'),
                                  item.get('average_temperature'), item.get(
                                      'feels_like_web'),
                                     item.get('feels_like_api'), item.get('average_feels_like')))
            self.conn.commit()

    def get_weather_data_table(self, name):
        self.logger.info(f"Getting weather data table for: {name}")
        data = self.cur.execute(f"SELECT * FROM {name}")
        self.conn.commit()
        table_data = data.fetchall()
        return table_data


    def get_weather_data_by_city(self, city):
        self.logger.info(f"Getting weather data for city: {city}    ")
        row_data = self.cur.execute("SELECT * FROM weather_data WHERE city=?", (city,))
        self.conn.commit()
        data = row_data.fetchall()
        return data
    

        





