import pytest
from unittest.mock import patch
from services.payment_service import PaymentGateway
from datetime import datetime, timedelta
from services.library_service import calculate_late_fee_for_book
from services.library_service import calculate_late_fee_for_book, borrow_book_by_patron, add_book_to_catalog
from database import init_database, get_book_by_isbn
import time

gateway = PaymentGateway()

@patch("services.payment_service.requests.post")
def test_payment_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}
    success, txn_id, msg = gateway.process_payment("123456", 100, "Test payment")
    assert success is True
    assert txn_id.startswith("txn_")
    assert "processed successfully" in msg

@patch("services.payment_service.requests.post")
def test_payment_invalid_amount(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"status": "failed"}
    success, txn_id, msg = gateway.process_payment("123456", 0, "Test zero amount")
    assert success is False
    assert txn_id == ""
    assert "Invalid amount" in msg

@patch("services.payment_service.requests.post")
def test_payment_negative_amount(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"status": "failed"}
    success, txn_id, msg = gateway.process_payment("123456", -50, "Negative test")
    assert success is False
    assert txn_id == ""
    assert "Invalid amount" in msg

@patch("services.payment_service.requests.post")
def test_payment_large_amount(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}
    success, txn_id, msg = gateway.process_payment("123456", 5000, "Over limit test")
    assert success is False
    assert txn_id == ""
    assert "exceeds limit" in msg

@patch("services.payment_service.requests.post")
def test_payment_invalid_patron_id(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"status": "failed"}
    success, txn_id, msg = gateway.process_payment("123", 100, "Bad ID test")
    assert success is False
    assert txn_id == ""
    assert "Invalid patron ID" in msg

@patch("services.payment_service.requests.post")
def test_payment_multiple_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}
    for i in range(3):
        success, txn_id, msg = gateway.process_payment("654321", 10 * (i+1), f"Payment {i}")
        assert success is True
        assert txn_id.startswith("txn_")
        assert "processed successfully" in msg

@patch("services.payment_service.requests.post")
def test_payment_edge_case_small_amount(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}
    success, txn_id, msg = gateway.process_payment("111111", 0.01, "Edge small")
    assert success is True
    assert txn_id.startswith("txn_")
    assert "processed successfully" in msg

@patch("services.payment_service.requests.post")
def test_payment_edge_case_large_valid_amount(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"status": "success"}
    success, txn_id, msg = gateway.process_payment("222222", 999.99, "Edge large valid")
    assert success is True
    assert txn_id.startswith("txn_")
    assert "processed successfully" in msg

@patch("services.payment_service.requests.post")
def test_payment_timeout_simulation(mock_post):
    mock_post.side_effect = TimeoutError("Timeout")
    success, txn_id, msg = gateway.process_payment("333333", 50, "Timeout test")
    assert success is True or success is False  # we just want to ensure no crash

@patch("services.payment_service.requests.post")
def test_payment_multiple_invalid_ids(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.json.return_value = {"status": "failed"}
    invalid_ids = ["12", "1234567", ""]  # only lengths that are invalid
    for pid in invalid_ids:
        success, txn_id, msg = gateway.process_payment(pid, 100, "Invalid ID test")
        assert success is False
        assert txn_id == ""
        assert "Invalid patron ID" in msg

# late fee tests

def setup_function():
    init_database()
    add_book_to_catalog("Late Book", "Author", "1111111111111", 2)
    book = get_book_by_isbn("1111111111111")
    borrow_book_by_patron("123456", book["id"])

def test_late_fee_on_time():
    fee = calculate_late_fee_for_book("123456", 1)
    assert fee['days_overdue'] >= 0
    assert fee['fee_amount'] >= 0
    assert fee['status'] in ["No late fee", "Late fee applied", "Invalid"]

def test_late_fee_late_return():
    fee = calculate_late_fee_for_book("123456", 2)
    assert fee['days_overdue'] >= 0
    assert fee['fee_amount'] >= 0
    assert fee['status'] in ["No late fee", "Late fee applied", "Invalid"]

def test_late_fee_invalid_patron():
    fee = calculate_late_fee_for_book("abc123", 1)
    assert fee['fee_amount'] == 0
    assert "invalid" in fee.get('status', '').lower()

def test_late_fee_invalid_book():
    fee = calculate_late_fee_for_book("123456", 999)
    assert fee['fee_amount'] == 0
    assert "invalid" in fee.get('status', '').lower()

    # more payment tests

def test_refund_invalid_transaction_id():
    success, msg = gateway.refund_payment("", 50)
    assert success is False
    assert "Invalid transaction ID" in msg

    success, msg = gateway.refund_payment("abc123", 50)
    assert success is False
    assert "Invalid transaction ID" in msg

def test_refund_invalid_amount():
    success, msg = gateway.refund_payment("txn_123456_1", 0)
    assert success is False
    assert "Invalid refund amount" in msg

    success, msg = gateway.refund_payment("txn_123456_1", -10)
    assert success is False
    assert "Invalid refund amount" in msg

def test_refund_success():
    transaction_id = f"txn_123456_{int(time.time())}"
    success, msg = gateway.refund_payment(transaction_id, 50)
    assert success is True
    assert "Refund of $50.00 processed successfully" in msg
    assert "Refund ID" in msg

    # some add books to catalog tests

def test_add_book_empty_author():
    success, msg = add_book_to_catalog("Some Title", "", "1234567890123", 1)
    assert success is False
    assert "Author required" in msg

def test_add_book_long_author():
    long_author = "A" * 101
    success, msg = add_book_to_catalog("Some Title", long_author, "1234567890123", 1)
    assert success is False
    assert "less than 100 characters" in msg

def test_add_book_invalid_total_copies():
    success, msg = add_book_to_catalog("Some Title", "Author", "1234567890123", 0)
    assert success is False
    assert "Total copies must be a positive integer" in msg

    success, msg = add_book_to_catalog("Some Title", "Author", "1234567890123", -5)
    assert success is False
    assert "Total copies must be a positive integer" in msg