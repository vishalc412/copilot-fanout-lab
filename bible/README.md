# copilot-fanout-lab: system reference

Status: CORRECTED AFTER VERIFICATION (report of 2026-11-23; about 100 statements, rows and citations added or changed since, not re-verified). Not VERIFIED: the verification verdict was PASS, the 27 numbered corrections and the other points of the report were applied in a revision pass (`revision-log.md`), and the parts changed by that pass have not been checked by anyone else.

| | |
| --- | --- |
| Depth | deep for all components |
| Version given by the user | none |
| Snapshot | 12 files in scope, 332 source lines, 2026-11-23 (the run of 2026-11-21 counted 13 because it included a `.git` pointer file) |
| Coverage | 100% files, 100% functions, 100% routes (none), 100% citations resolve (coverage.py, 2026-11-23, after the revision) |
| Produced with | a coding agent (Claude Sonnet 5.5) following the `analyzing-a-codebase` skill |
| Diagrams | checked by reading only; no Mermaid renderer was available |

## In two minutes

`copilot-fanout-lab` is an experiment repository, not a deployed product: it tests whether a coding agent can analyse a codebase one component at a time, one pull request per component, with several passes per pull request and a way to stop and ask the team (`README.md:3-5`). It holds a tiny sample shop and the scripts that drive the experiment. The shop is two Python libraries: `catalog`, an in-memory table of three products with price, stock and image lookups plus a supplier feed refresher, and `orders`, which totals an order with one discount, validates its lines against stock and posts a settled order to a payment partner (`components/catalog/catalog.py:8-47`, `components/orders/orders.py:19-51`). The `tools` component has three scripts: `plan.py` writes an inventory to `codebase-analysis/plan.json`, `fanout.sh` opens one GitHub issue per component, and `gate.py` checks each pass of a component's analysis against that inventory (`tools/plan.py:1-6`, `tools/fanout.sh:2-5`, `tools/gate.py:1-12`). The code imports only the Python 3 standard library and its own modules, plus bash and the `gh` command (every `import` line in `components` and `tools`, listed in `hld/06-cross-cutting.md`, Dependencies); nothing is deployed and nothing listens on a port (search `socket`, `listen`, `serve`, `flask` in `*.py` and `*.sh`: 0 hits). The only data is a dict in memory and the plan file. Three things matter most for whoever works on it next. First, the settlement call to the payment partner uses plain `http` with no authentication, and the team has not said whether that is to stay (`components/orders/orders.py:7-9`, `components/orders/orders.py:48-50`, `Q-001`). Second, `fetch_supplier_feed`, `apply_feed`, `order_total`, `validate` and `settle` have no caller in the repository, so how they are used is unknown (`Q-002`, `Q-003`). Third, tests cover one function per component and nothing in `tools` (`components/orders/test_orders.py:7-8`, `components/catalog/test_catalog.py:7-8`).

## At a glance

Who runs the system and which outside systems it touches. The `.github` workflows are drawn as one outside system because that folder is outside the analysis scope.

```mermaid
flowchart LR
  operator(["Operator<br/>shell user of the scripts"])
  agent{{"Analysing coding agent<br/>Copilot or Claude stand-in"}}
  actions{{"GitHub Actions<br/>runs the workflows"}}
  aiservice{{"AI service of the Claude action<br/>Anthropic API, assumed<br/>external"}}
  subgraph labsys["copilot-fanout-lab"]
    shop["catalog and orders<br/>Python 3 library<br/>Prices and settles orders"]
    tools["tools<br/>Python 3 and bash<br/>Plans, fans out and gates"]
  end
  github{{"GitHub<br/>issues, labels and pull requests"}}
  partner{{"Payment partner settlement endpoint<br/>external"}}
  supplier{{"Supplier product feed<br/>external"}}
  operator -->|"python tools/plan.py and tools/gate.py"| tools
  operator -.->|"tools/fanout.sh, per its usage comment"| tools
  actions -->|"python tools/plan.py and tools/gate.py"| tools
  actions -.->|"claude.yml runs the Claude action with a key or token"| aiservice
  tools -.->|"gh label create and gh issue create"| github
  github -.->|"issue or mention wakes the agent"| agent
  agent -.->|"writes analysis files, opens a PR"| github
  shop -->|"POST settlement JSON, HTTP"| partner
  shop -->|"GET products.json, HTTP"| supplier
```

