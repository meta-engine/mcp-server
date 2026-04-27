# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is the **only** documentation the next session will have. It is self-contained.

MetaEngine is a semantic code generation MCP. You describe types, relationships, methods as structured JSON; the engine emits compilable, correctly-imported source files for many languages including Java. Cross-file imports, generic instantiation, and language-idiomatic naming are resolved automatically. A single well-formed JSON call replaces dozens of file writes.

---

## Tools available

The metaengine MCP exposes:

- `mcp__metaengine__metaengine_initialize` — returns the canonical guide (already consumed in this warmup; no need to call again unless you want to re-read).
- `mcp__metaengine__generate_code` — the workhorse. Takes the JSON schema below and emits files.
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, `load_spec_from_file` — spec-conversion helpers (not needed for the DDD-from-spec task).

For Java DDD generation, you will use **only** `mcp__metaengine__generate_code`. **ONE call**, full spec.

---

## Top-level `generate_code` input schema

The root object accepts these top-level arrays/fields (every one optional, but you typically use several):

```jsonc
{
  "language": "java",            // REQUIRED. Lowercase. One of: typescript|csharp|python|go|java|kotlin|groovy|scala|swift|php
  "packageName": "com.example.shop",  // Java package — affects file path AND `package …;` header
  "initialize": false,           // (Default false. Some examples set true; not required.)
  "interfaces":  [...],          // emitted as Java interfaces
  "classes":     [...],          // emitted as Java classes (or records — see below)
  "enums":       [...],          // emitted as Java enums
  "arrayTypes":  [...],          // VIRTUAL — reusable List<T> references; no file produced
  "dictionaryTypes": [...],      // VIRTUAL — reusable Map<K,V> references; no file produced
  "concreteGenericClasses":    [...], // VIRTUAL — Foo<Bar> reusable references
  "concreteGenericInterfaces": [...], // VIRTUAL — IFoo<Bar> reusable references
  "customFiles": [...]           // arbitrary content files (rarely needed in Java DDD)
}
```

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are **virtual** — they create reusable typeIdentifiers but produce **no file**. Only `interfaces`, `classes`, `enums`, `customFiles` produce files.

### Common element fields (interfaces / classes / enums)

```jsonc
{
  "name": "User",                  // Pascal-cased Java type name
  "typeIdentifier": "user",        // string ID, MUST be unique in the batch — the only way to reference this type
  "fileName": "User",              // optional — override file name; default derived from name
  "path": "domain/user",           // optional — additional sub-path under the package root
  "comment": "Aggregate root.",    // optional — Javadoc emitted as /** … */
  "isAbstract": true,              // optional — emits `abstract` for class
  "decorators": [{"code": "@Entity"}],  // optional — Java annotations (raw); each item one line
  "customImports": [
    {"path": "com.fasterxml.jackson.annotation", "types": ["JsonIgnore"]}
  ],
  "properties": [...],
  "customCode":  [...],
  "constructorParameters": [...],  // class only
  "baseClassTypeIdentifier": "base-entity",        // class only — extends
  "baseInterfaceTypeIdentifiers": ["serializable"],// class/interface — implements/extends
  "genericArguments": [...]        // class/interface — generic type params (see Generics)
}
```

### `properties[]` element

```jsonc
{
  "name": "email",
  "primitiveType": "String",        // EITHER primitiveType ...
  "typeIdentifier": "address",      // ... OR typeIdentifier (refers to another type in the batch) ...
  "type": "Map<String, $addr>",     // ... OR raw `type` string (with optional templateRefs)
  "templateRefs": [
    {"placeholder": "$addr", "typeIdentifier": "address"}
  ],
  "isOptional": true,                // affects nullability — see notes
  "isReadOnly": true,                // affects setter generation in Java (final field, no setter)
  "comment": "User email address",
  "decorators": [{"code": "@NotBlank"}]  // field-level annotations
}
```

Allowed `primitiveType` values (canonical, mapped per language): `String`, `Number`, `Integer`, `Long`, `Decimal`, `Boolean`, `Date`, `DateTime`, `Time`, `UUID`, `Any`, `Bytes`. (See type mapping below.)

### `customCode[]` element

```jsonc
{
  "code": "public BigDecimal totalPrice() { return items.stream().map($item::getPrice).reduce(BigDecimal.ZERO, BigDecimal::add); }",
  "templateRefs": [
    {"placeholder": "$item", "typeIdentifier": "line-item"}
  ]
}
```

