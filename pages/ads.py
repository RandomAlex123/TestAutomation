import allure
from selenium.webdriver.common.by import By

from pages.base import BasePage


class AdsPage(BasePage):
    path = "ads/"
    heading = "Ads"
    AD = "#pum-1272"
    PANEL = "#popmake-1272"
    CLOSE = PANEL + " button.pum-close"

    @allure.step("Дождаться появления рекламного окна и его содержимого")
    def wait_ad(self):
        self.visible(self.PANEL + " .pum-content")
        self.wait.until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, self.PANEL + " .pum-content").text.strip()
        )
        return self.visible(self.PANEL)

    @allure.step("Закрыть рекламу")
    def close_ad(self):
        self.click(self.CLOSE)
        self.hidden(self.AD)

    def ad_visible(self):
        return any(e.is_displayed() for e in self.driver.find_elements(By.CSS_SELECTOR, self.AD))

