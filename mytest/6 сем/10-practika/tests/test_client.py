import unittest
from unittest.mock import patch
import requests
from app.client import CatalogClient, CatalogTimeoutError, CatalogResponseError

class TestCatalogClientSuccess(unittest.TestCase):
    @patch("app.client.requests.get")
    def test_fetch_product_success(self, mocked_get):
        response = mocked_get.return_value
        response.raise_for_status.return_value = None
        response.json.return_value = {"id": 101, "name": "Keyboard", "price": 99}
        
        client = CatalogClient("https://api.example", "token", 5)
        result = client.fetch_product(101)
        
        self.assertEqual(result["name"], "Keyboard")
        mocked_get.assert_called_once()

class TestCatalogClientTimeout(unittest.TestCase):
    @patch("app.client.requests.get")
    def test_fetch_product_timeout(self, mocked_get):
        mocked_get.side_effect = requests.Timeout()
        client = CatalogClient("https://api.example", "token", 5)
        
        with self.assertRaises(CatalogTimeoutError):
            client.fetch_product(101)

class TestCatalogClientHttp500(unittest.TestCase):
    @patch("app.client.requests.get")
    def test_fetch_product_http_500(self, mocked_get):
        response = mocked_get.return_value
        response.raise_for_status.side_effect = requests.HTTPError("500 Error")
        
        client = CatalogClient("https://api.example", "token", 5)
        
        with self.assertRaises(CatalogResponseError):
            client.fetch_product(101)
        
        response.json.assert_not_called()

if __name__ == "__main__":
    unittest.main()