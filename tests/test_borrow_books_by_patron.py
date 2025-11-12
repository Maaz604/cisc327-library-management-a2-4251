from services.library_service import borrow_book_by_patron
from unittest.mock import patch

@patch("services.library_service.get_book_by_id")
@patch("services.library_service.insert_borrow_record")
@patch("services.library_service.update_book_availability")
def test_borrow_ok(mock_update, mock_insert, mock_get):
    mock_get.return_value = {'id': 1, 'title': 'Mock Book', 'available_copies': 1}
    mock_insert.return_value = True
    mock_update.return_value = True
    ok, msg = borrow_book_by_patron("123456", 1)
    assert ok
    assert "borrowed" in msg.lower()

@patch("services.library_service.get_book_by_id")
def test_borrow_invalid_id(mock_get):
    mock_get.return_value = {'id': 1, 'available_copies': 1}
    ok, msg = borrow_book_by_patron("abc123", 1)
    assert not ok
    assert "invalid id" in msg.lower()

@patch("services.library_service.get_book_by_id")
def test_borrow_missing_book(mock_get):
    mock_get.return_value = None
    ok, msg = borrow_book_by_patron("123456", 999)
    assert not ok
    assert "book not located" in msg.lower()

@patch("services.library_service.get_book_by_id")
@patch("services.library_service.insert_borrow_record")
@patch("services.library_service.update_book_availability")
def test_borrow_out_of_stock(mock_update, mock_insert, mock_get):
    mock_get.return_value = {'id': 1, 'title': 'Mock Book', 'available_copies': 0}
    ok, msg = borrow_book_by_patron("111111", 1)
    assert not ok
    assert "not available" in msg.lower()
