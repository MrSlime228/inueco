import unittest
from unittest.mock import Mock, call

from app.invoice_service import InvoiceService, Invoice, ChargeResult


class TestInvoiceService(unittest.TestCase):
    """Тесты для InvoiceService с моками зависимостей"""
    
    def setUp(self):
        """Создаём моки и сервис перед каждым тестом"""
        self.invoice_repo = Mock()
        self.payment_gateway = Mock()
        self.service = InvoiceService(self.invoice_repo, self.payment_gateway)
    
    # ========== HAPPY PATH ==========
    
    def test_pay_success(self):
        """Успешная оплата: платёж успешен → статус "paid" """
        # Подготовка (Arrange)
        invoice = Invoice(id=1, customer_id="cus_42", amount=1000, status="pending")
        self.invoice_repo.get_by_id.return_value = invoice
        self.payment_gateway.charge.return_value = ChargeResult(ok=True, transaction_id="tx_123")
        
        # Действие (Act)
        result = self.service.pay(invoice_id=1)
        
        # Проверка (Assert)
        self.assertEqual(result, "paid")
        self.invoice_repo.get_by_id.assert_called_once_with(1)
        self.payment_gateway.charge.assert_called_once_with(customer_id="cus_42", amount=1000)
        self.invoice_repo.mark_paid.assert_called_once_with(1, "tx_123")
        self.invoice_repo.mark_failed.assert_not_called()
        self.invoice_repo.mark_retry.assert_not_called()
    
    # ========== ОШИБКИ ПЛАТЕЖА ==========
    
    def test_pay_declined(self):
        """Платёж отклонён → статус "failed", сохраняем причину"""
        invoice = Invoice(id=2, customer_id="cus_99", amount=500, status="pending")
        self.invoice_repo.get_by_id.return_value = invoice
        self.payment_gateway.charge.return_value = ChargeResult(ok=False, reason="insufficient_funds")
        
        result = self.service.pay(invoice_id=2)
        
        self.assertEqual(result, "failed")
        self.payment_gateway.charge.assert_called_once()
        self.invoice_repo.mark_failed.assert_called_once_with(2, "insufficient_funds")
        self.invoice_repo.mark_paid.assert_not_called()
        self.invoice_repo.mark_retry.assert_not_called()
    
    def test_pay_timeout(self):
        """Таймаут шлюза → статус "retry", помечаем на повтор"""
        invoice = Invoice(id=3, customer_id="cus_77", amount=200, status="pending")
        self.invoice_repo.get_by_id.return_value = invoice
        self.payment_gateway.charge.side_effect = TimeoutError("gateway timeout")
        
        result = self.service.pay(invoice_id=3)
        
        self.assertEqual(result, "retry")
        self.payment_gateway.charge.assert_called_once()
        self.invoice_repo.mark_retry.assert_called_once_with(3)
        self.invoice_repo.mark_paid.assert_not_called()
        self.invoice_repo.mark_failed.assert_not_called()
    
    # ========== БИЗНЕС-ПРОВЕРКИ ==========
    
    def test_pay_already_paid(self):
        """Счёт уже оплачен → не вызываем шлюз, возвращаем "already_paid" """
        invoice = Invoice(id=4, customer_id="cus_55", amount=300, status="paid")
        self.invoice_repo.get_by_id.return_value = invoice
        
        result = self.service.pay(invoice_id=4)
        
        self.assertEqual(result, "already_paid")
        self.payment_gateway.charge.assert_not_called()
        self.invoice_repo.mark_paid.assert_not_called()
        self.invoice_repo.mark_failed.assert_not_called()
        self.invoice_repo.mark_retry.assert_not_called()
    
    def test_pay_invoice_not_found(self):
        """Счёт не найден → LookupError, не вызываем шлюз"""
        self.invoice_repo.get_by_id.return_value = None
        
        with self.assertRaises(LookupError) as context:
            self.service.pay(invoice_id=999)
        
        self.assertEqual(str(context.exception), "invoice not found")
        self.payment_gateway.charge.assert_not_called()
        self.invoice_repo.mark_paid.assert_not_called()
    
    def test_pay_zero_amount(self):
        """Сумма <= 0 → ValueError, не вызываем шлюз"""
        invoice = Invoice(id=5, customer_id="cus_33", amount=0, status="pending")
        self.invoice_repo.get_by_id.return_value = invoice
        
        with self.assertRaises(ValueError) as context:
            self.service.pay(invoice_id=5)
        
        self.assertEqual(str(context.exception), "amount must be positive")
        self.payment_gateway.charge.assert_not_called()
    
    def test_pay_negative_amount(self):
        """Отрицательная сумма → ValueError"""
        invoice = Invoice(id=6, customer_id="cus_11", amount=-100, status="pending")
        self.invoice_repo.get_by_id.return_value = invoice
        
        with self.assertRaises(ValueError):
            self.service.pay(invoice_id=6)
        
        self.payment_gateway.charge.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)