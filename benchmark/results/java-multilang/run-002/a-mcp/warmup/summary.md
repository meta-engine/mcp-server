# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is the only context the next session will have. It must be self-contained: the next run will *not* be able to re-read the linkedResources. Sections are ordered for use during a generation: tools → schema → rules → Java mapping → output layout → patterns → mistakes.

---

## 1. Tools exposed by the metaengine MCP server

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__metaengine_initialize` | Returns the AI-assistant guide. Optional `language` arg ("java" etc.) tailors the guide. Pure helper — no generation. |
| `mcp__metaengine__generate_code` | The single workhorse. Generates compilable source files from a structured JSON spec. |
| `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, `load_spec_from_file` | Spec converters / loaders (NOT used in this run — the DDD spec is fed directly into `generate_code`). |

There is **one** generation entry point: `generate_code`. Every spec is one JSON payload.

---

## 2. `generate_code` — full input schema

Required field: `language`. Everything else is optional but the spec must contain at least one of `classes`, `interfaces`, `enums`, `customFiles`, `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`.

### Top-level fields

| Field | Type | Notes |
|-------|------|-------|
| `language` | enum (required) | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `packageName` | string | Java default: `com.metaengine.generated`. Sets the `package` declaration AND drives folder layout (see Java section). |
| `outputPath` | string | Target directory. Defaults to `.`. |
| `dryRun` | bool | Default `false`. When `true`, returns generated source in the response instead of writing files. Use to preview. |
| `skipExisting` | bool | Default `true`. New-only writes — pre-existing files are NOT overwritten. Critical for the "stub" pattern: regenerate spec safely without clobbering hand-edits. |
| `initialize` | bool | Default `false`. When `true`, properties get default-value initialization in the generated source (language-dependent). |
| `classes` | array | Class definitions (see below). |
| `interfaces` | array | Interface definitions. |
| `enums` | array | Enum definitions. |
| `arrayTypes` | array | Virtual array references — NO files generated. |
| `dictionaryTypes` | array | Virtual map references — NO files generated. |
| `concreteGenericClasses` | array | Virtual `Repository<User>`-style references — NO files. |
| `concreteGenericInterfaces` | array | Same idea, for interfaces. |
| `customFiles` | array | Hand-written source files (utility / aliases / barrels). |

### `classes[]` schema

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Class name. |
| `typeIdentifier` | string | Stable ID used by other types to reference this class. Convention: kebab-case (`user-repository`). |
| `path` | string | Subdirectory under `packageName` root, e.g. `models`, `services/auth`. |
| `fileName` | string | Override file name (without extension). |
| `comment` | string | Class-level Javadoc. |
| `isAbstract` | bool | Emit `abstract class …`. |
| `baseClassTypeIdentifier` | string | `extends` target — must reference another class or `concreteGenericClasses` identifier in the same call. |
| `interfaceTypeIdentifiers` | string[] | `implements` targets — interfaces or `concreteGenericInterfaces` identifiers. |
| `genericArguments` | array | Marks this as a generic class template (e.g. `Repository<T>`). Each entry: `{name, constraintTypeIdentifier?, propertyName?, isArrayProperty?}`. `propertyName`+`isArrayProperty` auto-creates a backing field of type `T` or `T[]`. |
| `constructorParameters` | array | Each: `{name, primitiveType?, type?, typeIdentifier?}`. **In Java, these auto-become fields — do NOT duplicate them in `properties`.** |
| `properties` | array | Field declarations only — see "properties" sub-schema below. |
| `customCode` | array | One entry = exactly one member (method, initialized field, static block). MetaEngine inserts blank lines between entries automatically. |
| `customImports` | array | External library imports only — `[{path, types[]}]`. NEVER include the auto-imported java.* / jakarta.validation.* / jackson.* packages. |
| `decorators` | array | Annotations. Each: `{code, templateRefs?}`. In Java these emit annotations like `@Service`, `@Entity`. |

