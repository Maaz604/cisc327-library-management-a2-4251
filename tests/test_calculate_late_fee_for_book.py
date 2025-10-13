import pytest
from library_service import calculate_late_fee_for_book, borrow_book_by_patron, add_book_to_catalog
from database import init_database, get_book_by_isbn

def setup_function():
    init_database()
    add_book_to_catalog("Late Book", "Author", "1111111111111", 2)
    book = get_book_by_isbn("1111111111111")
    borrow_book_by_patron("123456", book["id"])

def test_late_fee():
    book = get_book_by_isbn("1111111111111")
    fee = calculate_late_fee_for_book("123456", book["id"])
    assert fee['amount'] == 0
    assert fee['days_overdue'] == 0

def test_late_fee_overdue():
    book = get_book_by_isbn("1111111111111")
    fee = calculate_late_fee_for_book("123456", book["id"])
    assert isinstance(fee['amount'], (int, float))
    assert fee['days_overdue'] >= 0

def test_late_fee_invalid_id():
    book = get_book_by_isbn("1111111111111")
    fee = calculate_late_fee_for_book("abc123", book["id"])
    assert fee['amount'] == 0
    assert "invalid" in fee.get('status', '').lower()

def test_late_fee_invalid_book():
    fee = calculate_late_fee_for_book("123456", 999)
    assert fee['amount'] == 0
    assert "invalid" in fee.get('status', '').lower()