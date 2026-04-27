# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is a self-contained reference for the next session. It must be enough
to drive a single, complete `mcp__metaengine__generate_code` call for Java
without re-reading any external docs.

---

## 1. Tools exposed by this MCP

- `mcp__metaengine__metaengine_initialize` — returns the canonical guide. Optional `language` arg ("typescript" | "python" | "go" | "csharp" | "java" | "kotlin" | "groovy" | "scala" | "swift" | "php"). Pure-learning helper; no code emitted.
- `mcp__metaengine__generate_code` — **the workhorse**. Takes one structured JSON spec and writes compilable, fully-imported source files to disk.
- `mcp__metaengine__generate_graphql` — GraphQL SDL → code (out of scope here).
- `mcp__metaengine__generate_openapi` — OpenAPI spec → code (out of scope here).
- `mcp__metaengine__generate_protobuf` — `.proto` → code (out of scope here).
- `mcp__metaengine__generate_sql` — SQL DDL → code (out of scope here).
- `mcp__metaengine__load_spec_from_file` — loads an external spec.

For DDD-from-prose generation in Java, use `generate_code` only.

---

## 2. The cardinal rule (do not break it)

**Generate ALL related types in ONE call to `generate_code`.** `typeIdentifier`
references only resolve within the current batch. If `OrderService` references
`Order`, both must be in the same call. Splitting per-domain or per-aggregate
breaks the typegraph and produces broken imports.

Also cardinal:

- `properties[]` declares **typed fields, no logic**. `customCode[]` holds
  **methods, initialized fields, anything with a body**. One `customCode` item
  = exactly one member.
- Internal type references inside `customCode` must use `templateRefs` with
  `$placeholder` syntax — otherwise no import is generated.
- `templateRefs` are for types **inside the same call**. External library types
  use `customImports`. Never mix the two.
