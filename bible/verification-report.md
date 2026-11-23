# Verification report

| | |
| --- | --- |
| Verdict | PASS |
| Analysis snapshot | 13 files in scope, 332 source lines, 2026-11-21, no version given (front page) |
| Repository at verification | 12 files in scope, 332 source lines, no version given (see step 1 below) |
| Depth stated / depth found | deep / deep (card depth confirmed on the 12 audited cards; 1 Partial) |
| Verified with | Claude Code, Claude Sonnet 5.5, a new session that did not write the book |
| Analysis produced with | a coding agent (Claude Sonnet 5.5), per the front page |
| Sampling level | standard |
| Date | 2026-11-23 |

## Summary

The book is complete, deep and, on the evidence, accurate. Every source file, symbol, function and branch line is covered (`coverage.py` run by the checker: PASS at depth deep). Of the 1,134 citations, 610 were judged by the standard rule: 595 are confirmed as written, 11 are true but cite the wrong lines, 3 say slightly more than the code shows and 1 is wrong. No statement behind a diagram element is wrong or unsupported. All 12 audited function cards match the code; one is Partial (an error path left out). No secret value appears. No folder is missing from the ledger.

The weakest part is the book's handling of the `.github` folder, which the issue excludes from the analysis: its files are cited as evidence but carry no stamp, so the coverage script's drift check cannot see them. `.github/copilot-instructions.md` has changed since the book was written (it now routes the book to `bible/` and the Python and "never edit" lines moved from lines 5-7 to lines 15-17). Five sampled citations now point at the wrong lines and one hazard ("two acting documents disagree on where output goes") is no longer true. The second weak spot is counts on the front page, ledger and agent primer (13 or 14 files against 12, 87 nodes against 85), left over from before the last rebuild. All are `minor` and have a specific correction below. The verdict is `PASS`: coverage passes, accuracy is 99.3%, depth is 91.7%, and there is no `major` correction, no significant omission and no secret.

## Scores

| Measure | Value |
| --- | --- |
| Source files with a page | 7 / 7 (100.0%) |
| Symbols accounted for | 21 / 21 (100.0%) |
| Functions with a full card (pseudo-code, branches cited) | 17 / 17 (100.0%) |
| Branch lines cited / call-graph edges drawn / front matter | 49 / 49 (100.0%), 9 / 9 (100.0%), 11 / 11 (100.0%) |
| Routes with an endpoint card | 0 / 0 (the code declares none) |
| Citations that resolve | 1134 / 1134 (100.0%) |
| Coverage gate | PASS (depth deep) |
| Citations in the analysis / checked | 1134 / 610 |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | 595 / 11 / 3 / 1 / 0 |
| Omissions (significant) / Inconsistent | 0 / 9 (plus 2 minor omissions, see below) |
| Accuracy / citation quality | 99.3% (606 of 610) / 97.5% (595 of 610) |
| Cards audited: Complete / Partial / Shallow / Wrong | 12: 11 / 1 / 0 / 0 |
| Depth / depth, usable | 91.7% / 100.0% |

## How the sample was selected

Level `standard`, rules of `references/checks.md`, Step 3, applied to `ledger/citations.tsv` (1134 rows, rewritten by the script on this run, unchanged in content).

