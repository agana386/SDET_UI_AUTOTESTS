import pytest
from pages.home_page import HomePage
from pages.category_page import CategoryPage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
 
 
@pytest.fixture
def home_page(driver):
    return HomePage(driver)
 
 
@pytest.fixture
def cart_page(driver):
    return CartPage(driver)
 
 
@pytest.fixture
def category_page(driver):
    return CategoryPage(driver)
 
 
@pytest.fixture
def product_page(driver):
    return ProductPage(driver)
