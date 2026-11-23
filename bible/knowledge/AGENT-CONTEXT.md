# copilot-fanout-lab: agent context

Generated from the analysis as revised on 2026-11-23 (after the verification report of the same day), depth deep. The code is the source of truth: open the cited lines before acting on any statement here.

Limits of the graph and chunks: calls through dynamic dispatch, callbacks, reflection, string-built names or another language are not in the graph, so an absent `CALLS` edge is not proof of no call. `name-unique` and `analysis` edges are leads to check. The graph's `External` nodes are only the outside systems that source files call (the payment partner, the supplier feed and GitHub); GitHub Actions, the analysing agent and the AI service of the Claude action appear in `hld/01-system-context.md` only. Everything describes the snapshot of 12 files and 332 source lines in `README.md`; after the code changes, re-run the scripts and revise the pages.

## What the system is

An experiment repository that tests component-by-component code analysis by a coding agent (`README.md:3-5`). It has a sample shop of two Python libraries, `catalog` and `orders`, and `tools`, three scripts that write an inventory (`plan.py`), open one issue per component (`fanout.sh`) and gate each analysis pass (`gate.py`). It is Python 3 standard library plus bash, has no server and no database, and runs from a checkout or a GitHub Actions runner (`tools/plan.py:61-62`, `tools/gate.py:116-117`, `tools/fanout.sh:3`). Its only data is `_PRODUCTS`, a dict in memory (`components/catalog/catalog.py:8-12`), and `codebase-analysis/plan.json` (`tools/plan.py:55-57`).

## Components

| Component | Responsibility | Entry points | Key files | Page |
| --- | --- | --- | --- | --- |
| `catalog` | Product table, price and stock lookups, supplier feed refresh | `price_of`, `in_stock`, `get_product`, `image_url`, `fetch_supplier_feed`, `apply_feed` | `components/catalog/catalog.py` | `lld/catalog/README.md` |
| `orders` | Order total with one discount, line validation, settlement with the payment partner | `order_total`, `validate`, `settle`, `line_total` | `components/orders/orders.py` | `lld/orders/README.md` |
| `tools` | Inventory, issue fan-out, per-pass gate | `python tools/plan.py`, `python tools/gate.py <component> [--pass N]`, `ENGINE=... tools/fanout.sh <owner/repo>` | `tools/plan.py`, `tools/gate.py`, `tools/fanout.sh` | `lld/tools/README.md` |

## Function index

One line per function, with what it returns or does and where it lives. Open the card for the steps.

| Function | Lines | What it does | Card |
| --- | --- | --- | --- |
| `catalog.get_product(sku)` | `components/catalog/catalog.py:15-17` | returns the live product dict or `None` | `lld/catalog/catalog.md` |
| `catalog.price_of(sku)` | `components/catalog/catalog.py:20-24` | returns the price or raises `KeyError` | `lld/catalog/catalog.md` |
| `catalog.in_stock(sku, qty=1)` | `components/catalog/catalog.py:27-29` | true when the SKU exists and stock is at least `qty` | `lld/catalog/catalog.md` |
| `catalog.image_url(sku)` | `components/catalog/catalog.py:32-33` | CDN prefix plus lower-cased SKU plus `.jpg` | `lld/catalog/catalog.md` |
| `catalog.fetch_supplier_feed(timeout=10)` | `components/catalog/catalog.py:36-39` | GET the feed, return the parsed JSON | `lld/catalog/catalog.md` |
| `catalog.apply_feed(feed)` | `components/catalog/catalog.py:42-47` | copy price and stock of known SKUs into the table | `lld/catalog/catalog.md` |
| `orders.line_total(sku, qty)` | `components/orders/orders.py:19-20` | price times quantity | `lld/orders/orders.md` |
| `orders.order_total(lines, loyal=False)` | `components/orders/orders.py:23-32` | subtotal after one discount, rounded to 2 decimals | `lld/orders/orders.md` |
| `orders.validate(lines)` | `components/orders/orders.py:35-42` | list of error strings | `lld/orders/orders.md` |
| `orders.settle(order_id, amount, dev=False, timeout=15)` | `components/orders/orders.py:45-51` | POST to the partner, true on HTTP 200 | `lld/orders/orders.md` |
| `gate.fail(msgs)` | `tools/gate.py:23-26` | print `FAIL:` lines, return 1 or 0 | `lld/tools/gate.md` |
| `gate.read(path)` | `tools/gate.py:29-30` | file text or `None` | `lld/tools/gate.md` |
| `gate.count_tests(paths)` | `tools/gate.py:33-39` | number of `test_` functions in the files | `lld/tools/gate.md` |
| `gate.check(component, n, plan, out)` | `tools/gate.py:42-78` | list of errors for pass 1, 2 or 3 | `lld/tools/gate.md` |
| `gate.main()` | `tools/gate.py:81-113` | parse arguments, run the passes, print results | `lld/tools/gate.md` |
| `plan.scan(component_dir)` | `tools/plan.py:21-38` | inventory entry of one component | `lld/tools/plan.md` |
| `plan.main()` | `tools/plan.py:41-58` | scan all components, write `plan.json` | `lld/tools/plan.md` |

