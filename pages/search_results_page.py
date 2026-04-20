from typing import List
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from config.constants import SORT_NAME_AZ

MAX_QTY_PER_ORDER = 10


class SearchResultsPage(BasePage):
    PRODUCT_ITEMS   = (By.CSS_SELECTOR, ".prdocutname")
    THUMBNAILS      = (By.CSS_SELECTOR, ".thumbnail")
    SORT_DROPDOWN   = (By.ID, "sort")
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, "a.productcart")

    @allure.step("Ждём результаты")
    def wait_for_products(self):
        self.wait.until(EC.presence_of_all_elements_located(self.PRODUCT_ITEMS))
        return self

    @allure.step("Названия товаров")
    def get_product_names(self) -> List[str]:
        els = self.wait.until(EC.presence_of_all_elements_located(self.PRODUCT_ITEMS))
        return [el.text.strip() for el in els if el.text.strip()]

    @allure.step("Проверить наличие '{text}'")
    def assert_results_contain(self, text: str):
        names = self.get_product_names()
        assert any(text.lower() in n.lower() for n in names), f"'{text}' не найден. Список: {names}"
        return self

    @allure.step("Сортировка A→Z")
    def sort_by_name_asc(self):
        old_first = self.get_product_names()[0]
        Select(self.wait.until(EC.element_to_be_clickable(self.SORT_DROPDOWN))).select_by_value(SORT_NAME_AZ)
        self.wait.until(lambda d: self.get_product_names()[0] != old_first)
        return self

    @allure.step("Проверить сортировку A→Z")
    def assert_sorted_by_name_asc(self):
        names = self.get_product_names()
        allure.attach("\n".join(names), name="sorted_names", attachment_type=allure.attachment_type.TEXT)
        assert names == sorted(names, key=str.lower), f"Не A→Z.\nПолучено: {names}\nОжидалось: {sorted(names, key=str.lower)}"
        return self

    @allure.step("Добавить товар #{product_index} qty={qty}")
    def add_to_cart_by_index(self, product_index: int, qty: int):
        from pages.product_page import ProductPage
        safe_qty   = min(qty, MAX_QTY_PER_ORDER)
        search_url = self.driver.current_url
        btns       = self.wait.until(EC.presence_of_all_elements_located(self.ADD_TO_CART_BTN))
        self.driver.get(btns[product_index].get_attribute("href"))
        pp = ProductPage(self.driver)
        pp.wait_for_page()
        pp.set_quantity(safe_qty)
        pp.click_add_to_cart()
        self.driver.get(search_url)
        self.wait_for_products()
        return self
