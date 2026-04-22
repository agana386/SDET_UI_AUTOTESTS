import random
import allure
from typing import List, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.base_page import BasePage
from pages.search_results_page import SearchResultsPage
from config.constants import BASE_URL, SEARCH_INPUT, SEARCH_BUTTON

CATEGORY_TREE = [
    ("Apparel & accessories", "68", [("Shoes","68_69"), ("T-shirts","68_70")]),
    ("Makeup", "36", [("Cheeks","36_40"), ("Eyes","36_39"), ("Face","36_38"),
                      ("Lips","36_41"), ("Nails","36_42"), ("Value Sets","36_37")]),
    ("Skincare", "43", [("Eyes","43_47"), ("Face","43_46"), ("Gift Ideas & Sets","43_45"),
                        ("Hands & Nails","43_48"), ("Sun","43_44")]),
    ("Fragrance", "49", [("Men","49_51"), ("Women","49_50")]),
    ("Men", "58", [("Body & Shower","58_63"), ("Fragrance Sets","58_59"),
                   ("Pre-Shave & Shaving","58_61"), ("Skincare","58_60")]),
    ("Hair Care", "52", [("Conditioner","52_54"), ("Shampoo","52_53")]),
    ("Books", "65", [("Audio CD","65_66"), ("Paperback","65_67")]),
]


class HomePage(BasePage):
    PRODUCT_NAME_LINK = (By.CSS_SELECTOR, "a.prdocutname")
    CART_COUNT        = (By.CSS_SELECTOR, ".nav.topcart .label")

    @allure.step("Поиск: {query}")
    def search_for(self, query: str) -> SearchResultsPage:
        field = self.wait.until(EC.visibility_of_element_located(SEARCH_INPUT))
        field.clear()
        field.send_keys(query)
        self.wait.until(EC.element_to_be_clickable(SEARCH_BUTTON)).click()
        return SearchResultsPage(self.driver)

    @allure.step("Случайная категория с ≥{min_products} товарами")
    def navigate_to_random_category(self, min_products: int = 4):
        from pages.category_page import CategoryPage

        all_cats = []
        for parent_name, parent_path, subcats in CATEGORY_TREE:
            for sub_name, sub_path in subcats:
                all_cats.append((f"{parent_name} → {sub_name}", sub_path))
            all_cats.append((parent_name, parent_path))
        random.shuffle(all_cats)

        for cat_name, cat_path in all_cats:
            url = f"{BASE_URL}index.php?rt=product/category&path={cat_path}"
            self.driver.get(url)
            cat_page = CategoryPage(self.driver)
            try:
                # Ждём загрузки страницы (document.readyState == complete)
                WebDriverWait(self.driver, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                count = len(WebDriverWait(self.driver, 15).until(
                    EC.presence_of_all_elements_located(cat_page.PRODUCT_NAMES)
                ))
            except Exception:
                count = 0

            if count >= min_products:
                real_names = cat_page.get_product_names()
                if len(real_names) < min_products:
                    count = len(real_names)
                    continue

                self.attach_text(
                    f"Категория: {cat_name}\nPath: {cat_path}\nТоваров: {len(real_names)}",
                    "selected_category"
                )
                return cat_page, cat_name, cat_path

        raise AssertionError(f"Нет ни одной категории с ≥{min_products} товарами")

    @allure.step("Товары главной страницы")
    def get_featured_products(self) -> List[dict]:
        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located(self.PRODUCT_NAME_LINK)
        )
        seen_ids, products = set(), []
        for link in self.driver.find_elements(*self.PRODUCT_NAME_LINK):
            try:
                href = link.get_attribute("href") or ""
                name = link.text.strip()
                if not href or "product_id" not in href or not name:
                    continue
                pid = href.split("product_id=")[-1].split("&")[0]
                if pid not in seen_ids:
                    seen_ids.add(pid)
                    products.append({"name": name, "product_url": href})
            except Exception:
                continue
        self.attach_text(
            f"Найдено: {len(products)}\n" + "\n".join(p["name"] for p in products),
            "featured_products"
        )
        return products

    @allure.step("Добавить {count} рандомных товаров")
    def add_random_products_to_cart(
        self,
        count: int = 5,
        qty_min: int = 1,
        qty_max: int = 5,
        exclude_names: Optional[set] = None,
    ) -> List[dict]:
        from pages.product_page import ProductPage
        all_products = self.get_featured_products()
        if exclude_names:
            all_products = [p for p in all_products if p["name"] not in exclude_names]
        if len(all_products) < count:
            raise ValueError(f"Недостаточно товаров: {len(all_products)} < {count}")

        pool, added, idx = random.sample(all_products, len(all_products)), [], 0
        while len(added) < count and idx < len(pool):
            product = pool[idx]; idx += 1
            qty = random.randint(qty_min, qty_max)
            try:
                count_before = int(self.driver.find_element(*self.CART_COUNT).text.strip())
            except Exception:
                count_before = len(added)

            with allure.step(f"Добавить «{product['name']}» qty={qty}"):
                self.driver.get(product["product_url"])
                pp = ProductPage(self.driver)
                pp.wait_for_page()
                pp.set_quantity(qty)
                pp.click_add_to_cart()
                try:
                    count_after = int(self.driver.find_element(*self.CART_COUNT).text.strip())
                except Exception:
                    count_after = count_before
                if count_after > count_before:
                    added.append({"name": product["name"], "product_url": product["product_url"], "qty": qty})

        if len(added) < count:
            raise ValueError(f"Не удалось добавить {count} товаров, добавлено: {len(added)}")
        self.open(BASE_URL)
        return added
