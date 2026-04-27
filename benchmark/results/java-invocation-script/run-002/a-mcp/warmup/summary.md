# MetaEngine MCP — Knowledge Brief (Java focus)

This is a self-contained brief written for a downstream session that will call `mcp__metaengine__generate_code` to emit **Java** sources from a DDD spec. The next session has no access to the linkedResources docs — everything it needs is here.

---

## What MetaEngine MCP is

MetaEngine is a **semantic** code generator (not a template engine). You send a single JSON spec describing types, relationships, and method bodies. It resolves cross-references, computes imports, applies language idioms, and writes compilable source files. One well-formed call replaces dozens of file writes.

Languages supported: `typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php, rust`.

---

## Tools exposed by the MCP server

- `mcp__metaengine__metaengine_initialize` — returns the AI guide. Optional `language` parameter for language-specific tips. Already called in warmup; do not call again unless guidance is needed.
- `mcp__metaengine__generate_code` — the main generation entry point.
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` — spec-format conversions; **not relevant** for a DDD-from-JSON job.
- `mcp__metaengine__load_spec_from_file` — for loading existing specs from disk; not needed unless a spec file already exists.

For DDD generation, you only need `generate_code`.

---

## `generate_code` — full input schema

Top-level fields (only `language` is strictly required):

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `"java"` for this job |
| `packageName` | string | Defaults to `com.metaengine.generated` for Java. Sets the `package` declaration. |
| `outputPath` | string | Where files are written. Defaults to `"."`. |
| `dryRun` | bool | If true, returns content without writing files. |
| `skipExisting` | bool | Default `true`. Skips files that already exist (stub pattern). |
| `initialize` | bool | If true, properties get default-value initializers. |
| `classes[]` | array | Class definitions (also generic class templates). |
| `interfaces[]` | array | Interface definitions (also generic interface templates). |
| `enums[]` | array | Enum definitions. |
| `arrayTypes[]` | array | Virtual array refs (no files). |
| `dictionaryTypes[]` | array | Virtual map refs (no files). |
| `concreteGenericClasses[]` | array | Virtual `Repository<User>`-style refs (no files). |
| `concreteGenericInterfaces[]` | array | Same, for interfaces. |
| `customFiles[]` | array | Files generated **without** a class/interface wrapper (constants, package-info, etc.). |

### `classes[]` item schema

| Field | Type | Notes |
|---|---|---|
| `name` | string | The Java type name (`User`, `OrderService`). |
| `typeIdentifier` | string | **Stable kebab-case ID** other entries refer to (`user`, `order-service`). Pick once and reuse. |
| `comment` | string | Class-level Javadoc. |
| `fileName` | string | Override file name without extension. Default: derived from `name`. |
| `path` | string | Subdirectory under `outputPath`/package root (e.g., `domain/order`). |
| `isAbstract` | bool | |
| `baseClassTypeIdentifier` | string | Reference to another class in this batch. |
| `interfaceTypeIdentifiers` | string[] | Interfaces (in this batch) the class `implements`. |
| `genericArguments[]` | array | Marks the class as a generic template. Each arg: `name` (`T`), `constraintTypeIdentifier` (extends bound), `propertyName` (auto-creates a field of type T), `isArrayProperty` (field becomes `T[]`/`List<T>`). |
| `constructorParameters[]` | array | Each item `{name, primitiveType?, type?, typeIdentifier?}`. **In Java these auto-become fields** — do NOT also list them in `properties`. |
| `properties[]` | array | Field declarations only — see schema below. |
| `customCode[]` | array | One method or initialized field per item. See `customCode` schema below. |
| `customImports[]` | array | External (non-stdlib) imports only. Each `{path, types[]}`. |
| `decorators[]` | array | Class-level annotations. Each `{code, templateRefs?}`. In Java this is annotations like `@Service`, `@Entity`. |

### `interfaces[]` item schema

Same shape as classes, minus `isAbstract`/`baseClassTypeIdentifier`/`constructorParameters`. Use `interfaceTypeIdentifiers` to extend other interfaces. Method signatures go in `customCode` (one per method), **not** as function-typed properties.

### `enums[]` item schema

| Field | Type | Notes |
|---|---|---|
| `name` | string | Enum type name. |
| `typeIdentifier` | string | Stable ID. |
| `members[]` | `[{name, value}]` | `value` is numeric. Java engine emits ALL_CAPS member names (idiomatic transformation). |
| `path`, `fileName`, `comment` | | as for classes |

### `properties[]` item schema (used in classes and interfaces)

| Field | Notes |
|---|---|
| `name` | Field name. |
| `primitiveType` | One of `"String"`, `"Number"`, `"Boolean"`, `"Date"`, `"Any"`. |
| `typeIdentifier` | Reference to a type defined in the same batch (class / interface / enum / arrayType / dictionaryType / concreteGenericClass / concreteGenericInterface). |
| `type` | Free-form type expression for non-primitive non-batch types (e.g., `"BigDecimal"`, `"Optional<$user>"`). When this contains placeholders, supply `templateRefs`. |
| `templateRefs[]` | `[{placeholder: "$x", typeIdentifier: "x"}]` — substitutes batch types into a `type` string and triggers import resolution. |
| `isOptional` | Optional/nullable. |
| `isInitializer` | If true, generate a default initializer for the field. |
| `comment` | Field-level Javadoc. |
| `commentTemplateRefs[]` | Same templating, applied to comment. |
| `decorators[]` | Field annotations (`@NotNull`, `@Column(...)`, etc.). |

**Rule**: properties declare **type only**. No initialization logic, no methods. Anything with logic goes in `customCode`.

### `customCode[]` item schema

```jsonc
{
  "code": "public Optional<$user> findById(UUID id) { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

- One member per item (one method, or one initialized field).
- `code` is emitted **verbatim** into the class body. It must be valid Java for the surrounding context (full method including modifiers/return type/body).
- Use `$placeholder` syntax for **every** in-batch type reference and list it in `templateRefs`. This triggers automatic import emission. Raw class names without `templateRefs` will not pull in imports.
- Engine inserts blank lines between consecutive `customCode` blocks.

### `arrayTypes[]` / `dictionaryTypes[]` (virtual)

```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
  {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
],
"dictionaryTypes": [
  {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-by-email", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
]
```

These do **not** generate files — they're just reusable references for `properties[].typeIdentifier`. In Java they typically materialize as `List<T>` and `Map<K, V>` from `java.util.*` (auto-imported).

If you need a specific collection (`Set<T>`, `LinkedHashMap`, `Stream<T>`), skip `arrayTypes`/`dictionaryTypes` and use `type` + `templateRefs`:

```jsonc
{"name": "tags", "type": "Set<$tag>", "templateRefs": [{"placeholder": "$tag", "typeIdentifier": "tag"}]}
```

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]`

Materialize a virtual `Repository<User>` reference for use as a `baseClassTypeIdentifier` or in `templateRefs`:

```jsonc
"concreteGenericClasses": [{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}]
```

No file generated; purely a reference shorthand.

### `customFiles[]`

For files **without** a class/interface wrapper (e.g., a constants file, a `package-info.java`, a barrel of static helpers if you'd ever do that in Java):

```jsonc
{
  "name": "Constants",
  "path": "common",
  "identifier": "common-constants",
  "customCode": [
    {"code": "public static final String DEFAULT_LOCALE = \"en-US\";"}
  ]
}
```

The `identifier` lets other entries import it via `customImports`.

---

## Java-specific notes (CRITICAL — read carefully)

### packageName behavior
- **Default**: `com.metaengine.generated`. Set it explicitly to match the spec's bounded-context package (e.g., `com.example.shop.order`).
- The single top-level `packageName` is applied to all generated Java sources unless overridden by `path`.
- `path` on individual entries adds **subpackage** segments. If `packageName="com.example.shop"` and `path="order"`, the file lands at `com/example/shop/order/Order.java` with `package com.example.shop.order;`.
- Use `path` to mirror DDD bounded contexts (`domain/order`, `domain/customer`, `application/order`, `infrastructure/persistence`). Subpackage segments are derived from the path with dots.

### File path layout
- Standard Maven/Gradle layout is **NOT** auto-prepended. The engine writes to `outputPath/<packagePath>/Name.java`. If you want `src/main/java/...`, set `outputPath="src/main/java"` (or the harness writes wherever `outputPath` resolves to in the run dir).
- File names follow Java conventions: `User.java`, `OrderService.java`, `OrderStatus.java`. Override with `fileName`.

### Auto-imported packages (do NOT add to `customImports`)
- `java.util.*` — `List`, `Map`, `Set`, `Optional`, `UUID`, `Collection`, `ArrayList`, `HashMap`, `HashSet`, `Date` (legacy)
- `java.time.*` — `Instant`, `LocalDate`, `LocalDateTime`, `OffsetDateTime`, `ZonedDateTime`, `Duration`, `Period`
- `java.util.stream.*` — `Stream`, `Collectors`
- `java.math.*` — `BigDecimal`, `BigInteger`
- `jakarta.validation.*` — `@NotNull`, `@Size`, `@Email`, etc. (Jakarta EE 9+)
- Jackson (`com.fasterxml.jackson.*`) — `@JsonProperty`, `ObjectMapper`, etc.

Putting any of these in `customImports` will cause duplicate imports or errors. Reserve `customImports` for genuine third-party libs (Spring, Lombok, project-internal packages outside this batch).

### Type mapping for `primitiveType`
Java engine maps the cross-language primitives like this:

| primitiveType | Java type | Notes |
|---|---|---|
| `"String"` | `String` | |
| `"Number"` | `int` (integer-default) | For `long`, `double`, `BigDecimal`, etc., use `type` instead of `primitiveType`. |
| `"Boolean"` | `boolean` | Use `isOptional: true` to get `Boolean` (boxed) if nullability matters. |
| `"Date"` | `java.time.Instant` (auto-imported) | If the DDD spec calls for `LocalDate` only or `OffsetDateTime`, use `type: "LocalDate"` instead — both are auto-imported. |
| `"Any"` | `Object` | |

**Money / decimal**: never use `Number`. Use `{"type": "BigDecimal"}` (auto-imported from `java.math`).

**Long IDs / counts**: use `{"type": "long"}` or `{"type": "Long"}`.

**UUIDs**: use `{"type": "UUID"}` (auto-imported from `java.util`).

**Domain IDs as value objects**: model them as their own class with a single `String`/`UUID` property; reference by `typeIdentifier`.

### Class vs Record emission
- The engine emits **regular classes** by default. There is no documented `isRecord` toggle in the schema, so do **not** rely on Java 14+ records being auto-emitted. Treat all classes as standard POJOs unless the harness has been pre-configured otherwise.
- Constructor parameters auto-promote to fields with a generated constructor. Combined with appropriate getter customCode (or Lombok via `customImports` + `decorators`), this gives a clean immutable POJO without records.
- Getters/setters/equals/hashCode/toString are **not** emitted automatically. If they're needed, either:
  - Add them as `customCode` entries (one per method), OR
  - Use Lombok: `customImports: [{path: "lombok", types: ["Getter", "Setter", "EqualsAndHashCode", "Builder"]}]` plus `decorators: [{code: "@Getter"}, {code: "@Setter"}, ...]`. The DDD spec usually doesn't ask for Lombok unless stated; default to explicit getters via customCode.

### Constructor parameters auto-create fields (Java + C# + Go + Groovy)
This is the single biggest footgun. If you put `email` in `constructorParameters` AND in `properties`, the engine throws "Sequence contains more than one matching element". Rule:

```jsonc
"constructorParameters": [
  {"name": "id",    "type": "UUID"},
  {"name": "email", "primitiveType": "String"}
],
"properties": [
  // ONLY additional fields not in the constructor:
  {"name": "createdAt", "type": "Instant"}
]
```

For DDD aggregates with all-args constructors, list every field in `constructorParameters` and leave `properties` empty.

### customCode for method stubs
DDD specs typically describe methods/behavior on entities and services. The engine doesn't infer bodies — supply them in `customCode`:

```jsonc
"customCode": [
  {
    "code": "public Optional<$order> findById(UUID id) {\n    throw new UnsupportedOperationException(\"not implemented\");\n}",
    "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
  }
]
```

Conventions:
- Each `customCode` block is exactly **one** member (one method or one initialized field). Don't pack multiple methods into one block.
- Include the full Java member declaration: visibility, return type, name, params, body braces.
- Java engine does NOT auto-indent the body relative to the class — write the body indented as you want it to appear. (Python is the language with a strict 4-space rule; Java tolerates either, but be consistent.)
- For unimplemented behavior, throw `UnsupportedOperationException("not implemented")` rather than silently returning `null` — keeps the stubs honest.
- **Every in-batch type reference uses `$placeholder` + `templateRefs`.** A raw `Order` in the body without templateRefs may compile if same-package, but breaks across packages. Always template.
- Validation annotations (`@NotNull`, `@Email`) on method params: include them inline in the `code` string; they're auto-imported.

### Idiomatic transformations the engine applies
The engine applies language-aware transforms. For Java specifically:
- **Enums**: members emitted as `ALL_CAPS` (e.g., spec `Pending` → `PENDING`).
- **Methods/fields**: `camelCase` is preserved as-is in the spec (so write spec methods in camelCase).
- The downstream judge has tolerance for these idiomatic transformations — don't fight them by encoding awkward names.

### Annotations / decorators
Use `decorators[]` on classes, properties, and methods for Java annotations:
```jsonc
"decorators": [
  {"code": "@Entity"},
  {"code": "@Table(name = \"orders\")"}
]
```
For annotations that reference in-batch types, use `templateRefs`:
```jsonc
{"code": "@OneToMany(targetEntity = $orderItem.class)", "templateRefs": [{"placeholder": "$orderItem", "typeIdentifier": "order-item"}]}
```

---

## The seven critical rules (apply to every call)

1. **One call, all related types.** `typeIdentifier` resolution is batch-scoped. Splitting a domain into multiple calls breaks cross-imports.
2. **Properties declare types; customCode does logic.** Never put methods in `properties`. Never put uninitialized field declarations in `customCode`.
3. **Use `templateRefs` for every in-batch type reference inside `customCode`, `decorators`, or complex `type` strings.** This is what triggers import emission.
4. **Don't add stdlib imports to `customImports`.** Java auto-imports listed above. `customImports` is for third-party / project-external paths only.
5. **`templateRefs` are for in-batch types only.** External library types use `customImports`. Don't mix.
6. **Don't duplicate constructor parameters in `properties`.** Java auto-promotes constructor params to fields.
7. **Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) generate no files.** They're reference shorthand only.

---

## Output structure (what the engine produces)

For a Java call with `outputPath="."`, `packageName="com.example.shop"`, and entries with `path="domain/order"` etc., you get:

```
./com/example/shop/domain/order/Order.java
./com/example/shop/domain/order/OrderItem.java
./com/example/shop/domain/order/OrderStatus.java
./com/example/shop/domain/customer/Customer.java
./com/example/shop/application/OrderService.java
```

Each file has:
- `package com.example.shop.<sub>;`
- Auto-resolved `import` block (stdlib + same-batch + customImports), de-duplicated and sorted.
- Class/interface/enum body composed from properties → constructor → customCode (in that emission order, separated by blank lines).
- Class/property/method-level Javadoc from `comment` fields.

The MCP response (when `dryRun=false`) reports the list of written files plus any per-file diagnostics. With `dryRun=true`, file contents are returned in-line in the response.

---

## Common-mistake checklist (Java edition)

1. Referencing a `typeIdentifier` not defined in the batch → property silently dropped. Verify every ID has a definition.
2. Putting method signatures as function-typed `properties` on an interface → implementer duplicates them. Use `customCode` for interface methods.
3. Raw class names in `customCode` bodies without `templateRefs` → missing imports across packages.
4. Using `arrayTypes` when you actually need `Set<T>` / `Stream<T>` / a specific collection — use `type` + `templateRefs` instead.
5. Adding `java.util.*` / `java.time.*` / `jakarta.validation.*` / Jackson to `customImports` → duplicate imports.
6. **Duplicating `constructorParameters` in `properties`** — biggest Java footgun, throws "Sequence contains more than one matching element".
7. Java reserved words as identifiers (`class`, `interface`, `enum`, `package`, `import`, `final`, `static`, `abstract`, `synchronized`). Pick safe alternatives (`clazz`, `iface`, `pkg`, `importData`).
8. Splitting one DDD context across multiple `generate_code` calls — typegraph fragments, imports break.
9. Expecting `Number` to be `long` or `double` — it's `int`. Use `type: "long"` / `"BigDecimal"` / `"double"` for everything else.
10. Forgetting to set `packageName` — files land in `com.metaengine.generated`, which is rarely what a real DDD spec wants.

---

## Recommended approach for a DDD spec → Java

1. **Read the entire spec first.** Inventory all aggregates, value objects, enums, repositories, services, events.
2. **Pick stable kebab-case `typeIdentifier`s for every type.** Reuse them everywhere.
3. **Plan the `path` layout.** Match DDD layers: `domain/<context>` for entities/value objects/enums, `application/<context>` for services, `infrastructure/<context>` for repository implementations (interfaces typically live alongside the aggregate in `domain`).
4. **Map types**:
   - IDs → `UUID` via `type: "UUID"`, OR a dedicated value-object class
   - Money → `BigDecimal`
   - Timestamps → `Instant` (preferred for events) or `LocalDate` (calendar-only)
   - Counts → `long` or `int`
   - Optional fields → `Optional<X>` via `type` + `templateRefs`, or `isOptional: true`
   - Collections → `arrayTypes` (→ `List<T>`) or explicit `Set<T>` / `Map<K,V>` via `type`
5. **One `generate_code` call.** All classes, interfaces, enums, virtual types in a single payload.
6. **Method bodies**: stub with `throw new UnsupportedOperationException("not implemented")` unless the spec gives explicit semantics.
7. **Verify `packageName` is set** to match the spec's namespace; verify `outputPath` is the run directory.
8. **Set `dryRun: false`** (the default behavior) so files are written. Set `skipExisting: false` only if you need to overwrite a previous run's output.

---

## Quick mental model

- `classes[]` / `interfaces[]` / `enums[]` / `customFiles[]` → produce **files**.
- `arrayTypes[]` / `dictionaryTypes[]` / `concreteGenericClasses[]` / `concreteGenericInterfaces[]` → produce **virtual references** (no files).
- `properties[]` → field declarations only.
- `customCode[]` → one member each (method or initialized field), full Java syntax, with `$placeholder` + `templateRefs` for every in-batch type.
- `constructorParameters[]` → auto-fields in Java; never duplicate in `properties`.
- `customImports[]` → third-party only; `java.util.*` / `java.time.*` / `java.math.*` / `jakarta.validation.*` / Jackson are auto.
- `decorators[]` → annotations (class/property/method levels).

When in doubt, batch more, not less. The cost of a too-large batch is small; the cost of split batches is broken imports.
