from typing import List
import allure
import pytest
from selenium import webdriver
from pages.home_page import HomePage
from pages.category_page import CategoryPage


@allure.feature("Каталог товаров")
@allure.story("Сортировка в категории")
@allure.id("TC-01")
@allure.title("Сортировка товаров в категории (Name A-Z, Z-A, Price Low→High, High→Low)")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
Проверка корректной работы сортировки товаров в случайной категории.

Шаги:
1. Открыть случайную категорию с количеством товаров ≥ 4
2. Проверить, что товаров не менее 4
3. Применить сортировку Name A-Z и проверить порядок
4. Применить сортировку Name Z-A и проверить порядок
5. Применить сортировку Price Low→High и проверить порядок
6. Применить сортировку Price High→Low и проверить порядок

Ожидаемый результат:
Сортировка корректно применяется по имени и цене в обоих направлениях.
""")
class TestCategorySorting:

    @pytest.fixture(autouse=True)
    def setup(self, driver: webdriver.Chrome):
        self.home_page = HomePage(driver)
        self.driver = driver

    def _screenshot(self, name: str):
        allure.attach(self.driver.get_screenshot_as_png(), name=name,
                      attachment_type=allure.attachment_type.PNG)

    def _attach_names(self, names: List[str], label: str):
        allure.attach("\n".join(names), name=label, attachment_type=allure.attachment_type.TEXT)

    def _attach_prices(self, prices: List[float], label: str):
        allure.attach(str(prices), name=label, attachment_type=allure.attachment_type.TEXT)

    def test_sorting_all_variants(self):

        with allure.step("Шаг 1: Открыть случайную категорию с ≥4 товарами"):
            cat, cat_name, _ = self.home_page.navigate_to_random_category(min_products=4)
            self._screenshot("01_category")

        with allure.step(f"Шаг 2: Проверить, что в категории «{cat_name}» не менее 4 товаров"):
            names = cat.get_product_names()
            allure.attach(f"{cat_name}: {len(names)} товаров\n" + "\n".join(names),
                          name="products", attachment_type=allure.attachment_type.TEXT)
            assert len(names) >= 4, f"«{cat_name}»: найдено {len(names)} товаров, ожидалось ≥4"

        with allure.step("Шаг 3: Применить сортировку Name A-Z и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_NAME_AZ)
            names_asc = cat.get_product_names()
            self._attach_names(names_asc, "03_names_asc")
            expected = sorted(names_asc, key=str.lower)
            assert names_asc == expected, \
                f"[{cat_name}] Name A-Z: порядок не совпадает.\nПолучено: {names_asc}\nОжидалось: {expected}"
            self._screenshot("03_az")

        with allure.step("Шаг 4: Применить сортировку Name Z-A и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_NAME_ZA)
            names_desc = cat.get_product_names()
            self._attach_names(names_desc, "04_names_desc")
            expected = sorted(names_desc, key=str.lower, reverse=True)
            assert names_desc == expected, \
                f"[{cat_name}] Name Z-A: порядок не совпадает.\nПолучено: {names_desc}\nОжидалось: {expected}"
            self._screenshot("04_za")

        with allure.step("Шаг 5: Применить сортировку Price Low→High и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_PRICE_LOW_HIGH)
            prices_asc = cat.get_product_prices()
            self._attach_prices(prices_asc, "05_prices_asc")
            assert prices_asc == sorted(prices_asc), \
                f"[{cat_name}] Price Low→High: порядок не совпадает.\nПолучено: {prices_asc}\nОжидалось: {sorted(prices_asc)}"
            self._screenshot("05_price_asc")

        with allure.step("Шаг 6: Применить сортировку Price High→Low и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_PRICE_HIGH_LOW)
            prices_desc = cat.get_product_prices()
            self._attach_prices(prices_desc, "06_prices_desc")
            assert prices_desc == sorted(prices_desc, reverse=True), \
                f"[{cat_name}] Price High→Low: порядок не совпадает.\nПолучено: {prices_desc}\nОжидалось: {sorted(prices_desc, reverse=True)}"
            self._screenshot("06_price_desc")
