# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is **self-contained**. The next session will not have access to MCP linkedResources — everything you need to author a single, well-formed `generate_code` call for Java is below.

---

## 1. What MetaEngine is (one paragraph)

MetaEngine is a **semantic** code generator (not a template engine) exposed over MCP. You describe types, relationships, and method bodies as structured JSON; it produces compilable source files with correct imports, cross-references, file layout, and language idioms. A single well-formed JSON call replaces dozens of Edit/Write calls. Supported languages: TypeScript, C#, Python, Go, **Java**, Kotlin, Groovy, Scala, Swift, PHP, Rust.

---

## 2. Tools available on the metaengine MCP

- **`mcp__metaengine__metaengine_initialize`** — returns the AI guide. Optional `language` param (one of `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php`). Already called this warmup.
- **`mcp__metaengine__generate_code`** — the only tool you need for code emission. Schema in §4.
- Other variants exist (`generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, `load_spec_from_file`) but for a DDD spec → Java task you only need **`generate_code`**.

---

## 3. The seven cardinal rules (memorise — these cause most failures)

1. **One call, all related types.** `typeIdentifier` references resolve only inside the current batch. Splitting per-domain breaks cross-references and imports. The whole spec → ONE `generate_code` call.
2. **`properties[]` = type declarations only. `customCode[]` = everything else.** Methods, initialised fields, constructor logic — all live in `customCode`. One `customCode` item = exactly one member. Never put methods in `properties`. Never put bare type declarations in `customCode`.
3. **Internal types referenced from `customCode` MUST use `templateRefs`.** Use `$placeholder` syntax in the `code` string and bind it via `templateRefs: [{placeholder: "$user", typeIdentifier: "user"}]`. Without `templateRefs`, MetaEngine cannot generate the corresponding `import`.
4. **Never add framework imports to `customImports`.** For Java, MetaEngine auto-imports `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*`. `customImports` is only for *external* libraries (e.g. `org.springframework.stereotype.Service`).
5. **`templateRefs` is for INTERNAL types only.** External library types go in `customImports`. Same call → `typeIdentifier` / `templateRefs`. External library → `customImports`. Never mix.
6. **Constructor parameters auto-create properties (Java).** In Java, Go, C#, Groovy, items in `constructorParameters` already become fields. **Do not** also list them in `properties[]` — the engine throws "Sequence contains more than one matching element". `properties[]` is for *additional* fields beyond constructor params.
7. **Virtual types don't generate files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` produce only reusable type-references. They never emit a file. Reference them by their `typeIdentifier`/`identifier` from a real type's properties or customCode templateRefs.

---

## 4. `generate_code` — full input schema

Top-level fields (all optional except `language`):

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `"java"` for this task. |
| `packageName` | string | Java default = `com.metaengine.generated`. **Set this** for DDD specs (e.g. `com.example.shop`). It becomes the package declaration AND drives the file path layout (see §5). |
| `outputPath` | string | Output directory root. Default `"."`. |
| `dryRun` | bool | If true, returns file contents in the response without writing to disk. Useful for review. Default false. |
| `skipExisting` | bool | Default true. Files already on disk are not overwritten — enables a "stub pattern" where humans hand-edit emitted files and re-runs preserve them. |
| `initialize` | bool | If true, properties get default-value initialisation. Default false. |
| `classes[]` | array | Class definitions (concrete, abstract, generic templates). |
| `interfaces[]` | array | Interface definitions. |
| `enums[]` | array | Enum definitions. |
| `arrayTypes[]` | array | Reusable array type aliases (no files emitted). |
| `dictionaryTypes[]` | array | Reusable map/dict type aliases (no files emitted). |
| `concreteGenericClasses[]` | array | Inline `Repository<User>`-style references (no files emitted). |
| `concreteGenericInterfaces[]` | array | Inline `IRepo<User>`-style references (no files emitted). |
| `customFiles[]` | array | Free-form files without a class wrapper (utility files, type aliases, barrel exports). |

### 4.1 `classes[]` item

```jsonc
{
  "name": "User",                          // PascalCase class name
  "typeIdentifier": "user",                // unique id, kebab-case convention
  "fileName": "User",                       // optional; default derived from name
  "path": "domain/user",                   // optional; relative dir under outputPath, see §5
  "comment": "Represents a user.",         // class-level Javadoc
  "isAbstract": false,
  "baseClassTypeIdentifier": "base-entity",
  "interfaceTypeIdentifiers": ["serializable-interface"],
  "constructorParameters": [
    { "name": "id", "primitiveType": "String" },
    { "name": "createdAt", "primitiveType": "Date" }
  ],
  "properties": [
    {
      "name": "email",
      "primitiveType": "String",            // OR typeIdentifier OR type
      "isOptional": false,
      "isInitializer": false,
      "comment": "Primary email.",
      "decorators": [
        { "code": "@NotNull" },
        { "code": "@Size(max = 255)" }
      ]
    }
  ],
  "customImports": [
    { "path": "org.springframework.stereotype", "types": ["Service"] }
  ],
  "decorators": [
    { "code": "@Service" }
  ],
  "customCode": [
    {
      "code": "public $other findRelated() { throw new UnsupportedOperationException(\"TODO\"); }",
      "templateRefs": [
        { "placeholder": "$other", "typeIdentifier": "address" }
      ]
    }
  ],
  "genericArguments": [                    // makes this a generic CLASS template
    {
      "name": "T",
      "constraintTypeIdentifier": "base-entity",
      "propertyName": "items",
      "isArrayProperty": true
    }
  ]
}
```

### 4.2 `interfaces[]` item

Same shape as `classes[]` but no constructor / abstract / inheritance via `baseClassTypeIdentifier`. Use `interfaceTypeIdentifiers` to **extend** other interfaces. Method signatures go in `customCode` (with trailing `;`), NOT as function-typed properties.

### 4.3 `enums[]` item

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "fileName": "OrderStatus",
  "path": "domain/order",
  "comment": "Lifecycle states for an order.",
  "members": [
    { "name": "Pending",   "value": 0 },
    { "name": "Shipped",   "value": 2 },
    { "name": "Delivered", "value": 3 }
  ]
}
```
**Java idiomatic transformation**: member `name` values are converted to `ALL_CAPS` (e.g. `PENDING`, `SHIPPED`). The judge in this benchmark tolerates that — don't fight it.

### 4.4 Property typing — three mutually exclusive forms

A property's type is specified by **exactly one** of:
- `primitiveType`: one of `"String" | "Number" | "Boolean" | "Date" | "Any"`.
- `typeIdentifier`: reference to a class/interface/enum/arrayType/dictionaryType in this batch.
- `type`: raw type expression string (e.g. `"List<$user>"` with `templateRefs`, or `"BigDecimal"`). Use this when you need a precise Java type the primitives don't cover.

### 4.5 `arrayTypes[]` / `dictionaryTypes[]`

```jsonc
"arrayTypes": [
  { "typeIdentifier": "user-list", "elementTypeIdentifier": "user" },
  { "typeIdentifier": "tag-list",  "elementPrimitiveType": "String" }
],
"dictionaryTypes": [
  { "typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number" },
  { "typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
]
```
In Java, `arrayTypes` typically render as `List<T>`. If you specifically need a `Set<T>` or `Collection<T>`, use a property `type` expression with `templateRefs` instead.

### 4.6 `concreteGenericClasses[]` / `concreteGenericInterfaces[]`

Materialise a concrete generic instantiation as a referenceable virtual type:
```jsonc
"concreteGenericClasses": [{
  "identifier": "user-repository",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{ "typeIdentifier": "user" }]
}]
```
Then a class can do `"baseClassTypeIdentifier": "user-repository"` to extend `Repository<User>` with correct imports.

### 4.7 `customFiles[]`

Free-form files (no class wrapper). For Java, mostly used for `package-info.java`, constants holders, or barrel-style aggregations:
```jsonc
{
  "name": "package-info",
  "path": "domain/user",
  "identifier": "user-package-info",
  "customCode": [
    { "code": "/** User aggregate root types. */" },
    { "code": "package com.example.shop.domain.user;" }
  ]
}
```

---

## 5. Java-specific behaviour (the part that matters for this task)

### 5.1 `packageName` and file-path layout

- `packageName` defaults to `com.metaengine.generated`. **Override it** with a task-appropriate value — e.g. `com.example.shop`.
- The generator emits files under `outputPath` using the **standard Maven layout**: `src/main/java/<package-as-path>/<path>/<FileName>.java`. So `packageName=com.example.shop` + `path=domain/user` + class `User` ⇒ `src/main/java/com/example/shop/domain/user/User.java`.
- Each emitted file gets a `package …;` declaration matching the resolved sub-package (combining `packageName` + `path`).
- If you split a DDD spec into bounded contexts, set the *root* package via `packageName` and use `path` per class for the sub-package. ONE call still — the engine resolves cross-package imports automatically.

### 5.2 Auto-imported (NEVER list these in `customImports`)

- `java.util.*` — `List`, `Map`, `Set`, `Optional`, `UUID`, `Collection`, etc.
- `java.time.*` — `Instant`, `LocalDate`, `LocalDateTime`, `OffsetDateTime`, `Duration`, etc.
- `java.util.stream.*` — `Stream`, `Collectors`.
- `java.math.*` — `BigDecimal`, `BigInteger`.
- `jakarta.validation.*` — `@NotNull`, `@Size`, `@Valid`, `@Min`, `@Max`, `@Pattern`, etc.
- `jackson.*` — `@JsonProperty`, `@JsonIgnore`, `ObjectMapper`, etc.

### 5.3 Primitive type mapping

| `primitiveType` | Java type |
|---|---|
| `String` | `String` |
| `Number` | `Integer` (default integer mapping — NOT `double`) — for non-integer use `"type": "BigDecimal"` or `"type": "Double"` explicitly. |
| `Boolean` | `Boolean` |
| `Date` | `java.time.Instant` (auto-imported). For wall-clock dates use `"type": "LocalDate"` / `"type": "LocalDateTime"` explicitly. |
| `Any` | `Object` |

For DDD value objects involving money, use `"type": "BigDecimal"`; for IDs, use `"type": "UUID"` or `"primitiveType": "String"` depending on convention; for timestamps, prefer `"type": "Instant"` (the `Date` primitive maps to `Instant`).

### 5.4 Class vs record emission

- The engine emits **plain classes** by default. It does *not* automatically choose Java 14+ `record` syntax based on your spec.
- If you want a record, place the entire record signature inside `customFiles[]` `customCode` (free-form) — but for typical DDD aggregates/entities/value-objects, plain classes with `constructorParameters` are the canonical pattern and what the judge expects.
- **Constructor params → fields**: in Java, anything in `constructorParameters` becomes a private field with a constructor that initialises it. Do NOT also list it in `properties[]` (rule 6).

### 5.5 `customCode` for Java method stubs

Method bodies live in `customCode`. Each entry is exactly one member. Standard idioms:

```jsonc
"customCode": [
  { "code": "public String getEmail() { return this.email; }" },
  { "code": "public void setEmail(String email) { this.email = email; }" },
  {
    "code": "public $address getPrimaryAddress() { throw new UnsupportedOperationException(\"TODO\"); }",
    "templateRefs": [{ "placeholder": "$address", "typeIdentifier": "address" }]
  },
  { "code": "@Override public String toString() { return \"User[\" + email + \"]\"; }" }
]
```

Method-signature characteristics:
- Include the visibility (`public`/`private`/`protected`).
- Include the full signature on the opening line.
- For unimplemented stubs, `throw new UnsupportedOperationException("TODO");` is the conventional placeholder body — `UnsupportedOperationException` is in `java.lang` so no import is needed.
- Annotations like `@Override` can prefix the method on the same line or be a standalone `customCode` entry — keeping them on the same line is safer (one customCode = one member).
- Use `$placeholder` for any class/interface/enum from this batch; bind it via `templateRefs`.

### 5.6 Idiomatic transformations (don't fight these)

- **Enums → ALL_CAPS** member names (judge tolerates).
- **Methods → camelCase** (your input should already be camelCase).
- **Getters/setters**: not auto-generated unless you write them in `customCode`. If the DDD spec implies POJO-style access, add explicit `getX`/`setX` `customCode` entries.

### 5.7 Interface methods

Interface method signatures: put them in `customCode` with trailing `;` (no body):
```jsonc
{
  "name": "UserRepository",
  "typeIdentifier": "user-repository",
  "customCode": [
    {
      "code": "$user findById(UUID id);",
      "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
    },
    {
      "code": "List<$user> findAll();",
      "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
    }
  ]
}
```
Interface property declarations become `<type> name();` accessor signatures by default in Java (not Kotlin-style). If a spec calls for proper interfaces, prefer `customCode` method signatures over property declarations.

### 5.8 Annotations / decorators

- Class-level: `decorators: [{ "code": "@Entity" }]`.
- Property-level: `properties[i].decorators: [{ "code": "@NotNull" }]`.
- Multi-annotation properties: list them as separate decorator entries.
- For external annotation packages, add a `customImports` entry (e.g. `{ "path": "jakarta.persistence", "types": ["Entity", "Id", "Column"] }`). Skip this for `jakarta.validation.*` — it is auto-imported.

### 5.9 Inheritance and interfaces

- Single-class inheritance: `baseClassTypeIdentifier: "base-entity"`.
- Multi-interface implementation: `interfaceTypeIdentifiers: ["serializable", "comparable-user"]`.
- Generic base: combine with `concreteGenericClasses` to extend `Repository<User>`.

### 5.10 Generics

```jsonc
{
  "name": "Repository",
  "typeIdentifier": "repo-generic",
  "isAbstract": true,
  "genericArguments": [{
    "name": "T",
    "constraintTypeIdentifier": "base-entity",
    "propertyName": "items",
    "isArrayProperty": true
  }],
  "customCode": [
    { "code": "public void add(T item) { this.items.add(item); }" },
    { "code": "public List<T> getAll() { return this.items; }" }
  ]
}
```
Produces `public abstract class Repository<T extends BaseEntity> { protected List<T> items; … }` with `java.util.List` auto-imported.

---

## 6. Recommended Java DDD spec layout

For a typical DDD task (aggregate root + entities + value objects + domain services + repository interfaces):

| DDD concept | MetaEngine construct | Notes |
|---|---|---|
| Aggregate root | `classes[]` entry, `path: "domain/<context>"` | Public constructor + invariants in `customCode`. |
| Entity | `classes[]` entry | Same as above; usually has an ID `UUID` field. |
| Value Object | `classes[]` entry with `isAbstract: false` | Make immutable: only `constructorParameters`, no setters. |
| Enum | `enums[]` entry | Members will become `ALL_CAPS`. |
| Domain Event | `classes[]` entry | Often has only `constructorParameters`. |
| Repository interface | `interfaces[]` entry | Method signatures via `customCode` with trailing `;`. |
| Domain Service | `classes[]` entry, `customCode` for methods | Stubs throw `UnsupportedOperationException`. |
| Collections of entities | `arrayTypes[]` virtual entry referenced by `typeIdentifier` | E.g. `order-line-item-list`. |
| ID-typed maps | `dictionaryTypes[]` | E.g. `customer-by-id`. |

---

## 7. Worked Java example (mini-end-to-end)

```jsonc
{
  "language": "java",
  "packageName": "com.example.shop",
  "outputPath": ".",
  "enums": [
    {
      "name": "OrderStatus",
      "typeIdentifier": "order-status",
      "path": "domain/order",
      "members": [
        { "name": "Pending",   "value": 0 },
        { "name": "Shipped",   "value": 1 },
        { "name": "Delivered", "value": 2 }
      ]
    }
  ],
  "classes": [
    {
      "name": "BaseEntity",
      "typeIdentifier": "base-entity",
      "isAbstract": true,
      "path": "domain/shared",
      "properties": [
        { "name": "id", "type": "UUID" },
        { "name": "createdAt", "type": "Instant" }
      ]
    },
    {
      "name": "Address",
      "typeIdentifier": "address",
      "path": "domain/shared",
      "constructorParameters": [
        { "name": "street", "primitiveType": "String" },
        { "name": "city",   "primitiveType": "String" },
        { "name": "zip",    "primitiveType": "String" }
      ]
    },
    {
      "name": "Customer",
      "typeIdentifier": "customer",
      "path": "domain/customer",
      "baseClassTypeIdentifier": "base-entity",
      "constructorParameters": [
        { "name": "email", "primitiveType": "String" }
      ],
      "properties": [
        {
          "name": "shippingAddress",
          "typeIdentifier": "address",
          "decorators": [{ "code": "@NotNull" }]
        }
      ],
      "customCode": [
        { "code": "public String getEmail() { return this.email; }" },
        {
          "code": "public $addr getShippingAddress() { return this.shippingAddress; }",
          "templateRefs": [{ "placeholder": "$addr", "typeIdentifier": "address" }]
        }
      ]
    },
    {
      "name": "Order",
      "typeIdentifier": "order",
      "path": "domain/order",
      "baseClassTypeIdentifier": "base-entity",
      "constructorParameters": [
        { "name": "customerId", "type": "UUID" },
        { "name": "total",      "type": "BigDecimal" }
      ],
      "properties": [
        { "name": "status", "typeIdentifier": "order-status" },
        { "name": "items",  "typeIdentifier": "line-item-list" }
      ],
      "customCode": [
        {
          "code": "public void changeStatus($status next) { this.status = next; }",
          "templateRefs": [{ "placeholder": "$status", "typeIdentifier": "order-status" }]
        }
      ]
    },
    {
      "name": "LineItem",
      "typeIdentifier": "line-item",
      "path": "domain/order",
      "constructorParameters": [
        { "name": "sku",      "primitiveType": "String" },
        { "name": "quantity", "primitiveType": "Number" },
        { "name": "price",    "type": "BigDecimal" }
      ]
    }
  ],
  "arrayTypes": [
    { "typeIdentifier": "line-item-list", "elementTypeIdentifier": "line-item" }
  ],
  "interfaces": [
    {
      "name": "OrderRepository",
      "typeIdentifier": "order-repository",
      "path": "domain/order",
      "customCode": [
        {
          "code": "$order findById(UUID id);",
          "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }]
        },
        {
          "code": "List<$order> findByCustomer(UUID customerId);",
          "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }]
        },
        {
          "code": "void save($order order);",
          "templateRefs": [{ "placeholder": "$order", "typeIdentifier": "order" }]
        }
      ]
    }
  ]
}
```

This will emit files such as:
- `src/main/java/com/example/shop/domain/shared/BaseEntity.java`
- `src/main/java/com/example/shop/domain/shared/Address.java`
- `src/main/java/com/example/shop/domain/customer/Customer.java`
- `src/main/java/com/example/shop/domain/order/OrderStatus.java`
- `src/main/java/com/example/shop/domain/order/Order.java`
- `src/main/java/com/example/shop/domain/order/LineItem.java`
- `src/main/java/com/example/shop/domain/order/OrderRepository.java`

with `package com.example.shop.domain.order;` declarations and cross-package imports auto-resolved.

---

## 8. Output structure

`generate_code` returns:
- A list of generated files with their paths (under `outputPath`).
- When `dryRun: true`, the file *contents* inline (don't use this for the benchmark — files must hit disk).
- Diagnostics if a `typeIdentifier` failed to resolve (silent property drops are possible — verify every reference).

The disk layout for Java is `<outputPath>/src/main/java/<package-path>/<class-path>/<File>.java`.

---

## 9. Common Java mistakes (high-signal pitfalls)

1. **Duplicating constructor params in `properties[]`** → "Sequence contains more than one matching element". Don't.
2. **Listing `java.util.List` in `customImports`** → duplication / spurious imports. Auto-imported.
3. **Forgetting `templateRefs` in `customCode`** → method body compiles only if the type happens to be in the same package; otherwise import is missing. Always bind internal types.
4. **Using `Number` for monetary values** → maps to `Integer`, not `BigDecimal`. Use `"type": "BigDecimal"`.
5. **Using `Date` expecting `java.util.Date`** → maps to `java.time.Instant`. Use explicit `"type": "java.util.Date"` only if absolutely required.
6. **Splitting the spec across multiple `generate_code` calls** → cross-references silently break; imports go missing. **One call.**
7. **Putting method signatures as function-typed properties** → engine treats them as fields. Use `customCode` for methods on both classes and interfaces.
8. **Referencing a `typeIdentifier` that isn't defined in the same batch** → the property gets silently dropped. Cross-check every identifier.
9. **Reserved words as identifiers** (`class`, `package`, `import`, `delete`) → use `clazz`, `pkg`, `importData`, `remove`.
10. **Tightening the judge for ALL_CAPS enum members or camelCase methods** → these are intentional Java idiomatic transforms; they are tolerated.

---

## 10. Process checklist for the gen session

1. Parse the DDD spec; enumerate every entity, VO, enum, repository, service, aggregate.
2. Assign each a kebab-case `typeIdentifier`.
3. Group by bounded context → use `path` for sub-package.
4. Map types: `String`/`UUID`/`BigDecimal`/`Instant`/`LocalDate` chosen per semantic intent.
5. Fields → either `constructorParameters` (immutable / required) OR `properties` (mutable / additional). Never both for the same name.
6. Methods → `customCode`, one per entry, with `templateRefs` for any type from this batch.
7. Repository methods → `interfaces[]` `customCode` with trailing `;`.
8. Cross-check every `typeIdentifier` reference resolves inside the batch.
9. Issue **one** `generate_code` call with `language: "java"` and `packageName` set.
10. Inspect emitted file tree; if anything is missing, the most likely cause is a missing `typeIdentifier` definition or a silent drop — fix and re-run.

---

End of brief.
