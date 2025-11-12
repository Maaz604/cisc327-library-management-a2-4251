from services.library_service import search_books_in_catalog
from unittest.mock import patch

@patch("services.library_service.get_all_books")
def test_search_name(mock_get_all):
    mock_get_all.return_value = [
        {'id': 1, 'title': 'Search Book 1', 'author': 'Author', 'isbn': '1111111111111'},
        {'id': 2, 'title': 'Search Book 2', 'author': 'Author', 'isbn': '2222222222222'}
    ]
    results = search_books_in_catalog("Search Book", "title")
    assert len(results) >= 2
    titles = [b['title'] for b in results]
    assert "Search Book 1" in titles
    assert "Search Book 2" in titles

@patch("services.library_service.get_all_books")
def test_search_by_author(mock_get_all):
    mock_get_all.return_value = [
        {'id': 1, 'title': 'Search Book 1', 'author': 'Author', 'isbn': '1111111111111'},
        {'id': 2, 'title': 'Search Book 2', 'author': 'Author', 'isbn': '2222222222222'}
    ]
    results = search_books_in_catalog("author", "author")
    assert len(results) >= 2
    for b in results:
        assert b['author'].lower() == "author"

@patch("services.library_service.get_all_books")
def test_search_by_isbn(mock_get_all):
    mock_get_all.return_value = [
        {'id': 1, 'title': 'Search Book 1', 'author': 'Author', 'isbn': '1111111111111'},
        {'id': 2, 'title': 'Search Book 2', 'author': 'Author', 'isbn': '2222222222222'}
    ]
    results = search_books_in_catalog("1111111111111", "isbn")
    assert len(results) == 1
    assert results[0]['title'] == "Search Book 1"

@patch("services.library_service.get_all_books")
def test_search_invalid(mock_get_all):
    mock_get_all.return_value = []
    results = search_books_in_catalog("Search Book", "publisher")
    assert results == []
