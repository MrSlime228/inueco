from dataclasses import dataclass
from typing import Optional


@dataclass
class Invoice:
    """Модель счёта"""
    id: int
    customer_id: str
    amount: int
    status: str  # "pending", "paid", "failed", "retry"


@dataclass
class ChargeResult:
    """Результат платежа"""
    ok: bool
    transaction_id: Optional[str] = None
    reason: Optional[str] = None


class InvoiceService:
    """Сервис для оплаты счетов"""
    
    def __init__(self, invoice_repo, payment_gateway):
        """
        invoice_repo: репозиторий для работы со счетами
        payment_gateway: внешний платёжный шлюз
        """
        self.invoice_repo = invoice_repo
        self.payment_gateway = payment_gateway
    
    def pay(self, invoice_id: int) -> str:
        """
        Оплатить счёт.
        
        Возвращает:
            "paid" - оплата успешна
            "already_paid" - счёт уже оплачен
            "failed" - платёж отклонён
            "retry" - ошибка шлюза, нужно повторить
        
        Исключения:
            LookupError - счёт не найден
            ValueError - сумма <= 0
        """
        # Получаем счёт
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if invoice is None:
            raise LookupError("invoice not found")
        
        # Уже оплачен?
        if invoice.status == "paid":
            return "already_paid"
        
        # Проверка суммы
        if invoice.amount <= 0:
            raise ValueError("amount must be positive")
        
        # Пытаемся провести платёж
        try:
            result = self.payment_gateway.charge(
                customer_id=invoice.customer_id,
                amount=invoice.amount
            )
        except TimeoutError:
            self.invoice_repo.mark_retry(invoice_id)
            return "retry"
        
        # Обработка результата
        if result.ok:
            self.invoice_repo.mark_paid(invoice_id, result.transaction_id)
            return "paid"
        else:
            self.invoice_repo.mark_failed(invoice_id, result.reason)
            return "failed"