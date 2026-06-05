def parse_port(value):
    if isinstance(value, bool):
        raise TypeError(f"bool недопустим: {value}")
    
    if isinstance(value, int):
        if 1 <= value <= 65535:
            return value
        raise ValueError(f"Номер порта должен быть в диапазоне 1..65535, получено {value}")
    
    if isinstance(value, str):
        stripped = value.strip()
        
        if not stripped:
            raise ValueError(f"Пустая строка или строка из пробелов: '{value}'")
        
        if not stripped.isdigit():
            raise ValueError(f"Строка должна содержать только цифры: '{value}'")
        
        port = int(stripped)
        
        if 1 <= port <= 65535:
            return port
        raise ValueError(f"Номер порта должен быть в диапазоне 1..65535, получено {port}")
    
    raise TypeError(f"Неподдерживаемый тип: {type(value).__name__}")