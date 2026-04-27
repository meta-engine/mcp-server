# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is the only documentation the next session will see. It distills the metaengine MCP guide and language-specific notes for **Java** code generation from a DDD spec.

---

## 1. Tools exposed by the metaengine MCP

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns the AI-generation guide. Call once at session start with `language: "java"`. |
| `mcp__metaengine__generate_code` | The *one* code-generation tool. Accepts a single JSON spec describing types, returns generated files (or contents in `dryRun`). |
| `mcp__metaengine__load_spec_from_file` | Loads an external spec file. |
| `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` | Spec-format converters (not used in this Java-from-DDD task). |

Two MCP resources are also available:
- `metaengine://guide/ai-assistant` — the canonical guide returned by `metaengine_initialize`.
- `metaengine://guide/examples` — runnable examples (TypeScript-flavoured, but apply identically across languages).

---

## 2. `generate_code` — the one tool you will use

### 2.1 Top-level shape

```jsonc
{
  "language": "java",                       // REQUIRED — must be lowercase "java"
  "packageName": "com.example.domain",      // Java/Kotlin/Groovy default = "com.metaengine.generated"
  "outputPath": ".",                        // Defaults to "."
  "dryRun": false,                          // true = preview, no files written
  "skipExisting": true,                     // true = preserves existing files (stub pattern)
  "initialize": false,                      // true = emit default-value initializers in properties

  "interfaces":               [ ... ],      // Generates 1 file per item
  "classes":                  [ ... ],      // Generates 1 file per item
  "enums":                    [ ... ],      // Generates 1 file per item
  "customFiles":              [ ... ],      // Generates 1 file per item (free-form)

  "arrayTypes":               [ ... ],      // VIRTUAL — no files, only type references
  "dictionaryTypes":          [ ... ],      // VIRTUAL — no files, only type references
  "concreteGenericClasses":   [ ... ],      // VIRTUAL — concrete instantiations like Repository<User>
  "concreteGenericInterfaces":[ ... ]       // VIRTUAL — concrete instantiations like IRepo<User>
}
```

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` **never produce files** — they are reusable type identifiers referenced from `properties[]`/`customCode[]` of the file-generating arrays.

### 2.2 Class definition (full schema)

```jsonc
{
  "name": "User",                     // Java class name (PascalCase)
  "typeIdentifier": "user",           // Unique key inside this batch — used for cross-references
  "fileName": "User",                 // Optional override (no extension); default derived from name
  "path": "domain/user",              // Directory under outputPath (joined to package path)
  "comment": "Aggregate root...",     // Class-level Javadoc

  "isAbstract": true,                 // emits `public abstract class`
  "baseClassTypeIdentifier": "base-entity",            // extends X
  "interfaceTypeIdentifiers": ["i-aggregate-root"],     // implements A, B, C

  "genericArguments": [               // Makes this a generic class template
    { "name": "T",
      "constraintTypeIdentifier": "base-entity",       // T extends BaseEntity
      "propertyName": "items",        // emits `T items;` (or `T[] items;` if isArrayProperty)
      "isArrayProperty": true }
  ],

  "constructorParameters": [          // ⚠ AUTO-CREATE properties — do NOT duplicate in properties[]
    { "name": "email", "primitiveType": "String" },
    { "name": "status", "typeIdentifier": "status-enum" },
    { "name": "tags",  "typeIdentifier": "string-array" },
    { "name": "raw",   "type": "java.util.Map<String, Object>" }
  ],

  "properties": [                     // Type DECLARATIONS only — no logic, no initialization
    { "name": "createdAt",
      "primitiveType": "Date",
      "isOptional": false,
      "isInitializer": false,         // true = emit default value
      "comment": "Creation timestamp",
      "decorators": [ { "code": "@NotNull" } ] }
  ],

  "decorators": [                     // Annotations on the class itself
    { "code": "@Entity" },
    { "code": "@Table(name = \"users\")" }
  ],

  "customCode": [                     // ONE entry per member (method, initializer-field, ctor-extra)
    { "code": "private final $repo repository;",
      "templateRefs": [ { "placeholder": "$repo", "typeIdentifier": "user-repo" } ] },
    { "code": "public $list<$user> findActive() { throw new UnsupportedOperationException(); }",
      "templateRefs": [
        { "placeholder": "$list", "typeIdentifier": "list-of-users" },
        { "placeholder": "$user", "typeIdentifier": "user" } ] }
  ],

  "customImports": [                  // External libraries ONLY — never java.util/java.time/etc.
    { "path": "org.springframework.stereotype", "types": ["Service"] }
  ]
}
```

### 2.3 Interface definition

Same shape as class but: no `constructorParameters`, no `isAbstract`, no `baseClassTypeIdentifier`.
- `interfaceTypeIdentifiers` → `extends A, B`
- Method signatures go in **`customCode`**, not `properties`. Use trailing `;` to make them abstract.

### 2.4 Enum definition

```jsonc
{
  "name": "OrderStatus", "typeIdentifier": "order-status",
  "comment": "Lifecycle states",
  "members": [
    { "name": "PENDING", "value": 0 },
    { "name": "SHIPPED", "value": 2 }
  ]
}
```
For Java, member `value` becomes the ordinal/explicit assignment. Use UPPER_SNAKE_CASE for member names.

### 2.5 customFiles — free-form file emission

```jsonc
{
  "name": "package-info",       // file name (without .java)
  "path": "domain",
  "identifier": "pkg-info",     // optional — lets other files import via this id
  "customCode": [ { "code": "// arbitrary Java text" } ],
  "customImports": [ ... ]
}
```
Use customFiles for: `package-info.java`, marker constants, hand-written aliases — anything that isn't a class/interface/enum.

### 2.6 Virtual type definitions

```jsonc
"arrayTypes": [
  { "typeIdentifier": "user-list", "elementTypeIdentifier": "user" },
  { "typeIdentifier": "string-array", "elementPrimitiveType": "String" }
],
"dictionaryTypes": [
  { "typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number" },
  { "typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user" },
  { "typeIdentifier": "user-meta",   "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata" }
],
"concreteGenericClasses": [
  { "identifier": "user-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [ { "typeIdentifier": "user" } ] }
],
"concreteGenericInterfaces": [
  { "identifier": "i-user-repo-concrete",
    "genericClassIdentifier": "i-repo-generic",
    "genericArguments": [ { "typeIdentifier": "user" } ] }
]
```

Reference these by their `typeIdentifier` / `identifier` from `properties[]` (e.g. `{"name":"users","typeIdentifier":"user-list"}`) or via `templateRefs` inside `customCode`.

---

## 3. Java-specific behaviour

### 3.1 packageName & file path layout

- `packageName` is the Java package; default `com.metaengine.generated`. Always set it explicitly to the target package (e.g. `com.example.bookstore`).
- All generated files emit a matching `package <packageName>;` line at the top.
- `outputPath` is the root the engine writes into. The engine writes to `<outputPath>/<path>/<fileName>.java` (the `path` field on each class/interface is *additive* under outputPath).
- The engine does **not** automatically prepend `src/main/java/...` to outputPath — if you need that conventional Maven/Gradle layout, set `outputPath` to `<repo>/src/main/java` (or include it in the path the caller passes). The `path` per class is for sub-folders inside that root (for example `path: "domain/user"`).
- Within a single batch, all files share the same `packageName` value, but they sit in physically different directories driven by `path`. The engine still emits a single `package` declaration value (the one you passed). If your DDD spec maps each domain to its own Java sub-package, you must batch per package OR rely on the `path` only for organisation while keeping `packageName` flat. **For DDD generation, prefer one flat package and use `path` for sub-folder grouping**, OR generate each sub-package as a separate batch (but only if there are zero cross-batch typeIdentifier references, which is rarely true for DDD).

### 3.2 Auto-imports — never put these in `customImports`

The engine auto-imports for Java:

- `java.util.*` (List, Map, Set, ArrayList, HashMap, HashSet, Optional, UUID, Date, Collection, Iterator, …)
- `java.time.*` (LocalDate, LocalDateTime, Instant, Duration, ZonedDateTime, …)
- `java.util.stream.*` (Stream, Collectors, …)
- `java.math.*` (BigDecimal, BigInteger)
- `jakarta.validation.*` (`@NotNull`, `@Size`, `@Email`, etc. — Jakarta Validation, not `javax.validation`)
- Jackson annotations (`com.fasterxml.jackson.annotation.*` — `@JsonProperty`, `@JsonIgnore`, etc.)

Adding any of the above to `customImports` causes duplicate-import errors. Only put truly external libraries in `customImports` (Spring, JPA, custom packages, etc.).

### 3.3 Primitive type mapping

`primitiveType` is one of `"String" | "Number" | "Boolean" | "Date" | "Any"`. The guide explicitly documents only TypeScript and C# mappings; Java behaviour follows these conventions:

| primitiveType | Java emission |
|---|---|
| `String`  | `String` |
| `Number`  | `int` (matches the C# precedent — *not* `double`). For non-integer, use `"type": "double"`, `"type": "long"`, `"type": "java.math.BigDecimal"`, etc., instead of `primitiveType`. |
| `Boolean` | `boolean` (or `Boolean` when wrapped via `isOptional` / inside generics) |
| `Date`    | `java.time.LocalDateTime` (`java.time.*` is the auto-imported family — use the `type` escape hatch with `"java.time.Instant"` or `"java.time.LocalDate"` if you need a different temporal type) |
| `Any`     | `Object` |

**When the DDD spec mentions money / decimals / precision-sensitive numbers, use `"type": "java.math.BigDecimal"`** (auto-imported as `BigDecimal`). When the spec mentions identifiers or surrogate keys, `"type": "java.util.UUID"` → `UUID` is auto-imported.

### 3.4 Collections

- `arrayTypes` in Java emits `List<T>` (mutable). The TS guide notes "C# emits `IEnumerable<T>` — use `"type":"List<$x>"` for `List<T>`", but for Java the emission is already the conventional `java.util.List<T>` (and `ArrayList<T>` for initialised properties). If you specifically need `Set<T>`, use `"type": "java.util.Set<$x>"` with templateRefs.
- `dictionaryTypes` emit `java.util.Map<K, V>`. All four key/value combinations (prim-prim, prim-custom, custom-prim, custom-custom) are supported.
- For `List<List<X>>` or other nested collections, use the `type` field with templateRefs:
  ```jsonc
  { "name": "matrix",
    "type": "List<List<$user>>",
    "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
  ```

### 3.5 Classes vs records

The engine emits **standard `public class`** declarations. There is no `isRecord` switch documented. If the DDD spec maps value objects to Java records, you have two options:
1. **Recommended (engine-friendly)**: emit them as classes (the engine's default), with constructor parameters that auto-create the fields. This compiles everywhere and matches the engine's mental model.
2. **Custom-file workaround**: use `customFiles` and hand-author the `record Foo(...)` declaration. This loses cross-reference imports unless you list everything in `customImports`.

Default to option 1 unless the spec explicitly requires records.

### 3.6 Constructor parameters auto-create fields (Java)

Java is in the "constructor parameters auto-create properties" group along with C#, Go, Groovy. **Do NOT duplicate ctor params in `properties[]`** — that triggers `Sequence contains more than one matching element`. Only put *additional* fields (not in the constructor) in `properties[]`.

Constructor parameters become `private final` fields with a generated constructor, conventional Java DI-friendly. For mutable beans (JPA entities), do not use constructor parameters — declare fields via `properties[]` and add a no-arg constructor in `customCode` (if needed).

### 3.7 Method stubs in `customCode` (DDD use case)

DDD specs often say "this aggregate has method `transferFunds(amount, target)`". The engine cannot synthesise behaviour, so emit method stubs that compile and signal to the human that body is required:

```jsonc
"customCode": [
  { "code": "public void transferFunds($money amount, $account target) { throw new UnsupportedOperationException(\"transferFunds not implemented\"); }",
    "templateRefs": [
      { "placeholder": "$money",   "typeIdentifier": "money-vo" },
      { "placeholder": "$account", "typeIdentifier": "account-aggregate" } ] }
]
```

Rules for `customCode` in Java:
1. **One `customCode` entry = one Java member** (one method, one initialiser, one block). The engine inserts blank lines between entries.
2. Method signatures **must include the body** for non-abstract classes. Use `throw new UnsupportedOperationException("...");` for unimplemented stubs.
3. Interface methods omit the body and end with `;` (still one entry per signature).
4. Every reference to an internal type **must** use `$placeholder` + `templateRefs` to trigger import resolution. Raw class names like `User` work only if they are in the same package; cross-package references silently break.
5. Pre-existing fields (with logic / initialisation, e.g. `private final List<User> users = new ArrayList<>();`) belong in `customCode`, not in `properties[]`.
6. Do **not** include the `private`/`public` of constructor params again — those are emitted from `constructorParameters`.
7. Java 8 lambdas and generics inside `customCode` are passed through verbatim.

### 3.8 Interface method signatures

DDD repository / domain-service interfaces should expose method signatures via `customCode`:

```jsonc
{
  "name": "UserRepository",
  "typeIdentifier": "user-repo",
  "path": "domain/user",
  "customCode": [
    { "code": "$user findById($uuid id);",
      "templateRefs": [
        { "placeholder": "$user", "typeIdentifier": "user" },
        { "placeholder": "$uuid", "typeIdentifier": "uuid-type" } ] },
    { "code": "java.util.List<$user> findActive();",
      "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
  ]
}
```

Do **NOT** put method signatures as function-typed properties — Java does not have function types and the engine will produce nonsense.

### 3.9 Decorators / annotations

Annotations go in two places:
- **Class-level** (`@Entity`, `@Service`, `@Table(...)`, etc.): `decorators` array on the class.
- **Field-level** (`@NotNull`, `@Email`, `@Column(name="...")`): `decorators` array on the property.

Each decorator entry is `{ "code": "@Annotation(args)", "templateRefs": [...] }`. For Jakarta Validation and Jackson the engine auto-imports — don't list them in `customImports`. For Spring/JPA/Lombok/etc. you must list the import yourself in `customImports`.

### 3.10 isOptional / nullability

`isOptional: true` on a Java property does *not* generate `Optional<T>` automatically (the guide describes that for C# only, where it produces `T?`). For Java, model optionality explicitly:
- For nullable references, leave the field as `Type` and rely on `@Nullable` annotations or naming conventions.
- For `Optional<T>` wrapping, use `"type": "java.util.Optional<$user>"` with templateRefs (Optional is auto-imported as `Optional`).

### 3.11 Reserved keywords

Java reserved words (`class`, `interface`, `enum`, `package`, `import`, `static`, `final`, `default`, `switch`, `new`, `this`, `super`, `extends`, `implements`, `throws`, `synchronized`, `volatile`, `transient`, `native`, `assert`, `record`) must not appear as property/parameter names. Use safe alternatives (`clazz`, `iface`, `defaultValue`, …).

---

## 4. Critical rules (rule-of-thumb checklist)

1. **ONE call with the full spec.** `typeIdentifier` references resolve only within the current batch. If `OrderService` references `Order`, both must be in the same `generate_code` invocation. Splitting per-domain breaks the typegraph.
2. **Properties = pure type declarations.** No logic, no initialisation (unless `isInitializer: true` for default values). Methods, computed fields, initialised collections → `customCode`.
3. **`customCode` = one member per entry.** Engine inserts blank lines automatically. Don't pack two methods into one entry.
4. **Internal type references inside `customCode`/property `type` strings MUST use `$placeholder` + `templateRefs`.** Otherwise imports for cross-package references will not be generated.
5. **`templateRefs` are for *internal* types only.** External libraries → `customImports`. Never mix.
6. **Don't list framework imports in `customImports`** for Java (`java.util.*`, `java.time.*`, `java.math.*`, `java.util.stream.*`, `jakarta.validation.*`, Jackson). They are auto-imported.
7. **Constructor parameters auto-create fields in Java.** Never duplicate them in `properties[]`.
8. **Virtual types don't generate files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` produce zero files; they exist only to be referenced.
9. **Every `typeIdentifier` you reference must be defined in the same call.** Otherwise the property is silently dropped (no error). Audit before submitting.
10. **`Number` maps to `int`** (matching the C# precedent). For decimals, `long`, `double`, etc., use the `type` field with the explicit Java type.
11. **`Date` defaults to `java.time.LocalDateTime`.** For `Instant`, `LocalDate`, `ZonedDateTime`, etc., use `type` with the FQN.
12. **Use `customCode` (not function-typed properties) for interface methods.** End with `;` for interfaces; include `{ ... }` body for classes.
13. **Don't use Java reserved words as identifiers.**
14. **Use `path` for sub-folder organisation.** All files share one `packageName`. For multi-package DDD specs, prefer flat package + path-based folders unless cross-spec references are zero.
15. **Use `dryRun: true`** when you want to inspect the output without writing files.

---

## 5. Output structure — what the engine produces

Per `generate_code` call:
- For each `classes[]` / `interfaces[]` / `enums[]` / `customFiles[]` entry → one `.java` file written under `<outputPath>/<path>/<fileName or derivedName>.java`.
- File begins with `package <packageName>;`, then imports (auto-resolved + `customImports`), then the type declaration.
- Cross-references between batched types resolve to fully-qualified imports automatically.
- `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` → no files.
- `dryRun: true` → file contents returned in the response, nothing written.
- `skipExisting: true` (default) → existing files are kept; useful for "stub once, hand-edit later" workflows. Set `skipExisting: false` to overwrite on regeneration.

The engine response includes the list of files written (or, for dryRun, their contents).

---

## 6. Common failure modes

1. **`Sequence contains more than one matching element`** → ctor-param duplicated in `properties[]`. Remove from `properties[]`.
2. **Missing import for an internal type** → `customCode` references the type as a raw string instead of via `templateRefs`. Add `$placeholder` + `templateRefs`.
3. **Property silently dropped** → `typeIdentifier` references a non-existent identifier in this batch. Spell-check against your `typeIdentifier` definitions.
4. **Compile error: duplicate import** → framework type listed in `customImports`. Remove it; engine auto-imports `java.*`/`jakarta.validation.*`/Jackson.
5. **`Number` produced `int` when `double` was wanted** → use `"type": "double"` instead of `"primitiveType": "Number"`.
6. **Reserved-word property** → rename (`class` → `clazz`, `default` → `defaultValue`).
7. **Methods materialised as fields** → method placed in `properties[]`. Move to `customCode`.
8. **Interface with property bodies** → method signatures placed as function-type properties. Move to `customCode` with trailing `;`.
9. **Cross-batch references broken** → split into multiple calls. Re-batch as a single call.
10. **Package mismatch errors** → mixed `packageName`s across files in the same logical module. Batch with one `packageName`; use `path` for sub-folders.

---

## 7. DDD → MetaEngine mapping cheat sheet (for the next session)

| DDD concept | MetaEngine emission |
|---|---|
| Aggregate root | `class` with `typeIdentifier`, `properties` for fields, `customCode` for behaviour stubs (`UnsupportedOperationException`). Often `interfaceTypeIdentifiers: ["i-aggregate-root"]`. |
| Entity (non-root) | Plain `class`, often `baseClassTypeIdentifier: "base-entity"`. |
| Value object | `class` with all fields in `constructorParameters` (immutable). Override equals/hashCode via `customCode` if required. (Records are an alternative — see §3.5.) |
| Domain event | `class` with `constructorParameters` for the payload + `customCode` for the timestamp init. |
| Repository | `interface` with `customCode` method signatures, conventionally suffixed `Repository`, located under `path: "domain/<aggregate>"`. |
| Domain service | `interface` (port) + `class` (default impl, with `UnsupportedOperationException` bodies). |
| Enum / lifecycle state | `enums[]` entry with UPPER_SNAKE_CASE members. |
| `List<Aggregate>` collection field | Define an `arrayTypes` entry once, reference it from properties. |
| `Map<Id, Entity>` index | Define a `dictionaryTypes` entry, reference from properties. |
| Generic repository `Repository<T extends Entity>` | `genericArguments` on the class; concrete bindings go in `concreteGenericClasses`. |
| Money / decimals | `"type": "java.math.BigDecimal"` (BigDecimal is auto-imported). |
| Identifiers (UUID) | `"type": "java.util.UUID"` (UUID is auto-imported). |
| Timestamps | `primitiveType: "Date"` (→ `LocalDateTime`) or `"type": "java.time.Instant"`. |

---

## 8. Minimal Java example (for sanity)

```jsonc
{
  "language": "java",
  "packageName": "com.example.bookstore",
  "outputPath": "./generated",
  "enums": [
    { "name": "OrderStatus", "typeIdentifier": "order-status",
      "members": [
        { "name": "PENDING",   "value": 0 },
        { "name": "CONFIRMED", "value": 1 },
        { "name": "SHIPPED",   "value": 2 }
      ]}
  ],
  "classes": [
    { "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [{ "name": "id", "type": "java.util.UUID" }] },

    { "name": "Order", "typeIdentifier": "order",
      "baseClassTypeIdentifier": "base-entity",
      "path": "domain/order",
      "decorators": [{ "code": "@jakarta.persistence.Entity" }],
      "constructorParameters": [
        { "name": "customerEmail", "primitiveType": "String" },
        { "name": "status",        "typeIdentifier": "order-status" },
        { "name": "total",         "type": "java.math.BigDecimal" }
      ],
      "properties": [
        { "name": "createdAt", "primitiveType": "Date",
          "decorators": [{ "code": "@jakarta.validation.constraints.NotNull" }] }
      ],
      "customCode": [
        { "code": "public void confirm() { throw new UnsupportedOperationException(\"confirm not implemented\"); }" },
        { "code": "public void ship($status to) { throw new UnsupportedOperationException(); }",
          "templateRefs": [{ "placeholder": "$status", "typeIdentifier": "order-status" }] }
      ]
    }
  ],
  "interfaces": [
    { "name": "OrderRepository", "typeIdentifier": "order-repo",
      "path": "domain/order",
      "customCode": [
        { "code": "$order findById(java.util.UUID id);",
          "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] },
        { "code": "java.util.List<$order> findByStatus($status status);",
          "templateRefs": [
            { "placeholder": "$order",  "typeIdentifier": "order" },
            { "placeholder": "$status", "typeIdentifier": "order-status" } ] }
      ]
    }
  ]
}
```

This single call produces:
```
generated/OrderStatus.java
generated/BaseEntity.java
generated/domain/order/Order.java
generated/domain/order/OrderRepository.java
```
All sharing `package com.example.bookstore;`, with auto-imports for `UUID`, `BigDecimal`, `LocalDateTime`, `List`, `@NotNull`, `@Entity`, and cross-imports for `BaseEntity`, `OrderStatus`, `Order`.

---

## 9. TL;DR for the next session

- One `generate_code` call. `language: "java"`. `packageName` set explicitly.
- Use `typeIdentifier` everywhere; reference internal types via `$placeholder` + `templateRefs`.
- `properties[]` = type declarations. `customCode[]` = methods (one per entry, with body or `;`).
- Constructor params auto-create fields — never duplicate.
- Don't import `java.util.*`, `java.time.*`, `java.math.*`, `java.util.stream.*`, `jakarta.validation.*`, Jackson.
- For decimals → `"type": "java.math.BigDecimal"`. For UUIDs → `"type": "java.util.UUID"`. For non-default temporals → `"type": "java.time.Instant"` etc.
- `Number` → `int`. `Date` → `LocalDateTime`. `Boolean` → `boolean`. `String` → `String`. `Any` → `Object`.
- DDD method bodies → `throw new UnsupportedOperationException(...)`.
- Use `path` for sub-folders; everything shares one package.
- Audit every `typeIdentifier` reference before submitting — undefined refs are silently dropped.
