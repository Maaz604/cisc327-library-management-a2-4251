from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway
from unittest.mock import Mock, patch
import pytest

# pay_late_fees tests

def test_pay_late_fees_success():
    fake_gateway = Mock(spec=PaymentGateway)
    fake_gateway.process_payment.return_value = (True, "txn_123", "Success")

    # Patch calculate_late_fee_for_book to return a positive fee
    with patch("services.library_service.calculate_late_fee_for_book") as mock_fee:
        mock_fee.return_value = {'fee_amount': 5.0, 'days_overdue': 2, 'status': 'Late fee applied'}
        with patch("services.library_service.get_book_by_id") as mock_book:
            mock_book.return_value = {'id': 1, 'title': 'Some Book'}
            ok, msg, txn = pay_late_fees("123456", 1, fake_gateway)

    assert ok
    assert "Payment successful" in msg
    assert txn == "txn_123"


def test_pay_late_fees_declined():
    fake_gateway = Mock(spec=PaymentGateway)
    fake_gateway.process_payment.return_value = (False, None, "Card declined")

    with patch("services.library_service.calculate_late_fee_for_book") as mock_fee:
        mock_fee.return_value = {'fee_amount': 5.0, 'days_overdue': 2, 'status': 'Late fee applied'}
        with patch("services.library_service.get_book_by_id") as mock_book:
            mock_book.return_value = {'id': 1, 'title': 'Some Book'}
            ok, msg, txn = pay_late_fees("123456", 1, fake_gateway)

    assert not ok
    assert "Payment failed" in msg
    assert txn is None


def test_pay_late_fees_invalid_patron():
    fake_gateway = Mock(spec=PaymentGateway)
    ok, msg, txn = pay_late_fees("abc", 1, fake_gateway)
    assert not ok
    assert "Invalid patron ID" in msg
    assert txn is None


def test_pay_late_fees_zero_fee():
    fake_gateway = Mock(spec=PaymentGateway)
    with patch("services.library_service.calculate_late_fee_for_book") as mock_fee:
        mock_fee.return_value = {'fee_amount': 0.0, 'days_overdue': 0, 'status': 'No late fee'}
        ok, msg, txn = pay_late_fees("123456", 1, fake_gateway)

    assert not ok
    assert "No late fees" in msg
    assert txn is None


def test_pay_late_fees_network_error():
    fake_gateway = Mock(spec=PaymentGateway)
    fake_gateway.process_payment.side_effect = Exception("Network error")

    with patch("services.library_service.calculate_late_fee_for_book") as mock_fee:
        mock_fee.return_value = {'fee_amount': 5.0, 'days_overdue': 2, 'status': 'Late fee applied'}
        with patch("services.library_service.get_book_by_id") as mock_book:
            mock_book.return_value = {'id': 1, 'title': 'Some Book'}
            ok, msg, txn = pay_late_fees("123456", 1, fake_gateway)

    assert not ok
    assert "Payment processing error" in msg
    assert txn is None


# refund_late_fee_payment tests

def test_refund_late_fee_success():
    fake_gateway = Mock(spec=PaymentGateway)
    fake_gateway.refund_payment.return_value = (True, "Refunded")
    ok, msg = refund_late_fee_payment("txn_123", 5.0, fake_gateway)
    assert ok
    assert "Refunded" in msg


def test_refund_late_fee_invalid_txn():
    fake_gateway = Mock(spec=PaymentGateway)
    fake_gateway.refund_payment.return_value = (False, "Invalid transaction")
    ok, msg = refund_late_fee_payment("txn_123", 5.0, fake_gateway)
    assert not ok
    assert "Invalid transaction" in msg
    fake_gateway.refund_payment.assert_called_once_with("txn_123", 5.0)


def test_refund_late_fee_invalid_amount():
    fake_gateway = Mock(spec=PaymentGateway)
    for amt in [-5, 0, 20]:
        ok, msg = refund_late_fee_payment("txn_123", amt, fake_gateway)
        assert not ok
        assert "greater than 0" in msg or "exceeds" in msg