**One `customCode` item = exactly one Java member** (one method, one initialized field, etc.). Multiple methods → multiple items. Newlines between members are inserted automatically.

### `constructorParameters[]` (Java)

```jsonc
{
  "name": "email",
  "type": "String",                 // raw string, OR
  "typeIdentifier": "address",      // reference to another type, OR
  "primitiveType": "String"
}
```

**Java behavior**: constructor parameters **auto-create matching final fields/properties**. Do NOT also list them in `properties[]`. Doing so triggers `"Sequence contains more than one matching element"`.

### `genericArguments[]` (on the type definition)

```jsonc
{
  "name": "T",                          // Java type variable name
  "constraintTypeIdentifier": "base-entity",  // emits `T extends BaseEntity`
  "propertyName": "items",              // optional — generates a field of this name
  "isArrayProperty": true               // makes the auto-property a List<T>
}
```

### `concreteGenericClasses` / `concreteGenericInterfaces` element

```jsonc
{
  "identifier": "user-repo-concrete",      // its own typeIdentifier
  "genericClassIdentifier": "repo-generic",// or "genericInterfaceIdentifier"
  "genericArguments": [{"typeIdentifier": "user"}]
}
```

This creates a virtual `Repository<User>` reference. Use in `baseClassTypeIdentifier`, `properties`, or `templateRefs` to emit `Repository<User>` with imports.

### `arrayTypes` element

```jsonc
{"typeIdentifier": "user-list", "elementTypeIdentifier": "user"}
{"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
```

In Java, `arrayTypes` materialize as `List<T>` (NOT raw arrays). For DDD aggregates this is what you want.

### `dictionaryTypes` element

```jsonc
{"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"}
{"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
{"typeIdentifier": "user-meta", "keyTypeIdentifier": "user", "valueTypeIdentifier": "metadata"}
```

In Java, dictionaryTypes materialize as `Map<K, V>`.

