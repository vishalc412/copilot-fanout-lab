#!/usr/bin/env python3
"""Knowledge graph and knowledge base for agents, built from the code and the analysis.

Combines two sources:

  1. The code itself, freshly scanned (same scan as inventory.py): files, classes,
     functions, routes, imports and calls. These edges are computed, not written
     by a model, and each carries how it was resolved.
  2. The analysis pages: their front matter (component, reads, writes, calls,
     uses, config, exposes) and their sections, which become retrieval chunks.

Writes, inside <analysis>/knowledge/:

  graph.json         nodes and edges, with evidence and resolution per edge
  nodes.csv          the same nodes, for Neo4j, Memgraph or any graph tool
  edges.csv          the same edges
  chunks.jsonl       one retrieval chunk per page section, with metadata, for RAG
  symbol-index.json  every symbol and route -> file, lines, page, anchor, chunks
  README.md          what each file is and how an agent uses them

AGENT-CONTEXT.md, the short primer an agent loads first, is written by the analyst
from the template; this script does not write it.

Read-only on the repository. Standard library only. Never imports or runs
repository code.

  python3 -I <skill>/scripts/knowledge.py --repo . --analysis codebase-analysis
"""

from __future__ import annotations

import argparse
import csv
import datetime
import json
import os
import re
import sys

sys.dont_write_bytecode = True  # never leave __pycache__ inside the installed skill
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventory  # noqa: E402
import coverage  # noqa: E402

# Method names shared with built-in and standard-library types; a call `x.decode()` is far more
# often bytes.decode than the repository's own `decode`, so these are never matched by name alone.
COMMON_METHODS = set("""
get set put post delete patch head options update pop popitem clear copy keys values items setdefault
append extend insert remove index count sort reverse add discard union intersection difference
encode decode format split rsplit join strip lstrip rstrip replace lower upper title startswith endswith find rfind
read readline readlines write writelines close open flush seek tell send recv connect bind listen accept
load loads dump dumps parse run start stop wait cancel result submit map filter apply call execute
fetch fetchone fetchall fetchmany commit rollback cursor next iter group match search sub findall
info debug warning warn error exception critical log emit handle render save exists __init__ __call__
__enter__ __exit__ __str__ __repr__ __eq__ __hash__ __len__ __iter__ __next__ __getitem__ __setitem__ __contains__
toString equals hashCode valueOf then catch finally push shift unshift slice splice forEach reduce some every
""".split())

RELATIONS = ("reads", "writes", "calls", "uses", "config", "exposes", "publishes", "consumes", "depends_on")
MAX_CHUNK_CHARS = 6000  # about 1,500 tokens
CITE_FULL = re.compile(r"`([A-Za-z0-9_@+~./\\-]+\.[A-Za-z0-9_]+):(\d+)(?:\s*-\s*(\d+))?`")


def slug(title: str) -> str:
    """GitHub-style heading anchor."""
    text = re.sub(r"[`*~\[\]()<>]", "", title.strip().lower())
    text = re.sub(r"[^\w\- ]", "", text)
    return re.sub(r" ", "-", text)


class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self._edge_keys = set()

    def node(self, node_id: str, node_type: str, name: str, **attrs) -> str:
        current = self.nodes.get(node_id)
        if current is None:
            self.nodes[node_id] = dict({"id": node_id, "type": node_type, "name": name}, **attrs)
        else:
            for key, value in attrs.items():
                if value not in (None, "", []) and not current.get(key):
                    current[key] = value
        return node_id

    def edge(self, source: str, target: str, edge_type: str, evidence: str = "", resolution: str = "exact") -> None:
        key = (source, target, edge_type)
        if key in self._edge_keys:
            return
        self._edge_keys.add(key)
        self.edges.append({"source": source, "target": target, "type": edge_type,
                           "evidence": evidence, "resolution": resolution})


