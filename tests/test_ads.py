from urllib.parse import urlsplit

import allure
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.ads import AdsPage


pytestmark = [allure.feature("Ads")]


@pytest.fixture
def page(page_factory):
    return page_factory(AdsPage)


@pytest.mark.positive
@allure.title("ADS-P01: Реклама появляется автоматически с нужным текстом")
def test_ad_appears(page):
    original_handles = page.driver.window_handles
    panel = page.wait_ad()
    assert "I am an ad." in panel.text
    assert page.visible(page.PANEL + " .pum-title").text == "Hi"
    assert page.driver.window_handles == original_handles


@pytest.mark.positive
@allure.title("ADS-P02: Закрытие рекламы кнопкой крестика")
def test_close_ad(page):
    page.wait_ad()
    page.close_ad()
    assert not page.ad_visible()


@pytest.mark.positive
@allure.title("ADS-P03: Кнопка закрытия рекламы работает с клавиатуры")
def test_close_ad_with_keyboard(page):
    page.wait_ad()
    page.visible(page.CLOSE).send_keys(Keys.ENTER)
    page.hidden(page.AD)


@pytest.mark.positive
@allure.title("ADS-P04: После закрытия рекламы работает навигация страницы")
def test_page_usable_after_close(page):
    page.wait_ad()
    page.close_ad()
    page.driver.find_element(By.LINK_TEXT, "Home").click()
    page.wait.until(lambda driver: urlsplit(driver.current_url).path == urlsplit(page.base_url).path)


@pytest.mark.positive
@allure.title("ADS-P05: Обновление страницы снова запускает показ рекламы")
def test_ad_after_refresh(page):
    page.wait_ad()
    page.close_ad()
    page.driver.refresh()
    assert "I am an ad." in page.wait_ad().text


@pytest.mark.positive
@pytest.mark.parametrize("width", [390, 768], ids=["ADS-P06-phone", "ADS-P07-tablet"])
@allure.title("Рекламу можно закрыть при ширине окна {width}px")
def test_close_ad_on_narrow_viewport(page, width):
    page.driver.set_window_size(width, 900)
    page.wait_ad()
    page.close_ad()
    assert not page.ad_visible()


@pytest.mark.negative
@allure.title("ADS-N01: Escape не закрывает рекламное окно")
def test_escape_does_not_close_ad(page):
    page.wait_ad()
    page.escape()
    page.remains(page.ad_visible)


@pytest.mark.negative
@allure.title("ADS-N02: Нажатие на фон не закрывает рекламное окно")
def test_overlay_does_not_close_ad(page):
    page.wait_ad()
    page.click_overlay(page.AD)
    page.remains(page.ad_visible)


@pytest.mark.negative
@allure.title("ADS-N03: Закрытая реклама не появляется повторно без перезагрузки")
def test_ad_does_not_repeat(page):
    page.wait_ad()
    page.close_ad()
    page.remains(lambda: not page.ad_visible(), seconds=6)

