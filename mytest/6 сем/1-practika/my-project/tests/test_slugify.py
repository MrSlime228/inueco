import unittest
from mypackage.slugify import slugify

class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")
    
    def test_multiple_spaces(self):
        self.assertEqual(slugify("  multiple   spaces  "), "multiple-spaces")
    
    def test_only_invalid(self):
        self.assertEqual(slugify("!!!"), "")

if __name__ == "__main__":
    unittest.main()