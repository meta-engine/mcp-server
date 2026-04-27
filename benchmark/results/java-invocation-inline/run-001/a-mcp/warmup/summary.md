# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is everything the next session needs to call `mcp__metaengine__generate_code` for a Java target without re-reading the canonical docs. It is derived from `metaengine_initialize(language: "java")`, the `metaengine://guide/ai-assistant` resource, the `metaengine://guide/examples` resource, and the introspected JSON Schema of `generate_code`.

---

## 1. What MetaEngine MCP is

A **semantic** code generator (not a templater). You describe types, relationships, properties, and method bodies as structured JSON; MetaEngine resolves cross-references, picks the right collection/idiom for the language, manages every import, and emits compilable source files. It supports TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust.

For Java specifically, this means: package declarations, `import java.util.List`, `import java.time.Instant`, etc. are emitted automatically based on usage — you must NOT add framework imports manually.

---

## 2. Tools exposed by the server

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns the AI guide (language-tailored if `language` is passed). Optional `language` enum: `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php`. Read-only; safe to call any time. |
| `mcp__metaengine__generate_code` | The workhorse. Generates files from a structured spec. Always set `language: "java"`. |
| `mcp__metaengine__generate_openapi` / `generate_graphql` / `generate_protobuf` / `generate_sql` | Convert specs of those formats into the same structured spec model and generate code. Not required for the DDD-spec task. |
| `mcp__metaengine__load_spec_from_file` | Load a JSON spec from disk. Not needed for inline generation. |

MCP **resources** (read via `ReadMcpResourceTool` / server `metaengine`):
- `metaengine://guide/ai-assistant` — full AI guide.
- `metaengine://guide/examples` — six worked examples.

---

## 3. `generate_code` — full input schema

### Top-level fields

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `language` | enum | YES | — | Use `"java"`. |
| `packageName` | string | no | `com.metaengine.generated` | Java root package. Becomes `package x.y.z;` declaration AND drives the on-disk path layout (`com/metaengine/generated/...`). |
| `outputPath` | string | no | `"."` | Directory where files are written. Java sources land at `<outputPath>/<packageDir>/<File>.java`. (No `src/main/java` prefix is added by the engine; if the project expects Maven layout, set `outputPath` to that root.) |
| `dryRun` | bool | no | `false` | Returns generated file contents in the response without touching disk. Useful for inspection. |
| `initialize` | bool | no | `false` | Initialize properties with default values. |
| `skipExisting` | bool | no | `true` | If a file already exists at the target path, do NOT overwrite. Useful for the "stub" pattern (re-run to fill new types but preserve hand-edited bodies). Set `false` to overwrite. |
| `classes` | array | no | — | Concrete classes (regular & generic). Generates files. |
| `interfaces` | array | no | — | Interfaces (regular & generic). Generates files. |
| `enums` | array | no | — | Enums. Generates files. |
| `customFiles` | array | no | — | Free-form files (utility funcs, type aliases, barrel exports, package-info, etc.). Generates files WITHOUT a class wrapper. |
| `arrayTypes` | array | no | — | **Virtual** array type definitions; NO files generated. Reusable references like `List<User>`. |
| `dictionaryTypes` | array | no | — | **Virtual** map definitions; NO files generated. |
| `concreteGenericClasses` | array | no | — | **Virtual** concrete generic classes (e.g. `Repository<User>`); NO files generated. |
| `concreteGenericInterfaces` | array | no | — | **Virtual** concrete generic interfaces (e.g. `IRepository<User>`); NO files generated. |

### `classes[*]` shape