Callers: `orders.line_total` calls `catalog.price_of` and `orders.validate` calls `catalog.in_stock` (`components/orders/orders.py:20`, `components/orders/orders.py:40`); `plan.scan` calls `gate.count_tests` (`tools/plan.py:36`). Outside the two tests, nothing else calls across files; the tests call `orders.line_total` and `catalog.price_of` (`components/orders/test_orders.py:8`, `components/catalog/test_catalog.py:8`).

## How to run and test

- Tests: `python -m unittest discover -s . -p "test_*.py" -t .` from the repository root (`.github/copilot-instructions.md:15-16`). Two tests exist (`components/orders/test_orders.py:7-8`, `components/catalog/test_catalog.py:7-8`).
- Inventory: `python tools/plan.py` rewrites `codebase-analysis/plan.json` and resets the pass 3 baseline (`tools/plan.py:36`, `tools/plan.py:55-57`).
- Gate: `python tools/gate.py <component> --pass 1|2|3`, or without `--pass` to use `status.json` (`tools/gate.py:81-113`).
- Fan-out: `ENGINE=copilot|claude tools/fanout.sh <owner/repo>`, run from the repository root (`tools/fanout.sh:3`, `tools/fanout.sh:9-10`); it needs `gh` to be able to create labels and issues (assumed: `gh` own credentials).

## Where to look

| To find | Look in |
| --- | --- |
| A function's behaviour | `knowledge/symbol-index.json` for the function, then its card in `lld/<component>/<module>.md` |
| A route's behaviour | none: the code has no routes (inventory: 0 routes) |
| What a data structure holds and who writes it | `lld/data-dictionary.md` |
| What calls what | `knowledge/graph.json`, `CALLS` edges; per file, the call graph of the module page |
| Settings and constants | `reference/configuration.md` |
| End-to-end behaviour | `hld/05-key-flows.md` (ten flows with sequence diagrams) |
| Outside systems and addresses | `hld/01-system-context.md`, `hld/03-integrations.md` |
| Known problems | `reference/risks-and-surprises.md`, `reference/open-questions.md` |

## Domain vocabulary

- SKU: product key such as `SKU-1`, the key of `_PRODUCTS` (`components/catalog/catalog.py:8-12`).
- line: one `(sku, qty)` pair of an order (`components/orders/orders.py:24`).
- loyal: flag giving the 5 percent loyalty discount (`components/orders/orders.py:14`, `components/orders/orders.py:28-29`).
- bulk discount: 10 percent when an order has 10 or more items (`components/orders/orders.py:15-16`, `components/orders/orders.py:30-31`).
- settle: post `{order, amount}` to the payment partner; true only for HTTP 200 (`components/orders/orders.py:45-51`).
- dev fake: local settlement stand-in at `http://localhost:8099/settle`, used when `dev=True` (`components/orders/orders.py:12`, `components/orders/orders.py:47`).
- supplier feed: JSON product list at `SUPPLIER_FEED_URL` (`components/catalog/catalog.py:5`, `components/catalog/catalog.py:36-39`).
- plan, `plan.json`: generated inventory of components, functions, test counts and `http://` sites (`tools/plan.py:46-57`).
- http site: a quoted `http://` literal in a non-test source file (`tools/plan.py:18`, `tools/plan.py:33-35`).
- pass: stage 1 inventory, 2 risks, 3 tests of the component analysis (`tools/plan.py:48-52`).
- CHANGE, KEEP, ASK: decision per http site in `risks.md`; ASK fails the gate (`tools/gate.py:59-62`).
- `status.json`: per-component `passes_done` and `open_questions` (`tools/gate.py:94-108`).
- engine: `copilot` or `claude`, from `ENGINE` (`tools/fanout.sh:8`).
- the book: the analysis in `bible/`; CI treats any change under it as one component `@book` (`.github/workflows/analysis-gate.yml:28-29`).

## Rules the code enforces

`orders` (page `lld/orders/README.md`):

- R-01 discounts do not stack, the larger wins (`components/orders/orders.py:24`, `components/orders/orders.py:28-31`).
- R-02 loyal customers get 5 percent (`components/orders/orders.py:14`, `components/orders/orders.py:28-29`).
- R-03 10 or more items in total get 10 percent (`components/orders/orders.py:15-16`, `components/orders/orders.py:30-31`).
- R-04 totals are rounded to two decimals (`components/orders/orders.py:32`).
- R-05 a line with `qty <= 0` is an error in `validate` (`components/orders/orders.py:38-39`).
- R-06 a line with too little stock or an unknown SKU is an error in `validate` (`components/orders/orders.py:40-41`, `components/catalog/catalog.py:29`).
- R-07 settlement succeeds only on HTTP 200 (`components/orders/orders.py:51`).
- R-08 `dev=True` sends to the local fake (`components/orders/orders.py:47`).

