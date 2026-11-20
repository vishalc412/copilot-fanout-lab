# Progress

Run started 2026-11-21 (pass 1 of the PR thread, session 1). Depth: deep. Output folder: `bible/`.
Script arguments: `--repo . --analysis bible --exclude codebase-analysis --exclude .github`.
Version given by the user: none.

## Inventory (pass 1)

| Measure | Count |
| --- | --- |
| Files in scope | 13 |
| Source files / source lines | 10 / 332 |
| Classes and functions | 21 |
| Routes | 0 |
| Excluded folders | `.github` and `codebase-analysis` (excluded by the issue), `bible` (the output) |

## Components

Plan shown to the team in the PR description. Seven packets in all (every source file is under 400 lines and under 25 functions, so one packet per file).

| Component | Folders and files | Language | Starts by | Entry points | Packets |
| --- | --- | --- | --- | --- | --- |
| `orders` | `components/orders/orders.py`, `components/orders/test_orders.py` | Python 3 | imported as a library | `order_total`, `validate`, `settle` | 2 |
| `catalog` | `components/catalog/catalog.py`, `components/catalog/test_catalog.py` | Python 3 | imported as a library | `get_product`, `price_of`, `in_stock`, `fetch_supplier_feed`, `apply_feed` | 2 |
| `tools` | `tools/gate.py`, `tools/plan.py`, `tools/fanout.sh` | Python 3 and bash | run from the command line | `gate.py main`, `plan.py main`, `fanout.sh` | 3 |

Not planned: `components/__init__.py`, `components/catalog/__init__.py`, `components/orders/__init__.py` (empty files, 0 lines).

## Packets

| # | File | Lines | Status |
| --- | --- | --- | --- |
| 1 | `components/orders/orders.py` | 1-51 | done, page `lld/orders/orders.md`, 4 cards |
| 2 | `components/catalog/catalog.py` | 1-47 | done, page `lld/catalog/catalog.md`, 6 cards |
| 3 | `components/catalog/test_catalog.py` | 1-12 | done, page `lld/catalog/test_catalog.md` |
| 4 | `components/orders/test_orders.py` | 1-12 | done, page `lld/orders/test_orders.md` |
| 5 | `tools/gate.py` | 1-117 | done, page `lld/tools/gate.md`, 5 cards |
| 6 | `tools/plan.py` | 1-62 | done, page `lld/tools/plan.md`, 2 cards |
| 7 | `tools/fanout.sh` | 1-31 | done, page `lld/tools/fanout.md`, 0 cards (no functions; a script walkthrough in place of cards) |

Packets 1 to 6 done in session 1 (the budget of 6 per chat). `next.py` printed `NEW CHAT`. Packet 7 done in session 2.

## Coverage runs

| Date | Where | Files with page | Symbols | Cards | Citations | Result |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-21 | end of session 1, mid-run | 6 of 7 | 21 of 21 | 17 of 17 | 338 of 338 | GAPS: `tools/fanout.sh` page, 13 required pages and the mind map still to write |
| 2026-11-21 | session 2, after pass 9 | 7 of 7 | 21 of 21 | 17 of 17 | 1133 of 1133 | PASS (depth deep) |
| 2026-11-21 | session 3, final pass, after inventory and delta | 7 of 7 | 21 of 21 | 17 of 17 | 1134 of 1134 | PASS (depth deep) |

## Quality gate (pass 11)

| Check | Result |
| --- | --- |
| 1 Coverage gate | PASS at depth deep: files 7 of 7, symbols 21 of 21, cards 17 of 17, citations 1133 of 1133, branch lines 49 of 49, calls 9 of 9, front matter 11 of 11 |
| 2 Depth audit | `tools/gate.py` `check` card re-read against the code: every branch, message and substring rule is there; `orders.settle` and `catalog.apply_feed` cards likewise. Not repeated for every file: the repository has four source files over 40 lines |
| 4 Diagram audit | 30 diagrams. A script in the scratchpad (not part of the output) checked the pre-flight list of `mermaid-syntax.md` for flowcharts, sequence diagrams and mind maps: 0 problems. No renderer was available, so the diagrams were checked by reading only. No deployment diagram: nothing is deployed (stated in `hld/02-architecture.md`); the pipeline diagram stands in for it. No module map (fewer than 10 modules), no lifecycle (no record has a status), no class diagram (no classes besides tests) |
| 5 Evidence and safety | Every 10th row of `ledger/citations.tsv` sampled (113 rows): all support the sentence. Sweeping words in README, HLD and rules were narrowed or tied to a cited search. Search for `password`, `secret`, `token`, `api_key`, `BEGIN`, `Authorization:` in the output: hits are only the names of two repository secrets and prose about missing authentication, never a value. No e-mail address or personal data copied. Text addressed to an assistant is in `run-notes.md` |
| 6 Knowledge base | `knowledge.py` ran after the last page change; one name per thing (config keys all under `config:`); `AGENT-CONTEXT.md` follows the template, 1,500 words, cited |

