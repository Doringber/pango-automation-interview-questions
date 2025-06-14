# Weather Data Collection Framework

A Python automation framework that collects temperature data from multiple sources, stores it in a database, and generates analysis reports.

## Setup Instructions

### Prerequisites
```bash
pip install -r requirements.txt
```

### Configuration
1. Update API keys and settings in `config/test_config.py`
2. Configure test cities list in the same file
3. Ensure database permissions are set correctly

## How to Run the Project

### E2E runner
Running this file will collect temperature data from web scraping and APIs, store it in `weather_data.db`, and display any discrepancies.

```
python utilities/temperature_collector.py
```

For running tests, from test/location run:
```
pytest -v -s for regular run
```
This will run all tests in parallel, checking for coverage and reporting any missing lines. 6 stands for number of parallel processes

```
pytest -n 6 --cov=automation_framework --cov-report=term-missing 
```

Reports are in utilities/data/outputs



