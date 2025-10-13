import pytest
from library_service import return_book_by_patron, borrow_book_by_patron, add_book_to_catalog
from database import init_database, get_book_by_isbn

def setup_function():
    init_database()
    add_book_to_catalog("Return Book", "Author", "1111111111111", 2)
    add_book_to_catalog("Extra Book", "Author", "2222222222222", 1)

def test_return_valid_book():
    book = get_book_by_isbn("1111111111111")
    borrow_book_by_patron("123456", book["id"])
    ok, msg = return_book_by_patron("123456", book["id"])
    assert ok
    assert "returned" in msg.lower()

def test_return_not_borrowed():
    book = get_book_by_isbn("2222222222222")
    ok, msg = return_book_by_patron("123456", book["id"])
    assert not ok
    assert "not borrowed" in msg.lower()

def test_return_invalid_id():
    book = get_book_by_isbn("1111111111111")
    ok, msg = return_book_by_patron("abb123", book["id"])
    assert not ok
    assert "invalid id" in msg.lower()

def test_return_dne_book():
    ok, msg = return_book_by_patron("123456", 999)
    assert not ok
    assert "dne" in msg.lower()
