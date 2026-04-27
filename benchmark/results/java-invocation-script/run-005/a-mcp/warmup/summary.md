# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is self-contained. The next session will generate **Java** code from a DDD spec using a single `mcp__metaengine__generate_code` call. All knowledge needed to call the tool correctly is below.

---

## Tools exposed by the metaengine MCP server

- `mcp__metaengine__metaengine_initialize` — returns the AI guide; takes optional `language`. Don't call it during generation.
- `mcp__metaengine__generate_code` — **THE generator**. Takes a structured JSON spec and writes compilable source files to disk (or returns them when `dryRun: true`).
- Other generators: `generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, `load_spec_from_file` — not used for DDD code generation.

There are two MCP resources containing canonical documentation:
- `metaengine://guide/ai-assistant` (rules, patterns, language notes, common mistakes)
- `metaengine://guide/examples` (worked input/output examples)

---

## What MetaEngine is (one paragraph)

MetaEngine is a *semantic* code generator. You describe types, fields, relationships, and method bodies as JSON. MetaEngine resolves cross-type references, manages imports, applies language idioms (e.g. Java `ALL_CAPS` enums, Java `snake_case`/`camelCase` conventions), and emits compilable files. **One well-formed JSON call replaces dozens of error-prone file writes.** Cross-references resolve only inside a single call, so all related types must be in the same call.

---

## `generate_code` — full input schema

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | YES | `"java"` for this run. Also: typescript, python, go, csharp, kotlin, groovy, scala, swift, php, rust. |
| `packageName` | string | recommended for Java | Java default = `com.metaengine.generated`. Sets the package declaration AND directory layout. |
| `outputPath` | string | optional | Output directory; defaults to `.` (cwd). Files land at `<outputPath>/<package-as-dirs>/<path>/<File>.java` for Java. |
| `initialize` | boolean | optional | If true, initialize properties with default values. |
| `dryRun` | boolean | optional | If true, return file contents in the response without writing to disk. |
| `skipExisting` | boolean | optional, default true | If true, skip writing existing files (stub pattern). |
| `classes` | array | — | Class definitions (regular and generic templates). |
| `interfaces` | array | — | Interface definitions (regular and generic templates). |
| `enums` | array | — | Enum definitions. |
| `arrayTypes` | array | — | Reusable array type refs (no files emitted). |
| `dictionaryTypes` | array | — | Reusable map/dictionary type refs (no files emitted). |
| `concreteGenericClasses` | array | — | Inline `Foo<Bar>` references (no files emitted). |
| `concreteGenericInterfaces` | array | — | Inline `IFoo<Bar>` references (no files emitted). |
| `customFiles` | array | — | Free-form files (utility, type aliases, barrel exports). |

### Class entry shape

```jsonc
{
  "name": "User",                              // required — class name
  "typeIdentifier": "user",                    // unique id used by other entries to reference this class
  "fileName": "User",                          // optional — overrides file name
  "path": "domain/user",                       // optional — sub-directory under the package
  "comment": "User aggregate root",            // optional — class-level Javadoc

  "isAbstract": false,                         // optional
  "baseClassTypeIdentifier": "base-entity",    // refers to another class's typeIdentifier (or to a concreteGeneric*)
  "interfaceTypeIdentifiers": ["aggregate"],   // refers to interface typeIdentifiers

  "genericArguments": [                        // makes this a generic class template (Repository<T>)
    {
      "name": "T",
      "constraintTypeIdentifier": "base-entity",
      "propertyName": "items",                 // optional auto-property of type T
      "isArrayProperty": true                  // type T[] / List<T>
    }
  ],

  "constructorParameters": [                   // params auto-become properties in Java/C#/Go/Groovy — DO NOT also list in properties[]
    {"name": "id", "primitiveType": "String"},
    {"name": "address", "typeIdentifier": "address"},
    {"name": "tags", "type": "List<String>"}
  ],

  "properties": [                              // additional fields (non-constructor)
    {
      "name": "createdAt",
      "primitiveType": "Date",                 // String | Number | Boolean | Date | Any
      // OR:
      // "typeIdentifier": "address",          // reference to another generated type
      // "type": "Map<String, $resp>",         // raw type expression with templateRefs

      "comment": "Created at timestamp",
      "commentTemplateRefs": [],
      "isOptional": false,
      "isInitializer": false,
      "decorators": [
        {"code": "@NotNull"},
        {"code": "@Size(max = 100)"}
      ],
      "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
    }
  ],

  "decorators": [                              // class-level annotations
    {"code": "@Entity"},
    {"code": "@Table(name = \"users\")"}
  ],

  "customImports": [                           // ONLY for external libs — never java.* / jakarta.validation.* / jackson.*
    {"path": "org.springframework.stereotype", "types": ["Service"]}
  ],

  "customCode": [                              // methods + initialized fields. ONE member per entry.
    {
      "code": "public $user findByEmail(String email) { return repo.findByEmail(email); }",
      "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
    }
  ]
}
```