- Never duplicate a constructor parameter in `properties[]` (Java/C#/Go/Groovy
  auto-promote constructor params to properties; duplicating throws "Sequence
  contains more than one matching element").
- Never put framework/stdlib imports in `customImports`. The engine handles
  those automatically (see Java auto-import list below).
- Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`,
  `concreteGenericInterfaces`) **never produce files**; they only create
  reusable type references for use elsewhere.
- Reserved words in the target language (`class`, `delete`, `import`, `package`,
  `static`, etc.) must not be used as property names; substitute (`clazz`,
  `remove`, `importData`).

---

## 3. `generate_code` — full input schema

`language` is the only required field. Everything else is optional. Top-level
shape:

```jsonc
{
  "language": "java",                // required — enum (see §1 list)
  "packageName": "com.example.shop", // Java default: "com.metaengine.generated"
  "outputPath": ".",                 // default "."
  "skipExisting": true,              // default true (stub-friendly)
  "initialize": false,               // default false — auto default-init properties
  "dryRun": false,                   // default false — true returns code without writing
  "classes":              [ /* ClassDef[]    */ ],
  "interfaces":           [ /* InterfaceDef[] */ ],
  "enums":                [ /* EnumDef[]      */ ],
  "arrayTypes":           [ /* ArrayType[]    */ ], // virtual
  "dictionaryTypes":      [ /* DictType[]     */ ], // virtual
  "concreteGenericClasses":     [ /* … */ ],        // virtual
  "concreteGenericInterfaces":  [ /* … */ ],        // virtual
  "customFiles":          [ /* CustomFile[]   */ ]  // free-form file generation
}
```

### 3.1 ClassDef

```jsonc
{
  "name": "Order",                              // required, PascalCase
  "typeIdentifier": "order",                    // required, kebab-case-or-similar — referenced elsewhere
  "fileName": "Order",                          // optional override (no extension)
  "path": "domain/order",                       // optional dir under outputPath
  "comment": "Aggregate root for orders.",      // class-level doc comment
  "isAbstract": false,
  "baseClassTypeIdentifier": "base-entity",     // single base class
  "interfaceTypeIdentifiers": ["i-aggregate"],  // implements list
  "decorators": [
    { "code": "@Entity",                         "templateRefs": [] },
    { "code": "@Table(name = \"orders\")",        "templateRefs": [] }
  ],
  "customImports": [
    { "path": "jakarta.persistence", "types": ["Entity", "Table"] }
  ],
  "constructorParameters": [                    // becomes ctor + auto-properties (Java)
    { "name": "id",          "primitiveType": "String" },
    { "name": "customer",    "typeIdentifier": "customer" }
  ],
  "properties": [                               // additional fields ONLY (do NOT duplicate ctor params)
    {
      "name": "status",
      "typeIdentifier": "order-status",
      "isOptional": false,
      "isInitializer": false,
      "comment": "Current state of the order.",
      "decorators": [ { "code": "@NotNull", "templateRefs": [] } ],
      "type": "...",                            // raw type expression alternative
      "primitiveType": "String|Number|Boolean|Date|Any",  // OR primitive
      "templateRefs": [ /* if `type` uses $placeholders */ ],
      "commentTemplateRefs": [ /* if comment uses $placeholders */ ]
    }
  ],
  "genericArguments": [                         // makes this a generic class template
    {
      "name": "T",
      "constraintTypeIdentifier": "base-entity",  // Java: `T extends BaseEntity`
      "propertyName": "items",                    // creates `items` of type T
      "isArrayProperty": true                     // makes it List<T> instead
    }
  ],
  "customCode": [                               // ONE per member (method, init field, ctor body, etc.)
    {
      "code": "public BigDecimal total() { return items.stream().map($item::price).reduce(BigDecimal.ZERO, BigDecimal::add); }",
      "templateRefs": [
        { "placeholder": "$item", "typeIdentifier": "order-item" }
      ]
    }
  ]
}
```

A property entry must specify exactly one of: `primitiveType`, `typeIdentifier`,
or `type` (with `templateRefs` if `type` contains `$placeholders`).

### 3.2 InterfaceDef

Same shape as ClassDef minus class-only fields. Interfaces also support
`genericArguments`, `interfaceTypeIdentifiers` (extends-list of other
interfaces), `customCode` (for **method signatures**, not bodies — see §6),
`customImports`, `decorators`, `fileName`, `path`.

### 3.3 EnumDef

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "comment": "Lifecycle state of an order.",
  "fileName": "OrderStatus",
  "path": "domain/order",
  "members": [
    { "name": "Pending",   "value": 0 },
    { "name": "Paid",      "value": 1 },
    { "name": "Shipped",   "value": 2 },
    { "name": "Cancelled", "value": 3 }
  ]
}
```

Java: member names get language-aware idiomatic transformation to `ALL_CAPS`
(`Pending` → `PENDING`). The judge tolerates this — do not try to fight it by
manually capitalising in the spec.

### 3.4 ArrayType (virtual)

```jsonc
{ "typeIdentifier": "order-list",  "elementTypeIdentifier": "order" }
{ "typeIdentifier": "tag-list",    "elementPrimitiveType": "String" }
```

Reference via `"typeIdentifier": "order-list"` in any property/customCode slot.

### 3.5 DictType (virtual)

```jsonc
{
  "typeIdentifier": "score-map",
  "keyPrimitiveType": "String",
  "valuePrimitiveType": "Number"
}
```

Supports any combination of primitive/custom for both key and value
(`keyTypeIdentifier`, `valueTypeIdentifier`, `keyType` raw-string).

### 3.6 ConcreteGenericClass / ConcreteGenericInterface (virtual)

```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [ { "typeIdentifier": "user" } ]
}
```

Use the identifier as a `baseClassTypeIdentifier` to inherit `Repository<User>`
without creating a file for the closure.

### 3.7 CustomFile

For files that don't fit the class/interface/enum mould (utility files,
package-info, type aliases via Java records used as nominal types, etc.).

```jsonc
{
  "name": "package-info",
  "fileName": "package-info",
  "path": "domain/order",
  "identifier": "order-package-info",
  "customImports": [ /* … */ ],
  "customCode": [
    { "code": "// package summary", "templateRefs": [] }
  ]
}
```

