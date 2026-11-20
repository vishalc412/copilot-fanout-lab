# orders: inventory (pass 1)

Source: `components/orders/orders.py` (the only source file in plan.json).
Existing tests: `components/orders/test_orders.py` covers `line_total` only.

| Function | file:line | What it does | Called by |
|----------|-----------|--------------|-----------|
| `line_total` | `components/orders/orders.py:19` | Price of one order line: `catalog.price_of(sku) * qty`. Raises `KeyError` for an unknown SKU (propagated from the catalog). | `order_total` (`orders.py:25`); `test_orders.py:8`. No callers in other components. |
| `order_total` | `components/orders/orders.py:23` | Order total from `(sku, qty)` lines, rounded to 2 decimals. Applies the 5% loyalty discount if `loyal`, and the 10% bulk discount if total items >= 10. Discounts do not stack; the larger wins. | No callers found in the repo (no tests either). No callers in other components. |
| `validate` | `components/orders/orders.py:35` | Returns a list of error strings: quantity <= 0, or `catalog.in_stock(sku, qty)` false ("not enough stock"). Empty list means valid. | No callers found in the repo (no tests either). No callers in other components. |
| `settle` | `components/orders/orders.py:45` | POSTs `{"order", "amount"}` as JSON to the payment partner (`PARTNER_SETTLE_URL`, or `DEV_SETTLE_URL` when `dev=True`). Returns `True` if HTTP status is 200. Network errors propagate. | No callers found in the repo (no tests either). No callers in other components. |

## Dependencies on other components
- `orders` imports `components.catalog.catalog` and uses `price_of` (from `line_total`) and `in_stock` (from `validate`).

## Notes
- "Callers" were found by searching all `.py` and `.md` files in the repo for each name. Only `README.md` mentions orders, and only the settlement URL. If a caller exists outside this repo, this search cannot see it.
- Module constants (not functions): `PARTNER_SETTLE_URL` (line 9), `DEV_SETTLE_URL` (line 12), `LOYALTY_DISCOUNT`, `BULK_DISCOUNT`, `BULK_THRESHOLD`. The two `http://` sites are for pass 2.
