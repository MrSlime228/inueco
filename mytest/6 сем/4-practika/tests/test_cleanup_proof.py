import io
import sqlite3
import unittest
from pathlib import Path

from tests.demo_suite import (
    TMP_DIRS, CONNS,
    InnerPass, InnerFail, InnerError, InnerSetupError
)


class TestCleanupProof(unittest.TestCase):
    """Доказывает, что ресурсы очищаются при любом исходе"""
    
    def setUp(self):
        TMP_DIRS.clear()
        CONNS.clear()
    
    def test_cleanup_happens_on_success_fail_error(self):
        """Главный тест: проверяет уборку при всех исходах"""
        
        suite = unittest.TestSuite()
        loader = unittest.defaultTestLoader
        
        suite.addTests(loader.loadTestsFromTestCase(InnerPass))
        suite.addTests(loader.loadTestsFromTestCase(InnerFail))
        suite.addTests(loader.loadTestsFromTestCase(InnerError))
        suite.addTests(loader.loadTestsFromTestCase(InnerSetupError))
        
        stream = io.StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=0)
        result = runner.run(suite)
        
        # Проверки
        self.assertGreaterEqual(len(result.failures), 1)
        self.assertGreaterEqual(len(result.errors), 1)
        
        leaked_dirs = [p for p in TMP_DIRS if Path(p).exists()]
        self.assertEqual(leaked_dirs, [])
        
        not_closed = []
        for i, conn in enumerate(CONNS):
            try:
                conn.execute("SELECT 1")
                not_closed.append(i)
            except sqlite3.ProgrammingError:
                pass
        
        self.assertEqual(not_closed, [])
        
        print(f"\n✅ Все ресурсы очищены! (FAIL={len(result.failures)}, ERROR={len(result.errors)})")


if __name__ == "__main__":
    unittest.main(verbosity=2)