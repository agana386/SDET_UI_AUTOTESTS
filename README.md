# UI Autotests. Practice Automation Form Fields

Проект UI-автотестов на Python + Selenium WebDriver + PyTest + Allure.
Тестирование функциональности сайта https://automationteststore.com/.

## Стек

- Python 3.10+
- Selenium WebDriver 4 (Chrome)
- PyTest 8
- PyTest-xdist 3.5
- Allure-pytest
- webdriver-manager

## Структура проекта

```
SDET_UI_AUTOTESTS/
├── conftest.py          
├── pytest.ini           
├── requirements.txt     
├── config/constants.py
├── .gitignore
├── README.md
├── pages/
│   ├── base_page.py
│   ├── home_page.py
│   ├── category_page.py
│   ├── product_page.py
│   ├── search_results_page.py
│   └── cart_page.py
└── tests/
    ├── test_skincare_sorting.py
    ├── test_search_shirt_sorting.py
    └── test_cart_random_products.py

```

## Паттерны проектирования

| Паттерн | Реализация |
|---|---|
| **Page Object Model** | `FormPage` содержит только методы взаимодействия; тесты — в `tests/` |
| **Page Factory** | Локаторы реализованы как `@property` в `FormPage` — элемент ищется в DOM в момент обращения |
| **Fluent Interface** | Каждый action-метод возвращает `self`, что позволяет строить цепочки вызовов в тесте |

## Установка и запуск

```bash
python -m venv venv
source venv/bin/activate       
pip install -r requirements.txt
pytest -v -s
# Открыть отчет
allure serve allure-results
```

## Allure Report
![Allure](./Allure_result.png)

