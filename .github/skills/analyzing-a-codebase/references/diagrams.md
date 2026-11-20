# Diagrams

A diagram earns its place by answering one question a new engineer would ask, with names they will then find in the code. The examples below use an invented lending system; never copy its names, only its shape.

## Contents

- The diagram set
- What every diagram has
- Nodes: shapes and labels
- Edges: labels
- Evidence table
- Bad and good
- Examples by type: mind map, context, containers, deployment, components, main types, sequence, data model, lifecycle

## The diagram set

| Diagram | Answers | File | Mermaid | Required |
| --- | --- | --- | --- | --- |
| Mind map | What is in the system, on one page? | `00-mind-map.md` | `mindmap` | Always: one for the system, one per component |
| System context | Who uses the system, and which outside systems does it depend on? | `README.md` and `hld/01-system-context.md` | `flowchart LR` | Always |
| Containers | What runs, in what technology, and how do the parts talk? | `hld/02-architecture.md` | `flowchart LR` | Always |
| Deployment | Where does each part run, on what port, started by what? | `hld/02-architecture.md` | `flowchart TB` | When any deployment, container or pipeline file exists |
| Module map | How do the modules of one large component depend on each other? | `hld/02-architecture.md` | `flowchart LR` | When one component has more than about ten modules |
| Components | What are the parts inside one component and how does a request move through them? | `lld/<component>/README.md` | `flowchart TB` | One per component |
| Main types | What are the main classes, their key fields and methods, and how do they relate? | `lld/<component>/README.md` | `classDiagram` | One per component written in classes |
| Call graph | Which function of this file calls which? | `lld/<component>/<module>.md` | `flowchart LR` | One per module page at `deep` |
| Sequence | What happens, step by step, in one journey, including when it fails? | `hld/05-key-flows.md`, endpoint cards | `sequenceDiagram` | One per flow; one per endpoint card at `deep` (with three or more participants at `standard`) |
| Data model | What does the system store and how do the records relate? | `hld/04-data-architecture.md` | `erDiagram` | One per store whose schema is in the repository |
| Lifecycle | Which states can a record be in, and what moves it between them? | `hld/04-data-architecture.md` | `stateDiagram-v2` | For each record with a status the code changes |
| Pipeline | What are the build and deployment stages, and what does each produce? | `hld/02-architecture.md` | `flowchart LR` | When a pipeline file exists |

## What every diagram has

