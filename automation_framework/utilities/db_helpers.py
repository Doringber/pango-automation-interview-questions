import sqlite3

class DatabaseHelper:
    def __init__(self, db_name):
        self.conn = sqlite3.connect("../../" + db_name)
        self.create_tables()

    def create_tables(self):
        # Create tables if they don't exist
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                city TEXT PRIMARY KEY,
                temperature REAL,
                feels_like REAL,
                avg_temp REAL
            )''')

    def insert_weather_data(self, city, temperature, feels_like, avg_temp=0.0):
        sql = f'''
            INSERT INTO weather_data (city, temperature, feels_like, avg_temp) 
            values ('{city}', {temperature}, {feels_like}, {avg_temp});
        '''
        self.conn.execute(sql)
        self.conn.commit()

    def update_weather_data(self, city, temperature, feels_like, avg_temp=0.0):
        sql = f'''
            UPDATE weather_data
            SET temperature = {temperature}, feels_like = {feels_like}, avg_temp = {avg_temp}
            WHERE city = '{city}';
        '''
        self.conn.execute(sql)
        self.conn.commit()

    def get_weather_data(self, city):
        sql = f'''
            SELECT city, temperature, feels_like, avg_temp FROM weather_data WHERE city = '{city}'
        '''
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    def update_or_insert_weather_data(self, city, temperature, feels_like, avg_temp=0.0):
        if self.get_weather_data(city):
            self.update_weather_data(city, temperature, feels_like, avg_temp)
        else:
            self.insert_weather_data(city, temperature, feels_like, avg_temp)

    def get_city_with_highest_avg_temp(self):
        sql = f'''
            SELECT city, MAX(avg_temp) FROM weather_data GROUP BY city;
        '''
        cursor = self.conn.cursor()
        cursor.execute(sql)
        return cursor.fetchall()[0]