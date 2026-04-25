from typing import List
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class CategoryPage(BasePage):
    PRODUCT_LOCATOR = (By.CSS_SELECTOR, ".prdocutname")
    PRODUCT_NAMES = PRODUCT_LOCATOR
    THUMBNAILS = (By.CSS_SELECTOR, ".thumbnail")
    SORT_DROPDOWN = (By.ID, "sort")

    SORT_NAME_AZ = "pd.name-ASC"
    SORT_NAME_ZA = "pd.name-DESC"
    SORT_PRICE_LOW_HIGH = "p.price-ASC"
    SORT_PRICE_HIGH_LOW = "p.price-DESC"

    @allure.step("Сортировка: {sort_value}")
    def apply_sort(self, sort_value: str):
        Select(self.wait_clickable(self.SORT_DROPDOWN)).select_by_value(sort_value)
        WebDriverWait(self.driver, 8).until(lambda d: self._selected_sort(d) == sort_value)
        self.wait_for_products()
        return self

    def _selected_sort(self, driver) -> str:
        """
        Возвращает текущее выбранное значение в дропдауне сортировки.
        Используется как условие ожидания в apply_sort — позволяет убедиться
        что страница перезагрузилась с новой сортировкой, прежде чем читать товары.
        Возвращает пустую строку если элемент недоступен (страница ещё грузится).
        """
        try:
            el = driver.find_element(*self.SORT_DROPDOWN)
            return Select(el).first_selected_option.get_attribute("value") or ""
        except Exception:
            return ""

    @allure.step("Названия товаров")
    def get_product_names(self) -> List[str]:
        self.wait_for_products()
        names = self.get_element_texts(self.PRODUCT_NAMES)
        self.attach_text("\n".join(names), "product_names")
        return names

    @allure.step("Цены товаров")
    def get_product_prices(self) -> List[float]:
        self.wait_for_products()
        prices = []
        for thumb in self.find_all(self.THUMBNAILS):
            elems = thumb.find_elements(By.CSS_SELECTOR, ".pricenew") or \
                    thumb.find_elements(By.CSS_SELECTOR, ".oneprice")
            if elems:
                try:
                    prices.append(float(elems[0].text.strip().replace("$", "").replace(",", "")))
                except ValueError:
                    continue
        self.attach_text(str(prices), "product_prices")
        return prices
