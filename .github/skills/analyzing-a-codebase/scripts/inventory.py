#!/usr/bin/env python3
"""Inventory of a repository: every file, every class and function, every route.

Read-only on the repository. Writes two files inside the analysis folder:

  <analysis>/ledger/inventory.json      machine-readable, used by coverage.py
  <analysis>/ledger/symbol-checklist.md the work list: one row per file and symbol

Run isolated, from anywhere:

  python3 -I <skill>/scripts/inventory.py --repo . --analysis codebase-analysis

Standard library only. Python 3.9 or later. Makes no network connection and
runs nothing from the repository: Python files are parsed with `ast`, never
imported; other languages are read with regular expressions.
"""

from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import os
import re
import sys

EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "bower_components", "vendor",
    "third_party", "dist", "build", "target", "out", "bin", "obj", ".venv",
    "venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache", ".tox",
    ".idea", ".vscode", "coverage", ".next", ".nuxt", ".angular", ".gradle",
    ".terraform", "site-packages", ".remember", ".crib", ".migration-toolkit-backups",
}
TOOLKIT_FILES = {".DS_Store", ".migration-toolkit-version"}  # written by the OS and by this toolkit's installer

# The toolkit's own skills, wherever an assistant installed them, are not the system.
TOOLKIT_SKILLS = {
    "analyzing-a-codebase", "verifying-a-codebase-analysis",
    "reviewing-codebase-shortcomings", "migrating-http-to-https",
    "migrating-service-calls-to-tls", "verifying-a-tls-migration",
    "analyzing-a-remote-repository", "assessing-change-impact", "tracking-codebase-changes",
}

SOURCE_LANG = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript",
    ".cjs": "javascript", ".ts": "typescript", ".tsx": "typescript", ".vue": "vue",
    ".svelte": "svelte", ".java": "java", ".kt": "kotlin", ".kts": "kotlin",
    ".scala": "scala", ".groovy": "groovy", ".cs": "csharp", ".vb": "vbnet",
    ".go": "go", ".rb": "ruby", ".php": "php", ".pl": "perl", ".pm": "perl",
    ".rs": "rust", ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
    ".swift": "swift", ".m": "objc", ".sh": "shell", ".bash": "shell", ".ps1": "powershell",
    ".sql": "sql", ".cbl": "cobol", ".cob": "cobol", ".esql": "esql", ".html": "html",
    ".htm": "html", ".css": "css", ".scss": "css", ".less": "css",
}
CONFIG_EXT = {".yml", ".yaml", ".json", ".xml", ".properties", ".ini", ".cfg", ".conf",
              ".toml", ".env", ".config", ".tf", ".tfvars", ".hcl"}
DATA_EXT = {".xlsx", ".xls", ".xlsm", ".csv", ".tsv", ".db", ".sqlite", ".sqlite3", ".parquet"}
DOC_EXT = {".md", ".rst", ".txt", ".adoc", ".pdf", ".docx", ".pptx"}
BUILD_NAMES = {"pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle", "package.json",
               "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg", "pipfile",
               "go.mod", "cargo.toml", "gemfile", "composer.json", "makefile", "cmakelists.txt"}
DEPLOY_HINTS = ("dockerfile", "docker-compose", "jenkinsfile", "procfile", ".gitlab-ci",
                "azure-pipelines", "helm", "chart.yaml", "values", "k8s", "kubernetes",
                "deployment", "ingress", "service.yaml", "configmap", "cloudbuild", "skaffold")

MAX_FILE_BYTES = 5 * 1024 * 1024


def fail(message: str, code: int = 2) -> None:
    print("error: " + message, file=sys.stderr)
    sys.exit(code)


def safe_target(repo: str, path: str) -> str:
    """Refuse to write through a symbolic link or outside the repository."""
    base = os.path.abspath(repo)
    full = os.path.abspath(path)
    rel = os.path.relpath(full, base)
    if rel == os.curdir or rel.startswith(os.pardir):
        fail("output must stay inside the repository: " + path)
    current = base
    for part in rel.split(os.sep):
        current = os.path.join(current, part)
        if os.path.islink(current):
            fail("refusing to write through a symbolic link: " + current)
    return full


