import random
import allure
import pytest
from pages.search_results_page import SearchResultsPage
from config.constants import SEARCH_QUERY_SHIRT, BASE_URL


def attach_text(text: str, label: str):
    allure.attach(text, name=label, attachment_type=allure.attachment_type.TEXT)


@allure.feature("Поиск товаров")
@allure.story("Увеличение кол-ва товара в корзине")
@allure.id("TC-02")
@allure.title("Поиск 'shirt' → сортировка → корзина → Sub-Total")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
Проверка поисковой выдачи и корзины.

Шаги:
1. Ввести в поисковую строку 'shirt'
2. Отсортировать результат по наименованию А-Z
3. Добавить 2-й и 3-й товар из выдачи в корзину с рандомным количеством
4. Сравнить цены на товары в корзине, выбрать товар наименьшей стоимости
5. Увеличить количество товара с наименьшей стоимостью в два раза
6. Сравнить итоговую и ожидаемую стоимость товаров в корзине

Ожидаемый результат:
Второй и третий товары из выдачи по слову 'shirt' находятся в корзине.
Количество самого дешёвого товара увеличено вдвое, итоговая стоимость пересчитана.
""")
class TestSearchShirtSorting:

    def test_search_sort_add_to_cart_and_check_total(self, driver, home_page, cart_page):
        driver.get(BASE_URL)

        with allure.step(f"Шаг 1: Поиск '{SEARCH_QUERY_SHIRT}'"):
            results: SearchResultsPage = home_page.search_for(SEARCH_QUERY_SHIRT)
            results.wait_for_products()

        with allure.step("Шаг 2: Результаты содержат 'shirt'"):
            results.assert_results_contain(SEARCH_QUERY_SHIRT)

        with allure.step("Шаг 3: Сортировка A→Z и проверка порядка"):
            results.sort_by_name_asc()
            results.assert_sorted_by_name_asc()
            sorted_names = results.get_product_names()
            attach_text("\n".join(sorted_names), "sorted_names")

        qty_second = random.randint(2, 10)
        with allure.step(f"Шаг 4: Добавить 2-й товар «{sorted_names[1]}» qty={qty_second}"):
            results.add_to_cart_by_index(product_index=1, qty=qty_second)

        qty_third = random.randint(2, 10)
        with allure.step(f"Шаг 5: Добавить 3-й товар «{sorted_names[2]}» qty={qty_third}"):
            results.add_to_cart_by_index(product_index=2, qty=qty_third)

        with allure.step("Шаг 6: Открыть корзину"):
            cart_page.open_cart()
            cart_items = cart_page.get_cart_items()
            assert cart_items, "Корзина пуста после добавления товаров!"
            attach_text(
                "\n".join(f"{it['name']}: ${it['unit_price']:.2f} × {it['qty']}" for it in cart_items),
                "cart_contents")

        with allure.step("Шаг 7: Найти самый дешёвый товар"):
            cheapest = cart_page.get_cheapest_item(items=cart_items)

        with allure.step(f"Шаг 8: Удвоить «{cheapest['name']}» {cheapest['qty']}→{cheapest['qty'] * 2}"):
            updated_item, updated_items = cart_page.double_qty_of_cheapest(items=cart_items)
            attach_text(
                f"{updated_item['name']}\nqty: {updated_item['qty']}\n${updated_item['total']:.2f}",
                "updated_item")

        with allure.step("Шаг 9: Проверить Sub-Total"):
            expected = cart_page.calculate_expected_subtotal(items=updated_items)
            actual = cart_page.get_subtotal()
            attach_text(f"Ожидалось: ${expected:.2f}\nФактически: ${actual:.2f}", "subtotal")
            assert abs(actual - expected) < 0.01, (
                f"Sub-Total не совпадает! Ожидалось: ${expected:.2f}, фактически: ${actual:.2f}"
            )
