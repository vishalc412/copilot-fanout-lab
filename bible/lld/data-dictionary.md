---
id: lld/data-dictionary
kind: data-dictionary
summary: The one in-memory product table, the plan.json inventory and the analysis files the gate reads
reads: [store:_PRODUCTS, file:codebase-analysis/plan.json, file:codebase-analysis/components/*/status.json, file:codebase-analysis/components/*/inventory.md, file:codebase-analysis/components/*/risks.md, file:codebase-analysis/components/*/tests-report.md]
writes: [store:_PRODUCTS, file:codebase-analysis/plan.json]
---
# Data dictionary

The system has no database. Its data is one in-memory dict, one generated JSON file and four analysis files that the gate reads. This page lists each with the code that reads and writes it (search `sqlite`, `CREATE TABLE`, `execute` in `*.py` and `*.sh` under `components` and `tools`: 0 hits).

## Stores

| Store | Technology | Location or connection from | Owned by | Evidence |
| --- | --- | --- | --- | --- |
| `_PRODUCTS` | Python dict in process memory, lost at exit | module variable built at import | `catalog` | `components/catalog/catalog.py:8-12` |

No file, cache, bucket or share is used as a store by the sample code (search `.write(`, `read_text`, `open(` other than `urlopen` in `components/*.py`: 0 hits).

## `_PRODUCTS`: records

### `_PRODUCTS` (dict keyed by SKU)

Defined in `components/catalog/catalog.py:8-12`. Written by `apply_feed` (`components/catalog/catalog.py:46-47`). Read by `get_product` (`components/catalog/catalog.py:17`), and through it by `price_of`, `in_stock` and, in `orders`, `line_total` and `validate`. The dict is built at import with three entries and never grows (inferred: no assignment of a new key in `components/catalog/catalog.py:42-47`).

| Field | Type | Null | Key | Default | Meaning | Set by | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dict key | string | no | key | none | The SKU: `SKU-1`, `SKU-2`, `SKU-3` | the literal | `components/catalog/catalog.py:9-11` |
| `name` | string | no | | none | Product name: Kettle, Toaster, Mug | the literal only; `apply_feed` never changes it | `components/catalog/catalog.py:9-11` |
| `price` | float | no | | 24.0, 39.5, 6.0 | Unit price | the literal, then `apply_feed` as `float(item["price"])` | `components/catalog/catalog.py:9-11`, `components/catalog/catalog.py:46` |
| `stock` | int | no | | 12, 0, 140 | Units on hand | the literal, then `apply_feed` as `int(item["stock"])` | `components/catalog/catalog.py:9-11`, `components/catalog/catalog.py:47` |

The three entries in order, as price and stock: Kettle 24.0 and 12, Toaster 39.5 and 0, Mug 6.0 and 140 (`components/catalog/catalog.py:9-11`).

### Supplier feed (input, not stored)

`fetch_supplier_feed` returns the parsed JSON of `SUPPLIER_FEED_URL` (`components/catalog/catalog.py:36-39`). The fields `apply_feed` uses are:

| Field | Used as | Required | Evidence |
| --- | --- | --- | --- |
| `products` | list of items; a missing key means no items | no | `components/catalog/catalog.py:44` |
| `products[].sku` | key into `_PRODUCTS`; unknown SKUs are skipped | yes, a missing key raises `KeyError` (inferred: direct indexing) | `components/catalog/catalog.py:45` |
| `products[].price` | converted with `float` and stored as `price` | yes (inferred: direct indexing) | `components/catalog/catalog.py:46` |
| `products[].stock` | converted with `int` and stored as `stock` | yes (inferred: direct indexing) | `components/catalog/catalog.py:47` |

### Order lines and settlement message (in-flight data)

| Name | Shape | Used by | Evidence |
| --- | --- | --- | --- |
| order lines | list of `(sku, qty)` pairs | `order_total`, `validate` | `components/orders/orders.py:24`, `components/orders/orders.py:25-26`, `components/orders/orders.py:37` |
| validation errors | list of strings `"<sku>: quantity must be positive"` or `"<sku>: not enough stock"` | `validate` | `components/orders/orders.py:39`, `components/orders/orders.py:41` |
| settlement request body | JSON `{"order": <order_id>, "amount": <amount>}`, header `Content-Type: application/json`, POST | `settle` | `components/orders/orders.py:48-49` |
| settlement result | boolean: the partner answered HTTP 200 | `settle` | `components/orders/orders.py:51` |

