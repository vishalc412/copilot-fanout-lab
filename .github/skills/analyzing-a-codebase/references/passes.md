# Passes

## Contents

- Depth
- Packets
- Pass 1: inventory
- Pass 2: components and the work plan
- Pass 3: LLD, one page per source file
- Pass 4: LLD, endpoint cards
- Pass 5: LLD, component design
- Pass 6: sweep
- Pass 7: data dictionary
- Pass 8: HLD
- Pass 9: mind map, front page, reference
- Pass 10: knowledge base
- Pass 11: quality gate

## Depth

| Depth | Every source file | Full card for | Each card also has | Each module page has | Each endpoint card has | Use when |
| --- | --- | --- | --- | --- | --- | --- |
| `deep` (default) | Read in full, own page | Every function and method, however short | Pseudo-code; every branch, loop, `except` and `raise` cited on its own line | A call graph | A sequence diagram | The normal case: the bible |
| `standard` | Read in full, own page | Every function of 40 lines or more; a helper row for the rest | - | - | - | A very large repository, or the rest after `deep` areas |
| `survey` | Own page or a row | Nothing | - | - | - | A first look only. Never call a survey the bible |

Every LLD page at `deep` and `standard` starts with front matter ([output-templates.md](output-templates.md), "Front matter"): it is what turns the pages into a knowledge graph.

- State the depth at the top of `README.md`. Mixed depth is normal: say which components got which, and run `coverage.py` per depth with `--exclude` for the others.
- Test files get a page listing every test (name, what it checks, lines), not cards; HTML templates and stylesheets are covered on the pages of the code that uses them. `coverage.py` applies these rules.
- At `standard`, a function under the card threshold still gets a row in its page's helper table. At `deep` there is no threshold: a three-line helper gets a short card (Source, one step, one line of pseudo-code).
- `ledger/symbol-checklist.md` lists, for each function, the branch lines to cite and the calls it makes. Use them: the Branches and errors table needs one row per listed line, and the call graph one edge per call to a function of the same file.
- A file that is an exact copy of one already documented gets a page with one line: `Identical to <path>` and the evidence (both line counts and a compared listing).
- Generated code inside the source tree (protobuf stubs, ORM migrations written by a tool) gets one page per folder saying what generates it, and is listed in `ledger/not-documented.md` with that reason.

## Packets

A packet is the unit of work in one go: one source file, or a slice of about 400 lines of a large file. A 4,800-line file is 12 packets; plan them, do not skim it. At `deep`, plan about one packet per 25 functions as well: a large repository at `deep` is many chats. Tell the user the packet count up front, and propose `standard` for low-priority components if that is too many.

For each packet:

1. Open the lines. Read them in full.
2. Write or extend the module page: one function card per function (with steps, pseudo-code and a branch table at `deep`), every route the slice declares linked to its endpoint card, and the edges for the slice's calls in the page's call graph.
3. Write the endpoint cards for routes declared in the slice.
4. Add every business rule, outbound call, data access, configuration key and error path you met to the page, with its lines.
5. Save, tick the slice in `progress.md`, write one line to the user, and run `next.py` again.

Never write a card for a function you have not opened. Never compress a slice into one paragraph to save time; start a new chat instead.

## Pass 1: inventory

Read first: [output-templates.md](output-templates.md), "Folder layout" and "Ledger pages".

1. Run `python3 -I <skill folder>/scripts/inventory.py --repo . --analysis <output folder>`. It writes `ledger/inventory.json` and `ledger/symbol-checklist.md`. Add `--exclude <folder>` for anything the user rules out.
2. Read the checklist's totals and excluded folders. Check the exclusions are right (generated, vendored, dependency folders, this toolkit). A folder of the system's own code wrongly excluded is a stop: re-run without it.
3. Write `ledger/coverage-ledger.md` from the template: every top-level folder and its sub-folders that hold distinct things, files by kind, and status `not read`.
4. Record in `progress.md`: the date, file count, source lines, symbol and route totals, and any version the user gave. Never run a command to find a version.

Tell the user the output folder is a working document, not meant to be checked in. Do not edit ignore files.

## Pass 2: components and the work plan

Read first: "Depth" and "Packets" above, and [output-templates.md](output-templates.md), "progress.md".

