import pytest
import os
import tempfile
import sys
from pathlib import Path

import pytest_asyncio

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from automation_framework.config.test_config import TestConfig
from automation_framework.utilities.database_manager import DatabaseManager
from automation_framework.utilities.temperature_collector import TemperatureCollector, TimeAndDateScraper
from automation_framework.utilities.report_generator import ReportGenerator


@pytest.fixture(scope="session")
def config():
    """Configuration fixture"""
    return TestConfig()

@pytest_asyncio.fixture
async def scraper():
    scraper = TimeAndDateScraper()
    await scraper.start_browser()
    yield scraper
    await scraper.close_browser()

@pytest.fixture(scope="session")
def report_generator():
    """Report generator fixture using your existing database"""
    return ReportGenerator()

@pytest.fixture(scope="session")
def data_collector():
    """Data collector fixture"""
    return TemperatureCollector()

@pytest.fixture(scope="session")
def db_manager():
    """Data collector fixture"""
    return DatabaseManager(db_name="test_weather_data.db")


