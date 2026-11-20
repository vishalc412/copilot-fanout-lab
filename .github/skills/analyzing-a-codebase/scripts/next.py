#!/usr/bin/env python3
"""The work loop: print the one next job of the analysis, from the code and the pages on disk.

Each run scans the repository and the analysis folder fresh, works out which
packet (a source file, or a slice of a large one) is not yet documented to the
chosen depth, and prints exactly what to do next: the file and lines to read,
the page to write, every function to card with its branch lines and calls, and
every route declared there. When every packet is done it names the next pass,
and finally runs the gate. Nothing is remembered between runs except the
session counter, so the answer is always what the files show.

  python3 -I <skill>/scripts/next.py --repo . --analysis codebase-analysis [--depth deep] [--new-session]

Prints one of:
  NEXT DELTA ...       the code changed since the analysis matched it: do the job, then run next.py again
  NEXT PACKET ...      do it, then run next.py again
  NEXT PASS ...        do it, then run next.py again
  NEW CHAT             stop; tell the user to continue in a new chat
  DONE                 the coverage gate passes; finish as SKILL.md says

Writes `<analysis>/ledger/next.md` (the same text) and `<analysis>/ledger/session.json`.
Read-only on the repository. Standard library only; never imports or runs repository code.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True  # never leave __pycache__ inside the installed skill
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventory  # noqa: E402
import coverage  # noqa: E402
import delta  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PACKET_LINES = 400
PACKET_FUNCTIONS = 25
NOT_CARDED = ("class", "table", "view", "paragraph", "imports")


def norm(path: str) -> str:
    return coverage.strip_dot(path.replace("\\", "/").strip().strip("`"))


def pages_by_source(docs):
    page_for = {}
    for doc, text in docs.items():
        declared = coverage.front_matter(text).get("source", [])
        for path in ([declared] if isinstance(declared, str) else declared):
            if path:
                page_for.setdefault(norm(path.split(":")[0]), []).append(doc)
        for decl in coverage.SOURCE_DECL.findall(text):
            for token in coverage.BACKTICK.findall(decl):
                page_for.setdefault(norm(token.split(":")[0]), []).append(doc)
    return page_for


def packets_for(f):
    """Split one file into packets at symbol boundaries: about 400 lines or 25 functions each.
    A class longer than one packet is split between its methods."""
    units = []
    for top in sorted((x for x in f["symbols"] if x["kind"] != "imports" and "." not in x["qualname"]), key=lambda x: x["start"]):
        members = [m for m in f["symbols"] if m["qualname"].startswith(top["qualname"] + ".")]
        if top["size"] > PACKET_LINES and members:
            units += [(m["start"], m["end"], 1) for m in sorted(members, key=lambda m: m["start"]) if m["qualname"].count(".") == 1]
        else:
            units.append((top["start"], top["end"], 1 + len(members)))
    if not units:
        return [(1, max(f["lines"], 1))]
    starts, first, count = [], None, 0
    for a, b, n in units:
        if first is not None and (b - first + 1 > PACKET_LINES or count + n > PACKET_FUNCTIONS):
            starts.append(first)
            first, count = None, 0
        if first is None:
            first = a
        count += n
    starts.append(first)
    starts[0] = 1
    return [(starts[i], (starts[i + 1] - 1) if i + 1 < len(starts) else max(f["lines"], starts[i])) for i in range(len(starts))]


def component_of(path: str) -> str:
    parts = path.split("/")
    return parts[0] if len(parts) > 1 else "root"


def module_page(path: str, component: str) -> str:
    stem = os.path.splitext(os.path.basename(path))[0]
    return "lld/%s/%s.md" % (component, stem)


def packet_gaps(f, start, end, docs, pages, rules, skips, all_sections, stamps=None):
    """What is still missing for the symbols and routes declared in lines start..end."""
    gaps = []
    if not pages and not coverage.skipped(skips, f["path"], "*"):
        gaps.append(("page", None, "no page declares this file"))
    page_text = "\n".join(docs[p] for p in pages)
    page_sections = [sec for p in pages for sec in coverage.sections(docs[p])]
    for p in pages:
        if rules["frontmatter"] and not (coverage.front_matter(docs[p]).get("id") and coverage.front_matter(docs[p]).get("kind")):
            gaps.append(("frontmatter", None, "page %s has no front matter" % p))
    symbols = [s for s in f["symbols"] if s["kind"] != "imports"]
    test_file = coverage.is_test_file(f["path"])
    base = os.path.basename(f["path"])
    for s in symbols:
        if not (start <= s["start"] <= end):
            continue
        if coverage.skipped(skips, f["path"], s["qualname"]) or coverage.skipped(skips, f["path"], s["name"]):
            continue
        if rules["card_lines"] is None:
            continue
        if not (page_text and coverage.mentions(page_text, s["name"])):
            gaps.append(("symbol", s, "not named on the page"))
            continue
        if s["kind"] in NOT_CARDED or s["size"] < rules["card_lines"] or test_file:
            continue
        body = coverage.find_card(page_sections, s, symbols, base)
        if body is None:
            gaps.append(("card", s, "no card (heading naming it, Steps, a `%s:<lines>` citation)" % base))
            continue
        written_from = coverage.STAMP.search(body)
        if written_from and stamps is not None and written_from.group(1) != inventory.stamp(stamps, s["start"], s["end"]):
            gaps.append(("card", s, "the code changed since the card was written: rewrite it and replace its stamp"))
            continue
        if rules["pseudo"] and not coverage.pseudo_ok(body, s["size"]):
            gaps.append(("card", s, "card has no pseudo-code block"))
        lines = sorted({b["line"] for b in s.get("branches", [])})
        if rules["branches"] and lines:
            ranges = []
            for row in coverage.branch_table_rows(body):
                for cited, a, b in coverage.CITE_IN_LINE.findall(row):
                    if cited == base and int(b or a) - int(a) <= 3:
                        ranges.append((int(a), int(b or a)))
            missing = [n for n in lines if not any(a <= n <= b for a, b in ranges)]
            if missing:
                gaps.append(("card", s, "branch lines not in its Branches and errors table: %s" % ", ".join(map(str, missing))))
    for r in f["routes"]:
        if not (start <= r["line"] <= end) or r["methods"] == ["UI"] or coverage.skipped(skips, f["path"], r["path"]):
            continue
        path = coverage.norm_route(r["path"])
        pattern = re.compile(r"(?<![\w/{<:-])" + re.escape(path) + r"/?(?![\w/{<-])")
        wanted = [m for m in r["methods"] if m != "ANY"]
        ok = False
        for _doc, title, body, level in all_sections:
            if level > 1 and pattern.search(title) and all(re.search(r"\b%s\b" % m, title) for m in wanted):
                ok = re.search(r"\brequest\b", body, re.I) and re.search(r"\bresponses?\b", body, re.I) and \
                    (not rules["sequence"] or "sequenceDiagram" in body)
                break
        if not ok:
            gaps.append(("route", r, "no endpoint card in lld/api/ (heading with method and path, Request, Response%s)"
                         % (", sequence diagram" if rules["sequence"] else "")))
    return gaps


def describe_symbol(s, hashes=None):
    branches = ", ".join(str(b["line"]) for b in s.get("branches", [])) or "none"
    calls = ", ".join("`%s`" % c["name"] for c in s.get("calls", [])[:10]) or "none"
    stamp = "; stamp `<!-- code: %s -->`" % inventory.stamp(hashes, s["start"], s["end"]) if hashes else ""
    return "`%s` (%s, lines %d-%d) - branch lines to cite: %s; calls: %s%s" % (s["qualname"], s["kind"], s["start"], s["end"], branches, calls, stamp)


def file_hashes(repo, path):
    text = inventory.read_text(os.path.join(repo, path))
    return inventory.line_hashes(text) if text is not None else None


def delta_job(repo, analysis, excludes, files, depth):
    """The next job of a delta update, or None when there is none."""
    work = delta.pending_work(repo, analysis, excludes)
    if work is None:
        return None
    here = os.path.join(HERE, "delta.py")
    if work["drift"] or work["behind_pages"]:
        why = ("the code changed since the analysis last matched it" if work["drift"] else
               "%d pages count lines in another version of the code (after a merge or a page restored from Git): %s"
               % (len({d for d, _ in work["behind_pages"]}), ", ".join(sorted({d for d, _ in work["behind_pages"]})[:5])))
        return ["NEXT DELTA: " + why,
                "Run: python3 -I %s --repo . --analysis %s --depth %s --apply" % (here, analysis, depth),
                "(or tracking-codebase-changes' track.py --apply when the repository has a .git folder)",
                "It moves each citation from the version its page or card was written against, marks the rest for a recheck and records the work.",
                "Then run next.py again: it hands that work out file by file."]
    delta.record_new_pages(repo, os.path.join(repo, analysis), work["docs"], work["now"])
    by_path = {f["path"]: f for f in files}
    if work["items"]:
        path = work["items"][0]["path"]
        group = [i for i in work["items"] if i["path"] == path]
        pages = sorted(work["page_for"].get(path, set()))
        f = by_path.get(path)
        hashes = file_hashes(repo, path) if f else None
        out = ["NEXT DELTA %s (%d items open in %d files)" % (path, len(work["items"]), len({i["path"] for i in work["items"]})),
               "Pages:     %s" % (", ".join("%s/%s" % (analysis, p) for p in pages) or "none declares this file"),
               "Templates: references/output-templates.md - Function card%s" % (", lld/api/<group>.md" if any(i["kind"] in ("endpoint", "remove-route") for i in group) else ""),
               "", "To do (%d):" % len(group)]
        for item in group:
            kind = item["kind"]
            if kind == "card" and f:
                s = next(x for x in f["symbols"] if x["qualname"] == item["qualname"])
                out.append("  - %s the card %s (%s): read the lines, write every part from the code, put the stamp on its Source line"
                           % ("write" if item["why"] == "added" else "rewrite", describe_symbol(s, hashes), item["why"]))
            elif kind == "endpoint" and f:
                live = [r for r in f["routes"] if delta.route_key(r) == delta.route_key({"methods": item["methods"], "path": item["route"]})]
                handler = [x for x in f["symbols"] if live and x["qualname"] == live[0]["handler"]]
                span = (handler[0]["start"], handler[0]["end"]) if handler else ((live[0]["line"],) * 2 if live else (1, 1))
                out.append("  - endpoint %s %s -> `%s` (%s): rewrite or write its card in lld/api/, stamp `<!-- code: %s -->`"
                           % ("/".join(item["methods"]), item["route"], item.get("handler", ""), item["why"], inventory.stamp(hashes or [], *span)))
            elif kind == "remove-card":
                out.append("  - `%s` is gone from the code: delete its card, its call-graph edges and every row that names it" % item["qualname"])
            elif kind == "remove-route":
                out.append("  - endpoint %s %s is gone: delete its card and its row in lld/api/README.md" % ("/".join(item["methods"]), item["route"]))
            elif kind == "remove-file":
                out.append("  - the file is gone: delete its page (or its `Source file:` line), its rows in the component README and the indexes")
        out += ["", "Every citation with a `<!-- recheck ... -->` marker on these pages: open the code, fix the citation and its sentence, delete the marker.",
                "Then update the component README and the HLD pages that describe what changed, and run next.py again."]
        return out
    if work["markers"]:
        doc = work["markers"][0][0]
        rows = [m for m in work["markers"] if m[0] == doc]
        out = ["NEXT DELTA recheck %s/%s (%d citations waiting in %d pages)" % (analysis, doc, len(work["markers"]), len({m[0] for m in work["markers"]})), "",
               "Each line below cites code that changed. Open the code, correct the citation and the sentence it supports, then delete the marker:"]
        out += ["  - line %d: %s" % (n, text[:200]) for _d, n, text in rows[:40]]
        return out + ["", "Then run next.py again."]
    if work["knowledge"]:
        return ["NEXT DELTA: rebuild the knowledge base",
                "Run: python3 -I %s --repo . --analysis %s" % (os.path.join(HERE, "knowledge.py"), analysis),
                "Then update knowledge/AGENT-CONTEXT.md where the change touches it, and run next.py again."]
    return None


def session_state(path, new_session, done_now):
    state = {}
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as handle:
                state = json.load(handle)
        except (OSError, ValueError):
            state = {}
    if new_session or "start_done" not in state:
        state = {"start_done": done_now}
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--analysis", default="codebase-analysis")
    parser.add_argument("--depth", choices=sorted(coverage.DEPTHS), default="deep")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--priority", action="append", default=[], help="folder to do first (repeatable)")
    parser.add_argument("--new-session", action="store_true", help="start of a new chat: reset the packet budget")
    parser.add_argument("--budget", type=int, default=6, help="packets per chat before NEW CHAT (default 6)")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    analysis = norm(args.analysis)
    if os.path.isabs(args.analysis) or ".." in analysis.split("/") or analysis in ("", "."):
        inventory.fail("--analysis must be a folder inside the repository, given relative to it")
    analysis_abs = os.path.join(repo, analysis)
    if not os.path.isdir(analysis_abs):
        os.makedirs(inventory.safe_target(repo, analysis_abs), exist_ok=True)
    rules = coverage.DEPTHS[args.depth]
    excludes = [norm(e).strip("/") for e in args.exclude]
    files, _excluded = inventory.scan(repo, analysis, excludes)
    docs = coverage.load_docs(analysis_abs)
    page_for = pages_by_source(docs)
    skips = coverage.load_skips(analysis_abs)
    all_sections = [(doc, t, b, lvl) for doc, text in docs.items() for t, lvl, b, _ in coverage.sections(text)]

    out = []
    if not os.path.isfile(os.path.join(analysis_abs, "ledger", "inventory.json")):
        out = ["NEXT PASS 1: inventory",
               "Run: python3 -I %s --repo . --analysis %s%s" % (os.path.join(HERE, "inventory.py"), analysis, "".join(" --exclude " + e for e in excludes)),
               "Then write ledger/coverage-ledger.md (references/passes.md, Pass 1), then run next.py again."]
    elif not os.path.isfile(os.path.join(analysis_abs, "progress.md")) or "## Components" not in open(os.path.join(analysis_abs, "progress.md"), encoding="utf-8", errors="replace").read():
        comps = {}
        for f in files:
            if f["kind"] == "source" and not f["binary"] and f["lines"] > 0 and f["lang"] not in ("css", "html"):
                c = comps.setdefault(component_of(f["path"]), [0, 0, 0])
                c[0] += 1
                c[1] += len(packets_for(f))
                c[2] += len(f["routes"])
        out = ["NEXT PASS 2: components and plan",
               "Write progress.md with a '## Components' section (references/passes.md, Pass 2). Suggested split by top folder:"]
        out += ["  - %s: %d source files, %d packets, %d routes" % (c, v[0], v[1], v[2]) for c, v in sorted(comps.items(), key=lambda x: -x[1][1])]
        out += ["Total packets: %d. Split a large folder into the areas its routes, packages and services show." % sum(v[1] for v in comps.values()),
                "Show the list to the user once. Then run next.py again: it hands you packets in priority order."]
    if out:
        return finish(out, analysis_abs, repo)
    job = delta_job(repo, analysis, excludes, files, args.depth)
    if job:
        return finish(job, analysis_abs, repo)

    source = [f for f in files if f["kind"] == "source" and not f["binary"] and f["lines"] > 0
              and f["lang"] not in ("css", "html") and not coverage.skipped(skips, f["path"], "*")]
    priority = [norm(p).strip("/") for p in args.priority]

    def order(f):
        first = 0 if any(f["path"] == p or f["path"].startswith(p + "/") for p in priority) else 1
        comp = component_of(f["path"])
        comp_routes = -sum(len(g["routes"]) for g in source if component_of(g["path"]) == comp)
        return (first, comp_routes, comp, 0 if f["routes"] else 1, coverage.is_test_file(f["path"]), -f["lines"], f["path"])

    source.sort(key=order)
    queue = [(f, a, b) for f in source for a, b in packets_for(f)]
    total = len(queue)
    pending = None
    done = 0
    for f, a, b in queue:
        pages = sorted(set(page_for.get(f["path"], [])))
        gaps = packet_gaps(f, a, b, docs, pages, rules, skips, all_sections, file_hashes(repo, f["path"]))
        if gaps:
            if pending is None:
                pending = (f, a, b, pages, gaps)
        else:
            done += 1

    ledger = os.path.join(analysis_abs, "ledger")
    session_path = inventory.safe_target(repo, os.path.join(ledger, "session.json"))
    state = session_state(session_path, args.new_session, done)
    os.makedirs(ledger, exist_ok=True)
    with open(session_path, "w", encoding="utf-8") as handle:
        json.dump(state, handle)
    in_session = done - state["start_done"]

    if pending is not None:
        f, a, b, pages, gaps = pending
        if in_session >= args.budget:
            out = ["NEW CHAT",
                   "%d packets done in this chat (%d of %d overall, %d%%). Stop now and tell the user:" % (in_session, done, total, 100 * done // max(total, 1)),
                   "  continue the codebase analysis in %s" % analysis,
                   "The next chat starts with: python3 -I %s --repo . --analysis %s --new-session" % (os.path.join(HERE, "next.py"), analysis)]
            return finish(out, analysis_abs, repo)
        comp = component_of(f["path"])
        page = pages[0] if pages else module_page(f["path"], comp)
        index = next(i for i, q in enumerate(queue) if q[0] is f and q[1] == a) + 1
        out = ["NEXT PACKET %d of %d (%d done, %d%%; %d in this chat, budget %d)" % (index, total, done, 100 * done // max(total, 1), in_session, args.budget),
               "Component: %s" % comp,
               "Read:      %s lines %d-%d (of %d), in full" % (f["path"], a, b, f["lines"]),
               "Write:     %s/%s (%s)" % (analysis, page, "extend" if pages else "create; first line of the body: Source file: `%s`" % f["path"]),
               "Templates: references/output-templates.md - Front matter, lld/<component>/<module>.md, Function card%s" % (", lld/api/<group>.md" if any(g[0] == "route" for g in gaps) else ""),
               "", "To do in this packet (%d):" % len(gaps)]
        hashes = file_hashes(repo, f["path"])
        for kind, item, why in gaps:
            if kind == "symbol" or kind == "card":
                out.append("  - card %s: %s" % (describe_symbol(item, hashes), why))
            elif kind == "route":
                out.append("  - endpoint %s %s -> `%s` (line %d): %s" % ("/".join(item["methods"]), item["path"], item["handler"], item["line"], why))
            else:
                out.append("  - %s" % why)
        out += ["", "When every item is written, tick the packet in progress.md, write one line to the user, and run next.py again.",
                "Keep going: run next.py after every packet until it prints NEW CHAT or DONE. Do not end your turn in between.",
                "Command: python3 -I %s --repo . --analysis %s --depth %s" % (os.path.join(HERE, "next.py"), analysis, args.depth)]
        return finish(out, analysis_abs, repo)

    # Every packet is done: the remaining passes, in order.
    comps_in_pages = sorted({coverage.front_matter(t).get("component") for d, t in docs.items()
                             if d.startswith("lld/") and coverage.front_matter(t).get("component")})
    missing_readme = [c for c in comps_in_pages if "lld/%s/README.md" % c not in docs]
    progress = docs.get("progress.md", "")
    steps = [
        ("5: component design", missing_readme, "Write lld/<component>/README.md for: " + ", ".join(missing_readme)),
        ("6: sweep", [] if "## Sweep" in progress else ["sweep"], "Run the searches in references/search-sweep.md; record them under '## Sweep' in progress.md"),
        ("7: data dictionary", [] if "lld/data-dictionary.md" in docs else ["dd"], "Write lld/data-dictionary.md"),
        ("8: HLD", [h for h in ("hld/01-system-context.md", "hld/02-architecture.md", "hld/03-integrations.md",
                                "hld/04-data-architecture.md", "hld/05-key-flows.md", "hld/06-cross-cutting.md") if h not in docs], "Write: "),
        ("9: mind map, front page, reference", [h for h in ("00-mind-map.md", "README.md", "reference/glossary.md", "reference/configuration.md",
                                                           "reference/risks-and-surprises.md", "reference/open-questions.md") if h not in docs], "Write: "),
        ("10: knowledge base", [h for h in ("knowledge/AGENT-CONTEXT.md",) if h not in docs] +
         ([] if os.path.isfile(os.path.join(analysis_abs, "knowledge", "graph.json")) else ["run python3 -I %s --repo . --analysis %s" % (os.path.join(HERE, "knowledge.py"), analysis)]), "Do: "),
    ]
    for name, missing, text in steps:
        if missing:
            detail = text + (", ".join(missing) if text.endswith(": ") else "")
            out = ["NEXT PASS %s" % name, "All %d packets are done." % total, detail,
                   "Read that pass's section in references/passes.md first. Then run next.py again."]
            return finish(out, analysis_abs, repo)

    gate = subprocess.run([sys.executable, "-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "coverage.py"),
                           "--repo", repo, "--analysis", analysis, "--depth", args.depth] +
                          sum((["--exclude", e] for e in excludes), []), capture_output=True, text=True)
    if gate.returncode == 0:
        out = ["DONE", "coverage.py: result PASS at depth %s. Run references/quality-gate.md, then knowledge.py once more, then finish as SKILL.md says." % args.depth]
        if not os.path.isfile(os.path.join(analysis_abs, "ledger", "baseline.json")):
            out.append("Last, record the code this analysis describes, so later changes can be applied as a delta: "
                       "python3 -I %s --repo . --analysis %s --init" % (os.path.join(HERE, "delta.py"), analysis))
    else:
        out = ["NEXT PASS 11: quality gate", "coverage.py reports gaps; fix them from ledger/coverage-report.md, then run next.py again.", ""] + \
              [line for line in gate.stdout.splitlines() if line.startswith("  - ")][:15]
    return finish(out, analysis_abs, repo)


def finish(lines, analysis_abs, repo):
    text = "\n".join(lines) + "\n"
    target = inventory.safe_target(repo, os.path.join(analysis_abs, "ledger", "next.md"))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write("```text\n" + text + "```\n")
    sys.stdout.write(text)


if __name__ == "__main__":
    main()
