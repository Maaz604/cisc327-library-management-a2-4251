"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books
)

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Allow a patron to borrow a book.
    Implements R3 as per requirements  
    
    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book to borrow
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits."
    
    # Check if book exists and is available
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    
    if book['available_copies'] <= 0:
        return False, "This book is currently not available."
    
    # Check patron's current borrowed books count
    current_borrowed = get_patron_borrow_count(patron_id)
    
    if current_borrowed > 5:
        return False, "You have reached the maximum borrowing limit of 5 books."
    
    # Create borrow record
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    
    # Insert borrow record and update availability
    borrow_success = insert_borrow_record(patron_id, book_id, borrow_date, due_date)
    if not borrow_success:
        return False, "Database error occurred while creating borrow record."
    
    availability_success = update_book_availability(book_id, -1)
    if not availability_success:
        return False, "Database error occurred while updating book availability."
    
    return True, f'Successfully borrowed "{book["title"]}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    """
    Process book return by a patron.
    
    TODO: Implement R4 as per requirements
    """
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."

    success = update_book_availability(book_id, 1)
    if not success:
        return False, "Error occurred while updating book availability."

    record_success = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if not record_success:
        return False, "Error occurred while updating return record."

    return True, f'Book "{book["title"]}" has been successfully returned.'


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    """
    Calculate late fees for a specific book.
    
    TODO: Implement R5 as per requirements 
    

    return { // return the calculated values
        'fee_amount': 0.00,
        'days_overdue': 0,
        'status': 'Late fee calculation not implemented'
    }
    """

    record = update_borrow_record_return_date(patron_id, book_id, None)
    if not record or not record.get('due_date'):
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Borrow record not found'}

    duedate = record['due_date']
    return_date = record.get('return_date', datetime.now())
    days_overdue = (return_date - duedate).days

    if days_overdue <= 0:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'No late fee'}

    amount = round(days_overdue * 0.50, 2)
    return {'fee_amount': amount, 'days_overdue': days_overdue, 'status': 'Late fee applied'}

def search_books_in_catalog(search_term: str, search_type: str) -> List[Dict]:
    """
    Search for books in the catalog.
    
    TODO: Implement R6 as per requirements
    """

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
    
    return []

def get_patron_status_report(patron_id: str) -> Dict:
    """
    Get status report for a patron.
    
    TODO: Implement R7 as per requirements
    """
    count = get_patron_borrow_count(patron_id)
    books = get_all_books()
    borrowedbooks = [b for b in books if b.get("borrowed_by") == patron_id]

    late_fees = []
    total_fees = 0.0
    for b in borrowedbooks:
        fee_data = calculate_late_fee_for_book(patron_id, b["id"])
        late_fees.append({"title": b["title"], "fee": fee_data["fee_amount"]})
        total_fees += fee_data["fee_amount"]

    return {
        "patron id": patron_id,
        "borrowed_books": borrowedbooks,
        "count": count,
        "late fees": late_fees,
        "total fees": round(total_fees, 2)
    }
