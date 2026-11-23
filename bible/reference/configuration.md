# Configuration

Every constant, variable and setting the code reads. No secret value is written here. The code reads one environment variable and no configuration file.

| Key or variable | Purpose | Default | Read in | Set in (files, charts, pipeline) | Secret? |
| --- | --- | --- | --- | --- | --- |
| `PARTNER_SETTLE_URL` | Address of the payment partner's settlement endpoint | `http://partner-legacy.internal/settle` | `settle` (`components/orders/orders.py:47`) | constant in `components/orders/orders.py:9` | no |
| `DEV_SETTLE_URL` | Address of the local fake, used when `dev=True` | `http://localhost:8099/settle` | `settle` (`components/orders/orders.py:47`) | constant in `components/orders/orders.py:12` | no |
| `LOYALTY_DISCOUNT` | Loyalty discount rate | 0.05 | `order_total` (`components/orders/orders.py:29`) | constant in `components/orders/orders.py:14` | no |
| `BULK_DISCOUNT` | Bulk discount rate | 0.10 | `order_total` (`components/orders/orders.py:31`) | constant in `components/orders/orders.py:15` | no |
| `BULK_THRESHOLD` | Item count at which the bulk discount applies | 10 | `order_total` (`components/orders/orders.py:30`) | constant in `components/orders/orders.py:16` | no |
| `SUPPLIER_FEED_URL` | Address of the supplier feed | `http://feeds.supplier-one.example.com/v2/products.json` | `fetch_supplier_feed` (`components/catalog/catalog.py:38`) | constant in `components/catalog/catalog.py:5` | no |
| `IMAGE_CDN` | Prefix of product image addresses | `https://cdn.example.com/img/` | `image_url` (`components/catalog/catalog.py:33`) | constant in `components/catalog/catalog.py:6` | no |
| `settle` argument `timeout` | Seconds before the partner call gives up | 15 | `settle` (`components/orders/orders.py:50`) | default of the parameter at `components/orders/orders.py:45` | no |
| `fetch_supplier_feed` argument `timeout` | Seconds before the feed call gives up | 10 | `fetch_supplier_feed` (`components/catalog/catalog.py:38`) | default of the parameter at `components/catalog/catalog.py:36` | no |
| `ENGINE` | `copilot` or `claude`: who the fanned-out issue is for | `copilot` | `tools/fanout.sh:8` | environment of the caller; named in the usage comment at `tools/fanout.sh:3` | no |
| `<owner/repo>` argument | Target repository of `fanout.sh` | none; required (the script stops without it) | `tools/fanout.sh:7` | command line | no |
| `--pass N` argument | Run one gate pass instead of the passes in `status.json` | none | `tools/gate.py:84-92` | command line | no |
| `<component>` argument | Component to gate | none; required | `tools/gate.py:83` | command line | no |
| `ROOT` | Repository root, computed from the script's own path | the parent of `tools/` | `tools/gate.py:20`, `tools/plan.py:17` | not configurable | no |

## Files and settings outside the code

| Setting | Purpose | Where | Secret? |
| --- | --- | --- | --- |
| Python 3.12 | Interpreter in CI and in the repository instructions | `.github/workflows/copilot-setup-steps.yml:15-17`, `.github/workflows/toolkit-analysis.yml:16-18`, `.github/copilot-instructions.md:15` | no |
| `ARGS`, `S` | Shared arguments and script folder for the bible scripts in CI | `.github/workflows/toolkit-analysis.yml:8-10` | no |
| `ANTHROPIC_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN` | Repository secrets that switch on the Claude action; names only, values are never in the repository | `.github/workflows/claude.yml:32-33`, `.github/workflows/claude.yml:45-46` | yes (names only here) |
| `permissions` of each workflow | `contents: write` for `plan.yml` and `claude.yml`, `contents: read` for the others | `.github/workflows/plan.yml:4-5`, `.github/workflows/claude.yml:19-23`, `.github/workflows/analysis-gate.yml:4-5`, `.github/workflows/toolkit-analysis.yml:6-7`, `.github/workflows/copilot-setup-steps.yml:11-12` | no |
| `.gitignore` | Ignores `__pycache__/`, `*.pyc` and a third folder pattern | `.gitignore:1-3` | no |

All addresses are plain constants: to change one, edit the source. There are no profiles, no configuration server and no `.env` file (listing of the repository: none).

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