| Group | Rule | Rows | Row indexes |
| --- | --- | --- | --- |
| A | every citation on `hld/` pages and in `README.md`; `knowledge/AGENT-CONTEXT.md` judged as an HLD page | 415 | 2 to 416 (all) |
| B | label `inferred` or `assumed`, not already in A | 79 | 444-445, 448-452, 476-477, 502, 511-512, 521-522, 531, 534-537, 547-549, 609-610, 619-624, 642, 647, 660-662, 672-673, 683, 686-687, 698-699, 760-761, 767-770, 796, 799, 802, 818-822, 867, 874-875, 896-899, 914-916, 923, 935, 947, 979-983, 1009-1011, 1105-1106 |
| C | business-rule tables and outbound-call tables of the three component READMEs (the security, secrets and authentication sections are on `hld/06`, already in A) | 31 | 436-441, 595-606, 611-613, 742-750, 762 |
| D | all other citations whose index is divisible by 7 | 85 | 420, 427, 434, 455, 462, 469, 483, 490, 497, 504, 518, 525, 532, 539, 546, 553, 560, 567, 574, 581, 588, 616, 630, 637, 644, 651, 658, 665, 679, 693, 700, 707, 714, 721, 728, 735, 756, 763, 777, 784, 791, 798, 805, 812, 826, 833, 840, 847, 854, 861, 868, 882, 889, 903, 910, 917, 924, 931, 938, 945, 952, 959, 966, 973, 987, 994, 1001, 1008, 1015, 1022, 1029, 1036, 1043, 1050, 1057, 1064, 1071, 1078, 1085, 1092, 1099, 1113, 1120, 1127, 1134 |

Total 610. No delta update is pending: `delta-log.md` has two rows, `ledger/delta.md` names no changed file or function (its only entry is the removal of the `.git` entry), so no card was rewritten by a delta and the usual fixed sample applies to the whole book. This is the first verification report.

## Corrections

All corrections are `minor`. Evidence is the file and line in the repository today.

| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | `hld/02-architecture.md:112` (row 96) | Citation off | minor | Python 3.12 is stated at line 15 of the instructions; line 5 is the bullet about the book | `.github/copilot-instructions.md:15` | cite `.github/copilot-instructions.md:15`; also fix `reference/configuration.md` (Python 3.12 row, same line 5) |
| V-002 | `hld/06-cross-cutting.md:55` (row 312) | Citation off | minor | the unittest command is at lines 15-16 | `.github/copilot-instructions.md:15-16` | cite lines 15-16 |
| V-003 | `knowledge/AGENT-CONTEXT.md:47` (row 347) | Citation off | minor | same command, lines 15-16 | `.github/copilot-instructions.md:15-16` | cite lines 15-16 |
| V-004 | `knowledge/AGENT-CONTEXT.md:113` (row 395) | Citation off | minor | same, lines 15-16 | `.github/copilot-instructions.md:15-16` | cite lines 15-16 |
| V-005 | `knowledge/AGENT-CONTEXT.md:117` (row 400) | Citation off | minor | the "never edit" rule is line 17 | `.github/copilot-instructions.md:17` | cite line 17; same fix in `run-notes.md:22` (outside the sample) |
| V-006 | `hld/02-architecture.md:116` (row 104) | Citation off | minor | `anthropics/claude-code-action@v1` is at line 42; line 40 is `fetch-depth: 1` | `.github/workflows/claude.yml:42` | cite line 42 |
| V-007 | `hld/06-cross-cutting.md:61` (row 320) | Citation off | minor | same | `.github/workflows/claude.yml:42` | cite line 42 |
| V-008 | `hld/06-cross-cutting.md:43` (row 305) | Citation off | minor | the `echo` is at line 28; lines 25-26 are the step name and `env:` | `.github/workflows/claude.yml:28` | cite lines 25-28 |
| V-009 | `README.md:16` (row 8) | Citation off | minor | "no authentication" is shown by the headers built in `settle`, not by the constant and comment | `components/orders/orders.py:48-50` | add `components/orders/orders.py:48-50` |
| V-010 | `hld/01-system-context.md:3` (row 20) | Citation off | minor | the gate is described on README line 10, outside lines 1-9 | `README.md:10` | cite `README.md:1-10` |
| V-011 | `hld/03-integrations.md:26` (row 131) | Citation off | minor | "stops at the first failure" rests on `set -euo pipefail`, which the cited lines 10-28 do not include | `tools/fanout.sh:6` | add `tools/fanout.sh:6` |
| V-012 | `knowledge/AGENT-CONTEXT.md:130` (row 413) | Wrong | minor | the instructions no longer disagree with the issue: they route the whole-repository book to `bible/` and every other component to `codebase-analysis/components/<name>/`. Only the `component-analysis` skill (write scope, `SKILL.md:16-19`) still differs from the issue for the book. Not `major`: no security, data or function behaviour is involved, and the current file tells an agent the right folder | `.github/copilot-instructions.md:5-7`, `.github/copilot-instructions.md:11-12` | reword to name only the skill; same fix in `reference/risks-and-surprises.md` row 13 and `run-notes.md:20` (outside the sample); state the date of the instructions file |
| V-013 | `hld/02-architecture.md:102` (row 89) | Overstated | minor | the coverage step runs only on pull requests; a manual start runs three scripts | `.github/workflows/toolkit-analysis.yml:25-27` | "runs the four scripts (the coverage gate only on pull requests)"; flow 10 already says so |
| V-014 | `knowledge/AGENT-CONTEXT.md:50` (row 353) | Overstated | minor | the cited lines show the usage comment and `gh label create`, not that `gh` must be logged in; `hld/03` marks this (assumed) | `tools/fanout.sh:3-10` | add "(assumed: `gh` own credentials)" |
| V-015 | `lld/catalog/catalog.md:289` (row 512) | Overstated | minor | `float(None)` and `int(None)` raise `TypeError`, not `ValueError`, and a JSON `null` is a plausible feed value; same wording in `lld/catalog/README.md` Errors and in risk 3 | `components/catalog/catalog.py:46-47` | "a missing key raises `KeyError`, a non-numeric string raises `ValueError`, a `null` or list raises `TypeError`" |
| V-016 | `README.md` (Snapshot row, Totals), `ledger/coverage-ledger.md`, `progress.md`, `knowledge/AGENT-CONTEXT.md:5` | Inconsistent | minor | the stored inventory and the symbol checklist say 12 files in scope; the front page, ledger and `progress.md` say 13 and the agent primer says 14. The extra entry is the `.git` pointer the author's checkout had; the script now excludes `.git` | `ledger/inventory.json` (totals), `ledger/symbol-checklist.md` | state 12 files in scope everywhere |
| V-017 | `README.md` Totals, Knowledge graph row | Inconsistent | minor | the graph has 85 nodes, the front page and `progress.md` say 87; the front page dates the run 2026-11-21, the graph says 2026-11-23 | `knowledge/graph.json` (`stats`), `knowledge/README.md` | state 85 nodes and the date of the last rebuild |
| V-018 | `knowledge/AGENT-CONTEXT.md:43` | Inconsistent | minor | "Nothing else calls across files" leaves out the two tests, which call `orders.line_total` and `catalog.price_of` from another file | `components/orders/test_orders.py:8`, `components/catalog/test_catalog.py:8` | "outside the tests" |
| V-019 | `hld/04-data-architecture.md:3` | Inconsistent | minor | "keeps no data on disk" is contradicted by the same sentence's `plan.json`, which `plan.py` writes | `tools/plan.py:55-57` | "the shop keeps no data on disk" |
| V-020 | `lld/orders/README.md:28` | Inconsistent | minor | the search terms listed give 2 hits in `test_orders.py`, not 3 (the 3 of `orders.md` counts the extra term `orders`) | `components/orders/test_orders.py:7-8` | say 2, or list the same terms as `orders.md` |
| V-021 | `progress.md` (reader test 15, final pass, sweep table) | Inconsistent | minor | six functions have no caller (`image_url` too: `lld/catalog/README.md`, R-06); of the seven `http://` hits not in the literals, three are in `plan.py` and one is the `gate.py` docstring | `components/catalog/catalog.py:32-33`, `tools/gate.py:8` | "six" and "three in `plan.py`, one in `gate.py`" |
| V-022 | `00-mind-map.md` (system and tools maps) | Inconsistent | minor | the front page counts five outside systems including the analysing coding agent; the mind map shows four and no agent | `README.md` Totals, `hld/01-system-context.md` | add the agent to "Outside systems" |
| V-023 | `ledger/coverage-ledger.md` (folder rows) | Inconsistent | minor | `components/catalog` and `components/orders` are listed with 4 files each; each holds 3. The root row counts a `.git` pointer file | `components/catalog/`, `components/orders/` listings | 3 and 3; drop the `.git` file |
| V-024 | `hld/02-architecture.md` containers diagram | Omission | minor | the analysis files the gate reads (`status.json`, `inventory.md`, `risks.md`, `tests-report.md`) are a store on `hld/04` and in the data dictionary but not on the container diagram; nor is the `unittest` child process of pass 3 | `tools/gate.py:46,52,64,94`, `tools/gate.py:73-75` | add a store node with an edge from `gate` |
| V-025 | `hld/01-system-context.md`, `hld/02-architecture.md` | Omission | minor | `claude.yml` runs `anthropics/claude-code-action` with `ANTHROPIC_API_KEY` or an OAuth token, so the pipeline calls an AI service the context diagram does not show; its permissions also include `pull-requests: write`, `issues: write` and `id-token: write`, not only `contents: write` | `.github/workflows/claude.yml:19-23,42-46` | name the service as an outside system of the Actions pipeline and list the four permissions |
| V-026 | `lld/orders/orders.md`, card `validate`, Errors | Partial | minor | "none raised by this code" is false for a non-numeric `qty` (`qty <= 0` raises `TypeError`) or a malformed pair (unpacking raises); the `order_total` card says so, this one does not | `components/orders/orders.py:37-38` | add the error path |
| V-027 | `hld/05`, `hld/06`, `lld/tools/README.md` and others | Inconsistent | minor | statements that the operator runs `fanout.sh` rest only on its usage comment (`fanout.sh:3`), and carry no `(inferred` mark; the cron docstring is marked correctly | `tools/fanout.sh:3` | mark `(inferred: usage comment)` |

