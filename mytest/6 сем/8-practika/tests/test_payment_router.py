import unittest
from unittest.mock import Mock, patch

from app.payment_router import choose_payment_mode, charge_order


class TestChoosePaymentMode(unittest.TestCase):
    """Тесты для функции выбора режима оплаты"""
    
    def test_default_prod_mode(self):
        """По умолчанию (нет переменных) → "gateway" """
        with patch.dict("os.environ", {}, clear=True):
            result = choose_payment_mode()
        
        self.assertEqual(result, "gateway")
    
    def test_dev_mode(self):
        """PAYMENT_ENV=dev → "sandbox" """
        with patch.dict("os.environ", {"PAYMENT_ENV": "dev"}, clear=True):
            result = choose_payment_mode()
        
        self.assertEqual(result, "sandbox")
    
    def test_test_mode(self):
        """PAYMENT_ENV=test → "sandbox" """
        with patch.dict("os.environ", {"PAYMENT_ENV": "test"}, clear=True):
            result = choose_payment_mode()
        
        self.assertEqual(result, "sandbox")
    
    def test_prod_mode_explicit(self):
        """PAYMENT_ENV=prod → "gateway" """
        with patch.dict("os.environ", {"PAYMENT_ENV": "prod"}, clear=True):
            result = choose_payment_mode()
        
        self.assertEqual(result, "gateway")
    
    def test_dry_run_mode(self):
        """PAYMENT_DRY_RUN=1 → "dry-run" (игнорирует PAYMENT_ENV) """
        with patch.dict("os.environ", {
            "PAYMENT_ENV": "prod",
            "PAYMENT_DRY_RUN": "1"
        }, clear=True):
            result = choose_payment_mode()
        
        self.assertEqual(result, "dry-run")
    
    def test_unsupported_env(self):
        """Неподдерживаемое значение PAYMENT_ENV → ValueError """
        with patch.dict("os.environ", {"PAYMENT_ENV": "staging"}, clear=True):
            with self.assertRaises(ValueError) as context:
                choose_payment_mode()
        
        self.assertEqual(str(context.exception), "unsupported payment env: staging")


class TestChargeOrder(unittest.TestCase):
    """Тесты для функции оплаты заказа"""
    
    def setUp(self):
        """Создаём моки перед каждым тестом"""
        self.sandbox_client = Mock()
        self.gateway_client = Mock()
    
    def test_gateway_mode_by_default(self):
        """По умолчанию → вызов gateway_client, НЕ вызов sandbox_client"""
        with patch.dict("os.environ", {}, clear=True):
            result = charge_order(
                amount=1000,
                sandbox_client=self.sandbox_client,
                gateway_client=self.gateway_client
            )
        
        self.assertEqual(result, "gateway")
        self.gateway_client.charge.assert_called_once_with(1000)
        self.sandbox_client.charge.assert_not_called()
    
    def test_sandbox_mode_in_dev(self):
        """PAYMENT_ENV=dev → вызов sandbox_client, НЕ вызов gateway_client"""
        with patch.dict("os.environ", {"PAYMENT_ENV": "dev"}, clear=True):
            result = charge_order(
                amount=500,
                sandbox_client=self.sandbox_client,
                gateway_client=self.gateway_client
            )
        
        self.assertEqual(result, "sandbox")
        self.sandbox_client.charge.assert_called_once_with(500)
        self.gateway_client.charge.assert_not_called()
    
    def test_sandbox_mode_in_test(self):
        """PAYMENT_ENV=test → вызов sandbox_client"""
        with patch.dict("os.environ", {"PAYMENT_ENV": "test"}, clear=True):
            result = charge_order(
                amount=750,
                sandbox_client=self.sandbox_client,
                gateway_client=self.gateway_client
            )
        
        self.assertEqual(result, "sandbox")
        self.sandbox_client.charge.assert_called_once_with(750)
        self.gateway_client.charge.assert_not_called()
    
    def test_dry_run_mode_skips_all_clients(self):
        """PAYMENT_DRY_RUN=1 → "skipped", не вызываем клиентов"""
        with patch.dict("os.environ", {
            "PAYMENT_ENV": "prod",
            "PAYMENT_DRY_RUN": "1"
        }, clear=True):
            result = charge_order(
                amount=2000,
                sandbox_client=self.sandbox_client,
                gateway_client=self.gateway_client
            )
        
        self.assertEqual(result, "skipped")
        self.sandbox_client.charge.assert_not_called()
        self.gateway_client.charge.assert_not_called()
    
    def test_dry_run_has_priority_over_env(self):
        """Dry-run имеет приоритет над PAYMENT_ENV"""
        with patch.dict("os.environ", {
            "PAYMENT_ENV": "dev",
            "PAYMENT_DRY_RUN": "1"
        }, clear=True):
            result = charge_order(
                amount=100,
                sandbox_client=self.sandbox_client,
                gateway_client=self.gateway_client
            )
        
        self.assertEqual(result, "skipped")
        self.sandbox_client.charge.assert_not_called()
        self.gateway_client.charge.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)