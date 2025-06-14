#!/usr/bin/env python3
"""
Fixed Database Manager with proper connection handling
"""

import sqlite3
import json
import os
from typing import Optional, List, Tuple


class DatabaseManager:
    def __init__(self, db_name: str = "weather_data.db"):
        self.db_name = db_name
        self.conn = None
        self._connect()
        self.create_tables()

    def _connect(self):
        """Establish database connection"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_name)

    def _ensure_connection(self):
        """Ensure database connection is active"""
        try:
            # Test the connection
            self.conn.execute("SELECT 1")
        except (sqlite3.ProgrammingError, AttributeError):
            # Reconnect if connection is closed or None
            self._connect()

    def create_tables(self):
        """Create tables if they don't exist"""
        self._ensure_connection()
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    temperature_web REAL,
                    feels_like_web REAL,
                    temperature_api REAL,
                    feels_like_api REAL,
                    avg_temperature REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(city, timestamp)
                )
            ''')

    def insert_weather_data(self, city: str, temperature_web: float,
                            feels_like_web: float, temperature_api: float,
                            feels_like_api: float) -> bool:
        """Insert weather data for a city"""
        try:
            self._ensure_connection()
            avg_temperature = (temperature_web + temperature_api) / 2
            with self.conn:
                self.conn.execute('''
                    INSERT OR REPLACE INTO weather_data 
                    (city, temperature_web, feels_like_web, temperature_api, 
                     feels_like_api, avg_temperature)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (city, temperature_web, feels_like_web,
                      temperature_api, feels_like_api, avg_temperature))
            return True
        except sqlite3.Error as e:
            print(f"Database error for {city}: {e}")
            return False

    def get_weather_data(self, city: str) -> Optional[Tuple]:
        """Get weather data for a specific city"""
        self._ensure_connection()
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM weather_data 
            WHERE city = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        ''', (city,))
        return cursor.fetchone()

    def get_all_weather_data(self) -> List[Tuple]:
        """Get all weather data"""
        self._ensure_connection()
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM weather_data 
            ORDER BY timestamp DESC
        ''')
        return cursor.fetchall()

    def get_discrepancies(self, threshold: float) -> List[Tuple]:
        """Get cities with temperature discrepancies above threshold"""
        self._ensure_connection()
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT *, ABS(temperature_web - temperature_api) as discrepancy
            FROM weather_data 
            WHERE ABS(temperature_web - temperature_api) > ?
            ORDER BY discrepancy DESC
        ''', (threshold,))
        return cursor.fetchall()

    def get_statistics(self) -> dict:
        """Get summary statistics"""
        self._ensure_connection()
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT 
                AVG(ABS(temperature_web - temperature_api)) as mean_discrepancy,
                MAX(ABS(temperature_web - temperature_api)) as max_discrepancy,
                MIN(ABS(temperature_web - temperature_api)) as min_discrepancy,
                COUNT(*) as total_cities
            FROM weather_data
            WHERE temperature_web IS NOT NULL AND temperature_api IS NOT NULL
        ''')
        result = cursor.fetchone()
        return {
            'mean_discrepancy': result[0] or 0,
            'max_discrepancy': result[1] or 0,
            'min_discrepancy': result[2] or 0,
            'total_cities': result[3] or 0
        }

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def clear_data(self):
        """Clear all data (for testing)"""
        self._ensure_connection()
        with self.conn:
            self.conn.execute('DELETE FROM weather_data')


def load_temperature_data(db_path: str = "weather_data.db"):
    """Load temperature_data.json into database"""

    print("LOADING TEMPERATURE DATA")
    print("=" * 40)

    # Check if JSON file exists
    if not os.path.exists('temperature_data.json'):
        print("temperature_data.json not found!")
        return False

    # Initialize database with custom path
    db = DatabaseManager(db_path)

    try:
        # Load JSON data
        with open('temperature_data.json', 'r') as f:
            data = json.load(f)

        print(f"Found {len(data)} cities in JSON")

        # Clear existing data
        db.clear_data()
        print("Cleared existing data")

        loaded = 0
        skipped = 0

        # Process each city
        for city_data in data:
            city = city_data['city']
            api_data = city_data.get('api_data')
            web_data = city_data.get('web_data')

            if not api_data or not web_data:
                print(f"Skipping {city} - missing data")
                skipped += 1
                continue

            success = db.insert_weather_data(
                city=city,
                temperature_web=web_data['temperature'],
                feels_like_web=web_data['feels_like'],
                temperature_api=api_data['temperature'],
                feels_like_api=api_data['feels_like']
            )

            if success:
                discrepancy = abs(web_data['temperature'] - api_data['temperature'])
                print(f"{city}: {discrepancy:.1f}°C discrepancy")
                loaded += 1
            else:
                print(f"Failed: {city}")
                skipped += 1

        print(f"\nRESULTS:")
        print(f"Loaded: {loaded} cities")
        print(f"Skipped: {skipped} cities")

        if loaded > 0:
            stats = db.get_statistics()
            print(f"\nSTATISTICS:")
            print(f"   Total cities: {stats['total_cities']}")
            print(f"   Mean discrepancy: {stats['mean_discrepancy']:.2f}°C")
            print(f"   Max discrepancy: {stats['max_discrepancy']:.2f}°C")

        # DO NOT close the database here - let caller handle it
        # db.close()  # Commented out to fix the "closed database" error
        return loaded > 0

    except Exception as e:
        print(f"Error: {e}")
        db.close()
        return False