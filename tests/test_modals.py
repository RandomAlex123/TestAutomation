import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.modals import ModalsPage


pytestmark = [allure.feature("Modals")]


@pytest.fixture
def page(page_factory):
    return page_factory(ModalsPage)


@pytest.mark.positive
@allure.title("MOD-P01: Открытие простого окна с правильным содержимым")
def test_simple_content(page):
    content = page.open_simple()
    assert "Hi, I’m a simple modal." in content.text
    assert page.visible(page.SIMPLE + " .pum-title").text == "Simple Modal"
    page.hidden(page.FORM)


@pytest.mark.positive
@allure.title("MOD-P02: Закрытие простого окна возвращает доступ к странице")
def test_close_simple(page):
    page.open_simple()
    page.close(page.SIMPLE)
    page.open_form()
    assert page.visible(page.NAME).is_enabled()


@pytest.mark.positive
@allure.title("MOD-P03: Повторное открытие простого окна после закрытия")
def test_reopen_simple(page):
    page.open_simple()
    page.close(page.SIMPLE)
    assert "simple modal" in page.open_simple().text


@pytest.mark.positive
@allure.title("MOD-P04: Ввод кириллицы и многострочного сообщения")
def test_form_fields(page):
    page.open_form()
    page.fill_form(name="Иван Тестовый", message="Первая строка\nВторая строка")
    assert page.value(page.NAME) == "Иван Тестовый"
    assert page.value(page.EMAIL) == "automation@example.com"
    assert page.value(page.MESSAGE) == "Первая строка\nВторая строка"


@pytest.mark.positive
@allure.title("MOD-P05: Закрытие формы кнопкой без отправки")
def test_close_form(page):
    page.open_form()
    page.fill(page.NAME, "Draft")
    page.close(page.FORM)
    assert page.visible("#formModal").is_enabled()


@pytest.mark.positive
@allure.title("MOD-P06: Закрытие формы клавишей Escape")
def test_escape_closes_form(page):
    page.open_form()
    page.escape()
    page.hidden(page.FORM)


@pytest.mark.positive
@allure.title("MOD-P07: Открытие простого окна с клавиатуры")
def test_open_simple_with_keyboard(page):
    page.visible("#simpleModal").send_keys(Keys.ENTER)
    assert "simple modal" in page.visible(page.SIMPLE + " .pum-content").text


@pytest.mark.positive
@allure.title("MOD-P08: Успешная отправка заполненной формы")
def test_submit_valid_form(page):
    page.open_form()
    page.fill_form()
    page.submit()
    page.wait_success()


@pytest.mark.negative
@allure.title("MOD-N01: Пустое обязательное имя блокирует отправку")
def test_empty_required_name(page):
    page.open_form()
    page.submit()
    assert "required" in page.field_error(page.NAME).lower()
    assert page.visible(page.FORM).is_displayed()


@pytest.mark.negative
@pytest.mark.parametrize("email", ["invalid-address", "user@"], ids=["MOD-N02-missing-at", "MOD-N03-missing-domain"])
@allure.title("Некорректный email блокирует отправку: {email}")
def test_invalid_email(page, email):
    page.open_form()
    page.fill_form(email=email)
    page.submit()
    assert "email" in page.field_error(page.EMAIL).lower()
    assert page.value(page.NAME) == "Automation Test"


@pytest.mark.negative
@allure.title("MOD-N04: Escape не закрывает простое окно")
def test_escape_does_not_close_simple(page):
    page.open_simple()
    page.escape()
    page.remains(lambda: page.driver.find_element(By.CSS_SELECTOR, page.SIMPLE).is_displayed())


@pytest.mark.negative
@allure.title("MOD-N05: Нажатие на фон не закрывает простое окно")
def test_overlay_does_not_close_simple(page):
    page.open_simple()
    page.click_overlay(page.SIMPLE)
    page.remains(lambda: page.driver.find_element(By.CSS_SELECTOR, page.SIMPLE).is_displayed())

