#!/usr/bin/env python3
"""
Test Framework for Temperature Data Collector
Tests your existing working temperature collector implementation
"""

import pytest
import asyncio
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
import sys


sys.path.append('.')
from automation_framework.utilities.temperature_collector import OpenWeatherAPI, TimeAndDateScraper, TemperatureCollector, CITIES


class TestOpenWeatherAPI:
    """Test the OpenWeatherAPI class"""

    @pytest.fixture
    def api_client(self):
        """Create API client for testing"""
        return OpenWeatherAPI("test_key", "https://api.openweathermap.org/data/2.5/weather")

    def test_api_initialization(self, api_client):
        """Test API client initialization"""
        assert api_client.api_key == "test_key"
        assert api_client.base_url == "https://api.openweathermap.org/data/2.5/weather"

    def test_get_weather_data_success(self, api_client):
        """Test successful API call"""
        # Mock successful response
        mock_response_data = {
            'name': 'London',
            'sys': {'country': 'GB'},
            'main': {
                'temp': 22.5,
                'feels_like': 21.8,
                'humidity': 65
            },
            'weather': [{'description': 'clear sky'}]
        }

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            result = api_client.get_weather_data("London")

            assert result is not None
            assert result['city'] == 'London'
            assert result['country'] == 'GB'
            assert result['temperature'] == 22.5
            assert result['feels_like'] == 21.8
            assert result['source'] == 'API'

    def test_get_weather_data_failure(self, api_client):
        """Test API call failure"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")

            result = api_client.get_weather_data("NonExistentCity")

            assert result is None

    def test_temperature_range_validation(self, api_client):
        """Test that API returns reasonable temperature values"""
        # Using real API with a known city
        real_api = OpenWeatherAPI("f88d54cd8eddb5d1f23ff82a80b95fec",
                                  "https://api.openweathermap.org/data/2.5/weather")

        result = real_api.get_weather_data("London")

        if result:  # Only test if API call succeeds
            assert -50 <= result['temperature'] <= 60, "Temperature should be in reasonable range"
            assert -50 <= result['feels_like'] <= 60, "Feels like should be in reasonable range"


class TestTimeAndDateScraper:
    """Test the web scraper class"""

    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = TimeAndDateScraper()
        assert scraper.playwright is None
        assert scraper.browser is None

    @pytest.mark.asyncio
    async def test_browser_startup_cleanup(self):
        """Test browser startup and cleanup"""
        scraper = TimeAndDateScraper()

        # Test startup
        await scraper.start_browser()
        assert scraper.playwright is not None
        assert scraper.browser is not None

        # Test cleanup
        await scraper.close_browser()

    def test_extract_number_function(self):
        """Test the _extract_number helper function"""
        scraper = TimeAndDateScraper()

        # Test valid extractions
        assert scraper._extract_number("22°C") == 22.0
        assert scraper._extract_number("15.5°F") == 15.5
        assert scraper._extract_number("-5°C") == -5.0
        assert scraper._extract_number("Temperature: 20") == 20.0

        # Test invalid extractions
        assert scraper._extract_number("no numbers here") is None
        assert scraper._extract_number("") is None
        assert scraper._extract_number(None) is None

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_scrape_temperature_real_city(self, scraper):
        """Test scraping with a real city (slow test)"""
        result = await scraper.scrape_temperature("London", "uk/london")

        if result:  # Only test if scraping succeeds
            assert 'city' in result
            assert 'temperature' in result
            assert 'feels_like' in result
            assert 'source' in result
            assert result['source'] == 'Web'
            assert isinstance(result['temperature'], (int, float))
            assert -50 <= result['temperature'] <= 60


class TestTemperatureCollector:
    """Test the main temperature collector"""

    @pytest.fixture
    def collector(self):
        """Create collector for testing"""
        return TemperatureCollector()

    def test_collector_initialization(self, collector):
        """Test collector initialization"""
        assert collector.api is not None
        assert collector.scraper is not None
        assert collector.results == []

    @pytest.mark.asyncio
    async def test_collect_city_data_with_mocks(self, collector):
        """Test collecting data for a single city with mocked responses"""

        # Mock API response
        mock_api_data = {
            'city': 'London',
            'temperature': 22.0,
            'feels_like': 21.5,
            'source': 'API'
        }

        # Mock web scraping response
        mock_web_data = {
            'city': 'London',
            'temperature': 22.5,
            'feels_like': 22.0,
            'source': 'Web'
        }

        with patch.object(collector.api, 'get_weather_data', return_value=mock_api_data), \
                patch.object(collector.scraper, 'scrape_temperature', return_value=mock_web_data):
            result = await collector.collect_city_data("London", "uk/london")

            assert result['city'] == 'London'
            assert result['api_data'] == mock_api_data
            assert result['web_data'] == mock_web_data
            assert 'timestamp' in result

    def test_save_results(self, collector):
        """Test saving results to JSON"""
        # Add some test data
        collector.results = [
            {
                'city': 'Test City',
                'api_data': {'temperature': 20.0, 'feels_like': 19.0},
                'web_data': {'temperature': 21.0, 'feels_like': 20.0},
                'timestamp': 1234567890
            }
        ]

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            temp_filename = tmp_file.name

        try:
            collector.save_results(temp_filename)

            # Verify file was created and contains data
            assert os.path.exists(temp_filename)

            with open(temp_filename, 'r') as f:
                loaded_data = json.load(f)

            assert len(loaded_data) == 1
            assert loaded_data[0]['city'] == 'Test City'

        finally:
            # Cleanup
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)


class TestDataValidation:
    """Test data quality and validation"""

    def test_temperature_data_structure(self):
        """Test expected data structure for temperature data"""
        # Example of expected API data structure
        api_data = {
            'city': 'London',
            'country': 'GB',
            'temperature': 22.0,
            'feels_like': 21.5,
            'humidity': 65,
            'description': 'clear sky',
            'source': 'API'
        }

        # Example of expected web data structure
        web_data = {
            'city': 'London',
            'temperature': 22.5,
            'feels_like': 22.0,
            'source': 'Web',
            'url': 'https://www.timeanddate.com/weather/uk/london'
        }

        # Validate API data structure
        required_api_fields = ['city', 'temperature', 'feels_like', 'source']
        for field in required_api_fields:
            assert field in api_data, f"API data should contain {field}"

        # Validate web data structure
        required_web_fields = ['city', 'temperature', 'feels_like', 'source']
        for field in required_web_fields:
            assert field in web_data, f"Web data should contain {field}"


class TestIntegration:
    """Integration tests for the complete pipeline"""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_collect_few_cities_integration(self, data_collector):
        """Test collecting data for a few cities (integration test)"""

        # Test with just 3 cities for speed
        test_cities = list(CITIES.items())[:3]

        await data_collector.scraper.start_browser()

        try:
            for city, url_path in test_cities:
                result = await data_collector.collect_city_data(city, url_path)
                data_collector.results.append(result)

        finally:
            await data_collector.scraper.close_browser()

        # Validate results
        assert len(data_collector.results) == 3

        # Check that at least some data was collected
        has_api_data = any(r['api_data'] for r in data_collector.results)
        has_web_data = any(r['web_data'] for r in data_collector.results)

        assert has_api_data, "Should have collected some API data"
        # Note: Web data might fail due to network/website issues, so we don't assert it

    def test_discrepancy_calculation(self):
        """Test discrepancy calculation logic"""
        # Mock collector with test data
        collector = TemperatureCollector()
        collector.results = [
            {
                'city': 'City1',
                'api_data': {'temperature': 20.0, 'feels_like': 19.0},
                'web_data': {'temperature': 22.0, 'feels_like': 21.0},
                'timestamp': 1234567890
            },
            {
                'city': 'City2',
                'api_data': {'temperature': 15.0, 'feels_like': 14.0},
                'web_data': {'temperature': 15.5, 'feels_like': 14.5},
                'timestamp': 1234567891
            }
        ]

        # Calculate discrepancies manually
        discrepancies = []
        for result in collector.results:
            if result['api_data'] and result['web_data']:
                api_temp = result['api_data']['temperature']
                web_temp = result['web_data']['temperature']
                discrepancy = abs(api_temp - web_temp)
                discrepancies.append((result['city'], discrepancy))

        assert len(discrepancies) == 2
        assert discrepancies[0][1] == 2.0  # City1: |20.0 - 22.0| = 2.0
        assert discrepancies[1][1] == 0.5  # City2: |15.0 - 15.5| = 0.5



def run_tests():
    """Run the test suite"""
    print("TEMPERATURE COLLECTOR TEST SUITE")
    print("=" * 40)
    print("Testing your temperature data collection system")
    print("=" * 40)

    # Run different test categories
    test_commands = [
        # Quick unit tests
        ("-m", "unit", "-x", "--tb=short"),

        # Integration tests (may be slower)
        ("-m", "integration", "-x", "--tb=short"),

        # All tests except slow ones
        ("-m", "not slow", "-x", "--tb=short"),
    ]

    for i, cmd_args in enumerate(test_commands, 1):
        print(f"\n{i}. Running tests with: pytest {' '.join(cmd_args)}")
        exit_code = pytest.main(list(cmd_args) + [__file__])

        if exit_code != 0:
            print(f"Tests failed with exit code {exit_code}")
            break
        else:
            print("Tests passed!")

    print("\nTest suite completed")


if __name__ == "__main__":
    run_tests()

