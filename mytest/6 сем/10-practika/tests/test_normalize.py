import unittest
from app.service import normalize_product

class TestNormalizeProduct(unittest.TestCase):
    def test_normalizes_payload(self):
        result = normalize_product(
            payload={"id": 1, "name": "  Keyboard  ", "price": 99, "in_stock": 1},
            fetched_at="2026-03-20T12:00:00+00:00"
        )
        self.assertEqual(result["name"], "Keyboard")
        self.assertEqual(result["in_stock"], True)
    
    def test_default_currency(self):
        result = normalize_product(
            payload={"id": 2, "name": "Mouse", "price": 49},
            fetched_at="2026-03-20T12:00:00+00:00"
        )
        self.assertEqual(result["currency"], "USD")

if __name__ == "__main__":
    unittest.main()