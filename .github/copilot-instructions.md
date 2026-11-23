# Repository instructions for Copilot

- Each issue names the skill to use, under `.github/skills/`. Follow that skill;
  these repository instructions never override it.
  - The whole-repository book (label `component:bible`): `analyzing-a-codebase`.
    Run its scripts with `--repo . --analysis bible --exclude codebase-analysis --exclude .github`
    so the output goes to `bible/`, not the skill's default folder.
  - Verifying the book: `verifying-a-codebase-analysis` on the analysis folder
    `bible/` (pass `--analysis bible` and the same `--exclude` arguments), in a
    new session that did not write the book.
  - Every other `component:<name>` label: `component-analysis`, output in
    `codebase-analysis/components/<name>/`.
- Commits come from your agent harness: the Copilot coding agent commits for you,
  and the local stand-in harness commits after the session. Never push to `main`.
- Python 3.12, stdlib only. Run tests with
  `python -m unittest discover -s . -p "test_*.py" -t .`
- Never edit `codebase-analysis/plan.json` or anything under `tools/` or `.github/`.