```
{
  "name": "User",                      // required: class name
  "typeIdentifier": "user",            // required: stable cross-reference key (kebab-case convention)
  "path": "domain/users",              // optional: subdir under packageName (also extends the Java package)
  "fileName": "MyUser",                // optional: override file name (no extension)
  "comment": "...",                    // class-level Javadoc
  "isAbstract": true|false,
  "baseClassTypeIdentifier": "base-entity",                 // extends
  "interfaceTypeIdentifiers": ["printable","serializable"], // implements (multiple OK)
  "genericArguments": [
    {
      "name": "T",                                          // generic param name
      "constraintTypeIdentifier": "base-entity",            // T extends BaseEntity
      "propertyName": "items",                              // auto-create field of type T (or T[])
      "isArrayProperty": true                               // -> List<T> field
    }
  ],
  "constructorParameters": [
    { "name": "email", "primitiveType": "String" },
    { "name": "status", "typeIdentifier": "status" },
    { "name": "tags", "type": "List<String>" }              // free-form 'type' string
  ],
  "properties": [
    {
      "name": "createdAt",
      "primitiveType": "Date",        // String|Number|Boolean|Date|Any
      "typeIdentifier": "...",        // OR reference an internal type
      "type": "BigDecimal",           // OR a free-form type string
      "isOptional": true,
      "isInitializer": true,           // emit a default initializer
      "comment": "Creation timestamp",
      "templateRefs": [{"placeholder":"$x","typeIdentifier":"x"}],
      "decorators": [
        {"code":"@NotNull"},
        {"code":"@Size(max=100)"}
      ]
    }
  ],
  "customCode": [
    { "code": "public String greet() { return \"hi \" + email; }" },
    {
      "code": "public Optional<$user> findSelf() { return Optional.of(this); }",
      "templateRefs": [{"placeholder":"$user","typeIdentifier":"user"}]
    }
  ],
  "decorators": [
    {"code":"@Entity"},
    {"code":"@Table(name = \"users\")"}
  ],
  "customImports": [
    {"path":"org.springframework.stereotype","types":["Service"]}
  ]
}
```

### `interfaces[*]` shape
Same structure as classes but most members appear in the body as method signatures. Method signatures (`doThing(): T;`) belong in `customCode`, NOT as function-typed properties — otherwise the implementing class will duplicate them.

### `enums[*]` shape
```
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "fileName": "OrderStatus",          // optional
  "path": "domain/orders",            // optional
  "comment": "...",
  "members": [
    {"name":"Pending","value":0},
    {"name":"Shipped","value":2}
  ]
}
```
For Java, the engine applies idiomatic transformation: enum member names are emitted as `ALL_CAPS` (e.g., `Pending` → `PENDING`). Don't fight this; the judge tolerates it.

### `customFiles[*]` shape
```
{
  "name": "package-info",            // base file name
  "fileName": "package-info",        // optional override
  "path": "domain",                  // subdir
  "identifier": "domain-pkg-info",   // optional id so other files can customImports it
  "customCode": [
    {"code": "package com.example.domain;"}
  ],
  "customImports": [...]
}
```
Use this for `package-info.java`, constant holders, factory utility files, or anything not modeled as a class/interface/enum.

### `arrayTypes[*]` (virtual, no file)
```
{
  "typeIdentifier": "user-list",
  "elementTypeIdentifier": "user"           // reference an internal type
  // OR
  "elementPrimitiveType": "String"          // String|Number|Boolean|Date|Any
}
```
Reference `user-list` from a property's `typeIdentifier` to get a `List<User>` field with the import auto-added.

### `dictionaryTypes[*]` (virtual, no file)
```
{
  "typeIdentifier": "scores",
  "keyPrimitiveType": "String",             // OR keyTypeIdentifier
  "valuePrimitiveType": "Number"            // OR valueTypeIdentifier
}
```
All four key/value combinations (prim/prim, prim/custom, custom/prim, custom/custom) are supported. Emits `Map<K,V>` with `java.util.Map` auto-import.

### `concreteGenericClasses[*]` / `concreteGenericInterfaces[*]` (virtual, no file)
```
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",         // points at the generic class definition
  "genericArguments": [
    {"typeIdentifier":"user"},                      // OR primitiveType
    {"primitiveType":"String"}
  ]
}
```
Use these when you need `Repository<User>` as a *type* reference (e.g., to set as `baseClassTypeIdentifier` on `UserRepository extends Repository<User>`, or as a property/field type via `templateRefs`).

