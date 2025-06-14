#!/usr/bin/env python3
"""
Configuration for temperature analysis tests
"""

import os
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class TestConfig:
    """Configuration for temperature analysis tests"""

    # API Configuration
    OPENWEATHER_API_KEY: str = "f88d54cd8eddb5d1f23ff82a80b95fec"
    OPENWEATHER_BASE_URL: str = "https://api.openweathermap.org/data/2.5/weather"

    # Database Configuration
    TEST_DATABASE: str = "test_weather_data.db"
    PROD_DATABASE: str = "weather_data.db"

    # Test Cities (small set for faster testing)
    FEW_CITIES= {
        "New York": "usa/new-york",
        "London": "uk/london",
        "Tokyo": "japan/tokyo",

    }

    # All Cities (complete set for full testing)
    CITIES = {
        "New York": "usa/new-york",
        "London": "uk/london",
        "Tokyo": "japan/tokyo",
        "Sydney": "australia/sydney",
        "Paris": "france/paris",
        "Berlin": "germany/berlin",
        "Mumbai": "india/mumbai",
        "Toronto": "canada/toronto",
        "Moscow": "russia/moscow",
        "Cairo": "egypt/cairo",
        "Bangkok": "thailand/bangkok",
        "Rio de Janeiro": "brazil/rio-de-janeiro",
        "Mexico City": "mexico/mexico-city",
        "Lagos": "nigeria/lagos",
        "Istanbul": "turkey/istanbul",
        "Seoul": "south-korea/seoul",
        "Buenos Aires": "argentina/buenos-aires",
        "Jakarta": "indonesia/jakarta",
        "Johannesburg": "south-africa/johannesburg",
        "Dubai": "united-arab-emirates/dubai"
    }

    # Test Cities List
    TEST_CITIES = list(CITIES.keys())
    FEW_TEST_CITIES = list(FEW_CITIES.keys())

    # Analysis Configuration
    MAX_DISCREPANCY_ALLOWED: float = 10.0
    MIN_CITIES_REQUIRED: int = 15

    # Thresholds
    TEMPERATURE_THRESHOLD: float = 2.0
    MAX_DISCREPANCY: float = 10.0
    MIN_SUCCESS_RATE: float = 0.7

    # Performance Limits
    MAX_API_TIME: float = 10.0
    MAX_SCRAPE_TIME: float = 30.0

    # Reporting Configuration
    REPORTS_DIR: str = "data/outputs"
    GENERATE_REPORTS: bool = True
    REPORT_FORMATS: List[str] = None

    # Test Configuration
    TIMEOUT_SECONDS: int = 30
    RETRY_ATTEMPTS: int = 3
    PARALLEL_EXECUTION: bool = False

    # Scraping Configuration
    TIMEANDDATE_BASE_URL: str = "https://www.timeanddate.com/weather"
    REQUEST_TIMEOUT: int = 30

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Directories
    TEST_DATA_DIR: str = "test_data"
    TEST_REPORTS_DIR: str = "test_reports"

    @classmethod
    def get_test_cities(cls, fast_mode: bool = True) -> Dict[str, str]:
        """Get cities for testing"""
        return cls.FEW_CITIES if fast_mode else cls.CITIES

    @classmethod
    def get_database_path(cls, test_mode: bool = True) -> str:
        """Get database path"""
        return cls.TEST_DATABASE if test_mode else cls.PROD_DATABASE

    @classmethod
    def get_reports_dir(cls, test_mode: bool = True) -> str:
        """Get reports directory"""
        return cls.TEST_REPORTS_DIR if test_mode else cls.REPORTS_DIR