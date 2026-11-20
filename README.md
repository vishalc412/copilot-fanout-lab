# copilot-fanout-lab

Experiment: does the Copilot coding agent support component fan-out (one PR per
component, several passes per PR) and two-way stop-and-ask on the PR thread?

- `components/catalog`, `components/orders`: sample code.
- `tools/plan.py`: step 0, deterministic inventory -> `codebase-analysis/plan.json`.
- `tools/fanout.sh`: one issue per component, assigned to Copilot.
- `.github/skills/component-analysis/`: the skill Copilot follows.
- `tools/gate.py` + `.github/workflows/analysis-gate.yml`: per-component gate in CI.

`components/orders/orders.py` has a settlement URL whose https decision depends on
an external partner, so pass 2 should stop and ask.
