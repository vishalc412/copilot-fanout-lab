#!/usr/bin/env python3
"""Coverage gate for a codebase analysis: is every file, symbol and route documented?

Builds a fresh inventory of the repository (the same scan as inventory.py), reads
every Markdown file in the analysis folder, and reports:

  - source files with no page declaring them (`Source file:` line)
  - classes and functions never named on their file's page
  - functions with no full card (heading, Steps, citation; at deep also pseudo-code and every branch cited)
  - routes with no endpoint card (a heading naming the path, Request and Response parts)
  - build, deployment, configuration and data files never mentioned
  - citations (`path:line` in backticks) whose file or lines do not exist
  - opaque claim numbers such as C-154 in reader-facing text
  - template placeholders left behind
  - cards whose `<!-- code: ... -->` stamp no longer matches the code (the code changed since)
  - `<!-- recheck ... -->` markers delta.py left on citations it could not move
  - stamped cards for functions the file no longer has
  - drift between the stored inventory and the repository now

Anything listed in `<analysis>/ledger/not-documented.md` with a reason counts as
accounted for. Read-only on the repository; writes one report inside the analysis
folder. Exit 0 when the gate for the chosen depth passes, 1 when it does not, 2 on
a usage error.

  python3 -I <skill>/scripts/coverage.py --repo . --analysis codebase-analysis --depth deep
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # never leave __pycache__ inside the installed skill
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventory  # noqa: E402  (sibling script, isolated mode needs the explicit path)

DEPTHS = {
    # card_lines: functions at least this long need a full card (1 = every function)
    # symbols / cards / files / routes / citations: shares that must be met
    # branches: share of if/elif/loop/except/raise lines cited inside their function's card
    # pseudo: every full card carries a pseudo-code block
    # sequence: every endpoint card carries a sequence diagram
    # callgraph: share of same-file call edges drawn in the module page's call graph
    # frontmatter: every lld page starts with knowledge-graph front matter
    "deep": {"card_lines": 1, "symbols": 1.00, "cards": 1.00, "files": 1.00, "routes": 1.00, "citations": 0.98,
             "branches": 0.95, "pseudo": True, "sequence": True, "callgraph": 0.95, "frontmatter": 1.00},
    "standard": {"card_lines": 40, "symbols": 0.95, "cards": 0.90, "files": 1.00, "routes": 1.00, "citations": 0.95,
                 "branches": 0.0, "pseudo": False, "sequence": False, "callgraph": 0.0, "frontmatter": 1.00},
    "survey": {"card_lines": None, "symbols": 0.0, "cards": 0.0, "files": 1.00, "routes": 0.80, "citations": 0.90,
               "branches": 0.0, "pseudo": False, "sequence": False, "callgraph": 0.0, "frontmatter": 0.0},
}

REQUIRED = {
    "deep": ["README.md", "00-mind-map.md", "hld/01-system-context.md", "hld/02-architecture.md",
             "hld/03-integrations.md", "hld/04-data-architecture.md", "hld/05-key-flows.md",
             "hld/06-cross-cutting.md", "lld/data-dictionary.md", "reference/glossary.md",
             "reference/configuration.md", "reference/risks-and-surprises.md",
             "reference/open-questions.md", "ledger/coverage-ledger.md", "progress.md"],
}
REQUIRED["standard"] = REQUIRED["deep"]
REQUIRED["survey"] = ["README.md", "00-mind-map.md", "hld/01-system-context.md", "hld/02-architecture.md",
                      "hld/03-integrations.md", "reference/open-questions.md", "ledger/coverage-ledger.md"]

SKIP_DOCS = {"ledger/next.md", "ledger/symbol-checklist.md", "ledger/coverage-report.md", "ledger/not-documented.md",
             "verification-report.md", "verification-coverage.md", "knowledge/README.md",
             "ledger/delta.md", "ledger/track.md", "delta-log.md", "CHANGELOG.md"}

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
SOURCE_DECL = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?Source files?(?:\*\*)?\s*:\s*(.+)$", re.I | re.M)
BACKTICK = re.compile(r"`([^`\n]+)`")
CITATION = re.compile(r"`([A-Za-z0-9_@+~./\\-]+\.[A-Za-z0-9_]+|[A-Za-z0-9_@+~./\\-]*(?:Dockerfile|Jenkinsfile|Makefile|Procfile)):(\d+)(?:\s*-\s*(\d+))?`")
OPAQUE = re.compile(r"\bC-\d{3,4}\b")
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|<(?!br\b|br/)[a-z][a-z /-]{2,30}>")


FRONT_MATTER = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)
MERMAID_BLOCK = re.compile(r"```mermaid[ \t]*\n(.*?)```", re.S)
CITE_IN_LINE = re.compile(r"`(?:[^`\n]*/)?([^`/\n]+):(\d+)(?:\s*-\s*(\d+))?`")
STAMP = re.compile(r"<!--\s*code:\s*([0-9a-f]{12})\s*-->")        # the code a card was written from
RECHECK = re.compile(r"<!--\s*recheck\b[^>]*-->")                  # set by delta.py on a citation it could not move


def front_matter(text: str) -> dict:
    """Minimal parser: `key: value` and `key: [a, b]` lines between the first two --- lines."""
    match = FRONT_MATTER.match(text)
    data = {}
    if not match:
        return data
    for line in match.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key.strip()] = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        else:
            data[key.strip()] = value.strip("'\"")
    return data


def load_docs(analysis_abs: str):
    docs = {}
    for root, dirs, names in os.walk(analysis_abs, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not os.path.islink(os.path.join(root, d)))
        for name in sorted(names):
            if not name.endswith(".md"):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, analysis_abs).replace(os.sep, "/")
            if rel in SKIP_DOCS or rel.startswith("impact/") or os.path.islink(full):
                continue
            with open(full, encoding="utf-8", errors="replace") as handle:
                docs[rel] = handle.read()
    return docs


def sections(text: str):
    """Yield (heading, level, body, first_line) for every heading in the text."""
    lines = text.splitlines()
    marks = []
    in_fence = False
    for index, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        match = None if in_fence else HEADING.match(line)
        if match:
            marks.append((index, len(match.group(1)), match.group(2)))
    for position, (index, level, title) in enumerate(marks):
        end = len(lines)
        for later_index, later_level, _ in marks[position + 1:]:
            if later_level <= level:
                end = later_index
                break
        yield title, level, "\n".join(lines[index + 1:end]), index + 1


def name_pattern(name: str):
    return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])")


def card_title_pattern(symbol: dict, symbols) -> re.Pattern:
    """A method's card is found by `Class.method`; a bare name only when no other symbol of the file shares it."""
    same_name = [x for x in symbols if x["name"] == symbol["name"] and x["kind"] != "imports"]
    if "." in symbol["qualname"] and len(same_name) > 1:
        return name_pattern(symbol["qualname"])
    return re.compile(name_pattern(symbol["qualname"]).pattern + "|" + name_pattern(symbol["name"]).pattern)


