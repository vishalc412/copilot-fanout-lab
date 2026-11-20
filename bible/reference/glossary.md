# Glossary

| Term | Meaning in this system | Where it appears |
| --- | --- | --- |
| SKU | Product key such as `SKU-1`; the key of the `_PRODUCTS` dict | `components/catalog/catalog.py:8-12` |
| `_PRODUCTS` | The in-memory product table: name, price and stock per SKU | `lld/catalog/catalog.md`, `lld/data-dictionary.md` |
| line | One `(sku, qty)` pair of an order | `components/orders/orders.py:24` |
| loyal | Flag on `order_total` that earns the 5 percent loyalty discount | `components/orders/orders.py:23`, `components/orders/orders.py:28-29` |
| bulk discount | 10 percent off when an order has 10 or more items in total | `components/orders/orders.py:15-16`, `components/orders/orders.py:30-31` |
| settle, settlement | Telling the payment partner that an order is paid for an amount | `components/orders/orders.py:45-51` |
| payment partner | The outside system at `PARTNER_SETTLE_URL` | `components/orders/orders.py:7-9` |
| dev fake | The local stand-in for the partner at `DEV_SETTLE_URL`, port 8099, selected by `dev=True` | `components/orders/orders.py:11-12`, `components/orders/orders.py:47` |
| supplier feed | The JSON product list at `SUPPLIER_FEED_URL` | `components/catalog/catalog.py:5`, `components/catalog/catalog.py:36-39` |
| component | A folder under `components/`; the plan has one entry per component | `tools/plan.py:43-45` |
| plan, `plan.json` | The generated inventory of components, functions, test counts and `http://` sites | `tools/plan.py:46-57`, `lld/data-dictionary.md` |
| http site | A quoted `http://` string in a non-test source file, listed by `plan.py` with `file:line` | `tools/plan.py:18`, `tools/plan.py:33-35` |
| fan-out | Opening one issue per component, each analysed on its own pull request | `tools/fanout.sh:2`, `README.md:3-4` |
| pass | One stage of the component analysis: 1 inventory, 2 risks, 3 tests | `tools/plan.py:48-52`, `tools/gate.py:7-11` |
| gate | `tools/gate.py`: the pass and fail check on the analysis files | `tools/gate.py:1-12` |
| CHANGE, KEEP, ASK | Decisions per http site in `risks.md`; `ASK` blocks the gate | `tools/gate.py:59-62` |
| `status.json` | Per-component file with `passes_done` and `open_questions` | `tools/gate.py:94-108` |
| engine | `copilot` or `claude`, chosen with `ENGINE`: who the issue is for | `tools/fanout.sh:3-5`, `tools/fanout.sh:8` |
| the book, the bible | The analysis in `bible/`; the CI treats any change under it as one component, `@book` | `.github/workflows/analysis-gate.yml:28-29` |
| `codebase-analysis/` | The folder of the component lab; holds `plan.json` | `codebase-analysis/plan.json:1`, `tools/plan.py:55` |

<!-- cites README.md@61543f4e8ea18677f318b804951295e5b678b877 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