The `identifier` lets other files import the file via `customImports.path =
"<identifier>"`; the engine resolves to a relative path.

---

## 4. Java specifics — what to do and what not to do

### 4.1 packageName

- Defaults to `com.metaengine.generated` if omitted. **Always set it explicitly**
  for non-trivial domain work.
- Drives both `package …;` declaration and the on-disk path: with
  `outputPath = "."` and `packageName = "com.example.shop"`, files land under
  `./src/main/java/com/example/shop/<path>/<File>.java`.
- `path` on a class/interface/enum becomes a sub-package suffix and a
  sub-folder. E.g. `path = "domain/order"` with `packageName = "com.example.shop"`
  produces files under `com.example.shop.domain.order` at
  `src/main/java/com/example/shop/domain/order/`.

### 4.2 File path layout

Generated tree for Java looks like:

```
<outputPath>/
└── src/main/java/
    └── com/example/shop/
        ├── BaseEntity.java                   ← no `path`
        ├── domain/order/
        │   ├── Order.java                    ← path: "domain/order"
        │   ├── OrderItem.java
        │   └── OrderStatus.java
        └── application/
            └── OrderService.java
```

Java is one-public-type-per-file, so each class/interface/enum gets its own
`.java` file named after `name` (or `fileName` if set).

### 4.3 Type mapping (primitives)

| `primitiveType` | Java type                         |
|-----------------|-----------------------------------|
| `String`        | `String`                          |
| `Number`        | `int` (whole-number default)      |
| `Boolean`       | `boolean`                         |
| `Date`          | `java.time.*` (e.g. `Instant` / `LocalDateTime`) — auto-imported |
| `Any`           | `Object`                          |

For non-integer numerics or precise money types, **don't** use `Number` and
expect `BigDecimal`. Instead use `"type": "BigDecimal"` directly — `java.math.*`
is auto-imported. Same for `long`: `"type": "long"`.

### 4.4 Collections

- `arrayTypes` resolve to `List<T>` in Java (the engine understands
  Java collection idioms). If you specifically want a different collection
  (Set, Map, Queue), spell it via `type` with templateRefs:
  `"type": "Set<$tag>"`, `"templateRefs": [{"placeholder": "$tag", "typeIdentifier": "tag"}]`.
- `dictionaryTypes` resolve to `Map<K, V>`.
- `java.util.*` and `java.util.stream.*` are auto-imported — do not list them
  in `customImports`.

### 4.5 Auto-imported in Java (NEVER add to `customImports`)

`java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`,
`jakarta.validation.*`, `jackson.*` (jackson-annotations and databind core
types). Adding these manually causes duplicate-import errors.

`customImports` is for everything else: Spring (`org.springframework.…`),
Lombok (`lombok.*`), MapStruct, your own external libraries, JPA non-jakarta
artefacts, etc.

### 4.6 Classes vs records

The schema does not expose an explicit `record` flag. Default emission is a
**class** with field-per-property and (when `constructorParameters` are given)
an explicit constructor that auto-promotes those parameters into private
fields. Getters/setters follow Java idioms.

If you need an immutable value type that reads as a record, model it with
`constructorParameters` only (no extra `properties[]`) — that gives the
"record-like" shape without the engine emitting the literal `record` keyword.
Treat the engine's class output as the canonical shape for this benchmark.

### 4.7 `customCode` for Java method bodies

- One entry per method. Include the full Java signature **and** the body.
  Example:

  ```jsonc
  {
    "code": "public void place($order order) { this.orders.add(order); }",
    "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }]
  }
  ```

- For unimplemented stubs use:

  ```jsonc
  {
    "code": "public $order findById(String id) { throw new UnsupportedOperationException(\"not implemented\"); }",
    "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }]
  }
  ```

- For initialized fields use a single line:

  ```jsonc
  { "code": "private final List<$item> items = new ArrayList<>();",
    "templateRefs": [{ "placeholder": "$item", "typeIdentifier": "order-item" }] }
  ```

