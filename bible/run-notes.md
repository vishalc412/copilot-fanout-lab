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
| `.agent/PROMPT.md` | The session instruction from the run harness: follow the issue and the skill, write only under `bible/` | Followed as the session instruction, since it comes from the harness and not from the repository code |
| `.github/copilot-instructions.md:3-4` | Analysis work follows the `component-analysis` skill | Not followed for `bible/`: the issue names `analyzing-a-codebase` and says `codebase-analysis/` belongs to the component lab |
| `.github/skills/component-analysis/SKILL.md:16-19` | Write only under `codebase-analysis/components/<name>/`; stop and ask the team on a blocked decision | Not applied to `bible/`; its stop-and-ask idea is kept as the "Questions for the team" list in the PR description |
| `.github/copilot-instructions.md:7` | Never edit `codebase-analysis/plan.json`, `tools/` or `.github/` | Respected (nothing outside `bible/` was edited) |
| `tools/fanout.sh:14-21` | Issue text addressed to the analysing agent | Part of the system; documented in `lld/tools/fanout.md`, not acted on |
| `components/orders/orders.py:7-8` | Comment about the partner's TLS plans and month-end close | Data; recorded as a surprise and as Q-001 |

## Session 3 notes

| Item | Note |
| --- | --- |
| Delta | `delta.py` reported one changed file, `.agent/PROMPT.md` (the harness's task file, which is inside the repository root and so inside the scope). `--apply` moved nothing and left no work. The file is the session instruction, not code under analysis, and is not described in the pages |
| README status | A session comment asked to move `README.md` out of DRAFT "if the skill allows it". `SKILL.md` (Finish) says to leave it at `DRAFT` and send the bible to `verifying-a-codebase-analysis`, so it stays DRAFT |

The two documents that act (`copilot-instructions.md` and the `component-analysis` skill on one side, the issue and the `analyzing-a-codebase` skill on the other) differ on where output goes. The issue settles which is live for this run; no source code was changed.

<!-- cites components/orders/orders.py@33203a1b4d48a6d335cf411f56a54a7035a66ae0 -->

<!-- cites tools/fanout.sh@9ad43aa70e042837954fea1faf483f6c08e07470 -->