### Final pass (session 3)

Steps run in order: `next.py --new-session` reported a delta (one file outside the source differed from the baseline, a file of the run harness that is no longer part of the repository; no source file and no function changed); `delta.py --apply` recorded it (0 citations moved, 0 marked, 0 work items); `next.py` then asked for a knowledge rebuild; `inventory.py`, `coverage.py` and `knowledge.py` were re-run on the final pages. The baseline was later re-initialised without that file (session 4).

| Check | Result of the final pass |
| --- | --- |
| 1 Coverage gate | PASS at depth deep, same figures as above (files 7 of 7, symbols 21 of 21, cards 17 of 17, citations 1134 of 1134, branch lines 49 of 49, calls 9 of 9, front matter 11 of 11) |
| 2 Depth audit | Re-read against the code: every card of `tools/gate.py` (`fail`, `read`, `count_tests`, `check`, `main`) and the cards of `line_total`, `order_total`, `validate`, `settle` in `orders.py`. Branches, compared values, messages, outbound call and error paths match the code; no change needed. Not re-read: `catalog.py` and `plan.py` cards (read and checked in session 2) |
| 3 Reader test | The 15 answers below still hold; every page they name exists |
| 4 Diagram audit | No page with a diagram changed since the last audit; still no renderer, so checked by reading only |
| 5 Evidence and safety | Searches re-run by hand and agree with the sweep table: no import outside the standard library and the repository's own modules; no `socket`, `listen`, `serve` or `flask` in `*.py` or `*.sh`; the five functions without a caller still have none; `decisions` occurs once (`tools/gate.py:60`). Search of the output for `password`, `passwd`, `secret`, `token`, `api_key`, `apikey`, `BEGIN`, `Authorization:` and credentials in URLs: hits are only the names of two repository secrets and prose about missing authentication, never a value. No personal data |
| 6 Knowledge base | `knowledge.py` re-run after the delta: 87 nodes, 144 edges, 220 chunks, 1 unresolved call; `AGENT-CONTEXT.md` is 1,563 words, under the 3,000 limit; no new names, so no second spelling |

`README.md` stays at DRAFT: the skill's Finish step says to leave it at DRAFT until `verifying-a-codebase-analysis` has checked the bible. Q-001 to Q-003 remain open for the team.

## Reader test

1. Business problem and users: an experiment to see whether a coding agent can analyse a codebase one component at a time on separate pull requests; users are the operator and the agent (`README.md` of the bible, "In two minutes"; `hld/01-system-context.md`).
2. What runs: nothing runs by itself. Libraries `catalog` and `orders` (Python 3), scripts `plan.py`, `gate.py` and `fanout.sh` (`hld/02-architecture.md`, Containers).
3. Where and how it starts: from a checkout or a GitHub Actions runner, by command line; no ports, no containers (`hld/02-architecture.md`, Deployment and Pipeline).
4. How a request gets in: there is no request path; entry points are the three commands and the library functions; nothing authenticates (`hld/03-integrations.md`, Inbound; `hld/06-cross-cutting.md`, Authentication).
5. Other systems: the payment partner (HTTP POST, plain `http`), the supplier feed (HTTP GET, plain `http`), GitHub through `gh`; each address is a constant in source (`hld/03-integrations.md`, Outbound).
6. Data: `_PRODUCTS` (in memory, owned by `catalog`, three SKUs with name, price, stock) and `plan.json`; no tables; input files are the four analysis files the gate reads (`lld/data-dictionary.md`).
7. Rules: the 22 numbered rules; the ten main ones are discount stacking, loyalty 5 percent, bulk 10 percent at 10 items, rounding, quantity positive, stock must cover, settlement success on 200, `price_of` raising on unknown SKU, gate pass 1, gate pass 2 and 3 (`lld/orders/README.md`, `lld/catalog/README.md`, `lld/tools/README.md`, Business rules).
8. Configuration and secrets: module constants and `ENGINE`; no secrets in the code; two workflow secrets by name (`reference/configuration.md`, `hld/06-cross-cutting.md`).
9. A dependency slow or down: the partner and feed calls time out after 15 and 10 seconds and raise to the caller; no retry (`hld/06-cross-cutting.md`, Resilience; flows 3 and 4 in `hld/05-key-flows.md`).
10. Health: none; no logs, metrics or health check beyond printed result lines (`hld/06-cross-cutting.md`, Logging).
11. Build, test, deploy: no build; `unittest` with two tests; CI workflows run the scripts; nothing deployed (`hld/06-cross-cutting.md`, Build and Testing; `hld/02-architecture.md`, Pipeline).
12. Largest handler: there are no route handlers; the largest function is `gate.check`: for an empty input it fails with `... missing`, for valid files it checks substrings, for invalid ones it appends the named messages (`lld/tools/gate.md`, card of `check`).
13. One table: `_PRODUCTS`; `name` is never written after import, `price` and `stock` are written only by `apply_feed` (`lld/data-dictionary.md`).
14. One outside system: the payment partner is called only by `settle`; on failure the exception reaches the caller, and any status other than 200 returns `False` (`lld/orders/orders.md`, card of `settle`).
15. What would surprise a new engineer: plain `http` settlement, functions with no caller, a non-atomic feed update, a baseline reset by `plan.py`, silent pass numbers (`reference/risks-and-surprises.md`).

