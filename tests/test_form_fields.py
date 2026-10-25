import allure
import pytest

from pages.form_fields import FormFieldsPage


@pytest.mark.positive
@allure.feature("Form Fields")
@allure.title("FORM-P01: Message заполняется актуальным списком Automation tools через Selenium")
def test_message_contains_automation_tools(page_factory):
    page = page_factory(FormFieldsPage)
    tools = page.fill_message_with_tools()
    assert tools, "Список инструментов не должен быть пустым"
    assert page.value("#message") == ", ".join(tools)
    assert page.value("#message").split(", ") == tools
