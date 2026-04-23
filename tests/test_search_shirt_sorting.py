import random
import allure
from pages.search_results_page import SearchResultsPage
from pages.product_page import ProductPage
from config.constants import SEARCH_QUERY_SHIRT


def add_product_to_cart(driver, results: SearchResultsPage, product_index: int, qty: int):
    """
    Вспомогательная функция шага теста.
    Переходит на страницу товара по индексу из результатов поиска,
    устанавливает количество и добавляет в корзину, затем возвращается
    на страницу результатов поиска.
    Взаимодействует с двумя страницами (SearchResultsPage + ProductPage) —
    поэтому реализована на уровне теста, а не внутри page-класса.
    """
    MAX_QTY = 10
    search_url = results.get_search_url()
    product_url = results.get_product_url_by_index(product_index)
    driver.get(product_url)
    pp = ProductPage(driver)
    pp.wait_for_page()
    pp.set_quantity(min(qty, MAX_QTY))
    pp.click_add_to_cart()
    driver.get(search_url)
    results.wait_for_products()


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

        with allure.step(f"Шаг 1: Поиск '{SEARCH_QUERY_SHIRT}'"):
            results = home_page.search_for(SEARCH_QUERY_SHIRT)
            results.wait_for_products()

        with allure.step("Шаг 2: Результаты содержат 'shirt'"):
            names = results.get_product_names()
            assert any(SEARCH_QUERY_SHIRT.lower() in n.lower() for n in names), \
                f"'{SEARCH_QUERY_SHIRT}' не найден в результатах. Список: {names}"

        with allure.step("Шаг 3: Сортировка A→Z и проверка порядка"):
            results.sort_by_name_asc()
            sorted_names = results.get_product_names()
            assert sorted_names == sorted(sorted_names, key=str.lower), (
                f"Сортировка A→Z не работает.\n"
                f"Получено: {sorted_names}\n"
                f"Ожидалось: {sorted(sorted_names, key=str.lower)}"
            )

        qty_second = random.randint(2, 10)
        with allure.step(f"Шаг 4: Добавить 2-й товар «{sorted_names[1]}» qty={qty_second}"):
            add_product_to_cart(driver, results, product_index=1, qty=qty_second)

        qty_third = random.randint(2, 10)
        with allure.step(f"Шаг 5: Добавить 3-й товар «{sorted_names[2]}» qty={qty_third}"):
            add_product_to_cart(driver, results, product_index=2, qty=qty_third)

        with allure.step("Шаг 6: Открыть корзину"):
            cart_page.open_cart()
            cart_items = cart_page.get_cart_items()
            assert cart_items, "Корзина пуста после добавления товаров!"

        with allure.step("Шаг 7: Найти самый дешёвый товар"):
            cheapest = cart_page.get_cheapest_item(items=cart_items)

        with allure.step(f"Шаг 8: Удвоить «{cheapest['name']}» {cheapest['qty']}→{cheapest['qty'] * 2}"):
            updated_item, updated_items = cart_page.double_qty_of_cheapest(items=cart_items)

        with allure.step("Шаг 9: Проверить Sub-Total"):
            expected = cart_page.calculate_expected_subtotal(items=updated_items)
            actual = cart_page.get_subtotal()
            assert abs(actual - expected) < 0.01, (
                f"Sub-Total не совпадает! Ожидалось: ${expected:.2f}, фактически: ${actual:.2f}"
            )
