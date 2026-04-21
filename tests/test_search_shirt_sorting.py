import random
import allure
import pytest
from selenium import webdriver
from pages.home_page import HomePage
from pages.search_results_page import SearchResultsPage
from pages.cart_page import CartPage
from config.constants import SEARCH_QUERY_SHIRT, BASE_URL

@allure.feature("Поиск товаров")
@allure.story("Увеличение кол-ва товара в корзине")
@allure.id("TC-02")
@allure.title("Поиск 'shirt' → сортировка → корзина → Sub-Total")
@allure.description("""
Проверка поискововой выдачи и корзины

Шаги:
1. Ввести в поисковую строку 'shirt'
2. Отсортировать результат по наименованию А-Z
3. Добавить 2 и 3 товар из выдачи в корзину
4. Указать рандомное количество
5. Сравнить цены на товары в корзине, выбрать товар наименьшей стоимости
6. Увеличить количество товара с наименьшей стоимостью в два раза
7. Сравнить итоговую и ожидаемую стоимость товаров в корзине
                    
Ожидаемый результат: Второй и третий товары из выдачи по слову `shirt` находятся в корзине. Первоначальное количество самого дешевого товара увеличено в два раза, итоговая стоимость товаров в корзине пересчитана.
""")

@allure.severity(allure.severity_level.CRITICAL)
class TestSearchShirtSorting:

    @pytest.fixture(autouse=True)
    def setup(self, driver: webdriver.Chrome):
        self.driver    = driver
        self.home_page = HomePage(driver)
        self.driver.get(BASE_URL)

    def _screenshot(self, name: str):
        allure.attach(self.driver.get_screenshot_as_png(), name=name,
                      attachment_type=allure.attachment_type.PNG)

    def _attach_text(self, text: str, label: str):
        allure.attach(text, name=label, attachment_type=allure.attachment_type.TEXT)

    def test_search_sort_add_to_cart_and_check_total(self):

        with allure.step(f"Шаг 1: Поиск '{SEARCH_QUERY_SHIRT}'"):
            results: SearchResultsPage = self.home_page.search_for(SEARCH_QUERY_SHIRT)
            results.wait_for_products()
            self._screenshot("01_search")

        with allure.step("Шаг 2: Результаты содержат 'shirt'"):
            results.assert_results_contain(SEARCH_QUERY_SHIRT)
            self._screenshot("02_verified")

        with allure.step("Шаг 3: Сортировка A→Z"):
            results.sort_by_name_asc()
            self._screenshot("03_sorted")

        with allure.step("Шаг 4: Проверить A→Z"):
            results.assert_sorted_by_name_asc()
            sorted_names = results.get_product_names()
            self._attach_text("\n".join(sorted_names), "04_names")

        qty_second = random.randint(2, 10)
        with allure.step(f"Шаг 5: Добавить 2-й товар «{sorted_names[1]}» qty={qty_second}"):
            results.add_to_cart_by_index(product_index=1, qty=qty_second)
            self._screenshot("05_second_added")

        qty_third = random.randint(2, 10)
        with allure.step(f"Шаг 6: Добавить 3-й товар «{sorted_names[2]}» qty={qty_third}"):
            results.add_to_cart_by_index(product_index=2, qty=qty_third)
            self._screenshot("06_third_added")

        with allure.step("Шаг 7: Корзина"):
            cart = CartPage(self.driver)
            cart.open_cart()
            cart_items = cart.get_cart_items()
            assert cart_items, "Корзина пуста после добавления товаров!"
            self._attach_text(
                "\n".join(f"{it['name']}: ${it['unit_price']:.2f} × {it['qty']}" for it in cart_items),
                "07_cart")
            self._screenshot("07_cart")

        with allure.step("Шаг 8: Самый дешёвый товар"):
            cheapest = cart.get_cheapest_item(items=cart_items)
            self._screenshot("08_cheapest")

        with allure.step(f"Шаг 9: Удвоить «{cheapest['name']}» {cheapest['qty']}→{cheapest['qty']*2}"):
            updated_item, updated_items = cart.double_qty_of_cheapest(items=cart_items)
            self._attach_text(
                f"{updated_item['name']}\nqty: {updated_item['qty']}\n${updated_item['total']:.2f}",
                "09_updated")
            self._screenshot("09_doubled")

        with allure.step("Шаг 10: Sub-Total"):
            expected = cart.calculate_expected_subtotal(items=updated_items)
            actual   = cart.get_subtotal()
            self._attach_text(f"Ожидалось: ${expected:.2f}\nФактически: ${actual:.2f}", "10_subtotal")
            self._screenshot("10_subtotal")
            assert abs(actual - expected) < 0.01, f"Sub-Total не совпадает! Ожидалось: ${expected:.2f}, фактически: ${actual:.2f}"
