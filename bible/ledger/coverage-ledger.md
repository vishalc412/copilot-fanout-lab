# Coverage ledger

Depth: deep. Snapshot: 14 files in scope, 332 source lines, 2026-11-21. Inventory: `ledger/inventory.json` of 2026-11-21.

| Folder | Files | Opened | What it holds | Status | Pages |
| --- | --- | --- | --- | --- | --- |
| `components/` | 7 | 7 | The two sample components (`catalog`, `orders`) and the empty package marker | read in full | `lld/catalog/*`, `lld/orders/*` |
| `components/catalog` | 4 | 4 | Product catalog: prices, stock, supplier feed; one test file | read in full | `lld/catalog/*` |
| `components/orders` | 4 | 4 | Order totals, validation, settlement; one test file | read in full | `lld/orders/*` |
| `tools/` | 3 | 3 | The fan-out controller, plan generator and per-component gate | read in full | `lld/tools/*` |
| `.agent/` | 1 | 1 | The session instruction file of the coding agent harness (not committed) | read in full | `reference/risks-and-surprises.md` |
| repository root | 3 | 3 | `README.md`, `.gitignore`, `.git` pointer file | read in full | `README.md` of the bible, `hld/02-architecture.md` |
| `.github` | n/a | 0 | Workflows, skills and Copilot instructions | excluded (user's choice) | |
| `codebase-analysis` | n/a | 0 | The component lab's output and `plan.json` | excluded (user's choice) | |

## Totals

| Status | Folders | Files |
| --- | --- | --- |
| read in full | 6 | 14 |
| excluded | 2 | not counted |

## Coverage from coverage.py

Not yet run for this pass; see `ledger/coverage-report.md` once pass 11 has run.
