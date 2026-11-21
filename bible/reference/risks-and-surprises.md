# Risks and surprises

What a new engineer must be warned about, ordered by impact: security, data loss, outages, wrong results, maintainability. Each row names the page that has the detail.

| # | What | Why it matters | Evidence | Page |
| --- | --- | --- | --- | --- |
| 1 | The payment partner address is plain `http`, and `settle` sends order id and amount with no authentication header | Order and amount travel unencrypted and unauthenticated; the comment says the partner plans TLS without a date (`Q-001`) | `components/orders/orders.py:7-9`, `components/orders/orders.py:48-50` | [orders](../lld/orders/orders.md), `hld/03-integrations.md` |
| 2 | The supplier feed address is plain `http`, and the feed is applied with no signature or schema check | A person in the path could change prices and stock | `components/catalog/catalog.py:5`, `components/catalog/catalog.py:36-47` | [catalog](../lld/catalog/catalog.md) |
| 3 | `apply_feed` is not atomic: an item without `price` or `stock`, or with a non-numeric value, raises after earlier items were applied | A bad feed leaves the product table half updated | `components/catalog/catalog.py:44-47` | [catalog](../lld/catalog/catalog.md) |
| 4 | `settle` has no retry, no idempotency key and no handling of errors; a timeout does not say whether the partner processed the order | A caller that retries after a timeout may settle twice (inferred: no key in the body at `components/orders/orders.py:48`) | `components/orders/orders.py:45-51` | [orders](../lld/orders/orders.md) |
| 5 | `validate` is not called by `order_total` or `settle`, and no caller in the repository calls them | A negative quantity lowers a total; an unknown SKU raises `KeyError` in pricing (`Q-003`) | `components/orders/orders.py:23-32`, `components/orders/orders.py:35-42` | [orders](../lld/orders/orders.md) |
| 6 | `fetch_supplier_feed` is documented as nightly from cron, but nothing schedules it or calls `apply_feed` (`Q-002`) | Prices and stock may never refresh | `components/catalog/catalog.py:37` | [catalog](../lld/catalog/catalog.md) |
| 7 | `get_product` returns the live record | A caller that edits the returned dict changes the catalog | `components/catalog/catalog.py:17` | [catalog](../lld/catalog/catalog.md) |
| 8 | `in_stock` gives `False` for an unknown SKU and for too little stock, so `validate` reports both as "not enough stock"; `in_stock` with `qty` of zero or less is always true for a known SKU | The caller cannot tell a typo from a sold-out product | `components/catalog/catalog.py:29`, `components/orders/orders.py:40-41` | [catalog](../lld/catalog/catalog.md), [orders](../lld/orders/orders.md) |
| 9 | `plan.py` recounts `test_count` on every run, which moves the baseline of gate pass 3 | Running it after tests were added removes the "new tests" check | `tools/plan.py:3-5`, `tools/plan.py:36`, `tools/gate.py:69-72` | [plan](../lld/tools/plan.md) |
| 10 | The gate's ASK message tells the reader to wait for an answer in `decisions.md`, a file the gate never reads | The message points to a place the check does not use | `tools/gate.py:60` | [gate](../lld/tools/gate.md) |
| 11 | Pass numbers other than 1, 2 and 3 pass silently, and the pass 3 check runs the whole repository's tests | A typo such as `--pass 4` prints PASS; a failing test in another component fails this component's pass 3 | `tools/gate.py:45-78`, `tools/gate.py:73-75` | [gate](../lld/tools/gate.md) |
| 12 | `fanout.sh` creates issues again on every run, and an unknown `ENGINE` is noticed only after labels were made | Duplicate issues; partial side effects | `tools/fanout.sh:10-12`, `tools/fanout.sh:25-29` | [fanout](../lld/tools/fanout.md) |
| 13 | Two documents that act disagree on where analysis output goes: `.github/copilot-instructions.md` and the `component-analysis` skill say `codebase-analysis/components/<name>/`, while the issue for this book says `bible/` | An agent that follows the wrong one writes in the wrong place; the PR scope check accepts `bible/` as a separate "book" component | `.github/copilot-instructions.md:3-4`, `.github/skills/component-analysis/SKILL.md:16-17`, `.github/workflows/analysis-gate.yml:28-29` | `run-notes.md` |
| 14 | The repository README says the settlement URL should make pass 2 stop and ask; the code comment is the only place that explains the URL | The reason is a comment, not a decision record | `README.md:12-13`, `components/orders/orders.py:7-9` | [orders](../lld/orders/orders.md) |
| 15 | Both `http://partner-legacy.internal/settle` and the developer-only `http://localhost:8099/settle` appear in the plan as sites to classify, because the pattern cannot tell them apart | Pass 2 must classify a developer fake as if it were deployed | `tools/plan.py:18`, `codebase-analysis/plan.json:76-85` | [plan](../lld/tools/plan.md) |
| 16 | The tools component has no tests, and the library has one test per component | Discounts, validation, settlement, the feed and every gate rule are untested | `components/orders/test_orders.py:7-8`, `components/catalog/test_catalog.py:7-8` | [tools](../lld/tools/README.md) |

<!-- cites README.md@61543f4e8ea18677f318b804951295e5b678b877 -->

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/catalog/test_catalog.py@9be40d147e425d178067c8b34f19b28b9b374d1f -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites components/orders/test_orders.py@ca9144cf39abe39e988dc009863b036a7ee1a39f -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->

<!-- cites tools/gate.py@65eb0af527e554cfb2dadb9d0c8cd1ee6e975c99 -->

<!-- cites tools/plan.py@e1dae33df7990fe69b145146d570403758d0635e -->
