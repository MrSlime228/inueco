"""Табличные тесты для парсера конфигурации."""
import os
import unittest
import sys
from typing import List, Any

from config_parsing import parse_port, parse_bool, parse_csv


# ========== Проверка переменной окружения для медленных тестов ==========
RUN_SLOW = os.environ.get("RUN_SLOW") == "1"


# ========== Тесты для parse_port ==========
class TestParsePort(unittest.TestCase):
    """Тесты для parse_port."""
    
    def test_valid_ports(self):
        """Валидные значения порта."""
        cases = [
            ("1", 1),
            (" 80 ", 80),
            ("\t443\n", 443),
            ("65535", 65535),
            ("  8080  ", 8080),
            ("00022", 22),  # ведущие нули
        ]
        
        for raw, expected in cases:
            with self.subTest(raw=raw, expected=expected):
                result = parse_port(raw)
                self.assertEqual(result, expected)
    
    def test_invalid_ports(self):
        """Невалидные значения порта."""
        cases = [
            ("", ValueError, "empty"),
            ("   ", ValueError, "empty"),
            ("0", ValueError, "out of range"),
            ("65536", ValueError, "out of range"),
            ("-5", ValueError, "decimal integer"),
            ("80.5", ValueError, "decimal integer"),
            ("abc", ValueError, "decimal integer"),
            ("80,80", ValueError, "decimal integer"),
            (None, TypeError, "must be str"),  # type: ignore
            (123, TypeError, "must be str"),   # type: ignore
        ]
        
        for raw, exc_type, msg_part in cases:
            with self.subTest(raw=raw, exc=exc_type.__name__):
                with self.assertRaisesRegex(exc_type, msg_part):
                    parse_port(raw)  # type: ignore


