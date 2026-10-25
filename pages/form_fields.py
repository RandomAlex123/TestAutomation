import allure
from selenium.webdriver.common.by import By

from pages.base import BasePage


class FormFieldsPage(BasePage):
    path = "form-fields/"
    heading = "Form Fields"

    @allure.step("Прочитать список Automation tools средствами Selenium")
    def automation_tools(self):
        locator = (
            By.XPATH,
            "//label[normalize-space()='Automation tools']/following-sibling::ul[1]/li",
        )
        return self.wait.until(
            lambda driver: [e.text.strip() for e in driver.find_elements(*locator) if e.text.strip()]
        )

    @allure.step("Перенести список инструментов в Message через запятую")
    def fill_message_with_tools(self):
        tools = self.automation_tools()
        self.fill("#message", ", ".join(tools))
        return tools

