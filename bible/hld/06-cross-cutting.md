# Cross-cutting concerns

Each section says what the system does in plain words. The system is small, so most concerns are "absent" in the code; that is a finding, not a gap in the analysis.

## Authentication and authorisation

The Python code authenticates nothing: no function checks who calls it, and the two outbound HTTP calls send no authentication header (`components/orders/orders.py:49`, `components/catalog/catalog.py:38`; search `Authorization`, `Bearer`, `jwt`, `api_key` in `*.py` and `*.sh`: 0 hits). The access control found is outside the code: the `claude.yml` workflow reacts only to comments by an owner, member or collaborator (`.github/workflows/claude.yml:11-13`), and `fanout.sh` relies on the operator's own `gh` login (assumed).

Consistency: absent in the code.

## Secrets

No secret appears in the code, and none is read from the environment by it. The `claude.yml` workflow reads two repository secrets by name, `ANTHROPIC_API_KEY` and `CLAUDE_CODE_OAUTH_TOKEN`, and runs the Claude action only when one of them is set (`.github/workflows/claude.yml:29-36`, `.github/workflows/claude.yml:42-46`). Values are never written in this analysis.

Consistency: same everywhere (nothing stored in the repository).

## Configuration

Configuration is constants in source files and one environment variable. The URLs and discount rates are module constants (`components/orders/orders.py:9-16`, `components/catalog/catalog.py:5-6`); `ENGINE` is the one environment variable (`tools/fanout.sh:8`). There are no environments or profiles; the `dev` argument of `settle` selects a local fake address at call time (`components/orders/orders.py:47`). See `reference/configuration.md`.

Consistency: varies (2 variants): constants in the library, an environment variable and arguments in the tools.

## Error handling

Errors are mostly not handled. The library raises `KeyError` for an unknown SKU and lets `urllib` and `json` errors escape (`components/catalog/catalog.py:22-23`, `components/catalog/catalog.py:36-39`, `components/orders/orders.py:50`). `validate` is the one function that turns bad input into values, a list of messages (`components/orders/orders.py:35-42`). The tools report failure as printed `FAIL:` lines and exit code 1, and `gate.py` handles bad `status.json` explicitly (`tools/gate.py:23-26`, `tools/gate.py:95-103`); `fanout.sh` stops at the first failure and exits 2 for an unknown engine (`tools/fanout.sh:6`, `tools/fanout.sh:29`).

Consistency: varies (3 variants): exceptions in the library, messages in `validate`, exit codes in the tools.

| Component | How | Evidence |
| --- | --- | --- |
| `catalog` | exceptions propagate | `components/catalog/catalog.py:23`, `components/catalog/catalog.py:36-39` |
| `orders` | exceptions propagate, except `validate` which returns messages | `components/orders/orders.py:25`, `components/orders/orders.py:35-42` |
| `tools` | printed FAIL lines and exit codes | `tools/gate.py:23-26`, `tools/fanout.sh:29` |

## Resilience

There is none: no retry, circuit breaker, fallback or queue. Both HTTP calls have a timeout (15 seconds for `settle`, 10 for the feed) and nothing else (`components/orders/orders.py:45`, `components/catalog/catalog.py:36`; search `retry`, `backoff`, `circuit` in `*.py` and `*.sh`: 0 hits). `apply_feed` is not atomic, so a bad feed item leaves earlier items applied (`components/catalog/catalog.py:44-47`). `fanout.sh` is not idempotent for issues (`tools/fanout.sh:25-28`). The pass 3 test run in `gate.py` has no timeout (`tools/gate.py:73-75`).

Consistency: absent.

## Logging, metrics and tracing

No logging, metrics or tracing in the code (search `logging`, `print(` in `components`: 0 hits; `print` in `tools`: the result lines of `gate.py` and `plan.py`, `tools/gate.py:25`, `tools/gate.py:111`, `tools/plan.py:58`). There is no health check or dashboard. The Claude workflow echoes that a mention reached Actions (`.github/workflows/claude.yml:25-28`).

Consistency: absent in the library; printed result lines only in the tools.

## Build and deployment

There is nothing to build or deploy: no package file, no container, no release step (listing of the repository: none). CI runs the scripts on GitHub-hosted runners with Python 3.12 (`.github/workflows/copilot-setup-steps.yml:10-17`, `.github/workflows/toolkit-analysis.yml:13-18`). `plan.yml` commits `codebase-analysis/plan.json` to the repository with a bot identity when it changed (`.github/workflows/plan.yml:15-24`). The pipeline is drawn in `hld/02-architecture.md`.

Consistency: same everywhere (CI only).

## Testing

Two unittest files, one test each, `line_total("SKU-3", 2)` and `price_of("SKU-1")` (`components/orders/test_orders.py:7-8`, `components/catalog/test_catalog.py:7-8`). No test touches discounts, validation, settlement, the feed or any of the tools (inferred: only those calls appear in the two test files). The gate's pass 3 runs the whole suite with `python -m unittest discover` (`tools/gate.py:73-75`), and the repository instructions give the same command (`.github/copilot-instructions.md:15-16`). No network is used by the tests (inferred: `settle` and `fetch_supplier_feed` are not called by them).

Consistency: same everywhere (one-test files in each component, none in `tools`).

## Dependencies

No third-party Python package is used: every import is standard library or a repository module (imports at `components/orders/orders.py:2-5`, `components/catalog/catalog.py:2-3`, `tools/gate.py:13-18`, `tools/plan.py:8-15`). External programs: `gh` and `python3` for `fanout.sh` (`tools/fanout.sh:9-10`). CI uses four GitHub Actions at fixed major versions (`.github/workflows/toolkit-analysis.yml:15-16`, `.github/workflows/toolkit-analysis.yml:28`, `.github/workflows/claude.yml:42`).

Consistency: same everywhere.

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/test_catalog.py@9be40d147e425d178067c8b34f19b28b9b374d1f -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_orders.py@ca9144cf39abe39e988dc009863b036a7ee1a39f -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
