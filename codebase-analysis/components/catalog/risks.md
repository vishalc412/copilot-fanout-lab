# catalog: pass 2 risks

Scope: every `http://` site listed for `catalog` in `codebase-analysis/plan.json`
(one site). No source code was changed in this pass.

| file:line | URL | Decision | Reason |
|---|---|---|---|
| components/catalog/catalog.py:5 | `http://feeds.supplier-one.example.com/v2/products.json` | CHANGE | Move to `https://`. The URL is `SUPPLIER_FEED_URL`, read by `fetch_supplier_feed` (catalog.py:38) and its JSON goes to `apply_feed` (catalog.py:42), which overwrites `price` and `stock` in `_PRODUCTS`. Over plain http anyone on the network path can read or alter the feed, so they could set prices and stock levels that orders then charge and validate against (`price_of`, `in_stock`). The host is a third-party feed that this repo only consumes, and nothing in the repo makes http a requirement. The other URL in the module, `IMAGE_CDN`, is already https. |

## Notes for the change step (not done here)

- The fix is a one-line edit to `SUPPLIER_FEED_URL`. It is outside this pass and outside the write scope.
- If the supplier's host does not serve https, `urlopen` raises and the nightly fetch fails loudly (no silent bad data). That is why this is decided as CHANGE and not as a question: the failure is visible and the revert is one line. Confirm https works against the real host when the change is made.
- Nothing in this repo pins the URL: no tests, config or other callers reference it (searched the whole repository).
