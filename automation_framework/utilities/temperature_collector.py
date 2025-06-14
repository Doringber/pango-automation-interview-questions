#!/usr/bin/env python3
"""
Fixed City Temperature Data Collector
Proper URLs and improved temperature detection for timeanddate.com
"""

import requests
import time
import asyncio
from playwright.async_api import async_playwright, Browser, Page
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, List
import json

from automation_framework.utilities.database_manager import load_temperature_data
from automation_framework.utilities.report_generator import ReportGenerator
from automation_framework.config.test_config import TestConfig

CITIES = TestConfig.CITIES
OPENWEATHER_API_KEY = TestConfig.OPENWEATHER_API_KEY
OPENWEATHER_BASE_URL = TestConfig.OPENWEATHER_BASE_URL


class OpenWeatherAPI:
    """Handle OpenWeatherMap API calls"""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    def get_weather_data(self, city: str) -> Optional[Dict]:
        """Get weather data from OpenWeatherMap API"""
        try:
            url = f"{self.base_url}?q={city}&appid={self.api_key}&units=metric"
            print(f"Fetching API data for {city}...")

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            result = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'source': 'API'
            }

            print(f"API SUCCESS: {result['temperature']}°C (feels {result['feels_like']}°C)")
            return result

        except Exception as e:
            print(f"API ERROR for {city}: {e}")
            return None