Also noticed outside the sample, `Citation off`, `minor`: `reference/configuration.md`, row of `ANTHROPIC_API_KEY` and `CLAUDE_CODE_OAUTH_TOKEN`: the names are at `claude.yml:32-33` and `claude.yml:45-46`, not 29-31 and 43-44. The count in the scores table counts V-016 to V-023 and V-027 as the 9 Inconsistent findings (V-012 is the one Wrong).

## Coverage findings

`coverage.py` was run by the checker with `--repo . --analysis bible --exclude codebase-analysis --exclude .github --depth deep --report verification-coverage.md` (the `--report` name is resolved inside the analysis folder, so it writes `bible/verification-coverage.md`; a first run with the path `bible/verification-coverage.md` wrote a stray copy under `bible/bible/`, which was deleted).

```text
Source files with a page                                 7 / 7     100.0%
Symbols accounted for                                   21 / 21    100.0%
Functions with a full card (>= 1 lines)                 17 / 17    100.0%
Routes with an endpoint card                             0 / 0     100.0%
Citations that resolve                                1134 / 1134  100.0%
Branch lines cited in their card                        49 / 49    100.0%
Same-file calls drawn in call graphs                     9 / 9     100.0%
LLD pages with knowledge-graph front matter             11 / 11    100.0%
result: PASS (depth deep)
```

- Gaps: none. No `GAPS` result, so no major coverage finding.
- `ledger/not-documented.md` does not exist. The only source files without a page are the three empty `__init__.py` files (0 lines), which the inventory does not count as source files needing pages. Acceptable.
- Totals: inventory 12 files in scope, 10 source files, 7 needing pages, 332 source lines, 21 symbols, 0 routes. The front page matches on lines, symbols, routes and the 7 pages, but says 13 files (V-016).
- Drift section: "None". Blind spot: the script stamps and compares only the analysed source files. `.github/` and `codebase-analysis/` are excluded, their citations carry no stamp, and `.github/copilot-instructions.md` has already moved (V-001 to V-005, V-012). A person re-running the book should re-check every `.github/` citation by hand.

