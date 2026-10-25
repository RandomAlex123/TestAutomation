from datetime import date

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base import BasePage


class CalendarPage(BasePage):
    path = "calendars/"
    heading = "Calendars"
    FIELD = "input.jp-contact-form-date"
    PICKER = ".dp"

    @allure.step("Открыть календарь")
    def open_picker(self):
        # The date-picker script marks its input with aria-live when ready.
        self.wait.until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, self.FIELD)
            .get_attribute("aria-live") == "polite"
        )
        self.click("h1")
        self.hidden(self.PICKER)
        self.click(self.FIELD)

        def opened(driver):
            visible_days = [
                element for element in driver.find_elements(By.CSS_SELECTOR, ".dp-days")
                if element.is_displayed()
            ]
            if visible_days:
                return visible_days[0]
            # Jetpack has a short close-transition lock. If the click was
            # ignored during that transition, ArrowDown opens it once ready.
            # Recheck before every key so an already-open picker is untouched.
            driver.find_element(By.CSS_SELECTOR, self.FIELD).send_keys(Keys.ARROW_DOWN)
            return False

        self.wait.until(opened)

    def displayed_month(self):
        months = (
            "January February March April May June July August September "
            "October November December"
        ).split()
        return (
            int(self.visible(".dp-cal-year").text),
            months.index(self.visible(".dp-cal-month").text) + 1,
        )

    @allure.step("Выбрать день {day} в отображаемом месяце")
    def pick_day(self, day):
        year, month = self.displayed_month()
        buttons = self.driver.find_elements(
            By.CSS_SELECTOR, ".dp-day:not(.dp-edge-day)"
        )
        next(button for button in buttons if button.text == str(day)).click()
        self.hidden(self.PICKER)
        return date(year, month, day).isoformat()

    @allure.step("Выбрать дату {target} через календарь")
    def pick_date(self, target):
        self.open_picker()
        self.click(".dp-cal-year")
        self.click(f'.dp-year[data-year="{target.year}"]')
        self.click(".dp-cal-month")
        self.click(f'.dp-month[data-month="{target.month - 1}"]')
        return self.pick_day(target.day)

    @allure.step("Дождаться ошибки валидации даты")
    def date_error(self):
        self.wait.until(
            lambda driver: driver.find_element(By.CSS_SELECTOR, self.FIELD)
            .get_attribute("aria-invalid") == "true"
        )
        return self.visible(".grunion-field-date-wrap .contact-form__input-error.has-errors").text

    @allure.step("Отправить дату и дождаться подтверждения сервера")
    def submit_date(self):
        form = self.driver.find_element(By.CSS_SELECTOR, self.FIELD).find_element(
            By.XPATH, "ancestor::form"
        )
        form.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
        self.wait.until(lambda driver: "submission-success" in form.get_attribute("class").split())

