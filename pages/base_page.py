from typing import List, Optional, Tuple
import allure
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure


class BasePage:
    # Дочерние классы переопределяют этот атрибут своим локатором
    PRODUCT_LOCATOR: Optional[Tuple] = None

    def __init__(self, driver: webdriver.Chrome, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def find(self, locator):
        return self.driver.find_element(*locator)

    def find_all(self, locator):
        return self.driver.find_elements(*locator)

    def wait_for(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_for_all(self, locator):
        return self.wait.until(EC.presence_of_all_elements_located(locator))

    def wait_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def wait_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def open(self, url: str):
        self.driver.get(url)

    @allure.step("Ждём товары на странице")
    def wait_for_products(self, locator=None) -> "BasePage":
        """
        Ждёт появления товаров на странице.
        Использует переданный locator или PRODUCT_LOCATOR дочернего класса.
        """
        target = locator or self.PRODUCT_LOCATOR
        if target is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} должен определить PRODUCT_LOCATOR "
                f"или передать locator явно"
            )
        self.wait.until(EC.presence_of_all_elements_located(target))
        return self

    def get_element_texts(self, locator) -> List[str]:
        """Возвращает тексты всех элементов по локатору."""
        els = self.wait.until(EC.presence_of_all_elements_located(locator))
        return [el.text.strip() for el in els if el.text.strip()]

    def attach_text(self, text: str, name: str):
        """Прикрепляет текстовые данные к Allure-отчёту."""
        allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)
