from services.library_service import return_book_by_patron
from unittest.mock import patch

@patch("services.library_service.get_book_by_id")
@patch("services.library_service.update_borrow_record_return_date")
@patch("services.library_service.update_book_availability")
def test_return_valid_book(mock_update_avail, mock_update_record, mock_get):
    mock_get.return_value = {'id': 1, 'title': 'Mock Book'}
    mock_update_record.return_value = True
    mock_update_avail.return_value = True
    ok, msg = return_book_by_patron("123456", 1)
    assert ok
    assert "returned" in msg.lower()

@patch("services.library_service.get_book_by_id")
@patch("services.library_service.update_borrow_record_return_date")
def test_return_not_borrowed(mock_update_record, mock_get):
    mock_get.return_value = {'id': 2}
    mock_update_record.return_value = False
    ok, msg = return_book_by_patron("123456", 2)
    assert not ok
    assert "not borrowed" in msg.lower()

@patch("services.library_service.get_book_by_id")
def test_return_invalid_id(mock_get):
    mock_get.return_value = {'id': 1}
    ok, msg = return_book_by_patron("abb123", 1)
    assert not ok
    assert "invalid id" in msg.lower()

@patch("services.library_service.get_book_by_id")
def test_return_dne_book(mock_get):
    mock_get.return_value = None
    ok, msg = return_book_by_patron("123456", 999)
    assert not ok
    assert "dne" in msg.lower()
