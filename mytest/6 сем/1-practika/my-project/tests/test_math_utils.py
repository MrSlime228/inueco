import unittest
from mypackage.math_utils import add

class TestAdd(unittest.TestCase):
    def test_add_two_numbers(self):
        self.assertEqual(add(2, 3), 5)
    
    def test_add_negative_numbers(self):
        self.assertEqual(add(-1, -1), -2)
    
    def test_add_zero(self):
        self.assertEqual(add(5, 0), 5)
    
    def test_add_large_numbers(self):
        self.assertEqual(add(1000000, 2000000), 3000000)

if __name__ == '__main__':
    unittest.main()