## Depth findings

Files chosen by the rule: the five largest source files (`tools/gate.py` 117 lines, `tools/plan.py` 62, `components/orders/orders.py` 51, `components/catalog/catalog.py` 47, `tools/fanout.sh` 31); no file declares routes (0 routes); the 3rd and 7th source files in path order are `components/catalog/catalog.py` (already chosen) and `components/orders/test_orders.py` (a test file: rows, not cards, skipped). The three largest functions of each file were taken. Each card was read against the full source (branches, loops, compared values, fields, outbound calls, errors, pseudo-code order, each row of Branches and errors).

| File | Card | Score | What is missing |
| --- | --- | --- | --- |
| `tools/gate.py` | `check` (37 lines) | Complete | nothing; every branch, message and the loose substring match are described |
| `tools/gate.py` | `main` (33 lines) | Complete | nothing; the `--pass 0` and boolean `open_questions` cases are covered |
| `tools/gate.py` | `count_tests` (7 lines) | Complete | nothing |
| `tools/plan.py` | `scan` (18 lines) | Complete | nothing material (a syntax error in a test file surfaces through `count_tests`; the card names only source files) |
| `tools/plan.py` | `main` (18 lines) | Complete | nothing |
| `components/orders/orders.py` | `order_total` | Complete | nothing |
| `components/orders/orders.py` | `validate` | Partial | the error path for a non-numeric `qty` or a malformed pair (V-026) |
| `components/orders/orders.py` | `settle` | Complete | nothing (the `json.dumps` `TypeError` for a non-serialisable input is implied by "not checked") |
| `components/catalog/catalog.py` | `apply_feed` | Complete | nothing (the `null` value gives `TypeError`, V-015) |
| `components/catalog/catalog.py` | `price_of` | Complete | nothing |
| `components/catalog/catalog.py` | `fetch_supplier_feed` | Complete | nothing |
| `tools/fanout.sh` | script walkthrough (no functions) | Complete | nothing; labels, here-document, `case` arms, `set -euo pipefail` and exit 2 all match |

Endpoint cards: none exist, because the code has no routes.

## Diagram findings

30 diagrams: 4 mind maps, 1 at-a-glance (front page), 1 context, 2 architecture (containers, pipeline), 2 data models, 10 sequences, 3 component flowcharts, 7 module call graphs. Every edge has a row in its evidence or step table (the `person` edges on `lld/tools/README.md` are evidenced by the "Starts by" row rather than the element table); sequence step tables match the `autonumber` of every diagram (checked message by message, flows 1 to 10); the rows cited were judged in the sample. Dashed edges match inferred or assumed statements. Syntax screened by a script (reserved ids, `;` or `#` in labels, unquoted labels, unbalanced `alt`, `opt`, `loop`, `subgraph`, brackets in mind-map text, type brackets in data models): 0 problems. Not rendered: no Mermaid renderer is installed.

| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Mind maps (4) | ok | ok | V-022 | n/a | n/a | ok | no problem found (not rendered) | leaves are text, pages named in the list below them; every component present |
| Front-page at a glance, context | ok | ok | V-025 | ok | ok | ok | no problem found | agent edges dashed, matching the inferred rows |
| Containers | ok | ok | V-024 | ok | ok | `_PRODUCTS`, "PRODUCTS" (data model) and "product table" (flow 4) name one dict | no problem found | no deployment diagram: nothing deployed, stated with the file listing |
| Pipeline | ok | ok | ok | ok | ok | ok | no problem found | |
| Data models (2) | ok (one per store with a schema; no lifecycle: no record has a status) | ok | ok | n/a | cardinality and keys present | `PRODUCTS` against `_PRODUCTS` | no problem found | |
| Sequences (10) | ok (one per flow; no route has three participants) | ok | ok | HTTP shown on the two network edges; port and scheme per `hld/03` | `alt` for every handled or unhandled failure | ok | no problem found | |
| Component flowcharts (3) and module call graphs (7) | ok (no class diagram: only test classes) | ok | ok | ok | ok | ok | no problem found | |

