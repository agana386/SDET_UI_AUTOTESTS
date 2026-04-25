import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage


class ProductPage(BasePage):
    QTY_INPUT = (By.ID, "product_quantity")
    ADD_TO_CART = (By.CSS_SELECTOR, "ul.productpagecart a.cart")
    CART_COUNT = (By.CSS_SELECTOR, ".nav.topcart .label")

    @allure.step("Загрузка страницы товара")
    def wait_for_page(self):
        self.wait.until(EC.visibility_of_element_located(self.QTY_INPUT))
        self.wait.until(EC.visibility_of_element_located(self.ADD_TO_CART))
        return self

    @allure.step("Установить qty={qty}")
    def set_quantity(self, qty: int):
        field = self.wait.until(EC.visibility_of_element_located(self.QTY_INPUT))
        self.driver.execute_script("arguments[0].value = '';", field)
        field.click()
        field.send_keys(str(qty))
        if field.get_attribute("value") != str(qty):
            self.driver.execute_script(f"arguments[0].value = '{qty}';", field)
        return self

    @allure.step("Add to Cart")
    def click_add_to_cart(self):
        btn = self.wait.until(EC.visibility_of_element_located(self.ADD_TO_CART))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        handles_before = set(self.driver.window_handles)
        try:
            count_before = self.driver.find_element(*self.CART_COUNT).text
        except Exception:
            count_before = "0"

        btn.click()
        try:
            self.wait.until(lambda d: d.find_element(*self.CART_COUNT).text != count_before)
        except Exception:
            try:
                self.driver.execute_script("arguments[0].click();", self.driver.find_element(*self.ADD_TO_CART))
                self.wait.until(lambda d: d.find_element(*self.CART_COUNT).text != count_before)
            except Exception:
                pass

        new_handles = set(self.driver.window_handles) - handles_before
        if new_handles:
            for h in new_handles:
                self.driver.switch_to.window(h)
                self.driver.close()
            self.driver.switch_to.window(list(handles_before)[0])
        return self