def edge_drawn(lines, node_names, caller: str, callee: str) -> bool:
    """An arrow line whose two ends are (or are labelled with) caller and callee, in that order."""
    def ids_for(name):
        pattern = name_pattern(name)
        return {i for i, texts in node_names.items() if any(pattern.search(t) for t in texts)} | \
               ({name} if re.match(r"^[A-Za-z][A-Za-z0-9]*$", name) else set())
    callers, callees = ids_for(caller), ids_for(callee)
    for line in lines:
        match = re.match(r"\s*([A-Za-z][A-Za-z0-9]*)\b.*?(-->|-\.->|==>)(?:\|[^|]*\|)?\s*([A-Za-z][A-Za-z0-9]*)", line)
        if match and match.group(1) in callers and match.group(3) in callees:
            return True
    return False


def pseudo_ok(body: str, size: int) -> bool:
    """A Pseudo-code label followed by a fenced block; at least 3 lines for functions of 10 lines or more."""
    match = re.search(r"pseudo-?code[^\n]*\n+\s*```[^\n]*\n(.*?)```", body, re.I | re.S)
    if not match:
        return False
    lines = [l for l in match.group(1).splitlines() if l.strip()]
    return len(lines) >= (3 if size >= 10 else 1)


def branch_table_rows(body: str):
    """Table rows after a 'Branches' label, up to the next blank line that ends the table."""
    rows, inside = [], False
    for line in body.splitlines():
        if re.search(r"branch(es)?\b", line, re.I) and not line.lstrip().startswith("|"):
            inside = True
            continue
        if inside and line.lstrip().startswith("|"):
            rows.append(line)
        elif inside and rows and not line.strip():
            inside = False
    return rows


