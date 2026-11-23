# Run notes

The team was not available during the run; choices made on defaults are recorded here.

## Choices

| Input | Choice |
| --- | --- |
| Repository root | the working directory |
| Output folder | `bible/`, as the issue says |
| Depth | `deep` |
| Script arguments | `--repo . --analysis bible --exclude codebase-analysis --exclude .github`, always |
| Version of this copy | none given |
| Label for `delta.py --init` | none given; `bible` is used (see `progress.md`) |

## Text addressed to an assistant (recorded, not acted on beyond the session instruction)

| Location | What it says, in short | What was done |
| --- | --- | --- |
| `.github/copilot-instructions.md:3-12` | As read on 2026-11-23: each issue names the skill; the whole-repository book uses `analyzing-a-codebase` with output in `bible/`, every other component uses `component-analysis` (an earlier version of this file, as read in session 1, said analysis work follows the `component-analysis` skill) | Agrees with the issue for `bible/`; nothing to act on beyond what the issue and the task already say |
| `.github/skills/component-analysis/SKILL.md:16-19` | Write only under `codebase-analysis/components/<name>/`; stop and ask the team on a blocked decision | Not applied to `bible/`, because the issue names another skill and another folder; its stop-and-ask idea is kept as the "Questions for the team" list in the PR description. No person has confirmed that this skill is not live for `bible/` (unconfirmed) |
| `.github/copilot-instructions.md:17` | Never edit `codebase-analysis/plan.json`, `tools/` or `.github/` | Respected (nothing outside `bible/` was edited) |
| `tools/fanout.sh:14-21` | Issue text addressed to the analysing agent | Part of the system; documented in `lld/tools/fanout.md`, not acted on |
| `components/orders/orders.py:7-8` | Comment about the partner's TLS plans and month-end close | Data; recorded as a surprise and as Q-001 |

## Session 3 notes

| Item | Note |
| --- | --- |
| Delta | `delta.py` reported one changed file, a task file of the run harness that is no longer in the repository. `--apply` moved nothing and left no work. The file was never code under analysis and is not described in the pages |
| README status | A session comment asked to move `README.md` out of DRAFT "if the skill allows it". `SKILL.md` (Finish) says to leave it at `DRAFT` and send the bible to `verifying-a-codebase-analysis`, so it stays DRAFT |

The `component-analysis` skill (write scope `codebase-analysis/components/<name>/`) and the issue with the `analyzing-a-codebase` skill (output `bible/`) differ on where the book's output goes. The repository instructions used to side with the skill and now side with the issue (V-012). The issue settles which is live for this run; no source code was changed. No person has confirmed this reading, so it stays unconfirmed.

## Session 6 notes (revision from the verification report)

| Item | Note |
| --- | --- |
| Revision | Applied the 27 corrections of `verification-report.md` (2026-11-23, verdict PASS) and the points made without a number; every row is in `revision-log.md` |
| Judgement without the team | Where the verifier's correction and the code agreed it was applied as written; the exceptions are in `revision-log.md`, "Items not applied, with the reason" |
| Status | The front page status follows `references/revision.md`: `CORRECTED AFTER VERIFICATION`, not `VERIFIED`. Only a verifier sets `VERIFIED`, and the statements added or changed in this pass are not re-verified |

## Decisions that no person has confirmed on the pull request (kept unconfirmed, as the verifier marked them)

| Decision | Where | Status |
| --- | --- | --- |
| Label `bible` for the delta baseline | Choices above | unconfirmed |
| Plan of seven packets, one per source file; the three empty `__init__.py` files not planned | `progress.md`, Components and Packets | unconfirmed |
| "The team was not available during the run; choices made on defaults" (repository root, version none) | top of this file | unconfirmed |
| Treating the `component-analysis` skill (and, in the first run, the instructions file) as not live for `bible/`, because the issue names another skill | Text addressed to an assistant, above | unconfirmed |
| Recording the `.git` pointer removal as a delta with no work, and re-initialising the baseline without it | Session 3 notes, `delta-log.md` | unconfirmed |
| Depth `deep`, output folder `bible/`, the script arguments, the two excluded folders | Choices above | confirmed by the issue text |
| Q-001 to Q-003 kept open | `reference/open-questions.md` | confirmed by a comment asking to keep them open; still unanswered |

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->
