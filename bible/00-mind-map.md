# Mind map

The whole system on one page. Each leaf names the page that documents it. The system is `copilot-fanout-lab`: a sample shop library and three scripts that plan, open and gate component analysis (`README.md:1-9`).

```mermaid
mindmap
  root((copilot-fanout-lab))
    Components
      catalog
        get_product and price_of
        in_stock
        image_url
        fetch_supplier_feed
        apply_feed
      orders
        line_total
        order_total, one discount
        validate
        settle
      tools
        plan.py
        gate.py
        fanout.sh
    Data
      _PRODUCTS, in memory
      plan.json
      Analysis files read by the gate
    Outside systems
      Payment partner settlement endpoint
      Supplier product feed
      GitHub through gh
      GitHub Actions
    Reference
      Risks and surprises
      Open questions
      Configuration
```

Pages: components in `lld/catalog/README.md`, `lld/orders/README.md`, `lld/tools/README.md`; data in `lld/data-dictionary.md`; outside systems in `hld/01-system-context.md` and `hld/03-integrations.md`; reference in `reference/`.

## catalog

```mermaid
mindmap
  root((catalog))
    catalog.py
      get_product
      price_of, KeyError for unknown sku
      in_stock
      image_url
      fetch_supplier_feed, HTTP GET
      apply_feed, overwrites price and stock
    Data
      _PRODUCTS with 3 SKUs
    Outside
      Supplier product feed, plain http
      IMAGE_CDN prefix, never fetched
    Tests
      test_catalog.py, 1 test
```

Pages: [lld/catalog/README.md](lld/catalog/README.md), [lld/catalog/catalog.md](lld/catalog/catalog.md), [lld/catalog/test_catalog.md](lld/catalog/test_catalog.md).

## orders

```mermaid
mindmap
  root((orders))
    orders.py
      line_total
      order_total
        loyalty 5 percent
        bulk 10 percent at 10 items
        larger discount wins
      validate
        quantity must be positive
        not enough stock
      settle
        POST JSON, HTTP
        true only on 200
    Depends on
      catalog price_of and in_stock
    Outside
      Payment partner settlement endpoint
      Local fake on port 8099
    Tests
      test_orders.py, 1 test
```

Pages: [lld/orders/README.md](lld/orders/README.md), [lld/orders/orders.md](lld/orders/orders.md), [lld/orders/test_orders.md](lld/orders/test_orders.md).

## tools

```mermaid
mindmap
  root((tools))
    plan.py
      scan
      main, writes plan.json
    gate.py
      check, passes 1 to 3
      main, status.json
      count_tests
      fail and read
    fanout.sh
      labels
      issue per component
      ENGINE copilot or claude
    Data
      plan.json
      inventory, risks and tests-report files
    Outside
      GitHub through gh
      unittest child process
```

Pages: [lld/tools/README.md](lld/tools/README.md), [lld/tools/plan.md](lld/tools/plan.md), [lld/tools/gate.md](lld/tools/gate.md), [lld/tools/fanout.md](lld/tools/fanout.md).

## As a list

- copilot-fanout-lab ([README.md](README.md))
  - Components
    - catalog ([lld/catalog/README.md](lld/catalog/README.md))
      - catalog.py ([lld/catalog/catalog.md](lld/catalog/catalog.md)): get_product, price_of, in_stock, image_url, fetch_supplier_feed, apply_feed
      - test_catalog.py ([lld/catalog/test_catalog.md](lld/catalog/test_catalog.md))
    - orders ([lld/orders/README.md](lld/orders/README.md))
      - orders.py ([lld/orders/orders.md](lld/orders/orders.md)): line_total, order_total, validate, settle
      - test_orders.py ([lld/orders/test_orders.md](lld/orders/test_orders.md))
    - tools ([lld/tools/README.md](lld/tools/README.md))
      - plan.py ([lld/tools/plan.md](lld/tools/plan.md)): scan, main
      - gate.py ([lld/tools/gate.md](lld/tools/gate.md)): fail, read, count_tests, check, main
      - fanout.sh ([lld/tools/fanout.md](lld/tools/fanout.md)): top-level script
  - Data ([lld/data-dictionary.md](lld/data-dictionary.md))
    - _PRODUCTS, plan.json, analysis files
  - Outside systems ([hld/01-system-context.md](hld/01-system-context.md))
    - Payment partner settlement endpoint, Supplier product feed, GitHub, GitHub Actions
  - Reference ([reference/risks-and-surprises.md](reference/risks-and-surprises.md), [reference/open-questions.md](reference/open-questions.md), [reference/configuration.md](reference/configuration.md), [reference/glossary.md](reference/glossary.md))

<!-- cites README.md@61543f4e8ea18677f318b804951295e5b678b877 -->
