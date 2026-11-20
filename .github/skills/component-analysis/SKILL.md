---
name: component-analysis
description: Analyze one component of this repository in passes (1 inventory, 2 risks, 3 tests), writing only to that component's analysis folder, and stop to ask the team when a decision can't be made from the code. Use when an issue or PR comment asks for a pass of component analysis.
---

# Component analysis

One component per issue and per PR. A pass is one Copilot session. The issue
starts pass 1; each later pass is an `@copilot` comment on the same PR.

## Inputs
- `codebase-analysis/plan.json`: written by the plan job, never by you. It lists
  each component's functions and every `http://` site with `file:line`.
- The component's code under `components/<name>/`.

## Write scope (hard rule)
- Write only under `codebase-analysis/components/<name>/`.
- Pass 3 may also add or edit `components/<name>/test_*.py`.
- Never edit source code, `plan.json`, `tools/`, `.github/`, or another component.

## Passes
1. **Inventory** -> `inventory.md`: one row per function in plan.json for this
   component: name, `file:line`, what it does, who calls it (including callers in
   other components).
2. **Risks** -> `risks.md`: one row per `http://` site in plan.json:
   `file:line`, URL, decision `CHANGE` (move to https) or `KEEP` (with reason),
   or `ASK` if the decision depends on something the code can't tell you, such as
   an external party's plans. Do not change any code in this pass.
3. **Tests** -> add unit tests (stdlib `unittest`, no network) for functions that
   have none, run `python -m unittest discover -s . -p "test_*.py" -t .`, and write
   `tests-report.md`: tests added, result, functions still untested and why.

After each pass, update `status.json`:
`{"component": "<name>", "passes_done": [1, 2, ...], "open_questions": <n>}`
and run `python tools/gate.py <name> --pass <n>`. The pass is done only when the
gate prints PASS. Put the gate output in the PR description.

## When you are blocked (stop-and-ask)
If a decision can't be made from the code, plan.json or the issue:
1. Don't guess, and don't continue past that point.
2. Mark it `ASK` where it applies and commit the work done so far.
3. In the PR description, add a section `## Questions for the team` with at most
   5 questions. For each: the question, why it blocks, your recommended answer,
   and the options.
4. Record the same questions in `codebase-analysis/components/<name>/open-questions.md`.
5. End the session. Don't mark the pass complete.

When someone replies with `@copilot`, record each answer in `decisions.md`
(question, answer, who answered, date), apply it, and continue from where you
stopped. Never ask what the code or plan.json can answer.
