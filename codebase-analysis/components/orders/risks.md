# orders: risks (pass 2)

Scope: every `http://` site listed for `orders` in `codebase-analysis/plan.json`. No source code was changed.

| file:line | URL | Decision | Reason |
|-----------|-----|----------|--------|
| `components/orders/orders.py:9` | `http://partner-legacy.internal/settle` | KEEP | Production settlement endpoint (`PARTNER_SETTLE_URL`, used by `settle()` unless `dev=True`). The partner has given no TLS date, and switching to https before they serve TLS on this host would make every settlement fail. Decided by the tech lead on 2026-11-23: keep http for now and revisit when the partner confirms an https endpoint in writing (`decisions.md` Q1). Condition for the future switch: only outside month-end close, behind a config value so it can be rolled back without a code change; that is a follow-up change, not part of this analysis (`decisions.md` Q2). |
| `components/orders/orders.py:12` | `http://localhost:8099/settle` | KEEP | `DEV_SETTLE_URL` is a local fake for developers and is only selected when `settle(..., dev=True)`. The code comment says it is never deployed. The loopback address does not leave the machine, so TLS adds nothing. Nothing in the repo passes `dev=True` (no callers of `settle` were found), so this cannot be reached in production by the code as it stands. |

## Notes
- Exposure at line 9: `settle()` sends `{"order": <id>, "amount": <amount>}` as JSON over plain HTTP. No credentials or card data are visible in the code, but order ids and amounts travel unencrypted, and the response status is the only success signal (`status == 200`), so a tampered response could not be detected.
- Line 9 remains a known risk while it is KEEP: order ids and amounts travel unencrypted. Revisit trigger: the partner confirms an https endpoint in writing.
- Both sites are now decided (KEEP); pass 2 is complete.
