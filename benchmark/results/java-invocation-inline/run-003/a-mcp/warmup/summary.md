# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is the canonical reference for the next session. It is self-contained: the next session will NOT have access to the linkedResources docs and must generate Java code from a DDD spec using only this summary.

---

## 1. What the MCP is

MetaEngine is a *semantic* code generator. You describe types, relationships, methods, and metadata as JSON; it produces compilable, correctly-imported source files for: TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust.

It is NOT a templating engine. It resolves cross-file references, manages imports, applies language-idiomatic transformations (Java enum names → `ALL_CAPS`, Python methods → `snake_case`, Java getters/setters auto-generated, etc.), and lays out files according to language conventions.

---

## 2. Tools exposed

- `mcp__metaengine__metaengine_initialize` — returns the AI guide. Used during warmup; **not needed at gen time**.
- `mcp__metaengine__generate_code` — the only tool you call to generate. ONE call with the full spec.
- `mcp__metaengine__load_spec_from_file`, `generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` — variant entry points (not needed for a DDD spec).

The MCP also exposes two resources:
- `metaengine://guide/ai-assistant` (the rules)
- `metaengine://guide/examples` (worked TypeScript examples that apply structurally to all languages)

---

## 3. `generate_code` — input schema (full)

Top-level fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **yes** | `"java"` for this run. |
| `packageName` | string | no | Default for Java/Kotlin/Groovy = `com.metaengine.generated`. **Set this explicitly.** |
| `outputPath` | string | no | Default `.`. Files written under it. |
| `dryRun` | bool | no | If true, returns content in response without writing. Useful when you want to check before writing. |
| `initialize` | bool | no | If true, properties get default initialisers. Java: typically false (let JVM defaults handle primitives, set in constructor). |
| `skipExisting` | bool | no | Default true — won't overwrite. Set false if you need to rewrite files. |
| `classes[]` | array | no | Class definitions (regular or generic). |
| `interfaces[]` | array | no | Interface definitions. |
| `enums[]` | array | no | Enum definitions. |
| `arrayTypes[]` | array | no | **Virtual** — defines reusable array references (no file emitted). |
| `dictionaryTypes[]` | array | no | **Virtual** — reusable map references (no file emitted). |
| `concreteGenericClasses[]` | array | no | **Virtual** — `Repository<User>` style. |
| `concreteGenericInterfaces[]` | array | no | **Virtual** — `IRepository<User>` style. |
| `customFiles[]` | array | no | Free-form files (utilities, helpers). |

### `classes[]` item

```
{
  "name": string,                             // PascalCase class name
  "typeIdentifier": string,                   // unique id used to reference this class elsewhere
  "path": string?,                            // subdir under packageName/outputPath (e.g. "domain/user")
  "fileName": string?,                        // override filename (without extension)
  "comment": string?,                         // class-level Javadoc
  "isAbstract": bool?,
  "baseClassTypeIdentifier": string?,         // typeIdentifier OR a concreteGeneric* identifier
  "interfaceTypeIdentifiers": string[]?,      // ids of interfaces to implement
  "genericArguments": [{                      // makes this a generic class template
    "name": "T",                              // type parameter name
    "constraintTypeIdentifier": string?,     // T extends ...
    "propertyName": string?,                  // optional auto-property of type T
    "isArrayProperty": bool?                  // T[] / List<T> instead of T
  }],
  "constructorParameters": [{                 // see warning below
    "name": string,
    "primitiveType": "String"|"Number"|"Boolean"|"Date"|"Any",
    "type": string?,                          // raw type string (e.g. "BigDecimal")
    "typeIdentifier": string?                 // reference internal type
  }],
  "properties": [{
    "name": string,
    "primitiveType": "String"|"Number"|"Boolean"|"Date"|"Any"  // OR
    "type": string?,                          // raw type string, can include $placeholders
    "typeIdentifier": string?,                // reference internal type / array type / dict type
    "isOptional": bool?,
    "isInitializer": bool?,                   // emit default initialiser
    "comment": string?,
    "decorators": [{ code, templateRefs[] }], // e.g. @NotNull, @Email
    "templateRefs": [{ placeholder, typeIdentifier }]
  }],
  "decorators": [{ code, templateRefs[] }],   // class-level annotations (@Entity, @Service, ...)
  "customCode": [{                            // ONE block = ONE member
    "code": string,                            // method body, initialised field, ctor extra, etc.
    "templateRefs": [{ placeholder: "$x", typeIdentifier: "..." }]
  }],
  "customImports": [{
    "path": string,                            // e.g. "org.springframework.stereotype"
    "types": string[]                          // e.g. ["Service"]
  }]
}
```

