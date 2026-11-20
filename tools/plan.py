"""Step 0 of the fan-out: deterministic inventory, no LLM.

Run it once per analysis, before fan-out: test_count is the baseline the
gate's pass 3 compares against. Walks components/<name>/ and writes codebase-analysis/plan.json with, per
component: source files, functions (file:line), test files and every
http:// literal (file:line). The gate checks the analysis against this file.
"""
import ast
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gate import count_tests  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTTP = re.compile(r"""["'](http://[^"']+)["']""")


def scan(component_dir):
    sources, tests, functions, http_sites = [], [], [], []
    for path in sorted(component_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        rel = path.relative_to(ROOT).as_posix()
        (tests if path.name.startswith("test_") else sources).append(rel)
        text = path.read_text()
        if not path.name.startswith("test_"):
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.FunctionDef):
                    functions.append({"name": node.name, "at": f"{rel}:{node.lineno}"})
            for lineno, line in enumerate(text.splitlines(), 1):
                for match in HTTP.finditer(line):
                    http_sites.append({"url": match.group(1), "at": f"{rel}:{lineno}"})
    test_count = count_tests(tests)  # same rule the gate uses
    return {"sources": sources, "tests": tests, "test_count": test_count,
            "functions": functions, "http_sites": http_sites}


def main():
    components = {}
    for d in sorted((ROOT / "components").iterdir()):
        if d.is_dir() and not d.name.startswith("_"):
            components[d.name] = scan(d)
    plan = {
        "version": 1,
        "passes": {
            "1": "inventory: every function, what it does, who calls it",
            "2": "risks: classify every http:// site as CHANGE or KEEP; ask when unsure",
            "3": "tests: add unit tests for untested functions, run them, report",
        },
        "components": components,
    }
    out = ROOT / "codebase-analysis" / "plan.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(plan, indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)}: {len(components)} components")


if __name__ == "__main__":
    main()