Searches of `progress.md` repeated by hand and agree: `http://` 7 hits (3 literals, 3 in `plan.py`, 1 in `gate.py`, see V-021), `https://` 1, `urllib` 5, `subprocess` 2, `cron` 1, environment reads 0, route or messaging patterns 0, authentication words 1 (a comment). Ways the code reaches outside itself found by search: `urllib.request` (2 call sites), `gh` and `python3` in `fanout.sh`, `subprocess.run` in `gate.py`, file reads and the one write (`plan.json`). All are on the diagrams, except the omissions in V-024 and V-025.

## Data dictionary and mind map findings

- Data dictionary: every store and every file opened by name is present with fields: `_PRODUCTS` (key, `name`, `price`, `stock`), the supplier feed fields, order lines and settlement message, `plan.json` (all eight keys, each checked against the reading code: `sources` and `passes` are written only), and the four analysis files with what the gate needs of each. The three-pattern `.gitignore` entry does not name its third pattern; a reader cannot tell what it is (readability, minor).
- Two tables and one spreadsheet: the repository has no table and no spreadsheet. The two data shapes with fields (`_PRODUCTS`, `plan.json`) were opened against `catalog.py:8-12,44-47` and `plan.py:37-38,46-54`: every field the code uses is listed.
- Mind map: every component and every module page is on it; the "As a list" section names pages that exist. The analysing agent is missing from the outside systems (V-022).

## Knowledge base findings

- `graph.json` `generated` is 2026-11-23T06:14:39. All page files share one modification time (the checkout), so "newer than every page" cannot be shown or refuted; `delta-log.md` shows no page change after the rebuild. Not a finding; stated as a limit.
- Ten `analysis` edges (first, then every tenth of 91, in file order): `HAS_PAGE` catalog to its README and to `catalog.md`; `READS` data dictionary to `_PRODUCTS`; `CONTAINS` orders to its test; `DEPENDS_ON` orders to catalog (`orders.py:5`); `CONFIG` `orders.py` to `LOYALTY_DISCOUNT` (`orders.py:14,29`); `READS` tools to `plan.json`; `EXPOSES` tools to `python tools/gate.py`; `READS` `gate.py` to `status.json` (`gate.py:94`); `USES` `plan.py` to `count_tests` (`plan.py:15,36`). 10 of 10 supported. No `WRITES` or `CALLS` edge was among them; the six `WRITES` edges (all `analysis`) point to `_PRODUCTS` and `plan.json` and are supported by `catalog.py:46-47` and `plan.py:55-57`.
- `name-unique` edges: none exist in this graph (resolutions are `exact` 39, `same-file` 9, `import` 5, `analysis` 91). Five `CALLS` edges resolved by `import` were checked instead (`validate` to `in_stock` `orders.py:40`; `line_total` to `price_of` `orders.py:20`; the two tests to `price_of` and `line_total`, `test_catalog.py:8`, `test_orders.py:8`; `scan` to `count_tests` `plan.py:36`): 5 of 5 correct.
- Node duplicates: none (one node per config key, store, outside system and job). The graph has 3 `External` nodes against 5 outside systems on the front page (GitHub Actions and the agent are not nodes): `minor`, same cause as V-022.
- `AGENT-CONTEXT.md`: every citation was in group A. It states all three limits (dynamic dispatch, callbacks, reflection, string-built names and other languages are not edges; `name-unique` and `analysis` edges are leads; the snapshot it describes). Its snapshot count is wrong (14 files, V-016); three citations point at moved lines (V-003 to V-005) and one hazard is out of date (V-012).
- Counts: the front page says 87 nodes, the graph 85 (V-017).