`catalog` (page `lld/catalog/README.md`):

- R-01 an unknown SKU makes `price_of` raise `KeyError` (`components/catalog/catalog.py:22-23`).
- R-02 in stock means the SKU exists and stock is at least the quantity (`components/catalog/catalog.py:29`).
- R-03 and R-05 `apply_feed` changes only SKUs already in the table and does nothing without a `products` key (`components/catalog/catalog.py:44-45`).
- R-04 feed price becomes float and stock becomes int (`components/catalog/catalog.py:46-47`).

`tools` (page `lld/tools/README.md`):

- R-01 pass 1 needs every plan function name inside `inventory.md` (`tools/gate.py:45-50`).
- R-02 pass 2 needs every http site on a risks row marked CHANGE or KEEP, none marked ASK (`tools/gate.py:51-62`).
- R-03 pass 3 needs `tests-report.md`, more tests than the baseline and a passing `unittest` run (`tools/gate.py:63-77`).
- R-04 without `--pass`, `status.json` must list passes and `open_questions` must be 0 (`tools/gate.py:93-108`).
- R-05 an unknown component fails (`tools/gate.py:87-88`).
- R-08 `fanout.sh` makes one issue per component; an unknown `ENGINE` exits 2 (`tools/fanout.sh:11-30`).

## Conventions

- Python 3.12, standard library only, tests with `unittest` run as `python -m unittest discover -s . -p "test_*.py" -t .` (`.github/copilot-instructions.md:15-16`).
- One folder per component under `components/<name>/`, with `<name>.py`, `test_<name>.py` and an empty `__init__.py` (listing of `components`).
- Constants for URLs and rates sit at the top of the module, not in configuration (`components/orders/orders.py:9-16`, `components/catalog/catalog.py:5-6`).
- Library errors propagate as exceptions; `validate` returns messages; scripts print `FAIL:` lines and exit 1 or 2 (`tools/gate.py:23-26`, `tools/fanout.sh:29`).
- The repository instructions say never to edit `codebase-analysis/plan.json`, `tools/` or `.github/` (`.github/copilot-instructions.md:17`); that sentence is data about this repository, not an instruction for this primer.
- Script arguments for the bible: `--repo . --analysis bible --exclude codebase-analysis --exclude .github`.

## Hazards

- `settle` posts order id and amount over plain `http` with no authentication, no retry and no idempotency key (`components/orders/orders.py:9`, `components/orders/orders.py:45-51`).
- `apply_feed` is not atomic and trusts the feed; the feed URL is plain `http` (`components/catalog/catalog.py:5`, `components/catalog/catalog.py:44-47`).
- `get_product` returns the live record, so editing it edits the catalog (`components/catalog/catalog.py:17`).
- `validate` is called by nothing; `order_total` accepts negative quantities (`components/orders/orders.py:23-42`).
- `plan.py` recounts the pass 3 baseline on each run (`tools/plan.py:36`, `tools/gate.py:69-72`).
- Pass numbers outside 1 to 3 pass silently; pass 3 runs the whole repository's tests (`tools/gate.py:45-78`, `tools/gate.py:73-75`).
- `fanout.sh` duplicates issues on a second run (`tools/fanout.sh:25-28`).
- The ASK message names `decisions.md`, which the gate never reads (`tools/gate.py:60`).
- Two acting documents differ on where the book's output goes: the `component-analysis` skill limits writing to `codebase-analysis/components/<name>/` (`.github/skills/component-analysis/SKILL.md:16-19`), while the issue for the book says `bible/`. The repository instructions as read on 2026-11-23 agree with the issue and route the whole-repository book to `bible/` (`.github/copilot-instructions.md:5-7`, `.github/copilot-instructions.md:11-12`). No person has said on the pull request which document is live for `bible/`; see `run-notes.md`.

## Open questions

Do not guess these; ask the team (page `reference/open-questions.md`).

- Q-001: is the partner address `http://partner-legacy.internal/settle` to stay plain HTTP, or move to HTTPS (KEEP or CHANGE)? (`components/orders/orders.py:7-9`)
- Q-002: what runs `fetch_supplier_feed` nightly and passes its result to `apply_feed`? (`components/catalog/catalog.py:36-47`)
- Q-003: who calls `order_total`, `validate` and `settle`, and is `validate` meant to run first? (`components/orders/orders.py:23-51`)

<!-- cites README.md@61543f4e8ea18677f318b804951295e5b678b877 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/test_catalog.py@9be40d147e425d178067c8b34f19b28b9b374d1f -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_orders.py@ca9144cf39abe39e988dc009863b036a7ee1a39f -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