### `properties[]` sub-schema

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Field name (camelCase). Avoid Java reserved words (`class`, `package`, `import`, `default`, `case`, …). |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any`. Mutually exclusive with `type` / `typeIdentifier`. |
| `type` | string | Free-form type expression. Use this for custom Java types (`List<$user>`, `Optional<$user>`, `BigDecimal`, `long`, `int`). |
| `typeIdentifier` | string | Reference another type by stable ID. Triggers automatic import resolution. |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — substitutes `$placeholder` tokens inside `type`/`code`/decorator strings AND triggers import generation. |
| `isOptional` | bool | Emits a nullable form (Java: `Optional<T>` or just nullable; see Java section). |
| `isInitializer` | bool | Add a default initializer (e.g. `= new ArrayList<>()`). |
| `comment` | string | Field-level Javadoc. |
| `commentTemplateRefs` | array | Template substitutions inside the comment. |
| `decorators` | array | Field-level annotations (`@NotNull`, `@JsonProperty(...)`, `@Column(...)`). |

### `customCode[]` sub-schema

`{code: string, templateRefs?: [{placeholder, typeIdentifier}]}`. The `code` string is a verbatim Java member declaration — method, initialized field, static block. Each placeholder beginning with `$` is replaced by the resolved type's simple name and an `import` is emitted. ONE customCode item per member.

### `enums[]` schema

`{name, typeIdentifier, fileName?, path?, comment?, members:[{name, value}]}`. Java emits `public enum Name { … }` with integer values mapped to constants (each constant gets its `value`).

### `interfaces[]` schema

Mirrors classes but with `interface` semantics: `name`, `typeIdentifier`, `path`, `fileName`, `comment`, `genericArguments`, `interfaceTypeIdentifiers` (extends), `properties`, `customCode`, `customImports`, `decorators`. In Java, properties on interfaces become `getX()` / `setX()` abstract methods; method signatures must be put in `customCode` (no body, ending in `;`).

### `arrayTypes[]` schema

`{typeIdentifier, elementPrimitiveType?, elementTypeIdentifier?}`. Virtual — no file. Reference via `typeIdentifier` in any property. Java emits `List<T>`.

### `dictionaryTypes[]` schema

`{typeIdentifier, keyPrimitiveType?, keyType?, keyTypeIdentifier?, valuePrimitiveType?, valueTypeIdentifier?}`. Virtual — no file. Java emits `Map<K, V>`.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]`

`{identifier, genericClassIdentifier, genericArguments:[{primitiveType?, typeIdentifier?}]}`. Creates a virtual `Repository<User>` reference for use as a `baseClassTypeIdentifier`, in `customCode` template refs, etc. NO file generated.

### `customFiles[]` schema

`{name, fileName?, path?, identifier?, customCode:[{code, templateRefs?}], customImports?}`. Emits a raw file with the given lines (each `customCode` entry separated by blank lines). Use for non-class artifacts (e.g. `package-info.java`, configuration constants). The `identifier` lets other entries import it via `customImports: [{path: "<identifier>"}]`.

---

## 3. Critical rules (failures most often violate one of these)

