import sqlite3
import tempfile
import unittest
from pathlib import Path

# Глобальные следы для проверки уборки
TMP_DIRS = []  # пути к временным директориям
CONNS = []     # объекты соединений SQLite


class _BaseWithResources(unittest.TestCase):
    """Базовый класс с ресурсами (временная директория + SQLite)"""
    
    def setUp(self):
        # 1. Временная директория
        tmp = tempfile.TemporaryDirectory()
        TMP_DIRS.append(tmp.name)
        self.addCleanup(tmp.cleanup)  # гарантированная уборка
        self.workdir = Path(tmp.name)
        
        # 2. Соединение SQLite
        conn = sqlite3.connect(":memory:")
        CONNS.append(conn)
        self.addCleanup(conn.close)  # гарантированное закрытие
        self.conn = conn
        
        # 3. Используем ресурсы (создаём таблицу)
        conn.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'test')")


class InnerPass(_BaseWithResources):
    """Тест, который успешно проходит"""
    
    def test_ok(self):
        result = self.conn.execute("SELECT name FROM test WHERE id=1").fetchone()
        self.assertEqual(result[0], "test")


class InnerFail(_BaseWithResources):
    """Тест, который намеренно падает (FAIL)"""
    
    def test_fail(self):
        # Намеренный FAIL - проверка не пройдёт
        self.assertEqual(1, 2)


class InnerError(_BaseWithResources):
    """Тест, который намеренно вызывает ошибку (ERROR)"""
    
    def test_error(self):
        # Намеренный ERROR
        raise RuntimeError("Simulated error in test")


class InnerSetupError(unittest.TestCase):
    """Тест, где setUp() падает ПОСЛЕ захвата ресурсов"""
    
    def setUp(self):
        # Регистрируем ресурсы ДО ТОГО, как упадём
        tmp = tempfile.TemporaryDirectory()
        TMP_DIRS.append(tmp.name)
        self.addCleanup(tmp.cleanup)
        
        conn = sqlite3.connect(":memory:")
        CONNS.append(conn)
        self.addCleanup(conn.close)
        
        # А теперь падаем! TearDown не вызовется, но cleanup сработает
        raise RuntimeError("Boom in setUp")
    
    def test_never_runs(self):
        self.assertTrue(False)