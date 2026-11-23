# orders: decisions

Answers to the questions in `open-questions.md`. Both concern `components/orders/orders.py:9` (`http://partner-legacy.internal/settle`).

## Q1. Has the settlement partner committed to a date or endpoint for TLS on `partner-legacy.internal`?
- **Answer:** No TLS date from the partner yet. KEEP `http://partner-legacy.internal/settle` for now; revisit when the partner confirms an https endpoint in writing.
- **Answered by:** vishalc412, relaying the tech lead (PR #6 comment).
- **Date:** 2026-11-23
- **Applied:** `risks.md` row for `components/orders/orders.py:9` changed from ASK to KEEP.

## Q2. How should the change be timed relative to month-end close?
- **Answer:** When the switch happens: outside month-end close only, behind a config value so it can be rolled back without a code change. That is a follow-up change, not part of this analysis.
- **Answered by:** vishalc412, relaying the tech lead (PR #6 comment).
- **Date:** 2026-11-23
- **Applied:** Recorded as a condition on the future switch in `risks.md`. No code was changed in this pass.
