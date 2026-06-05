"""Сервис для оплаты заказов (ИСПРАВЛЕННАЯ ВЕРСИЯ)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Order:
    """Модель заказа."""
    id: int
    amount: int
    user_id: Optional[int] = None


class OrderRepo:
    """Репозиторий заказов (контракт)."""
    
    def get(self, order_id: int) -> Order:
        """Получает заказ по ID."""
        raise NotImplementedError


class PaymentGateway:
    """Платёжный шлюз (контракт)."""
    
    def charge(self, amount: int, currency: str = "RUB") -> str:
        """Списывает средства."""
        raise NotImplementedError


class AuditClient:
    """Клиент для аудита (контракт)."""
    
    def __init__(self, endpoint: str, token: str) -> None:
        """Инициализация клиента аудита."""
        self.endpoint = endpoint
        self.token = token
    
    def write(self, event: str, payload: dict) -> None:
        """Записывает событие в аудит."""
        raise NotImplementedError


class OrderService:
    """Сервис для оплаты заказов (ИСПРАВЛЕННАЯ ВЕРСИЯ)."""
    
    def __init__(self, repo: OrderRepo, payment_gateway: PaymentGateway):
        self.repo = repo
        self.payment_gateway = payment_gateway
    
    def pay(self, order_id: int) -> str:
        """Оплачивает заказ."""
        # Исправлено: правильное имя метода
        order = self.repo.get(order_id)
        
        # Исправлено: правильные аргументы
        tx_id = self.payment_gateway.charge(order.amount, currency="RUB")
        
        # Исправлено: правильный конструктор
        audit = AuditClient(endpoint="https://audit.local", token="secret")
        audit.write("payment_ok", {"order_id": order.id, "tx_id": tx_id})
        
        return tx_id