None of these is persisted.

## Files read and written

### `codebase-analysis/plan.json`

Written by `plan.main` (`tools/plan.py:55-57`). Read by `gate.main` (`tools/gate.py:86`) and `fanout.sh` (`tools/fanout.sh:9`). Its top-level keys and what the code uses:

| Key | Type | Used as | Evidence |
| --- | --- | --- | --- |
| `version` | int, 1 | written only | `tools/plan.py:47` |
| `passes` | map `"1"`, `"2"`, `"3"` to a text | written only; no reader in the repository (search `passes` in `*.py` and `*.sh`: the gate reads `passes_done` from `status.json`, not this key) | `tools/plan.py:48-52`, `tools/gate.py:101` |
| `components` | map component name to its entry | gate checks the name (`tools/gate.py:87`); `fanout.sh` lists the names (`tools/fanout.sh:9`) | `tools/plan.py:53` |
| `components.<name>.sources` | list of repository paths | written only | `tools/plan.py:37` |
| `components.<name>.tests` | list of repository paths | used by `gate.check` pass 3 when `test_count` is absent | `tools/gate.py:69` |
| `components.<name>.test_count` | int | pass 3 baseline | `tools/gate.py:69-72` |
| `components.<name>.functions` | list of `{name, at}`, `at` is `path:line` | pass 1 | `tools/gate.py:49-50` |
| `components.<name>.http_sites` | list of `{url, at}` | pass 2 | `tools/gate.py:55-62` |

Current content: two components, `catalog` (6 functions, 1 http site, test count 1) and `orders` (4 functions, 2 http sites, test count 1) (`codebase-analysis/plan.json:9-86`).

### Analysis files read by the gate

All sit in `codebase-analysis/components/<name>/`, are written by the analysing agent and are not present in this checkout (listing of `codebase-analysis`: only `plan.json`).

| File | Read by | What the gate needs in it | Evidence |
| --- | --- | --- | --- |
| `status.json` | `gate.main`, only when `--pass` is not given | JSON object with `passes_done` (non-empty list of pass numbers) and `open_questions` (integer, 0 or more); any number above 0 blocks the gate | `tools/gate.py:94-108` |
| `inventory.md` | `gate.check`, pass 1 | contains the name of each function of the plan | `tools/gate.py:46-50` |
| `risks.md` | `gate.check`, pass 2 | a line with each site's `file:line`, containing CHANGE or KEEP and none containing ASK | `tools/gate.py:52-62` |
| `tests-report.md` | `gate.check`, pass 3 | must exist; its content is not read | `tools/gate.py:64-65` |

### `.gitignore`

Three patterns: `__pycache__/`, `*.pyc` and a third folder pattern (`.gitignore:1-3`). It controls what is committed, not what the code reads. The third pattern is left unnamed on purpose: a comment on this pull request (2026-11-20) asked for references to the retired run-harness folder to be removed from `bible/`; the pattern is at `.gitignore:3` for anyone who needs it (revision item N-03).

## Status and enum values

| Field | Value | Set by | Meaning |
| --- | --- | --- | --- |
| `ENGINE` | `copilot` | default (`tools/fanout.sh:8`) | issue assigned to `@copilot` (`tools/fanout.sh:25-26`) |
| `ENGINE` | `claude` | the caller | issue labelled `agent:claude` (`tools/fanout.sh:27-28`) |
| risk decision in `risks.md` | `CHANGE`, `KEEP`, `ASK` | the analysing agent | `ASK` fails the gate; `CHANGE` or `KEEP` passes it (`tools/gate.py:59-62`) |
| gate output | `PASS`, `FAIL` | `gate.main` | per-pass result line (`tools/gate.py:111`) |
| discount rates | 0.05 loyalty, 0.10 bulk, threshold 10 items | constants | `components/orders/orders.py:14-16` |

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
