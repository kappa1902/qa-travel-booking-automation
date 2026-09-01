import requests
import pytest
from tests.db_helper import get_last_payment_status, get_last_credit_status, clear_db


BASE_URL = "http://localhost:8080"

@pytest.fixture(autouse=True)
def clean_database():
    clear_db()

VALID_APPROVED_CARD = {
    "number": "4444 4444 4444 4441",
    "year": "27",
    "month": "08",
    "holder": "IVAN IVANOV",
    "cvc": "123"
}

VALID_DECLIVED_CARD = {
    "number": "4444 4444 4444 4442",
    "year": "27",
    "month": "08",
    "holder": "IVAN IVANOV",
    "cvc": "123"
}

### ----- Тесты обычной оплаты -----

def test_api_valid_approved_card():
    response = requests.post(f"{BASE_URL}/api/v1/pay", json=VALID_APPROVED_CARD)
    assert response.status_code == 200
    assert response.json().get("status") == "APPROVED"
    assert get_last_payment_status() == "APPROVED"

def test_pay_valid_declined_card():
    response = requests.post(f"{BASE_URL}/api/v1/pay", json=VALID_DECLIVED_CARD)
    assert response.status_code == 200
    assert response.json().get("status") == "DECLINED"
    assert get_last_payment_status() == "DECLINED"

### ----- Тесты покупки в кредит -----

def test_credit_valid_approved_card():
    response = requests.post(f"{BASE_URL}/api/v1/credit", json=VALID_APPROVED_CARD)
    assert response.status_code == 200
    assert response.json().get("status") == "APPROVED"
    assert get_last_credit_status() == "APPROVED"

def test_credit_valid_declined_card():
    response = requests.post(f"{BASE_URL}/api/v1/credit", json=VALID_DECLIVED_CARD)
    assert response.status_code == 200
    assert response.json().get("status") == "DECLINED"
    assert get_last_credit_status() == "DECLINED"