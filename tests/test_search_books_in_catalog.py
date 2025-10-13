import pytest
from library_service import search_books_in_catalog, add_book_to_catalog
from database import init_database

def setup_module(module):
    init_database()
    add_book_to_catalog("Search Book 1", "Author", "1111111111111", 2)
    add_book_to_catalog("Search Book 2", "Author", "2222222222222", 1)

def test_search_name():
    results = search_books_in_catalog("Search Book", "title")
    assert len(results) >= 2
    assert any("Search Book 1" in b['title'] for b in results)
    assert any("Search Book 2" in b['title'] for b in results)

def test_search_by_author():
    results = search_books_in_catalog("author", "author")
    assert len(results) >= 2
    for b in results:
        assert b['author'].lower() == "author"

def test_search_by_isbn():
    results = search_books_in_catalog("1111111111111", "isbn")
    assert len(results) == 1
    assert results[0]['title'] == "Search Book 1"

def test_search_invalid():
    results = search_books_in_catalog("Search Book", "publisher")
    assert results == []