import os


def choose_payment_mode() -> str:
    """
    Выбирает режим оплаты на основе переменных окружения.
    
    Правила:
    - PAYMENT_DRY_RUN=1 → "dry-run"
    - PAYMENT_ENV=dev или test → "sandbox"
    - PAYMENT_ENV=prod → "gateway"
    - другое значение PAYMENT_ENV → ValueError
    """
    dry_run = os.getenv("PAYMENT_DRY_RUN", "0")
    if dry_run == "1":
        return "dry-run"
    
    payment_env = os.getenv("PAYMENT_ENV", "prod")
    
    if payment_env == "dev" or payment_env == "test":
        return "sandbox"
    
    if payment_env == "prod":
        return "gateway"
    
    raise ValueError(f"unsupported payment env: {payment_env}")


def charge_order(amount: int, sandbox_client, gateway_client) -> str:
    """
    Проводит оплату заказа в зависимости от режима.
    
    Args:
        amount: сумма в копейках/центах
        sandbox_client: клиент для тестовой среды (должен иметь метод charge)
        gateway_client: клиент для реального шлюза (должен иметь метод charge)
    
    Returns:
        "skipped" - dry-run режим
        "sandbox" - оплата через sandbox
        "gateway" - оплата через реальный шлюз
    """
    mode = choose_payment_mode()
    
    if mode == "dry-run":
        return "skipped"
    
    if mode == "sandbox":
        sandbox_client.charge(amount)
        return "sandbox"
    
    # mode == "gateway"
    gateway_client.charge(amount)
    return "gateway"