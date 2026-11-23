#!/usr/bin/env python3
"""Delta update: bring a finished analysis in line with code that changed since, without starting again.

Compares the repository now with the fingerprint recorded when the analysis last matched the code
(`<analysis>/ledger/baseline.json`) and works out, file by file and function by function, what
changed: files added, removed, renamed and changed; functions added, removed, changed and only
moved; routes added and removed. No source control is used. The comparison is between line
fingerprints, so it works the same after a pull, a branch switch, a merge or a copied folder.

  python3 -I <skill>/scripts/delta.py --repo . --analysis codebase-analysis --init [--label NAME] [--changed FILE]
  python3 -I <skill>/scripts/delta.py --repo . --analysis codebase-analysis [--label NAME]
  python3 -I <skill>/scripts/delta.py --repo . --analysis codebase-analysis --apply [--label NAME]

--init      Records the fingerprint of the code the analysis describes now. Run it when the gate passes.
            With --changed FILE, a list of paths a person made (for example the output of
            `git diff --name-status <commit the analysis was written from>`), the listed files are
            treated as changed since the analysis: their cards become work and every citation into
            them is marked for a recheck. For analyses written before delta updates existed.
(no flag)   Report only: writes ledger/delta.md with what changed and what --apply would do.
--apply     The mechanical part, on the pages: moves every citation whose lines only moved, rewrites
            the paths of renamed files, marks each citation it cannot move with
            <!-- recheck: was path:lines -->, records the work left in ledger/baseline.json and adds
            a row to delta-log.md. next.py then hands that work out.

Writes only inside the analysis folder. Read-only on the repository. Standard library only; never
imports or runs repository code and runs no source-control command.
"""

from __future__ import annotations

import argparse
import datetime
import difflib
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # never leave __pycache__ inside the installed skill
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inventory  # noqa: E402
import coverage  # noqa: E402

TOOL = "analyzing-a-codebase/scripts/delta.py 1.8.0"
NOT_CARDED = ("class", "table", "view", "paragraph", "imports")
RENAME_SIMILARITY = 0.5  # a removed and an added file this alike (same extension) are one file, renamed and edited
# Configuration files that may hold secrets keep a whole-file fingerprint only, never one per line.
SECRET_LIKE = re.compile(r"(^|/)\.env[^/]*$|\.(pem|key|p12|pfx|jks|keystore|crt|cer)$|secret|credential|passw|token", re.I)
# Historical records keep the line numbers they were written with.
NOT_REWRITTEN = {"revision-log.md", "delta-log.md", "CHANGELOG.md"}
# One line per cited file at the end of a page: the version of that file the page's citations count lines in.
RECORD = re.compile(r"^<!--\s*cites\s+(\S+)@([0-9a-f]{40})\s*-->\s*$")
RECORD_ANY = re.compile(r"^<!--\s*cites\s+\S+@[0-9a-f]{40}\s*-->", re.M)
HEADING_LINE = re.compile(r"^#{1,6}\s")
GITATTRIBUTES = """# Written by analyzing-a-codebase: how Git merges this folder when several people update it.
# A page changed on both sides is never mixed line by line (its line numbers would count against two versions
# of the code): Git keeps your side and reports a conflict. Keep it as it is, mark it resolved, and run the
# update: the other side's code changes are found again and their cards redone.
# Changelogs keep both sides. Generated files keep one side and are rebuilt by the scripts.
*.md merge=binary
CHANGELOG.md merge=union
delta-log.md merge=union
ledger/baseline.json merge=binary
ledger/inventory.json merge=binary
ledger/session.json merge=binary
ledger/next.md merge=binary
ledger/delta.md merge=binary
ledger/track.md merge=binary
ledger/symbol-checklist.md merge=binary
ledger/coverage-report.md merge=binary
ledger/citations.tsv merge=binary
knowledge/*.json merge=binary
knowledge/*.jsonl merge=binary
knowledge/*.csv merge=binary
"""


