# Checks

## Contents

- Finding vocabulary
- Step 2: Coverage gate
- Step 3: Selecting the sample
- Step 4: Judging a statement
- Step 5: Depth audit
- Step 6: Diagrams, data dictionary, mind map, knowledge base
- Step 7: Readability, ledger, consistency

## Finding vocabulary

Every finding in the report uses these words and no others.

| Verdict | Use for |
| --- | --- |
| `Confirmed` | A sampled statement the cited lines support as written |
| `Citation off` | True, but the cited lines do not show it; give the right location |
| `Overstated` | The main statement holds but says more than the code supports; give supported wording |
| `Wrong` | The code contradicts the main statement, or a part a reader would act on |
| `Unsupported` | Nothing at the citation, or anywhere you looked, supports it |
| `Omission` | Something the analysis should state and does not (a file, function, route, store, outside system, column) |
| `Inconsistent` | An error outside a sampled statement: a summary, count, label, flow step or name that disagrees with another part or with the code |

| Weight | Use for |
| --- | --- |
| `major` | Misleads about security, data, how the system fits together, or what a function does |
| `minor` | Wording, counts, a citation, a missing column, readability |
| significant (omissions only) | A reader would be misled about what the system connects to, what data it keeps, how it is secured, or how its main parts fit together. A missing internal helper is not. An item listed as an open question is not an omission unless the repository answers it |

## Step 2: Coverage gate

Done when the coverage table, the `not-documented.md` judgement and the totals comparison are written in the report.

```text
python3 -I <this skill>/scripts/coverage.py --repo . --analysis <folder> --depth <depth in README.md> --report verification-coverage.md
```

Mixed depth: if `README.md` says some areas were done at another depth, run once at the main depth with `--exclude <area>` for each such area, then once per other depth for those areas, each with its own `--report` name. `ledger/citations.tsv` lists every citation whatever the depth, so each run rewrites it unchanged.

An analysis whose pages carry claim numbers like `C-154`, or with `units/` or `components/` folders, fails this gate by design: say so, do the other steps anyway, and recommend a new analysis. One with no front matter and no `knowledge/` fails the `deep` gate: recommend revision mode.


1. Copy its table and its result into the report. A `GAPS` result with any file, route or symbol gap is a `major` coverage finding; list the gaps or, if there are many, the count per component and the ten largest.
2. Open `ledger/not-documented.md`. For each row, open the file: generated code, an exact copy, or a user's exclusion (confirmed with the user) is acceptable. Hand-written code listed there to pass the gate is a `major` finding.
3. Compare the inventory totals with `README.md`'s totals. A difference is an `Inconsistent` finding.

## Step 3: Selecting the sample

Done when the selected row indexes, per group, are written in the report.

`coverage.py` writes `ledger/citations.tsv`: every citation in the analysis, numbered, with its page, line and label. Select in this order, and describe the selection in the report so someone else would pick the same rows.

| Group | `quick` | `standard` | `full` |
| --- | --- | --- | --- |
| A. Citations on pages under `hld/`, and in `README.md` | half | all | all |
| B. Citations labelled `inferred` or `assumed` | half | all | all |
| C. Citations in business-rule tables, outbound-call tables, and security, secrets and authentication sections | half | all | all |
| D. All other citations | index divisible by 20 | index divisible by 7 | all |

- "Half" means the rows of the group whose index in `citations.tsv` is even. Group D uses the row's own index.
- A citation already judged in an earlier group is not judged twice.
- Statements checked outside the sample are reported separately. Scores use the sample only.

## Step 4: Judging a statement

Done when every selected row has one verdict from the vocabulary table, and each non-`Confirmed` row has a correction.

For each sampled row, read the sentence, table row or step it supports, open the cited lines, and give one of the first five verdicts in the vocabulary table.

- A true statement that leaves out something that matters is `Confirmed`, plus an `Omission` row.
- A statement about what a document says: check the document says it, and whether the code agrees.
- A statement of absence ("no retry"): search the component for the missing thing first. A statement citing a search: repeat the search.
- Check the marks: a plain statement must rest on code, configuration or a document that acts; one resting on a comment or an absence must say `(inferred`. A dashed diagram edge must match an inferred or assumed statement.
- Weigh each correction `major` or `minor` by the vocabulary table.

## Step 5: Depth audit

Done when every chosen card has a score and every `Partial`, `Shallow` or `Wrong` score names what is missing.

Coverage says a card exists; this says whether it is any good.

