# Repository instructions for Copilot

- Each issue names the skill to use, under `.github/skills/`. Follow that skill;
  these repository instructions never override it.
  - Component issues (`component:<name>` label): `component-analysis`, output in
    `codebase-analysis/components/<name>/`.
  - The whole-repository book (`component:bible` label): `analyzing-a-codebase`,
    output in `bible/`.
- Python 3.12, stdlib only. Run tests with
  `python -m unittest discover -s . -p "test_*.py" -t .`
- Never edit `codebase-analysis/plan.json` or anything under `tools/` or `.github/`.
- Never run git or gh yourself unless the issue says to; the harness commits.
