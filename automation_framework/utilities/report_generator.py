import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict

from automation_framework.config.test_config import TestConfig
from automation_framework.utilities.database_manager import DatabaseManager


class ReportGenerator:
    """Real report generator using your existing database"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or TestConfig.PROD_DATABASE
        self.reports_dir = TestConfig.REPORTS_DIR
        self.ensure_reports_directory()

    def ensure_reports_directory(self):
        """Create reports directory if it doesn't exist"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def get_data_from_database(self, threshold: float = None) -> Dict:
        """Get data from your existing database"""
        if threshold is None:
            threshold = TestConfig.TEMPERATURE_THRESHOLD

        # Import your existing DatabaseHelper
        sys.path.append('utilities')

        # Handle directory navigation for database
        original_dir = os.getcwd()
        if not os.path.basename(original_dir) == 'utilities':
            os.chdir('utilities')

        try:
            db = DatabaseManager(self.db_path)

            # Get statistics using your existing methods
            stats = db.get_statistics()

            # Get discrepancies above threshold using your existing methods
            discrepancies = db.get_discrepancies(threshold)

            # Get all data using your existing methods
            all_data = db.get_all_weather_data()


            return {
                'stats': stats,
                'discrepancies': discrepancies,
                'all_data': all_data,
                'threshold': threshold,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        finally:
            os.chdir(original_dir)

    def generate_discrepancy_csv_report(self, threshold: float = None) -> str:
        """Generate CSV report for cities above threshold"""

        data = self.get_data_from_database(threshold)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"discrepancies_above_{data['threshold']}C_{timestamp}.csv"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Header with metadata
            writer.writerow(['# Temperature Discrepancy Report'])
            writer.writerow(['# Generated:', data['timestamp']])
            writer.writerow(['# Threshold:', f"{data['threshold']}C"])
            writer.writerow(['# Cities above threshold:', len(data['discrepancies'])])
            writer.writerow([])

            # Data header
            writer.writerow(['City', 'Web_Temp_C', 'API_Temp_C', 'Discrepancy_C', 'Web_FeelsLike_C', 'API_FeelsLike_C',
                             'Avg_Temp_C'])

            # Data rows
            for row in data['discrepancies']:
                city = row[1]
                temp_web = row[2]
                feels_web = row[3]
                temp_api = row[4]
                feels_api = row[5]
                avg_temp = row[6]
                discrepancy = abs(temp_web - temp_api)

                writer.writerow([city, temp_web, temp_api, discrepancy, feels_web, feels_api, avg_temp])

        return filepath

    def generate_statistics_csv_report(self, threshold: float = None) -> str:
        """Generate CSV report for summary statistics"""

        data = self.get_data_from_database(threshold)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temperature_statistics_{timestamp}.csv"
        filepath = os.path.join(self.reports_dir, filename)

        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Report header
            writer.writerow(['Temperature Analysis Statistics Report'])
            writer.writerow(['Generated:', data['timestamp']])
            writer.writerow(['Threshold:', f"{data['threshold']}C"])
            writer.writerow([])

            # Statistics
            writer.writerow(['Metric', 'Value', 'Unit'])
            writer.writerow(['Total Cities Analyzed', data['stats']['total_cities'], 'count'])
            writer.writerow(['Mean Discrepancy', f"{data['stats']['mean_discrepancy']:.2f}", 'Celsius'])
            writer.writerow(['Maximum Discrepancy', f"{data['stats']['max_discrepancy']:.2f}", 'Celsius'])
            writer.writerow(['Minimum Discrepancy', f"{data['stats']['min_discrepancy']:.2f}", 'Celsius'])
            writer.writerow(['Cities Above Threshold', len(data['discrepancies']), 'count'])
            writer.writerow(
                ['Success Rate', f"{(data['stats']['total_cities'] / len(TestConfig.TEST_CITIES) * 100):.1f}", 'percent'])

        return filepath

    def generate_json_report(self, threshold: float = None) -> str:
        """Generate comprehensive JSON report"""

        data = self.get_data_from_database(threshold)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temperature_analysis_{timestamp}.json"
        filepath = os.path.join(self.reports_dir, filename)

        # Format data for JSON
        report = {
            "metadata": {
                "title": "Temperature Discrepancy Analysis Report",
                "generated": data['timestamp'],
                "threshold": data['threshold'],
                "total_cities_analyzed": data['stats']['total_cities'],
                "cities_above_threshold": len(data['discrepancies'])
            },
            "summary_statistics": data['stats'],
            "cities_with_discrepancies": []
        }

        # Add cities above threshold
        for row in data['discrepancies']:
            city_data = {
                "city": row[1],
                "temperature_web": row[2],
                "feels_like_web": row[3],
                "temperature_api": row[4],
                "feels_like_api": row[5],
                "avg_temperature": row[6],
                "discrepancy": abs(row[2] - row[4]),
                "timestamp": row[7]
            }
            report["cities_with_discrepancies"].append(city_data)

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        return filepath

    def generate_all_reports(self, threshold: float = None) -> Dict[str, str]:
        """Generate all report types"""

        reports = {}

        try:
            reports['discrepancy_csv'] = self.generate_discrepancy_csv_report(threshold)
            reports['statistics_csv'] = self.generate_statistics_csv_report(threshold)
            reports['json_report'] = self.generate_json_report(threshold)

            return reports

        except Exception as e:
            print(f"ERROR: generation failedv in generate report  - {e}")
            return {}