- Auto-newlines are inserted between `customCode` blocks; do not add trailing
  blank lines inside a block.
- The judge tolerates idiomatic transformations such as
  `snake_case → camelCase` for method names and `ALL_CAPS` for enum members
  — write the spec naturally.

### 4.8 Interface method signatures

For interfaces that a class will `implements`, put method signatures in
`customCode` (no body, just the signature ending in `;`). Do NOT model methods
as function-typed properties — that produces duplicated declarations on the
implementing class. Example:

```jsonc
{
  "name": "OrderRepository",
  "typeIdentifier": "order-repository",
  "customCode": [
    { "code": "$order findById(String id);",
      "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] },
    { "code": "void save($order order);",
      "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] }
  ]
}
```

### 4.9 Constructor parameters caveat (CRITICAL for Java)

Constructor parameters auto-promote to private final fields. If you also list
the same field under `properties[]`, you'll get a duplicate-member error:

> Sequence contains more than one matching element

Rule: shared fields go in `constructorParameters` only. Additional fields not
exposed via the constructor go in `properties[]`.

### 4.10 Inheritance and generics in Java

- `baseClassTypeIdentifier` → `extends BaseEntity` (single inheritance).
- `interfaceTypeIdentifiers: ["i-foo", "i-bar"]` → `implements Foo, Bar`.
- `genericArguments` with `constraintTypeIdentifier` → `<T extends BaseEntity>`.
- Closing a generic for inheritance (e.g. `extends Repository<Order>`) uses
  `concreteGenericClasses`:

  ```jsonc
  "concreteGenericClasses": [{
    "identifier": "order-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{ "typeIdentifier": "order" }]
  }]
  ```
  Then on the subclass: `"baseClassTypeIdentifier": "order-repo-concrete"`.

### 4.11 Decorators / annotations

Use `decorators[].code`. Annotation imports must be in `customImports` (unless
they're in the auto-import set above — `jakarta.validation.*` and `jackson.*`
are already covered, so `@NotNull`, `@JsonProperty`, etc. need no
`customImports` entry).

```jsonc
"decorators": [
  { "code": "@Service" }                          // needs customImports for org.springframework.stereotype.Service
],
"customImports": [
  { "path": "org.springframework.stereotype", "types": ["Service"] }
]
```

If a decorator references an internal type, use `templateRefs` inside the
decorator entry just like inside `customCode`.

### 4.12 Reserved word avoidance

Don't use these as property/parameter names: `class`, `package`, `import`,
`static`, `final`, `default`, `enum`, `interface`, `new`, `return`, `void`,
`super`, `this`, `null`, `true`, `false`. Pick a safe synonym.

---

## 5. Output structure produced by the engine

For a successful Java generation:

- One file per class/interface/enum (and one per `customFile`).
- Path: `<outputPath>/src/main/java/<package-as-folders>/<path>/<Name>.java`.
- Each file has:
  - A `package …;` declaration matching `packageName` + `path`.
  - Only the imports it actually needs — auto-imports for the Java stdlib
    set above, plus any `customImports` you supplied, plus imports inferred
    from `templateRefs`/`typeIdentifier` references.
  - The type body assembled from `properties`, `constructorParameters`,
    `customCode`, decorators, generic arguments, base class, interfaces.
- Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGeneric*`) produce
  no files.

The response object summarises what was written. With `dryRun: true`, full
file contents are returned in the response — useful for review without
touching disk.

---

## 6. Common Java mistakes and how to dodge them

1. **Splitting the call by domain** → broken imports. Always one batch.
2. **Method body in `properties` or method signature as a function-typed
   property** → duplicated members on implementing class. Use `customCode`.
3. **Internal type as a raw string in `customCode`** → no import. Use
   `$placeholder` + `templateRefs`.
4. **Listing `java.util.List` or similar in `customImports`** → duplicate
   import error. Let the engine auto-import.
5. **Duplicating a `constructorParameter` under `properties`** → "Sequence
   contains more than one matching element". Pick exactly one home.
6. **Using `Number` and expecting `BigDecimal`** → you'll get `int`. Spell it
   via `"type": "BigDecimal"` (auto-imported from `java.math.*`).
7. **Using `Date` and expecting `java.util.Date`** → engine maps to
   `java.time.*` modern API (`Instant` / `LocalDateTime`). If you need legacy
   `java.util.Date`, spell `"type": "java.util.Date"` explicitly.
8. **Reserved-word property name** → compile error. Substitute.
9. **Generating the same `typeIdentifier` twice** → silently dropped reference.
   Each identifier must be unique within the call.
10. **Forgetting `packageName`** → defaults to `com.metaengine.generated`,
    which leaks the engine's name into your code.

---

## 7. Quick recipe — a minimal Java DDD generation

```jsonc
{
  "language": "java",
  "packageName": "com.example.shop",
  "outputPath": ".",
  "enums": [
    {
      "name": "OrderStatus", "typeIdentifier": "order-status",
      "path": "domain/order",
      "members": [
        { "name": "Pending",   "value": 0 },
        { "name": "Paid",      "value": 1 },
        { "name": "Shipped",   "value": 2 },
        { "name": "Cancelled", "value": 3 }
      ]
    }
  ],
  "classes": [
    {
      "name": "OrderItem", "typeIdentifier": "order-item",
      "path": "domain/order",
      "constructorParameters": [
        { "name": "sku",      "primitiveType": "String" },
        { "name": "quantity", "primitiveType": "Number" },
        { "name": "price",    "type": "BigDecimal" }
      ]
    },
    {
      "name": "Order", "typeIdentifier": "order",
      "path": "domain/order",
      "constructorParameters": [
        { "name": "id",        "primitiveType": "String" },
        { "name": "customerId","primitiveType": "String" }
      ],
      "properties": [
        { "name": "status", "typeIdentifier": "order-status" },
        { "name": "items",  "typeIdentifier": "order-item-list" }
      ],
      "customCode": [
        {
          "code": "public BigDecimal total() { return items.stream().map($item::price).reduce(BigDecimal.ZERO, BigDecimal::add); }",
          "templateRefs": [{ "placeholder": "$item", "typeIdentifier": "order-item" }]
        },
        {
          "code": "public void cancel() { this.status = $status.CANCELLED; }",
          "templateRefs": [{ "placeholder": "$status", "typeIdentifier": "order-status" }]
        }
      ]
    }
  ],
  "interfaces": [
    {
      "name": "OrderRepository", "typeIdentifier": "order-repository",
      "path": "domain/order",
      "customCode": [
        { "code": "$order findById(String id);",
          "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] },
        { "code": "void save($order order);",
          "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] }
      ]
    }
  ],
  "arrayTypes": [
    { "typeIdentifier": "order-item-list", "elementTypeIdentifier": "order-item" }
  ]
}
```

This produces:

```
src/main/java/com/example/shop/domain/order/
├── OrderStatus.java       (enum, members ALL_CAPS)
├── OrderItem.java         (class with ctor-promoted fields)
├── Order.java             (class with status/items, methods total()/cancel())
└── OrderRepository.java   (interface with findById/save)
```

with `java.util.List`, `java.math.BigDecimal`, and the cross-references all
auto-imported.

---

## 8. Final checklist before calling `generate_code` for Java

1. `language: "java"` set.
2. `packageName` set explicitly.
3. Every `typeIdentifier` referenced is also defined in this same call.
4. No `properties[]` entry duplicates a `constructorParameter`.
5. `customCode` is one method/field per entry; internal types via
   `$placeholder` + `templateRefs`.
6. `customImports` contains zero entries from the Java auto-import set
   (`java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`,
   `jakarta.validation.*`, `jackson.*`).
7. No reserved Java words used as identifiers.
8. Enum members in `members[]` are spelled naturally (PascalCase or
   ALL_CAPS) — the engine normalises to `ALL_CAPS`.
9. Run with `dryRun: true` first if uncertain about output paths.
