# Revision mode

Use when the user gives a verification report. Do not start the analysis again.

## Work through every item

Every item counts, not only the numbered corrections: coverage, depth, diagram, readability and consistency findings, and small points made without asking for a change. Give unnumbered items your own numbers (`N-01`, `N-02`, ...).

For each item:

1. Re-open the cited code yourself. The verifier can be wrong; if the code disagrees with the correction, follow the code and say so in the log.
2. Apply it:

   | Item | Action |
   | --- | --- |
   | Wrong or unsupported statement | Remove it, or replace it with what the code shows. Log the old wording. |
   | Overstated statement | Narrow it to what the cited lines support, or mark it `(inferred: ...)`. |
   | Citation off | Correct the path or lines after opening the file. |
   | Shallow card | Rewrite the card from the code: every branch, value, field, call and error. |
   | Missing file, function, route, table or outside system | Add the page, card, row or diagram element where it belongs. |
   | Inconsistent summary, flow step, diagram label or count | Fix the text. |

3. Update everything that rested on a changed statement: diagrams and their evidence tables, summaries, flow steps, the mind map, the component READMEs and the questions.
4. Move questions the revision answers to a "Closed in revision" table in `reference/open-questions.md`, with the page that answers them. Their numbers are retired.

## Bookkeeping

- Re-run `inventory.py` and `coverage.py`; the gate must pass again.
- **Ledger:** files opened for the first time, changed statuses, totals.
- **Front page status:** `CORRECTED AFTER VERIFICATION (report of <date>; <n> statements added or changed since, not re-verified)` when every item is applied, otherwise `DRAFT, corrections outstanding`.
- **`revision-log.md`:** one row per item, from the template.
- **`run-notes.md`:** any judgement made without the user.

Then run the depth audit, the diagram audit and the evidence audit from [quality-gate.md](quality-gate.md) on every added or changed page, card and diagram, and tell the user those parts are unverified.

## What comes next

| Report | Next |
| --- | --- |
| `FAIL` | Full verification again |
| `PASS AFTER CORRECTIONS` with a `major` correction | Verification of the added and changed parts |
| `PASS AFTER CORRECTIONS` with only `minor` corrections, or `PASS` | None required |

## An analysis made with an earlier version

Decide by what is on disk:

- Pages contain claim numbers like `C-154`, or `units/` or `components/` folders exist: start a new analysis from pass 1. Keep its open questions, and any fact you re-confirm with the code open. Tell the user the claim numbers will disappear.
- Otherwise, when `coverage.py --depth deep` lists missing front matter, pseudo-code, branch tables, call graphs or sequence diagrams: add them in place, then run pass 10.
