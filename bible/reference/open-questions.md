# Open questions

Questions the code cannot answer. Each was searched for first.

| # | Question | Why it matters | Where I looked | Who could answer |
| --- | --- | --- | --- | --- |
| Q-001 | Is `http://partner-legacy.internal/settle` still plain HTTP today, and is there a date or a plan for TLS on that host? The comment says the partner's operations team announced TLS as "coming soon" with no date, and that settlement must not break at month-end close. Should `PARTNER_SETTLE_URL` stay `http` (KEEP) or move to `https` (CHANGE)? | `settle` sends order ids and amounts without TLS and without an authentication header; the decision depends on the partner, not on the code | `components/orders/orders.py:7-9`, `components/orders/orders.py:45-51`; search `https` for the partner host in the repository: 0 hits | the team that owns the partner integration |
| Q-002 | What runs `fetch_supplier_feed` nightly, and what passes its result to `apply_feed`? The docstring says "Runs nightly from cron" but nothing in the repository schedules or calls either function. | If no job exists, prices and stock never refresh; if it exists elsewhere, its configuration is part of the system | `components/catalog/catalog.py:36-47`; search `fetch_supplier_feed`, `apply_feed`, `cron` in the repository outside `catalog.py` and its docs: 0 hits (the one `cron` hit is the docstring); no crontab, workflow or job file | the team that owns the supplier feed job |
| Q-003 | Who calls `order_total`, `validate` and `settle`? No code in the repository does, outside one test of `line_total`. Is `validate` meant to run before `order_total` and `settle`? | The order of calls decides whether a bad quantity or unknown SKU reaches pricing and settlement | search `order_total`, `validate`, `settle` in `*.py` and `*.sh` outside `components/orders/orders.py`: 0 hits | the team that owns the code that imports `orders` |

<!-- cites components/catalog/catalog.py@1e15fdaab1fa3c720d99a864abb4cac9c8259421 -->

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->
