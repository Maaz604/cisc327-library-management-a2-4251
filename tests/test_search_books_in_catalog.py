import pytest
from library_service import search_books_in_catalog, add_book_to_catalog
from database import init_database, get_book_by_isbn

def setup_module(module):
    init_database()
    add_book_to_catalog("Search Book 1", "Author", "1111111111111", 2)
    add_book_to_catalog("Search Book 2", "Author", "2222222222222", 1)

def test_search_name():
    results = search_books_in_catalog("Search Book", "title")
    assert len(results) >= 2
    titles = [b['title'] for b in results]
    assert "Search Book 1" in titles
    assert "Search Book 2" in titles

def test_search_by_author():
    results = search_books_in_catalog("author", "author")
    assert len(results) >= 2
    for b in results:
        assert b['author'].lower() == "author"

def test_search_by_isbn():
    book = get_book_by_isbn("1111111111111")
    results = search_books_in_catalog(book['isbn'], "isbn")
    assert len(results) == 1
    assert results[0]['title'] == "Search Book 1"

def test_search_invalid():
    results = search_books_in_catalog("Search Book", "publisher")
    assert results == []
