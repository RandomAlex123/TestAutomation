from datetime import date

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.calendar import CalendarPage


pytestmark = [allure.feature("Calendars")]


@pytest.fixture
def page(page_factory):
    return page_factory(CalendarPage)


@pytest.mark.positive
@allure.title("CAL-P01: Выбор сегодняшней даты мышью")
def test_select_today(page):
    expected = page.driver.execute_script("const d=new Date();return [d.getFullYear(),d.getMonth()+1,d.getDate()]")
    page.open_picker()
    page.click(".dp-day-today")
    assert page.value(page.FIELD) == date(*expected).isoformat()
    page.hidden(page.PICKER)


@pytest.mark.positive
@pytest.mark.parametrize("direction,delta", [("next", 1), ("prev", -1)], ids=["CAL-P02-next-month", "CAL-P03-previous-month"])
@allure.title("Переключение месяца: {direction}")
def test_adjacent_month(page, direction, delta):
    page.open_picker()
    year, month = page.displayed_month()
    page.click(f".dp-{direction}")
    expected_year, zero_month = divmod(year * 12 + month - 1 + delta, 12)
    assert page.displayed_month() == (expected_year, zero_month + 1)
    selected = page.pick_day(15)
    assert selected == date(expected_year, zero_month + 1, 15).isoformat()
    assert page.value(page.FIELD) == selected


@pytest.mark.positive
@allure.title("CAL-P04: Выбор 29 февраля високосного года через год и месяц")
def test_select_leap_day(page):
    page.pick_date(date(2024, 2, 29))
    assert page.value(page.FIELD) == "2024-02-29"


@pytest.mark.positive
@pytest.mark.parametrize("value", ["2026-01-01", "2026-12-31"], ids=["CAL-P05-year-start", "CAL-P06-year-end"])
@allure.title("Ручной ввод корректной ISO-даты: {value}")
def test_manual_iso_date(page, value):
    page.fill(page.FIELD, value)
    assert page.value(page.FIELD) == value
    assert page.driver.find_element(By.CSS_SELECTOR, page.FIELD).get_attribute("aria-invalid") != "true"


@pytest.mark.positive
@allure.title("CAL-P07: Замена уже выбранной даты")
def test_replace_date(page):
    page.fill(page.FIELD, "2026-06-15")
    page.fill(page.FIELD, "2026-07-20")
    assert page.value(page.FIELD) == "2026-07-20"


@pytest.mark.positive
@allure.title("CAL-P08: Очистка необязательного поля даты")
def test_clear_optional_date(page):
    page.fill(page.FIELD, "2026-06-15")
    page.fill(page.FIELD, "")
    assert page.value(page.FIELD) == ""
    assert page.driver.find_element(By.CSS_SELECTOR, page.FIELD).get_attribute("aria-invalid") != "true"


@pytest.mark.positive
@allure.title("CAL-P09: Закрытие календаря Escape сохраняет введённую дату")
def test_escape_preserves_date(page):
    page.fill(page.FIELD, "2026-06-15")
    page.open_picker()
    page.escape()
    page.hidden(page.PICKER)
    assert page.value(page.FIELD) == "2026-06-15"


@pytest.mark.positive
@allure.title("CAL-P10: Успешная отправка выбранной даты")
def test_submit_selected_date(page):
    page.pick_date(date(2026, 6, 15))
    assert page.value(page.FIELD) == "2026-06-15"
    page.submit_date()


@pytest.mark.negative
@pytest.mark.parametrize("value", ["not-a-date", "2025-02-30", "2026-13-01", "25.10.2026"], ids=["CAL-N01-text", "CAL-N02-impossible-day", "CAL-N03-impossible-month", "CAL-N04-wrong-format"])
@allure.title("Календарь отклоняет некорректную дату: {value}")
def test_invalid_date(page, value):
    page.fill(page.FIELD, value)
    assert "valid date" in page.date_error().lower()

