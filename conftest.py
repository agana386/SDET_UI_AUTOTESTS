import os
import glob
import shutil
from webdriver_manager.chrome import ChromeDriverManager
import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from config.constants import BASE_URL
 
 
def _resolve_chromedriver() -> str:
    system_driver = shutil.which("chromedriver")
    if system_driver:
        return system_driver
 
    installed_path = ChromeDriverManager().install()
    driver_dir = os.path.dirname(installed_path)
 
    for name in ["chromedriver", "chromedriver.exe"]:
        candidate = os.path.join(driver_dir, name)
        if os.path.isfile(candidate):
            os.chmod(candidate, 0o755)
            return candidate
 
    raise FileNotFoundError(
        f"chromedriver not found in {driver_dir}. "
        f"Files: {os.listdir(driver_dir)}"
    )
 
 
def pytest_configure(config):
    if not os.environ.get("CHROMEDRIVER_PATH"):
        os.environ["CHROMEDRIVER_PATH"] = _resolve_chromedriver()
 
 
@pytest.fixture(scope="function")
def driver(request):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")
    if os.environ.get("CI"):
        options.add_argument("--headless=new")
 
    service = Service(os.environ["CHROMEDRIVER_PATH"])
    drv = webdriver.Chrome(service=service, options=options)
    drv.implicitly_wait(20)
 
    for attempt in range(3):
        try:
            drv.get(BASE_URL)
            break
        except Exception:
            if attempt == 2:
                raise
 
    yield drv
 
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        allure.attach(
            drv.get_screenshot_as_png(),
            name="FAILURE_screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
 
    drv.quit()
 
 
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
