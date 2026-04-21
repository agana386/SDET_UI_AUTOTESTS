import allure
import pytest
from selenium import webdriver
from pages.home_page import HomePage
from pages.cart_page import CartPage
from config.constants import BASE_URL

@allure.feature("Корзина")
@allure.story("Рандомные товары, удаление четных, проверка суммы")
@allure.id("TC-03")
@allure.title("Выбрать 5 рандомных товаров → удалить четные → Sub-Total")
@allure.description("""
Проверка корректной работы удаления товароя из корзины и расчета итоговой стоимости                    

Шаги:
1. Выбрать на главной странице магазина 5 случайных товаров
2. Добавить их в корзину
2. Проверить, что товаров ровно 5
3. Удалить из корзины четные по порядку товары 
4. Рассчитать новую стоимость корзины
5. Сравнить с ожидаемым значением
                    
Ожидаемый результат:
5 случаных товаров помещены в корзину, 2 и 4 товары в корзине удалены, итоговая сумма рассчитана верно
""")

@allure.severity(allure.severity_level.CRITICAL)
class TestCartRandomProducts:

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

    def _items_summary(self, items: list) -> str:
        lines = [f"[{i+1}] {it['name']}: ${it['unit_price']:.2f} × {it['qty']} = ${it['unit_price']*it['qty']:.2f}"
                 for i, it in enumerate(items)]
        lines.append(f"{'─'*50}\nSub-Total: ${sum(it['unit_price']*it['qty'] for it in items):.2f}")
        return "\n".join(lines)

    def test_add_random_delete_even_check_total(self):

        with allure.step("Шаг 1: Добавить 5 рандомных товаров"):
            added = self.home_page.add_random_products_to_cart(count=5, qty_min=1, qty_max=5)
            self._attach_text("\n".join(f"[{i+1}] {p['name']} qty={p['qty']}" for i, p in enumerate(added)), "01_added")
            self._screenshot("01_added")

        with allure.step("Шаг 2: Корзина — убедиться что 5 товаров"):
            cart = CartPage(self.driver)
            cart.open_cart()
            cart_items = cart.get_cart_items()
            self._attach_text(self._items_summary(cart_items), "02_cart_initial")

            if len(cart_items) < 5:
                missing = 5 - len(cart_items)
                extra = self.home_page.add_random_products_to_cart(
                    count=missing, qty_min=1, qty_max=5,
                    exclude_names={it["name"] for it in cart_items},
                )
                added.extend(extra)
                cart.open_cart()
                cart_items = cart.get_cart_items()
                self._screenshot("02_after_refill")

            assert len(cart_items) == 5, f"В корзине {len(cart_items)} товаров, ожидалось 5"
            self._attach_text(self._items_summary(cart_items), "02_cart")
            self._screenshot("02_cart")

        with allure.step(f"Шаг 3: Удалить 2-й «{cart_items[1]['name']}» и 4-й «{cart_items[3]['name']}»"):
            remaining_items = cart.remove_even_items()
            self._screenshot("03_removed")

        with allure.step("Шаг 4: Остались 1-й, 3-й, 5-й товары"):
            assert len(remaining_items) == 3, f"Осталось {len(remaining_items)}, ожидалось 3"
            expected_names = {cart_items[0]["name"], cart_items[2]["name"], cart_items[4]["name"]}
            actual_names   = {it["name"] for it in remaining_items}
            assert actual_names == expected_names, \
                f"Не те товары!\nОжидалось: {expected_names}\nОсталось: {actual_names}"
            self._attach_text(self._items_summary(remaining_items), "04_remaining")
            self._screenshot("04_remaining")

        with allure.step("Шаг 5: Sub-Total"):
            expected = cart.calculate_expected_subtotal(items=remaining_items)
            actual   = cart.get_subtotal()
            self._attach_text(f"Ожидалось: ${expected:.2f}\nФактически: ${actual:.2f}", "05_subtotal")
            self._screenshot("05_subtotal")
            assert abs(actual - expected) < 0.01, f"Sub-Total не совпадает! ${expected:.2f} ≠ ${actual:.2f}"
