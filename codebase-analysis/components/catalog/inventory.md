# catalog: pass 1 inventory

Source: `components/catalog/catalog.py` (module-level data: `_PRODUCTS` in-memory
dict with SKU-1..SKU-3, `SUPPLIER_FEED_URL`, `IMAGE_CDN`). Function list comes
from `codebase-analysis/plan.json`; callers were found by searching the whole
repository.

| Function | file:line | What it does | Called by |
|---|---|---|---|
| `get_product` | components/catalog/catalog.py:15 | Returns the product dict for a SKU from `_PRODUCTS`, or `None` if unknown. Returns the live dict, not a copy. | `price_of` (catalog.py:21), `in_stock` (catalog.py:28). No callers in other components. |
| `price_of` | components/catalog/catalog.py:20 | Returns the unit price for a SKU. Raises `KeyError("unknown sku ...")` if the SKU is unknown. | `line_total` in components/orders/orders.py:20 (other component); `test_price_of_known_sku` in components/catalog/test_catalog.py:8. |
| `in_stock` | components/catalog/catalog.py:27 | True if the SKU exists and its stock is at least `qty` (default 1). Unknown SKU gives False. | `validate` in components/orders/orders.py:40 (other component). |
| `image_url` | components/catalog/catalog.py:32 | Builds the CDN image URL: `IMAGE_CDN` + lowercased SKU + `.jpg`. Does not check that the SKU exists. | None found in the repository. |
| `fetch_supplier_feed` | components/catalog/catalog.py:36 | Downloads and JSON-decodes the supplier product feed from `SUPPLIER_FEED_URL` (plain `http://`, see plan.json http_sites) with a timeout (default 10 s). Network call. | None found in the repository. Its docstring says it runs nightly from cron; the cron job is not in this repo. |
| `apply_feed` | components/catalog/catalog.py:42 | Updates `price` (float) and `stock` (int) in `_PRODUCTS` for each feed item whose SKU is already known. Unknown SKUs are ignored; missing keys in an item raise `KeyError`. Mutates module state. | None found in the repository. Presumably paired with `fetch_supplier_feed` by the external nightly job. |

## Cross-component summary

- `orders` depends on `catalog.price_of` (line_total) and `catalog.in_stock` (validate).
- `get_product`, `image_url`, `fetch_supplier_feed` and `apply_feed` have no in-repo callers outside catalog.py. The last two are described as cron-driven, so an external caller is likely.

## Test coverage today (plan time)

Only `price_of` has a test (`test_price_of_known_sku`). The other five functions are untested; that belongs to pass 3.

## Notes for later passes

- Pass 2: `SUPPLIER_FEED_URL` at components/catalog/catalog.py:5 is the only `http://` site for this component.