def now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def file_sha(full: str) -> str:
    digest = hashlib.sha256()
    with open(full, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def blob_id(raw: bytes) -> str:
    """The id Git gives this content (computed here; no Git command). Pages record it per cited file."""
    return hashlib.sha1(b"blob %d\x00" % len(raw) + raw).hexdigest()


def file_ids(full: str):
    with open(full, "rb") as handle:
        raw = handle.read()
    return hashlib.sha256(raw).hexdigest(), blob_id(raw)


# ---------- the fingerprint of a tree ----------

def make_entry(f: dict, sha: str, text, blob: str = "") -> dict:
    """The baseline entry of one file: whole-file hash, and for text files line fingerprints, symbols and routes."""
    entry = {"sha": sha, "blob": blob, "kind": f["kind"], "lines": f["lines"], "binary": f["binary"]}
    if text is not None and not (f["kind"] != "source" and SECRET_LIKE.search(f["path"])):
        hashes = inventory.line_hashes(text)
        entry["hashes"] = hashes
        entry["symbols"] = [{"qualname": s["qualname"], "name": s["name"], "kind": s["kind"],
                             "start": s["start"], "end": s["end"], "size": s["size"],
                             "stamp": inventory.stamp(hashes, s["start"], s["end"])}
                            for s in f["symbols"] if s["kind"] != "imports"]
        entry["routes"] = [{"methods": r["methods"], "path": r["path"], "handler": r["handler"], "line": r["line"]}
                           for r in f["routes"]]
    return entry


def entry_from_bytes(path: str, raw: bytes) -> dict:
    """The same entry for content that is not on disk (a file as it was in an older commit)."""
    text = inventory.decode(raw)
    return make_entry(inventory.file_entry(path, text), hashlib.sha256(raw).hexdigest(), text, blob_id(raw))


def snapshot(repo: str, analysis: str, excludes):
    files, _excluded = inventory.scan(repo, analysis, excludes)
    snap = {}
    for f in files:
        full = os.path.join(repo, f["path"])
        try:
            sha, blob = file_ids(full)
        except OSError:
            continue
        snap[f["path"]] = make_entry(f, sha, None if f["binary"] else inventory.read_text(full), blob)
    return snap


def line_map(old: dict, new: dict):
    """old line -> new line for every line that is the same on both sides; None when the files are identical."""
    if old["sha"] == new["sha"]:
        return None
    if "hashes" not in old or "hashes" not in new:
        return {}
    mapping = {}
    matcher = difflib.SequenceMatcher(None, old["hashes"], new["hashes"], autojunk=False)
    for tag, i1, i2, j1, _j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                mapping[i1 + k + 1] = j1 + k + 1
    return mapping


def pair_symbols(old_syms, new_syms):
    by_name = {}
    for s in old_syms:
        by_name.setdefault(s["qualname"], []).append(s)
    pairs, added = [], []
    for s in new_syms:
        bucket = by_name.get(s["qualname"])
        if bucket:
            pairs.append((bucket.pop(0), s))
        else:
            added.append(s)
    removed = [s for bucket in by_name.values() for s in bucket]
    return pairs, added, removed


def route_key(r) -> tuple:
    return (tuple(sorted(r["methods"])), coverage.norm_route(r["path"]))


def compare(old: dict, new: dict) -> dict:
    added = sorted(set(new) - set(old))
    removed = sorted(set(old) - set(new))
    renames = {}
    by_sha = {}
    for p in added:
        by_sha.setdefault(new[p]["sha"], []).append(p)
    for p in removed:
        if by_sha.get(old[p]["sha"]):
            renames[p] = by_sha[old[p]["sha"]].pop(0)
    left = [p for p in added if p not in renames.values()]
    for p in removed:
        if p in renames or "hashes" not in old[p]:
            continue
        best, ratio = None, 0.0
        for q in left:
            if os.path.splitext(q)[1] != os.path.splitext(p)[1] or "hashes" not in new[q]:
                continue
            score = difflib.SequenceMatcher(None, old[p]["hashes"], new[q]["hashes"], autojunk=False).ratio()
            if score > ratio:
                best, ratio = q, score
        if best is not None and ratio >= RENAME_SIMILARITY:
            renames[p] = best
            left.remove(best)
    result = {"added": left, "removed": [p for p in removed if p not in renames], "renamed": renames,
              "changed": sorted(p for p in set(old) & set(new) if old[p]["sha"] != new[p]["sha"]), "files": {}}
    for old_path, new_path in [(p, p) for p in result["changed"]] + sorted(renames.items()):
        o, n = old[old_path], new[new_path]
        pairs, sym_added, sym_removed = pair_symbols(o.get("symbols", []), n.get("symbols", []))
        old_routes = {route_key(r): r for r in o.get("routes", [])}
        new_routes = {route_key(r): r for r in n.get("routes", [])}
        result["files"][new_path] = {
            "from": old_path,
            "changed": [b for a, b in pairs if a["stamp"] != b["stamp"]],
            "moved": [b for a, b in pairs if a["stamp"] == b["stamp"] and a["start"] != b["start"]],
            "added": sym_added, "removed": sym_removed,
            "routes_added": [new_routes[k] for k in new_routes if k not in old_routes],
            "routes_removed": [old_routes[k] for k in old_routes if k not in new_routes],
        }
    return result


# ---------- work items ----------

def needs_card(path: str, s: dict, rules: dict) -> bool:
    return (rules["card_lines"] is not None and s["kind"] not in NOT_CARDED
            and (s["size"] or 0) >= rules["card_lines"] and not coverage.is_test_file(path))


def items_from(diff: dict, new: dict, rules: dict):
    items = []
    for path, d in diff["files"].items():
        changed_names = {s["qualname"] for s in d["changed"]}
        for why, group in (("changed", d["changed"]), ("added", d["added"])):
            items += [{"kind": "card", "path": path, "qualname": s["qualname"], "why": why}
                      for s in group if needs_card(path, s, rules)]
        items += [{"kind": "remove-card", "path": path, "qualname": s["qualname"], "name": s["name"]}
                  for s in d["removed"] if s["kind"] not in ("imports",)]
        for r in new[path].get("routes", []):
            if r["methods"] == ["UI"]:
                continue
            if r in d["routes_added"] or r["handler"] in changed_names:
                items.append({"kind": "endpoint", "path": path, "methods": r["methods"], "route": r["path"],
                              "handler": r["handler"], "why": "added" if r in d["routes_added"] else "handler changed"})
        items += [{"kind": "remove-route", "path": path, "methods": r["methods"], "route": r["path"]}
                  for r in d["routes_removed"] if r["methods"] != ["UI"]]
    items += [{"kind": "remove-file", "path": p} for p in diff["removed"]]
    return items


def item_key(item) -> tuple:
    return (item["kind"], item["path"], item.get("qualname") or item.get("route") or "", tuple(sorted(item.get("methods", []))))


def carry_over(items, diff: dict, new: dict):
    """Earlier items follow renames; items on code that disappeared since become removals."""
    out = []
    for item in items:
        item = dict(item)
        if item["path"] in diff["renamed"]:
            item["path"] = diff["renamed"][item["path"]]
        if item["path"] not in new and item["kind"] != "remove-file":
            item = {"kind": "remove-file", "path": item["path"]}
        elif item["kind"] == "card" and item["qualname"] not in {s["qualname"] for s in new[item["path"]].get("symbols", [])}:
            item = {"kind": "remove-card", "path": item["path"], "qualname": item["qualname"],
                    "name": item["qualname"].split(".")[-1]}
        elif item["kind"] == "endpoint" and route_key({"methods": item["methods"], "path": item["route"]}) not in \
                {route_key(r) for r in new[item["path"]].get("routes", [])}:
            item = {"kind": "remove-route", "path": item["path"], "methods": item["methods"], "route": item["route"]}
        out.append(item)
    return out


def merge(*groups):
    seen, out = set(), []
    for group in groups:
        for item in group:
            if item_key(item) not in seen:
                seen.add(item_key(item))
                out.append(item)
    return out


# ---------- reading the pages ----------

def pages_by_source(docs):
    page_for = {}
    for doc, text in docs.items():
        declared = coverage.front_matter(text).get("source", [])
        for path in ([declared] if isinstance(declared, str) else declared):
            if path:
                page_for.setdefault(coverage.strip_dot(path.strip("`").split(":")[0]), set()).add(doc)
        for decl in coverage.SOURCE_DECL.findall(text):
            for token in coverage.BACKTICK.findall(decl):
                page_for.setdefault(coverage.strip_dot(token.split(":")[0].strip()), set()).add(doc)
    return page_for


def endpoint_body(all_sections, methods, route):
    path = coverage.norm_route(route)
    pattern = re.compile(r"(?<![\w/{<:-])" + re.escape(path) + r"/?(?![\w/{<-])")
    wanted = [m for m in methods if m != "ANY"]
    for _doc, title, body, level in all_sections:
        if level > 1 and pattern.search(title) and all(re.search(r"\b%s\b" % m, title) for m in wanted) \
                and re.search(r"\brequest\b", body, re.I) and re.search(r"\bresponses?\b", body, re.I):
            return body
    return None


def handler_stamp(entry: dict, handler: str, line: int) -> str:
    match = [s for s in entry.get("symbols", []) if s["qualname"] == handler]
    return match[0]["stamp"] if match else inventory.stamp(entry.get("hashes", []), line, line)


def is_open(item, now, docs, page_for, all_sections) -> bool:
    kind, path = item["kind"], item["path"]
    entry = now.get(path)
    pages = sorted(page_for.get(path, set()))
    if kind == "card":
        if entry is None:
            return False
        symbols = entry.get("symbols", [])
        match = [s for s in symbols if s["qualname"] == item["qualname"]]
        if not match:
            return False
        page_sections = [sec for p in pages for sec in coverage.sections(docs[p])]
        body = coverage.find_card(page_sections, match[0], symbols, os.path.basename(path))
        return body is None or match[0]["stamp"] not in coverage.STAMP.findall(body)
    if kind == "endpoint":
        if entry is None:
            return False
        body = endpoint_body(all_sections, item["methods"], item["route"])
        wanted_key = route_key({"methods": item["methods"], "path": item["route"]})
        live = [r for r in entry.get("routes", []) if route_key(r) == wanted_key]
        if not live:
            return False
        wanted = handler_stamp(entry, live[0]["handler"], live[0]["line"])
        return body is None or wanted not in coverage.STAMP.findall(body)
    if kind == "remove-card":
        if entry is None:
            return False
        live = entry.get("symbols", [])
        if item["qualname"] in {s["qualname"] for s in live}:
            return False
        names = [item["qualname"]] + ([] if item["name"] in {s["name"] for s in live} or item["name"] == item["qualname"] else [item["name"]])
        patterns = [coverage.name_pattern(n) for n in names]
        for p in pages:
            for title, level, body, _line in coverage.sections(docs[p]):
                if level > 1 and any(x.search(title) for x in patterns) and re.search(r"\bsteps?\b", body, re.I):
                    return True
        return False
    if kind == "remove-route":
        if any(route_key(r) == route_key({"methods": item["methods"], "path": item["route"]})
               for e in now.values() for r in e.get("routes", [])):
            return False
        return endpoint_body(all_sections, item["methods"], item["route"]) is not None
    if kind == "remove-file":
        return path not in now and bool(pages)
    return False


def markers(docs):
    found = []
    for doc in sorted(docs):
        for number, line in enumerate(docs[doc].splitlines(), 1):
            if coverage.RECHECK.search(line):
                found.append((doc, number, line.strip()))
    return found


# ---------- moving citations ----------

def records_block(records: dict) -> list:
    """Record lines, a blank line between each, so two branches changing two files' records merge cleanly."""
    out = []
    for path in sorted(records):
        out += ["", "<!-- cites %s@%s -->" % (path, records[path])]
    return out


def settle_conflicts(text: str):
    """(text, unresolved): conflict blocks made only of record lines are dropped (both sides: those citations are
    then rechecked, never guessed); any other conflict leaves the page untouched for a person."""
    if "\n<<<<<<< " not in "\n" + text:
        return text, False
    out, block, state = [], [], None
    for line in text.split("\n"):
        if line.startswith("<<<<<<< ") and state is None:
            state, block = "in", []
        elif state == "in" and (line.startswith(">>>>>>> ")):
            if any(l.strip() and not RECORD.match(l) and l != "=======" and not l.startswith("||||||| ") for l in block):
                return text, True
            state = None
        elif state == "in":
            block.append(line)
        else:
            out.append(line)
    return "\n".join(out), state is not None


def page_records(text: str) -> dict:
    return {coverage.strip_dot(m.group(1)): m.group(2) for m in (RECORD.match(l) for l in text.split("\n")) if m}


def shift(mapping, start: int, end: int):
    """New (start, end) when every line of the range survived in one piece; None otherwise. mapping None = identity."""
    if mapping is None:
        return start, end
    if all(k in mapping for k in range(start, end + 1)) and mapping[end] - mapping[start] == end - start:
        return mapping[start], mapping[end]
    return None


def map_hashes(old_hashes, new_hashes):
    if old_hashes == new_hashes:
        return None
    mapping = {}
    for tag, i1, i2, j1, _j2 in difflib.SequenceMatcher(None, old_hashes, new_hashes, autojunk=False).get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                mapping[i1 + k + 1] = j1 + k + 1
    return mapping


def rewrite_docs(docs, old: dict, now: dict, maps: dict, renames: dict, hashes_of=None):
    """Bring every citation to the code on disk, or mark it; record per page the version each cited file is at.

    Each citation is placed by the first rule that applies:
      1. Inside a stamped card, into the card's own lines: the card's code is found by its stamp, wherever it is
         now, and the citation moves with it. The card's code changed: marked.
      2. The page records the version of the cited file: lines are mapped from that version to the file now.
         A version that cannot be read: marked.
      3. No record, pages carry records elsewhere: kept if the file is unchanged since the baseline, else marked.
      4. No record anywhere yet (an analysis from before records): mapped from the baseline, as recorded.
    So a page merged in from another branch is placed by its own record, never by this branch's baseline.
    maps: old path -> (new path or None when removed, line map); renames: old path -> new path.
    Returns (new texts of the changed docs, statistics).
    """
    stats = {"moved": 0, "renamed": 0, "marked": 0, "anchored": 0, "recorded": 0}
    records_era = any(RECORD_ANY.search(t) for t in docs.values())
    back = {b: a for a, b in renames.items()}
    basenames = {}
    for p in set(old) | set(now):
        basenames.setdefault(os.path.basename(p), set()).add(p)
    by_blob = {e["blob"]: e["hashes"] for e in list(old.values()) + list(now.values()) if e.get("blob") and "hashes" in e}

    def version_hashes(blob):
        if blob in by_blob:
            return by_blob[blob]
        if hashes_of is not None:
            try:
                found = hashes_of(blob)
            except Exception:  # an unreadable version is unknown, and its citations are marked
                found = None
            if found is not None:
                by_blob[blob] = found
            return found
        return None

    declared_by = {}
    for path, pages in pages_by_source(docs).items():
        for doc in pages:
            declared_by.setdefault(doc, set()).add(path)
    front_renames = [(re.compile(r"(?<![\w./-])" + re.escape(a) + r"(?![\w/-])"), b) for a, b in renames.items()]
    out = {}
    for doc, text in docs.items():
        if doc in NOT_REWRITTEN:
            continue
        declared = declared_by.get(doc, set())
        original = text
        text, unresolved = settle_conflicts(text)
        if unresolved:
            stats.setdefault("conflicted", []).append(doc)
            continue
        records = page_records(text)
        lines = [l for l in text.split("\n") if not RECORD.match(l)]
        while lines and not lines[-1].strip():
            lines.pop()

        def resolve(cited):
            """(path in the baseline or None, path now or None) for a cited path, or None when it is not a known file."""
            if cited not in old and cited not in now and "/" not in cited:
                cands = {p for p in declared if os.path.basename(p) == cited} or basenames.get(cited, set())
                if len(cands) != 1:
                    return None
                cited = next(iter(cands))
            if cited in old:
                cur = renames.get(cited, cited)
                return cited, (cur if cur in now else None)
            if cited in now:
                return back.get(cited, cited), cited
            return None

        # Cards: the block under each heading (up to the next heading) that carries a stamp.
        anchor_of, in_fence, block = {}, False, None
        blocks = []
        for index, line in enumerate(lines):
            if line.strip().startswith("```"):
                in_fence = not in_fence
            if not in_fence and HEADING_LINE.match(line):
                block = [index]
                blocks.append(block)
            elif block is not None:
                block.append(index)
        for block in blocks:
            text_block = "\n".join(lines[i] for i in block)
            stamp = coverage.STAMP.search(text_block)
            if not stamp:
                continue
            for index in block:
                anchor = next((m for m in coverage.CITATION.finditer(lines[index]) if m.group(3)
                               and not lines[index][m.end():].lstrip().startswith("<!-- recheck")), None)
                if anchor:
                    break
            if not anchor:
                continue
            found = resolve(coverage.strip_dot(anchor.group(1).replace("\\", "/")))
            if not found or not found[1]:
                continue
            cur, a, b = found[1], int(anchor.group(2)), int(anchor.group(3))
            matches = [x for x in now[cur].get("symbols", []) if x["stamp"] == stamp.group(1)]
            matches.sort(key=lambda x: abs(x["start"] - a))
            offset = matches[0]["start"] - a if matches and matches[0]["end"] - matches[0]["start"] == b - a else None
            for index in block:
                anchor_of[index] = (cur, a, b, offset)

        cited_now = set()

        def fix(match, index):
            raw = match.group(1)
            tail = match.string[match.end():].lstrip()
            cited = coverage.strip_dot(raw.replace("\\", "/"))
            found = resolve(cited)
            if found is None:
                return match.group(0)
            if tail.startswith("<!--") and coverage.RECHECK.match(tail):
                return match.group(0)  # already waiting for a recheck: its numbers belong to an older version
            old_path, cur = found
            start = int(match.group(2))
            end = int(match.group(3) or start)
            was = "%s:%d%s" % (raw, start, "-%d" % end if match.group(3) else "")
            ranged = bool(match.group(3))

            def mark(why):
                stats["marked"] += 1
                return match.group(0) + " <!-- recheck: was %s%s -->" % (was, ", " + why if why else "")

            if cur is None:
                return mark("file removed")
            path_text = raw
            if old_path and cur != old_path:
                if cited == old_path:
                    path_text = cur
                elif "/" not in cited and cited == os.path.basename(old_path) != os.path.basename(cur):
                    path_text = os.path.basename(cur)
                if path_text != raw:
                    stats["renamed"] += 1
            entry = now[cur]

            def place(new_range, how):
                if new_range is None:
                    return mark("")
                a, b = new_range
                if (a, b) != (start, end):
                    stats[how] += 1
                cited_now.add(cur)
                return "`%s:%s`" % (path_text, "%d-%d" % (a, b) if ranged else a)

            anchor = anchor_of.get(index)
            if anchor and anchor[0] == cur and anchor[1] <= start and end <= anchor[2]:
                if anchor[3] is None:
                    return mark("the card's code changed")
                return place((start + anchor[3], end + anchor[3]), "anchored")
            record = records.get(cur) or (records.get(old_path) if old_path else None)
            if record:
                if record == entry.get("blob"):
                    return place((start, end), "moved")
                old_hashes = version_hashes(record)
                if old_hashes is None or "hashes" not in entry:
                    return mark("version of the page unknown")
                return place(shift(map_hashes(old_hashes, entry["hashes"]), start, end), "moved")
            if records_era:
                if old_path in old and old[old_path]["sha"] == entry["sha"]:
                    return place((start, end), "moved")
                return mark("version of the page unknown")
            if old_path not in maps:
                return place((start, end), "moved")
            return place(shift(maps[old_path][1], start, end), "moved")

        in_fence, front_end = False, 0
        if lines and lines[0].strip() == "---":
            front_end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        for index, line in enumerate(lines):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            new_line = coverage.CITATION.sub(lambda m, i=index: fix(m, i), line)
            if index <= front_end:  # front matter: source, reads, writes ... name files without backticks
                for pattern, target in front_renames:
                    new_line = pattern.sub(lambda _m, t=target: t, new_line)
            else:  # `Source file:` lines and plain mentions
                for a, b in renames.items():
                    new_line = new_line.replace("`%s`" % a, "`%s`" % b)
            lines[index] = new_line
        new_records = {p: now[p]["blob"] for p in cited_now if now[p].get("blob")}
        if new_records:
            stats["recorded"] += 1
            while lines and not lines[-1].strip():
                lines.pop()
            lines += records_block(new_records)
        new_text = "\n".join(lines) + ("\n" if original.endswith("\n") else "")
        if new_text != original:
            out[doc] = new_text
    return out, stats


def stale_records(docs, now):
    """(page, file) pairs whose recorded version is not the file on disk: the page needs --apply."""
    return [(doc, path) for doc in sorted(docs) if doc not in NOT_REWRITTEN
            for path, blob in page_records(docs[doc]).items() if path in now and now[path].get("blob") and blob != now[path]["blob"]]


def record_new_pages(repo: str, analysis_abs: str, docs, now) -> int:
    """Pages written since the last apply cite the code on disk: give each its records. Call only with no drift."""
    count = 0
    for doc, text in docs.items():
        if doc in NOT_REWRITTEN:
            continue
        if settle_conflicts(text)[1] or "\n<<<<<<< " in "\n" + text:
            continue  # a page in a merge conflict is left to --apply and to the person
        have = page_records(text)
        cited = set()
        for match in coverage.CITATION.finditer(text):
            path = coverage.strip_dot(match.group(1).replace("\\", "/"))
            if path not in now and "/" not in path:
                cands = [p for p in now if os.path.basename(p) == path]
                path = cands[0] if len(cands) == 1 else path
            if path in now and now[path].get("blob") and path not in have:
                cited.add(path)
        if cited:
            have.update({p: now[p]["blob"] for p in cited})
            body = [l for l in text.split("\n") if not RECORD.match(l)]
            while body and not body[-1].strip():
                body.pop()
            write(repo, os.path.join(analysis_abs, doc), "\n".join(body + records_block(have)) + "\n")
            count += 1
    return count


def write_gitattributes(repo: str, analysis_abs: str) -> None:
    path = os.path.join(analysis_abs, ".gitattributes")
    if not os.path.isfile(path):
        write(repo, path, GITATTRIBUTES)


# ---------- files ----------

def ours_side(text: str) -> str:
    """The text with Git conflict blocks reduced to the checked-out side."""
    out, state = [], "both"
    for line in text.split("\n"):
        if line.startswith("<<<<<<< "):
            state = "ours"
        elif line.startswith("||||||| ") and state == "ours":
            state = "base"
        elif line == "=======" and state in ("ours", "base"):
            state = "theirs"
        elif line.startswith(">>>>>>> ") and state == "theirs":
            state = "both"
        elif state in ("both", "ours"):
            out.append(line)
    return "\n".join(out)


def load_baseline(path: str):
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        if "\n<<<<<<< " in "\n" + text:
            print("note: %s has a merge conflict; using the checked-out side. Every page is still placed by its own "
                  "record, and cards by their stamps. Mark the file resolved in Git after --apply." % os.path.basename(path))
            text = ours_side(text)
        return json.loads(text)
    except (OSError, ValueError):
        inventory.fail("cannot read %s; record a fresh one with --init" % path)


def write(repo: str, path: str, text: str) -> None:
    target = inventory.safe_target(repo, path)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(text)


def parse_changed(path: str):
    """Plain paths, or `git diff --name-status` lines (M, A, D, R<score>, C<score>)."""
    changed, deleted, renamed = set(), set(), {}
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            rows = handle.read().splitlines()
    except OSError:
        inventory.fail("cannot read the changed-files list: " + path)
    for row in rows:
        if not row.strip() or row.lstrip().startswith("#"):
            continue
        parts = [coverage.strip_dot(p.strip()) for p in (row.split("\t") if "\t" in row else row.split())]
        status = parts[0][:1].upper() if len(parts) > 1 and re.match(r"^[ACDMRTU]\d*$", parts[0]) else ""
        if status == "D":
            deleted.add(parts[1])
        elif status == "R" and len(parts) >= 3:
            renamed[parts[1]] = parts[2]
        else:
            changed.add(parts[-1])
    return changed, deleted, renamed


def log_row(repo, analysis_abs, label_from, label_to, diff, stats, items) -> None:
    path = os.path.join(analysis_abs, "delta-log.md")
    head = ("# Delta log\n\nOne row per `delta.py --apply`: the code the analysis was brought in line with.\n\n"
            "| Applied | From | To | Files changed, added, removed, renamed | Functions changed | Citations moved | Citations to recheck | Work items |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n")
    existing = open(path, encoding="utf-8").read() if os.path.isfile(path) else head
    functions = sum(len(d["changed"]) for d in diff["files"].values())
    row = "| %s | %s | %s | %d, %d, %d, %d | %d | %d | %d | %d |\n" % (
        now_iso(), label_from or "-", label_to or "-", len(diff["changed"]), len(diff["added"]),
        len(diff["removed"]), len(diff["renamed"]), functions, stats["moved"], stats["marked"], len(items))
    write(repo, path, existing.rstrip("\n") + "\n" + row)


def names(group) -> str:
    return (", ".join("`%s`" % s["qualname"] for s in group[:8]) + (" ..." if len(group) > 8 else "")) or "-"


def report(diff, stats, items, open_items, found_markers, baseline, label, applied) -> str:
    files = diff["files"]
    out = ["# Delta since the analysis last matched the code", "",
           "Baseline recorded %s%s. %s on %s%s." % (
               baseline.get("recorded", "?"), " (%s)" % baseline["label"] if baseline.get("label") else "",
               "Applied" if applied else "Report only, nothing changed", now_iso(), " (%s)" % label if label else ""), "",
           "| Measure | Count |", "| --- | --- |",
           "| Files changed | %d |" % len(diff["changed"]), "| Files added | %d |" % len(diff["added"]),
           "| Files removed | %d |" % len(diff["removed"]), "| Files renamed | %d |" % len(diff["renamed"]),
           "| Functions changed | %d |" % sum(len(d["changed"]) for d in files.values()),
           "| Functions added | %d |" % sum(len(d["added"]) for d in files.values()),
           "| Functions removed | %d |" % sum(len(d["removed"]) for d in files.values()),
           "| Functions only moved | %d |" % sum(len(d["moved"]) for d in files.values()),
           "| Routes added, removed | %d, %d |" % (sum(len(d["routes_added"]) for d in files.values()),
                                                  sum(len(d["routes_removed"]) for d in files.values())),
           "| Citations %s to new lines | %d |" % ("moved" if applied else "that will move", stats["moved"]),
           "| Card citations %s with their code (found by stamp) | %d |" % ("moved" if applied else "that will move", stats.get("anchored", 0)),
           "| Citations %s for a recheck | %d |" % ("marked" if applied else "that will be marked", stats["marked"]),
           "| Work items open | %d |" % len(open_items), ""]
    if diff["renamed"]:
        out += ["## Renamed", "", "| From | To |", "| --- | --- |"] + ["| `%s` | `%s` |" % kv for kv in sorted(diff["renamed"].items())] + [""]
    for title, key in (("Files added (next.py hands these out as packets)", "added"), ("Files removed", "removed")):
        if diff[key]:
            out += ["## " + title, ""] + ["- `%s`" % p for p in diff[key]] + [""]
    if files:
        out += ["## Changed files", "", "| File | Changed | Added | Removed | Only moved |", "| --- | --- | --- | --- | --- |"]
        for path in sorted(files):
            d = files[path]
            out.append("| `%s` | %s | %s | %s | %d |" % (path, names(d["changed"]), names(d["added"]), names(d["removed"]), len(d["moved"])))
        out.append("")
    out += ["## Work for the analysis", ""]
    if not applied:
        out += ["Run `delta.py --apply` to move the citations and record this work; next.py then hands it out.", ""]
    rows = open_items if applied else items
    out += ["- %s `%s` %s" % (i["kind"], i["path"], i.get("qualname") or ("%s %s" % ("/".join(i.get("methods", [])), i.get("route", "")))) for i in rows] or ["None."]
    if found_markers:
        out += ["", "## Citations waiting for a recheck (%d)" % len(found_markers), ""] + ["- %s:%d" % (d, n) for d, n, _ in found_markers[:200]]
    return "\n".join(out) + "\n"


# ---------- what next.py asks ----------

def pending_work(repo: str, analysis: str, excludes, check_drift: bool = True):
    """None without a baseline; else {"drift": bool, "items": [...], "markers": [...], "knowledge": bool, "now": snapshot}."""
    analysis_abs = os.path.join(repo, analysis)
    path = os.path.join(analysis_abs, "ledger", "baseline.json")
    if not os.path.isfile(path):
        return None
    baseline = load_baseline(path)
    now = snapshot(repo, analysis, baseline.get("excludes", excludes))
    drift = check_drift and {p: e["sha"] for p, e in now.items()} != {p: e["sha"] for p, e in baseline["files"].items()}
    docs = coverage.load_docs(analysis_abs)
    behind_pages = stale_records(docs, now) if check_drift else []
    page_for = pages_by_source(docs)
    all_sections = [(d, t, b, lvl) for d, text in docs.items() for t, lvl, b, _ in coverage.sections(text)]
    items = [i for i in baseline.get("pending", []) if is_open(i, now, docs, page_for, all_sections)]
    graph = os.path.join(analysis_abs, "knowledge", "graph.json")
    knowledge = bool(baseline.get("knowledge_after")) and (
        not os.path.isfile(graph) or os.path.getmtime(graph) < baseline["knowledge_after"])
    return {"drift": drift, "behind_pages": behind_pages, "items": items, "markers": markers(docs), "knowledge": knowledge, "docs": docs,
            "now": now, "page_for": page_for, "label": baseline.get("label")}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--analysis", default="codebase-analysis")
    parser.add_argument("--depth", choices=sorted(coverage.DEPTHS), default="deep")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--label", default="", help="a name for the code now, as the person gives it (branch, tag, date)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--init", action="store_true", help="record the fingerprint of the code the analysis describes now")
    mode.add_argument("--apply", action="store_true", help="move citations, mark the rest, record the work")
    parser.add_argument("--changed", default=None, help="with --init: list of paths changed since the analysis")
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    analysis = coverage.strip_dot(args.analysis.replace("\\", "/")).strip("/")
    if os.path.isabs(args.analysis) or ".." in analysis.split("/") or analysis in ("", "."):
        inventory.fail("--analysis must be a folder inside the repository, given relative to it")
    analysis_abs = os.path.join(repo, analysis)
    if not os.path.isdir(analysis_abs):
        inventory.fail("analysis folder not found: " + analysis)
    if args.changed and not args.init:
        inventory.fail("--changed goes with --init")
    rules = coverage.DEPTHS[args.depth]
    excludes = [coverage.strip_dot(e.replace("\\", "/")).strip("/") for e in args.exclude]
    baseline_path = os.path.join(analysis_abs, "ledger", "baseline.json")
    docs = coverage.load_docs(analysis_abs)

    if args.init:
        if os.path.isfile(baseline_path):
            inventory.fail("ledger/baseline.json exists: the analysis is already tracked. Run without --init to see the delta")
        now = snapshot(repo, analysis, excludes)
        items, diff = [], {"changed": [], "added": [], "removed": [], "renamed": {}, "files": {}}
        texts, stats = rewrite_docs(docs, now, now, {}, {})  # the pages match this code: record it on each page
        if args.changed:
            changed, deleted, renamed = parse_changed(args.changed)
            # Without the old fingerprint nothing can be moved: every citation into a listed file is marked.
            old = {p: {"sha": "-"} for p in set(now) | deleted | set(renamed)}
            maps = {p: (None, {}) for p in deleted}
            maps.update({a: (b, {}) for a, b in renamed.items() if b in now})
            maps.update({p: (p, {}) for p in changed if p in now})
            texts, stats = rewrite_docs(docs, old, now, maps, {a: b for a, b in renamed.items() if b in now})
            touched = sorted({p for p in changed if p in now} | {b for b in renamed.values() if b in now})
            for p in touched:
                items += [{"kind": "card", "path": p, "qualname": s["qualname"], "why": "listed as changed"}
                          for s in now[p].get("symbols", []) if needs_card(p, s, rules)]
                items += [{"kind": "endpoint", "path": p, "methods": r["methods"], "route": r["path"],
                           "handler": r["handler"], "why": "listed as changed"}
                          for r in now[p].get("routes", []) if r["methods"] != ["UI"]]
            items += [{"kind": "remove-file", "path": p} for p in sorted(deleted) if p not in now]
            diff.update({"changed": touched, "removed": sorted(deleted - set(now)), "renamed": renamed})
        for doc, text in texts.items():
            write(repo, os.path.join(analysis_abs, doc), text)
        write_gitattributes(repo, analysis_abs)
        baseline = {"tool": TOOL, "recorded": now_iso(), "label": args.label, "excludes": excludes,
                    "depth": args.depth, "pending": items, "files": now,
                    "knowledge_after": datetime.datetime.now().timestamp() if items else None}
        write(repo, baseline_path, json.dumps(baseline, indent=0))
        if args.changed:
            log_row(repo, analysis_abs, "(analysis)", args.label, diff, stats, items)
        print("ok: recorded the fingerprint of %d files%s" % (len(now), " (%s)" % args.label if args.label else ""))
        if args.changed:
            print("%d citations marked for a recheck, %d paths renamed, %d work items" % (stats["marked"], stats["renamed"], len(items)))
            print("next: python3 -I %s --repo . --analysis %s --depth %s" % (os.path.join(HERE, "next.py"), analysis, args.depth))
        print("wrote " + os.path.relpath(baseline_path, repo))
        return

    if not os.path.isfile(baseline_path):
        inventory.fail("no ledger/baseline.json: record it with --init when the analysis matches the code "
                       "(references/delta.md says how to start from an older analysis)")
    baseline = load_baseline(baseline_path)
    now = snapshot(repo, analysis, baseline.get("excludes", excludes))
    result = run_delta(repo, analysis, baseline, baseline["files"], now, rules, args.apply, args.label)
    print_summary(repo, analysis, result, args.apply, args.depth)


def run_delta(repo, analysis, baseline, old, now, rules, apply, label, extra=None, hashes_of=None):
    """Compare old with now; with apply, rewrite citations, record the work and log it. Returns the result."""
    analysis_abs = os.path.join(repo, analysis)
    baseline_path = os.path.join(analysis_abs, "ledger", "baseline.json")
    docs = coverage.load_docs(analysis_abs)
    diff = compare(old, now)
    maps = {p: (p, line_map(old[p], now[p])) for p in diff["changed"]}
    maps.update({a: (b, line_map(old[a], now[b])) for a, b in diff["renamed"].items()})
    maps.update({p: (None, {}) for p in diff["removed"]})
    texts, stats = rewrite_docs(docs, old, now, maps, diff["renamed"], hashes_of)
    items = merge(carry_over(baseline.get("pending", []), diff, now), items_from(diff, now, rules))
    if apply:
        label_from = baseline.get("label", "")
        for doc, text in texts.items():
            write(repo, os.path.join(analysis_abs, doc), text)
        docs.update(texts)
        write_gitattributes(repo, analysis_abs)
        anything = bool(diff["changed"] or diff["added"] or diff["removed"] or diff["renamed"])
        baseline.update({"tool": TOOL, "recorded": now_iso(), "files": now, "pending": items,
                         "label": label or baseline.get("label", ""), "excludes": baseline.get("excludes", [])})
        baseline.update(extra or {})
        if anything:
            baseline["knowledge_after"] = datetime.datetime.now().timestamp()
            log_row(repo, analysis_abs, label_from, label, diff, stats, items)
        write(repo, baseline_path, json.dumps(baseline, indent=0))
    page_for = pages_by_source(docs)
    all_sections = [(d, t, b, lvl) for d, text in docs.items() for t, lvl, b, _ in coverage.sections(text)]
    open_items = [i for i in items if is_open(i, now, docs, page_for, all_sections)]
    text = report(diff, stats, items, open_items, markers(docs), baseline, label, apply)
    write(repo, os.path.join(analysis_abs, "ledger", "delta.md"), text)
    return {"diff": diff, "stats": stats, "items": items, "open": open_items, "page_for": page_for, "docs": docs}


def print_summary(repo, analysis, result, applied, depth) -> None:
    diff, stats = result["diff"], result["stats"]
    functions = sum(len(d["changed"]) for d in diff["files"].values())
    print("files: %d changed, %d added, %d removed, %d renamed; functions changed: %d"
          % (len(diff["changed"]), len(diff["added"]), len(diff["removed"]), len(diff["renamed"]), functions))
    print("citations: %d %s, %d %s" % (stats["moved"] + stats.get("anchored", 0), "moved" if applied else "would move",
                                         stats["marked"], "marked for a recheck" if applied else "would be marked"))
    print("work items open: %d" % len(result["open"]))
    if stats.get("conflicted"):
        print("pages left untouched, they hold a merge conflict a person must resolve: " + ", ".join(stats["conflicted"]))
    print("wrote " + os.path.relpath(os.path.join(repo, analysis, "ledger", "delta.md"), repo))
    if applied:
        print("next: python3 -I %s --repo . --analysis %s --depth %s" % (os.path.join(HERE, "next.py"), analysis, depth))
    elif functions or diff["added"] or diff["removed"] or diff["renamed"] or diff["changed"]:
        print("next: run again with --apply")


if __name__ == "__main__":
    main()
