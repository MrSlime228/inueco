import unittest
from netutils.ports import parse_port

class TestParsePort(unittest.TestCase):
    
    def test_accepts_int_valid_port(self):
        """int в диапазоне 1-65535 -> возвращает число"""
        self.assertEqual(parse_port(8080), 8080)
        self.assertEqual(parse_port(1), 1)
        self.assertEqual(parse_port(65535), 65535)
    
    def test_raises_type_error_on_bool(self):
        """bool (True/False) -> TypeError"""
        with self.assertRaises(TypeError):
            parse_port(True)
        with self.assertRaises(TypeError):
            parse_port(False)
    
    def test_int_boundary_invalid(self):
        """Значения вне диапазона -> ValueError"""
        invalid_ports = [0, -1, 65536]
        for port in invalid_ports:
            with self.subTest(port=port):
                with self.assertRaises(ValueError):
                    parse_port(port)
    
    def test_accepts_string_valid(self):
        """Строка с цифрами -> конвертируется в int"""
        self.assertEqual(parse_port("443"), 443)
        self.assertEqual(parse_port("  80  "), 80)
    
    def test_string_whitespace_only(self):
        """Пустая строка или пробелы -> ValueError"""
        with self.assertRaises(ValueError):
            parse_port("")
        with self.assertRaises(ValueError):
            parse_port("   ")
    
    def test_string_with_letters(self):
        """Строка с буквами -> ValueError"""
        with self.assertRaises(ValueError):
            parse_port("80a")

if __name__ == "__main__":
    unittest.main(verbosity=2)