### `enums[]` element

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "comment": "Lifecycle of an order",
  "members": [
    {"name": "Pending",   "value": 0,  "comment": "Not yet paid"},
    {"name": "Paid",      "value": 1},
    {"name": "Shipped",   "value": 2},
    {"name": "Cancelled", "value": 3}
  ]
}
```

For Java the engine emits `public enum OrderStatus { PENDING, PAID, SHIPPED, CANCELLED }` — note **idiomatic ALL_CAPS member names** even if you specify PascalCase. The judge harness has tolerance for this; do not "correct" it.

### `customFiles[]` element (rarely needed for DDD)

```jsonc
{
  "name": "package-info",
  "path": "domain",
  "identifier": "domain-package-info",   // optional — enables import resolution by identifier
  "customCode": [{"code": "package com.example.shop.domain;"}]
}
```

---

## Java-specific behaviors — READ CAREFULLY

### `packageName` and file paths

- `packageName` (e.g. `"com.example.shop"`) is REQUIRED for non-trivial Java output. It controls the `package …;` declaration AND the file path layout.
- The engine writes files to `src/main/java/com/example/shop/<path>/<TypeName>.java` (Maven/Gradle convention).
- A type with `"path": "domain/user"` and root `packageName: "com.example.shop"` lands at `src/main/java/com/example/shop/domain/user/User.java` and gets `package com.example.shop.domain.user;` automatically.
- **Do not** stick a manual `package …;` line into customCode — the engine emits it.

### Auto-imported (NEVER list these in `customImports`)

For Java, the engine auto-imports:

- `java.util.*` (List, Map, Set, Optional, UUID, Collection, Collections, Arrays, …)
- `java.time.*` (Instant, LocalDate, LocalDateTime, ZonedDateTime, Duration, …)
- `java.util.stream.*` (Stream, Collectors)
- `java.math.*` (BigDecimal, BigInteger)
- `jakarta.validation.*` (constraints: `@NotNull`, `@NotBlank`, `@Email`, `@Size`, …)
- Jackson annotations from `com.fasterxml.jackson.*`

Adding any of these to `customImports` causes duplicates / errors. Only use `customImports` for things outside that list (e.g., `org.springframework.stereotype.Service`, application packages).

### Type mapping (canonical primitiveType → Java)

| primitiveType | Java emitted type                                         |
|---------------|------------------------------------------------------------|
| `String`      | `String`                                                   |
| `Number`      | `Integer` (NOT `double`!) — for non-int use `"type": "BigDecimal"` or `"type": "Double"` |
| `Integer`     | `Integer`                                                  |
| `Long`        | `Long`                                                     |
| `Decimal`     | `BigDecimal`                                               |
| `Boolean`     | `Boolean`                                                  |
| `Date`        | `LocalDate` (date-only). For timestamps prefer `DateTime`. |
| `DateTime`    | `Instant` (UTC instant). If you need `LocalDateTime`, set `"type": "LocalDateTime"`. |
| `Time`        | `LocalTime`                                                |
| `UUID`        | `UUID`                                                     |
| `Any`         | `Object`                                                   |
| `Bytes`       | `byte[]`                                                   |

**Money / Decimal in DDD** — always use `Decimal` (→ `BigDecimal`), never `Number`.

**Identifiers in DDD** — `String` or `UUID`; pick one and be consistent.

`isOptional: true` on a property emits the field as `Optional<T>` only if you use `"type": "Optional<...>"` explicitly; otherwise the engine just emits the unwrapped type (Java has no nullable-marker like `?`). For DDD aggregates you usually do NOT want `Optional` fields — use validation annotations instead.

### Class vs record emission

- The engine emits **classes by default**, with private fields and standard getters/setters.
- `constructorParameters` produce a constructor whose params automatically become **`private final` fields** (i.e., immutable value-object style), with getters but no setters.
- The engine does NOT auto-emit `record` syntax. If you need a record, write it via `customCode` on a `customFiles` entry; for DDD value objects, the constructor-only pattern (constructorParameters + no setters) gets you immutable shape without needing records.
- `isReadOnly: true` on a `properties[]` field makes the field `private final` (no setter generated).

### `interfaces` in Java

- Java interfaces are emitted as `public interface Foo { … }`.
- Method signatures on an interface go in `customCode` as signature-only strings ending with `;`:
  ```jsonc
  "customCode": [
    {"code": "List<$user> findAll();",
     "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
    {"code": "Optional<$user> findById(UUID id);",
     "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
  ]
  ```
- Do NOT use function-typed properties (`"type": "() => ..."`) for Java method signatures.
- Java does NOT strip the `I` prefix (that's a TypeScript-only behavior). `IUserRepository` stays `IUserRepository`.

### `customCode` for method bodies / stubs

For DDD method stubs the idiomatic pattern is:

```jsonc
"customCode": [
  {"code": "public void confirm() { throw new UnsupportedOperationException(\"Not implemented\"); }"}
]
```

You can use templateRefs for any internal type referenced inside the body:

```jsonc
{
  "code": "public $order place($cart cart) { throw new UnsupportedOperationException(); }",
  "templateRefs": [
    {"placeholder": "$order", "typeIdentifier": "order"},
    {"placeholder": "$cart",  "typeIdentifier": "cart"}
  ]
}
```

The engine uses `templateRefs` to (a) substitute `$placeholder` with the resolved Java type name and (b) generate the `import` statement. **External library types** (`Stream`, `BigDecimal`, `Instant`, `Optional`, `List`, `UUID`, `@NotBlank`) are auto-imported and need NO templateRefs and NO customImports — just write them directly in the code string.

### Method naming

Java methods are camelCase (`getTotalPrice`, `confirmOrder`). The engine applies idiomatic transformation if you provide PascalCase, so it's safe either way; prefer writing methods in camelCase to match Java conventions.

### Decorators (annotations)

In Java, `decorators` emit annotations on the type or member. Each `decorators[]` item is one line:

```jsonc
"decorators": [
  {"code": "@Entity"},
  {"code": "@Table(name = \"users\")"}
]
```

Field-level annotations go inside `properties[i].decorators` or `constructorParameters[i].decorators`.

For validation annotations like `@NotBlank`, `@Email`, `@NotNull`, `@Size(...)` you can put them directly in `decorators`; jakarta.validation imports come for free.

### Inheritance / implementation

- `baseClassTypeIdentifier: "base-entity"` → emits `extends BaseEntity` and imports.
- `baseInterfaceTypeIdentifiers: ["aggregate-root", "serializable"]` → emits `implements AggregateRoot, Serializable` (or `extends Foo, Bar` if on an interface). For internal interfaces use the typeIdentifier from the same batch; `serializable` would need to be resolvable — if you want `java.io.Serializable`, declare it via `customImports` or simply leave it off.

### Generics

- On a type definition, `genericArguments` declare type variables: `Repository<T extends BaseEntity>`.
- `propertyName` + `isArrayProperty` on a generic argument auto-creates a backing field (`private List<T> items;`).
- `concreteGenericClasses` is how you reference `Repository<User>` from another class (in `baseClassTypeIdentifier`, `properties.typeIdentifier`, or `templateRefs`).

---

## DDD generation — recipe

A typical Java DDD spec maps to MetaEngine like this:

| DDD concept             | MetaEngine                                                                    |
|-------------------------|--------------------------------------------------------------------------------|
| Entity / Aggregate root | `classes[]` with id property; methods in `customCode`; `decorators` for `@Entity` if persisted. |
| Value object            | `classes[]` with `constructorParameters` only, no setters (immutable).         |
| Domain event            | `classes[]` with `constructorParameters` (immutable record-like).              |
| Enumeration             | `enums[]`.                                                                     |
| Repository (interface)  | `interfaces[]` with method signatures in `customCode`.                         |
| Domain service          | `classes[]` with methods (stubbed to `UnsupportedOperationException` if no logic given). |
| Collection field        | Reference an `arrayTypes` typeIdentifier, OR use `"type": "List<$item>"` with templateRefs. |
| Map / index             | `dictionaryTypes` typeIdentifier, OR `"type": "Map<String,$x>"` with templateRefs. |

### Sketch for a Java DDD generation call

```jsonc
{
  "language": "java",
  "packageName": "com.example.shop",

  "enums": [
    {"name": "OrderStatus", "typeIdentifier": "order-status",
     "members": [
       {"name": "Pending", "value": 0},
       {"name": "Paid", "value": 1},
       {"name": "Shipped", "value": 2},
       {"name": "Cancelled", "value": 3}
     ]}
  ],

  "classes": [
    {
      "name": "Money", "typeIdentifier": "money",
      "path": "domain/shared",
      "comment": "Value object representing an amount in a currency.",
      "constructorParameters": [
        {"name": "amount",   "primitiveType": "Decimal"},
        {"name": "currency", "primitiveType": "String"}
      ]
    },
    {
      "name": "LineItem", "typeIdentifier": "line-item",
      "path": "domain/order",
      "constructorParameters": [
        {"name": "productId", "primitiveType": "UUID"},
        {"name": "quantity",  "primitiveType": "Integer"},
        {"name": "price",     "typeIdentifier": "money"}
      ]
    },
    {
      "name": "Order", "typeIdentifier": "order",
      "path": "domain/order",
      "comment": "Aggregate root for the ordering bounded context.",
      "decorators": [{"code": "@Entity"}],
      "properties": [
        {"name": "id",     "primitiveType": "UUID",     "decorators": [{"code": "@Id"}]},
        {"name": "status", "typeIdentifier": "order-status"},
        {"name": "items",  "typeIdentifier": "line-item-list"},
        {"name": "placedAt", "primitiveType": "DateTime"}
      ],
      "customCode": [
        {"code": "public $money totalPrice() { throw new UnsupportedOperationException(\"Not implemented\"); }",
         "templateRefs": [{"placeholder": "$money", "typeIdentifier": "money"}]},
        {"code": "public void confirm() { throw new UnsupportedOperationException(\"Not implemented\"); }"},
        {"code": "public void cancel() { throw new UnsupportedOperationException(\"Not implemented\"); }"}
      ]
    }
  ],

  "arrayTypes": [
    {"typeIdentifier": "line-item-list", "elementTypeIdentifier": "line-item"}
  ],

  "interfaces": [
    {
      "name": "OrderRepository", "typeIdentifier": "order-repo",
      "path": "domain/order",
      "customCode": [
        {"code": "Optional<$order> findById(UUID id);",
         "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]},
        {"code": "List<$order> findAll();",
         "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]},
        {"code": "void save($order order);",
         "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]}
      ]
    }
  ]
}
```

Files emitted (under `src/main/java/com/example/shop/`):

- `domain/shared/Money.java`
- `domain/order/LineItem.java`
- `domain/order/Order.java`
- `domain/order/OrderStatus.java` (enum, ALL_CAPS members)
- `domain/order/OrderRepository.java` (interface)

---

## Cardinal rules — DO NOT VIOLATE

1. **ONE call.** Put the entire spec into a single `generate_code` invocation. `typeIdentifier` cross-references resolve only within one batch. Splitting per-domain or per-aggregate breaks the typegraph and produces files with missing imports or unresolved references.

2. **Properties = type declarations only. CustomCode = methods, initialized fields, anything with logic.** Never put a method in `properties[]`; never put an uninitialized field declaration in `customCode[]`. One `customCode` item == one Java member.

3. **Constructor parameters auto-create fields** (Java). Do NOT also list them in `properties[]`. Duplicates produce `"Sequence contains more than one matching element"`.

4. **Use templateRefs for cross-batch type references inside customCode strings.** Internal types referenced as raw names without templateRefs may not get imports. (For the Java standard library, no templateRefs needed — those are auto-imported.)

5. **Don't add Java standard-library imports to `customImports`.** `java.util.*`, `java.time.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` — all auto-imported. Listing them causes errors. `customImports` is only for things outside that list (Spring annotations, third-party libs).

6. **Don't reference an undefined `typeIdentifier`.** A property pointing to a missing typeIdentifier is silently dropped. Every `typeIdentifier` you reference must correspond to a `typeIdentifier` defined somewhere in the batch — `classes[]`, `interfaces[]`, `enums[]`, `arrayTypes[]`, `dictionaryTypes[]`, `concreteGenericClasses[]`, `concreteGenericInterfaces[]`, or `customFiles[]` (with `identifier`).

7. **Virtual types don't produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` exist only as reusable type references. They never emit a `.java` file.

8. **Don't use Java reserved words as identifiers.** `class`, `import`, `package`, `interface`, `enum`, `final`, `volatile`, etc. The engine doesn't sanitize these.

9. **Idiomatic transformations are intentional.** Enum members become ALL_CAPS, methods are camelCase. The judge tolerates these. Do not "fight" the engine by trying to force PascalCase enum members.

10. **`Number` → `Integer` in Java**, not `Double` or `BigDecimal`. For money use `Decimal`; for floating point set `"type": "Double"` explicitly.

11. **No fallbacks / no manual file edits after generation.** If output is wrong, the issue is in the spec; fix the JSON and re-run.

---

## Common Java pitfalls — preempted

- **Aggregate root with collection of value objects** → use `arrayTypes` with `elementTypeIdentifier`, then reference it via `typeIdentifier` in the aggregate's `properties`. Don't try to inline `List<LineItem>` as a raw `type` string unless using templateRefs.
- **Money / amount field** → primitiveType `Decimal` (→ `BigDecimal`). NEVER `Number`.
- **Timestamp field** → primitiveType `DateTime` (→ `Instant`). For local datetime use `"type": "LocalDateTime"` (auto-imported).
- **Optional fields** → in DDD prefer `@Nullable` annotation or just the unwrapped type with documentation, not `Optional<T>` as a field type. If you DO want `Optional<T>` as a field, set `"type": "Optional<String>"`.
- **Repository as interface** → put method signatures in `customCode` with trailing `;`, not as function-typed properties.
- **Domain method stubs** → method body in `customCode` like `public Money totalPrice() { throw new UnsupportedOperationException("Not implemented"); }`.
- **Cross-aggregate references by ID, not by object** → use `UUID` (or `String`) properties, not a `typeIdentifier` reference, when the spec calls for ID-only references.
- **Bounded contexts** → use `path` field on each type to mirror the DDD package structure (`domain/order`, `domain/customer`, etc.).

---

## Output structure (what generate_code returns)

The tool returns a list of generated files, each with:
- relative path under `src/main/java/<packageName-as-path>/`
- file name (e.g. `Order.java`)
- full contents (with `package …;` header, automatic imports, and the body)

The MCP itself does NOT write to disk in some setups — read the tool's response to see whether it returned file contents or wrote files. In this benchmark harness, treat the tool result as authoritative; the generated files are what get judged.

---

## Quick mental checklist before calling generate_code

- [ ] `language: "java"` set
- [ ] `packageName` set (e.g. `com.example.shop`)
- [ ] Every aggregate / entity / VO is a class with the right typeIdentifier
- [ ] Every enum is in `enums[]`
- [ ] Every repository is an interface with method signatures in `customCode`
- [ ] All cross-references use existing `typeIdentifier`s
- [ ] No constructor parameter is duplicated in properties
- [ ] No `java.util.*` / `java.time.*` / `java.math.*` / `jakarta.validation.*` listed in customImports
- [ ] Money fields are `Decimal`, not `Number`
- [ ] All collections use `arrayTypes` (or templateRefs into `List<>`)
- [ ] All method bodies are in customCode, one per item

ONE CALL. FULL SPEC. Then trust the output.