## Questions

Last question number used: none yet.

## Component pages (pass 5)

Written in session 2: `lld/catalog/README.md`, `lld/orders/README.md`, `lld/tools/README.md`.

## Sweep

Run in session 2 over `components`, `tools`, `README.md` and `.gitignore` (`.github` and `codebase-analysis` are excluded by the issue, so they are only cited, not swept). File types `*.py`, `*.sh`, `*.md`. Every hit was read.

| Pattern | Files | Hits | What became of them |
| --- | --- | --- | --- |
| `http://` | py, sh, md | 7 | 3 real literals (`components/catalog/catalog.py:5`, `components/orders/orders.py:9`, `components/orders/orders.py:12`) documented on the module and component pages and in hld/03; 4 are the text of `tools/plan.py` that finds them (comment, regex, pass text), documented on `lld/tools/plan.md` |
| `https://` | py, sh, md | 1 | `IMAGE_CDN` (`components/catalog/catalog.py:6`), documented as a string constant only; the code never fetches it |
| `ws://`, `wss://`, `jdbc:`, `mongodb://`, `redis://`, `amqp://`, `ldap://`, `ftp://`, `file://`, `kafka`, `smtp`, `sftp` | py, sh, md | 0 | none |
| `:[0-9]{4,5}` | py, sh, md | 1 | port 8099 of `DEV_SETTLE_URL`, documented |
| `urllib`, `requests.`, `httpx`, `aiohttp`, `grpc.` | py | 5 | all `urllib.request` in `catalog.py` and `orders.py`: three outbound call sites (`components/catalog/catalog.py:38`, `components/orders/orders.py:49-50`), documented |
| `@Entity`, `CREATE TABLE`, `SQLAlchemy`, `sqlite`, `DBI` | py, sh | 0 | no database |
| `Kafka`, `Rabbit`, `Jms`, `SqsClient`, `PubSub` | py, sh | 0 | no messaging |
| `@app.route`, `urlpatterns`, `app.get(`, `router.` | py | 0 | no routes (matches the inventory: 0 routes) |
| `ENTRYPOINT`, `CMD `, `Procfile` | py, sh | 0 | none |
| `cron`, `crontab`, `@Scheduled`, `celery`, `setInterval` | py, sh | 1 | docstring `components/catalog/catalog.py:37`; nothing schedules the call (Q-002) |
| `os.environ`, `getenv`, `process.env`, `@Value` | py, sh | 0 | the only environment read is `${ENGINE:-copilot}` in `tools/fanout.sh:8` (shell syntax, not matched) |
| `jwt`, `Bearer`, `Authorization`, `api_key`, `CORS`, `csrf`, `verify=False`, `ssl`, `tls`, `TLS` | py, sh, md | 1 | comment `components/orders/orders.py:7` about the partner's TLS plan (Q-001) |
| `subprocess`, `os.system`, `child_process`, `sendmail` | py, sh | 2 | `tools/gate.py:17` and `tools/gate.py:73`, documented |
| `docker push`, `docker login`, `npm publish`, `twine upload`, `helm push`, `ghcr.io`, `azurecr`, `dkr.ecr` | py, sh | 0 | no registry or build output |
| text addressed to an assistant (`Copilot`, `Claude`, `LLM`, `you must`, ...) | py, sh, md, plus `.github` | 12 in code and docs, more in `.github` | recorded in `run-notes.md`; none acted on |

Entry points sweep (`main(`): `tools/gate.py:81`, `tools/plan.py:41`, both documented; `tools/fanout.sh` has no function.

## Questions

Last question number used: Q-003.

## Next step

The bible is complete at depth deep and `coverage.py` passes. Remaining for a person: run `verifying-a-codebase-analysis` in a new chat, on a different model if one is available; answer Q-001 to Q-003 in `reference/open-questions.md`; leave `README.md` at DRAFT until then (the skill does not allow leaving DRAFT before verification; session 3 confirmed the gate again and kept it).

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
