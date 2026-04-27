# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is the *only* MetaEngine documentation the next session will see. It is comprehensive and self-contained.

---

## 1. What MetaEngine MCP is

A **semantic code generator** exposed via MCP. You describe types/relationships/methods as structured JSON, MetaEngine emits compilable, correctly-imported source files. It resolves cross-references, manages imports, and applies language idioms automatically. **One well-formed JSON call replaces dozens of file writes**, and crucially: cross-file imports only resolve **within a single batch**.

Supported languages: `typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php, rust`.

---

## 2. Tools exposed

- `mcp__metaengine__metaengine_initialize(language?)` — returns the AI guide (already consumed for this brief).
- `mcp__metaengine__generate_code(...)` — the only generator call you make. Schema below.
- `mcp__metaengine__load_spec_from_file`, `generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` — spec adapters; not needed for direct DDD spec → Java generation.

You will **only call `generate_code`**. Do **not** use Edit/Write to author Java files; let MetaEngine produce them.

---

## 3. `generate_code` — full input schema

Top-level fields (one big JSON object):

| Field | Type | Notes |
|---|---|---|
| `language` | enum string, **required** | `"java"` for this run. |
| `packageName` | string, optional | Java default: `com.metaengine.generated`. Sets the package declaration AND the on-disk path (`src/main/java/<dotted/path>/...`). |
| `outputPath` | string, optional | Defaults to `.`. Root directory for emitted files. |
| `dryRun` | bool, default `false` | If `true`, returns file contents in the response without writing. |
| `skipExisting` | bool, default `true` | When true, won't overwrite existing files (stub pattern). |
| `initialize` | bool, default `false` | Initialize properties with default values. |
| `classes` | array<Class> | File-generating. |
| `interfaces` | array<Interface> | File-generating. |
| `enums` | array<Enum> | File-generating. |
| `customFiles` | array<CustomFile> | File-generating, no class/interface wrapper. |
| `arrayTypes` | array<ArrayType> | **Virtual** — produces NO files; reusable type ref. |
| `dictionaryTypes` | array<DictType> | **Virtual** — no files; reusable type ref. |
| `concreteGenericClasses` | array<ConcreteGen> | **Virtual** — no files; e.g. `Repository<User>`. |
| `concreteGenericInterfaces` | array<ConcreteGen> | **Virtual** — no files. |

### 3.1 Class shape

```jsonc
{
  "name": "User",                         // required
  "typeIdentifier": "user",               // unique key used for cross-refs
  "fileName": "User",                     // optional; without extension
  "path": "model",                        // optional subdir under package root
  "comment": "Doc comment",               // class-level Javadoc
  "isAbstract": false,
  "baseClassTypeIdentifier": "base-entity",
  "interfaceTypeIdentifiers": ["printable"],
  "genericArguments": [
    { "name": "T", "constraintTypeIdentifier": "base-entity",
      "propertyName": "items", "isArrayProperty": true }
  ],
  "constructorParameters": [              // becomes ctor + fields automatically
    { "name": "id",   "primitiveType": "String" },
    { "name": "addr", "typeIdentifier": "address" }
  ],
  "properties": [                         // type declarations only (no init, no logic)
    { "name": "createdAt", "primitiveType": "Date",
      "comment": "...", "isOptional": false, "isInitializer": false,
      "decorators": [ { "code": "@NotNull" } ],
      "templateRefs": [ { "placeholder": "$x", "typeIdentifier": "x" } ] }
  ],
  "customCode": [                         // ONE entry per member (method or initialized field)
    { "code": "public $addr getAddress() { return this.addr; }",
      "templateRefs": [ { "placeholder": "$addr", "typeIdentifier": "address" } ] }
  ],
  "decorators": [ { "code": "@Service" } ],
  "customImports": [
    { "path": "org.springframework.stereotype", "types": ["Service"] }
  ]
}
```

### 3.2 Property shape

`{ name, primitiveType?, type?, typeIdentifier?, isOptional?, isInitializer?, comment?, decorators?, templateRefs?, commentTemplateRefs? }`

