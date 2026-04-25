from typing import List, Optional
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from config.constants import CART_URL


class CartPage(BasePage):
    CART_ROWS = (By.CSS_SELECTOR, "table.table.table-striped.table-bordered tbody tr")
    PRODUCT_NAME = (By.CSS_SELECTOR, "td.align_left a")
    QTY_INPUT = (By.CSS_SELECTOR, "input.form-control.short")
    UPDATE_BTN = (By.ID, "cart_update")
    REMOVE_BTN = (By.CSS_SELECTOR, "td.align_center a.btn.btn-sm.btn-default")
    SUBTOTAL_SPAN = (By.CSS_SELECTOR, "#totals_table tr:first-child td:last-child span.bold")

    @allure.step("Открыть корзину")
    def open_cart(self):
        self.open(CART_URL)
        self.wait_for(self.CART_ROWS)
        return self

    def wait_for_cart(self):
        self.wait_for(self.CART_ROWS)
        return self

    def _parse_price(self, text: str) -> float:
        return float(text.replace("$", "").replace(",", "").strip())

    @allure.step("Товары корзины")
    def get_cart_items(self) -> List[dict]:
        items = []
        for i, row in enumerate(self.find_all(self.CART_ROWS)):
            try:
                name_els = row.find_elements(*self.PRODUCT_NAME)
                if not name_els:
                    continue
                name = name_els[0].text.strip()
                if not name:
                    continue
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 6:
                    continue
                unit_price = self._parse_price(cells[3].text)
                qty_inputs = row.find_elements(*self.QTY_INPUT)
                qty = int(qty_inputs[0].get_attribute("value")) if qty_inputs else 1
                items.append({
                    "name": name,
                    "unit_price": unit_price,
                    "qty": qty,
                    "total": round(unit_price * qty, 2),
                    "row_index": i,
                })
            except Exception:
                continue
        self.attach_text(
            "\n".join(
                f"[{i+1}] {it['name']}: ${it['unit_price']:.2f} × {it['qty']}"
                for i, it in enumerate(items)
            ),
            "cart_items"
        )
        return items

    @allure.step("Самый дешёвый товар")
    def get_cheapest_item(self, items: Optional[list] = None) -> dict:
        if items is None:
            items = self.get_cart_items()
        cheapest = min(items, key=lambda x: x["unit_price"])
        self.attach_text(
            f"{cheapest['name']} — ${cheapest['unit_price']:.2f} × {cheapest['qty']}",
            "cheapest"
        )
        return cheapest

    @allure.step("Sub-Total")
    def get_subtotal(self) -> float:
        return self._parse_price(self.wait_for(self.SUBTOTAL_SPAN).text)

    @allure.step("Ожидаемый Sub-Total")
    def calculate_expected_subtotal(self, items: Optional[list] = None) -> float:
        if items is None:
            items = self.get_cart_items()
        subtotal = round(sum(it["unit_price"] * it["qty"] for it in items), 2)
        self.attach_text(
            "\n".join(
                f"{it['name']}: ${it['unit_price']:.2f} × {it['qty']} = ${it['unit_price'] * it['qty']:.2f}"
                for it in items
            ) + f"\n{'─' * 40}\n${subtotal:.2f}",
            "subtotal_breakdown"
        )
        return subtotal

    @allure.step("Обновить qty строки #{row_index} = {new_qty}")
    def set_qty_for_item(self, row_index: int, new_qty: int):
        rows = self.find_all(self.CART_ROWS)
        qty_input = rows[row_index].find_element(*self.QTY_INPUT)
        self.driver.execute_script("arguments[0].value = '';", qty_input)
        qty_input.click()
        qty_input.send_keys(str(new_qty))
        try:
            subtotal_before = self.find(self.SUBTOTAL_SPAN).text
        except Exception:
            subtotal_before = ""
        self.wait_clickable(self.UPDATE_BTN).click()
        if subtotal_before:
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: d.find_element(*self.SUBTOTAL_SPAN).text != subtotal_before
                )
            except Exception:
                self.wait_for_cart()
        else:
            self.wait.until(EC.staleness_of(qty_input))
            self.wait_for_cart()
        return self

    @allure.step("Удвоить qty дешёвого товара")
    def double_qty_of_cheapest(self, items: Optional[list] = None):
        cheapest = self.get_cheapest_item(items)
        new_qty = cheapest["qty"] * 2
        self.attach_text(f"{cheapest['name']}: {cheapest['qty']} → {new_qty}", "double_qty")
        self.set_qty_for_item(cheapest["row_index"], new_qty)
        updated_items = self.get_cart_items()
        updated = next((it for it in updated_items if it["name"] == cheapest["name"]), None)
        return updated, updated_items

    @allure.step("Удалить чётные позиции")
    def remove_even_items(self) -> List[dict]:
        items = self.get_cart_items()
        even_indices = list(range(1, len(items), 2))
        self.attach_text(
            "Удаляем: " + ", ".join(str(i + 1) for i in even_indices)
            + "\n" + "\n".join(f"  [{i+1}] {items[i]['name']}" for i in even_indices),
            "even_items"
        )
        rows = self.find_all(self.CART_ROWS)
        product_rows = [r for r in rows if r.find_elements(*self.PRODUCT_NAME)]
        remove_hrefs = [
            product_rows[i].find_element(*self.REMOVE_BTN).get_attribute("href")
            for i in even_indices if i < len(product_rows)
        ]
        for href in remove_hrefs:
            self.driver.get(href)
            try:
                self.wait_for(self.CART_ROWS)
            except Exception:
                self.open_cart()
        self.open_cart()
        return self.get_cart_items()
