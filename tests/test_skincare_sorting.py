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
@allure.severity(allure.severity_level.NORMAL)
class TestCategorySorting:

    @pytest.fixture(autouse=True)
    def setup(self, driver: webdriver.Chrome):
        self.home_page = HomePage(driver)
        self.driver = driver

    def _screenshot(self, name: str):
        allure.attach(
            self.driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG
        )

    def _attach_names(self, names: List[str], label: str):
        allure.attach(
            "\n".join(names),
            name=label,
            attachment_type=allure.attachment_type.TEXT
        )

    def _attach_prices(self, prices: List[float], label: str):
        allure.attach(
            str(prices),
            name=label,
            attachment_type=allure.attachment_type.TEXT
        )

    def test_sorting_all_variants(self):

        with allure.step("Открыть случайную категорию с ≥4 товарами"):
            cat, cat_name, _ = self.home_page.navigate_to_random_category(min_products=4)
            self._screenshot("category")

        with allure.step(f"Проверить, что в категории «{cat_name}» не менее 4 товаров"):
            names = cat.get_product_names()
            allure.attach(
                f"{cat_name}: {len(names)} товаров\n" + "\n".join(names),
                name="products",
                attachment_type=allure.attachment_type.TEXT
            )
            assert len(names) >= 4

        with allure.step("Применить сортировку Name A-Z и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_NAME_AZ)
            names_asc = cat.get_product_names()
            self._attach_names(names_asc, "names_asc")
            assert names_asc == sorted(names_asc, key=str.lower)
            self._screenshot("az")

        with allure.step("Применить сортировку Name Z-A и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_NAME_ZA)
            names_desc = cat.get_product_names()
            self._attach_names(names_desc, "names_desc")
            assert names_desc == sorted(names_desc, key=str.lower, reverse=True)
            self._screenshot("za")

        with allure.step("Применить сортировку Price Low→High и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_PRICE_LOW_HIGH)
            prices_asc = cat.get_product_prices()
            self._attach_prices(prices_asc, "prices_asc")
            assert prices_asc == sorted(prices_asc)
            self._screenshot("price_asc")

        with allure.step("Применить сортировку Price High→Low и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_PRICE_HIGH_LOW)
            prices_desc = cat.get_product_prices()
            self._attach_prices(prices_desc, "prices_desc")
            assert prices_desc == sorted(prices_desc, reverse=True)
            self._screenshot("price_desc")