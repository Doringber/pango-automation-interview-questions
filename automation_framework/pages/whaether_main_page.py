from utilities.base_page import BasePage
from selenium.webdriver.common.by import By

# class that perfoerms actions on the weather page


class WeatherPage(BasePage):

    CITIES_LIST_NUM = (By.CSS_SELECTOR,"body > div.main-content-div > section.bg--grey.pdflexi-t--small > div > section > div:nth-child(3) > div > table > tbody > tr >td:nth-child(1)")


    TITLE_NAME = (By.XPATH, "/html/body/div[5]/header/div[2]/div/div/h1")

    def __init__(self, driver):
        super().__init__(driver)
        self.driver = driver

    def get_cities_list(self, num):
        return self.get_elements_list(self.CITIES_LIST_NUM, num)



    def scroll_to_element_by_name(self, name):
        self.scroll_to_element_by_action((By.XPATH, f"//*[contains(text(), '{name}')]"))
        
        
    def click_element_by_name(self, name):
        self.click_element((By.XPATH, f"//*[contains(text(), '{name}')]"))


    def is_element_present_by_name(self, name):
        return self.is_element_present((By.XPATH, f"//*[contains(text(), '{name}')]"))
    
    
    def get_title_name(self):
        return self.get_element_text(self.TITLE_NAME)