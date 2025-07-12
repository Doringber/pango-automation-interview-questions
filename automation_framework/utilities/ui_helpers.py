from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UiHelper:
    def get_weather_from_web(self, city, country):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 5)

        try:
            city_url = f"https://www.timeanddate.com/weather/{country}/{city}"
            driver.get(city_url)
            try:
                wait.until(EC.visibility_of_element_located((By.XPATH,f"//h1[contains(text(),'Weather in {city}')]")))
            except Exception as e:
                print(f"No city link found for {city}: {e}")
                return None, None

            # Extract temperature and "feels like" value
            temp = driver.find_element(By.CSS_SELECTOR, "#qlook .h2").text.replace("°C","").strip()
            feels_like_elem = driver.find_elements(By.XPATH, "//*[@id='qlook']/p[contains(text(),'Feels Like')]")[0]
            feels_like_line = feels_like_elem.text.split("\n")[0]
            feels_like_temp = feels_like_line.replace("Feels Like:","").replace("°C","").strip() if feels_like_elem else None

            return float(temp), float(feels_like_temp)

        except Exception as e:
            print(f"Error scraping {city}: {e}")
            return None, None

        finally:
            driver.quit()
