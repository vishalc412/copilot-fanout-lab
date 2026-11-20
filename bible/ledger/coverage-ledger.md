# Coverage ledger

Depth: deep. Snapshot: 13 files in scope, 332 source lines, 2026-11-21. Inventory: `ledger/inventory.json` of 2026-11-21.

| Folder | Files | Opened | What it holds | Status | Pages |
| --- | --- | --- | --- | --- | --- |
| `components/` | 7 | 7 | The two sample components (`catalog`, `orders`) and the empty package marker | read in full | `lld/catalog/*`, `lld/orders/*` |
| `components/catalog` | 4 | 4 | Product catalog: prices, stock, supplier feed; one test file | read in full | `lld/catalog/*` |
| `components/orders` | 4 | 4 | Order totals, validation, settlement; one test file | read in full | `lld/orders/*` |
| `tools/` | 3 | 3 | The fan-out controller, plan generator and per-component gate | read in full | `lld/tools/*` |
| repository root | 3 | 3 | `README.md`, `.gitignore`, `.git` pointer file | read in full | `README.md` of the bible, `hld/02-architecture.md`, `lld/data-dictionary.md` |
| `.github` | n/a | 0 | Workflows, skills and Copilot instructions; the workflow files and two instruction files were opened and are cited as evidence in `hld/` and `reference/` | excluded (user's choice) | `hld/02-architecture.md`, `hld/05-key-flows.md` |
| `codebase-analysis` | n/a | 1 | The component lab's output; only `plan.json` exists, opened as the data file `plan.py` writes | excluded (user's choice) | `lld/data-dictionary.md` |

## Totals

| Status | Folders | Files |
| --- | --- | --- |
| read in full | 5 | 13 |
| excluded | 2 | not counted |

## Coverage from coverage.py

| Measure | Done | Total | Share | Needed |
| --- | --- | --- | --- | --- |
| Source files with a page | 7 | 7 | 100.0% | 100% |
| Symbols accounted for | 21 | 21 | 100.0% | 100% |
| Functions with a full card | 17 | 17 | 100.0% | 100% |
| Routes with an endpoint card | 0 | 0 | 100.0% | 100% |
| Citations that resolve | 1134 | 1134 | 100.0% | 98% |
| Branch lines cited in their card | 49 | 49 | 100.0% | 95% |
| Same-file calls drawn in call graphs | 9 | 9 | 100.0% | 95% |
| LLD pages with knowledge-graph front matter | 11 | 11 | 100.0% | 100% |

Result: PASS at depth deep (2026-11-21). Full report: `ledger/coverage-report.md`.
