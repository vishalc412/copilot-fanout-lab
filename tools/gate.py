"""Per-component gate. Deterministic; runs in CI and can be run by the agent.

usage: python tools/gate.py <component> [--pass N]
Without --pass, checks every pass listed in the component's status.json, and
fails while status.json reports open questions (the component is blocked).

Pass 1: inventory.md names every function in plan.json for the component.
Pass 2: risks.md lists every http:// site (file:line) as CHANGE or KEEP.
        An unresolved ASK fails the gate: the component is blocked on a human.
Pass 3: tests-report.md exists, the component has more test functions than in
        plan.json, and the component's tests pass.
"""
import argparse
import ast
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def fail(msgs):
    for m in msgs:
        print("FAIL:", m)
    return 1 if msgs else 0


def read(path):
    return path.read_text() if path.exists() else None


def count_tests(paths):
    n = 0
    for p in paths:
        for node in ast.walk(ast.parse((ROOT / p).read_text())):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                n += 1
    return n


def check(component, n, plan, out):
    spec = plan["components"][component]
    errors = []
    if n == 1:
        inv = read(out / "inventory.md")
        if inv is None:
            return ["inventory.md missing"]
        errors += [f"inventory.md does not cover {f['name']} ({f['at']})"
                   for f in spec["functions"] if f["name"] not in inv]
    elif n == 2:
        risks = read(out / "risks.md")
        if risks is None:
            return ["risks.md missing"]
        for site in spec["http_sites"]:
            rows = [l for l in risks.splitlines() if site["at"] in l]
            if not rows:
                errors.append(f"risks.md does not list {site['at']} ({site['url']})")
            elif any("ASK" in r for r in rows):
                errors.append(f"{site['at']} is still ASK: waiting for an answer in decisions.md")
            elif not any(("CHANGE" in r) or ("KEEP" in r) for r in rows):
                errors.append(f"{site['at']} has no CHANGE/KEEP decision")
    elif n == 3:
        if read(out / "tests-report.md") is None:
            errors.append("tests-report.md missing")
        tests = sorted(p.relative_to(ROOT).as_posix()
                       for p in (ROOT / "components" / component).glob("test_*.py"))
        before = count_tests(spec["tests"])
        now = count_tests(tests)
        if now <= before:
            errors.append(f"no new tests: {now} test functions, {before} at plan time")
        run = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", ".",
                              "-p", "test_*.py", "-t", "."], cwd=ROOT,
                             capture_output=True, text=True)
        if run.returncode != 0:
            errors.append("tests fail:\n" + run.stderr[-1500:])
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("component")
    ap.add_argument("--pass", dest="n", type=int)
    args = ap.parse_args()
    plan = json.loads((ROOT / "codebase-analysis" / "plan.json").read_text())
    if args.component not in plan["components"]:
        return fail([f"unknown component {args.component}"])
    out = ROOT / "codebase-analysis" / "components" / args.component
    errors = []
    if args.n:
        passes = [args.n]
    else:
        raw = read(out / "status.json")
        try:
            status = json.loads(raw) if raw else {}
        except json.JSONDecodeError as e:
            return fail([f"status.json is not valid JSON: {e}"])
        if not isinstance(status, dict):
            return fail(["status.json must be a JSON object"])
        passes = status.get("passes_done", [])
        if not passes:
            return fail(["status.json missing or no passes_done"])
        open_q = status.get("open_questions", 0)
        if not isinstance(open_q, int) or isinstance(open_q, bool) or open_q < 0:
            errors.append(f"status.json open_questions must be a non-negative integer, got {open_q!r}")
        elif open_q > 0:
            errors.append(f"blocked: {open_q} open question(s) waiting for the team (see the PR description)")
    for n in passes:
        errs = check(args.component, n, plan, out)
        print(f"{args.component} pass {n}: {'PASS' if not errs else 'FAIL'}")
        errors += errs
    return fail(errors)


if __name__ == "__main__":
    sys.exit(main())
