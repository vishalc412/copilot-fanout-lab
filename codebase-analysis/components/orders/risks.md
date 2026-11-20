# orders: risks (pass 2)

Scope: every `http://` site listed for `orders` in `codebase-analysis/plan.json`. No source code was changed.

| file:line | URL | Decision | Reason |
|-----------|-----|----------|--------|
| `components/orders/orders.py:9` | `http://partner-legacy.internal/settle` | ASK | Production settlement endpoint (`PARTNER_SETTLE_URL`, used by `settle()` unless `dev=True`). Moving to https is only possible if the partner serves TLS on this host. The code comment says their ops team described TLS as "coming soon" with no date, and that settlement must not break during month-end close. Switching the URL before the partner supports TLS would make every settlement fail. Whether to wait, and what to do meanwhile, depends on the partner's plans and on a business constraint. See `open-questions.md` (Q1, Q2). |
| `components/orders/orders.py:12` | `http://localhost:8099/settle` | KEEP | `DEV_SETTLE_URL` is a local fake for developers and is only selected when `settle(..., dev=True)`. The code comment says it is never deployed. The loopback address does not leave the machine, so TLS adds nothing. Nothing in the repo passes `dev=True` (no callers of `settle` were found), so this cannot be reached in production by the code as it stands. |

## Notes
- Exposure at line 9: `settle()` sends `{"order": <id>, "amount": <amount>}` as JSON over plain HTTP. No credentials or card data are visible in the code, but order ids and amounts travel unencrypted, and the response status is the only success signal (`status == 200`), so a tampered response could not be detected.
- Pass 2 is not complete: line 9 is ASK. The gate fails until the answer is recorded in `decisions.md` and the row is changed to CHANGE or KEEP.
