from typing import List
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
 
 
class SearchResultsPage(BasePage):
    PRODUCT_LOCATOR = (By.CSS_SELECTOR, ".prdocutname")
    PRODUCT_ITEMS = PRODUCT_LOCATOR
    SORT_DROPDOWN = (By.ID, "sort")
    ADD_TO_CART_BTN = (By.CSS_SELECTOR, "a.productcart")
 
    @allure.step("Названия товаров")
    def get_product_names(self) -> List[str]:
        self.wait_for_products()
        names = self.get_element_texts(self.PRODUCT_ITEMS)
        self.attach_text("\n".join(names), "product_names")
        return names
 
    @allure.step("Сортировка A→Z")
    def sort_by_name_asc(self):
        old_first = self.get_product_names()[0]
        Select(self.wait_clickable(self.SORT_DROPDOWN)).select_by_value("pd.name-ASC")
        self.wait.until(lambda d: self.get_product_names()[0] != old_first)
        return self
 
    @allure.step("Получить URL товара по индексу #{product_index}")
    def get_product_url_by_index(self, product_index: int) -> str:
        """Возвращает URL страницы товара по его позиции в списке результатов."""
        btns = self.wait_for_all(self.ADD_TO_CART_BTN)
        return btns[product_index].get_attribute("href")
 
    def get_search_url(self) -> str:
        """Возвращает текущий URL страницы результатов поиска для возврата после добавления."""
        return self.driver.current_url