### `interfaces[]` item

Same shape as `classes` minus `isAbstract`, `baseClassTypeIdentifier`, `constructorParameters`. Use `interfaceTypeIdentifiers` to extend other interfaces. Method signatures go in `customCode` (one block per method), NOT as function-typed properties.

### `enums[]` item

```
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "path": string?,
  "fileName": string?,
  "comment": string?,
  "members": [
    { "name": "Pending", "value": 0 },
    { "name": "Shipped", "value": 2 }
  ]
}
```

The engine will idiomatically rewrite member names per language. **Java**: `Pending` → `PENDING`, `InProgress` → `IN_PROGRESS`. Don't fight it.

### `arrayTypes[]` / `dictionaryTypes[]` items (virtual)

```
arrayTypes: [
  { "typeIdentifier": "user-list", "elementTypeIdentifier": "user" },
  { "typeIdentifier": "tag-list",  "elementPrimitiveType": "String" }
]
dictionaryTypes: [
  { "typeIdentifier": "score-map", "keyPrimitiveType": "String", "valuePrimitiveType": "Number" },
  { "typeIdentifier": "user-by-id", "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
]
```

Reference them in properties via `typeIdentifier: "user-list"`. They emit no files; they just resolve into `List<User>` / `Map<String, Integer>` at the use site, with imports handled.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` (virtual)

```
concreteGenericClasses: [{
  "identifier": "user-repository",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{ "typeIdentifier": "user" }]
}]
```

Use this when you need to extend or reference a *closed* generic, e.g. `class UserRepository extends Repository<User>`. Set the subclass's `baseClassTypeIdentifier` to `"user-repository"`.

### `customFiles[]` (free-form)

```
{
  "name": "Constants",
  "path": "shared",
  "identifier": "shared-constants",   // referenceable from customImports
  "fileName": string?,
  "customCode": [{ code, templateRefs[] }],
  "customImports": [...]
}
```

Use for utility code that doesn't fit the class/interface/enum mould.

---

## 4. Java-specific rules — the heart of this brief

### 4.1 packageName & file path layout

- `packageName` is the **Java package**. Default `com.metaengine.generated`. Always set it explicitly to whatever the spec asks for, e.g. `"packageName": "com.example.commerce"`.
- The engine writes Java files under `outputPath` using a Maven-style layout. Files end up at `<outputPath>/src/main/java/<packageName-with-/>/<path>/<ClassName>.java` (engine handles the `src/main/java` prefix and dot-to-slash translation).
- The `path` field on a class/interface/enum is **a sub-package suffix** appended after `packageName`. So `packageName="com.acme.shop"` + `path="domain/order"` produces files in package `com.acme.shop.domain.order` and the engine writes the corresponding `package com.acme.shop.domain.order;` declaration.
- **Do not** include `src/main/java` in `outputPath` or `path` — the engine adds it.
- **Do not** put dots in `path`; use `/` (e.g. `path: "domain/order"` not `path: "domain.order"`).

### 4.2 Type mapping (CRITICAL)

| `primitiveType` | Emitted Java type |
|---|---|
| `"String"` | `String` |
| `"Number"` | `int`/`Integer` (Java picks integer by default — see note) |
| `"Boolean"` | `boolean`/`Boolean` |
| `"Date"` | `java.time.LocalDateTime` (auto-imported via `java.time.*`) |
| `"Any"` | `Object` |

**`Number` is integer in Java**, not double. If the DDD spec wants money, decimals, or floating-point, **do NOT use `primitiveType: "Number"`**. Instead use `"type": "BigDecimal"` (auto-imported via `java.math.*`) or `"type": "double"` / `"type": "long"` as needed.

Date guidance: `primitiveType: "Date"` is convenient for "some sort of timestamp." If the spec is specific, use `"type": "LocalDate"`, `"type": "LocalDateTime"`, `"type": "Instant"`, `"type": "OffsetDateTime"` etc. — all in `java.time.*` and auto-imported. **Do not** map Date to `java.util.Date` — that's legacy.

UUIDs: `"type": "UUID"` (auto-imported from `java.util`).

### 4.3 Auto-imported packages (NEVER add to `customImports`)

The engine auto-imports these for Java:
- `java.util.*` (List, Map, Set, Optional, UUID, Date, Collection, Arrays, Collections, Objects, …)
- `java.time.*` (LocalDate, LocalDateTime, Instant, ZoneId, Duration, OffsetDateTime, …)
- `java.util.stream.*` (Stream, Collectors, …)
- `java.math.*` (BigDecimal, BigInteger, RoundingMode, MathContext)
- `jakarta.validation.*` (`@NotNull`, `@Email`, `@Size`, `@Valid`, …)
- `jackson.*` (com.fasterxml.jackson annotations)

Use `customImports` ONLY for:
- Spring (`org.springframework.stereotype.Service`, `org.springframework.web.bind.annotation.*`, …)
- Lombok (`lombok.Data`, `lombok.Builder`, …)
- Domain libraries (axon, hibernate beyond JPA, etc.)
- Anything not in the above auto list.

### 4.4 Constructor parameters auto-create properties (Java)

This is rule #6 of the engine. In Java, every entry in `constructorParameters` becomes a private final field with a public getter. **Do NOT also list those names in `properties[]`** — that triggers a "Sequence contains more than one matching element" error.

Pattern:
```
{
  "name": "Order",
  "constructorParameters": [
    { "name": "id", "primitiveType": "String" },
    { "name": "total", "type": "BigDecimal" }
  ],
  "properties": [
    // only ADDITIONAL fields not in constructorParameters
    { "name": "createdAt", "primitiveType": "Date" }
  ]
}
```

If the entity should be immutable with all-args ctor → put everything in `constructorParameters`. If you want a no-arg JPA entity with setters → put fields in `properties` only. **Never both.**

### 4.5 Class vs Java records

The engine emits **regular classes** by default (with private fields, getters/setters, and a constructor for `constructorParameters`). It does **not** automatically emit Java 14+ `record` declarations.

If the DDD spec asks for a value object that should be a record, the cleanest path is a `customFile` whose `customCode` declares the record literally:
```
"customFiles": [{
  "name": "Money",
  "path": "domain/shared",
  "customCode": [
    { "code": "public record Money(BigDecimal amount, String currency) {}" }
  ]
}]
```
Set `packageName` so the file lands in the right package — `customFiles` honour `packageName` + `path` for the package declaration. Imports needed inside the record (e.g. `BigDecimal`) are auto-resolved if the engine recognises the type; for safety you can include them as `customImports` (BigDecimal IS auto-imported, so don't bother).

Default behaviour: emit a normal class. Only reach for the customFile/record trick if the spec explicitly asks for it.

### 4.6 Methods and `customCode` for Java

- One `customCode` block = one Java method or one initialised field.
- Method signature must be a complete Java method declaration: `public List<$user> findAll() { return List.of(); }`.
- For abstract method stubs, write the body as `throw new UnsupportedOperationException("not implemented");`.
- Reference internal types via `$placeholder` + `templateRefs`:
  ```
  {
    "code": "public Optional<$user> findById(String id) { return Optional.empty(); }",
    "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
  }
  ```
- Multiline method bodies use `\n`; the engine handles indent. Java does not need explicit indentation injection (unlike Python).
- Annotations on methods go inside the `code` string itself: `"@Override\npublic String toString() { return name; }"`.

### 4.7 Interface method signatures

For interfaces that classes will `implements`, put the signatures in `customCode` (each block ends with `;`):
```
"interfaces": [{
  "name": "UserRepository",
  "typeIdentifier": "user-repo",
  "customCode": [
    { "code": "Optional<$user> findById(String id);",
      "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] },
    { "code": "List<$user> findAll();",
      "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
  ]
}]
```
Do NOT put method signatures as function-typed properties — that's a TypeScript-style anti-pattern and will produce malformed Java.

### 4.8 Enums

Java enums are emitted with `ALL_CAPS` member names (engine transforms automatically). A `value` field is added if you supply numeric values — engine emits an enum with a `private final int value;` constructor + getter when values are present. If you don't need values, omit them.

```
"enums": [{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "path": "domain/order",
  "members": [
    { "name": "Pending", "value": 0 },
    { "name": "Shipped", "value": 2 }
  ]
}]
```
Generated file: `OrderStatus.java`. Members: `PENDING(0)`, `SHIPPED(2)`. The judge tolerates `ALL_CAPS` — don't try to override it.

### 4.9 Inheritance & interface implementation

- `baseClassTypeIdentifier`: id of the parent class (or a `concreteGenericClasses` entry for `extends Repository<User>`).
- `interfaceTypeIdentifiers`: ids of interfaces (or `concreteGenericInterfaces` entries for `implements Comparable<User>`).
- Engine emits `extends X implements A, B` and resolves imports.

### 4.10 Annotations / decorators

Pass annotations via `decorators` on classes/properties or inline in `customCode`. JPA / Bean Validation / Jackson are auto-imported, so you can write `@Entity`, `@NotNull`, `@JsonProperty("foo")` directly. Spring annotations need `customImports`:

```
"decorators": [{ "code": "@Service" }],
"customImports": [{ "path": "org.springframework.stereotype", "types": ["Service"] }]
```

### 4.11 Generics

Define a generic class template:
```
{
  "name": "Repository",
  "typeIdentifier": "repo-generic",
  "isAbstract": true,
  "genericArguments": [
    { "name": "T", "constraintTypeIdentifier": "base-entity",
      "propertyName": "items", "isArrayProperty": true }
  ],
  "customCode": [
    { "code": "public List<T> findAll() { return items; }" }
  ]
}
```
Java emits `public abstract class Repository<T extends BaseEntity> { protected List<T> items; ... }`.

To extend with a concrete arg, use `concreteGenericClasses`:
```
"concreteGenericClasses": [{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{ "typeIdentifier": "user" }]
}]
```
Then on the subclass: `"baseClassTypeIdentifier": "user-repo-concrete"` → emits `class UserRepository extends Repository<User>`.

### 4.12 Reserved words

Avoid Java reserved words as property/parameter names: `class`, `default`, `enum`, `int`, `long`, `package`, `private`, `static`, `final`, `interface`, `volatile`, `synchronized`, `transient`, `native`, `throws`, `import`, `new`, `this`, `super`, etc. Pick safe alternatives (`clazz`, `kind`, `count`, `payload`).

---

## 5. Cardinal rules (the ones that bite hardest)

1. **ONE call with the full spec.** `typeIdentifier` resolution is per-batch. Splitting the spec into multiple `generate_code` calls breaks cross-references and imports.
2. **Properties = type declarations only. customCode = methods and initialised fields.** Never put method signatures as properties; never put plain field declarations as customCode.
3. **Use `templateRefs` for every internal type referenced in `customCode` or `type` strings.** Without templateRefs the engine can't add the correct import. Raw class names work *only* when in the same package; they break across packages.
4. **Don't duplicate constructor parameters in properties** (Java is one of the affected languages).
5. **Don't add `java.util.*`, `java.time.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` to `customImports`.** They're automatic.
6. **Don't reference an undefined `typeIdentifier`** — the property is silently dropped, leaving an orphaned reference.
7. **Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) emit no files.** They are reference helpers only.
8. **`Number` ≠ `double`.** In Java it becomes `int`. Use `"type": "BigDecimal"` / `"type": "double"` / `"type": "long"` for non-integer numbers.

---

## 6. Output structure (Java)

For a call with `outputPath="."` and `packageName="com.acme.shop"`:

```
./src/main/java/com/acme/shop/<path>/<ClassName>.java
./src/main/java/com/acme/shop/<path>/<InterfaceName>.java
./src/main/java/com/acme/shop/<path>/<EnumName>.java
```

Each file gets:
- `package com.acme.shop.<path-as-dots>;`
- Auto-resolved `import` statements (auto-list + cross-references + customImports).
- Class/interface/enum declaration with members in this order: properties → constructor (if `constructorParameters`) → customCode methods.
- Getters/setters auto-emitted for properties.

Files are written by default; pass `dryRun: true` to see the contents in the response without writing.

---

## 7. Worked Java example (canonical reference)

```json
{
  "language": "java",
  "packageName": "com.example.shop",
  "outputPath": "./generated",
  "enums": [{
    "name": "OrderStatus",
    "typeIdentifier": "order-status",
    "path": "domain/order",
    "members": [
      { "name": "Pending", "value": 0 },
      { "name": "Shipped", "value": 1 },
      { "name": "Delivered", "value": 2 }
    ]
  }],
  "classes": [
    {
      "name": "Money",
      "typeIdentifier": "money",
      "path": "domain/shared",
      "constructorParameters": [
        { "name": "amount", "type": "BigDecimal" },
        { "name": "currency", "primitiveType": "String" }
      ]
    },
    {
      "name": "Customer",
      "typeIdentifier": "customer",
      "path": "domain/customer",
      "decorators": [{ "code": "@Entity" }],
      "constructorParameters": [
        { "name": "id", "type": "UUID" },
        { "name": "email", "primitiveType": "String" }
      ],
      "properties": [
        { "name": "createdAt", "type": "Instant" }
      ]
    },
    {
      "name": "Order",
      "typeIdentifier": "order",
      "path": "domain/order",
      "decorators": [{ "code": "@Entity" }],
      "constructorParameters": [
        { "name": "id", "type": "UUID" },
        { "name": "customer", "typeIdentifier": "customer" },
        { "name": "total", "typeIdentifier": "money" },
        { "name": "status", "typeIdentifier": "order-status" }
      ],
      "customCode": [
        {
          "code": "public void ship() { /* state transition */ throw new UnsupportedOperationException(\"not implemented\"); }"
        }
      ]
    }
  ],
  "interfaces": [{
    "name": "OrderRepository",
    "typeIdentifier": "order-repo",
    "path": "domain/order",
    "customCode": [
      { "code": "Optional<$order> findById(UUID id);",
        "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] },
      { "code": "List<$order> findByCustomer(UUID customerId);",
        "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }] }
    ]
  }]
}
```

This produces (under `./generated/src/main/java/com/example/shop/...`):
- `domain/order/OrderStatus.java`
- `domain/shared/Money.java`
- `domain/customer/Customer.java`
- `domain/order/Order.java`
- `domain/order/OrderRepository.java`

with correct `package`, `import` (auto for `UUID`, `BigDecimal`, `Instant`, `List`, `Optional`; cross-package imports auto-resolved between Order ↔ Customer ↔ Money ↔ OrderStatus).

---

## 8. Quick decision table for Java DDD specs

| Spec says… | MetaEngine input |
|---|---|
| Aggregate root entity | `class` with `decorators: [{code:"@Entity"}]`, fields in `constructorParameters` (or `properties` if mutable JPA-style) |
| Value object (immutable) | `class` with all fields in `constructorParameters` (engine emits final-field class with all-args ctor + getters). Or `customFile` with `record`. |
| Domain event | `class` with `constructorParameters` for payload |
| Repository | `interface` with method signatures in `customCode` |
| Domain service | `class` with `decorators: [{code:"@Service"}]` + Spring `customImports`; methods in `customCode` |
| Enum | `enums[]` (members get `ALL_CAPS` automatically) |
| Money / decimal | `"type": "BigDecimal"` (NOT `primitiveType: "Number"`) |
| Date/time | `"type": "Instant"` / `"LocalDate"` / `"LocalDateTime"` (NOT legacy `Date`) |
| UUID id | `"type": "UUID"` |
| Collection field | `arrayTypes` entry + reference via `typeIdentifier` |
| Map field | `dictionaryTypes` entry + reference via `typeIdentifier` |
| Generic repository | `class` with `genericArguments` + `concreteGenericClasses` for closed type |
| Method body unknown | `throw new UnsupportedOperationException("not implemented");` inside `customCode` |

---

## 9. Final reminders

- The judge tolerates language-idiomatic transformations (Java enum `ALL_CAPS`, Java method signatures with getters/setters auto-emitted). Don't fight idioms — accept what the engine produces.
- Always set `packageName` explicitly to match the spec's domain.
- Run ONE `generate_code` call. If the response shows an error like "typeIdentifier 'X' not found", you have a typo or a missing definition — fix the spec, call again with the COMPLETE spec (not a partial patch).
- `dryRun: true` is your friend if you want to inspect output before committing files.

End of brief.
