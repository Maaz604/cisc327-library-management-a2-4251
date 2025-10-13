import pytest
from library_service import borrow_book_by_patron, add_book_to_catalog
from database import init_database

def setup_module(module):
    init_database()
    add_book_to_catalog("Borrow Book", "Author", "9999999999999", 2)

def test_borrow_ok():
    ok, msg = borrow_book_by_patron("123456", 1)
    assert ok
    assert "borrowed" in msg.lower()

def test_borrow_invalid_id():
    ok, msg = borrow_book_by_patron("abc123", 1)
    assert not ok
    assert "invalid id" in msg.lower()

def test_borrow_missing_book():
    ok, msg = borrow_book_by_patron("123456", 999)
    assert not ok
    assert "book not locateda" in msg.lower()

def test_borrow_out_of_stock():
    borrow_book_by_patron("654321", 1)
    ok, msg = borrow_book_by_patron("123456", 1)
    assert not ok
    assert " not available" in msg.lower()