def module_candidates(module: str, from_file: str):
    """Python module name -> repository paths it may be."""
    if module.startswith("."):
        level = len(module) - len(module.lstrip("."))
        base = os.path.dirname(from_file)
        for _ in range(level - 1):
            base = os.path.dirname(base)
        rest = module.lstrip(".").replace(".", "/")
        stem = os.path.join(base, rest) if rest else base
        return [stem + ".py", os.path.join(stem, "__init__.py")]
    stem = module.replace(".", "/")
    return [stem + ".py", stem + "/__init__.py"]


def resolve_module(module: str, from_file: str, py_files):
    for candidate in module_candidates(module, from_file):
        candidate = os.path.normpath(candidate).replace(os.sep, "/")
        if candidate in py_files:
            return candidate
        matches = [p for p in py_files if p.endswith("/" + candidate) or p == candidate]
        if len(matches) == 1:
            return matches[0]
    return None


def build_code_graph(graph: Graph, files):
    py_files = {f["path"] for f in files if f["lang"] == "python"}
    symbol_id = {}
    by_name = {}
    for f in files:
        file_id = graph.node("file:" + f["path"], "File", os.path.basename(f["path"]), path=f["path"],
                             kind=f["kind"], lang=f["lang"] or "", lines=f["lines"])
        for s in f["symbols"]:
            if s["kind"] == "imports":
                continue
            sid = "symbol:%s#%s" % (f["path"], s["qualname"])
            symbol_id[(f["path"], s["qualname"])] = sid
            graph.node(sid, s["kind"].capitalize(), s["qualname"], path=f["path"], start=s["start"], end=s["end"],
                       branches=len(s.get("branches", [])), lang=f["lang"] or "")
            parent = s["qualname"].rsplit(".", 1)[0] if "." in s["qualname"] else None
            if parent and (f["path"], parent) in symbol_id:
                graph.edge(symbol_id[(f["path"], parent)], sid, "DEFINES", "%s:%d" % (f["path"], s["start"]))
            else:
                graph.edge(file_id, sid, "DEFINES", "%s:%d" % (f["path"], s["start"]))
            by_name.setdefault(s["name"], []).append(sid)
        for r in f["routes"]:
            rid = "route:%s %s" % ("/".join(r["methods"]), r["path"])
            graph.node(rid, "Route", "%s %s" % ("/".join(r["methods"]), r["path"]), path=f["path"], line=r["line"],
                       methods=r["methods"], route=r["path"])
            graph.edge(file_id, rid, "DECLARES", "%s:%d" % (f["path"], r["line"]))
            handler = (f["path"], r["handler"])
            if handler in symbol_id:
                graph.edge(rid, symbol_id[handler], "HANDLED_BY", "%s:%d" % (f["path"], r["line"]))

    unresolved = 0
    for f in files:
        imports = []
        for s in f["symbols"]:
            if s["kind"] == "imports":
                imports = s.get("imports", [])
        alias_module, alias_symbol = {}, {}
        for imp in imports:
            target = resolve_module(imp["module"], f["path"], py_files) if f["lang"] == "python" else None
            if imp["name"] is None:
                if target:
                    alias_module[imp["as"]] = target
            else:
                sub = resolve_module(imp["module"] + "." + imp["name"], f["path"], py_files) if not imp["module"].endswith(".") else None
                if sub:
                    alias_module[imp["as"]] = sub
                    target = target or sub
                elif target:
                    alias_symbol[imp["as"]] = (target, imp["name"])
            if target and target != f["path"]:
                graph.edge("file:" + f["path"], "file:" + target, "IMPORTS", "%s:%d" % (f["path"], imp["line"]))
        local = {s["name"]: s["qualname"] for s in f["symbols"] if s["kind"] not in ("imports",)}
        for s in f["symbols"]:
            if s["kind"] in ("class", "imports"):
                continue
            caller = symbol_id.get((f["path"], s["qualname"]))
            owner = s["qualname"].rsplit(".", 1)[0] if "." in s["qualname"] else None
            for call in s.get("calls", []):
                parts = call["name"].split(".")
                evidence = "%s:%d" % (f["path"], call["line"])
                target, resolution = None, None
                if len(parts) == 1 and parts[0] in local:
                    target, resolution = symbol_id.get((f["path"], local[parts[0]])), "same-file"
                elif len(parts) == 1 and parts[0] in alias_symbol:
                    path, name = alias_symbol[parts[0]]
                    target, resolution = symbol_id.get((path, name)), "import"
                elif len(parts) == 2 and parts[0] in ("self", "cls") and owner:
                    target, resolution = symbol_id.get((f["path"], owner + "." + parts[1])), "self"
                elif len(parts) >= 2 and parts[0] in alias_module:
                    path = alias_module[parts[0]]
                    target, resolution = symbol_id.get((path, ".".join(parts[1:]))), "import"
                elif len(parts) >= 2 and parts[0] in alias_symbol:
                    path, name = alias_symbol[parts[0]]
                    target, resolution = symbol_id.get((path, name + "." + parts[-1])), "import"
                if target is None and len(parts) >= 2 and parts[-1] not in COMMON_METHODS:
                    candidates = [c for c in by_name.get(parts[-1], []) if c != caller
                                  and graph.nodes[c].get("lang") == f["lang"] and graph.nodes[c]["type"] == "Method"]
                    if len(candidates) == 1:
                        target, resolution = candidates[0], "name-unique"
                if target and caller and target != caller:
                    graph.edge(caller, target, "CALLS", evidence, resolution)
                elif len(parts) >= 1 and parts[-1] in by_name:
                    unresolved += 1
    return symbol_id, unresolved