### Common nested shapes

`templateRefs[*]`:
```
{ "placeholder": "$user", "typeIdentifier": "user" }
```
The placeholder string in `code`/`type` is replaced with the resolved Java type name AND the import is auto-added. Without templateRefs, references to internal types are silently emitted as raw text and imports are NOT generated.

`customImports[*]`:
```
{ "path": "org.springframework.stereotype", "types": ["Service"] }
```
For Java, `path` is the package and `types` are the simple names. Used ONLY for external libraries. Never list anything in §6's auto-import table.

`decorators[*]` — annotations on Java. The `code` field is the raw annotation text, e.g. `@Entity`, `@Service`, `@Column(name = \"email\")`. Annotations on properties go in the property's `decorators[]`. Annotations on the class go in the class-level `decorators[]`.

---

## 4. Java specifics — defaults & emission rules

### packageName
- Default if omitted: **`com.metaengine.generated`**.
- The `packageName` becomes the `package x.y.z;` declaration of every emitted file.
- Path layout on disk: files are written as `<outputPath>/<packageDir>/<Name>.java`, where `<packageDir>` is the dotted package converted to slashes. There's no automatic `src/main/java` prefix — if you want Maven layout, set `outputPath: "src/main/java"` (or whatever the consuming project expects).
- A `path` on a class/interface/enum is appended to the package: `path: "domain/users"` with `packageName: "com.example"` produces `package com.example.domain.users;` and writes the file under `<outputPath>/com/example/domain/users/`.
- Use one consistent `packageName` for the whole batch unless you deliberately want subpackages — easier to have everything in one batch and let `path` on each type carve subpackages.

