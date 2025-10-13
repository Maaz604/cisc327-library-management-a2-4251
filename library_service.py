"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from database import (
    get_book_by_id,
    get_book_by_isbn,
    get_patron_borrow_count,
    insert_book,
    insert_borrow_record,
    update_book_availability,
    update_borrow_record_return_date,
    get_all_books
)


def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    if not title or not title.strip():
        return False, "Title required."

    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."

    if not author or not author.strip():
        return False, "Author required."

    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."

    if len(isbn) != 13 or not isbn.isdigit():
        return False, "ISBN must be exactly 13 digits."

    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."

    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "Book already exists."

    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error while adding book."


def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid ID"

    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not locateda"

    if book['available_copies'] <= 0:
        return False, "Book not available"

    current_borrowed = get_patron_borrow_count(patron_id)
    if current_borrowed >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."

    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)

    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error while creating borrow record."

    update_book_availability(book_id, -1)
    return True, f'Successfully borrowed "{book["title"]}".'


def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid ID"

    book = get_book_by_id(book_id)
    if not book:
        return False, "Book DNE"

    record_success = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if not record_success:
        return False, "Not borrowed"

    update_book_availability(book_id, 1)
    return True, f'Book "{book["title"]}" has been successfully returned.'


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {'amount': 0.00, 'days_overdue': 0, 'status': 'Invalid'}

    book = get_book_by_id(book_id)
    if not book:
        return {'amount': 0.00, 'days_overdue': 0, 'status': 'Invalid'}

    record = update_borrow_record_return_date(patron_id, book_id, None)
    if not record or not record.get('due_date'):
        return {'amount': 0.00, 'days_overdue': 0, 'status': 'Invalid'}

    duedate = record['due_date']
    return_date = record.get('return_date', datetime.now())
    days_overdue = max((return_date - duedate).days, 0)
    fee_amount = round(days_overdue * 0.50, 2) if days_overdue > 0 else 0
    status = "Late fee applied" if days_overdue > 0 else "No late fee"

    return {'amount': fee_amount, 'days_overdue': days_overdue, 'status': status}


def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    books = get_all_books()
    terms = search_term.strip().lower()
    results = []

    for book in books:
        if search_type == "title" and terms in book["title"].lower():
            results.append(book)
        elif search_type == "author" and terms in book["author"].lower():
            results.append(book)
        elif search_type == "isbn" and terms in book["isbn"].lower():
            results.append(book)

    return results


def get_patron_status_report(patron_id: str) -> Dict:
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return {}

    count = get_patron_borrow_count(patron_id)
    books = get_all_books()
    borrowedbooks = [b for b in books if b.get("borrowed_by") == patron_id]

    late_fees = []
    total_fees = 0.0
    for b in borrowedbooks:
        fee_data = calculate_late_fee_for_book(patron_id, b["id"])
        late_fees.append({"title": b["title"], "fee": fee_data["amount"]})
        total_fees += fee_data["amount"]

    return {
        "patron id": patron_id,
        "borrowed_books": borrowedbooks,
        "count": count,
        "late fees": late_fees,
        "total fees": round(total_fees, 2)
    }