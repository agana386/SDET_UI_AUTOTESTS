import os
import glob
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.constants import BASE_URL


def _resolve_chromedriver() -> str:
    installed_path = ChromeDriverManager().install()
    driver_dir = os.path.dirname(installed_path)
    candidates = glob.glob(os.path.join(driver_dir, "chromedriver*"))
    chromedriver_bin = next(
        (p for p in candidates
         if os.path.isfile(p)
         and os.access(p, os.X_OK)
         and "NOTICES" not in os.path.basename(p)
         and "LICENSE" not in os.path.basename(p)),
        None,
    )
    if chromedriver_bin is None:
        raise FileNotFoundError(
            f"chromedriver not found in {driver_dir}. "
            f"Files: {[os.path.basename(f) for f in candidates]}"
        )
    return chromedriver_bin


def pytest_configure(config):
    if not os.environ.get("CHROMEDRIVER_PATH"):
        os.environ["CHROMEDRIVER_PATH"] = _resolve_chromedriver()


@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")
    # Headless только в CI (GitHub Actions автоматически выставляет CI=true)
    # Локально браузер открывается как обычно
    if os.environ.get("CI"):
        options.add_argument("--headless=new")
    service = Service(os.environ["CHROMEDRIVER_PATH"])
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(10)
    with allure.step("Открыть главную страницу"):
        drv.get(BASE_URL)
    yield drv
    drv.quit()
