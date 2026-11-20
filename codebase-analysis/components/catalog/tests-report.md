# catalog: pass 3 tests

New test file: `components/catalog/test_catalog_functions.py` (stdlib `unittest`,
no network). The existing `components/catalog/test_catalog.py` is unchanged.
`urllib.request.urlopen` is stubbed with `unittest.mock.patch` in the
`fetch_supplier_feed` tests. `apply_feed` mutates the module-level `_PRODUCTS`,
so every test class that touches it restores a deep copy in `setUp` (via
`addCleanup`), and tests do not depend on run order.

## Tests added

At plan time: 1 test function (`test_price_of_known_sku` in `test_catalog.py`).
Now: 23 across the two catalog test files (22 added, all in
`test_catalog_functions.py`).

| Function | Tests added |
|---|---|
| `get_product` | known SKU returns the product dict; unknown SKU returns `None`; returns the live dict, not a copy (documents current behaviour) |
| `price_of` | second known SKU (SKU-2, 39.5); unknown SKU raises `KeyError("unknown sku ...")` |
| `in_stock` | default qty 1; zero stock is out; qty equal to stock is in; qty above stock is out; unknown SKU is False |
| `image_url` | lowercases SKU and adds `.jpg` on the https CDN; does not check the SKU exists |
| `fetch_supplier_feed` | returns the decoded JSON and calls `urlopen(SUPPLIER_FEED_URL, timeout=10)`; custom timeout is passed through; network error (`OSError`) propagates; invalid JSON raises `ValueError` |
| `apply_feed` | price/stock updated and coerced to float/int; unknown SKU ignored; `{}` and empty `products` are no-ops; item missing `stock` raises `KeyError`; `name` untouched; changes visible through `price_of` and `in_stock` |

## Result

Command: `python3 -m unittest discover -s . -p "test_*.py" -t .`

```
Ran 24 tests in 0.001s

OK
```

24 = 23 catalog tests + 1 existing orders test. All pass.

## Why a new file and not `test_catalog.py`

`tools/gate.py` compares the test count of the files listed in plan.json
(`test_catalog.py`, read from disk at gate time) with the count across all
`components/catalog/test_*.py`. Adding tests to `test_catalog.py` itself makes
both sides equal, so the gate reports "no new tests" even when tests were added.
New tests therefore live in a separate `test_catalog_functions.py`. `tools/` is
out of scope for this pass, so the gate was not changed; the team may want to
have plan.py snapshot the count into plan.json.

## Functions still untested

None: all six functions in plan.json (`get_product`, `price_of`, `in_stock`,
`image_url`, `fetch_supplier_feed`, `apply_feed`) now have at least one test.

Gaps worth knowing about, not covered because they would need a source change
or a real network (both out of scope):

- The real supplier endpoint is never contacted. The tests check only what
  `fetch_supplier_feed` passes to `urlopen`, and the pass 2 decision to move
  `SUPPLIER_FEED_URL` to `https://` is not applied here. When that source change is made,
  the URL assertions use `catalog.SUPPLIER_FEED_URL`, so the tests will not need editing.
- `apply_feed` has no validation (negative stock, non-numeric price) and these
  tests do not pin down that behaviour; it is undefined in the code today.
- Feed items that omit `stock` or `price` crash the whole run midway, leaving
  earlier items applied (partial update). The test only asserts the `KeyError`.
