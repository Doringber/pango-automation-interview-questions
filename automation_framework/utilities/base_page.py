from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains



class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.waitDriver = WebDriverWait(driver, 10)

    def open_url(self, url):
        self.driver.get(url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)

    def is_element_present(self, el):
        try:
            self.waitDriver.until(EC.element_to_be_clickable(el))
            return True
        except Exception as e:
            print(f"Element not found: {e}")
            return False

    def click_element(self, el, by=None, value=None):
        try:
            if not isinstance(el, tuple) and by and value:
                el = (by, value)
            element = self.waitDriver.until(EC.presence_of_element_located(el))
            element.click()
        except Exception as e:
            print(f"Failed to click element: {e}")
            raise e



    def get_element_text(self, el):
        try:
            if self.is_element_present(el):
                element = self.waitDriver.until(
                    EC.visibility_of_element_located(el)).text
                print(f"Element text: {element}")
                return element
            else:
                print("Element not found, returning empty string")
                return ""
        except Exception as e:
            print(f"Failed to get text from element: {e}")
            raise e

    def get_elements_list(self, el, num):
        try:
            elements = self.waitDriver.until(
                EC.presence_of_all_elements_located(el))
            return elements[:num]
        except Exception as e:
            print(f"Failed to get list of elements: {e}")
            raise e

    def scroll_to_element_by_action(self, el, by=None, value=None):
        try:
            if not isinstance(el, tuple) and by and value:
                el = (by, value)
            element = self.waitDriver.until(
                EC.presence_of_element_located(el))
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
        except Exception as e:
            print(f"Failed to scroll to element: {e}")
            raise e


    def wait_for_element(self, el, timeout=10):
        try:
            self.waitDriver.until(EC.presence_of_element_located(el), timeout)
        except Exception as e:
            print(f"Element not found within {timeout} seconds: {e}")
            raise e