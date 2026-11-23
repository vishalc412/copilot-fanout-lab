# Revision log

Applied from: `verification-report.md` of 2026-11-23, verdict PASS (27 numbered corrections, all `minor`, and the points made without a number, numbered N-01 and on here). Revision pass of 2026-11-23 (session 6). Every cited line below was re-opened in the repository before the text was changed; the report's page and line positions were checked against the pages first.

| Item | Location | What was done | Code re-opened | Agrees with the report? |
| --- | --- | --- | --- | --- |
| V-001 | `hld/02-architecture.md` Technology table; `reference/configuration.md` Python 3.12 row | Python 3.12 now cites `.github/copilot-instructions.md:15` | `.github/copilot-instructions.md:15-16` | yes |
| V-002 | `hld/06-cross-cutting.md` Testing | the unittest command now cites lines 15-16 | `.github/copilot-instructions.md:15-16` | yes |
| V-003 | `knowledge/AGENT-CONTEXT.md` How to run and test | cites lines 15-16 | same | yes |
| V-004 | `knowledge/AGENT-CONTEXT.md` Conventions | cites lines 15-16 | same | yes |
| V-005 | `knowledge/AGENT-CONTEXT.md` Conventions; `run-notes.md` | the "never edit" rule now cites line 17 in both | `.github/copilot-instructions.md:17` | yes |
| V-006 | `hld/02-architecture.md` Technology table | `claude-code-action@v1` now cites `claude.yml:42` | `.github/workflows/claude.yml:42` | yes |
| V-007 | `hld/06-cross-cutting.md` Dependencies | same | same | yes |
| V-008 | `hld/06-cross-cutting.md` Logging | the echo step now cites `claude.yml:25-28` | `.github/workflows/claude.yml:25-28` | yes |
| V-009 | `README.md` In two minutes | "no authentication" now also cites `components/orders/orders.py:48-50`, the headers built in `settle` | `components/orders/orders.py:48-50` | yes |
| V-010 | `hld/01-system-context.md` opening; `00-mind-map.md` opening (same citation) | now cites `README.md:1-10` | `README.md:1-10` | yes |
| V-011 | `hld/03-integrations.md` outbound row for `fanout.sh` | "stops at the first failure" now names `set -euo pipefail` and cites `tools/fanout.sh:6` | `tools/fanout.sh:6` | yes |
| V-012 | `knowledge/AGENT-CONTEXT.md` Hazards; `reference/risks-and-surprises.md` row 13; `run-notes.md` (text-addressed table and closing paragraph) | the hazard now names only the `component-analysis` skill (`SKILL.md:16-19`) against the issue, says the instructions of 2026-11-23 route the book to `bible/` (`copilot-instructions.md:5-7`, `:11-12`) and that no person has said which document is live | `.github/copilot-instructions.md:3-17`, `.github/skills/component-analysis/SKILL.md:16-19`, `.github/workflows/analysis-gate.yml:28-29` | yes; I did not say which document is live: that stays an open decision (PR description) |
| V-013 | `hld/02-architecture.md` Pipeline table and diagram label | "runs four scripts (the coverage gate only on pull requests; a manual start runs three)" | `.github/workflows/toolkit-analysis.yml:25-27` | yes |
| V-014 | `knowledge/AGENT-CONTEXT.md` How to run and test | `gh` login is now `(assumed: gh own credentials)`, no longer stated as a fact | `tools/fanout.sh:3-10` | yes |
| V-015 | `lld/catalog/catalog.md` `apply_feed` Errors; `lld/catalog/README.md` Errors; `reference/risks-and-surprises.md` row 3 | `KeyError` for a missing key, `ValueError` for a non-numeric string, `TypeError` for a `null` or a list | `components/catalog/catalog.py:44-47` | yes |
| V-016 | `README.md` Snapshot; `ledger/coverage-ledger.md`; `progress.md`; `knowledge/AGENT-CONTEXT.md` | 12 files in scope everywhere, with the reason for the earlier 13 and 14; `ledger/inventory.json` re-run on 2026-11-23 says 12 | `ledger/inventory.json` after `inventory.py`; repository listing | yes |
| V-017 | `README.md` Totals; `progress.md` final pass | graph is 86 nodes, 144 edges, 233 chunks, dated 2026-11-23, after `knowledge.py` was run again | `knowledge/graph.json` stats | yes |
| V-018 | `knowledge/AGENT-CONTEXT.md` Function index | "Outside the two tests, nothing else calls across files", with the two test calls cited | `components/orders/test_orders.py:8`, `components/catalog/test_catalog.py:8` | yes |
| V-019 | `hld/04-data-architecture.md` opening | "The shop keeps no data on disk"; the sentence now says `plan.py` writes `plan.json` to disk | `tools/plan.py:55-57` | yes |
| V-020 | `lld/orders/README.md` Responsibility | lists the same five search terms as `orders.md` (3 hits, lines 3, 7, 8 of `test_orders.py`), and says only `line_total` is called | `components/orders/test_orders.py:3,7,8`; search of `components` and `tools` | yes |
| V-021 | `progress.md` final pass, reader test 15, sweep table | "six" functions without a caller, listed by name; the `http://` row says three hits in `plan.py` and one in `gate.py` | `components/catalog/catalog.py:32-33`; `tools/plan.py:6,18,50`; `tools/gate.py:8` | yes (search repeated: 7 hits) |
| V-022 | `00-mind-map.md` system map, tools map and list | "Analysing coding agent" added under outside systems on both maps and the list; the AI service of the Claude action added to the system map (see V-025) | `README.md` Totals, `hld/01-system-context.md` | yes |
| V-023 | `ledger/coverage-ledger.md` folder rows | catalog 3, orders 3, root 2; the `.git` entry dropped from the root row and listed as an excluded folder; totals 12 | listings of `components/catalog`, `components/orders`, root | yes |
| V-024 | `hld/02-architecture.md` containers diagram and element table | added the store "Analysis files read by the gate" and the `unittest` child process, with edges from `gate` and evidence rows; the intro sentence says what is drawn | `tools/gate.py:46,52,64,73-75,94` | yes |
| V-025 | `hld/01-system-context.md` diagram, element table and outside-systems table; `hld/02-architecture.md` pipeline diagram, table and `claude.yml` paragraph; `README.md` diagram, table and Totals | added the AI service of the Claude action as an outside system (dashed, `(assumed: the action's own behaviour)`) and listed the four permissions of `claude.yml`; outside systems are now 6 | `.github/workflows/claude.yml:19-23,29-36,42-46` | yes; the name "Anthropic API" is an assumption from the `anthropic_api_key` input and the action name |
| V-026 | `lld/orders/orders.md` `validate` card (Inputs, Branches and errors, Output, Errors); `lld/orders/README.md` Errors; `hld/05-key-flows.md` flow 2 failure paths | the error path is added: a `qty` that is not a number raises `TypeError` at `qty <= 0`; a pair that does not unpack raises; the list is then lost. The flow 2 diagram is unchanged (the failure is named in the text under it) | `components/orders/orders.py:35-42` | yes |
| V-027 | `README.md`, `hld/01`, `hld/02`, `hld/03`, `hld/05` flow 8, `lld/tools/README.md`, `knowledge/AGENT-CONTEXT.md` | every statement that the operator runs `fanout.sh` now carries `(inferred: usage comment)`; the matching diagram edges are dashed, with the legends adjusted. Searched `fanout` outside the script: 2 hits, both in the repository README | `tools/fanout.sh:3`; search of `.github`, `components`, `tools`, `README.md` | yes |
| N-01 | `reference/configuration.md` secrets row (the report's "also noticed") | names at `claude.yml:32-33` and the use at `:45-46`; the same drift fixed in `hld/06` Secrets (`:29-36`, `:42-46`) and `hld/02` (`:29-46`) | `.github/workflows/claude.yml:29-46` | yes |
| N-02 | `hld/06-cross-cutting.md` Authentication | the repeated search sentence removed | `hld/06` text | yes |
| N-03 | `hld/05-key-flows.md` opening | rewritten: no caller of the five functions, the tests included; the tests call only `line_total` and `price_of` | `components/*/test_*.py` | yes |
| N-04 | `lld/data-dictionary.md` `.gitignore` | not applied as the report suggests (naming the third pattern). A comment on this pull request (2026-11-20) asked for references to the retired run-harness folder to be removed from `bible/`; the pattern stays unnamed and the page now says why | `.gitignore:1-3` | no, by choice; a person can reverse it |
| N-05 | `README.md` | added "Known limit": `.github/` citations carry no stamp, the drift check cannot see them, and a person should re-check them when those files change. Open question for the team in the PR description | `.github/copilot-instructions.md` (already changed once) | yes |
| N-06 | `README.md` Totals | marks counted again on 2026-11-23: the marks (an opening bracket followed by the word) in the pages (front page, mind map, HLD, LLD, reference, agent primer), stated as a count with its definition | the pages | yes |
| N-07 | `knowledge/AGENT-CONTEXT.md` | the graph has three `External` nodes (the systems the source files call) against six outside systems on the front page: not changed in the graph, because `knowledge.py` builds those nodes from the `calls` front matter of module pages and GitHub Actions, the agent and the AI service are not called from any source file. The primer now says so | `knowledge/nodes.csv` | partly: the cause is explained and written down, no node added |
| N-08 | `lld/tools/README.md` element table and legend | evidence rows added for the operator and CI edges of the structure diagram | `tools/plan.py:61-62`, `tools/gate.py:116-117`, `tools/fanout.sh:3` | yes |
| N-09 | `run-notes.md` | the decisions the verifier marked unconfirmed are listed in one table and stay unconfirmed; none was marked confirmed | `verification-report.md` table | yes |
| N-10 | `README.md` Verification paragraph | the same-model limit and the advice that a person or another model re-check V-012, V-025 and the changed parts are stated on the front page | `verification-report.md` Limits | yes |

No other point of the report asked for a change: the coverage findings ("Gaps: none"), the depth findings (11 of 12 cards Complete), the diagram syntax screen, the knowledge base edge samples and the ledger completeness check were confirmations. The first-run `--report` path slip of the checker left nothing in the book (`bible/bible/` does not exist).

## Statements added

- The AI service of the Claude action as an outside system, and the four `claude.yml` permissions (V-025).
- The analysis files and the `unittest` child process on the containers diagram (V-024).
- The error path of `validate` for malformed lines (V-026).
- The "Known limit" and "Verification" paragraphs on the front page, the session 6 notes and the unconfirmed-decisions table in `run-notes.md`, and the explanation of the graph's External nodes (N-05, N-07, N-09, N-10).

## Statements corrected

- Citations: V-001 to V-011 and N-01.
- Wording narrowed or fixed: V-012 to V-015, V-018 to V-021, V-027, N-02, N-03.
- Counts and dates: V-016, V-017, V-023, N-06 (12 files, 86 nodes, 233 chunks, 1209 citations, six outside systems).
- Diagrams: V-022, V-024, V-025, V-027, N-08.

## Statements withdrawn

- "Nothing raised" for `validate` (V-026) and "ValueError for a value that is not a number" as the only conversion error (V-015).
- "Two acting documents disagree" about the repository instructions (V-012): the instructions no longer disagree with the issue.
- "13 files", "14 files", "87 nodes" and "about 51 / 27" as figures (V-016, V-017, N-06).

## Questions closed or narrowed

None closed. Q-001 to Q-003 are still open for the team; the revision does not answer them. The wish of V-012 to know which acting document is live is a decision for the team, not a code question, and is in the PR description.

## Items not applied, with the reason

- N-04: the third `.gitignore` pattern is not named, because a person's earlier comment on this pull request asked for references to that folder to be removed. Reversible by a person.
- N-07: no `External` node was added to the graph for GitHub Actions, the agent or the AI service, because the graph is built from the pages' `calls` lists and none of the three is called from a source file; a false `calls` entry would put a wrong edge in the graph. The difference is documented instead.
- The diagram of flow 2 in `hld/05-key-flows.md` was not redrawn for the malformed-input error of V-026: the step table is numbered by the diagram's `autonumber`, and the failure is stated in the text under the table (an unhandled exception, not a branch the code takes).
- The baseline `pending` entry `remove-file .git` in `ledger/baseline.json` was left as `delta.py` wrote it: ledger files are not edited by hand.

## Audits of the changed parts (unverified by anyone else)

- Depth: the `validate` and `apply_feed` cards were re-read against `orders.py:35-42` and `catalog.py:42-47`; every branch, message and error path is now named.
- Diagrams: the changed diagrams (front page, context, containers, pipeline, the three mind maps, `lld/tools/README.md` structure) were screened with the pre-flight list of `mermaid-syntax.md` by a script in the scratchpad: 0 problems on all diagrams of the book. Not rendered: no renderer is installed.
- Evidence: every changed citation was re-opened; sweeping words were narrowed or tied to a search; no secret value (the search of the output hits only names); no personal data.
