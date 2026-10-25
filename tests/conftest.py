import platform
from pathlib import Path

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService


_DRIVER_KEY = pytest.StashKey()


def pytest_addoption(parser):
    group = parser.getgroup("ui")
    group.addoption("--browser", choices=("chrome", "firefox"), default="chrome")
    group.addoption("--headed", action="store_true", help="Show browser window")
    group.addoption("--base-url", default="https://practice-automation.com/")
    group.addoption("--timeout", type=float, default=20)
    group.addoption("--driver-path", help="Use an existing matching WebDriver")
    group.addoption("--browser-binary", help="Path to the Chrome or Firefox executable")
    group.addoption("--no-sandbox", action="store_true", help="Chrome only: for restricted containers")


@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    headed = request.config.getoption("--headed")
    driver_path = request.config.getoption("--driver-path")
    browser_binary = request.config.getoption("--browser-binary")
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        if browser_binary:
            options.binary_location = browser_binary
        if not headed:
            options.add_argument("--headless=new")
        if request.config.getoption("--no-sandbox"):
            options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=en-US")
        service = ChromeService(executable_path=driver_path) if driver_path else ChromeService()
        browser_driver = webdriver.Chrome(options=options, service=service)
    else:
        options = webdriver.FirefoxOptions()
        if browser_binary:
            options.binary_location = browser_binary
        if not headed:
            options.add_argument("-headless")
        options.set_preference("intl.accept_languages", "en-US,en")
        service = FirefoxService(executable_path=driver_path) if driver_path else FirefoxService()
        browser_driver = webdriver.Firefox(options=options, service=service)
    request.node.stash[_DRIVER_KEY] = browser_driver
    try:
        browser_driver.set_window_size(1440, 1000)
        browser_driver.set_page_load_timeout(60)
        # Explicit waits only. Fresh browser/profile per test prevents state leaks.
        browser_driver.implicitly_wait(0)
        report_dir = request.config.getoption("allure_report_dir")
        if report_dir:
            directory = Path(report_dir)
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "environment.properties").write_text(
                f"Browser={browser}\n"
                f"Browser.version={browser_driver.capabilities.get('browserVersion')}\n"
                f"Python={platform.python_version()}\n"
                f"OS={platform.system()}\n"
                f"Base.URL={request.config.getoption('--base-url')}\n",
                encoding="utf-8",
            )
        yield browser_driver
    finally:
        browser_driver.quit()
        del request.node.stash[_DRIVER_KEY]


@pytest.fixture
def page_factory(driver, request):
    def make(page_class):
        return page_class(
            driver,
            request.config.getoption("--base-url").rstrip("/") + "/",
            request.config.getoption("--timeout"),
        ).open()
    return make


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    driver = item.stash.get(_DRIVER_KEY, None)
    if report.failed and driver is not None:
        try:
            allure.attach(driver.get_screenshot_as_png(), name=f"failure-{report.when}", attachment_type=allure.attachment_type.PNG)
            allure.attach(driver.current_url, name="Current URL", attachment_type=allure.attachment_type.TEXT)
            allure.attach(driver.page_source, name="Page source", attachment_type=allure.attachment_type.HTML)
        except Exception as error:
            # Preserve the original test failure if the browser has crashed.
            allure.attach(str(error), name="Diagnostic capture error", attachment_type=allure.attachment_type.TEXT)

