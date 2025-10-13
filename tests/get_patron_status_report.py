import pytest
from library_service import get_patron_status_report, borrow_book_by_patron, add_book_to_catalog
from database import init_database, add_sample_data, get_book_by_isbn


def setup_module(module):
    init_database()
    add_sample_data()
    add_book_to_catalog("Status Book 1", "Author", "1111111111111", 2)
    add_book_to_catalog("Status Book 2", "Author", "2222222222222", 1)

    book1 = get_book_by_isbn("1111111111111")
    if book1:
        borrow_book_by_patron("123456", book1['id'])


def test_patron_borrowed():
    status = get_patron_status_report("123456")
    assert 'borrowed_books' in status
    assert len(status['borrowed_books']) >= 1
    assert any(b['title'] == "Status Book 1" for b in status['borrowed_books'])


def test_patron_with_unborrowed():
    status = get_patron_status_report("654321")
    assert 'borrowed_books' in status
    assert len(status['borrowed_books']) == 0


def test_invalid_id():
    status = get_patron_status_report("abc123")
    assert isinstance(status, dict)
    assert status == {} or 'borrowed_books' in status


def test_patron_total_books():
    status = get_patron_status_report("123456")
    assert 'borrowed_books' in status
    assert status.get('total_borrowed', len(status['borrowed_books'])) == len(status['borrowed_books'])
