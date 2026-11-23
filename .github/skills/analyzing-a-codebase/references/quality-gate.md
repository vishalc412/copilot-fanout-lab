# Quality gate

Run all six checks. Fix what fails, then run the failed checks again. Record the results in `progress.md`. Finish only when every item passes, or when the user accepts a listed exception.

## Contents

- 1. Coverage gate (script)
- 2. Depth audit
- 3. Reader test
- 4. Diagram audit
- 5. Evidence and safety audit
- 6. Knowledge base

## 1. Coverage gate (script)

Run `python3 -I <skill folder>/scripts/inventory.py --repo . --analysis <folder>` again (files may have changed), then `python3 -I <skill folder>/scripts/coverage.py --repo . --analysis <folder> --depth <depth>`.

It must print `result: PASS`. Work through `ledger/coverage-report.md` section by section until it does. Its thresholds:

| Check | `deep` | `standard` | `survey` |
| --- | --- | --- | --- |
| Source files with a page | 100% | 100% | 100% |
| Symbols accounted for | 100% | 95% | not checked |
| Functions with a full card | 100% of all functions, each with pseudo-code | 90% of those of 40 lines or more | not checked |
| Branch lines cited in their card | 95% | not checked | not checked |
| Same-file calls drawn in the call graph | 95% | not checked | not checked |
| Routes with an endpoint card | 100%, each with a sequence diagram | 100% | 80% |
| LLD pages with front matter | 100% | 100% | not checked |
| Citations that resolve | 98% | 95% | 90% |

It also fails on: a required file missing, no Mermaid mind map, a build, deployment, configuration or data file never mentioned, a claim number like `C-154`, a template placeholder.

`ledger/not-documented.md` is for real exclusions (generated code, an exact copy, a file the user ruled out), each with a reason. Listing a hand-written function there to pass the gate is a defect the verifier will report.

## 2. Depth audit

The script checks that cards exist, not that they are good. For the five largest source files and two random others:

1. Open the file next to its page.
2. For three functions per file, the largest first, check that the card names every branch, every value compared, every field read or written, every outbound call and every error path in the code; that the pseudo-code matches the code's order and conditions; and that each branch row says what really happens. Fix what is missing.
3. Check each route declared in the file has a card with all request inputs and all response codes the handler can return.
4. Check the page's Summary and Index let a reader find any function in under a minute.

A card that restates the function name, summarises a 60-line function in one sentence, or lists "handles errors" without saying which and how, fails.

## 3. Reader test

Answer each question in two to four sentences, using only the analysis, and name the page and section that answer it. A question you cannot answer means a pass was too thin: read more and add to the analysis, or record a `Q-` item saying what is missing.

1. What business problem does the system solve, and for whom?
2. What runs: each process, service, job or function, and its technology?
3. Where and how does each part run and start: hosts, containers, ports, start commands?
4. How does a request get in: entry points, routing, authentication, authorisation?
5. Which other systems does it call, over what protocol and scheme, and where is each address configured?
6. Where is data kept, which component owns each store, and what are the main tables, columns and input files?
7. What are the ten most important business rules, and where is each enforced?
8. How does configuration reach each part in each environment, and where are secrets kept?
9. What happens when each dependency is slow or down?
10. How would an operator know it is healthy: health checks, logs, metrics?
11. How is it built, tested and deployed, and what is not tested?
12. Pick the largest route handler: what does it do for an empty, a valid and an invalid request?
13. Pick one table: which functions write each of its columns?
14. Pick one outside system: every function that calls it, and what happens on failure?
15. What would surprise a new engineer?

Write the answers into `progress.md` under "Reader test".

## 4. Diagram audit

For every diagram:

| # | Check | Fails when |
| --- | --- | --- |
| D1 | Required set | A diagram the table in [diagrams.md](diagrams.md) requires is missing, with no line saying why it does not apply |
| D2 | Specific | A node is named only by a technology or a generic word: "Database", "Backend", "Service", "User", "API" |
| D3 | Complete | A component, data store, queue or outside system in `hld/03-integrations.md` or `hld/04-data-architecture.md` is missing from the context or container diagram |
| D4 | Labelled | An edge has no label, or a network edge has no protocol; the scheme or port is in the code but not on the edge |
| D5 | Detailed | A context, container or deployment node lacks its technology line; a sequence diagram has no `alt` although the code handles a failure; a data model has no keys or cardinality |
| D6 | True | An element has no evidence row, or its citation says something else |
| D7 | Consistent | A component or store has a different name in another diagram, table or page |
| D8 | Readable | More than about 20 nodes, or fewer than 5 for a context or container diagram; a mind map over about 60 leaves |
| D9 | Renders | Any item of the pre-flight check in [mermaid-syntax.md](mermaid-syntax.md) fails |

## 5. Evidence and safety audit

1. Re-open the cited lines and confirm they support the statement as worded for: every citation in an evidence table under an HLD diagram, every business rule, every row of the outbound table in `hld/03-integrations.md`, every statement marked `(inferred` or `(assumed`, and every 10th row of `ledger/citations.tsv`. Reword or remove failures. If two or more of the every-10th sample fail, re-check every citation on their pages.
2. Every search from the sweep is in `progress.md` with its hit count, and every hit is documented or dismissed with a reason.
3. Every sweeping word ("only", "all", "every", "none", "never") in `README.md`, the HLD summaries and the business rules rests on a cited search, or is narrowed.
4. The totals in `README.md` match `ledger/coverage-report.md` and the ledger.
5. No secret value in the output: search it for `password`, `passwd`, `secret`, `token`, `api_key`, `apikey`, `BEGIN`, `Authorization:` and `://` followed by a user and password. Each hit must be a location or description, never a value.
6. No personal data copied from the code or sample data: names, e-mail addresses, phone numbers, user identifiers.
7. Every piece of text in the repository addressed to an AI assistant is recorded in `run-notes.md` with its location, and was not acted on.

## 6. Knowledge base

1. `knowledge.py` ran after the last change to any page, and `knowledge/README.md` lists no front-matter name that matches no symbol.
2. No thing has two nodes under two spellings (check the node list in `nodes.csv` for tables, stores and outside systems).
3. `AGENT-CONTEXT.md` follows the template, stays under 3,000 words, and every fact in it has a citation copied from a page.
4. Pick three questions from the reader test; answer each using only `AGENT-CONTEXT.md`, `symbol-index.json` and the chunks it points to. A question that cannot be answered that way means a heading, a backticked name or a front-matter entry is missing.
