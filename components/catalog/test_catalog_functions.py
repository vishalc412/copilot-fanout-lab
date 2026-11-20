import copy
import json
import unittest
from unittest import mock

from components.catalog import catalog


class CatalogStateTestCase(unittest.TestCase):
    """Restores the module-level _PRODUCTS after each test (apply_feed mutates it)."""

    def setUp(self):
        saved = copy.deepcopy(catalog._PRODUCTS)

        def restore():
            catalog._PRODUCTS.clear()
            catalog._PRODUCTS.update(saved)

        self.addCleanup(restore)


class GetProductTest(CatalogStateTestCase):
    def test_known_sku_returns_product(self):
        self.assertEqual(catalog.get_product("SKU-3"),
                         {"name": "Mug", "price": 6.0, "stock": 140})

    def test_unknown_sku_returns_none(self):
        self.assertIsNone(catalog.get_product("SKU-999"))

    def test_returns_live_dict_not_copy(self):
        self.assertIs(catalog.get_product("SKU-1"), catalog._PRODUCTS["SKU-1"])


class PriceOfTest(CatalogStateTestCase):
    def test_other_known_sku(self):
        self.assertEqual(catalog.price_of("SKU-2"), 39.5)

    def test_unknown_sku_raises_keyerror(self):
        with self.assertRaises(KeyError) as ctx:
            catalog.price_of("SKU-999")
        self.assertIn("unknown sku SKU-999", str(ctx.exception))


class InStockTest(CatalogStateTestCase):
    def test_default_qty_one(self):
        self.assertTrue(catalog.in_stock("SKU-1"))

    def test_zero_stock_is_out(self):
        self.assertFalse(catalog.in_stock("SKU-2"))

    def test_qty_equal_to_stock_is_in_stock(self):
        self.assertTrue(catalog.in_stock("SKU-1", 12))

    def test_qty_above_stock_is_out(self):
        self.assertFalse(catalog.in_stock("SKU-1", 13))

    def test_unknown_sku_is_false(self):
        self.assertFalse(catalog.in_stock("SKU-999"))


class ImageUrlTest(unittest.TestCase):
    def test_lowercases_sku_and_adds_jpg(self):
        self.assertEqual(catalog.image_url("SKU-1"),
                         "https://cdn.example.com/img/sku-1.jpg")

    def test_does_not_check_sku_exists(self):
        self.assertEqual(catalog.image_url("NOPE"),
                         catalog.IMAGE_CDN + "nope.jpg")


class FetchSupplierFeedTest(unittest.TestCase):
    def _fake_response(self, payload):
        resp = mock.MagicMock()
        resp.read.return_value = json.dumps(payload).encode()
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        return resp

    def test_returns_decoded_json(self):
        feed = {"products": [{"sku": "SKU-1", "price": "25.5", "stock": "3"}]}
        with mock.patch("urllib.request.urlopen",
                        return_value=self._fake_response(feed)) as urlopen:
            result = catalog.fetch_supplier_feed()
        self.assertEqual(result, feed)
        urlopen.assert_called_once_with(catalog.SUPPLIER_FEED_URL, timeout=10)

    def test_passes_custom_timeout(self):
        with mock.patch("urllib.request.urlopen",
                        return_value=self._fake_response({})) as urlopen:
            catalog.fetch_supplier_feed(timeout=2)
        urlopen.assert_called_once_with(catalog.SUPPLIER_FEED_URL, timeout=2)

    def test_network_error_propagates(self):
        with mock.patch("urllib.request.urlopen", side_effect=OSError("down")):
            with self.assertRaises(OSError):
                catalog.fetch_supplier_feed()

    def test_invalid_json_raises(self):
        resp = mock.MagicMock()
        resp.read.return_value = b"not json"
        resp.__enter__.return_value = resp
        resp.__exit__.return_value = False
        with mock.patch("urllib.request.urlopen", return_value=resp):
            with self.assertRaises(ValueError):
                catalog.fetch_supplier_feed()


class ApplyFeedTest(CatalogStateTestCase):
    def test_updates_price_and_stock_with_coercion(self):
        catalog.apply_feed({"products": [
            {"sku": "SKU-1", "price": "25.5", "stock": "7"}]})
        product = catalog.get_product("SKU-1")
        self.assertEqual(product["price"], 25.5)
        self.assertIsInstance(product["price"], float)
        self.assertEqual(product["stock"], 7)
        self.assertIsInstance(product["stock"], int)

    def test_unknown_sku_is_ignored(self):
        before = copy.deepcopy(catalog._PRODUCTS)
        catalog.apply_feed({"products": [
            {"sku": "SKU-999", "price": 1, "stock": 1}]})
        self.assertEqual(catalog._PRODUCTS, before)

    def test_missing_or_empty_products_is_noop(self):
        before = copy.deepcopy(catalog._PRODUCTS)
        catalog.apply_feed({})
        catalog.apply_feed({"products": []})
        self.assertEqual(catalog._PRODUCTS, before)

    def test_item_missing_keys_raises_keyerror(self):
        with self.assertRaises(KeyError):
            catalog.apply_feed({"products": [{"sku": "SKU-1", "price": 1}]})

    def test_name_is_left_unchanged(self):
        catalog.apply_feed({"products": [
            {"sku": "SKU-2", "price": 40, "stock": 5}]})
        self.assertEqual(catalog.get_product("SKU-2")["name"], "Toaster")

    def test_feed_changes_visible_to_price_of_and_in_stock(self):
        catalog.apply_feed({"products": [
            {"sku": "SKU-2", "price": 41, "stock": 2}]})
        self.assertEqual(catalog.price_of("SKU-2"), 41.0)
        self.assertTrue(catalog.in_stock("SKU-2", 2))


if __name__ == "__main__":
    unittest.main()
