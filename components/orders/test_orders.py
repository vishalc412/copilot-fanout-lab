import unittest

from components.orders import orders


class OrdersTest(unittest.TestCase):
    def test_line_total(self):
        self.assertEqual(orders.line_total("SKU-3", 2), 12.0)


if __name__ == "__main__":
    unittest.main()