### File names
- Java filenames follow the class name: `User.java`, `OrderStatus.java`. Use `fileName` to override (rare).
- Enums: filename = `EnumName.java` (no `.enum` suffix in Java; that's a TypeScript convention).

### Type mapping (primitive → Java)

| `primitiveType` | Java type |
|---|---|
| `String` | `String` |
| `Number` | `Integer` (or `int` for primitive, depending on context) — if you need decimals or longs, use the explicit `type` field with `BigDecimal`, `Double`, `Long`, etc. |
| `Boolean` | `Boolean` (or `boolean`) |
| `Date` | `java.time.Instant` (auto-imported via `java.time.*`) |
| `Any` | `Object` |

For non-`Number` numerics, use the free-form `"type"` field:
- `"type": "BigDecimal"` → `import java.math.BigDecimal` (auto)
- `"type": "Long"` → built-in
- `"type": "Double"` → built-in
- `"type": "UUID"` → `import java.util.UUID` (auto, in `java.util.*`)
- `"type": "LocalDate"` / `"LocalDateTime"` / `"OffsetDateTime"` → all auto-imported via `java.time.*`

### Collections
- `arrayTypes` → `List<T>` (`java.util.List`, auto). The engine doesn't emit Java native arrays (`T[]`) — model intent as a list.
- `dictionaryTypes` → `Map<K,V>` (`java.util.Map`, auto).
- For sets, model with `"type": "Set<$user>"` + templateRefs (auto-imports `java.util.Set`).
- For streams, `"type": "Stream<$user>"` + templateRefs (auto-imports `java.util.stream.Stream`).

### Auto-imported namespaces (DO NOT add to customImports)
For Java, the engine automatically imports from:
- `java.util.*` — List, Map, Set, Optional, Collection, UUID, etc.
- `java.time.*` — Instant, LocalDate, LocalDateTime, OffsetDateTime, Duration, ZoneId, etc.
- `java.util.stream.*` — Stream, Collectors, IntStream, etc.
- `java.math.*` — BigDecimal, BigInteger, MathContext, RoundingMode.
- `jakarta.validation.*` — @NotNull, @Size, @Email, @Valid, etc. (Jakarta, not javax.)
- `jackson.*` — Jackson annotations like @JsonProperty, @JsonIgnore, @JsonCreator.

If you need anything outside those (Spring, JPA, Lombok, etc.), declare it via `customImports`:
```
"customImports": [
  {"path": "org.springframework.stereotype", "types": ["Service"]},
  {"path": "jakarta.persistence", "types": ["Entity","Id","Column"]},
  {"path": "lombok", "types": ["Data","Builder"]}
]
```

### Classes vs records
The engine emits **classes** for everything in the `classes` array. There is **no first-class record emission** in the schema (no `isRecord` flag, no `records` array). If you need Java 14+ records, the cleanest path is to model them as classes with `constructorParameters` (which auto-become final fields + getters in idiomatic Java), or place a record declaration in `customFiles` as raw code. For DDD specs the safer default is `class` with constructor params — it works on every Java version the consumer might have.

### Constructor parameters
- Java is in the same camp as C#/Go/Groovy: **`constructorParameters` automatically become class properties.** Do NOT duplicate them in `properties[]` — that triggers a "Sequence contains more than one matching element" error.
- Put non-constructor fields (e.g., `createdAt` defaulted to `Instant.now()`) in `properties[]`.
- For value objects with all-final fields, putting everything in `constructorParameters` is the right call.

### customCode for method bodies
- One `customCode` entry = one method/member. The engine inserts blank lines between entries.
- Bodies are raw Java text — write whatever you want inside the braces.
- For DDD method stubs (where the spec says "method exists but body is TBD"), use:
  ```
  {"code": "public Order place() { throw new UnsupportedOperationException(\"TODO\"); }"}
  ```
- Reference internal types via `$placeholder` + `templateRefs` — do NOT hard-code the simple class name in the code, otherwise the import isn't generated:
  ```
  {
    "code": "public Optional<$order> findById(String id) { throw new UnsupportedOperationException(); }",
    "templateRefs": [{"placeholder":"$order","typeIdentifier":"order"}]
  }
  ```
- `Optional<T>`, `List<T>`, `Map<K,V>` etc. are auto-imported because they're in `java.util.*`. No template ref needed for them — only for *internal* (in-batch) types.

### Interface method signatures
For an interface that a class will `implements`, put method signatures in `customCode`, terminated with a `;`:
```
"customCode": [
  {"code": "Optional<$order> findById(String id);",
   "templateRefs": [{"placeholder":"$order","typeIdentifier":"order"}]}
]
```
Don't model methods as function-typed properties — the implementor will end up with duplicate field-style declarations.

### Decorators / annotations
- Class-level: `decorators: [{"code":"@Service"}]`.
- Field-level: inside the property: `decorators: [{"code":"@Column(name=\"email\")"},{"code":"@NotNull"}]`.
- Annotations from `jakarta.validation.*` and `jackson.*` are auto-imported by simple-name use; for everything else (Spring, JPA, Lombok), declare the annotation type in `customImports`.

---

## 5. The seven critical rules (verbatim from the guide)

1. **Generate ALL related types in ONE call.** `typeIdentifier` references only resolve within the current batch. Splitting per-domain breaks the typegraph and silently drops cross-references.
2. **`properties` = type declarations. `customCode` = everything else.** One `customCode` item = exactly one member. Never put methods in properties; never put uninitialized type declarations in customCode.
3. **Use `templateRefs` for internal types in customCode.** `$placeholder` + a templateRef triggers automatic import resolution. Without it, raw class names appear in the code but no `import` statement is emitted.
4. **Never add framework imports to `customImports`.** The auto-imported list (§4 above) is exhaustive for Java's standard library + jakarta validation + jackson. Adding `java.util.List` manually causes duplicates.
5. **`templateRefs` are ONLY for internal types.** External library types must use `customImports`.
6. **Constructor parameters auto-create properties** (Java/C#/Go/Groovy). Don't duplicate in `properties[]`.
7. **Virtual types don't generate files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reference-only. They must be referenced from a file-generating type's properties or `templateRefs` to produce any output.

---

## 6. Common Java mistakes to avoid

1. Referencing a `typeIdentifier` that doesn't exist in the batch → property is silently dropped. Verify every `typeIdentifier` matches a defined type in the same call.
2. Writing internal type names as raw strings in customCode (e.g., `"public Order placeOrder() {...}"` without templateRefs) → no import, build break across packages.
3. Adding `java.util.*`, `java.time.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` to `customImports` → duplicates.
4. Duplicating constructor parameter names in the `properties` array → "Sequence contains more than one matching element" error.
5. Using reserved Java words (`class`, `import`, `package`, `enum`, `interface`, `default`, `new`, `final`, `static`, `void`) as property names → use safe alternatives.
6. Modeling decimals as `Number` → emits `Integer`. For money/quantities use `"type": "BigDecimal"`.
7. Modeling dates as `String` because you remember TS uses strings → for Java prefer `"primitiveType": "Date"` (→ `Instant`) or `"type": "LocalDate"` / `"LocalDateTime"` / `"OffsetDateTime"`.
8. Splitting one DDD bounded context across multiple `generate_code` calls → cross-package imports break. Bundle into one call; carve packages with `path` per type.
9. Forgetting `;` at the end of an interface method signature in `customCode` → emits a malformed class-style method.
10. Putting decorators with quoted attributes in JSON without escaping the inner quotes → JSON parse failure. Escape: `"@Column(name = \"email\")"`.

---

## 7. Pattern templates ready to copy

### A — Plain DTO/value object
```
{
  "name": "Money",
  "typeIdentifier": "money",
  "path": "domain/shared",
  "constructorParameters": [
    {"name":"amount","type":"BigDecimal"},
    {"name":"currency","primitiveType":"String"}
  ]
}
```

### B — Entity with optional fields and validation
```
{
  "name": "User",
  "typeIdentifier": "user",
  "path": "domain/users",
  "decorators": [{"code":"@Entity"}],
  "constructorParameters": [
    {"name":"id","primitiveType":"String"},
    {"name":"email","primitiveType":"String"}
  ],
  "properties": [
    {
      "name":"createdAt","primitiveType":"Date",
      "decorators":[{"code":"@NotNull"}]
    },
    {
      "name":"nickname","primitiveType":"String","isOptional":true
    }
  ],
  "customCode": [
    {"code":"public boolean isActive() { return true; }"}
  ]
}
```

### C — Aggregate root with method stubs
```
{
  "name": "Order",
  "typeIdentifier": "order",
  "path": "domain/orders",
  "constructorParameters": [
    {"name":"id","primitiveType":"String"},
    {"name":"customerId","primitiveType":"String"}
  ],
  "properties": [
    {"name":"lines","typeIdentifier":"order-line-list"},
    {"name":"status","typeIdentifier":"order-status"}
  ],
  "customCode": [
    {"code":"public void place() { throw new UnsupportedOperationException(\"TODO\"); }"},
    {"code":"public void cancel(String reason) { throw new UnsupportedOperationException(\"TODO\"); }"},
    {
      "code":"public Optional<$line> lineFor(String sku) { return lines.stream().filter(l -> l.getSku().equals(sku)).findFirst(); }",
      "templateRefs":[{"placeholder":"$line","typeIdentifier":"order-line"}]
    }
  ]
}
```
Plus virtual:
```
"arrayTypes": [
  {"typeIdentifier":"order-line-list","elementTypeIdentifier":"order-line"}
]
```

### D — Repository interface implemented by a class
```
"interfaces": [{
  "name": "OrderRepository",
  "typeIdentifier": "order-repo",
  "path": "domain/orders",
  "customCode": [
    {"code":"Optional<$order> findById(String id);",
     "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]},
    {"code":"List<$order> findAll();",
     "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]},
    {"code":"void save($order order);",
     "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]}
  ]
}],
"classes": [{
  "name": "InMemoryOrderRepository",
  "typeIdentifier": "in-mem-order-repo",
  "path": "infra/persistence",
  "interfaceTypeIdentifiers": ["order-repo"],
  "decorators": [{"code":"@Service"}],
  "customImports": [
    {"path":"org.springframework.stereotype","types":["Service"]}
  ],
  "customCode": [
    {"code":"private final Map<String,$order> store = new HashMap<>();",
     "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]},
    {"code":"public Optional<$order> findById(String id) { return Optional.ofNullable(store.get(id)); }",
     "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]},
    {"code":"public List<$order> findAll() { return new ArrayList<>(store.values()); }",
     "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]},
    {"code":"public void save($order order) { store.put(order.getId(), order); }",
     "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]}
  ]
}]
```

### E — Enum used by an entity
```
"enums": [{
  "name":"OrderStatus","typeIdentifier":"order-status","path":"domain/orders",
  "members":[
    {"name":"Pending","value":0},
    {"name":"Placed","value":1},
    {"name":"Shipped","value":2},
    {"name":"Cancelled","value":3}
  ]
}]
```
Emitted as `PENDING, PLACED, SHIPPED, CANCELLED` in Java (engine applies `ALL_CAPS` idiom).

---

## 8. The end-to-end checklist for a Java DDD spec batch

1. Set `language: "java"` and pick a `packageName` (the spec usually implies one — e.g., `com.example.bookstore`). Without it, default is `com.metaengine.generated`.
2. Plan ALL types in one mental pass: aggregates, entities, value objects, enums, repositories, services. Every `typeIdentifier` you reference must be defined in the same call.
3. Decide the package layout via `path` per type (e.g., `domain/orders`, `domain/users`, `domain/shared`, `application/services`, `infra/persistence`).
4. Translate primitives — IDs as `String` (or `UUID` via `type`), money as `BigDecimal`, timestamps as `Date` (`Instant`) or explicit `LocalDate`/`LocalDateTime`.
5. Constructor parameters for required, immutable fields. `properties` for additional/optional/initialized fields. Never duplicate.
6. Methods → `customCode` with stub bodies (`throw new UnsupportedOperationException("TODO");` or trivially-correct logic). Reference internal types only via `$placeholder` + `templateRefs`.
7. Collections → declare a virtual `arrayType` (or `dictionaryType`) up front; reference by `typeIdentifier` from properties.
8. Annotations → class-level in `decorators`, field-level in property `decorators`. External annotation types (Spring, JPA, Lombok) need `customImports`.
9. Decide on `dryRun: true` for first invocation if you want to inspect output without touching disk; default writes to `outputPath` (default `.`).
10. **One call.** Never split a coherent type-graph across two `generate_code` calls.

---

## 9. Output structure

Files are written under `<outputPath>/<packageDir>/[<path>/]<Name>.java` with:
- A `package <packageName>[.<path-converted>];` header.
- All necessary `import` statements (deduplicated, sorted by the engine).
- The class/interface/enum body with annotations, fields, constructors, and methods in idiomatic Java order.
- Constructor params auto-emit final fields + a constructor that assigns them; the engine also emits idiomatic getters for those fields (matching standard Java POJO conventions).

The response from `generate_code` contains the list of generated files. With `dryRun: true`, the response includes the file contents as well — useful for inspection or for re-piping the output without writing to disk.

---

## 10. Key invariants to never violate

- **One call** per logical type-graph (the DDD spec is one type-graph).
- **`templateRefs` for every internal type reference** appearing in `customCode`/`type` strings/decorators.
- **No framework imports** in `customImports` (only external libs like Spring/JPA/Lombok).
- **No duplicate constructor params in `properties`.**
- **No methods in `properties`; no plain field declarations in `customCode`** (initialized fields ARE allowed in `customCode` — that's the dividing line: initialized => customCode, plain typed => properties).
- **One `customCode` item = one member.** Don't pack two methods into one entry.
- **Decimals use explicit `BigDecimal`/`Double`**, not `Number` (which becomes `Integer`).

If anything in the spec hits a case the schema doesn't model directly (e.g., need a `package-info.java`, a static factory class, a marker file), reach for `customFiles` with raw `customCode` blocks — that's the universal escape hatch.