- `primitiveType` ∈ `{"String","Number","Boolean","Date","Any"}`.
- `type` is a raw type-expression string (use it for `BigDecimal`, `List<...>`, `Optional<...>`, etc.). Combine with `templateRefs` for internal types via `$placeholder`.
- `typeIdentifier` references another generated type (must exist in the same call).

### 3.3 Enum shape

```jsonc
{ "name": "OrderStatus", "typeIdentifier": "order-status", "fileName": "OrderStatus",
  "path": "model", "comment": "...",
  "members": [ { "name": "Pending", "value": 0 }, { "name": "Shipped", "value": 2 } ] }
```

### 3.4 Interface shape

Same fields as Class minus `constructorParameters`/`isAbstract`. `interfaceTypeIdentifiers` = list of interfaces this one extends. Use `customCode` for method **signatures** that an implementing class will fulfill (don't model them as function-typed properties).

### 3.5 Virtual-type shapes

```jsonc
"arrayTypes": [
  { "typeIdentifier": "user-list",  "elementTypeIdentifier": "user" },
  { "typeIdentifier": "string-list", "elementPrimitiveType": "String" }
]
"dictionaryTypes": [
  { "typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number" },
  { "typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user" },
  { "typeIdentifier": "u-meta",      "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata" }
]
"concreteGenericClasses": [
  { "identifier": "user-repo",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [ { "typeIdentifier": "user" } ] }
]
```

Reference these via `typeIdentifier` (in properties) or `templateRefs` (in code). They never produce files.

### 3.6 customFiles shape

```jsonc
{ "name": "Constants", "fileName": "Constants", "path": "shared",
  "identifier": "shared-constants",          // optional, lets other files import via this id
  "customCode": [ { "code": "public static final int MAX = 10;" } ],
  "customImports": [ ... ] }
```

`customFiles` write a raw file with no class wrapper — useful for type aliases (TS), Go const blocks, etc. **In Java the file still needs a top-level declaration**; usually you should prefer a regular `class` (e.g., a final class with static constants) over `customFiles` unless you have a clear reason.

---

## 4. The 7 critical rules (in order of how often they bite)

1. **ONE call for related types.** `typeIdentifier` references resolve only within the current batch. Splitting per-domain breaks the typegraph and cross-file imports won't render.
2. **`properties` = declarations, `customCode` = everything else.** No methods or initializers in `properties`. No bare type declarations in `customCode`. **One `customCode` entry per member** (the engine inserts blank lines between them).
3. **Internal type refs in `customCode` must use `templateRefs`.** Raw type names in code strings won't trigger Java imports across packages — use `$placeholder` + `templateRefs: [{placeholder, typeIdentifier}]`.
4. **Never put framework imports in `customImports`.** For Java, the engine auto-imports `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, and Jackson types. `customImports` is **only** for genuine external libraries (Spring, Lombok, project-internal packages, etc.).
5. **`templateRefs` are ONLY for internal (in-batch) types.** External libs → `customImports`. Don't mix.
6. **Constructor parameters auto-create fields in Java.** Do NOT also list those names in `properties[]` or you get `Sequence contains more than one matching element`. `properties[]` should hold only fields that are *not* in `constructorParameters`.
7. **Virtual types never emit files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are pure references.

Bonus pitfalls: never reference a `typeIdentifier` you didn't define (the field is **silently dropped**); avoid Java reserved words as identifiers (`class`, `enum`, `package`, `import`, `interface`, `final`, `default`, `switch`, `synchronized`, etc.).

---

## 5. Java-specific behavior

### 5.1 packageName & file path layout

- Default Java package: `com.metaengine.generated`.
- The engine emits files under `<outputPath>/src/main/java/<package as path>/<class.path or "">/<ClassName>.java`.
  - Example: `outputPath="."`, `packageName="com.example.shop"`, class with `path="model"` and `name="Order"` → `./src/main/java/com/example/shop/model/Order.java`, with `package com.example.shop.model;` at the top.
  - The class-level `path` is appended to the package; sub-package declaration is generated accordingly.
- Set `packageName` once at the top of the `generate_code` call. Don't try to override per-class via custom imports.

### 5.2 Type mapping (primitive → Java)

| `primitiveType` | Java type |
|---|---|
| `"String"` | `String` |
| `"Number"` | `Integer` (no decimals). For decimals use `"type":"BigDecimal"` or `"type":"Double"`. |
| `"Boolean"` | `Boolean` |
| `"Date"` | `java.time.Instant` (auto-imported). For other shapes use `"type":"LocalDate"` / `"type":"LocalDateTime"` / `"type":"OffsetDateTime"` (all under `java.time.*`, auto-imported). |
| `"Any"` | `Object` |

For DDD specs that mention "DateTime" / "timestamp", default to `Instant`. If the spec says "Date" (no time), use `"type":"LocalDate"`. For monetary amounts, use `"type":"BigDecimal"`. For UUIDs, `"type":"UUID"` (auto-imported from `java.util`).

### 5.3 Collections

- Prefer the virtual `arrayTypes` for `List<T>` semantics — for Java these emit `List<T>` with auto-import.
- Prefer `dictionaryTypes` for `Map<K,V>`.
- For `Set<T>`, optional values, streams, etc., use a property-level `"type":"Set<$user>"` with `templateRefs`.
- `Optional<T>` → use `"type":"Optional<$user>"` + templateRefs (`Optional` is in `java.util`, auto-imported).

### 5.4 Class vs record

The engine emits **classes by default**. There is **no first-class `isRecord` switch**. If a true Java 14+ `record` is required for an immutable value object, model it as a `customFile` with the `record` declaration as raw code. Otherwise, model value objects as classes with `constructorParameters` (becomes ctor + fields automatically) and rely on the engine for getter/setter conventions. For most DDD value objects, **a regular class with constructor parameters is the right choice** — it gives you ctor injection and clear field declarations without the record tax (sealed hierarchies, no inheritance, etc.).

### 5.5 Constructor / DI patterns

- `constructorParameters` produces a ctor whose params are also fields. Don't repeat them in `properties[]`.
- For Spring service injection: put the dependency in `constructorParameters` (so it becomes a `private final` field + ctor param) and add a class-level `@Service` decorator + `customImports` for `org.springframework.stereotype.Service`.

### 5.6 customCode for method stubs

DDD specs typically describe a method's signature and intent but not its body. The convention is:

```jsonc
"customCode": [
  { "code": "public $order placeOrder($cart cart) { throw new UnsupportedOperationException(\"TODO: implement placeOrder\"); }",
    "templateRefs": [
      { "placeholder": "$order", "typeIdentifier": "order" },
      { "placeholder": "$cart",  "typeIdentifier": "cart"  }
    ] }
]
```

Notes:
- One `customCode` entry per method. The engine inserts blank lines between entries, so don't add leading/trailing newlines yourself.
- For `void` methods, omit the return statement: `public void cancel() { throw new UnsupportedOperationException("TODO: cancel"); }`.
- All internal type references (parameters, return types, generics, exceptions) must be `$placeholder`s with matching `templateRefs`.
- Don't `import java.lang.UnsupportedOperationException` — it's `java.lang.*`, never imported anyway.

### 5.7 Decorators / annotations

Annotations are passed via `decorators[].code`. You can:
- Put class-level annotations in the class's `decorators` (e.g. `@Service`, `@Entity`).
- Put property-level annotations in the property's `decorators` (e.g. `@NotNull`, `@Column(name="email")`).
- Annotations from `jakarta.validation.*` are auto-imported. Anything else (Spring, Lombok, JPA `jakarta.persistence.*`) needs `customImports`.

### 5.8 Interfaces

- Method signatures live in `customCode`, ending with `;` and no body:
  ```jsonc
  { "code": "$order findById(String id);",
    "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] }
  ```
- A class implementing the interface lists it in `interfaceTypeIdentifiers: [...]`.
- Interface names are not stripped/prefixed in Java (no TS-style `I` prefix transform).

### 5.9 Generics

`genericArguments` on a class/interface produces `class Foo<T>` / `class Foo<T extends BaseEntity>`. To use a concrete instantiation as a base class or field type, define it via `concreteGenericClasses` and reference its `identifier` from `baseClassTypeIdentifier` or via `templateRefs`.

### 5.10 Idiomatic transformations the engine applies

The judge tolerates Java idiomatic naming, so don't fight these:

- Enum members are emitted in `ALL_CAPS` regardless of the casing you supply.
- Method names defined in `customCode` are accepted as-written; if you use mixed conventions across languages, the engine generally normalizes Java methods to `camelCase`.
- Getters/setters are not auto-generated for `properties[]`; if you need them, add them as `customCode` (`public $t getX() { ... }`).
- Fields default to `private`; visibility modifiers in `customCode` are honored verbatim.

---

## 6. Output structure (what you'll see after a call)

For Java, expect a tree like:

```
<outputPath>/
  src/main/java/<package as path>/
    <ClassName>.java
    <subpath>/<OtherClass>.java
    ...
```

The tool returns a JSON-ish summary of files written (or, with `dryRun: true`, the file contents inline). Verify by:
- Counting files: one per class/interface/enum/customFile (no files for arrayTypes, dictionaryTypes, or concreteGenericClasses/Interfaces).
- Spot-checking imports: cross-references between in-batch types should generate matching `import com.<pkg>.<sub>.OtherType;` lines.

---

## 7. End-to-end Java pattern (DDD-style sketch)

```jsonc
{
  "language": "java",
  "packageName": "com.example.shop",
  "outputPath": ".",
  "enums": [
    { "name": "OrderStatus", "typeIdentifier": "order-status", "path": "model",
      "members": [
        { "name": "Pending", "value": 0 },
        { "name": "Paid",    "value": 1 },
        { "name": "Shipped", "value": 2 }
      ] }
  ],
  "classes": [
    { "name": "Money", "typeIdentifier": "money", "path": "model",
      "constructorParameters": [
        { "name": "amount",   "type": "BigDecimal" },
        { "name": "currency", "primitiveType": "String" }
      ] },

    { "name": "Customer", "typeIdentifier": "customer", "path": "model",
      "constructorParameters": [
        { "name": "id",    "type": "UUID" },
        { "name": "email", "primitiveType": "String" }
      ] },

    { "name": "OrderLine", "typeIdentifier": "order-line", "path": "model",
      "constructorParameters": [
        { "name": "sku",      "primitiveType": "String" },
        { "name": "quantity", "primitiveType": "Number" },
        { "name": "price",    "typeIdentifier": "money" }
      ] },

    { "name": "Order", "typeIdentifier": "order", "path": "model",
      "constructorParameters": [
        { "name": "id",       "type": "UUID" },
        { "name": "customer", "typeIdentifier": "customer" },
        { "name": "placedAt", "primitiveType": "Date" },
        { "name": "status",   "typeIdentifier": "order-status" }
      ],
      "properties": [
        { "name": "lines", "typeIdentifier": "order-line-list" }
      ],
      "customCode": [
        { "code": "public $money total() { throw new UnsupportedOperationException(\"TODO: total\"); }",
          "templateRefs": [{ "placeholder": "$money", "typeIdentifier": "money" }] },
        { "code": "public void markPaid() { throw new UnsupportedOperationException(\"TODO: markPaid\"); }" }
      ] },

    { "name": "OrderService", "typeIdentifier": "order-service", "path": "service",
      "decorators": [{ "code": "@Service" }],
      "customImports": [{ "path": "org.springframework.stereotype", "types": ["Service"] }],
      "constructorParameters": [
        { "name": "repo", "typeIdentifier": "order-repository" }
      ],
      "customCode": [
        { "code": "public $order place($customer customer, $lineList lines) { throw new UnsupportedOperationException(\"TODO: place\"); }",
          "templateRefs": [
            { "placeholder": "$order",    "typeIdentifier": "order" },
            { "placeholder": "$customer", "typeIdentifier": "customer" },
            { "placeholder": "$lineList", "typeIdentifier": "order-line-list" }
          ] }
      ] }
  ],
  "interfaces": [
    { "name": "OrderRepository", "typeIdentifier": "order-repository", "path": "repository",
      "customCode": [
        { "code": "$order findById(UUID id);",
          "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] },
        { "code": "void save($order order);",
          "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] }
      ] }
  ],
  "arrayTypes": [
    { "typeIdentifier": "order-line-list", "elementTypeIdentifier": "order-line" }
  ]
}
```

This single call emits roughly:

```
src/main/java/com/example/shop/model/OrderStatus.java
src/main/java/com/example/shop/model/Money.java
src/main/java/com/example/shop/model/Customer.java
src/main/java/com/example/shop/model/OrderLine.java
src/main/java/com/example/shop/model/Order.java
src/main/java/com/example/shop/service/OrderService.java
src/main/java/com/example/shop/repository/OrderRepository.java
```

with `import` lines wired across packages.

---

## 8. Pre-flight checklist before calling `generate_code`

- [ ] `language: "java"` set.
- [ ] `packageName` chosen (use the spec's bounded-context name where possible).
- [ ] Every `typeIdentifier` referenced (in properties, baseClassTypeIdentifier, interfaceTypeIdentifiers, templateRefs, arrayTypes, dictionaryTypes, concreteGenericClasses) is defined somewhere in the same call.
- [ ] No name appears in both `constructorParameters[]` and `properties[]` of the same class.
- [ ] Every method in `customCode` uses `$placeholder` + `templateRefs` for in-batch types.
- [ ] No `java.util.*` / `java.time.*` / `jakarta.validation.*` / `com.fasterxml.jackson.*` in `customImports`.
- [ ] No methods in `properties[]`; no bare type declarations in `customCode[]`.
- [ ] Reserved words (`class`, `enum`, `package`, etc.) avoided as identifiers.
- [ ] Single, batched call — not split per domain or per file.
- [ ] If unsure about output, set `dryRun: true` first and inspect.

---

## 9. Common failure signatures & fixes

| Symptom | Cause | Fix |
|---|---|---|
| `Sequence contains more than one matching element` | Same name in `constructorParameters` and `properties` | Remove from `properties[]`. |
| Property silently missing in output | Referenced `typeIdentifier` not defined in batch | Add the missing type, or fix the typo. |
| Compile error: cannot resolve `Foo` | Internal type used as raw string in `customCode` | Replace with `$foo` + `templateRefs`. |
| Duplicate import / unused import | Framework class added to `customImports` | Remove it; engine auto-imports stdlib. |
| Wrong number type (Integer vs BigDecimal) | Used `primitiveType:"Number"` for a decimal | Switch to `"type":"BigDecimal"` (or `Double`). |
| File written to wrong directory | `path` on class clashes with `packageName` expectations | Set `packageName` correctly; `path` is appended as sub-package. |

---

## 10. TL;DR for the gen session

1. Read the spec, list every entity / value object / aggregate / service / repository / enum.
2. Decide one `packageName` (e.g. `com.example.<context>`).
3. Build ONE `generate_code` call:
   - `enums[]` for all enumerations.
   - `classes[]` for entities, value objects (with `constructorParameters`), services, controllers.
   - `interfaces[]` for repositories / ports.
   - `arrayTypes[]` / `dictionaryTypes[]` for every collection type referenced.
4. For methods described by the spec but without bodies, emit `customCode` stubs that throw `UnsupportedOperationException`.
5. Cross-reference *only* via `typeIdentifier` and `templateRefs` (`$placeholder`).
6. Don't add stdlib imports. Do add Spring/JPA/Lombok if used.
7. Submit the single call. If unsure, `dryRun: true` first; otherwise let it write.