1. List the source files yourself with their line counts (do not use the author's checklist). Take the five largest, plus the file declaring the most routes (search the route patterns), plus the 3rd and 7th source files in alphabetical order of path.
2. For each, open the file next to its page. Take its three largest functions and three of its routes (the first, middle and last in the file).
3. For each function card (cards in test files are rows, not cards; skip them), check against the code: every branch and loop, every value compared, every field read or written, every outbound call, every error raised, caught or swallowed; that the pseudo-code follows the code's order and conditions; and that each row of the Branches and errors table says what that line really does. Score the card:

   | Score | Meaning |
   | --- | --- |
   | `Complete` | A reader could predict the function's behaviour for any input |
   | `Partial` | The main path is right, but a branch, error path, field or call that matters is missing |
   | `Shallow` | Restates the name, or summarises the function in a sentence or two |
   | `Wrong` | Describes behaviour the code does not have |

4. For each endpoint card: every request input the handler reads, its validation, every response code the handler can return, the authentication check, and the data touched. Score the same way.
5. Each `Partial` is a `minor` finding, each `Shallow` or `Wrong` a `major` one, with what is missing.

## Step 6: Diagrams, data dictionary, mind map, knowledge base

Done when every diagram has a result per check, and each bullet below has a written result.

### Diagrams

For every diagram, first the evidence:

- Every edge has a row in its evidence or step table, and that row was judged. A node with an edge may rest on the edge's citation; a node with no edge needs its own row.
- The citation in each row shows that element. A true citation about something else is a finding.
- The edge label (protocol, scheme, port, direction) matches the code.
- Repeat the searches listed in `progress.md`, and search the repository for the ways the code reaches outside itself (network clients, database handles, queues, mail, external programs, spreadsheets and files). Record any target missing from the context and container diagrams as an `Omission`.

Then the quality, one result per check for each diagram:

| # | Check | Finding when |
| --- | --- | --- |
| D1 | Required set | A required diagram is missing with no reason: mind map, context, containers, deployment (when deployment files exist), components and main types per component, one sequence per flow and per endpoint with three or more participants, a data model per store whose schema is in the repository, a lifecycle per record with a status the code changes |
| D2 | Specific | A node is named only by a technology or generic word ("Database", "Backend", "User") |
| D3 | Complete | A component, store, queue or outside system in the integration or data pages is missing from the context or container diagram |
| D4 | Labelled | An edge has no label, or a network edge has no protocol, or a scheme or port shown in the code is not on the edge |
| D5 | Detailed | An architecture node has no technology; a sequence diagram has no `alt` although the code handles a failure; a data model has no keys or cardinality |
| D7 | Consistent | A component or store is named differently in two places |
| D9 | Renders | The diagram breaks the syntax subset: an unquoted flowchart label; a reserved word (`end`, `graph`, `subgraph`, `class`, `style`) as an id; an unclosed `subgraph`, `alt`, `opt` or `loop`; `;` or `#` in a label or message; a type with brackets in a data model; brackets or colons in mind-map node text. Render it if you can. |

D6 (true) is the evidence check above; D8 (size) is not checked here.

A missing outside system or data store is an `Omission`. A diagram that does not render, a missing required diagram, or a generic node is `minor`.

### Data dictionary and mind map

- For each store and each input file in the inventory (`kind` data, and every file the code opens by name), check the data dictionary has it, with columns or sheets. For two tables and one spreadsheet, open the schema or the reading code and check every column the code uses is listed. A missing table or input file is an `Omission`; missing columns are `minor`.
- Check the mind map's leaves name real pages, and every component is on it.

### Knowledge base

The graph and chunks are built by a script from the pages and the code, so check their inputs, not the script:

- `knowledge/graph.json` is newer than every page (compare its `generated` time with the pages' file times); if not, the agent context is stale: a `minor` finding.
- Take ten edges with resolution `analysis` (the first, then every tenth, in file order): open the page and the cited code and judge each like a statement. A `WRITES` or `CALLS` edge the code does not support is a `major` finding.
- Take five `CALLS` edges with resolution `name-unique`: open the call line and say whether the target is right. Report the share; above one wrong in five, say so in the limits for whoever uses the graph.
- Two nodes for one table, store or outside system are a `minor` finding each.
- Judge `knowledge/AGENT-CONTEXT.md` like an HLD page: sample every citation in it (group A), and check it states these limits: calls through dynamic dispatch, callbacks, reflection or another language are not edges; `name-unique` and `analysis` edges are leads; the graph describes the snapshot date it names.

## Step 7: Readability, ledger, consistency

Done when each bullet below has a written result.

### Readability and prose

- For one page per component (its README) and three module pages, read as a new engineer would: is it plain, specific and in a sensible order? Does each page open with a summary? Can you find any function from the index? Record what blocks understanding, as `minor` findings.
- Claim numbers like `C-154`, evidence bullet lists standing in for explanation, or template text left in, are findings (the coverage script lists the first and last).
- For every fifth sentence or table row that cites lines, on each HLD page and each component README, check it says no more than its citation. A sentence that states a fact with no citation, or more than its citation, is `Inconsistent`, `major` if a reader would act on the extra part.

### Coverage ledger

- **Completeness:** list the folders yourself and report any missing from the ledger. A sub-folder rolled into its parent's row is not missing.
- **"Read in full":** take the five such folders with the most files. In each, open two files and look for an entry point, external call, data store, credential or scheduled job the analysis never mentions.
- **"Not read", "sampled", "excluded":** take the ten largest such rows, plus any named for security, data or integration. Open enough to judge whether skipping it could change a conclusion. Say yes or no, and why.


### Internal consistency

- Names of components, stores and outside systems agree across the mind map, HLD, LLD and data dictionary.
- Summaries and the front page agree with the pages they summarise.
- The totals in `README.md` match the coverage report and your own count.
- No secret value appears in the analysis.
