from urllib.parse import urljoin

import allure
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    path = ""
    heading = ""

    def __init__(self, driver, base_url, timeout):
        self.driver = driver
        self.base_url = base_url
        self.timeout = timeout
        self.wait = WebDriverWait(
            driver, timeout, ignored_exceptions=(StaleElementReferenceException,)
        )

    @allure.step("Открыть страницу упражнения")
    def open(self):
        self.driver.get(urljoin(self.base_url, self.path))
        self.wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "h1"), self.heading))
        return self

    def visible(self, css):
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))

    def hidden(self, css):
        self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, css)))

    @allure.step("Нажать элемент: {css}")
    def click(self, css):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css))).click()

    @allure.step("Заполнить поле {css}: {text}")
    def fill(self, css, text):
        field = self.visible(css)
        field.clear()
        if text:
            field.send_keys(text)
        # Native blur starts the site's own validation; no validation is injected.
        field.send_keys(Keys.TAB)

    def value(self, css):
        return self.driver.find_element(By.CSS_SELECTOR, css).get_property("value")

    @allure.step("Нажать Escape")
    def escape(self):
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    @allure.step("Нажать на фон за пределами окна")
    def click_overlay(self, css):
        overlay = self.visible(css)
        # W3C offsets are relative to the element's in-view centre. Select a
        # point near the upper left of the viewport, outside the modal panel.
        width = self.driver.execute_script("return innerWidth")
        height = self.driver.execute_script("return innerHeight")
        ActionChains(self.driver).move_to_element_with_offset(
            overlay, -width // 2 + 10, -height // 2 + 10
        ).click().perform()

    @allure.step("Убедиться, что состояние не меняется в течение {seconds} с")
    def remains(self, predicate, seconds=1):
        # A negative wait fails as soon as the forbidden state is observed.
        # Timeout means the predicate remained true for the observation window.
        from selenium.common.exceptions import TimeoutException

        try:
            WebDriverWait(self.driver, seconds, poll_frequency=0.1).until(
                lambda driver: not predicate()
            )
        except TimeoutException:
            return
        raise AssertionError("Состояние изменилось в течение окна наблюдения")