def find_card(page_sections, symbol: dict, symbols, base: str):
    """Body of the card section for this symbol, or None. Qualified-name headings win."""
    exact = name_pattern(symbol["qualname"])
    loose = card_title_pattern(symbol, symbols)
    citation = re.compile(re.escape(base) + r":\d")
    for pattern in (exact, loose):
        for title, _level, body, _line in page_sections:
            if pattern.search(title) and re.search(r"\bsteps?\b", body, re.I) and citation.search(body):
                return body
    return None


def mentions(text: str, name: str) -> bool:
    pattern = name_pattern(name)
    for token in BACKTICK.findall(text):
        if pattern.search(token):
            return True
    for line in text.splitlines():
        if line.lstrip().startswith("#") and pattern.search(line):
            return True
    return False


def strip_dot(path: str) -> str:
    """Forward slashes; remove a leading `./` only; `.github/...` and `.env.example` keep their dot."""
    path = path.replace("\\", "/")
    while path.startswith("./"):
        path = path[2:]
    return path


TEST_FILE = re.compile(r"(^|/)(tests?|spec|specs|__tests__)/|(^|/)(test_[^/]+|[^/]+_test\.\w+|[^/]+\.(test|spec)\.\w+|[^/]+Tests?\.\w+)$")


def is_test_file(path: str) -> bool:
    return TEST_FILE.search(path) is not None


def norm_route(path: str) -> str:
    path = path.strip()
    return path.rstrip("/") or "/"