class TimeAndDateScraper:
    """Improved web scraping for timeanddate.com with better detection"""

    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start_browser(self):
        """Initialize browser with better settings"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            print("Browser started successfully")
        except Exception as e:
            print(f"Browser startup error: {e}")
            raise

    async def close_browser(self):
        """Safely close browser"""
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            print("Browser closed safely")
        except Exception as e:
            print(f"Browser cleanup warning: {e}")

    async def scrape_temperature(self, city: str, url_path: str) -> Optional[Dict]:
        """Scrape temperature data with improved detection"""
        page = None
        try:
            url = f"https://www.timeanddate.com/weather/{url_path}"
            print(f"Scraping {city} from {url}...")

            # Create new page
            page = await self.browser.new_page()

            # Set user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            # Navigate with shorter timeout
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)

            # Wait for content to load
            await page.wait_for_timeout(3000)

            # Try multiple detection methods
            temperature = await self._detect_temperature(page)
            feels_like = await self._detect_feels_like(page, temperature)

            if temperature is not None:
                result = {
                    'city': city,
                    'temperature': round(temperature, 1),
                    'feels_like': round(feels_like or temperature, 1),
                    'source': 'Web',
                    'url': url
                }
                print(f"WEB SUCCESS: {result['temperature']}°C (feels {result['feels_like']}°C)")
                return result
            else:
                print(f"No temperature found for {city}")
                return None

        except Exception as e:
            print(f"Web scraping error for {city}: {e}")
            return None
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass

    async def _detect_temperature(self, page: Page) -> Optional[float]:
        """Multiple methods to detect temperature"""

        # Method 1: Look for specific selectors
        selectors = [
            '[data-module="weather"] .temp',
            '.weather-info .temp',
            '.temperature',
            '.temp',
            'span.h2',
            '.cur-weather .h2',
            '#qlook .h2'
        ]

        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text:
                        temp = self._extract_number(text)
                        if temp and -50 <= temp <= 60:
                            print(f"Found temperature using selector {selector}: {temp}°C")
                            return temp
            except:
                continue

        # Method 2: Look in page text
        try:
            page_text = await page.text_content('body')
            if page_text:
                # Find temperature patterns
                patterns = [
                    r'(\d{1,2}(?:\.\d)?)\s*°[CF]',  # 20°C or 20.5°C
                    r'Temperature[:\s]*(\d{1,2}(?:\.\d)?)',  # Temperature: 20
                    r'(\d{1,2})\s*degrees?',  # 20 degrees
                ]

                for pattern in patterns:
                    matches = re.findall(pattern, page_text)
                    for match in matches:
                        try:
                            temp = float(match)
                            if -50 <= temp <= 60:
                                print(f"Found temperature in text: {temp}°C")
                                return temp
                        except ValueError:
                            continue
        except:
            pass

        # Method 3: Look for JSON data or structured data
        try:
            # Check for JSON-LD or other structured data
            json_scripts = await page.query_selector_all('script[type="application/ld+json"]')
            for script in json_scripts:
                content = await script.text_content()
                if content and 'temperature' in content.lower():
                    # Try to extract temperature from JSON
                    import json as json_lib
                    try:
                        data = json_lib.loads(content)
                        # Look for temperature in various JSON structures
                        temp = self._find_temp_in_json(data)
                        if temp:
                            print(f"Found temperature in JSON: {temp}°C")
                            return temp
                    except:
                        continue
        except:
            pass

        print("No temperature detected with any method")
        return None

    async def _detect_feels_like(self, page: Page, fallback_temp: Optional[float]) -> Optional[float]:
        """Improved feels like temperature detection"""
        try:
            # Method 1: Look for specific feels-like selectors first
            feels_like_selectors = [
                '[data-module="weather"] .feels-like',
                '.feels-like',
                '.real-feel',
                '.apparent-temp'
            ]

            for selector in feels_like_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        text = await element.text_content()
                        if text:
                            temp = self._extract_number(text)
                            if temp and -50 <= temp <= 60:
                                print(f"Found feels-like using selector {selector}: {temp}°C")
                                return temp
                except:
                    continue

            # Method 2: Look for feels-like in nearby text
            page_text = await page.text_content('body')
            if page_text:
                # More specific patterns that include context
                patterns = [
                    r'feels?\s*like[:\s]*(-?\d{1,2}(?:\.\d)?)\s*°?[CF]?',
                    r'real\s*feel[:\s]*(-?\d{1,2}(?:\.\d)?)\s*°?[CF]?',
                    r'apparent[:\s]*(-?\d{1,2}(?:\.\d)?)\s*°?[CF]?',
                    r'RealFeel®?\s*(-?\d{1,2}(?:\.\d)?)\s*°?[CF]?'
                ]

                text_lower = page_text.lower()
                for pattern in patterns:
                    matches = re.findall(pattern, text_lower)
                    for match in matches:
                        try:
                            temp = float(match)
                            if -50 <= temp <= 60:
                                # Additional validation: feels-like should be reasonably close to actual temp
                                if fallback_temp and abs(temp - fallback_temp) <= 15:  # Within 15°C seems reasonable
                                    print(f"Found feels-like in text: {temp}°C")
                                    return temp
                        except ValueError:
                            continue

            # Method 3: If no specific feels-like found, return fallback
            print(f"Using temperature as feels-like fallback: {fallback_temp}°C")
            return fallback_temp

        except Exception as e:
            print(f"Feels-like detection error: {e}")
            return fallback_temp

    def _extract_number(self, text: str) -> Optional[float]:
        """Extract number from text"""
        if not text:
            return None

        # Remove common non-numeric characters
        cleaned = re.sub(r'[°CFcf\s]', '', text)

        # Find number pattern
        match = re.search(r'(-?\d+(?:\.\d+)?)', cleaned)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return None

    def _find_temp_in_json(self, data) -> Optional[float]:
        """Recursively find temperature in JSON data"""
        if isinstance(data, dict):
            for key, value in data.items():
                if 'temp' in key.lower():
                    if isinstance(value, (int, float)):
                        return float(value)
                else:
                    result = self._find_temp_in_json(value)
                    if result:
                        return result
        elif isinstance(data, list):
            for item in data:
                result = self._find_temp_in_json(item)
                if result:
                    return result
        return None


class TemperatureCollector:
    """Main collector with improved error handling"""

    def __init__(self):
        self.api = OpenWeatherAPI(OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL)
        self.scraper = TimeAndDateScraper()
        self.results = []

    async def collect_city_data(self, city: str, url_path: str) -> Dict:
        """Collect data for a single city"""
        print(f"\n{'=' * 50}")
        print(f"Processing: {city}")
        print(f"{'=' * 50}")

        # Get API data
        api_data = self.api.get_weather_data(city)

        # Get web data
        web_data = await self.scraper.scrape_temperature(city, url_path)

        # Combine results
        result = {
            'city': city,
            'api_data': api_data,
            'web_data': web_data,
            'timestamp': time.time()
        }

        # Show summary
        if api_data and web_data:
            discrepancy = abs(api_data['temperature'] - web_data['temperature'])
            print(f"Summary for {city}:")
            print(f"   API: {api_data['temperature']}°C (feels {api_data['feels_like']}°C)")
            print(f"   Web: {web_data['temperature']}°C (feels {web_data['feels_like']}°C)")
            print(f"   Discrepancy: {discrepancy:.1f}°C")
        elif api_data:
            print(f"WARNING: Only API data available for {city}")
        elif web_data:
            print(f"WARNING: Only web data available for {city}")
        else:
            print(f"ERROR: No data collected for {city}")

        return result

    async def collect_all_cities(self):
        """Collect data for all cities with proper resource management"""
        print("City Temperature Data Collection")
        print(f"Cities to process: {len(CITIES)}")
        print(f"Cities: {', '.join(CITIES.keys())}")

        # Start browser once
        await self.scraper.start_browser()

        try:
            for i, (city, url_path) in enumerate(CITIES.items(), 1):
                print(f"\nProgress: {i}/{len(CITIES)}")

                result = await self.collect_city_data(city, url_path)
                self.results.append(result)

                # Add delay between requests
                if i < len(CITIES):
                    await asyncio.sleep(2)

        except Exception as e:
            print(f"Collection error: {e}")
        finally:
            # Always close browser
            await self.scraper.close_browser()

        return self.results

    def print_summary(self):
        """Print detailed summary"""
        print(f"\n{'=' * 60}")
        print("COLLECTION SUMMARY")
        print(f"{'=' * 60}")

        total_cities = len(self.results)
        successful_api = sum(1 for r in self.results if r['api_data'])
        successful_web = sum(1 for r in self.results if r['web_data'])
        both_sources = sum(1 for r in self.results if r['api_data'] and r['web_data'])

        print(f"Total cities processed: {total_cities}")
        print(f"Successful API calls: {successful_api}/{total_cities}")
        print(f"Successful web scraping: {successful_web}/{total_cities}")
        print(f"Both sources available: {both_sources}/{total_cities}")

        if both_sources > 0:
            print(f"\nTemperature Discrepancies:")
            discrepancies = []
            for result in self.results:
                if result['api_data'] and result['web_data']:
                    api_temp = result['api_data']['temperature']
                    web_temp = result['web_data']['temperature']
                    discrepancy = abs(api_temp - web_temp)
                    discrepancies.append((result['city'], discrepancy, api_temp, web_temp))
                    print(f"   {result['city']}: {discrepancy:.1f}°C (API: {api_temp}°C, Web: {web_temp}°C)")

            if discrepancies:
                avg_discrepancy = sum(d[1] for d in discrepancies) / len(discrepancies)
                max_discrepancy = max(discrepancies, key=lambda x: x[1])
                print(f"\nStatistics:")
                print(f"   Average discrepancy: {avg_discrepancy:.1f}°C")
                print(f"   Maximum discrepancy: {max_discrepancy[1]:.1f}°C ({max_discrepancy[0]})")

    def save_results(self, filename: str = "temperature_data.json"):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"Results saved to {filename}")


async def main():
    """Main function to run the complete temperature analysis workflow"""
    collector = TemperatureCollector()

    try:
        # 1. Collect data for all cities
        results = await collector.collect_all_cities()

        # 2. Print summary
        collector.print_summary()

        # 3. Save results to JSON
        collector.save_results()

        # 4. Load data into database
        db_success = load_temperature_data()

        # 5. Generate reports
        if db_success:
            print(f"\n{'=' * 60}")
            print("GENERATING REPORTS")
            print(f"{'=' * 60}")

            report_gen = ReportGenerator()
            threshold = 1.0  # Configurable threshold

            reports = report_gen.generate_all_reports(threshold)

            if reports:
                print(f"Reports generated successfully:")
                print(f"  Discrepancy CSV: {reports.get('discrepancy_csv', 'Failed')}")
                print(f"  Statistics CSV: {reports.get('statistics_csv', 'Failed')}")
                print(f"  JSON Report: {reports.get('json_report', 'Failed')}")
                print(f"  Reports directory: reports/")
            else:
                print("ERROR: Report generation failed")

        print(f"\n{'=' * 60}")
        print("WORKFLOW COMPLETED!")
        print(f"{'=' * 60}")
        print(f"Total results: {len(results)}")
        print(f"JSON file saved: {'Yes' if results else 'No'}")
        print(f"Database saved: {'Yes' if db_success else 'No'}")
        print(f"Reports generated: {'Yes' if reports else 'No'}")

        if db_success:
            print(f"\nFiles created:")
            print(f"  Database: weather_data.db")
            print(f"  JSON: temperature_data.json")
            print(f"  Reports: reports/ directory")

    except Exception as e:
        print(f"Error in main execution: {e}")


if __name__ == "__main__":
    asyncio.run(main())