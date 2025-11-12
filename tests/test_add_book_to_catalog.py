from services.library_service import add_book_to_catalog
from unittest.mock import patch

@patch("services.library_service.get_book_by_isbn")
@patch("services.library_service.insert_book")
def test_add_valid_book(mock_insert, mock_get):
    mock_get.return_value = None
    mock_insert.return_value = True
    ok, msg = add_book_to_catalog("My Book", "Author", "1234567890123", 5)
    assert ok
    assert "added" in msg.lower()

@patch("services.library_service.get_book_by_isbn")
@patch("services.library_service.insert_book")
def test_add_book_no_title(mock_insert, mock_get):
    mock_get.return_value = None
    ok, msg = add_book_to_catalog("", "Author", "1234567890123", 5)
    assert not ok
    assert "title required" in msg.lower()

@patch("services.library_service.get_book_by_isbn")
@patch("services.library_service.insert_book")
def test_add_book_title_long(mock_insert, mock_get):
    mock_get.return_value = None
    name = "ABC" * 500
    ok, msg = add_book_to_catalog(name, "Author", "1234567890123", 5)
    assert not ok
    assert "less than 200" in msg.lower()

@patch("services.library_service.get_book_by_isbn")
@patch("services.library_service.insert_book")
def test_add_book_bad_isbn(mock_insert, mock_get):
    mock_get.return_value = None
    ok, msg = add_book_to_catalog("My Book", "Author", "123456", 5)
    assert not ok
    assert "13 digits" in msg.lower()