def load_skips(analysis_abs: str):
    """Rows of ledger/not-documented.md: | `path` | `symbol or route or *` | reason |"""
    skips = set()
    full = os.path.join(analysis_abs, "ledger", "not-documented.md")
    if not os.path.isfile(full):
        return skips
    with open(full, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3 or set(cells[0]) <= set("-: "):
                continue
            path = cells[0].strip("`")
            what = cells[1].strip("`") or "*"
            if cells[2] and path.lower() not in ("file", "path"):
                skips.add((path, what))
    return skips


def skipped(skips, path: str, what: str) -> bool:
    return (path, what) in skips or (path, "*") in skips


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--analysis", default="codebase-analysis")
    parser.add_argument("--depth", choices=sorted(DEPTHS), default="deep")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--report", default=None,
                        help="report file inside the analysis folder (default ledger/coverage-report.md)")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    args.analysis = args.analysis.replace("\\", "/")
    if os.path.isabs(args.analysis) or ".." in args.analysis.split("/") or args.analysis.strip("/") in ("", "."):
        inventory.fail("--analysis must be a folder inside the repository, given relative to it")
    analysis_abs = os.path.join(repo, args.analysis)
    if not os.path.isdir(analysis_abs):
        inventory.fail("analysis folder not found: " + args.analysis)
    report_rel = args.report or "ledger/coverage-report.md"
    if os.path.isabs(report_rel) or ".." in report_rel.split("/"):
        inventory.fail("--report must be a path inside the analysis folder")
    report_path = inventory.safe_target(repo, os.path.join(analysis_abs, report_rel))

    rules = DEPTHS[args.depth]
    files, _excluded = inventory.scan(repo, args.analysis, [e.strip("/") for e in args.exclude])
    all_files = files if not args.exclude else inventory.scan(repo, args.analysis, [])[0]
    by_path = {f["path"]: f for f in all_files}  # citations may point into excluded areas
    basenames = {}
    for f in all_files:
        basenames.setdefault(os.path.basename(f["path"]), []).append(f["path"])
    docs = load_docs(analysis_abs)
    all_text = "\n".join(docs.values())
    skips = load_skips(analysis_abs)

    # Pages declaring source files.
    page_for = {}
    for doc, text in docs.items():
        declared = front_matter(text).get("source", [])
        for path in ([declared] if isinstance(declared, str) else declared):
            if path:
                page_for.setdefault(strip_dot(path.strip("`").split(":")[0]), []).append(doc)
        for decl in SOURCE_DECL.findall(text):
            for token in BACKTICK.findall(decl):
                path = strip_dot(token.split(":")[0].strip())
                page_for.setdefault(path, []).append(doc)

    source = [f for f in files if f["kind"] == "source" and not f["binary"] and f["lines"] > 0
              and f["lang"] not in ("css", "html")]
    gaps = {k: [] for k in ("files", "symbols", "cards", "routes", "mentions", "citations",
                            "short", "opaque", "placeholders", "required", "mindmap", "stale", "recheck", "orphan")}
    hash_cache = {}

    def stamp_of(path, start, end):
        if path not in hash_cache:
            text = inventory.read_text(os.path.join(repo, path))
            hash_cache[path] = inventory.line_hashes(text) if text is not None else []
        return inventory.stamp(hash_cache[path], start, end)
    counts = {"files": [0, 0], "symbols": [0, 0], "cards": [0, 0], "routes": [0, 0], "citations": [0, 0],
              "branches": [0, 0], "callgraph": [0, 0], "frontmatter": [0, 0]}
    for key in ("branches", "callgraph", "pseudo", "sequence", "frontmatter"):
        gaps[key] = []

    for f in source:
        counts["files"][1] += 1
        pages = page_for.get(f["path"], [])
        if pages or skipped(skips, f["path"], "*"):
            counts["files"][0] += 1
        else:
            gaps["files"].append("`%s` (%d lines, %d symbols)" % (f["path"], f["lines"], len(f["symbols"])))
        page_text = "\n".join(docs[p] for p in pages)
        page_sections = []
        for p in pages:
            page_sections.extend(sections(docs[p]))
        if rules["card_lines"] is None:
            continue
        test_file = is_test_file(f["path"])
        symbols = [x for x in f["symbols"] if x["kind"] != "imports"]
        for s in symbols:
            counts["symbols"][1] += 1
            if skipped(skips, f["path"], s["qualname"]) or skipped(skips, f["path"], s["name"]):
                counts["symbols"][0] += 1
                continue
            if page_text and mentions(page_text, s["name"]):
                counts["symbols"][0] += 1
            else:
                gaps["symbols"].append("`%s` `%s` (%s, lines %d-%d)" % (f["path"], s["qualname"], s["kind"], s["start"], s["end"]))
                continue
            if s["kind"] in ("class", "table", "view", "paragraph") or s["size"] < rules["card_lines"] or test_file:
                continue  # test functions need a row naming them and what they check, not a full card
            counts["cards"][1] += 1
            base = os.path.basename(f["path"])
            card_body = find_card(page_sections, s, symbols, base)
            branch_lines = sorted({b["line"] for b in s.get("branches", [])})
            if rules["branches"]:
                counts["branches"][1] += len(branch_lines)
            if card_body is None:
                gaps["cards"].append("`%s` `%s` (%d lines): needs a heading naming it, a Steps part and a `%s:<lines>` citation"
                                     % (f["path"], s["qualname"], s["size"], base))
                continue
            written_from = STAMP.search(card_body)
            if written_from and written_from.group(1) != stamp_of(f["path"], s["start"], s["end"]):
                gaps["stale"].append("`%s` `%s` (lines %d-%d): rewrite the card from the code and stamp it `<!-- code: %s -->`"
                                     % (f["path"], s["qualname"], s["start"], s["end"], stamp_of(f["path"], s["start"], s["end"])))
            missing = []
            if rules["pseudo"] and not pseudo_ok(card_body, s["size"]):
                missing.append("pseudo-code block")
                gaps["pseudo"].append("`%s` `%s`" % (f["path"], s["qualname"]))
            if rules["branches"] and branch_lines:
                ranges = []
                for line in branch_table_rows(card_body):
                    for cited_base, start, end in CITE_IN_LINE.findall(line):
                        if cited_base == base:
                            start, end = int(start), int(end or start)
                            if end - start <= 3:
                                ranges.append((start, end))
                uncited = [n for n in branch_lines if not any(a <= n <= b for a, b in ranges)]
                counts["branches"][0] += len(branch_lines) - len(uncited)
                if uncited:
                    gaps["branches"].append("`%s` `%s`: branch lines %s not cited in its card (one row each in the Branches and errors table, cited to its line or a range of 3 lines or fewer)"
                                            % (f["path"], s["qualname"], ", ".join(str(n) for n in uncited)))
            if missing:
                continue
            counts["cards"][0] += 1
        names = {x["qualname"] for x in symbols} | {x["name"] for x in symbols}
        for title, _level, body, _line in page_sections:
            own = re.split(r"\n#{1,6}\s", "\n" + body)[0]  # the card's own text, not the cards under it
            if not STAMP.search(own) or not re.search(re.escape(os.path.basename(f["path"])) + r":\d", own):
                continue
            tokens = [t.split("(")[0].strip() for t in BACKTICK.findall(title)]
            tokens = [t for t in tokens if t and not t.startswith("/")]
            if tokens and not any(t in names or t.split(".")[-1] in names for t in tokens):
                gaps["orphan"].append("`%s`: card `%s` describes code the file no longer has" % (f["path"], title.strip()))
        if rules["callgraph"] and pages:
            local = {x["name"] for x in symbols if x["kind"] not in ("class", "table", "view", "paragraph")}
            edges = set()
            for x in symbols:
                for call in x.get("calls", []):
                    target = call["name"].split(".")[-1]
                    if target in local and target != x["name"]:
                        edges.add((x["name"], target))
            graph_lines = [line for p in pages for block in MERMAID_BLOCK.findall(docs[p])
                           if re.match(r"\s*(flowchart|graph)\b", block) for line in block.splitlines()]
            node_names = {}
            for line in graph_lines:
                for node_id, text in re.findall(r"([A-Za-z][A-Za-z0-9]*)\s*[\[({]+\"?([^\]\)}\"]*)", line):
                    node_names.setdefault(node_id, set()).add(text)
            for caller, callee in sorted(edges):
                counts["callgraph"][1] += 1
                if edge_drawn(graph_lines, node_names, caller, callee):
                    counts["callgraph"][0] += 1
                else:
                    gaps["callgraph"].append("`%s`: `%s` -> `%s` not in the page's call-graph flowchart" % (f["path"], caller, callee))

    if rules["frontmatter"]:
        for doc, text in sorted(docs.items()):
            if not doc.startswith("lld/"):
                continue
            counts["frontmatter"][1] += 1
            meta = front_matter(text)
            if meta.get("id") and meta.get("kind"):
                counts["frontmatter"][0] += 1
            else:
                gaps["frontmatter"].append("`%s`: no front matter with `id` and `kind`" % doc)

    all_sections = []
    for doc, text in docs.items():
        for title, level, body, line in sections(text):
            all_sections.append((doc, title, body, level))
    for f in files:
        for r in f["routes"]:
            counts["routes"][1] += 1
            path = norm_route(r["path"])
            label = "%s %s" % ("/".join(r["methods"]), r["path"])
            if skipped(skips, f["path"], r["path"]):
                counts["routes"][0] += 1
                continue
            if r["methods"] == ["UI"]:
                if path in all_text:
                    counts["routes"][0] += 1
                else:
                    gaps["routes"].append("`%s` UI route `%s` (line %d) never mentioned" % (f["path"], r["path"], r["line"]))
                continue
            card = False
            route_pattern = re.compile(r"(?<![\w/{<:-])" + re.escape(path) + r"/?(?![\w/{<-])")
            wanted = [m for m in r["methods"] if m not in ("ANY",)]
            for _doc, title, body, level in all_sections:
                if level > 1 and route_pattern.search(title) and all(re.search(r"\b%s\b" % m, title) for m in wanted):
                    if re.search(r"\brequest\b", body, re.I) and re.search(r"\bresponses?\b", body, re.I):
                        card = True
                        written_from = STAMP.search(body)
                        handler = [x for x in f["symbols"] if x["qualname"] == r["handler"]]
                        span = (handler[0]["start"], handler[0]["end"]) if handler else (r["line"], r["line"])
                        if written_from and written_from.group(1) != stamp_of(f["path"], *span):
                            gaps["stale"].append("`%s` endpoint `%s`: rewrite the card from the code and stamp it `<!-- code: %s -->`"
                                                 % (f["path"], label, stamp_of(f["path"], *span)))
                        if rules["sequence"] and "sequenceDiagram" not in body:
                            card = False
                            gaps["sequence"].append("`%s` `%s`: endpoint card has no sequence diagram" % (f["path"], label))
                        break
            if card:
                counts["routes"][0] += 1
            else:
                where = "mentioned but no endpoint card" if path in all_text else "never mentioned"
                gaps["routes"].append("`%s` `%s` -> `%s` (line %d): %s" % (f["path"], label, r["handler"], r["line"], where))

    for f in files:
        if f["kind"] in ("build", "deploy", "config", "data") or f["lang"] in ("css", "html"):
            if skipped(skips, f["path"], "*"):
                continue
            if f["path"] not in all_text and not ("`%s`" % os.path.basename(f["path"]) in all_text
                                                   and len(basenames[os.path.basename(f["path"])]) == 1):
                gaps["mentions"].append("`%s` (%s)" % (f["path"], f["kind"]))

    citation_rows = []
    for doc in sorted(docs):
        text = docs[doc]
        fenced, in_fence = set(), False
        for number, raw in enumerate(text.splitlines(), 1):
            if raw.strip().startswith("```"):
                in_fence = not in_fence
                fenced.add(number)
            elif in_fence:
                fenced.add(number)
        for line_no, line in enumerate(text.splitlines(), 1):
            label = "inferred" if "(inferred" in line.lower() else ("assumed" if "(assumed" in line.lower() else "")
            for match in CITATION.finditer(line):
                cited = strip_dot(match.group(1).replace("\\", "/"))
                start = int(match.group(2))
                end = int(match.group(3) or start)
                counts["citations"][1] += 1
                status = "ok"
                target = by_path.get(cited)
                if target is None and len(basenames.get(os.path.basename(cited), [])) == 1 and "/" not in cited:
                    target = by_path[basenames[os.path.basename(cited)][0]]
                    status = "short path"
                if target is None:
                    status = "no such file"
                elif target["binary"]:
                    status = "binary file"
                elif start < 1 or end < start or end > max(target["lines"], 1):
                    status = "lines out of range (file has %d)" % target["lines"]
                if status == "short path" and doc in page_for.get(target["path"], []):
                    status = "ok"
                if status in ("ok", "short path"):
                    counts["citations"][0] += 1
                if status == "short path":
                    gaps["short"].append("%s:%d `%s:%s`" % (doc, line_no, cited, match.group(2)))
                elif status != "ok":
                    gaps["citations"].append("%s:%d `%s:%d-%d`: %s" % (doc, line_no, cited, start, end, status))
                citation_rows.append((len(citation_rows) + 1, doc, line_no, cited, start, end, status, label))
            for match in RECHECK.finditer(line):
                gaps["recheck"].append("%s:%d `%s`" % (doc, line_no, match.group(0)))
            for match in OPAQUE.finditer(line):
                gaps["opaque"].append("%s:%d `%s`" % (doc, line_no, match.group(0)))
            if line_no not in fenced:
                for match in PLACEHOLDER.finditer(re.sub(r"`[^`]*`", "", line)):
                    gaps["placeholders"].append("%s:%d `%s`" % (doc, line_no, match.group(0)))

    for required in REQUIRED[args.depth]:
        if required not in docs and not os.path.isfile(os.path.join(analysis_abs, required)):
            gaps["required"].append("`%s`" % required)
    mind = docs.get("00-mind-map.md", "")
    if "```mermaid" not in mind or "mindmap" not in mind:
        gaps["mindmap"].append("`00-mind-map.md` has no Mermaid mindmap")

    drift = []
    stored = os.path.join(analysis_abs, "ledger", "inventory.json")
    if os.path.isfile(stored):
        try:
            with open(stored, encoding="utf-8") as handle:
                old = {f["path"]: f["lines"] for f in json.load(handle).get("files", [])}
            now = {f["path"]: f["lines"] for f in files}
            drift += ["added since inventory: `%s`" % p for p in sorted(set(now) - set(old))]
            drift += ["removed since inventory: `%s`" % p for p in sorted(set(old) - set(now))]
            drift += ["changed length: `%s` %d -> %d lines" % (p, old[p], now[p])
                      for p in sorted(set(now) & set(old)) if old[p] != now[p]]
        except (OSError, ValueError, KeyError):
            drift.append("stored inventory.json could not be read")
    else:
        drift.append("no stored ledger/inventory.json: run inventory.py first")

    def share(key):
        done, total = counts[key]
        return 1.0 if total == 0 else done / total

    checks = [
        ("Source files with a page", "files"),
        ("Symbols accounted for", "symbols"),
        ("Functions with a full card (>= %s lines)" % rules["card_lines"], "cards"),
        ("Routes with an endpoint card", "routes"),
        ("Citations that resolve", "citations"),
        ("Branch lines cited in their card", "branches"),
        ("Same-file calls drawn in call graphs", "callgraph"),
        ("LLD pages with knowledge-graph front matter", "frontmatter"),
    ]
    failures = []
    for title, key in checks:
        if share(key) + 1e-9 < rules[key]:
            failures.append("%s: %.1f%% (needs %.0f%%)" % (title, share(key) * 100, rules[key] * 100))
    for key, why in (("required", "required files missing"), ("mindmap", "mind map missing"),
                     ("mentions", "build, deployment, configuration or data files never mentioned"),
                     ("opaque", "opaque claim numbers in reader-facing text"),
                     ("placeholders", "template placeholders left"),
                     ("stale", "cards written from code that has changed since"),
                     ("recheck", "citations awaiting a recheck after a code change"),
                     ("orphan", "cards for code that no longer exists")):
        if gaps[key] and not (key == "mentions" and args.depth == "survey"):
            failures.append("%d %s" % (len(gaps[key]), why))
    passed = not failures

    out = ["# Coverage report", "",
           "Generated by `coverage.py` on %s, depth `%s`. Result: **%s**." % (
               datetime.datetime.now().isoformat(timespec="seconds"), args.depth, "PASS" if passed else "GAPS"), "",
           "| Measure | Done | Total | Share | Needed |", "| --- | --- | --- | --- | --- |"]
    for title, key in checks:
        done, total = counts[key]
        out.append("| %s | %d | %d | %.1f%% | %.0f%% |" % (title, done, total, share(key) * 100, rules[key] * 100))
    out += ["", "Files in scope: %d. Source files: %d. Analysis pages read: %d." % (len(files), len(source), len(docs)), ""]
    if failures:
        out += ["## Why the gate does not pass", ""] + ["- " + f for f in failures] + [""]
    sections_out = [
        ("Source files with no page", "files", "Write `lld/<component>/<module>.md` with a `Source file:` line, or list the file in `ledger/not-documented.md` with a reason."),
        ("Symbols never named on their file's page", "symbols", "Add a function card or a row in the page's helper table."),
        ("Functions without a full card", "cards", "Give each a heading with its name, a Steps part and a citation."),
        ("Cards without pseudo-code", "pseudo", "Add a **Pseudo-code** part with a fenced block."),
        ("Branches not cited", "branches", "Add a row per branch to the card's Branches and errors table, citing its line."),
        ("Endpoint cards without a sequence diagram", "sequence", "Add a Mermaid sequenceDiagram to the card."),
        ("Call-graph edges missing", "callgraph", "Draw the module's call graph: a flowchart with one edge per call."),
        ("LLD pages without front matter", "frontmatter", "Start the page with the front matter block from output-templates.md."),
        ("Routes without an endpoint card", "routes", "Add an endpoint card in `lld/api/` with Request and Response parts."),
        ("Build, deployment, configuration and data files never mentioned", "mentions", "Describe each where it belongs (architecture, configuration, data dictionary)."),
        ("Citations that do not resolve", "citations", "Open the file and correct the path or the lines."),
        ("Citations with a file name outside that file's own page", "short", "Write the path from the repository root."),
        ("Opaque claim numbers", "opaque", "Replace with a `path:line` citation and plain words."),
        ("Placeholders", "placeholders", "Fill in or remove."),
        ("Cards written from code that has changed since", "stale", "Re-read the lines, rewrite the card, and replace its stamp with the one given."),
        ("Cards for code that no longer exists", "orphan", "Delete the card, its call-graph edges and every row that names it."),
        ("Citations awaiting a recheck after a code change", "recheck", "Open the cited code, correct the citation and the sentence it supports, then delete the marker."),
        ("Required files missing", "required", "Write them from the templates."),
        ("Mind map", "mindmap", "Write `00-mind-map.md` with a Mermaid `mindmap`."),
    ]
    for title, key, action in sections_out:
        if not gaps[key]:
            continue
        out += ["## %s (%d)" % (title, len(gaps[key])), "", action, ""] + ["- " + g for g in gaps[key]] + [""]
    notes = ["`%s`: %s" % (f["path"], f["note"]) for f in files if f.get("note")]
    if notes:
        out += ["## Files the scanner could not parse (%d)" % len(notes), "",
                "Their functions were found by pattern; check each page against the file by hand.", ""] + \
               ["- " + n for n in notes] + [""]
    out += ["## Drift since the stored inventory", ""] + (["- " + d for d in drift] or ["None."]) + [""]
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out) + "\n")

    tsv_path = inventory.safe_target(repo, os.path.join(analysis_abs, "ledger", "citations.tsv"))
    os.makedirs(os.path.dirname(tsv_path), exist_ok=True)
    with open(tsv_path, "w", encoding="utf-8") as handle:
        handle.write("index\tdoc\tdoc_line\tcited_path\tstart\tend\tstatus\tlabel\n")
        for row in citation_rows:
            handle.write("\t".join(str(c) for c in row) + "\n")

    for title, key in checks:
        done, total = counts[key]
        print("%-52s %5d / %-5d %5.1f%%" % (title, done, total, share(key) * 100))
    print("result: %s (depth %s)" % ("PASS" if passed else "GAPS", args.depth))
    for f in failures:
        print("  - " + f)
    print("wrote " + os.path.relpath(report_path, repo))
    print("wrote " + os.path.relpath(tsv_path, repo))
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
