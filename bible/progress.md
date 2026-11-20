# Progress

Run started 2026-11-21 (pass 1 of the PR thread, session 1). Depth: deep. Output folder: `bible/`.
Script arguments: `--repo . --analysis bible --exclude codebase-analysis --exclude .github`.
Version given by the user: none.

## Inventory (pass 1)

| Measure | Count |
| --- | --- |
| Files in scope | 14 |
| Source files / source lines | 10 / 332 |
| Classes and functions | 21 |
| Routes | 0 |
| Excluded folders | `.github` and `codebase-analysis` (excluded by the issue), `bible` (the output) |

## Components

Plan shown to the team in the PR description. Seven packets in all (every source file is under 400 lines and under 25 functions, so one packet per file).

| Component | Folders and files | Language | Starts by | Entry points | Packets |
| --- | --- | --- | --- | --- | --- |
| `orders` | `components/orders/orders.py`, `components/orders/test_orders.py` | Python 3 | imported as a library | `order_total`, `validate`, `settle` | 2 |
| `catalog` | `components/catalog/catalog.py`, `components/catalog/test_catalog.py` | Python 3 | imported as a library | `get_product`, `price_of`, `in_stock`, `fetch_supplier_feed`, `apply_feed` | 2 |
| `tools` | `tools/gate.py`, `tools/plan.py`, `tools/fanout.sh` | Python 3 and bash | run from the command line | `gate.py main`, `plan.py main`, `fanout.sh` | 3 |

Not planned: `components/__init__.py`, `components/catalog/__init__.py`, `components/orders/__init__.py` (empty files, 0 lines).

## Packets

| # | File | Lines | Status |
| --- | --- | --- | --- |
| 1 | `components/orders/orders.py` | 1-51 | done, page `lld/orders/orders.md`, 4 cards |
| 2 | `components/catalog/catalog.py` | 1-47 | done, page `lld/catalog/catalog.md`, 6 cards |
| 3 | `components/catalog/test_catalog.py` | 1-12 | done, page `lld/catalog/test_catalog.md` |
| 4 | `components/orders/test_orders.py` | 1-12 | done, page `lld/orders/test_orders.md` |
| 5 | `tools/gate.py` | 1-117 | done, page `lld/tools/gate.md`, 5 cards |
| 6 | `tools/plan.py` | 1-62 | done, page `lld/tools/plan.md`, 2 cards |
| 7 | `tools/fanout.sh` | 1-31 | todo (first packet of the next chat) |

Packets 1 to 6 done in session 1 (the budget of 6 per chat). `next.py` printed `NEW CHAT`.

## Coverage runs

| Date | Where | Files with page | Symbols | Cards | Citations | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-21 | end of session 1, mid-run | 6 of 7 | 21 of 21 | 17 of 17 | 338 of 338 | GAPS: `tools/fanout.sh` page, 13 required pages and the mind map still to write |

## Questions

Last question number used: none yet.

## Next step

Start the next chat with `next.py --new-session`; the first packet is `tools/fanout.sh`. Then passes 5 to 11: component README pages for `orders`, `catalog` and `tools`, the sweep, data dictionary, HLD, mind map, front page, reference pages, knowledge base, quality gate, `delta.py --init`.
