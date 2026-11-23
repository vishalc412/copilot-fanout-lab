# Coverage ledger

Depth: deep. Snapshot: 12 files in scope, 332 source lines, 2026-11-23. Inventory: `ledger/inventory.json` of 2026-11-23 (revision pass). The first run counted 13 files because a `.git` pointer file was in that checkout; the inventory script now skips `.git` (V-016, V-023).

| Folder | Files | Opened | What it holds | Status | Pages |
| --- | --- | --- | --- | --- | --- |
| `components/` | 7 | 7 | The two sample components (`catalog`, `orders`) and the empty package marker | read in full | `lld/catalog/*`, `lld/orders/*` |
| `components/catalog` | 3 | 3 | Product catalog: prices, stock, supplier feed; one test file | read in full | `lld/catalog/*` |
| `components/orders` | 3 | 3 | Order totals, validation, settlement; one test file | read in full | `lld/orders/*` |
| `tools/` | 3 | 3 | The fan-out controller, plan generator and per-component gate | read in full | `lld/tools/*` |
| repository root | 2 | 2 | `README.md`, `.gitignore` | read in full | `README.md` of the bible, `hld/02-architecture.md`, `lld/data-dictionary.md` |
| `.github` | n/a | 0 | Workflows, skills and Copilot instructions; the workflow files and two instruction files were opened and are cited as evidence in `hld/` and `reference/` | excluded (user's choice) | `hld/02-architecture.md`, `hld/05-key-flows.md` |
| `.git` | n/a | 0 | Version-control folder; skipped by `inventory.py` as a tool folder. Not opened and not described; source control is left to a person | excluded (the script's rule) | none |
| `codebase-analysis` | n/a | 1 | The component lab's output; only `plan.json` exists, opened as the data file `plan.py` writes | excluded (user's choice) | `lld/data-dictionary.md` |

## Totals

| Status | Folders | Files |
| --- | --- | --- |
| read in full | 5 | 12 (the folder rows overlap: `components/` holds the two component folders) |
| excluded | 3 | not counted |

## Coverage from coverage.py

| Measure | Done | Total | Share | Needed |
| --- | --- | --- | --- | --- |
| Source files with a page | 7 | 7 | 100.0% | 100% |
| Symbols accounted for | 21 | 21 | 100.0% | 100% |
| Functions with a full card | 17 | 17 | 100.0% | 100% |
| Routes with an endpoint card | 0 | 0 | 100.0% | 100% |
| Citations that resolve | 1209 | 1209 | 100.0% | 98% |
| Branch lines cited in their card | 49 | 49 | 100.0% | 95% |
| Same-file calls drawn in call graphs | 9 | 9 | 100.0% | 95% |
| LLD pages with knowledge-graph front matter | 11 | 11 | 100.0% | 100% |

Result: PASS at depth deep (2026-11-23, after the revision). Full report: `ledger/coverage-report.md`.
