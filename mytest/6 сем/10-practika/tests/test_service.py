import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from app.service import build_product_snapshot

class TestBuildProductSnapshot(unittest.TestCase):
    def test_orchestrates_config_client_and_timestamp(self):
        fixed_now = datetime(2026, 3, 20, 12, 0, 0, tzinfo=timezone.utc)
        
        with (
            patch("app.service.load_config") as mock_load_config,
            patch("app.service.CatalogClient", autospec=True) as MockCatalogClient,
            patch("app.service.datetime") as mock_datetime,
        ):
            mock_load_config.return_value = {"base_url": "https://api.example", "api_key": "token", "timeout": 5}
            
            client_instance = MockCatalogClient.return_value
            client_instance.fetch_product.return_value = {"id": 1, "name": "  Item  ", "price": 100, "in_stock": 1}
            
            mock_datetime.now.return_value = fixed_now
            
            result = build_product_snapshot("config.json", 1)
        
        self.assertEqual(result["name"], "Item")
        self.assertEqual(result["fetched_at"], "2026-03-20T12:00:00+00:00")
        mock_load_config.assert_called_once()
        client_instance.fetch_product.assert_called_once_with(1)

if __name__ == "__main__":
    unittest.main()