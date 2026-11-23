# orders: tests (pass 3)

## Tests added
`components/orders/test_orders.py` went from 1 test to 26 (25 added), stdlib `unittest`, no network.
The catalog is stubbed with `unittest.mock.patch.object(orders.catalog, ...)` and
`urllib.request.urlopen` is stubbed in the `settle` tests. Only `line_total` kept its original
test, which still uses the real catalog.

| Function | Tests added |
|----------|-------------|
| `line_total` | price x quantity; unknown SKU raises `KeyError` |
| `order_total` | no discount below threshold; empty order is 0.0; loyalty 5%; bulk 10% at exactly 10 items; no bulk at 9 items; bulk counts items across lines; loyalty + bulk does not stack (10% wins); rounds to 2 decimals; unknown SKU propagates |
| `validate` | valid lines give `[]`; empty order; qty 0 rejected without a stock check; negative qty rejected; out of stock rejected; one error per bad line, in order |
| `settle` | True on 200; False on other status (202); POSTs JSON body and `Content-Type` to `PARTNER_SETTLE_URL`; `dev=True` uses `DEV_SETTLE_URL`; timeout passed through; default timeout is 15; network error propagates |

## Result
`python -m unittest discover -s . -p "test_*.py" -t .`: Ran 26 tests, OK. (Full suite, all components.)

## Functions still untested and why
None. All four orders functions in plan.json now have tests.

## Notes
- No source code was changed. The tests pin current behavior, including that `settle` uses the
  `http://` partner URL (decision: KEEP, see `decisions.md`). When the https switch happens as a follow-up,
  `test_posts_json_body_to_partner_url` reads the constant, so it will not need editing.
- `validate` does not guard against non-integer quantities and `order_total` does not validate lines;
  these are not tested because the code does not define that behavior.