A component is a part a reader would name when explaining the system: a deployable unit (service, web app, job, function, CLI), and inside a large unit, each cohesive area (the upload pipeline, the Jira integration, the audit store, the UI's migration screens). A monolith is never one component: split it by responsibility, as the routes, packages and service classes show.

For each component, note in `progress.md`: its name in the code, its files and folders, language and framework, how it starts, its entry points, and its packets.

Write the plan in `progress.md` under a `## Components` heading (`next.py` waits for that heading): each component, its folders, its packet count from `next.py`'s suggestion. Show it to the user once and carry on; a large plan is not a reason to stop, since `next.py` paces the work across chats. If the user wants to narrow it, use `--priority` or `standard` depth for named components.

## Pass 3: LLD, one page per source file

Read first: [output-templates.md](output-templates.md), "Front matter", "lld/<component>/<module>.md", "Function card", "Helper table" and "UI screen card"; [mermaid-syntax.md](mermaid-syntax.md), "Every diagram", "Flowcharts" and "Pre-flight check", before the first call graph.

For each file in the plan, packet by packet, write `lld/<component>/<module>.md` from the module-page template. The page opens with front matter and a `Source file: \`<path>\`` line so the scripts can find it.

- Start at the entry points, then follow calls inward to the logic and outward to data access and other systems.
- Each function card says what the code does, step by step, in plain words, with the lines of each step: the branches, the loops, the values compared, the fields read and written, the calls made, the errors raised or swallowed. A card that restates the function name ("`get_user` gets the user") is a defect.
- The pseudo-code is the function's logic in ten to thirty lines of plain structured text, keeping the real names and values; it is not the code copied.
- The Branches and errors table has one row per `if`, `elif`, loop, `case`, `except`, `catch` and `raise` or `throw`: the line, the condition in plain words, and what happens on each side.
- The page's call graph is a Mermaid flowchart with one node per function of the file and one edge per call between them; calls to other files' functions are drawn as nodes named `<module>.<function>`.
- Fill the front matter's `reads`, `writes`, `calls`, `uses`, `config`, `exposes`, `publishes` and `consumes` lists as you read: they become the knowledge graph's data and integration edges.
- Write each business rule as you meet it, numbered `R-01`, `R-02` within the component: validations, calculations, limits, state changes, permission checks. Name where it is enforced and what triggers it; a validation, schema constraint or policy file enforces nothing unless the code applies it.
- Where a prompt, tool description, API document, comment or message states a rule, compare it with the code that enforces it. A difference goes under "Surprises" on the page and in `reference/risks-and-surprises.md`.
- For UI files: one card per screen or component, with its route, the state it keeps, the API calls it makes (method, path, which endpoint card), and what the user can do on it.
- For pipeline, container and infrastructure files (Jenkinsfile, Dockerfile, Helm charts, Terraform, Kubernetes manifests): a page per file or chart, with each stage, each value that matters (ports, replicas, mounts, ingress, secrets referenced by name) and its lines.
- For SQL and schema files: a page per file, feeding the data dictionary.
- When a caller lies outside the file, open the calling function and cite it.
- Update the ledger and `progress.md` after each file: `done`, files opened, symbols covered.

## Pass 4: LLD, endpoint cards

Read first: [output-templates.md](output-templates.md), "lld/api/<group>.md"; [mermaid-syntax.md](mermaid-syntax.md), "Sequence diagrams".

Every route in the checklist gets a card in `lld/api/<group>.md`, grouped by URL prefix or blueprint, with an index table at the top of each group. The card's heading contains the method and the path exactly as the code declares it, so `coverage.py` can match it.

Each card holds: the handler and its lines; who may call it and how that is checked; every request input (path, query, header, body field, file upload) with type, whether required and the validation applied; the processing steps (link to the handler's function card rather than repeating it); data read and written; outbound calls; every response, with status code and shape; every error path; and which screen or client calls it, when the repository shows that. At `deep` every card has a sequence diagram, with an `alt` block for each error response; at `standard`, a route with three or more participants.

## Pass 5: LLD, component design

Read first: [output-templates.md](output-templates.md), "lld/<component>/README.md"; [diagrams.md](diagrams.md) in full, before the first component diagram.

After a component's files are done, write `lld/<component>/README.md`: its responsibility, its module list with one line each, a structure diagram and, for object-oriented code, a class diagram of its main types, its public interface (routes, functions other components call, events), the business rules table, the data it owns, its outbound calls, its configuration, its error handling and its surprises. This page is the bridge between HLD and LLD: a reader arriving from the architecture should know which module page to open next.

Then run `next.py` again.

## Pass 6: sweep

Run the searches in [search-sweep.md](search-sweep.md) that fit the languages in the checklist. Read every hit not already on a page and add it there, or dismiss it with the reason. Record each search with its hit count under a `## Sweep` heading in `progress.md` (`next.py` waits for that heading).

## Pass 7: data dictionary

Read first: [output-templates.md](output-templates.md), "lld/data-dictionary.md".

Write `lld/data-dictionary.md`: every store (database, schema, SQLite file, cache, bucket, share), every table or collection, every column or field (name, type, null, key, default, meaning, written by, read by), every input or output file the code reads or writes (Excel workbooks with each sheet and the columns the code uses, CSV, JSON, templates), and every status or enum value with the code that sets it. Read the schema files, migrations, `CREATE TABLE` statements and entity classes themselves, and the code that reads each spreadsheet column.

## Pass 8: HLD

Read first: [output-templates.md](output-templates.md), "HLD pages"; [diagrams.md](diagrams.md), the examples for context, containers, deployment, data model and lifecycle.

Only now, with every component written, write the HLD from the LLD pages. Copy names and citations from the pages; open the code again for anything new.

| File | Holds |
| --- | --- |
| `hld/01-system-context.md` | Context diagram; every person and outside system, with how and why the system talks to each |
| `hld/02-architecture.md` | Container diagram, deployment diagram, module map, technology table with versions, configuration sources per environment |
| `hld/03-integrations.md` | Every inbound interface and every outbound connection, with protocol, scheme, port, address source, authentication, timeout and retry; the dependency matrix |
| `hld/04-data-architecture.md` | Stores and ownership, data model diagrams, lifecycle diagrams, files and caches; shared stores are a finding |
| `hld/05-key-flows.md` | Eight to fifteen end-to-end flows, each with a sequence diagram, a step table and its failure paths |
| `hld/06-cross-cutting.md` | Authentication and authorisation, secrets, configuration, error handling, resilience, logging, metrics, tracing, build and deployment, testing, dependencies |

Where a call goes through a logical name (registry, Kubernetes service, gateway route), resolve the port and scheme from the deployment files and cite them; write "not found" only after looking.

Compare each setting that appears in more than one place: ports in Dockerfiles, compose files, charts and code; names in code and in dashboards; versions in build files. Each difference goes to `reference/risks-and-surprises.md`.

## Pass 9: mind map, front page, reference

Read first: [output-templates.md](output-templates.md), "00-mind-map.md", "README.md" and "Reference pages"; [mermaid-syntax.md](mermaid-syntax.md), "Mind maps".

1. `00-mind-map.md`: the whole system as a Mermaid mind map (system, components, modules, main capabilities, outside systems, stores), then one smaller mind map per component, then the same tree as a nested list for renderers without mind-map support. Each leaf names a page of the analysis.
2. `reference/glossary.md`, `reference/configuration.md` (every key, environment variable and setting: name, purpose, default, where read, never a secret value), `reference/risks-and-surprises.md` (what a new engineer must be warned about, with the lines), `reference/open-questions.md` (every `Q-001`, grouped by who could answer it).
3. `README.md`: status, the two-minute summary, the context diagram, reading paths for each kind of reader, the component table, the file list and the totals.

## Pass 10: knowledge base

Follow [knowledge.md](knowledge.md): write `knowledge/AGENT-CONTEXT.md`, run `knowledge.py`, read its report of unresolved calls and dangling nodes, fix the front matter they point at, and run it again. Copy its node, edge and chunk counts into `README.md`.

## Pass 11: quality gate

Run `coverage.py --depth <depth>` and [quality-gate.md](quality-gate.md). Fix and re-run the failed checks until every item passes. Copy the coverage figures into `README.md` and `progress.md`.

Re-run `knowledge.py` after the last fix, so the graph matches the final pages.