| Element | Evidence |
| --- | --- |
| operator and workflows run the scripts (inferred for the operator and `fanout.sh`: usage comment) | `tools/plan.py:61-62`, `tools/gate.py:116-117`, `tools/fanout.sh:3`, `.github/workflows/analysis-gate.yml:53` |
| the Claude action calls an AI service (assumed: the action's own behaviour) | `.github/workflows/claude.yml:42-46` |
| `tools` calls GitHub through `gh` (inferred) | `tools/fanout.sh:10-28` |
| `shop` calls the partner and the feed | `components/orders/orders.py:45-51`, `components/catalog/catalog.py:36-39` |
| agent wakes on an issue and writes files (inferred) | `tools/fanout.sh:14-28`, `.github/workflows/claude.yml:11-13` |

Shapes: rounded = people, rectangle = this system's units, hexagon = outside system. Dashed line = inferred.

## Components

| Component | Kind | Technology | Responsibility | Pages | Size (files, lines, functions, routes) |
| --- | --- | --- | --- | --- | --- |
| `catalog` | library | Python 3 | Product table, price and stock lookups, supplier feed refresh | [lld/catalog/README.md](lld/catalog/README.md) | 3 files, 59 lines, 6 functions, 0 routes |
| `orders` | library | Python 3 | Order totals with one discount, line validation, settlement | [lld/orders/README.md](lld/orders/README.md) | 3 files, 63 lines, 4 functions, 0 routes |
| `tools` | tool | Python 3 and bash | Inventory, issue fan-out and per-pass gate | [lld/tools/README.md](lld/tools/README.md) | 3 files, 210 lines, 7 functions, 0 routes |

## Reading paths

| You are | Read, in order |
| --- | --- |
| Manager or new joiner | this page, [00-mind-map.md](00-mind-map.md), [hld/01-system-context.md](hld/01-system-context.md), [hld/05-key-flows.md](hld/05-key-flows.md) |
| Architect | [hld/01](hld/01-system-context.md) to [hld/06](hld/06-cross-cutting.md), then each `lld/<component>/README.md` |
| Engineer changing `orders` or `catalog` | [lld/orders/README.md](lld/orders/README.md) or [lld/catalog/README.md](lld/catalog/README.md), the module pages, [lld/data-dictionary.md](lld/data-dictionary.md) |
| Engineer changing the scripts | [lld/tools/README.md](lld/tools/README.md), then [plan](lld/tools/plan.md), [gate](lld/tools/gate.md), [fanout](lld/tools/fanout.md) |
| Operator | [hld/02-architecture.md](hld/02-architecture.md) (pipeline), [hld/06-cross-cutting.md](hld/06-cross-cutting.md), [reference/configuration.md](reference/configuration.md) |
| Anyone deciding what to fix first | [reference/risks-and-surprises.md](reference/risks-and-surprises.md), [reference/open-questions.md](reference/open-questions.md) |

## Files

| File | What it holds |
| --- | --- |
| [README.md](README.md) | this page |
| [00-mind-map.md](00-mind-map.md) | mind maps of the system and each component |
| [hld/01-system-context.md](hld/01-system-context.md) | people and outside systems |
| [hld/02-architecture.md](hld/02-architecture.md) | containers, deployment (none), pipeline, technology, configuration sources |
| [hld/03-integrations.md](hld/03-integrations.md) | inbound interfaces, outbound connections, dependency matrix |
| [hld/04-data-architecture.md](hld/04-data-architecture.md) | stores, data models, lifecycles |
| [hld/05-key-flows.md](hld/05-key-flows.md) | ten flows with sequence diagrams |
| [hld/06-cross-cutting.md](hld/06-cross-cutting.md) | security, errors, resilience, logging, build, tests, dependencies |
| [lld/catalog/](lld/catalog/README.md) | `README.md`, `catalog.md`, `test_catalog.md` |
| [lld/orders/](lld/orders/README.md) | `README.md`, `orders.md`, `test_orders.md` |
| [lld/tools/](lld/tools/README.md) | `README.md`, `plan.md`, `gate.md`, `fanout.md` |
| [lld/data-dictionary.md](lld/data-dictionary.md) | product table, `plan.json`, analysis files, enum values |
| [reference/glossary.md](reference/glossary.md) | terms |
| [reference/configuration.md](reference/configuration.md) | every constant, variable and setting |
| [reference/risks-and-surprises.md](reference/risks-and-surprises.md) | 16 items, by impact |
| [reference/open-questions.md](reference/open-questions.md) | Q-001 to Q-003 |
| [knowledge/AGENT-CONTEXT.md](knowledge/AGENT-CONTEXT.md) | primer for an LLM agent; the other files in `knowledge/` are built by `knowledge.py` |
| [ledger/](ledger/coverage-ledger.md) | coverage ledger, coverage report, symbol checklist |
| [progress.md](progress.md), [run-notes.md](run-notes.md) | work plan and run notes |
| [verification-report.md](verification-report.md), [verification-coverage.md](verification-coverage.md), [revision-log.md](revision-log.md) | the independent check of 2026-11-23 and what was done about each item |

## Totals

| Measure | Count |
| --- | --- |
| Components / source files / source lines | 3 / 7 (plus 3 empty `__init__.py`) / 332 |
| Classes and functions documented / full cards | 21 symbols / 17 function cards (the file `tools/fanout.sh` has a script walkthrough instead of cards) |
| Routes documented | 0 (the code declares none) |
| Outside systems / data stores / tables / input files | 6 (payment partner, supplier feed, GitHub, GitHub Actions, analysing agent, AI service of the Claude action) / 2 (`_PRODUCTS`, `plan.json`) / 0 tables / 5 files (`plan.json` and four analysis files) |
| Flows traced / diagrams | 10 / 30 (including 4 mind maps) |
| Business rules | 22 (orders 8, catalog 6, tools 8) |
| Statements marked inferred / assumed | 59 / 36 (count of the marks, an opening bracket followed by the word, in the front page, mind map, HLD, LLD, reference pages and agent primer, 2026-11-23; the first run said about 51 / 27) |
| Risks and surprises / open questions | 16 / 3 |
| Coverage (coverage.py) | result PASS at depth deep: files 7 of 7, symbols 21 of 21, function cards 17 of 17, routes 0 of 0, citations 1209 of 1209, branch lines 49 of 49, same-file calls 9 of 9, front matter 11 of 11 |
| Knowledge graph | 86 nodes, 144 edges, 233 chunks, 1 call not resolved to one symbol (knowledge.py, 2026-11-23) |

Verification: `verification-report.md` (2026-11-23, verdict PASS, sampling level standard: 610 of 1134 citations, 12 function cards, 30 diagrams) and `verification-coverage.md`. The report was written by the same model family in a separate session. This revision applied every item of the report (`revision-log.md`); no further verification is required for minor corrections only, but the statements added or changed in the revision are not re-verified, and a person or another model should re-check V-012 and V-025 of the report and the changed parts.

Known limit: `.github/` is outside the analysis scope, so its citations carry no stamp and the drift check of `coverage.py` cannot see them. The repository instructions in that folder have already changed once since the book was first written (V-001 to V-005, V-012). Re-check every `.github/` citation by hand whenever those files change.

<!-- cites README.md@61543f4e8ea18677f318b804951295e5b678b877 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/test_catalog.py@9be40d147e425d178067c8b34f19b28b9b374d1f -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_orders.py@ca9144cf39abe39e988dc009863b036a7ee1a39f -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