## Readability and prose findings

- Read as a new engineer: `README.md` (opens with "In two minutes"), the three component READMEs, `catalog.md`, `orders.md` and `gate.md`. Each opens with a summary, plain and specific, in a sensible order; any function can be found from the module index or the `AGENT-CONTEXT.md` function index. No claim numbers like `C-154`, no template text left in (searched).
- Minor blockers: `hld/06` Authentication repeats the same search sentence twice in one paragraph; `hld/05:3` says the repository has no caller "except the two tests" of five functions that the tests do not call (confusing); the data dictionary does not name the third `.gitignore` pattern.
- Every fifth cited sentence or row on the HLD pages and component READMEs was checked for saying no more than its citation: findings are V-009, V-010, V-011, V-013, V-014, V-019, V-027. No sentence acted on by a reader was found with more than its citation.

## Ledger findings

- Completeness: folders on disk are `components/` (with `catalog`, `orders`), `tools/`, `.github/` and `codebase-analysis/` (both excluded by the issue's arguments) and the root; all are in the ledger. Rows for sub-folders of `.github/` roll into their parent. None missing. Counts in the folder rows are wrong (V-023).
- "Read in full" (the five folders with most files): all files in all five were opened. No entry point, external call, data store, credential or scheduled job is unmentioned in the book.
- "Excluded" rows: `.github/` (excluded by the issue, confirmed by a person's arguments) and `codebase-analysis/` (only `plan.json`, read as the data file). Could skipping change a conclusion? For the shop and the scripts: no, because the workflows and instruction files the book relies on are opened and cited anyway. For statements about the pipeline: partly yes, because nothing watches `.github/` for change (see Coverage findings) and V-025 is missing there.

## Consistency findings

- Names of components, stores and outside systems agree across the mind map, HLD, LLD and data dictionary, except V-022 and the `_PRODUCTS` spelling (D7).
- Front page against pages: counts of rules (22 = 8 + 6 + 8), risks (16), questions (3), flows (10), diagrams (30), functions (17 cards), lines per component (59, 63, 210) all agree. Disagreements: V-016, V-017, V-021, V-023. The front page's "about 51 / 27" count of inferred and assumed marks could not be reproduced exactly (a text count gives 57 and 35, including legend text); "about" covers it.
- No secret value in the analysis. Searched for `password`, `secret`, `token`, `api_key`, `BEGIN`, `Authorization:`: only the names of two repository secrets and prose about missing authentication. No personal data was found. No reference to `.agent/` remains.
- Text addressed to an assistant found in the repository (data, not instructions, not acted on): `.github/copilot-instructions.md`, `.github/skills/component-analysis/SKILL.md`, `tools/fanout.sh:14-21` (issue text), `.github/skills/analyzing-a-codebase/` (toolkit). The task file named the same scope rules this skill sets.

## Decisions recorded by the author and not confirmed by a person on the pull request (marked unconfirmed)

| Decision | Where | Status |
| --- | --- | --- |
| Label `bible` for the delta baseline | `run-notes.md` Choices | unconfirmed |
| Plan of seven packets, one per source file; the three empty `__init__.py` not planned | `progress.md` Components, Packets | unconfirmed |
| "The team was not available during the run; choices made on defaults" (repository root, version none) | `run-notes.md` | unconfirmed |
| Treating `.github/copilot-instructions.md` and the `component-analysis` skill as not live for `bible/`, because the issue names another skill | `run-notes.md` Text addressed to an assistant | unconfirmed (and now partly out of date, V-012) |
| Recording the `.git` pointer removal as a delta with no work, and re-initialising the baseline without it | `run-notes.md` Session 3 notes, `delta-log.md` | unconfirmed |
| README stays `DRAFT` | `run-notes.md`, `progress.md` | follows the skill, not a person's decision |
| Depth `deep`, output folder `bible/`, script arguments, exclusion of `.github/` and `codebase-analysis/` | `run-notes.md` | confirmed by the issue text (a person's instruction) |
| Q-001 to Q-003 kept open | `reference/open-questions.md` | confirmed: a person's comment asked to keep them open; they still await answers |

## Limits

- A sample was checked (610 of 1134 citations), not every citation. The 524 unchecked citations are group D rows not divisible by 7.
- The cited lines were checked against full reads of the seven source files, the front `README.md`, `.gitignore`, `plan.json` and six `.github` files (five workflows and the instructions file) held open for the whole check, plus targeted searches; not every row was opened as a separate view.
- The coverage script matches names; it does not read meaning. The depth audit covers 12 cards of the 17 and the one script walkthrough, not every card.
- Verification shows the analysis matches the code, not that the code matches what runs in production. The application, its tests and its build were not run, and no source control command was used.
- Diagrams were read and syntax-screened by a script, not rendered: no renderer is installed.
- Same model: the front page says the book was produced with Claude Sonnet 5.5, and this check was run with Claude Sonnet 5.5 in a new session. A person or another model should re-check V-012 (wrong), V-025 (omission) and a few confirmed statements (the `gate.py` `check` and `main` cards, hld/05 flows 6 and 7).
- Citations to `.github/` and `codebase-analysis/` are not stamped, so the drift check cannot see them (see Coverage findings). File times could not be used to date the knowledge base (all pages share the checkout time).
- A first run of `coverage.py` with `--report bible/verification-coverage.md` wrote a stray copy to `bible/bible/verification-coverage.md`; it was deleted and the run repeated with `--report verification-coverage.md`.

## Everything checked

Confirmed rows are given as index ranges per group. Rows that are not simply confirmed are listed one by one with their correction number.

| Citation row | Why selected | Verdict | Note |
| --- | --- | --- | --- |
| 2-416 except 8, 20, 89, 96, 104, 131, 305, 312, 320, 347, 353, 395, 400, 413 (401 rows) | A | Confirmed | `README.md`, `hld/01` to `hld/06`, `AGENT-CONTEXT.md`; the inferred and assumed rows among them were also checked against the marks rule |
| 8 | A | Citation off | V-009 |
| 20 | A | Citation off | V-010 |
| 89 | A | Overstated | V-013 |
| 96 | A | Citation off | V-001 |
| 104 | A | Citation off | V-006 |
| 131 | A | Citation off | V-011 |
| 305 | A | Citation off | V-008 |
| 312 | A | Citation off | V-002 |
| 320 | A | Citation off | V-007 |
| 347 | A | Citation off | V-003 |
| 353 | A | Overstated | V-014 |
| 395 | A | Citation off | V-004 |
| 400 | A | Citation off | V-005 |
| 413 | A | Wrong | V-012 |
| 444-445, 448-452, 476-477, 502, 511, 521-522, 531, 534-537, 547-549, 609-610, 619-624, 642, 647, 660-662, 672-673, 683, 686-687, 698-699, 760-761, 767-770, 796, 799, 802, 818-822, 867, 874-875, 896-899, 914-916, 923, 935, 947, 979-983, 1009-1011, 1105-1106 (78 rows) | B | Confirmed | |
| 512 | B | Overstated | V-015 |
| 436-441, 595-606, 611-613, 742-750, 762 (31 rows) | C | Confirmed | business-rule and outbound-call tables |
| the 85 rows of group D | D | Confirmed | |

Statements checked outside the sample: the diagram step tables of flows 1 to 10 against their `autonumber`; the 30 diagram syntax screens; the seven sweep searches of `progress.md`; the data dictionary fields; ten `analysis` and five `CALLS` graph edges; the five `.github` workflow files for the pipeline claims; the front-page totals (V-016, V-017, V-021, V-023); the ledger folder list; the unconfirmed-decision table above.
