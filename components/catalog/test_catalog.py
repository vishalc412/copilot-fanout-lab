import unittest

from components.catalog import catalog


class CatalogTest(unittest.TestCase):
    def test_price_of_known_sku(self):
        self.assertEqual(catalog.price_of("SKU-1"), 24.0)


if __name__ == "__main__":
    unittest.main()
