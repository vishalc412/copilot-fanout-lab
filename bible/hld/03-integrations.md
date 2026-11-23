# Integrations

Every way into and out of the system. There is no network listener: the inbound interfaces are command lines and one importable library; the outbound connections are two HTTP calls in library functions that nothing calls, one GitHub call through the `gh` command, and one child process.

## Inbound interfaces

| Component | Interface | Kind | Exposed to | Authentication | Card |
| --- | --- | --- | --- | --- | --- |
| `tools` | `python tools/plan.py` | command line | operator, the `plan.yml` workflow | none | [card](../lld/tools/plan.md#main) |
| `tools` | `python tools/gate.py <component> [--pass N]` | command line, exit code 0 or 1 | operator, the `analysis-gate.yml` workflow, the Copilot setup check (`--help`) | none | [card](../lld/tools/gate.md#main) |
| `tools` | `ENGINE=copilot\|claude tools/fanout.sh <owner/repo>` | command line | operator (inferred: usage comment at `tools/fanout.sh:3`) | the operator's `gh` login (assumed) | [walkthrough](../lld/tools/fanout.md#script-walkthrough) |
| `orders` | `line_total`, `order_total`, `validate`, `settle` | Python functions | any importer; only its test imports it in this repository | none | [orders page](../lld/orders/orders.md#functions-and-methods) |
| `catalog` | `get_product`, `price_of`, `in_stock`, `image_url`, `fetch_supplier_feed`, `apply_feed` | Python functions | `orders` and the catalog test | none | [catalog page](../lld/catalog/catalog.md#functions-and-methods) |

Evidence: `tools/plan.py:61-62`, `tools/gate.py:81-117`, `tools/fanout.sh:3-8`, `.github/workflows/plan.yml:14`, `.github/workflows/analysis-gate.yml:53`, `.github/workflows/copilot-setup-steps.yml:18-19`, `components/orders/orders.py:19-51`, `components/catalog/catalog.py:15-47`, `components/orders/test_orders.py:3`, `components/orders/orders.py:5`.

There are no HTTP routes, queues or scheduled jobs (inventory: 0 routes; search `@app.route`, `Kafka`, `@Scheduled`, `celery` in `*.py` and `*.sh`: 0 hits; the one `cron` hit is a docstring at `components/catalog/catalog.py:37`, see `Q-002`).

## Outbound connections

| From | To | Purpose | Protocol | Scheme | Port | Address from | Authentication | Timeout, retry | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `orders.settle` | Payment partner settlement endpoint | Post `{order, amount}` as JSON and report whether the answer is HTTP 200 | HTTP POST | `http` | 80 implied (inferred: no port in the URL) | `PARTNER_SETTLE_URL` in `components/orders/orders.py:9` | none sent | timeout 15 seconds by default; no retry | `components/orders/orders.py:9`, `components/orders/orders.py:45-51` |
| `orders.settle` with `dev=True` | Local settlement fake | same body, developer use | HTTP POST | `http` | 8099 | `DEV_SETTLE_URL` in `components/orders/orders.py:12` | none sent | same as above | `components/orders/orders.py:11-12`, `components/orders/orders.py:47` |
| `catalog.fetch_supplier_feed` | Supplier product feed | Download `products.json` and parse it | HTTP GET | `http` | 80 implied | `SUPPLIER_FEED_URL` in `components/catalog/catalog.py:5` | none sent | timeout 10 seconds by default; no retry | `components/catalog/catalog.py:5`, `components/catalog/catalog.py:36-39` |
| `fanout.sh` | GitHub, through `gh` | Create the labels `agent:claude` and `component:<name>`, and one issue per component | whatever `gh` uses (assumed: HTTPS REST) | not stated in the repository | not stated | first argument `<owner/repo>` | `gh` login (assumed) | none; stops at the first failure (`set -euo pipefail`) | `tools/fanout.sh:6`, `tools/fanout.sh:7`, `tools/fanout.sh:10-28` |
| `gate.check` pass 3 | child process `python -m unittest discover` | Run the repository tests | process | not applicable | not applicable | `sys.executable` | none | no timeout | `tools/gate.py:73-75` |
| `orders` | `catalog` | Price and stock lookups | in-process call | not applicable | not applicable | import `components.catalog.catalog` | none | none | `components/orders/orders.py:5`, `components/orders/orders.py:20`, `components/orders/orders.py:40` |

All three HTTP addresses are plain `http`. The settlement endpoint carries order ids and amounts without TLS and without an authentication header; the comment next to it says the partner has said TLS is "coming soon" (`components/orders/orders.py:7-9`, `components/orders/orders.py:48-49`). Whether to change the scheme depends on the partner; it is recorded as `Q-001`. The addresses are constants in the source, not configuration: changing one means editing code.

Where an address goes through a logical name: none. The host names `partner-legacy.internal` and `feeds.supplier-one.example.com` are literals; no DNS, registry or gateway file in the repository resolves them (search `partner-legacy` and `supplier-one` outside the two source files and `plan.json`: 0 hits).

## Dependency matrix

Rows call columns. `x` marks a call read in the code, `?` an inferred one.

| From \ To | catalog | orders | plan.json | Payment partner | Supplier feed | GitHub | unittest |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `orders` | x | | | x | | | |
| `catalog` | | | | | x | | |
| `plan.py` | x (scans source) | x (scans source) | x (writes) | | | | |
| `gate.py` | x (counts tests) | x (counts tests) | x (reads) | | | | x |
| `fanout.sh` | | | x (reads) | | | ? | |

Evidence: `components/orders/orders.py:20`, `components/orders/orders.py:40`, `components/orders/orders.py:50`, `components/catalog/catalog.py:38`, `tools/plan.py:43-45`, `tools/plan.py:55-57`, `tools/gate.py:66-67`, `tools/gate.py:73-75`, `tools/gate.py:86`, `tools/fanout.sh:9`, `tools/fanout.sh:25-28`.

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_orders.py@ca9144cf39abe39e988dc009863b036a7ee1a39f -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
