import unittest
from src.shop.pricing import final_price_cents


class TestFinalPrice(unittest.TestCase):
    
    def test_basic_calculation_with_default_tax(self):
        result = final_price_cents(1000, 10)
        self.assertEqual(result, 1080)
    
    def test_discount_100_percent(self):
        result = final_price_cents(1000, 100, 20)
        self.assertEqual(result, 0)
    
    def test_discount_0_percent(self):
        result = final_price_cents(1000, 0, 20)
        self.assertEqual(result, 1200)
    
    def test_tax_0_percent(self):
        result = final_price_cents(1000, 10, 0)
        self.assertEqual(result, 900)
    
    def test_invalid_base_negative(self):
        with self.assertRaises(ValueError):
            final_price_cents(-100)
    
    def test_invalid_discount_too_high(self):
        with self.assertRaises(ValueError):
            final_price_cents(1000, 150)
    
    def test_invalid_base_type_none(self):
        with self.assertRaises(TypeError):
            final_price_cents(None)


if __name__ == '__main__':
    unittest.main()
