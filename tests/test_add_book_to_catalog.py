import pytest
from library_service import add_book_to_catalog

def test_add_valid_book():
    ok, msg = add_book_to_catalog("My Book", "Author", "1234567890123", 5)
    assert ok
    assert "added" in msg.lower()

def test_add_book_no_title():
    ok, msg = add_book_to_catalog("", "Author", "1234567890123", 5)
    assert not ok
    assert "title required" in msg.lower()

def test_add_book_title_long():
    name = "ABC" * 500
    ok, msg = add_book_to_catalog(name, "Author", "1234567890123", 5)
    assert not ok
    assert "less than 200" in msg.lower()

def test_add_book_bad_isbn():
    ok, msg = add_book_to_catalog("My Book", "Author", "123456", 5)
    assert not ok
    assert "13 digits" in msg.lower()
