"""Модуль для парсинга конфигурационных значений из строк."""
import re
from typing import List

_TRUE = {"1", "true", "yes", "y", "on"}
_FALSE = {"0", "false", "no", "n", "off"}


def parse_port(value: str) -> int:
    """Парсит порт из строки. Диапазон 1..65535."""
    if not isinstance(value, str):
        raise TypeError(f"port value must be str, got {type(value).__name__}")
    
    raw = value.strip()
    if raw == "":
        raise ValueError("port is empty")
    
    if not re.fullmatch(r"[0-9]+", raw):
        raise ValueError(f"port is not a decimal integer: {value!r}")
    
    port = int(raw)
    if not (1 <= port <= 65535):
        raise ValueError("port out of range: 1..65535")
    
    return port


def parse_bool(value: str) -> bool:
    """Парсит булево значение из строки."""
    if not isinstance(value, str):
        raise TypeError(f"bool value must be str, got {type(value).__name__}")
    
    token = value.strip().lower()
    if token in _TRUE:
        return True
    if token in _FALSE:
        return False
    raise ValueError(f"invalid boolean literal: {value!r}")


def parse_csv(value: str) -> List[str]:
    """Парсит CSV строку в список строк.
    
    Разделитель - запятая. Пробелы вокруг элементов игнорируются.
    Пустые элементы отбрасываются.
    """
    if not isinstance(value, str):
        raise TypeError(f"csv value must be str, got {type(value).__name__}")
    
    if value.strip() == "":
        return []
    
    # Разделяем по запятой, убираем пробелы, фильтруем пустые
    items = [item.strip() for item in value.split(",")]
    return [item for item in items if item]