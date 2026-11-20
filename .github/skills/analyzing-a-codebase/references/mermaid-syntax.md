# Mermaid that renders everywhere

GitHub, Azure DevOps, GitLab, VS Code previews and documentation sites run different Mermaid versions. This subset renders in all of them. A diagram that does not render is a defect: the reader sees an error box.

## Contents

- Every diagram
- Flowcharts
- Sequence diagrams
- Data models
- Lifecycles
- Class diagrams
- Mind maps
- Pre-flight check

## Every diagram

- Fence it as ` ```mermaid ` and start with the type on the first line: `flowchart LR`, `flowchart TB`, `sequenceDiagram`, `erDiagram`, `stateDiagram-v2`, `classDiagram`, `mindmap`.
- No styling or extras: no `classDef`, `class`, `style`, `linkStyle`, `click`, `%%{init}%%`, icons, Font Awesome, links or HTML. The one exception is `<br/>` inside a quoted label.
- No comments inside diagrams; put notes in the sentence above.
- Keep each label under about 120 characters.

## Flowcharts

- **Ids:** lowercase letters and digits only, starting with a letter: `orders`, `ordersdb`, `gw2`. Unique within the diagram.
- **Reserved words never as ids:** `end`, `graph`, `flowchart`, `subgraph`, `style`, `class`, `click`, `default`, `direction`.
- **Quote every label**, node and edge: `orders["orders-service<br/>Java 21"]`, `-->|"GET /stock/{sku}"|`. Quotes make brackets, braces, slashes, colons and `@` safe.
- **Inside a label never use:** a double quote (use a single quote), a backtick, `#`, `;`, `|`, or `<` and `>` other than `<br/>`.
- **Shapes:** `id["..."]` rectangle, `id(["..."])` stadium, `id[("...")]` cylinder, `id[["..."]]` subroutine, `id{{"..."}}` hexagon. Nothing else.
- **Edges:** `a -->|"label"| b` solid, `a -.->|"label"| b` dashed. One edge per line. No chained edges (`a --> b --> c`) and no `&`.
- **Subgraphs:** `subgraph sysid["Label"]` on its own line, members indented, closed by `end` on its own line. The subgraph id follows the id rules and differs from every node id. Nest at most two levels.
- **Declare each node once**, with its label, then refer to it by id alone.

## Sequence diagrams

- `autonumber` on the second line.
- Declare every participant first: `participant GW as edge-gateway` or `actor Staff as Branch staff`. The id is letters and digits; the alias may contain spaces, hyphens and dots, nothing else.
- Messages: `A->>B: text` for a call, `B-->>A: text` for a reply. One per line.
- **Inside message text never use** `;` (it ends the message), `#`, or a double quote. Write `200 with status AVAILABLE`, not `200 {"status": "AVAILABLE"}`.
- Blocks: `alt condition` ... `else condition` ... `end`; `opt condition` ... `end`; `loop condition` ... `end`. Every block closes with `end`. Conditions are plain words.
- Notes: `Note over A,B: text`, same character rules as messages.

## Data models

- Entity names: letters, digits and underscores, written as in the schema, or in capitals: `OWNERS`, `visit_log`.
- Relationship: `A ||--o{ B : "label"`. Cardinality markers only from `||`, `|o`, `o|`, `}o`, `o{`, `}|`, `|{`. The label is always quoted.
- Attributes: `type name` then optional `PK`, `FK` or `PK, FK`, then an optional quoted comment. The type is one word with no brackets: `string`, `int`, `bigint`, `decimal`, `date`, `datetime`, `boolean`, `text`. Put `varchar(30)` in the comment.

## Lifecycles

- `stateDiagram-v2` on the first line.
- State names: letters, digits and underscores only. For a value with spaces or symbols, declare `state "In review" as INREVIEW` first.
- Transitions: `A --> B : label`. Start and end with `[*]`.

## Class diagrams

- `class Name` with members in braces, one per line: `+String name`, `+cancel() void`.
- Relations: `A "1" --> "*" B : label`. No generics with angle brackets: write `List~Pet~`.

## Mind maps

- `mindmap` on the first line, then the root on the next, indented two spaces: `  root((System name))`. The root is the only node with a shape.
- Every other node is plain text on its own line, indented two more spaces than its parent. Indent with spaces only, never tabs, and keep the indentation exact: it is the tree.
- **Inside node text never use** brackets of any kind `( ) [ ] { }`, a double quote, a backtick, `#`, `;`, `:` or `<` `>`. Write `LoanController, 9 routes`, not `LoanController (9 routes)`. Commas, hyphens, dots, slashes and spaces are safe.
- No icons (`::icon`), no classes (`:::`), no markdown.
- Mind maps need Mermaid 9.3 or later. GitHub, GitLab and current VS Code previews have it; older Azure DevOps wikis and documentation sites may not. That is why `00-mind-map.md` also carries the same tree as a nested list.

## Pre-flight check

Run this on every diagram before moving on, and again in the quality gate:

1. The first line names a type from the list above.
2. Every node and edge label is in double quotes (flowcharts) or follows the character rules (other types).
3. No reserved word is an id; ids are unique; no subgraph id equals a node id.
4. Every `subgraph`, `alt`, `opt`, `loop` and `state` block is closed by its own `end` or brace.
5. Brackets in shapes are balanced: `[" "]`, `([" "])`, `[(" ")]`, `[[" "]]`, `{{" "}}`.
6. No `;` or `#` anywhere in the diagram; no HTML except `<br/>`.
7. Data model types are single words.
8. Mind maps: two-space indentation, only the root has a shape, no brackets or colons in node text.
9. The evidence or step table follows the diagram.

If your environment offers a Mermaid validator, render tool or preview, run every diagram through it and fix what fails. If not, say in `README.md` that the diagrams were checked by reading only.