def subject_of(doc: str, meta: dict, graph: Graph) -> str:
    source = meta.get("source")
    sources = [source] if isinstance(source, str) else (source or [])
    if meta.get("kind") == "module" and sources and ("file:" + sources[0]) in graph.nodes:
        return "file:" + sources[0]
    if meta.get("kind") == "component" and meta.get("component"):
        return graph.node("component:" + meta["component"], "Component", meta["component"])
    return "page:" + doc


def build_doc_graph(graph: Graph, docs, page_for):
    for doc, text in sorted(docs.items()):
        meta = coverage.front_matter(text)
        page_id = graph.node("page:" + doc, "Page", doc, path=doc, kind=meta.get("kind", ""),
                             summary=meta.get("summary", ""))
        component = meta.get("component")
        if component:
            comp_id = graph.node("component:" + component, "Component", component)
            graph.edge(comp_id, page_id, "HAS_PAGE", doc, "analysis")
        source = meta.get("source")
        for path in ([source] if isinstance(source, str) else (source or [])):
            if ("file:" + path) in graph.nodes:
                graph.edge(page_id, "file:" + path, "DOCUMENTS", doc)
                if component:
                    graph.edge("component:" + component, "file:" + path, "CONTAINS", doc, "analysis")
        subject = subject_of(doc, meta, graph)
        for relation in RELATIONS:
            values = meta.get(relation, [])
            for value in ([values] if isinstance(values, str) else values):
                if not value:
                    continue
                node_type, _, name = value.partition(":")
                if not name:
                    node_type, name = "Thing", value
                if node_type == "file" and ("file:" + name) in graph.nodes:
                    target = "file:" + name
                elif node_type == "symbol":
                    found = [n["id"] for n in graph.nodes.values() if n["type"] in ("Function", "Method", "Class")
                             and (n["name"] == name or n["name"].endswith("." + name) or n["id"].endswith("#" + name))]
                    target = found[0] if len(found) == 1 else graph.node("symbol:" + name, "Symbol", name, unresolved=True)
                elif node_type in ("route", "component"):
                    target = graph.node("%s:%s" % (node_type, name), node_type.capitalize(), name)
                else:
                    target = graph.node("%s:%s" % (node_type.lower(), name), node_type.capitalize(), name)
                graph.edge(subject, target, relation.upper(), doc, "analysis")
    for path, pages in page_for.items():
        for doc in pages:
            if ("file:" + path) in graph.nodes:
                graph.edge("page:" + doc, "file:" + path, "DOCUMENTS", doc)


