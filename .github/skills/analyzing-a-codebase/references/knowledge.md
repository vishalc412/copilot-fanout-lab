# Knowledge graph and knowledge base

The pages are written for people. The `knowledge/` folder serves the same knowledge to an LLM agent, in three forms it can use: a short primer to load every time, chunks to retrieve, and a graph to walk.

## Contents

- What is built, and from what
- Steps
- Making the graph good
- How an agent uses it
- Limits

## What is built, and from what

| Output | Built by | From |
| --- | --- | --- |
| `AGENT-CONTEXT.md` | You, from the template in [output-templates.md](output-templates.md) | The finished pages |
| `graph.json`, `nodes.csv`, `edges.csv` | `scripts/knowledge.py` | The code (files, symbols, routes, imports, calls) and the pages' front matter (components, tables, stores, outside systems, configuration, topics) |
| `chunks.jsonl` | `scripts/knowledge.py` | Every page, split at headings of level 1 to 3, at most about 1,500 tokens each, with heading path, component, kind, files cited and symbols named |
| `symbol-index.json` | `scripts/knowledge.py` | Every symbol and route: file, lines, pages, its card's chunk |
| `README.md` | `scripts/knowledge.py` | Counts, edge meanings, and how to load the files |

Node types: `File`, `Function`, `Method`, `Class`, `Route`, `Component`, `Page`, and one per front-matter prefix (`Table`, `Store`, `External`, `Config`, `Topic`, ...).

Edge types and how each is resolved:

| Edge | Meaning | Resolution |
| --- | --- | --- |
| `DEFINES` | file or class defines a symbol | `exact` (parser) |
| `DECLARES` | file declares a route | `exact` |
| `HANDLED_BY` | route is handled by a function | `exact` |
| `IMPORTS` | file imports another file | `exact` (Python) |
| `CALLS` | function calls function | `same-file`, `self`, `import`, or `name-unique` (only method of that name in that language; a lead, not a fact) |
| `DOCUMENTS`, `HAS_PAGE`, `CONTAINS` | page documents file; component has page; component contains file | from `Source file:` lines and front matter |
| `READS`, `WRITES`, `CALLS`, `USES`, `CONFIG`, `EXPOSES`, `PUBLISHES`, `CONSUMES`, `DEPENDS_ON` | from front matter | `analysis` |

Every edge carries its evidence: a `path:line` for code edges, the page for analysis edges.

## Steps

1. Check every LLD page has front matter with its lists filled (`coverage.py` fails pages without `id` and `kind`; it cannot tell an empty `writes` from a forgotten one, so check that yourself against the page's Data section).
2. Write `knowledge/AGENT-CONTEXT.md` from the template. Facts and citations come from the pages; keep it under 3,000 words.
3. Run `python3 -I <skill folder>/scripts/knowledge.py --repo . --analysis <output folder>`.
4. Read `knowledge/README.md`:
   - "Front-matter names that match no symbol": fix the spelling in the front matter, or remove the entry.
   - "Calls the script could not resolve": normal for library calls; for calls between the system's own functions, make sure the card names the callee, so retrieval still finds it.
   - Node types: two nodes for one table or outside system (`table:Audit` and `table:audit`) mean two spellings. Pick one, fix the pages, run again.
5. Copy the counts into `README.md` and the totals.

Run it again after every revision: the graph is a build product of the pages and the code, never edited by hand.

## Making the graph good

- **One name per thing.** Tables by their schema name, outside systems by the name in `hld/01-system-context.md`, components by the name in `README.md`, routes as `<METHOD> <path>` exactly as the code declares them.
- **Front matter mirrors the page.** Every table in a module page's Data section is in `reads` or `writes`; every outside system in its outbound calls is in `calls`; every configuration key it reads is in `config`.
- **Cards name their callees in backticks.** That puts the symbol in the chunk's `symbols` list, which is how retrieval links a question to every card that mentions a function.
- **Headings name symbols and routes.** The symbol index finds a card by its heading.

## How an agent uses it

`knowledge/README.md` repeats this for whoever wires up the agent:

1. Load `AGENT-CONTEXT.md` into the system prompt or the first message.
2. A question names a function, route or file: look it up in `symbol-index.json`, read its card chunk, then the cited lines.
3. A broader question: retrieve from `chunks.jsonl` by similarity, filtered by `component` or `kind`.
4. "What breaks if I change X": walk `CALLS`, `HANDLED_BY`, `READS` and `WRITES` from X in `graph.json`, then read the cards reached.
5. Before acting, open the cited lines: the code wins over the analysis.

`nodes.csv` and `edges.csv` load into Neo4j, Memgraph, NetworkX or a spreadsheet; `knowledge/README.md` has a Neo4j example. `chunks.jsonl` loads into any vector store; embed `text`, keep the rest as metadata.

## Limits

State these in `AGENT-CONTEXT.md` under its opening line:

- Calls through dynamic dispatch, callbacks, reflection, string-built names or another language are not in the graph; an absent `CALLS` edge is not proof of no call.
- `name-unique` and `analysis` edges are only as good as their resolution and the analysis; both are leads to check.
- The graph and chunks describe the snapshot in `README.md`. After the code changes, re-run `inventory.py`, revise the pages, and re-run `knowledge.py`.
