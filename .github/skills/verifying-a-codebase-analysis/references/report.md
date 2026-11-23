# Scores, verdict and report

## Scores

Over the citations in the selected sample:

- **Accuracy** = (`Confirmed` + `Citation off`) / checked
- **Citation quality** = `Confirmed` / checked

Over the cards in the depth audit:

- **Depth** = `Complete` / cards audited
- **Depth, usable** = (`Complete` + `Partial`) / cards audited

From `coverage.py`, run by you: every measure in its table, and its result.

## Verdict

| Verdict | Condition |
| --- | --- |
| `PASS` | `coverage.py` result `PASS` at the stated depth; accuracy at least 95%; depth at least 80% and no `Shallow` or `Wrong` card; no `Wrong` or `Unsupported` statement behind a diagram element; no folder missing from the ledger; no significant omission; no `major` correction; no secret value. `minor` corrections may remain. |
| `PASS AFTER CORRECTIONS` | Coverage at least 95% of files, symbols and routes; accuracy at least 85%; depth, usable at least 80%; at most five `major` corrections; every problem has a specific correction |
| `FAIL` | Anything else |

A secret value in the analysis makes the verdict at most `PASS AFTER CORRECTIONS`, with its removal as the first correction.

After `PASS`, the author may change the front page status to `VERIFIED` and cite this report. After `PASS AFTER CORRECTIONS`, a second verification is needed only if a correction was `major`, and may cover the corrected parts only.

## Report template

Write `verification-report.md` in the analysis folder.

```markdown
# Verification report

| | |
| --- | --- |
| Verdict | PASS / PASS AFTER CORRECTIONS / FAIL |
| Analysis snapshot | <file count, date, version given> |
| Repository at verification | <file count, version given> |
| Depth stated / depth found | |
| Verified with | <assistant and model> |
| Analysis produced with | <from the front page> |
| Sampling level | |
| Date | |

## Summary
How complete, deep and reliable the analysis is, where it is weakest, and why the verdict is
what it is. Written for a manager deciding whether to rely on it.

## Scores
| Measure | Value |
| --- | --- |
| Source files with a page | |
| Symbols accounted for | |
| Functions with a full card (pseudo-code, branches cited) | |
| Branch lines cited / call-graph edges drawn / front matter | |
| Routes with an endpoint card | |
| Citations that resolve | |
| Coverage gate | PASS / GAPS |
| Citations in the analysis / checked | |
| Confirmed / Citation off / Overstated / Wrong / Unsupported | |
| Omissions (significant) / Inconsistent | |
| Accuracy / citation quality | |
| Cards audited: Complete / Partial / Shallow / Wrong | |
| Depth / depth, usable | |

## How the sample was selected

## Corrections
| # | Page and line, or citation row | Verdict | Weight | What the code shows | Evidence | Correction |
| --- | --- | --- | --- | --- | --- | --- |
| V-001 | lld/backend/upload_service.md:42 | Wrong | major | | `app/upload_service.py:212` | |

## Coverage findings
## Depth findings
| File | Card | Score | What is missing |
## Diagram findings
| Diagram | D1 | D2 | D3 | D4 | D5 | D7 | D9 | Note |
## Data dictionary and mind map findings
## Knowledge base findings
## Readability and prose findings
## Ledger findings
## Consistency findings
## Limits

## Everything checked
Every citation not simply confirmed, one row each. Confirmed ones may be index ranges per
group. Then statements checked outside the sample, and the diagram, ledger and consistency checks.

| Citation row | Why selected | Verdict | Note |
```

## Limits to state

- A sample was checked, unless the level was `full`.
- The coverage script matches names; it does not read meaning. The depth audit covers the files it names, not every card.
- Verification shows the analysis matches the code, not that the code matches what runs in production.
- Diagrams were read, not rendered, unless you could render them. Say which.
- If the same model wrote and verified the analysis, say so, and recommend a person or another model re-check the `major` corrections and a few confirmed statements.
