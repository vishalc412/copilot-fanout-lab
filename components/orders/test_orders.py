import json
import unittest
from unittest import mock

from components.orders import orders

PRICES = {"SKU-1": 10.0, "SKU-2": 3.0}


def fake_price_of(sku):
    if sku not in PRICES:
        raise KeyError(f"unknown sku {sku}")
    return PRICES[sku]


class OrdersTest(unittest.TestCase):
    def test_line_total(self):
        self.assertEqual(orders.line_total("SKU-3", 2), 12.0)


@mock.patch.object(orders.catalog, "price_of", side_effect=fake_price_of)
class LineTotalTest(unittest.TestCase):
    def test_multiplies_price_by_quantity(self, _):
        self.assertEqual(orders.line_total("SKU-1", 3), 30.0)

    def test_unknown_sku_raises_key_error(self, _):
        with self.assertRaises(KeyError):
            orders.line_total("NOPE", 1)


@mock.patch.object(orders.catalog, "price_of", side_effect=fake_price_of)
class OrderTotalTest(unittest.TestCase):
    def test_no_discount_below_threshold(self, _):
        self.assertEqual(orders.order_total([("SKU-1", 2), ("SKU-2", 1)]), 23.0)

    def test_empty_order_is_zero(self, _):
        self.assertEqual(orders.order_total([]), 0.0)

    def test_loyalty_discount(self, _):
        self.assertEqual(orders.order_total([("SKU-1", 2)], loyal=True), 19.0)

    def test_bulk_discount_at_threshold(self, _):
        # 10 items is exactly the threshold: 10% off 100.0
        self.assertEqual(orders.order_total([("SKU-1", 10)]), 90.0)

    def test_just_below_bulk_threshold_has_no_discount(self, _):
        self.assertEqual(orders.order_total([("SKU-1", 9)]), 90.0)

    def test_bulk_counts_items_across_lines(self, _):
        # 5 + 5 items: bulk applies; subtotal 65.0 -> 58.5
        self.assertEqual(orders.order_total([("SKU-1", 5), ("SKU-2", 5)]), 58.5)

    def test_discounts_do_not_stack_larger_wins(self, _):
        # loyal (5%) and bulk (10%) together: only 10% is applied
        self.assertEqual(orders.order_total([("SKU-1", 10)], loyal=True), 90.0)

    def test_result_rounded_to_two_decimals(self, _):
        with mock.patch.object(orders.catalog, "price_of", return_value=0.333):
            self.assertEqual(orders.order_total([("X", 1)]), 0.33)

    def test_unknown_sku_propagates(self, _):
        with self.assertRaises(KeyError):
            orders.order_total([("NOPE", 1)])


class ValidateTest(unittest.TestCase):
    def test_valid_lines_give_no_errors(self):
        with mock.patch.object(orders.catalog, "in_stock", return_value=True):
            self.assertEqual(orders.validate([("SKU-1", 2)]), [])

    def test_empty_order_is_valid(self):
        self.assertEqual(orders.validate([]), [])

    def test_zero_quantity_rejected_without_stock_check(self):
        with mock.patch.object(orders.catalog, "in_stock") as in_stock:
            errors = orders.validate([("SKU-1", 0)])
        self.assertEqual(errors, ["SKU-1: quantity must be positive"])
        in_stock.assert_not_called()

    def test_negative_quantity_rejected(self):
        with mock.patch.object(orders.catalog, "in_stock", return_value=True):
            errors = orders.validate([("SKU-1", -2)])
        self.assertEqual(errors, ["SKU-1: quantity must be positive"])

    def test_out_of_stock_rejected(self):
        with mock.patch.object(orders.catalog, "in_stock", return_value=False) as in_stock:
            errors = orders.validate([("SKU-2", 5)])
        self.assertEqual(errors, ["SKU-2: not enough stock"])
        in_stock.assert_called_once_with("SKU-2", 5)

    def test_collects_one_error_per_bad_line(self):
        stock = {"SKU-1": True, "SKU-2": False}
        with mock.patch.object(orders.catalog, "in_stock",
                               side_effect=lambda sku, qty: stock[sku]):
            errors = orders.validate([("SKU-1", 1), ("SKU-2", 1), ("SKU-1", 0)])
        self.assertEqual(errors, ["SKU-2: not enough stock",
                                  "SKU-1: quantity must be positive"])


class FakeResponse:
    def __init__(self, status):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class SettleTest(unittest.TestCase):
    def _settle(self, response=None, side_effect=None, **kwargs):
        with mock.patch.object(orders.urllib.request, "urlopen",
                               return_value=response, side_effect=side_effect) as urlopen:
            result = orders.settle("ORD-1", 42.5, **kwargs)
        return result, urlopen

    def test_returns_true_on_200(self):
        result, _ = self._settle(FakeResponse(200))
        self.assertTrue(result)

    def test_returns_false_on_other_status(self):
        result, _ = self._settle(FakeResponse(202))
        self.assertFalse(result)

    def test_posts_json_body_to_partner_url(self):
        _, urlopen = self._settle(FakeResponse(200))
        req = urlopen.call_args.args[0]
        self.assertEqual(req.full_url, orders.PARTNER_SETTLE_URL)
        self.assertEqual(json.loads(req.data), {"order": "ORD-1", "amount": 42.5})
        self.assertEqual(req.get_header("Content-type"), "application/json")

    def test_dev_flag_uses_dev_url(self):
        _, urlopen = self._settle(FakeResponse(200), dev=True)
        self.assertEqual(urlopen.call_args.args[0].full_url, orders.DEV_SETTLE_URL)

    def test_timeout_passed_through(self):
        _, urlopen = self._settle(FakeResponse(200), timeout=3)
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 3)

    def test_default_timeout_is_15(self):
        _, urlopen = self._settle(FakeResponse(200))
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 15)

    def test_network_error_propagates(self):
        with self.assertRaises(OSError):
            self._settle(side_effect=OSError("down"))


if __name__ == "__main__":
    unittest.main()