# ========== Тесты для parse_bool ==========
class TestParseBool(unittest.TestCase):
    """Тесты для parse_bool."""
    
    def test_valid_bools(self):
        """Валидные булевы значения."""
        cases = [
            ("true", True),
            (" TRUE ", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("y", True),
            ("on", True),
            ("false", False),
            (" FALSE ", False),
            ("0", False),
            ("no", False),
            ("n", False),
            ("off", False),
        ]
        
        for raw, expected in cases:
            with self.subTest(raw=raw, expected=expected):
                result = parse_bool(raw)
                self.assertEqual(result, expected)
    
    def test_invalid_bools(self):
        """Невалидные булевы значения."""
        cases = [
            ("", ValueError, "invalid"),
            ("   ", ValueError, "invalid"),
            ("maybe", ValueError, "invalid"),
            ("2", ValueError, "invalid"),
            ("truefalse", ValueError, "invalid"),
            (None, TypeError, "must be str"),  # type: ignore
            (123, TypeError, "must be str"),   # type: ignore
        ]
        
        for raw, exc_type, msg_part in cases:
            with self.subTest(raw=raw, exc=exc_type.__name__):
                with self.assertRaisesRegex(exc_type, msg_part):
                    parse_bool(raw)  # type: ignore


# ========== Тесты для parse_csv ==========
class TestParseCSV(unittest.TestCase):
    """Тесты для parse_csv."""
    
    def test_valid_csv(self):
        """Валидные CSV строки."""
        cases = [
            ("a,b,c", ["a", "b", "c"]),
            ("  a , b , c  ", ["a", "b", "c"]),
            ("single", ["single"]),
            ("", []),
            ("   ", []),
            ("value1,,value2", ["value1", "value2"]),  # пустой элемент пропускаем
            (",,", []),  # только пустые
            ("  one  ,  ,  two  ", ["one", "two"]),
        ]
        
        for raw, expected in cases:
            with self.subTest(raw=raw, expected=expected):
                result = parse_csv(raw)
                self.assertEqual(result, expected)
    
    def test_invalid_csv(self):
        """Невалидные входные данные для CSV."""
        cases = [
            (None, TypeError, "must be str"),  # type: ignore
            (123, TypeError, "must be str"),   # type: ignore
            ([], TypeError, "must be str"),    # type: ignore
        ]
        
        for raw, exc_type, msg_part in cases:
            with self.subTest(raw=raw, exc=exc_type.__name__):
                with self.assertRaisesRegex(exc_type, msg_part):
                    parse_csv(raw)  # type: ignore


# ========== Медленные/расширенные тесты (условно) ==========
@unittest.skipUnless(RUN_SLOW, "set RUN_SLOW=1 to enable extended parsing tests")
class TestExtendedCases(unittest.TestCase):
    """Расширенный набор тестов, запускается только при RUN_SLOW=1."""
    
    def test_extended_ports(self):
        """Дополнительные граничные случаи для портов."""
        valid_cases = [
            ("   1   ", 1),
            ("   65535   ", 65535),
            (" 00001 ", 1),
            (" 00080 ", 80),
        ]
        
        for raw, expected in valid_cases:
            with self.subTest(raw=raw, expected=expected):
                self.assertEqual(parse_port(raw), expected)
        
        invalid_cases = [
            ("99999", ValueError, "out of range"),
            ("100000", ValueError, "out of range"),
            ("-0", ValueError, "decimal integer"),
            ("+80", ValueError, "decimal integer"),
            ("0x1F", ValueError, "decimal integer"),
        ]
        
        for raw, exc_type, msg_part in invalid_cases:
            with self.subTest(raw=raw, exc=exc_type.__name__):
                with self.assertRaisesRegex(exc_type, msg_part):
                    parse_port(raw)
    
    def test_extended_bools(self):
        """Дополнительные варианты булевых значений."""
        valid_cases = [
            ("  YeS  ", True),
            ("  OfF  ", False),
            ("  On  ", True),
            ("  No  ", False),
        ]
        
        for raw, expected in valid_cases:
            with self.subTest(raw=raw, expected=expected):
                self.assertEqual(parse_bool(raw), expected)
        
        invalid_cases = [
            ("not_a_bool", ValueError, "invalid"),
            ("true false", ValueError, "invalid"),
            ("1 0", ValueError, "invalid"),
        ]
        
        for raw, exc_type, msg_part in invalid_cases:
            with self.subTest(raw=raw, exc=exc_type.__name__):
                with self.assertRaisesRegex(exc_type, msg_part):
                    parse_bool(raw)
    
    def test_extended_csv(self):
        """Дополнительные варианты CSV."""
        cases = [
            ("a ,, b ,, c", ["a", "b", "c"]),
            ("  ", []),
            (" , , ", []),
            ("a;b;c", ["a;b;c"]),  # не стандартный разделитель
        ]
        
        for raw, expected in cases:
            with self.subTest(raw=raw, expected=expected):
                self.assertEqual(parse_csv(raw), expected)


# ========== Тесты для опциональной зависимости ==========
# Проверяем наличие yaml (PyYAML) - стандартная библиотека не содержит yaml
# Это пример того, как нужно тестировать опциональные зависимости
try:
    import importlib.util
    YAML_AVAILABLE = importlib.util.find_spec("yaml") is not None
except ImportError:
    YAML_AVAILABLE = False


@unittest.skipUnless(YAML_AVAILABLE, "requires PyYAML: https://pyyaml.org/ (не установлена на учебном компьютере)")
class TestYamlDependency(unittest.TestCase):
    """Тесты, требующие PyYAML (обычно не установлена на учебных ПК)."""
    
    def test_yaml_parsing(self):
        """Пример теста с yaml (будет пропущен)."""
        import yaml
        data = yaml.safe_load("port: 80\n")
        self.assertEqual(data["port"], 80)


# ========== Дополнительно: демонстрация работы skipTest в setUp ==========
class TestDynamicSkip(unittest.TestCase):
    """Демонстрация динамического пропуска через setUp."""
    
    def setUp(self):
        # Пример: пропускаем тесты на Python старше 3.9
        if sys.version_info < (3, 9):
            self.skipTest(f"requires Python >= 3.9, got {sys.version_info.major}.{sys.version_info.minor}")
    
    def test_python_version(self):
        """Этот тест выполнится только на Python 3.9+."""
        self.assertTrue(True)


# ========== Точка входа для прямого запуска ==========
if __name__ == "__main__":
    unittest.main()