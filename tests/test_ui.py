import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tests.db_helper import clear_db, get_last_payment_status, get_last_credit_status

URL = "http://localhost:8080"

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.fixture(autouse=True)
def clean_database():
    clear_db()


def fill_form(driver, number, month, year, holder, cvc):
    driver.find_element(By.XPATH, "//input[@placeholder='0000 0000 0000 0000']").send_keys(number)
    driver.find_element(By.XPATH, "//input[@placeholder='08']").send_keys(month)
    driver.find_element(By.XPATH, "//input[@placeholder='22']").send_keys(year)
    driver.find_element(By.XPATH, "//span[text()='Владелец']/following-sibling::span/input").send_keys(holder)
    driver.find_element(By.XPATH, "//input[@placeholder='999']").send_keys(cvc)
    driver.find_element(By.XPATH, "//span[text()='Продолжить']/ancestor::button").click()


### --- Позитивные UI сценарии ---

def test_ui_pay_approved_card(driver):
    driver.get(URL)
    driver.find_element(By.XPATH, "//span[text()='Купить']/ancestor::button").click()
    fill_form(driver, "4444 4444 4444 4441", "08", "27", "IVAN IVANOV", "123")

    notification = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'notification_status_ok')]"))
    )
    assert "операция одобрена банком" in notification.text.lower()
    assert get_last_payment_status() == "APPROVED"


def test_ui_credit_approved_card(driver):
    driver.get(URL)
    driver.find_element(By.XPATH, "//span[text()='Купить в кредит']/ancestor::button").click()
    fill_form(driver, "4444 4444 4444 4441", "08", "27", "IVAN IVANOV", "123")

    notification = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'notification_status_ok')]"))
    )
    assert "операция одобрена банком" in notification.text.lower()
    assert get_last_credit_status() == "APPROVED"


### --- Негативные UI сценарии ---
@pytest.mark.xfail
def test_ui_pay_declined_card(driver):
    driver.get(URL)
    driver.find_element(By.XPATH, "//span[text()='Купить']/ancestor::button").click()
    fill_form(driver, "4444 4444 4444 4442", "08", "27", "IVAN IVANOV", "123")

    notification = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(@class, 'notification_status_error')]"))
    )
    assert "ошибка! банк отказал в проведении операции" in notification.text.lower()
    assert get_last_payment_status() == "DECLINED"


def test_ui_empty_form_validation(driver):
    driver.get(URL)
    driver.find_element(By.XPATH, "//span[text()='Купить']/ancestor::button").click()
    driver.find_element(By.XPATH, "//span[text()='Продолжить']/ancestor::button").click()

    error_messages = driver.find_elements(By.XPATH, "//*[contains(@class, 'input__sub')]")
    assert len(error_messages) > 0