def chunk_docs(docs, known_symbols):
    chunks = []
    for doc, text in sorted(docs.items()):
        meta = coverage.front_matter(text)
        body = coverage.FRONT_MATTER.sub("", text, count=1)
        lines = body.splitlines()
        marks, in_fence = [], False
        for index, line in enumerate(lines):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            match = None if in_fence else coverage.HEADING.match(line)
            if match and len(match.group(1)) <= 3:
                marks.append((index, len(match.group(1)), match.group(2)))
        if not marks or marks[0][0] > 0:
            marks.insert(0, (0, 0, meta.get("id", doc)))
        trail, used = {}, {}
        for position, (index, level, title) in enumerate(marks):
            end = marks[position + 1][0] if position + 1 < len(marks) else len(lines)
            trail = {k: v for k, v in trail.items() if k < level}
            trail[level] = title
            section = "\n".join(lines[index:end]).strip()
            if not section:
                continue
            pieces = [section]
            if len(section) > MAX_CHUNK_CHARS:
                pieces, current = [], ""
                for paragraph in re.split(r"\n\s*\n", section):
                    if current and len(current) + len(paragraph) > MAX_CHUNK_CHARS:
                        pieces.append(current)
                        current = ""
                    current = (current + "\n\n" + paragraph).strip()
                if current:
                    pieces.append(current)
            for part_no, piece in enumerate(pieces, 1):
                cited = sorted({coverage.strip_dot(m.group(1)) for m in CITE_FULL.finditer(piece)})
                named = sorted({t for t in re.findall(r"`([A-Za-z_][\w.]*)", piece) if t.split(".")[-1] in known_symbols})
                anchor = slug(title) if level else ""
                if part_no == 1 and level:
                    seen = used.get(anchor, 0)
                    used[anchor] = seen + 1
                    if seen:
                        anchor = "%s-%d" % (anchor, seen)  # GitHub numbers repeated headings
                    section_anchor = anchor
                elif level:
                    anchor = section_anchor
                chunks.append({
                    "id": "%s#%s%s" % (doc, anchor, "" if len(pieces) == 1 else "-part%d" % part_no),
                    "doc": doc,
                    "anchor": anchor,
                    "heading_path": [trail[k] for k in sorted(trail) if k > 0],
                    "kind": meta.get("kind", "page"),
                    "component": meta.get("component", ""),
                    "source_files": cited,
                    "symbols": named[:50],
                    "tokens_estimate": len(piece) // 4,
                    "text": piece,
                })
    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--analysis", default="codebase-analysis")
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()

    repo = os.path.abspath(args.repo)
    if os.path.isabs(args.analysis) or ".." in args.analysis.split("/") or args.analysis.strip("/") in ("", "."):
        inventory.fail("--analysis must be a folder inside the repository, given relative to it")
    analysis_abs = os.path.join(repo, args.analysis)
    if not os.path.isdir(analysis_abs):
        inventory.fail("analysis folder not found: " + args.analysis)
    out_dir = os.path.join(analysis_abs, "knowledge")
    targets = {name: inventory.safe_target(repo, os.path.join(out_dir, name))
               for name in ("graph.json", "nodes.csv", "edges.csv", "chunks.jsonl", "symbol-index.json", "README.md")}
    os.makedirs(out_dir, exist_ok=True)

    files, _excluded = inventory.scan(repo, args.analysis, [e.strip("/") for e in args.exclude])
    docs = coverage.load_docs(analysis_abs)
    docs = {k: v for k, v in docs.items() if not k.startswith("knowledge/README")}

    page_for = {}
    for doc, text in docs.items():
        declared = coverage.front_matter(text).get("source", [])
        for path in ([declared] if isinstance(declared, str) else declared):
            if path:
                page_for.setdefault(coverage.strip_dot(path.strip("`")), []).append(doc)
        for decl in coverage.SOURCE_DECL.findall(text):
            for token in coverage.BACKTICK.findall(decl):
                page_for.setdefault(coverage.strip_dot(token.split(":")[0].strip()), []).append(doc)

    graph = Graph()
    symbol_id, unresolved = build_code_graph(graph, files)
    build_doc_graph(graph, docs, page_for)

    known = {s["name"] for f in files for s in f["symbols"] if s["kind"] != "imports"}
    chunks = chunk_docs(docs, known)

    # Symbol index: where each symbol and route is defined, documented and chunked.
    index = {"symbols": {}, "routes": {}}
    chunks_by_symbol = {}
    for chunk in chunks:
        for name in chunk["symbols"]:
            chunks_by_symbol.setdefault(name.split(".")[-1], []).append(chunk["id"])
    chunks_by_doc = {}
    for chunk in chunks:
        chunks_by_doc.setdefault(chunk["doc"], []).append(chunk)
    page_chunks = {path: [c for doc in sorted(set(docs_)) for c in chunks_by_doc.get(doc, [])]
                   for path, docs_ in page_for.items()}
    for f in files:
        pages = sorted(set(page_for.get(f["path"], [])))
        for s in f["symbols"]:
            if s["kind"] == "imports":
                continue
            title_pattern = coverage.card_title_pattern(s, f["symbols"])
            exact = coverage.name_pattern(s["qualname"])
            own = [c for c in page_chunks.get(f["path"], [])]
            card = [c["id"] for c in own if c["heading_path"] and exact.search(c["heading_path"][-1])] or \
                   [c["id"] for c in own if c["heading_path"] and title_pattern.search(c["heading_path"][-1])]
            index["symbols"][symbol_id[(f["path"], s["qualname"])]] = {
                "name": s["qualname"], "kind": s["kind"], "file": f["path"], "lines": [s["start"], s["end"]],
                "pages": pages, "card": card[:3], "chunks": sorted(set(chunks_by_symbol.get(s["name"], [])))[:20]}
        for r in f["routes"]:
            rid = "route:%s %s" % ("/".join(r["methods"]), r["path"])
            pattern = re.compile(re.escape(r["path"].rstrip("/") or "/") + r"/?(?![\w/{<-])")
            index["routes"][rid] = {"file": f["path"], "line": r["line"], "handler": r["handler"],
                                    "card": [c["id"] for c in chunks if pattern.search(" ".join(c["heading_path"]))][:3]}

    stats = {"nodes": len(graph.nodes), "edges": len(graph.edges), "chunks": len(chunks),
             "calls_unresolved": unresolved, "by_node_type": {}, "by_edge_type": {}, "by_resolution": {}}
    for node in graph.nodes.values():
        stats["by_node_type"][node["type"]] = stats["by_node_type"].get(node["type"], 0) + 1
    for edge in graph.edges:
        stats["by_edge_type"][edge["type"]] = stats["by_edge_type"].get(edge["type"], 0) + 1
        stats["by_resolution"][edge["resolution"]] = stats["by_resolution"].get(edge["resolution"], 0) + 1
    generated = datetime.datetime.now().isoformat(timespec="seconds")

    with open(targets["graph.json"], "w", encoding="utf-8") as handle:
        json.dump({"generated": generated, "tool": "analyzing-a-codebase/scripts/knowledge.py 1.5.0", "stats": stats,
                   "nodes": sorted(graph.nodes.values(), key=lambda n: n["id"]), "edges": graph.edges}, handle, indent=1)
    node_fields = ["id", "type", "name", "path", "kind", "lang", "lines", "start", "end", "line", "branches", "summary"]
    with open(targets["nodes.csv"], "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=node_fields, extrasaction="ignore")
        writer.writeheader()
        for node in sorted(graph.nodes.values(), key=lambda n: n["id"]):
            writer.writerow(node)
    with open(targets["edges.csv"], "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source", "target", "type", "resolution", "evidence"])
        writer.writeheader()
        for edge in graph.edges:
            writer.writerow(edge)
    with open(targets["chunks.jsonl"], "w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    with open(targets["symbol-index.json"], "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=1)

    readme = ["# Knowledge graph and knowledge base", "",
              "Generated by `knowledge.py` on %s. Do not edit; re-run the script after the analysis changes." % generated, "",
              "| Measure | Count |", "| --- | --- |",
              "| Nodes | %d |" % stats["nodes"], "| Edges | %d |" % stats["edges"], "| Chunks | %d |" % stats["chunks"],
              "| Calls the script could not resolve to one symbol | %d |" % unresolved, ""] + \
             (["## Front-matter names that match no symbol", ""] +
              ["- `%s` (from %s)" % (n["name"], ", ".join(sorted({e["evidence"] for e in graph.edges if e["target"] == n["id"]})))
               for n in sorted(graph.nodes.values(), key=lambda n: n["id"]) if n.get("unresolved")] + [""]
              if any(n.get("unresolved") for n in graph.nodes.values()) else []) + [
              "| Node type | Count |", "| --- | --- |"] + \
             ["| %s | %d |" % kv for kv in sorted(stats["by_node_type"].items())] + \
             ["", "| Edge type | Count |", "| --- | --- |"] + \
             ["| %s | %d |" % kv for kv in sorted(stats["by_edge_type"].items())] + \
             ["", "| Edge resolution | Meaning | Count |", "| --- | --- | --- |"] + \
             ["| %s | %s | %d |" % (k, {
                 "exact": "structural fact from the parser (defines, declares, imports)",
                 "same-file": "call to a function of the same file, by name",
                 "self": "call to a method of the same class through self or cls",
                 "import": "call resolved through an import statement",
                 "name-unique": "method call matched to the only symbol of that name in the repository; check before relying on it",
                 "analysis": "written in the analysis page's front matter by the analyst; verified only as far as the analysis was"}.get(k, ""), v)
              for k, v in sorted(stats["by_resolution"].items())] + \
             ["", "## Files", "",
              "| File | What it is | Use it to |", "| --- | --- | --- |",
              "| `AGENT-CONTEXT.md` | The primer, written by the analyst | Load first into every agent's context |",
              "| `symbol-index.json` | Symbol and route -> file, lines, page, card chunk | Jump from a name in a question or a stack trace to its card |",
              "| `chunks.jsonl` | One chunk per page section, about 1,500 tokens at most, with heading path, component, kind, files cited and symbols named | Embed into a vector store for retrieval |",
              "| `graph.json` | Nodes and edges with evidence and resolution | Walk callers, callees, routes, components, data and outside systems |",
              "| `nodes.csv`, `edges.csv` | The same graph as tables | Load into Neo4j, Memgraph, NetworkX or a spreadsheet |",
              "",
              "## How an agent should use it", "",
              "1. Put `AGENT-CONTEXT.md` in the system prompt or the first message.",
              "2. For a question naming a function, route or file, look it up in `symbol-index.json` and read its card chunk.",
              "3. For a broader question, retrieve from `chunks.jsonl` by similarity, filtered by `component` or `kind` when the question names one.",
              "4. For impact questions (\"what breaks if I change X\"), walk `CALLS`, `HANDLED_BY`, `READS` and `WRITES` edges in `graph.json` from X, then read the cards of what you reach.",
              "5. Before acting on any statement, open the cited `path:line` in the repository: the code is the source of truth, and edges marked `name-unique` or `analysis` are leads.",
              "",
              "Neo4j, from the folder holding the CSV files:", "",
              "```text",
              "LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS r CREATE (:Node {id: r.id, type: r.type, name: r.name, path: r.path});",
              "CREATE INDEX FOR (n:Node) ON (n.id);",
              "LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS r MATCH (a:Node {id: r.source}), (b:Node {id: r.target})",
              "  CREATE (a)-[:REL {type: r.type, resolution: r.resolution, evidence: r.evidence}]->(b);",
              "```", ""]
    with open(targets["README.md"], "w", encoding="utf-8") as handle:
        handle.write("\n".join(readme))

    print("ok: %d nodes, %d edges, %d chunks, %d unresolved calls" % (stats["nodes"], stats["edges"], stats["chunks"], unresolved))
    for name in targets:
        print("wrote " + os.path.relpath(targets[name], repo))


if __name__ == "__main__":
    main()
