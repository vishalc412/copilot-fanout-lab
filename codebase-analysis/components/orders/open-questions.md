# orders: open questions

All answered on 2026-11-23; answers are in `decisions.md`. Nothing is open.

Originally blocking pass 2 (risks). Both concern `components/orders/orders.py:9` (`http://partner-legacy.internal/settle`).

## Q1. Has the settlement partner committed to a date or endpoint for TLS on `partner-legacy.internal`?
- **Why it blocks:** The code says only that TLS is "coming soon" with no date. If the host does not serve https, changing the URL breaks every settlement. Nothing in the repo or plan.json can tell us the partner's plans.
- **Recommended answer:** No date yet; classify as KEEP for now and revisit once the partner confirms an https endpoint in writing.
- **Options:**
  1. No date known: KEEP now, revisit when the partner confirms.
  2. Partner has a date or an https endpoint: give the date and URL, and classify as CHANGE (with the rollout timing below).

## Q2. How should the change be timed relative to month-end close?
- **Why it blocks:** A comment in the code says settlement must never break during month-end close. If the answer to Q1 is CHANGE, the team must say whether a switch is allowed in a close window, and whether a fallback to http is acceptable during the transition. This is a business constraint, not something the code states.
- **Recommended answer:** Do the switch outside month-end close, and keep it behind a config value so it can be rolled back without a code change (a follow-up, not part of this analysis).
- **Options:**
  1. Switch outside month-end close only, with a rollback path.
  2. Switch at any time once the partner's https endpoint is verified.
  3. Never change until the partner retires the legacy host.