def classify(rel: str) -> tuple:
    name = os.path.basename(rel).lower()
    ext = os.path.splitext(name)[1]
    low = rel.lower()
    if name in BUILD_NAMES:
        return "build", None
    if name.startswith("dockerfile") or name == "jenkinsfile" or any(h in low for h in DEPLOY_HINTS) and ext in CONFIG_EXT | {""}:
        return "deploy", None
    if ext in SOURCE_LANG:
        return "source", SOURCE_LANG[ext]
    if ext in CONFIG_EXT:
        return "config", None
    if ext in DATA_EXT:
        return "data", None
    if ext in DOC_EXT:
        return "doc", None
    return "other", None


def read_text(full: str):
    try:
        if os.path.getsize(full) > MAX_FILE_BYTES:
            return None
        with open(full, "rb") as handle:
            raw = handle.read()
    except OSError:
        return None
    return decode(raw)


def decode(raw: bytes):
    """Text of a file's bytes, or None for binary and oversized content."""
    if len(raw) > MAX_FILE_BYTES or b"\x00" in raw[:8192]:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")  # older code bases; every byte maps, line numbers stay right


# ---------- fingerprints (delta updates, card stamps) ----------

def text_lines(text: str):
    """Lines as editors and citations number them: split on newline only, drop the final empty line."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [line[:-1] if line.endswith("\r") else line for line in lines]


def normalize_line(line: str) -> str:
    """The form of a line that is fingerprinted: two lines with the same form are "unchanged".

    This decides what a delta update treats as a code change. A line that normalizes the
    same before and after keeps its card and its citations; anything else makes the card stale.
    """
    return line.rstrip()


def line_hashes(text: str):
    """A short fingerprint per line. Not the content: the baseline never stores code."""
    return [hashlib.sha256(normalize_line(line).encode("utf-8", "replace")).hexdigest()[:10]
            for line in text_lines(text)]


def stamp(hashes, start: int, end: int) -> str:
    """Fingerprint of lines start..end, written into a card as <!-- code: <stamp> -->."""
    return hashlib.sha256(" ".join(hashes[max(start, 1) - 1:end]).encode("ascii")).hexdigest()[:12]


# ---------- Python ----------

ROUTE_ATTRS = {"route", "get", "post", "put", "delete", "patch", "api_route", "websocket"}


def _decorator_name(node: ast.AST) -> str:
    target = node.func if isinstance(node, ast.Call) else node
    parts = []
    while isinstance(target, ast.Attribute):
        parts.append(target.attr)
        target = target.value
    if isinstance(target, ast.Name):
        parts.append(target.id)
    return ".".join(reversed(parts))


def _route_from_decorator(dec: ast.AST):
    if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
        return None
    attr = dec.func.attr
    if attr not in ROUTE_ATTRS:
        return None
    if not dec.args or not isinstance(dec.args[0], ast.Constant) or not isinstance(dec.args[0].value, str):
        return None
    path = dec.args[0].value
    methods = []
    if attr == "route" or attr == "api_route":
        for kw in dec.keywords:
            if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple, ast.Set)):
                methods = [e.value.upper() for e in kw.value.elts
                           if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        methods = methods or ["GET"]
    else:
        methods = [attr.upper()]
    return {"methods": methods, "path": path}


BRANCH_NODES = [(ast.If, "if"), (ast.IfExp, "ternary"), (ast.For, "loop"), (ast.AsyncFor, "loop"),
                (ast.While, "loop"), (ast.ExceptHandler, "except"), (ast.Raise, "raise")]
if hasattr(ast, "Match"):
    BRANCH_NODES.append((ast.match_case, "case"))


def _call_name(func: ast.AST) -> str:
    """`helper`, `self.record`, `audit.record`, `requests.post` -> the dotted name as written."""
    parts = []
    while isinstance(func, ast.Attribute):
        parts.append(func.attr)
        func = func.value
    if isinstance(func, ast.Name):
        parts.append(func.id)
    elif isinstance(func, ast.Call):
        parts.append("()")
    return ".".join(reversed(parts))


def _branches_and_calls(node: ast.AST):
    branches, calls, seen = [], [], set()
    walked = [child for statement in node.body for child in ast.walk(statement)]  # decorators are not calls of the body
    for child in walked:
        for cls, kind in BRANCH_NODES:
            if isinstance(child, cls) and hasattr(child, "lineno"):
                if kind == "if" and getattr(child, "_elif", False):
                    kind = "elif"
                detail = ""
                if kind == "except":
                    detail = _call_name(child.type) if child.type is not None else "any exception"
                branches.append({"kind": kind, "line": child.lineno, "detail": detail})
                if isinstance(child, ast.If) and len(child.orelse) == 1 and isinstance(child.orelse[0], ast.If):
                    child.orelse[0]._elif = True
        if isinstance(child, ast.Call):
            name = _call_name(child.func)
            if name and name not in seen:
                seen.add(name)
                calls.append({"name": name, "line": child.lineno})
    branches.sort(key=lambda b: (b["line"], b["kind"]))
    return branches, calls


def python_imports(tree: ast.AST):
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"module": alias.name, "name": None, "as": alias.asname or alias.name.split(".")[0], "line": node.lineno})
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports.append({"module": ("." * node.level) + (node.module or ""), "name": alias.name,
                                "as": alias.asname or alias.name, "line": node.lineno})
    return imports


def python_symbols(text: str):
    symbols, routes = [], []
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        return symbols, routes, "python parse error at line %s" % exc.lineno

    def visit(body, prefix, depth):
        for node in body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start = min([node.lineno] + [d.lineno for d in node.decorator_list])
                end = getattr(node, "end_lineno", None) or node.lineno
                kind = "class" if isinstance(node, ast.ClassDef) else ("method" if prefix else "function")
                qual = prefix + node.name
                decorators = [_decorator_name(d) for d in node.decorator_list]
                entry = {"name": node.name, "qualname": qual, "kind": kind,
                         "start": start, "end": end, "size": end - start + 1,
                         "decorators": decorators}
                if kind != "class":
                    entry["branches"], entry["calls"] = _branches_and_calls(node)
                symbols.append(entry)
                for dec in node.decorator_list:
                    route = _route_from_decorator(dec)
                    if route:
                        route.update({"handler": qual, "line": dec.lineno})
                        routes.append(route)
                if isinstance(node, ast.ClassDef) and depth < 2:
                    visit(node.body, qual + ".", depth + 1)
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                call = node.value
                if isinstance(call.func, ast.Attribute) and call.func.attr == "add_url_rule" and call.args:
                    first = call.args[0]
                    if isinstance(first, ast.Constant) and isinstance(first.value, str):
                        routes.append({"methods": ["GET"], "path": first.value,
                                       "handler": "(add_url_rule)", "line": node.lineno})

    visit(tree.body, "", 0)
    symbols.append({"name": "(imports)", "qualname": "(imports)", "kind": "imports", "start": 0, "end": 0,
                    "size": 0, "decorators": [], "imports": python_imports(tree)})
    return symbols, routes, None


# ---------- other languages (regular expressions; end lines are approximate) ----------

KEYWORDS = {"if", "for", "while", "switch", "catch", "return", "else", "new", "function",
            "elif", "with", "try", "do", "foreach", "using", "lock", "typeof", "sizeof"}

LANG_PATTERNS = {
    "java": [
        ("class", re.compile(r"^\s*(?:public|private|protected|abstract|final|static|\s)*(?:class|interface|enum|record)\s+(\w+)")),
        ("method", re.compile(r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:public|private|protected)\s+(?:static\s+|final\s+|synchronized\s+|abstract\s+|default\s+)*[\w<>\[\],.? ]+\s+(\w+)\s*\(")),
        ("constructor", re.compile(r"^\s*(?:public|private|protected)?\s*([A-Z]\w*)\s*\([^;]*\)\s*(?:throws\s+[\w.,\s]+)?\{?\s*$")),
        ("method", re.compile(r"^\s{2,}(?:static\s+|final\s+|synchronized\s+)*(?!return\b|new\b|else\b|throw\b)[A-Za-z_][\w<>\[\],.?]*\s+(\w+)\s*\([^;]*\)\s*(?:throws\s+[\w.,\s]+)?\{\s*$")),
    ],
    "kotlin": [
        ("class", re.compile(r"^\s*(?:data\s+|sealed\s+|open\s+|abstract\s+|enum\s+)*(?:class|interface|object)\s+(\w+)")),
        ("function", re.compile(r"^\s*(?:override\s+|private\s+|public\s+|internal\s+|suspend\s+)*fun\s+(?:<[^>]+>\s*)?(?:[\w.]+\.)?(\w+)\s*\(")),
    ],
    "csharp": [
        ("class", re.compile(r"^\s*(?:public|private|internal|protected|static|sealed|abstract|partial|\s)*(?:class|interface|record|struct|enum)\s+(\w+)")),
        ("method", re.compile(r"^\s*(?:public|private|protected|internal)\s+(?:static\s+|async\s+|virtual\s+|override\s+|abstract\s+)*[\w<>\[\],.? ]+\s+(\w+)\s*\(")),
    ],
    "javascript": [
        ("class", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?class\s+(\w+)")),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*(\w+)\s*\(")),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|\w+)\s*=>")),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\b")),
        ("method", re.compile(r"^\s{2,}(?:static\s+|async\s+|public\s+|private\s+|protected\s+|readonly\s+)*(\w+)\s*\([^;]*\)\s*(?::\s*[\w<>\[\]|, .]+)?\s*\{\s*$")),
    ],
    "go": [
        ("function", re.compile(r"^func\s+(?:\([^)]*\)\s*)?(\w+)\s*\(")),
        ("class", re.compile(r"^type\s+(\w+)\s+(?:struct|interface)\b")),
    ],
    "ruby": [
        ("class", re.compile(r"^\s*(?:class|module)\s+([A-Z]\w*)")),
        ("method", re.compile(r"^\s*def\s+(?:self\.)?(\w+[?!]?)")),
    ],
    "php": [
        ("class", re.compile(r"^\s*(?:abstract\s+|final\s+)?(?:class|interface|trait)\s+(\w+)")),
        ("function", re.compile(r"^\s*(?:public\s+|private\s+|protected\s+|static\s+)*function\s+(\w+)\s*\(")),
    ],
    "perl": [("function", re.compile(r"^\s*sub\s+(\w+)"))],
    "shell": [("function", re.compile(r"^\s*(?:function\s+)?(\w[\w-]*)\s*\(\)\s*\{"))],
    "powershell": [("function", re.compile(r"^\s*function\s+([\w-]+)", re.I))],
    "rust": [
        ("function", re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+(\w+)")),
        ("class", re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait)\s+(\w+)")),
    ],
    "groovy": [("function", re.compile(r"^\s*(?:def|void|String|boolean|int)\s+(\w+)\s*\("))],
    "sql": [
        ("table", re.compile(r"^\s*create\s+(?:or\s+replace\s+)?(?:global\s+temporary\s+)?table\s+(?:if\s+not\s+exists\s+)?([\w.\"\[\]]+)", re.I)),
        ("view", re.compile(r"^\s*create\s+(?:or\s+replace\s+)?view\s+([\w.\"\[\]]+)", re.I)),
        ("procedure", re.compile(r"^\s*create\s+(?:or\s+replace\s+)?(?:procedure|function|trigger|package)\s+([\w.\"\[\]]+)", re.I)),
    ],
    "cobol": [("paragraph", re.compile(r"^.{7}([A-Z0-9][A-Z0-9-]+)\.\s*$"))],
    "esql": [("function", re.compile(r"^\s*CREATE\s+(?:COMPUTE\s+|DATABASE\s+|FILTER\s+)?(?:MODULE|FUNCTION|PROCEDURE)\s+(\w+)", re.I))],
}
LANG_PATTERNS["python"] = [  # only when ast cannot parse the file (Python 2, syntax errors)
    ("class", re.compile(r"^\s*class\s+(\w+)")),
    ("function", re.compile(r"^\s*(?:async\s+)?def\s+(\w+)\s*\(")),
]
LANG_PATTERNS["typescript"] = LANG_PATTERNS["javascript"]
LANG_PATTERNS["vue"] = LANG_PATTERNS["javascript"]
LANG_PATTERNS["svelte"] = LANG_PATTERNS["javascript"]
LANG_PATTERNS["scala"] = LANG_PATTERNS["kotlin"]

ROUTE_PATTERNS = [
    # Express, Koa, Fastify, Hono: app.get('/x'), router.post("/y")
    (re.compile(r"\b(?:app|router|server|fastify|route[rs]?)\.(get|post|put|delete|patch|all)\(\s*['\"`]([^'\"`]+)['\"`]", re.I), None),
    # Spring, with a path, and bare (the class prefix only)
    (re.compile(r"@(Get|Post|Put|Delete|Patch|Request)Mapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?\{?\s*\"([^\"]*)\""), None),
    (re.compile(r"@(Get|Post|Put|Delete|Patch)Mapping()(?!\s*\()"), None),
    # ASP.NET
    (re.compile(r"\[Http(Get|Post|Put|Delete|Patch)\s*\(\s*\"([^\"]*)\""), None),
    (re.compile(r"\.Map(Get|Post|Put|Delete|Patch)\s*\(\s*\"([^\"]*)\""), None),
    # Go net/http, gin, echo, chi
    (re.compile(r"\.(GET|POST|PUT|DELETE|PATCH|HandleFunc|Handle)\(\s*\"([^\"]+)\""), None),
    # Angular / React router
    (re.compile(r"\bpath\s*:\s*['\"]([^'\"]*)['\"]"), "ui"),
    (re.compile(r"<Route\s+[^>]*path=['\"{]+([^'\"}]+)"), "ui"),
]
BRANCH_LINE = re.compile(r"^\s*\}?\s*(else if|elif|if|unless|catch|except|rescue|switch|case|when|for|foreach|while|throw|raise)\b", re.I)
CALL_TOKEN = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
CLASS_PREFIX = re.compile(r"@RequestMapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?\"([^\"]*)\"")


def regex_symbols(text: str, lang: str):
    symbols, routes = [], []
    lines = text.splitlines()
    patterns = LANG_PATTERNS.get(lang, [])
    for number, line in enumerate(lines, 1):
        for kind, pattern in patterns:
            match = pattern.match(line)
            if not match:
                continue
            name = match.group(1).strip('"[]')
            if name in KEYWORDS or name.isdigit():
                continue
            symbols.append({"name": name, "qualname": name, "kind": kind, "start": number,
                            "end": None, "size": None, "decorators": [], "approximate": True})
            break
    # End line approximated as the line before the next symbol at the same or lower indentation.
    names = {s["name"] for s in symbols if s["kind"] not in ("class", "table", "view")}
    for index, symbol in enumerate(symbols):
        nxt = symbols[index + 1]["start"] - 1 if index + 1 < len(symbols) else len(lines)
        symbol["end"] = max(symbol["start"], nxt)
        symbol["size"] = symbol["end"] - symbol["start"] + 1
        if symbol["kind"] in ("class", "table", "view", "paragraph"):
            continue
        branches, calls, seen = [], [], set()
        for number in range(symbol["start"] + 1, symbol["end"] + 1):
            line = lines[number - 1]
            match = BRANCH_LINE.match(line)
            if match:
                branches.append({"kind": match.group(1).replace("else if", "elif").lower(), "line": number, "detail": ""})
            for call in CALL_TOKEN.findall(line):
                if call in names and call != symbol["name"] and call not in seen:
                    seen.add(call)
                    calls.append({"name": call, "line": number})
        symbol["branches"], symbol["calls"] = branches, calls
    class_prefix = ""
    for number, line in enumerate(lines, 1):
        prefix_match = CLASS_PREFIX.search(line)
        if prefix_match and re.search(r"\bclass\b", " ".join(lines[number:number + 4])):
            class_prefix = prefix_match.group(1).rstrip("/")
            continue
        for pattern, flavour in ROUTE_PATTERNS:
            for match in pattern.finditer(line):
                if flavour == "ui":
                    routes.append({"methods": ["UI"], "path": match.group(1), "handler": "", "line": number})
                    continue
                method, path = match.group(1).upper(), match.group(2)
                if method in ("REQUEST", "HANDLEFUNC", "HANDLE", "ALL"):
                    method = "ANY"
                if pattern.pattern.startswith("@(Get"):
                    path = class_prefix + ("/" + path.lstrip("/") if path else "")
                tail = line[match.end():]
                inline = "=>" in tail or re.search(r"\bfunc(?:tion)?\s*\(", tail) is not None
                routes.append({"methods": [method], "path": path or "/", "handler": "(inline)" if inline else "",
                               "line": number})
    for route in routes:
        if route["methods"] == ["UI"] or route["handler"] == "(inline)":
            continue
        owner = [s for s in symbols if s["start"] >= route["line"] and s["kind"] != "class"]
        route["handler"] = owner[0]["qualname"] if owner and owner[0]["start"] - route["line"] <= 3 else ""
    return symbols, routes, None


def scan(repo: str, analysis_rel: str, extra_excludes):
    extra_excludes = [e.replace("\\", "/").strip("/") for e in extra_excludes]  # Windows users type .github\skills
    analysis_rel = analysis_rel.replace("\\", "/")
    repo = os.path.abspath(repo)
    analysis_abs = os.path.abspath(os.path.join(repo, analysis_rel))
    files, excluded = [], []
    for root, dirs, names in os.walk(repo, followlinks=False):
        rel_root = os.path.relpath(root, repo)
        keep = []
        for d in sorted(dirs):
            full = os.path.join(root, d)
            rel = os.path.normpath(os.path.join(rel_root, d)).replace(os.sep, "/")
            reason = None
            if d in EXCLUDED_DIRS:
                reason = "generated, vendored or tool folder"
            elif d in TOOLKIT_SKILLS and os.path.basename(root) == "skills":
                reason = "this toolkit"
            elif os.path.abspath(full) == analysis_abs:
                reason = "the analysis output"
            elif os.path.islink(full):
                reason = "symbolic link, not followed"
            elif any(rel == e or rel.startswith(e + "/") for e in extra_excludes):
                reason = "excluded by the user"
            if reason:
                excluded.append({"path": rel.replace(os.sep, "/"), "reason": reason})
            else:
                keep.append(d)
        dirs[:] = keep
        for name in sorted(names):
            full = os.path.join(root, name)
            if os.path.islink(full) or name in TOOLKIT_FILES:
                continue
            rel = os.path.normpath(os.path.join(rel_root, name)).replace(os.sep, "/")
            files.append(file_entry(rel, read_text(full)))
    return files, excluded


def file_entry(rel: str, text):
    """Kind, language, line count, symbols and routes of one file; text is None for binary content."""
    kind, lang = classify(rel)
    entry = {"path": rel, "kind": kind, "lang": lang, "binary": text is None,
             "lines": 0 if text is None else text.count("\n") + (0 if text.endswith("\n") or not text else 1),
             "symbols": [], "routes": []}
    if text is not None and kind in ("source", "deploy", "build"):
        if lang == "python":
            symbols, routes, note = python_symbols(text)
            if note:
                symbols, routes, _ = regex_symbols(text, "python")
                note += "; functions found by pattern instead, end lines approximate"
        else:
            symbols, routes, note = regex_symbols(text, lang or "")
        entry["symbols"], entry["routes"] = symbols, routes
        if note:
            entry["note"] = note
    return entry


def in_scope(rel: str, analysis_rel: str, extra_excludes) -> bool:
    """The rule scan() applies while walking, for a path known only by name (a file in an older commit)."""
    parts = rel.split("/")
    analysis_rel = analysis_rel.replace("\\", "/").strip("/")
    if rel == analysis_rel or rel.startswith(analysis_rel + "/") or parts[-1] in TOOLKIT_FILES:
        return False
    for i, part in enumerate(parts[:-1]):
        if part in EXCLUDED_DIRS or (part in TOOLKIT_SKILLS and i > 0 and parts[i - 1] == "skills"):
            return False
    extra = [e.replace("\\", "/").strip("/") for e in extra_excludes]
    return not any(rel == e or rel.startswith(e + "/") for e in extra)


def write_outputs(repo: str, analysis_rel: str, files, excluded) -> tuple:
    ledger = os.path.join(repo, analysis_rel, "ledger")
    json_path = safe_target(repo, os.path.join(ledger, "inventory.json"))
    md_path = safe_target(repo, os.path.join(ledger, "symbol-checklist.md"))
    os.makedirs(ledger, exist_ok=True)
    totals = {
        "files": len(files),
        "source_files": sum(1 for f in files if f["kind"] == "source"),
        "source_lines": sum(f["lines"] for f in files if f["kind"] == "source"),
        "symbols": sum(1 for f in files for x in f["symbols"] if x["kind"] != "imports"),
        "routes": sum(len(f["routes"]) for f in files),
        "by_kind": {},
    }
    for f in files:
        totals["by_kind"][f["kind"]] = totals["by_kind"].get(f["kind"], 0) + 1
    data = {"generated": datetime.datetime.now().isoformat(timespec="seconds"),
            "tool": "analyzing-a-codebase/scripts/inventory.py 1.8.0",
            "totals": totals, "excluded": excluded, "files": files}
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=1)

    out = ["# Symbol checklist", "",
           "Generated by `scripts/inventory.py` on %s. This is the work list: every file below gets a" % data["generated"],
           "page or a row in the analysis, and every symbol a function card or a helper row. Do not edit by hand;",
           "re-run the script instead. `coverage.py` ticks the list against the analysis.", "",
           "| Measure | Count |", "| --- | --- |"]
    out += ["| Files in scope | %d |" % totals["files"],
            "| Source files | %d |" % totals["source_files"],
            "| Source lines | %d |" % totals["source_lines"],
            "| Classes and functions | %d |" % totals["symbols"],
            "| Routes | %d |" % totals["routes"]]
    out += ["", "## Excluded folders", "", "| Folder | Reason |", "| --- | --- |"]
    out += ["| `%s` | %s |" % (e["path"], e["reason"]) for e in excluded] or ["| (none) | |"]
    out += ["", "## Files by kind", ""]
    for kind in ("source", "build", "deploy", "config", "data", "doc", "other"):
        group = [f for f in files if f["kind"] == kind]
        if not group:
            continue
        out += ["### %s (%d)" % (kind, len(group)), "", "| File | Lines | Symbols | Routes |", "| --- | --- | --- | --- |"]
        out += ["| `%s` | %s | %d | %d |" % (f["path"], "binary" if f["binary"] else f["lines"],
                                            len(f["symbols"]), len(f["routes"])) for f in group]
        out.append("")
    out += ["## Symbols per source file", ""]
    for f in files:
        if not [x for x in f["symbols"] if x["kind"] != "imports"] and not f["routes"]:
            continue
        out += ["### `%s` (%d lines)" % (f["path"], f["lines"]), ""]
        if f["routes"]:
            out += ["| Route | Methods | Handler | Line |", "| --- | --- | --- | --- |"]
            out += ["| `%s` | %s | `%s` | %d |" % (r["path"], ", ".join(r["methods"]), r["handler"], r["line"]) for r in f["routes"]]
            out.append("")
        if f["symbols"]:
            out += ["| Symbol | Kind | Lines | Size | Branch lines to cite | Calls |", "| --- | --- | --- | --- | --- | --- |"]
            out += ["| `%s` | %s | %d-%d%s | %d | %s | %s |" % (
                        s["qualname"], s["kind"], s["start"], s["end"], " (approx.)" if s.get("approximate") else "",
                        s["size"], ", ".join(str(b["line"]) for b in s.get("branches", [])) or "-",
                        ", ".join("`%s`" % c["name"] for c in s.get("calls", [])[:12]) or "-")
                    for s in f["symbols"] if s["kind"] != "imports"]
            out.append("")
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(out) + "\n")
    return json_path, md_path, totals


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=".", help="repository root (default: current folder)")
    parser.add_argument("--analysis", default="codebase-analysis", help="analysis folder, relative to the repository")
    parser.add_argument("--exclude", action="append", default=[], help="extra folder to exclude, relative to the repository")
    args = parser.parse_args()
    if not os.path.isdir(args.repo):
        fail("repository not found: " + args.repo)
    args.analysis = args.analysis.replace("\\", "/")
    if os.path.isabs(args.analysis) or ".." in args.analysis.split("/") or args.analysis.strip("/") in ("", "."):
        fail("--analysis must be a folder inside the repository, given relative to it")
    files, excluded = scan(args.repo, args.analysis, [e.replace("\\", "/").strip("/") for e in args.exclude])
    json_path, md_path, totals = write_outputs(os.path.abspath(args.repo), args.analysis, files, excluded)
    print("ok: %d files, %d source files, %d source lines, %d symbols, %d routes"
          % (totals["files"], totals["source_files"], totals["source_lines"], totals["symbols"], totals["routes"]))
    print("wrote " + os.path.relpath(json_path, os.path.abspath(args.repo)))
    print("wrote " + os.path.relpath(md_path, os.path.abspath(args.repo)))


if __name__ == "__main__":
    main()
