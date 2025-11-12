"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

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

from services.payment_service import PaymentGateway


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
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid'}

    book = get_book_by_id(book_id)
    if not book:
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid'}

    record = update_borrow_record_return_date(patron_id, book_id, None)
    if not record or not record.get('due_date'):
        return {'fee_amount': 0.00, 'days_overdue': 0, 'status': 'Invalid'}

    duedate = record['due_date']
    return_date = record.get('return_date', datetime.now())
    days_overdue = max((return_date - duedate).days, 0)
    fee_amount = round(days_overdue * 0.50, 2) if days_overdue > 0 else 0
    status = "Late fee applied" if days_overdue > 0 else "No late fee"

    return {'fee_amount': fee_amount, 'days_overdue': days_overdue, 'status': status}


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


def pay_late_fees(patron_id: str, book_id: int, payment_gateway: PaymentGateway = None) -> Tuple[
    bool, str, Optional[str]]:
    """
    Process payment for late fees using external payment gateway.

    NEW FEATURE FOR ASSIGNMENT 3: Demonstrates need for mocking/stubbing
    This function depends on an external payment service that should be mocked in tests.

    Args:
        patron_id: 6-digit library card ID
        book_id: ID of the book with late fees
        payment_gateway: Payment gateway instance (injectable for testing)

    Returns:
        tuple: (success: bool, message: str, transaction_id: Optional[str])

    Example for you to mock:
        # In tests, mock the payment gateway:
        mock_gateway = Mock(spec=PaymentGateway)
        mock_gateway.process_payment.return_value = (True, "txn_123", "Success")
        success, msg, txn = pay_late_fees("123456", 1, mock_gateway)
    """
    # Validate patron ID
    if not patron_id or not patron_id.isdigit() or len(patron_id) != 6:
        return False, "Invalid patron ID. Must be exactly 6 digits.", None

    # Calculate late fee first
    fee_info = calculate_late_fee_for_book(patron_id, book_id)

    # Check if there's a fee to pay
    if not fee_info or 'fee_amount' not in fee_info:
        return False, "Unable to calculate late fees.", None

    fee_amount = fee_info.get('fee_amount', 0.0)

    if fee_amount <= 0:
        return False, "No late fees to pay for this book.", None

    # Get book details for payment description
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found.", None

    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()

    # Process payment through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN THEIR TESTS!
    try:
        success, transaction_id, message = payment_gateway.process_payment(
            patron_id=patron_id,
            amount=fee_amount,
            description=f"Late fees for '{book['title']}'"
        )

        if success:
            return True, f"Payment successful! {message}", transaction_id
        else:
            return False, f"Payment failed: {message}", None

    except Exception as e:
        # Handle payment gateway errors
        return False, f"Payment processing error: {str(e)}", None


def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway: PaymentGateway = None) -> Tuple[
    bool, str]:
    """
    Refund a late fee payment (e.g., if book was returned on time but fees were charged in error).

    NEW FEATURE FOR ASSIGNMENT 3: Another function requiring mocking

    Args:
        transaction_id: Original transaction ID to refund
        amount: Amount to refund
        payment_gateway: Payment gateway instance (injectable for testing)

    Returns:
        tuple: (success: bool, message: str)
    """
    # Validate inputs
    if not transaction_id or not transaction_id.startswith("txn_"):
        return False, "Invalid transaction ID."

    if amount <= 0:
        return False, "Refund amount must be greater than 0."

    if amount > 15.00:  # Maximum late fee per book
        return False, "Refund amount exceeds maximum late fee."

    # Use provided gateway or create new one
    if payment_gateway is None:
        payment_gateway = PaymentGateway()

    # Process refund through external gateway
    # THIS IS WHAT YOU SHOULD MOCK IN YOUR TESTS!
    try:
        success, message = payment_gateway.refund_payment(transaction_id, amount)

        if success:
            return True, message
        else:
            return False, f"Refund failed: {message}"

    except Exception as e:
        return False, f"Refund processing error: {str(e)}"