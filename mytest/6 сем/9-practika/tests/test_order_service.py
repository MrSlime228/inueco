"""Тесты для OrderService с plain mocks (ложнозелёные)."""
import unittest
from unittest.mock import Mock, patch, create_autospec

# Добавляем путь для импорта
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from order_service import OrderService, Order


class TestOrderServicePlainMock(unittest.TestCase):
    """
    Тесты с обычными моками.
    
    ЭТИ ТЕСТЫ БУДУТ ЗЕЛЁНЫМИ, хотя production-код содержит ошибки!
    Это демонстрирует проблему plain mocks.
    """
    
    @patch("order_service.AuditClient")
    def test_pay_with_plain_mocks(self, MockAuditClient):
        """Тест с plain mocks - будет зелёным, даже если код сломан."""
        # Создаём моки
        repo = Mock()
        payment_gateway = Mock()
        
        # Настраиваем поведение
        mock_order = Order(id=123, amount=5000)
        repo.find_by_id.return_value = mock_order
        
        mock_tx_id = "tx-abc-123"
        payment_gateway.charge.return_value = mock_tx_id
        
        # Создаём сервис и вызываем метод
        service = OrderService(repo, payment_gateway)
        result = service.pay(123)
        
        # Проверяем результат
        self.assertEqual(result, mock_tx_id)
        
        # Проверяем вызовы
        repo.find_by_id.assert_called_once_with(123)
        payment_gateway.charge.assert_called_once_with(total=5000, curr="RUB")
        MockAuditClient.assert_called_once_with("https://audit.local")
        MockAuditClient.return_value.write.assert_called_once_with(
            "payment_ok",
            {"order_id": 123, "tx_id": mock_tx_id}
        )


if __name__ == "__main__":
    unittest.main()

class TestOrderServiceWithAutospec(unittest.TestCase):
    """
    Тесты с autospec.
    
    ЭТИ ТЕСТЫ БУДУТ КРАСНЫМИ, показывая реальные ошибки в коде!
    """
    
    @patch("order_service.AuditClient", autospec=True)
    def test_pay_with_autospec(self, MockAuditClient):
        """
        Тест с autospec - должен упасть, показывая ошибки.
        
        Ожидаем 3 ошибки последовательно:
        1. repo.find_by_id не существует
        2. payment_gateway.charge вызван с неверными аргументами
        3. AuditClient создан с неверными аргументами
        """
        from order_service import OrderRepo, PaymentGateway, AuditClient
        
        # Создаём строгие моки с проверкой контракта
        repo = create_autospec(OrderRepo, instance=True)
        payment_gateway = create_autospec(PaymentGateway, instance=True)
        
        # Настраиваем поведение (используем ПРАВИЛЬНЫЕ имена методов)
        mock_order = Order(id=123, amount=5000)
        # ВНИМАНИЕ: Здесь мы используем get, потому что это правильное имя!
        # Но production-код использует find_by_id - тест должен упасть
        repo.get.return_value = mock_order
        
        mock_tx_id = "tx-abc-123"
        payment_gateway.charge.return_value = mock_tx_id
        
        # Создаём сервис и вызываем метод
        service = OrderService(repo, payment_gateway)
        
        # Этот вызов должен упасть, потому что в коде используется find_by_id
        result = service.pay(123)
        
        # Эти проверки будут выполнены только если код дойдёт до них
        self.assertEqual(result, mock_tx_id)
        repo.get.assert_called_once_with(123)
        payment_gateway.charge.assert_called_once_with(5000, currency="RUB")
        MockAuditClient.assert_called_once_with(
            endpoint="https://audit.local",
            token="secret"
        )
        MockAuditClient.return_value.write.assert_called_once_with(
            "payment_ok",
            {"order_id": 123, "tx_id": mock_tx_id}
        )