1. **One call, full graph.** `typeIdentifier` resolution is per-batch. If `OrderService` references `Order`, both must live in the same `generate_code` call. Splitting per-domain breaks all cross-references and silently drops imports. The DDD spec must be flattened into ONE call regardless of how many bounded contexts it covers.
2. **`properties` = type declarations only.** No initializers, no methods, no logic. Anything with a body or a value goes in `customCode`.
3. **One `customCode` entry = one member.** Don't pack several methods into one block — you lose the auto-spacing AND you can't attach distinct templateRefs.
4. **Use `templateRefs` for every internal type referenced inside `code`/`type` strings.** Raw type names like `User` work for the simple-name only — they will NOT generate `import com.metaengine.generated.user.User;`. Always use `$user` + `templateRefs: [{placeholder:"$user", typeIdentifier:"user"}]`.
5. **NEVER list auto-imported packages in `customImports`.** For Java: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, and `com.fasterxml.jackson.*` are auto-imported when their types appear. Adding them manually causes duplicate-import errors.
6. **`templateRefs` are ONLY for in-batch types.** External libraries go through `customImports` (e.g. Spring, Lombok, JUnit). If it's in this call → templateRefs/typeIdentifier. If it's a JAR dep → customImports.
7. **Constructor parameters auto-create fields in Java.** Do NOT also list them in `properties` — generation throws "Sequence contains more than one matching element". Put only the *additional* (non-constructor) fields in `properties`.
8. **Virtual types never produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` exist only as references. They show up in field types (`List<User>`, `Map<String, Order>`, `Repository<User>`) but never as standalone Java files.
9. **Reserved-word collisions.** Don't use Java keywords as property/parameter names: `class`, `package`, `import`, `default`, `case`, `enum`, `interface`, `new`, `null`, `void`, `final`, `static`, `volatile`, `transient`, `synchronized`, `instanceof`, `throws`, `record`, `sealed`, `permits`, `yield`. Pick alternatives (`clazz`, `pkg`, …).
10. **Verify every `typeIdentifier` is defined in the same call.** Dangling references silently drop the property without erroring — the resulting class compiles but is missing the field.

---

## 4. Java-specific generation behavior

### packageName & on-disk layout

- Default `packageName` for Java is `com.metaengine.generated`.
- The `package` statement at the top of every file = `packageName` + (path-as-dot-segments if `path` is set).
  - Example: `packageName: "com.acme.shop"`, class `path: "model/order"`, file `Order.java` → top of file is `package com.acme.shop.model.order;` and the file is written to `com/acme/shop/model/order/Order.java` under `outputPath`.
- The `path` field is segregated by `/` in the spec, but mapped to dot-segments for `package` and folder slashes on disk.
- Omit `path` to put the file directly under the root package directory.
- Use a single shared `packageName` per call; mix sub-namespaces via the per-class `path`.

### Auto-imported (do NOT add to customImports)

- `java.util.*` — `List`, `ArrayList`, `Map`, `HashMap`, `Set`, `HashSet`, `UUID`, `Optional`, `Collection`, `Iterator`, etc.
- `java.time.*` — `Instant`, `LocalDate`, `LocalDateTime`, `LocalTime`, `OffsetDateTime`, `ZonedDateTime`, `Duration`, `Period`, `ZoneId`.
- `java.util.stream.*` — `Stream`, `Collectors`.
- `java.math.*` — `BigDecimal`, `BigInteger`.
- `jakarta.validation.*` — `@NotNull`, `@NotBlank`, `@Email`, `@Size`, `@Min`, `@Max`, `@Valid`, `@Pattern`.
- `com.fasterxml.jackson.*` — `@JsonProperty`, `@JsonIgnore`, `@JsonInclude`, `@JsonFormat`, `ObjectMapper`, etc.

Use `customImports` for: Spring (`org.springframework.*`), Lombok (`lombok.*`), JUnit (`org.junit.jupiter.api.*`), AssertJ, Mockito, Hibernate (`org.hibernate.*`), JPA (`jakarta.persistence.*` IS NOT in the auto-import list — add it explicitly), MapStruct, your own projects' types, etc.

> Note: `jakarta.validation.*` is auto-imported but `jakarta.persistence.*` (Entity, Column, Id, GeneratedValue) is NOT — list it under `customImports` when generating JPA entities.

### Primitive-type mapping

The 5 `primitiveType` enum values map to Java types as follows. (Note: Java mapping mirrors C# in spirit — `Number` defaults to integer.)

| primitiveType | Emitted Java type |
|---------------|-------------------|
| `String`  | `String` |
| `Number`  | `int` (NOT `double`). For floating point, use `"type": "double"`. For money/precision, use `"type": "BigDecimal"`. For 64-bit, use `"type": "long"`. |
| `Boolean` | `boolean` (primitive) — or `Boolean` if `isOptional: true`. |
| `Date`    | `Instant` (auto-imported from `java.time`). For local-only date use `"type": "LocalDate"`; for date+time use `"type": "LocalDateTime"`. |
| `Any`     | `Object`. |

When you need a specific numeric type, **bypass `primitiveType`** and use the free-form `"type"` field:

```json
{"name": "price", "type": "BigDecimal"}
{"name": "weightKg", "type": "double"}
{"name": "viewCount", "type": "long"}
{"name": "ratingPercent", "type": "float"}
```

### Optional / nullable fields

`isOptional: true` on a property emits the field wrapped or nullable. In Java this typically becomes `Optional<T>` or a nullable reference type with `@Nullable` depending on how the engine resolves it. Concretely, **prefer using the explicit `type` field** (`"type": "Optional<$user>"` with templateRefs) when you want to be sure the wrapper is `Optional<>` — it reads cleanly and removes ambiguity.

For "absent vs present" semantics on collections, prefer empty collection over `Optional<List<>>`.

### Class vs record emission

- The current MetaEngine Java emitter generates **classes**, not Java 14+ `record` types. Expect to see standard POJOs with `private` fields plus generated `getX()` / `setX()` accessors and a constructor.
- Constructors come from `constructorParameters`. Listing all immutable fields there gives you a `final`-friendly object even though it's not a record.
- If the spec calls for "record-like" immutability, declare fields via `constructorParameters` only (no extra `properties`) and avoid setters by using `customCode` to expose only getters.
- There is no first-class flag like `isRecord: true` — to coerce a record, you would need `customFiles` with hand-written `public record Foo(…) {}`. Default behavior = class.

### Interface methods

Java interfaces lose their property-as-method auto-generation when the implementing class needs concrete bodies. Best practice for a `Service` / `Repository` interface:

- Put each abstract method signature in `customCode` ending with `;` (no body).
- Use `templateRefs` for every in-batch type appearing in the signature.
- The implementing class then puts the concrete bodies in its own `customCode`.

```json
{
  "interfaces": [{
    "name": "OrderRepository",
    "typeIdentifier": "order-repo",
    "path": "domain/order",
    "customCode": [
      {"code": "$order findById(UUID id);",
       "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]},
      {"code": "List<$order> findAll();",
       "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]}
    ]
  }]
}
```

### customCode for method stubs (DDD pattern)

Domain methods often need a concrete-but-pending body. The conventional stub is:

```json
{
  "code": "public Money totalPrice() { throw new UnsupportedOperationException(\"Not implemented yet\"); }"
}
```

Use this when you want the spec to capture *intent* (the method exists on the type) without committing logic. Because `skipExisting: true` is the default, regenerating after a developer fills in the real body will not overwrite their work — the stub is a safe placeholder. (To regenerate a single file deliberately, delete it on disk first or pass `skipExisting: false`.)

For getters on private fields, you almost never need to write one — properties auto-emit getters. Custom logic getters go in `customCode`:

```json
{
  "code": "public String getDisplayName() { return firstName + \" \" + lastName; }"
}
```

### Annotations / decorators

Annotations go via `decorators[]` on a class, property, or interface. The string under `code` is emitted verbatim *above* the member.

```json
"decorators": [
  {"code": "@Service"},
  {"code": "@Transactional(readOnly = true)"}
]
```

For internal-type-aware annotations, use `templateRefs`:

```json
{
  "code": "@Repository(repositoryInterface = $repo.class)",
  "templateRefs": [{"placeholder": "$repo", "typeIdentifier": "order-repo"}]
}
```

Spring (`@Service`, `@Component`, `@RestController`, `@Autowired`, …) and JPA (`@Entity`, `@Table`, `@Id`, `@Column`, …) require explicit `customImports`:

```json
"customImports": [
  {"path": "org.springframework.stereotype", "types": ["Service"]},
  {"path": "org.springframework.transaction.annotation", "types": ["Transactional"]}
]
```

### Constructor patterns

```jsonc
// All-args constructor (preferred — auto-creates fields):
"constructorParameters": [
  {"name": "id", "primitiveType": "String"},
  {"name": "amount", "type": "BigDecimal"},
  {"name": "status", "typeIdentifier": "order-status"}
]
// DO NOT also put id/amount/status in `properties`.
```

If you need both a primary constructor *and* extra computed/transient fields, put the extras in `properties[]`:

```jsonc
"constructorParameters": [...primary fields...],
"properties": [
  {"name": "createdAt", "primitiveType": "Date", "isInitializer": true}
]
```

### Generic classes (Java type erasure caveats)

- `genericArguments[].name` — type variable name (`T`, `K`, `V`).
- `constraintTypeIdentifier` → emitted as `T extends BaseEntity` in the class signature.
- `propertyName` + `isArrayProperty: true` → auto-creates `protected List<T> items;` (or whatever name). Don't redeclare it in `properties[]`.

To use the generic class with a concrete type as a base class, declare a `concreteGenericClasses` entry:

```json
"concreteGenericClasses": [{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}],
"classes": [{
  "name": "UserRepository", "typeIdentifier": "user-repo",
  "baseClassTypeIdentifier": "user-repo-concrete"
}]
```

This emits `public class UserRepository extends Repository<User> { … }` with both imports.

### Enums

- Java enum members get integer `value` from the spec. Generation typically emits `MEMBER(value)` constants with a private final int field + getter — exact shape may vary, but assume each enum value is reachable via the spec name.
- File name: `OrderStatus.java`. Place under a `path` like `domain/order` to colocate with the aggregate.
- Reference enums from properties using `typeIdentifier` — no `customImports` needed.

---

## 5. Output structure (what files come back)

Per `generate_code` call:

- `classes[]` → one `<Name>.java` per class.
- `interfaces[]` → one `<Name>.java` per interface.
- `enums[]` → one `<Name>.java` per enum.
- `customFiles[]` → one file per entry, name from `name`/`fileName`.
- `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` → no files.

Each file contains:

1. `package <packageName>[.<path-segments>];`
2. Auto-imports (only for types actually used in this file).
3. `customImports` (filtered/deduped with the auto-imports).
4. Class/interface/enum declaration with annotations.
5. Fields (from `properties` and from `constructorParameters`).
6. Constructor (if `constructorParameters` provided).
7. `customCode` blocks, one blank line between each.
8. Auto-generated getters/setters for `properties[]` fields.

When `dryRun: true`, the response body contains the file contents instead of writing to disk. When `skipExisting: true` (default), already-existing files are left untouched.

---

## 6. Patterns relevant to a DDD Java spec

### 6.1 Aggregate root with value objects

```json
{
  "language": "java",
  "packageName": "com.acme.ordering",
  "classes": [
    {
      "name": "Money", "typeIdentifier": "money", "path": "shared",
      "constructorParameters": [
        {"name": "amount", "type": "BigDecimal"},
        {"name": "currency", "primitiveType": "String"}
      ]
    },
    {
      "name": "Order", "typeIdentifier": "order", "path": "domain/order",
      "constructorParameters": [
        {"name": "id", "type": "UUID"},
        {"name": "customerId", "type": "UUID"},
        {"name": "total", "typeIdentifier": "money"},
        {"name": "status", "typeIdentifier": "order-status"}
      ],
      "customCode": [
        {"code": "public void confirm() { throw new UnsupportedOperationException(\"Not implemented yet\"); }"},
        {"code": "public boolean isPaid() { return status == $status.PAID; }",
         "templateRefs":[{"placeholder":"$status","typeIdentifier":"order-status"}]}
      ]
    }
  ],
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status", "path": "domain/order",
    "members": [
      {"name": "PENDING", "value": 0},
      {"name": "PAID", "value": 1},
      {"name": "SHIPPED", "value": 2},
      {"name": "CANCELLED", "value": 3}
    ]
  }]
}
```

### 6.2 Repository interface + JPA entity

```json
{
  "language": "java",
  "packageName": "com.acme.ordering",
  "interfaces": [{
    "name": "OrderRepository", "typeIdentifier": "order-repo",
    "path": "domain/order",
    "customCode": [
      {"code": "$order findById(UUID id);",
       "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]},
      {"code": "List<$order> findByCustomerId(UUID customerId);",
       "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]},
      {"code": "void save($order order);",
       "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]}
    ]
  }],
  "classes": [{
    "name": "Order", "typeIdentifier": "order", "path": "domain/order",
    "decorators": [{"code": "@Entity"}, {"code": "@Table(name = \"orders\")"}],
    "customImports": [
      {"path": "jakarta.persistence", "types": ["Entity", "Table", "Id", "Column", "Enumerated", "EnumType"]}
    ],
    "constructorParameters": [
      {"name": "id", "type": "UUID"},
      {"name": "customerId", "type": "UUID"}
    ],
    "properties": [
      {"name": "status", "typeIdentifier": "order-status",
       "decorators": [{"code": "@Enumerated(EnumType.STRING)"}]}
    ]
  }]
}
```

### 6.3 Application service with constructor injection

```json
{
  "name": "OrderService",
  "typeIdentifier": "order-service",
  "path": "application",
  "decorators": [{"code": "@Service"}],
  "customImports": [
    {"path": "org.springframework.stereotype", "types": ["Service"]}
  ],
  "constructorParameters": [
    {"name": "orderRepository", "typeIdentifier": "order-repo"}
  ],
  "customCode": [
    {"code": "public $order placeOrder(UUID customerId) { throw new UnsupportedOperationException(\"Not implemented yet\"); }",
     "templateRefs":[{"placeholder":"$order","typeIdentifier":"order"}]}
  ]
}
```

### 6.4 Collection-typed properties

```json
"properties": [
  {"name": "lineItems", "typeIdentifier": "line-item-list"},
  {"name": "tags", "type": "List<String>"},
  {"name": "metadata", "typeIdentifier": "metadata-map"}
]
```

with

```json
"arrayTypes": [
  {"typeIdentifier": "line-item-list", "elementTypeIdentifier": "line-item"}
],
"dictionaryTypes": [
  {"typeIdentifier": "metadata-map", "keyPrimitiveType": "String", "valuePrimitiveType": "String"}
]
```

### 6.5 Stub method for not-yet-implemented logic

```json
{
  "code": "public $invoice generateInvoice() { throw new UnsupportedOperationException(\"Pending invoice domain rules\"); }",
  "templateRefs": [{"placeholder": "$invoice", "typeIdentifier": "invoice"}]
}
```

`skipExisting: true` ensures the next regeneration won't overwrite the developer's eventual implementation.

---

## 7. Common Java-relevant mistakes

1. Letting `Number` slip through when you needed `BigDecimal` / `long` / `double`. Always use the explicit `type` field for non-int numerics.
2. Using `Date` (the legacy `java.util.Date`) in your head — the engine maps `primitiveType: "Date"` to `Instant`. Use `"type": "LocalDate"` etc. when you need a different temporal type.
3. Listing `java.util.*` or `java.time.*` in `customImports` — duplicate import errors.
4. Listing `jakarta.persistence.*` annotations as decorators without adding the matching `customImports` (only `jakarta.validation.*` is auto-imported).
5. Duplicating constructor parameters in `properties[]` → `Sequence contains more than one matching element`.
6. Writing raw type names (`User`, `Order`) inside `customCode` without `templateRefs` → cross-package imports never get generated → the file fails to compile.
7. Multiple methods crammed into one `customCode` entry → can't attach distinct templateRefs, no auto-spacing.
8. Splitting a DDD spec across two `generate_code` calls (e.g. once per bounded context). Cross-context references silently lose imports. **One call.**
9. Using a Java reserved word (`class`, `package`, `default`, `enum`, `record`, `sealed`, `permits`) as a property name.
10. Assuming `interfaces` properties auto-become method signatures usable from an implementing class. Use `customCode` for the abstract method signatures so the implementing class can supply concrete bodies of the same shape.
11. Forgetting that `arrayTypes` / `dictionaryTypes` / `concreteGenericClasses` produce NO files. If you defined one but never referenced its `typeIdentifier` in a real type, it's dead weight.
12. Pre-creating the output directory and being surprised when generation is no-op: that's `skipExisting: true` behaving correctly. Pass `skipExisting: false` only when you want to regenerate over a clean tree.

---

## 8. One-shot generation checklist (for the next session)

Before calling `generate_code`:

1. Confirm `language: "java"` is in the payload.
2. Pick a single `packageName` for the whole spec (e.g. `com.acme.ordering`). All sub-namespaces go via per-class `path`.
3. Walk the DDD spec and, for each domain entity / value object / aggregate / repository / service / event / DTO, decide: class? interface? enum? customFile?
4. Assign every type a unique kebab-case `typeIdentifier`.
5. Map fields to either `primitiveType`, `type` (for `BigDecimal`, `long`, `double`, `LocalDate`, `Optional<…>`, `List<…>`), or `typeIdentifier`.
6. For every cross-type reference inside `customCode`, add a matching `templateRefs` entry. Every. Single. One.
7. Put primary fields ONLY in `constructorParameters`; supplementary fields in `properties[]`.
8. Stub un-implemented methods with `throw new UnsupportedOperationException("Not implemented yet");`.
9. Add `customImports` only for non-auto-imported libraries (Spring, Lombok, JUnit, Hibernate, JPA persistence annotations, MapStruct, etc.).
10. Verify EVERY `typeIdentifier` referenced (in `baseClassTypeIdentifier`, `interfaceTypeIdentifiers`, properties, customCode templateRefs, decorator templateRefs, arrayTypes/dictionaryTypes elements, concreteGenerics genericArguments) is defined somewhere in the same call.
11. Submit ONE `generate_code` call with the full graph.
12. Inspect output, fix spec, regenerate (rely on `skipExisting: true` + delete-or-pass-false to refresh specific files).

---

## 9. Key reminders

- The next session has only this brief. Treat every claim above as load-bearing.
- The metaengine MCP only ships TWO documentation resources (`metaengine://guide/ai-assistant`, `metaengine://guide/examples`); both are summarized here.
- The DDD spec must become **one** `generate_code` JSON. Splitting it loses cross-references silently.
- When in doubt about a type mapping, prefer the explicit `type` field over `primitiveType` — it is more deterministic.
- Java emission today is plain classes with getters/setters, NOT records. Use `customFiles` if a record is mandatory.
