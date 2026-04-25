import allure
import pytest
from config.constants import BASE_URL
 
 
@allure.feature("Корзина")
@allure.story("Рандомные товары, удаление четных, проверка суммы")
class TestCartRandomProducts:
 
    @allure.id("TC-03")
    @allure.title("Выбрать 5 рандомных товаров – удалить четные – Sub-Total")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("""
Проверка корректной работы удаления товаров из корзины и расчета итоговой стоимости.
 
Шаги:
1. Выбрать на главной странице магазина 5 случайных товаров и добавить в корзину
2. Проверить, что в корзине ровно 5 товаров
3. Удалить из корзины четные по порядку товары (2-й и 4-й)
4. Проверить, что остались 1-й, 3-й и 5-й товары
5. Рассчитать ожидаемую стоимость и сравнить с фактической
 
Ожидаемый результат:
5 случайных товаров помещены в корзину, 2-й и 4-й товары удалены, итоговая сумма рассчитана верно.
    """)
    def test_add_random_delete_even_check_total(self, driver, home_page, cart_page):
 
        with allure.step("Шаг 1: Добавить 5 рандомных товаров с главной страницы"):
            added = home_page.add_random_products_to_cart(count=5, qty_min=1, qty_max=5)
 
        with allure.step("Шаг 2: Открыть корзину и убедиться, что товаров 5"):
            cart_page.open_cart()
            cart_items = cart_page.get_cart_items()
 
            if len(cart_items) < 5:
                missing = 5 - len(cart_items)
                extra = home_page.add_random_products_to_cart(
                    count=missing, qty_min=1, qty_max=5,
                    exclude_names={it["name"] for it in cart_items},
                )
                added.extend(extra)
                cart_page.open_cart()
                cart_items = cart_page.get_cart_items()
 
            assert len(cart_items) == 5, \
                f"В корзине {len(cart_items)} товаров, ожидалось 5"
 
        with allure.step(f"Шаг 3: Удалить 2-й «{cart_items[1]['name']}» и 4-й «{cart_items[3]['name']}»"):
            remaining_items = cart_page.remove_even_items()
 
        with allure.step("Шаг 4: Проверить, что остались 1-й, 3-й и 5-й товары"):
            assert len(remaining_items) == 3, \
                f"Осталось {len(remaining_items)} товаров, ожидалось 3"
            expected_names = {cart_items[0]["name"], cart_items[2]["name"], cart_items[4]["name"]}
            actual_names = {it["name"] for it in remaining_items}
            assert actual_names == expected_names, \
                f"Остались не те товары!\nОжидалось: {expected_names}\nФактически: {actual_names}"
 
        with allure.step("Шаг 5: Проверить Sub-Total"):
            expected = cart_page.calculate_expected_subtotal(items=remaining_items)
            actual = cart_page.get_subtotal()
            assert abs(actual - expected) < 0.01, \
                f"Sub-Total не совпадает! Ожидалось: ${expected:.2f}, фактически: ${actual:.2f}"
