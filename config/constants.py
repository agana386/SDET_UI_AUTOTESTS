from selenium.webdriver.common.by import By

# URLs
BASE_URL = "https://automationteststore.com/"
CART_URL = f"{BASE_URL}index.php?rt=checkout/cart"

# Поисковая строка — используется в HomePage
SEARCH_QUERY_SHIRT = "shirt"
SEARCH_INPUT = (By.ID, "filter_keyword")
SEARCH_BUTTON = (By.CSS_SELECTOR, ".button-in-search")
