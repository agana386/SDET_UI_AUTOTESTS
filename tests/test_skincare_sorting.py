from typing import List
import allure
import pytest
from pages.home_page import HomePage
from pages.category_page import CategoryPage


def attach_text(text: str, label: str):
    allure.attach(text, name=label, attachment_type=allure.attachment_type.TEXT)


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

    def test_sorting_all_variants(self, driver, home_page):

        with allure.step("Шаг 1: Открыть случайную категорию с ≥4 товарами"):
            cat, cat_name, _ = home_page.navigate_to_random_category(min_products=4)

        with allure.step(f"Шаг 2: Проверить, что в категории «{cat_name}» не менее 4 товаров"):
            names = cat.get_product_names()
            attach_text(f"{cat_name}: {len(names)} товаров\n" + "\n".join(names), "products")
            assert len(names) >= 4, f"«{cat_name}»: найдено {len(names)} товаров, ожидалось ≥4"

        with allure.step("Шаг 3: Применить сортировку Name A-Z и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_NAME_AZ)
            names_asc = cat.get_product_names()
            attach_text("\n".join(names_asc), "03_names_asc")
            expected = sorted(names_asc, key=str.lower)
            assert names_asc == expected, \
                f"[{cat_name}] Name A-Z: порядок не совпадает.\nПолучено: {names_asc}\nОжидалось: {expected}"

        with allure.step("Шаг 4: Применить сортировку Name Z-A и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_NAME_ZA)
            names_desc = cat.get_product_names()
            attach_text("\n".join(names_desc), "04_names_desc")
            expected = sorted(names_desc, key=str.lower, reverse=True)
            assert names_desc == expected, \
                f"[{cat_name}] Name Z-A: порядок не совпадает.\nПолучено: {names_desc}\nОжидалось: {expected}"

        with allure.step("Шаг 5: Применить сортировку Price Low→High и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_PRICE_LOW_HIGH)
            prices_asc = cat.get_product_prices()
            attach_text(str(prices_asc), "05_prices_asc")
            assert prices_asc == sorted(prices_asc), \
                f"[{cat_name}] Price Low→High: порядок не совпадает.\nПолучено: {prices_asc}\nОжидалось: {sorted(prices_asc)}"

        with allure.step("Шаг 6: Применить сортировку Price High→Low и проверить порядок"):
            cat.apply_sort(CategoryPage.SORT_PRICE_HIGH_LOW)
            prices_desc = cat.get_product_prices()
            attach_text(str(prices_desc), "06_prices_desc")
            assert prices_desc == sorted(prices_desc, reverse=True), \
                f"[{cat_name}] Price High→Low: порядок не совпадает.\nПолучено: {prices_desc}\nОжидалось: {sorted(prices_desc, reverse=True)}"
