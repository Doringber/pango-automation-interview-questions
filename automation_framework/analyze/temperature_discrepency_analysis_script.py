from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from automation_framework.utilities.db_helpers import DatabaseHelper
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.analyze import BASE_URL, API_KEY, DB_NAME
import pandas as pd

db = DatabaseHelper(DB_NAME)
api = ApiHelper(BASE_URL, API_KEY)

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.maximize_window()

driver.get("https://www.timeanddate.com/weather/")
tds: list[WebElement] = driver.find_elements(By.XPATH, "//table/tbody/tr/td")

def split_list(lst, chunk_size=4):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]

tds_split = list(split_list(tds, 4))

for td_4 in tds_split:
    city = td_4[0].text
    scraped_temp = td_4[3].text.split(" ")[0]
    api.get_current_weather_by_city_name(city)
    if api.response.status_code == 200:
        temperature, feels_like = api.extract_current_temp_and_feels_like()
        avg_temp = api.calculate_average_temperature()
        db.update_or_insert_weather_data(city, temperature, feels_like, avg_temp, scraped_temp)
    else:
        print(f"Cant get city temp with name {city}")

driver.quit()

# Generate report
temperature_data = db.get_all_city_temp()
df = pd.DataFrame(temperature_data, columns=["city_name", "temp_from_api", "temp_from_website"])
df["Temperature Difference"] = abs(df["temp_from_api"] - df["temp_from_website"])

# Define a threshold for significant differences (e.g., 2°C difference)
threshold = 2
significant_differences = df[df["Temperature Difference"] >= threshold]

# Display the report
print("\nSignificant Temperature Differences (Threshold >= 2°C):")
print(significant_differences.to_string(index=False))