1. **A heading and one sentence** above it saying what it shows and what is left out: "Runtime containers and their connections. Build tools and tests are not shown."
2. **Real names.** Nodes carry the names used in the code, configuration or deployment files: `customers-service`, `OwnerResource`, `owners` table. `reference/glossary.md` explains them once.
3. **The same name everywhere.** A unit is called the same in every diagram, table and sentence.
4. **The right size:** 5 to 20 nodes. Fewer means it says too little (merge it into another diagram, or look harder); more means split it by area and say so.
5. **Nothing invented.** Every node and edge rests on a citation. A typical part that the code does not show (a load balancer, a cache, a queue) is not drawn.
6. **An evidence table** directly under it (sequence diagrams use their step table; a module's call graph needs none, since each edge is a call listed in the symbol checklist and in the cards).
7. **Valid syntax** per [mermaid-syntax.md](mermaid-syntax.md).

## Nodes: shapes and labels

Shapes say what kind of thing a node is. Use these and no others, and add the key line under architecture diagrams:

| Kind | Shape | Example |
| --- | --- | --- |
| Person or role | stadium | `staff(["Branch staff<br/>web browser"])` |
| Unit of this system (service, app, job, function) | rectangle | `loans["loans-service<br/>Spring Boot 3.2, Java 17<br/>Issues and returns loans"]` |
| Data store (database, cache, bucket, file share) | cylinder | `loansdb[("loans DB<br/>PostgreSQL 15")]` |
| Queue, topic or stream | subroutine | `events[["loans.events<br/>Kafka topic"]]` |
| System outside this repository | hexagon | `pay{{"PayCo payments API<br/>external"}}` |

Key line: `Shapes: rounded = people, rectangle = this system's units, cylinder = data store, double-sided = queue or topic, hexagon = outside system. Dashed line = inferred.`

Labels on context, container and deployment nodes have up to three lines, joined with `<br/>`: name, technology and version, one-line responsibility. Component nodes have the class or module name and its role. Never a bare technology ("Database", "Backend", "API").

## Edges: labels

Every edge is labelled with what travels and how, in that order:

- synchronous: `"GET /loans/{id}<br/>REST, HTTP :8081"`, `"SQL over JDBC"`, `"gRPC LoanService.Create"`
- asynchronous: `"publishes LoanIssued"`, `"consumes LoanIssued"`
- configuration and discovery: `"reads config at start-up, HTTP :8888"`, `"registers, Eureka :8761"`

Give the scheme (`HTTP` or `HTTPS`) and port whenever the code or configuration shows them. Draw arrows in the direction the call or message goes, not the direction data comes back.

Use a solid edge (`-->`) for a connection read in the code and a dashed edge (`-.->`) for an inferred or assumed one.

## Evidence table

Directly under each flowchart, class diagram, data model or lifecycle diagram:

```markdown
| Element | Evidence |
| --- | --- |
| loans-service -> loans DB | `loans-service/src/main/resources/application.yml:4-9` |
| loans-service -> loans.events | `loans-service/src/main/java/lend/loans/LoanEventPublisher.java:18-25` |
| PayCo payments API (inferred: base URL only in the chart) | `charts/fees-job/values.yaml:31` |
```

- A node with an edge rests on the edge's evidence and needs no row of its own; a node with no edge needs one.
- An element with no evidence is removed from the diagram.
- A sequence diagram uses its step table instead; a mind map is evidenced by the pages its leaves name.

## Bad and good

Bad, and typical of a first draft:

```mermaid
flowchart LR
  user["User"] --> fe["Frontend"]
  fe --> be["Backend"]
  be --> db[("Database")]
```

It would fit any system; there is no technology, protocol, port or responsibility, and nothing a reader could find in the code. The good container example below shows the same system.

Other faults to remove before finishing:

- Infrastructure the code depends on is missing: a gateway, configuration server, service registry, identity provider, message broker, scheduler or observability back end.
- Every unit is drawn talking to every other unit, because that is "usually" the case.
- The context diagram shows only the system and one user. Run the sweep ([search-sweep.md](search-sweep.md)) and draw every outside system it finds.
- A sequence diagram shows only the happy path although the code handles failure.
- A data model shows boxes with no keys, or relations with no cardinality or label.

## Example: mind map

```mermaid
mindmap
  root((Lending platform))
    Channels
      Branch staff web UI
      Member mobile app
    loans-service
      LoanController, 9 routes
      LoanService, issue and return rules
      FeeCalculator
      CatalogueClient
    catalogue-service
      BookRouter, 6 routes
      CopyStore
    Data
      loans DB, PostgreSQL 15
      catalogue DB, MongoDB 6
      loans.events, Kafka
    Outside systems
      PayCo payments
      Corporate identity provider
      Mail relay
```

Branch by what a reader looks for: channels, components, data, outside systems; under each component, its modules with a few words each. Keep to about 60 leaves; the per-component mind maps carry the rest.

## Example: system context

```mermaid
flowchart LR
  staff(["Branch staff<br/>web browser"])
  member(["Library member<br/>mobile app"])
  subgraph lending["Lending platform"]
    platform["Lending platform<br/>5 services<br/>Lends books and collects fees"]
  end
  idp{{"Corporate identity provider<br/>OpenID Connect"}}
  pay{{"PayCo payments API<br/>external"}}
  smtp{{"Mail relay<br/>SMTP"}}
  staff -->|"HTTPS :443"| platform
  member -->|"HTTPS :443"| platform
  platform -->|"verifies tokens, HTTPS"| idp
  platform -->|"charges late fees, REST over HTTPS"| pay
  platform -.->|"sends reminders, SMTP :25"| smtp
```

## Example: containers

```mermaid
flowchart LR
  staff(["Branch staff<br/>web browser"])
  subgraph lending["Lending platform"]
    gw["edge-gateway<br/>Spring Cloud Gateway 4<br/>Routes and authenticates requests"]
    ui["web-ui<br/>React 18, served by gateway<br/>Staff screens"]
    loans["loans-service<br/>Spring Boot 3.2, Java 17<br/>Issues and returns loans"]
    cat["catalogue-service<br/>Node 20, Express<br/>Books and copies"]
    fees["fees-job<br/>Spring Batch, nightly<br/>Charges late fees"]
    loansdb[("loans DB<br/>PostgreSQL 15")]
    catdb[("catalogue DB<br/>MongoDB 6")]
    events[["loans.events<br/>Kafka topic"]]
  end
  pay{{"PayCo payments API<br/>external"}}
  staff -->|"HTTPS :443"| gw
  gw -->|"serves static files"| ui
  gw -->|"/api/loans/**, HTTP :8081"| loans
  gw -->|"/api/books/**, HTTP :8082"| cat
  loans -->|"GET /copies/{id}, REST, HTTP :8082"| cat
  loans -->|"SQL over JDBC"| loansdb
  cat -->|"MongoDB driver"| catdb
  loans -->|"publishes LoanReturned"| events
  fees -->|"consumes LoanReturned"| events
  fees -->|"POST /charges, REST over HTTPS"| pay
```

Shapes: rounded = people, rectangle = this system's units, cylinder = data store, double-sided = queue or topic, hexagon = outside system. Dashed line = inferred.

## Example: deployment

```mermaid
flowchart TB
  subgraph cluster["Kubernetes cluster, namespace lending"]
    subgraph gwpod["Deployment edge-gateway, 2 replicas"]
      gw["edge-gateway :8080"]
    end
    subgraph loanspod["Deployment loans-service, 3 replicas"]
      loans["loans-service :8081"]
    end
    cron["CronJob fees-job<br/>schedule 0 2 * * *"]
    cfg[("ConfigMap loans-config")]
  end
  ing["Ingress lending.example<br/>TLS terminated here"]
  pg[("PostgreSQL 15<br/>managed, outside the cluster")]
  ing -->|"HTTP :8080"| gw
  gw -->|"HTTP :8081"| loans
  cfg -->|"environment variables"| loans
  loans -->|"JDBC :5432"| pg
  cron -->|"JDBC :5432"| pg
```

## Example: components inside one unit

```mermaid
flowchart TB
  gw["edge-gateway"]
  subgraph loans["loans-service"]
    ctl["LoanController<br/>REST endpoints"]
    svc["LoanService<br/>issue and return rules"]
    repo["LoanRepository<br/>Spring Data JPA"]
    cat["CatalogueClient<br/>RestClient wrapper"]
    pub["LoanEventPublisher<br/>KafkaTemplate"]
  end
  db[("loans DB")]
  catsvc["catalogue-service"]
  topic[["loans.events"]]
  gw -->|"HTTP /loans/**"| ctl
  ctl -->|"issue, giveBack"| svc
  svc -->|"save, findOpenByMember"| repo
  svc -->|"copyStatus"| cat
  svc -->|"LoanReturned"| pub
  repo -->|"SQL"| db
  cat -->|"GET /copies/{id}, HTTP"| catsvc
  pub -->|"publishes"| topic
```

## Example: main types

```mermaid
classDiagram
  class LoanService {
    +issue(memberId, copyId) Loan
    +giveBack(loanId) Loan
  }
  class Loan {
    +Long id
    +Long memberId
    +Long copyId
    +LocalDate dueOn
    +LoanStatus status
  }
  class FeeCalculator {
    +outstanding(memberId) BigDecimal
  }
  class LoanRepository {
    +findOpenByMember(memberId) List~Loan~
  }
  LoanService --> LoanRepository : saves and reads
  LoanService --> FeeCalculator : checks fees
  LoanRepository "1" --> "*" Loan : stores
```

## Example: sequence

```mermaid
sequenceDiagram
  autonumber
  actor Staff as Branch staff
  participant GW as edge-gateway
  participant LS as loans-service
  participant CS as catalogue-service
  participant DB as loans DB
  Staff->>GW: POST /api/loans with memberId and copyId
  GW->>LS: POST /loans
  LS->>CS: GET /copies/{copyId}
  alt copy is on loan
    CS-->>LS: 200 with status ON_LOAN
    LS-->>GW: 409 Conflict
    GW-->>Staff: 409 Copy already on loan
  else copy available
    CS-->>LS: 200 with status AVAILABLE
    LS->>DB: INSERT into loan
    LS-->>GW: 201 Created with loan id
    GW-->>Staff: 201 Created
  end
```

Use `autonumber`, real participant names, the real operation on each message, and an `alt` block for each failure path the code handles. Name people by their role in this system (`Clinic staff`, `Operator`), never only `User` or `Browser`. Replies are dashed (`-->>`); calls are solid.

## Example: data model

```mermaid
erDiagram
  MEMBER ||--o{ LOAN : "borrows"
  COPY ||--o{ LOAN : "is lent in"
  LOAN ||--o| FEE : "may incur"
  MEMBER {
    bigint id PK
    string card_number "unique"
    string email
  }
  LOAN {
    bigint id PK
    bigint member_id FK
    bigint copy_id FK
    date due_on
    string status "OPEN, RETURNED, LOST"
  }
  COPY {
    bigint id PK
    string isbn
  }
  FEE {
    bigint id PK
    bigint loan_id FK
    decimal amount
  }
```

Entity names are the table or collection names. Attribute types are one word; put lengths, constraints and allowed values in the quoted comment.

## Example: lifecycle

```mermaid
stateDiagram-v2
  [*] --> OPEN : LoanService.issue
  OPEN --> RETURNED : LoanService.giveBack
  OPEN --> OVERDUE : fees-job, due_on passed
  OVERDUE --> RETURNED : LoanService.giveBack
  OVERDUE --> LOST : 60 days overdue
  RETURNED --> [*]
  LOST --> [*]
```

States are the values the code uses; each transition names the method, job or rule that makes it.
