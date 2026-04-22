from typing import List
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from pages.product_page import ProductPage
from config.constants import SORT_NAME_AZ

MAX_QTY_PER_ORDER = 10


class SearchResultsPage(BasePage):
    PRODUCT_LOCATOR = (By.CSS_SELECTOR, ".prdocutname")
    PRODUCT_ITEMS   = PRODUCT_LOCATOR
    SORT_DROPDOWN   = (By.ID, "sort")
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, "a.productcart")

    @allure.step("Названия товаров")
    def get_product_names(self) -> List[str]:
        self.wait_for_products()
        return self.get_element_texts(self.PRODUCT_ITEMS)

    @allure.step("Сортировка A→Z")
    def sort_by_name_asc(self):
        old_first = self.get_product_names()[0]
        Select(self.wait.until(EC.element_to_be_clickable(self.SORT_DROPDOWN))).select_by_value(SORT_NAME_AZ)
        self.wait.until(lambda d: self.get_product_names()[0] != old_first)
        return self

    @allure.step("Получить URL товара по индексу #{product_index}")
    def get_product_url_by_index(self, product_index: int) -> str:
        btns = self.wait.until(EC.presence_of_all_elements_located(self.ADD_TO_CART_BTN))
        return btns[product_index].get_attribute("href")

    @allure.step("Добавить товар #{product_index} в корзину qty={qty}")
    def add_to_cart_by_index(self, product_index: int, qty: int):
        safe_qty = min(qty, MAX_QTY_PER_ORDER)
        search_url = self.driver.current_url
        product_url = self.get_product_url_by_index(product_index)

        self.driver.get(product_url)
        pp = ProductPage(self.driver)
        pp.wait_for_page()
        pp.set_quantity(safe_qty)
        pp.click_add_to_cart()

        self.driver.get(search_url)
        self.wait_for_products()
        return self
