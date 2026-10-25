import allure
from selenium.webdriver.common.by import By

from pages.base import BasePage


class ModalsPage(BasePage):
    path = "modals/"
    heading = "Modals"
    SIMPLE = "#pum-1318"
    FORM = "#pum-674"
    NAME = FORM + " input.name"
    EMAIL = FORM + " input.email"
    MESSAGE = FORM + " textarea.textarea"

    @allure.step("Открыть простое модальное окно")
    def open_simple(self):
        self.click("#simpleModal")
        return self.visible(self.SIMPLE + " .pum-content")

    @allure.step("Открыть модальное окно с формой")
    def open_form(self):
        self.click("#formModal")
        self.visible(self.NAME)

    @allure.step("Закрыть модальное окно кнопкой")
    def close(self, css):
        self.click(css + " button.pum-close")
        self.hidden(css)

    @allure.step("Заполнить контактную форму")
    def fill_form(self, name="Automation Test", email="automation@example.com", message="Educational UI test."):
        self.fill(self.NAME, name)
        self.fill(self.EMAIL, email)
        self.fill(self.MESSAGE, message)

    @allure.step("Отправить контактную форму")
    def submit(self):
        self.click(self.FORM + " button[type=submit]")

    def field_error(self, field_css):
        self.wait.until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, field_css)
            .get_attribute("aria-invalid") == "true"
        )
        field = self.driver.find_element(By.CSS_SELECTOR, field_css)
        error_id = field.get_attribute("aria-describedby").split()[0]
        return self.wait.until(
            lambda driver: driver.find_element(By.ID, error_id).text
        )

    @allure.step("Дождаться подтверждения успешной отправки")
    def wait_success(self):
        # Success is hidden in the initial DOM; presence of the thank-you text
        # alone is not proof that the request actually succeeded.
        self.wait.until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, self.FORM + " form")
            .get_attribute("class").split().count("submission-success") == 1
        )