### Interface entry shape

Same as class but no `constructorParameters`, no `isAbstract`. Interfaces use `interfaceTypeIdentifiers` to extend other interfaces. Method signatures go in `customCode` (terminated with `;` for Java).

### Enum entry shape

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "fileName": "OrderStatus",
  "path": "domain/order",
  "comment": "Order lifecycle status",
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2}
  ]
}
```

For Java the engine applies idiomatic transformation: enum members emit as `ALL_CAPS` (e.g. `PENDING`, `SHIPPED`).

### arrayTypes / dictionaryTypes (virtual — no files)

```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
  {"typeIdentifier": "tag-list",  "elementPrimitiveType": "String"}
],
"dictionaryTypes": [
  {"typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-by-id",  "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
  {"typeIdentifier": "user-meta",   "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata"}
]
```

Reference these via `typeIdentifier` in property definitions. They expand to language-idiomatic collection types.

### concreteGenericClasses / concreteGenericInterfaces (virtual)

```jsonc
"concreteGenericClasses": [{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}]
```

Used to bind a generic template to a concrete type, e.g. `Repository<User>`. Reference the `identifier` from `baseClassTypeIdentifier`, `interfaceTypeIdentifiers`, or templateRefs.

### customFiles

```jsonc
"customFiles": [{
  "name": "Constants",
  "path": "shared",
  "identifier": "shared-constants",
  "customCode": [{"code": "public static final String VERSION = \"1.0\";"}]
}]
```

Generates a free-form file (not wrapped in a class). Java usage is unusual but possible for top-level utility constants.

---

## Java-specific behaviour

### packageName → package declaration AND directory layout

- Default Java package: `com.metaengine.generated`.
- The package becomes both the `package` statement at the top of every file AND the directory tree under `outputPath`. So `outputPath = "out/"` + `packageName = "com.acme.shop"` + a class `path = "domain/order"` produces `out/com/acme/shop/domain/order/Order.java`.
- The `path` field on a class adds sub-package segments under the base package (some engine versions emit them as nested package declarations; either way the file lands inside the directory).
- Set `packageName` once at the top level — it applies to every emitted file.

### File path & naming

- `<outputPath>/<packageDirs>/<path?>/<ClassName>.java`
- `name` → `ClassName.java` (PascalCase). Use `fileName` only if you need an exact override.
- Enums emit as `EnumName.java`.

### Auto-imported (NEVER add to customImports)

The Java emitter automatically imports from these packages as needed:
- `java.util.*` (List, Map, Set, Optional, UUID, Date, etc.)
- `java.time.*` (Instant, LocalDate, LocalDateTime, ZonedDateTime, Duration, etc.)
- `java.util.stream.*` (Stream, Collectors)
- `java.math.*` (BigDecimal, BigInteger)
- `jakarta.validation.*` (`@NotNull`, `@Size`, `@Email`, etc.)
- `jackson.*` (Jackson annotations and ObjectMapper utilities)

Never list any of those in `customImports`. Use `customImports` ONLY for non-stdlib third-party libs (Spring, Lombok, Hibernate, MapStruct, etc.).

### Type mapping (Java)

| spec | emitted |
|---|---|
| `"primitiveType": "String"` | `String` |
| `"primitiveType": "Number"` | `int` (integer default — for non-integer use `"type": "double"` or `"type": "BigDecimal"`) |
| `"primitiveType": "Boolean"` | `boolean` (or `Boolean` if optional) |
| `"primitiveType": "Date"` | `java.time.Instant` (auto-imported) |
| `"primitiveType": "Any"` | `Object` |
| `"typeIdentifier": "user"` | `User` (with import resolved) |
| `arrayTypes` reference | `List<T>` |
| `dictionaryTypes` reference | `Map<K, V>` |

If you need a specific numeric type, set `"type": "BigDecimal"`, `"type": "long"`, `"type": "double"`, etc. — these bypass the `primitiveType` mapping.

For UUIDs explicitly: `"type": "UUID"` (java.util.UUID auto-imports).

### Class vs record emission

- The Java emitter produces **classes** by default (with constructor parameters becoming fields, getters/setters per engine defaults).
- Records are not auto-emitted from a flag in this schema; if a Java record is needed, the safest practice is a normal class with `constructorParameters` (which serves the same DTO role with auto-fields) — or use `customCode` for a record-shaped declaration.
- Default: pass DDD value objects and entities as classes. Don't try to toggle records mid-spec.

### Constructor parameters auto-create fields (Java)

This is the rule that bites most often:

```jsonc
// CORRECT
"constructorParameters": [
  {"name": "id", "primitiveType": "String"},
  {"name": "email", "primitiveType": "String"}
],
"properties": [
  {"name": "createdAt", "primitiveType": "Date"}   // ONLY non-constructor extras
]
```

Listing the same field in both produces `Sequence contains more than one matching element`.

### Method stubs in `customCode`

DDD aggregates often need method *signatures* with bodies that throw or are minimal. Idiomatic Java stubs:

```jsonc
"customCode": [
  {
    "code": "public $user findByEmail(String email) { throw new UnsupportedOperationException(\"not implemented\"); }",
    "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
  },
  {
    "code": "public void deactivate() { this.active = false; }"
  },
  {
    "code": "public List<$order> getOpenOrders() { return List.of(); }",
    "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
  }
]
```

Rules for `customCode` in Java:
- **One member per entry.** One method, one initialized field, or one annotation block.
- Each block gets blank-line separation automatically.
- Use `$placeholder` + `templateRefs` for *every* in-batch type reference. Without templateRefs, the import is not added.
- Java method signatures end with `{ ... }` (a body). Interface method signatures end with `;`.
- Use idiomatic Java method names: `camelCase`. The engine is lenient with naming style transforms.

### Interfaces with method signatures

```jsonc
{
  "name": "UserRepository",
  "typeIdentifier": "user-repository",
  "customCode": [
    {
      "code": "Optional<$user> findById(String id);",
      "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
    },
    {
      "code": "List<$user> findAll();",
      "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
    }
  ]
}
```

Then a class implements it via `"interfaceTypeIdentifiers": ["user-repository"]`.

### Validation & framework annotations

Use `decorators` on the class or property to add Java annotations:

```jsonc
"decorators": [{"code": "@Entity"}, {"code": "@Table(name = \"orders\")"}]

"properties": [{
  "name": "email",
  "primitiveType": "String",
  "decorators": [
    {"code": "@NotNull"},
    {"code": "@Email"}
  ]
}]
```

`jakarta.validation.*` and Jackson annotations auto-import. Spring annotations need an entry in `customImports`:

```jsonc
"customImports": [
  {"path": "org.springframework.stereotype", "types": ["Service"]}
]
```

---

## Critical rules (recapped, in priority order)

1. **ONE call with the full spec.** `typeIdentifier` references resolve only inside the current batch. Splitting the DDD spec across multiple calls breaks the typegraph and produces broken/missing imports.
2. **Properties are *type declarations only*.** Anything with logic, initialization, or a method goes in `customCode`. One member per `customCode` entry.
3. **Use templateRefs for every internal type referenced inside a `code` string.** Without `$placeholder` + `templateRefs`, the import is not generated even if the type exists in the batch. Raw type names in code strings are silently un-imported.
4. **Don't add Java stdlib imports to `customImports`.** `java.util.*`, `java.time.*`, `java.math.*`, `jakarta.validation.*`, Jackson — all auto. `customImports` is only for third-party libs.
5. **Do not duplicate constructor parameters in `properties[]`.** In Java, constructor params already become fields.
6. **Virtual types never produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reference-only.
7. **Reserved words.** Avoid `class`, `interface`, `import`, `package`, `enum`, `default`, `record`, `static`, `final`, `private`, `public`, etc. as property names. Use safe alternatives.
8. **Verify every `typeIdentifier`.** A reference to a non-existent identifier is silently dropped from the property — the field disappears in the output without an error.
9. **Number → int.** If you want a non-integer numeric, use `"type": "double"` / `"type": "BigDecimal"` / `"type": "long"` instead of `"primitiveType": "Number"`.
10. **Set `packageName` explicitly** (e.g. `com.example.shop`). Don't rely on the default `com.metaengine.generated` for real specs.

---

## Output structure (Java)

For an input like:

```jsonc
{
  "language": "java",
  "packageName": "com.example.shop",
  "outputPath": "out",
  "classes": [
    {"name": "User",  "typeIdentifier": "user",  "path": "domain/user",  "constructorParameters": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Order", "typeIdentifier": "order", "path": "domain/order", "properties": [{"name": "buyer", "typeIdentifier": "user"}]}
  ]
}
```

You get:

```
out/
  com/example/shop/
    domain/
      user/
        User.java
      order/
        Order.java
```

Each file declares its package, imports any cross-referenced types automatically, and includes the requested fields/methods.

---

## Worked example — DDD-shaped Java spec

Below is a representative shape for a small DDD bounded context. **Use this as the structural template** for the upcoming gen call. Adapt names/fields to whatever the actual spec demands.

```jsonc
{
  "language": "java",
  "packageName": "com.example.ordering",
  "outputPath": "out",

  "enums": [{
    "name": "OrderStatus",
    "typeIdentifier": "order-status",
    "path": "domain/order",
    "members": [
      {"name": "Pending",   "value": 0},
      {"name": "Confirmed", "value": 1},
      {"name": "Shipped",   "value": 2},
      {"name": "Cancelled", "value": 3}
    ]
  }],

  "classes": [
    {
      "name": "Money",
      "typeIdentifier": "money",
      "path": "domain/shared",
      "comment": "Value object: amount + currency",
      "constructorParameters": [
        {"name": "amount",   "type": "BigDecimal"},
        {"name": "currency", "primitiveType": "String"}
      ],
      "customCode": [
        {
          "code": "public $money add($money other) { return new Money(this.amount.add(other.amount), this.currency); }",
          "templateRefs": [{"placeholder": "$money", "typeIdentifier": "money"}]
        }
      ]
    },
    {
      "name": "Customer",
      "typeIdentifier": "customer",
      "path": "domain/customer",
      "constructorParameters": [
        {"name": "id",    "primitiveType": "String"},
        {"name": "email", "primitiveType": "String"}
      ],
      "properties": [
        {"name": "createdAt", "primitiveType": "Date"}
      ],
      "decorators": [{"code": "@Entity"}]
    },
    {
      "name": "OrderLine",
      "typeIdentifier": "order-line",
      "path": "domain/order",
      "constructorParameters": [
        {"name": "productId", "primitiveType": "String"},
        {"name": "quantity",  "primitiveType": "Number"},
        {"name": "price",     "typeIdentifier": "money"}
      ]
    },
    {
      "name": "Order",
      "typeIdentifier": "order",
      "path": "domain/order",
      "comment": "Order aggregate root",
      "constructorParameters": [
        {"name": "id",       "primitiveType": "String"},
        {"name": "customer", "typeIdentifier": "customer"},
        {"name": "status",   "typeIdentifier": "order-status"}
      ],
      "properties": [
        {"name": "lines",     "typeIdentifier": "order-line-list"},
        {"name": "createdAt", "primitiveType": "Date"}
      ],
      "customCode": [
        {
          "code": "public void addLine($line line) { this.lines.add(line); }",
          "templateRefs": [{"placeholder": "$line", "typeIdentifier": "order-line"}]
        },
        {
          "code": "public $money total() { return lines.stream().map(l -> l.getPrice()).reduce(new Money(BigDecimal.ZERO, \"USD\"), Money::add); }",
          "templateRefs": [{"placeholder": "$money", "typeIdentifier": "money"}]
        },
        {
          "code": "public void confirm() { this.status = OrderStatus.CONFIRMED; }"
        }
      ]
    }
  ],

  "arrayTypes": [
    {"typeIdentifier": "order-line-list", "elementTypeIdentifier": "order-line"}
  ],

  "interfaces": [
    {
      "name": "OrderRepository",
      "typeIdentifier": "order-repository",
      "path": "domain/order",
      "customCode": [
        {
          "code": "Optional<$order> findById(String id);",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
        },
        {
          "code": "List<$order> findByCustomerId(String customerId);",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
        },
        {
          "code": "void save($order order);",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
        }
      ]
    }
  ]
}
```

This produces:
- `out/com/example/ordering/domain/order/OrderStatus.java` (enum, members `PENDING`, `CONFIRMED`, `SHIPPED`, `CANCELLED`)
- `out/com/example/ordering/domain/shared/Money.java`
- `out/com/example/ordering/domain/customer/Customer.java`
- `out/com/example/ordering/domain/order/OrderLine.java`
- `out/com/example/ordering/domain/order/Order.java`
- `out/com/example/ordering/domain/order/OrderRepository.java`

All with correct `package` declarations, all cross-imports auto-resolved, `BigDecimal` / `Optional` / `List` auto-imported.

---

## Common mistakes (Java edition)

1. **Splitting per-domain calls.** Always one call. Cross-imports break otherwise.
2. **`primitiveType: "Number"` for monetary amounts.** Emits `int`. Use `"type": "BigDecimal"`.
3. **Adding `java.util.List` to customImports.** Don't — it's auto.
4. **Forgetting `templateRefs` in customCode.** The import won't be generated even though the type exists in the batch.
5. **Listing constructor params again in properties.** `Sequence contains more than one matching element`.
6. **Method signatures in `properties` instead of `customCode`.** Properties are field-only.
7. **Using `delete` / `class` / `default` as property names.** Reserved.
8. **Multiple methods crammed into one `customCode` entry.** One member per entry — split them.
9. **Trying to mutate `packageName` mid-call.** It's global to the call.
10. **Forgetting `language: "java"`.** Without it, the engine has no idea what to emit.

---

## Quick reference — call shape

```jsonc
{
  "language": "java",
  "packageName": "com.example.foo",
  "outputPath": "out",
  "classes":    [ /* ... */ ],
  "interfaces": [ /* ... */ ],
  "enums":      [ /* ... */ ],
  "arrayTypes":      [ /* ... */ ],
  "dictionaryTypes": [ /* ... */ ],
  "concreteGenericClasses":    [ /* ... */ ],
  "concreteGenericInterfaces": [ /* ... */ ],
  "customFiles": [ /* ... */ ]
}
```

ONE call. ALL types. ALL templateRefs in place. NO stdlib imports in `customImports`. NO duplicated constructor params. Numeric defaults to `int` — be explicit otherwise.
