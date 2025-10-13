import pytest
from library_service import calculate_late_fee_for_book, borrow_book_by_patron, add_book_to_catalog
from database import init_database


def setup_module(module):
    init_database()
    add_book_to_catalog("Late Book", "Author", "1111111111111", 2)
    borrow_book_by_patron("123456", 1)

def test_late_fee():
    fee = calculate_late_fee_for_book("123456", 1)
    assert fee['amount'] == 0
    assert fee['days_overdue'] == 0

def test_late_fee_overdue():
    fee = calculate_late_fee_for_book("123456", 1)
    assert isinstance(fee['amount'], (int, float))
    assert fee['days_overdue'] >= 0

def test_late_fee_invalid_id():
    fee = calculate_late_fee_for_book("abc123", 1)
    assert fee['fee_amount'] == 0
    assert "invalid" in fee.get('status', '').lower()

def test_late_fee_invalid_book():
    fee = calculate_late_fee_for_book("123456", 999)
    assert fee['fee_amount'] == 0
    assert "invalid" in fee.get('status', '').lower()

