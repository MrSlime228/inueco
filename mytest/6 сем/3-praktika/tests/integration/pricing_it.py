# tests/integration/pricing_it.py
import unittest
from src.shop.pricing import final_price_cents


class TestPricingIntegration(unittest.TestCase):
    
    def test_multiple_calculations_chain(self):
        """Цепочка вычислений с разными параметрами"""
        # Тест 1: большая скидка
        price1 = final_price_cents(5000, 50, 20)
        self.assertEqual(price1, 3000)  # 5000/2 = 2500, +20% = 3000
        
        # Тест 2: маленькая скидка, большой налог
        price2 = final_price_cents(price1, 10, 50)
        # 3000 - 10% = 2700, +50% = 4050
        self.assertEqual(price2, 4050)
        
        # Тест 3: без скидки, без налога
        price3 = final_price_cents(price2, 0, 0)
        self.assertEqual(price3, 4050)
    
    def test_real_world_scenario_cart(self):
        """Сценарий корзины с несколькими товарами"""
        items = [
            (1000, 0, 20),   # без скидки
            (2000, 15, 20),  # скидка 15%
            (3000, 25, 20),  # скидка 25%
        ]
        
        total = 0
        for base, discount, tax in items:
            total += final_price_cents(base, discount, tax)
        
        # Посчитаем вручную:
        # 1000 + 20% = 1200
        # 2000 - 15% = 1700 + 20% = 2040
        # 3000 - 25% = 2250 + 20% = 2700
        # Сумма = 5940
        self.assertEqual(total, 5940)
    
    def test_edge_case_combination(self):
        """Комбинация крайних значений"""
        # Максимальная скидка и максимальный налог
        result = final_price_cents(10000, 100, 100)
        self.assertEqual(result, 0)  # 100% скидка дает 0, налог на 0 = 0


if __name__ == '__main__':
    unittest.main()