import pytest
from library_service import return_book_by_patron, borrow_book_by_patron, add_book_to_catalog
from database import init_database

def setup_module(module):
    init_database()
    add_book_to_catalog("Return Book", "Author", "1111111111111", 2)
    borrow_book_by_patron("123456", 1)

def test_return_valid_book():
    ok, msg = return_book_by_patron("123456", 1)
    assert ok
    assert "returned" in msg.lower()

def test_return_not_borrowed():
    ok, msg = return_book_by_patron("123456", 2)
    assert not ok
    assert "ot borrowed" in msg.lower()

def test_return_invalid_id():
    ok, msg = return_book_by_patron("abb123", 1)
    assert not ok
    assert "invalid id" in msg.lower()

def test_return_dne_book():
    ok, msg = return_book_by_patron("123456", 999)
    assert not ok
    assert "Book DNE" in msg.lower()
