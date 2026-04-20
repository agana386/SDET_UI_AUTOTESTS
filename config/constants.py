from selenium.webdriver.common.by import By

BASE_URL            = "https://automationteststore.com/"
SKINCARE_FACE_URL   = f"{BASE_URL}index.php?rt=product/category&path=43_46"
CART_URL            = f"{BASE_URL}index.php?rt=checkout/cart"

SEARCH_QUERY_SHIRT  = "shirt"
SEARCH_INPUT        = (By.ID, "filter_keyword")
SEARCH_BUTTON       = (By.CSS_SELECTOR, ".button-in-search")

SORT_NAME_AZ        = "pd.name-ASC"
SORT_NAME_ZA        = "pd.name-DESC"
SORT_PRICE_LOW_HIGH = "p.price-ASC"
SORT_PRICE_HIGH_LOW = "p.price-DESC"

LIST_VIEW_BTN       = (By.ID, "list")
SORT_DROPDOWN       = (By.ID, "sort")
