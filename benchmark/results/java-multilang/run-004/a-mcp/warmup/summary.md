# MetaEngine MCP — Knowledge Brief (Java focus)

This is a self-contained summary of the MetaEngine MCP server, derived from
its `linkedResources` (the AI Code Generation Guide, the Examples document
and the `generate_code` tool schema). The next session will generate **Java**
code from a DDD spec without access to these docs — everything it needs is
captured below.

---

## 1. What MetaEngine is

MetaEngine is a *semantic* code generator (not a templating engine). You
describe types, relationships and methods as a single structured JSON
document; it emits compilable, correctly-imported source files for
TypeScript, C#, Python, Go, **Java**, Kotlin, Groovy, Scala, Swift, PHP and
Rust.

It resolves cross-references between types, manages imports automatically,
and applies language idioms. One well-formed JSON call replaces dozens of
error-prone file writes.

---

## 2. Tools exposed (MCP)

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__metaengine_initialize` | Returns the AI guide. Optional `language` parameter (one of: typescript, python, go, csharp, **java**, kotlin, groovy, scala, swift, php). Call once at the start of a session. |
| `mcp__metaengine__generate_code` | The workhorse. Takes a JSON spec (classes, interfaces, enums, …) and emits source files. Required: `language`. |
| `mcp__metaengine__generate_openapi` | Generate from an OpenAPI spec. |
| `mcp__metaengine__generate_graphql` | Generate from a GraphQL schema. |
| `mcp__metaengine__generate_protobuf` | Generate from a Protobuf definition. |
| `mcp__metaengine__generate_sql` | Generate from a SQL DDL. |
| `mcp__metaengine__load_spec_from_file` | Load a spec file from disk and feed it to the engine. |

Linked resources:
- `metaengine://guide/ai-assistant` — the full AI Code Generation Guide.
- `metaengine://guide/examples` — worked input/output examples.

---

## 3. `generate_code` — full input schema

Top-level fields (all optional except `language`):

| Field | Type | Notes |
|---|---|---|
| `language` | enum **REQUIRED** | `"typescript" \| "python" \| "go" \| "csharp" \| "java" \| "kotlin" \| "groovy" \| "scala" \| "swift" \| "php" \| "rust"` |
| `packageName` | string | Java/Kotlin/Groovy default: `com.metaengine.generated`. Sets the Java `package` declaration and on-disk path. |
| `outputPath` | string (default `.`) | Root directory where files are written. |
| `initialize` | boolean (default false) | When true, properties get default-value initializers in generated code. |
| `dryRun` | boolean (default false) | If true, no files are written — generated code is returned in the response for review. |
| `skipExisting` | boolean (default true) | When true, files that already exist on disk are not overwritten (stub pattern). |
| `classes` | array | Class definitions (concrete + generic templates). |
| `interfaces` | array | Interface definitions (concrete + generic templates). |
| `enums` | array | Enum definitions. |
| `arrayTypes` | array | Reusable array type aliases — produces NO files. |
| `dictionaryTypes` | array | Reusable dictionary type aliases — produces NO files. |
| `concreteGenericClasses` | array | Inline concrete generic refs like `Repository<User>` — produces NO files. |
| `concreteGenericInterfaces` | array | Inline concrete generic refs like `IRepository<User>` — produces NO files. |
| `customFiles` | array | Free-form files (utility / type alias / barrel exports) without a class wrapper. |

### 3.1 `classes[]` item

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | Unique id used to reference this class from other definitions in the same call. |
| `fileName` | string | Override generated file name (without extension). |
| `path` | string | Subdirectory under `outputPath`/`packageName` (e.g. `services/auth`). |
| `comment` | string | Class-level docstring. |
| `isAbstract` | boolean | Generates `abstract class` in Java. |
| `baseClassTypeIdentifier` | string | Type id of the base class to `extends`. May refer to another class OR a `concreteGenericClasses[]` entry. |
| `interfaceTypeIdentifiers` | string[] | Interface ids to `implements`. |
| `genericArguments` | array | Makes this a generic template (`class Repository<T>`). Each item: `name`, `constraintTypeIdentifier`, `propertyName`, `isArrayProperty`. |
| `constructorParameters` | array | Constructor params. Each item: `name`, plus one of `primitiveType`/`type`/`typeIdentifier`. **In Java these auto-become fields — DO NOT duplicate them in `properties[]`.** |
| `properties` | array | Field declarations only (no logic, no initialization). See 3.4. |
| `customCode` | array | Methods, initialized fields, ctor bodies — anything with logic. One block = one member. See 3.5. |
| `customImports` | array | External library imports only (never JDK / Jackson / validation packages). Each item: `path`, `types[]`. |
| `decorators` | array | Class-level annotations (e.g. `@Entity`, `@Service`). Each item: `code`, `templateRefs[]`. |

### 3.2 `interfaces[]` item

Same shape as classes: `name`, `typeIdentifier`, `fileName`, `path`, `comment`,
`genericArguments`, `interfaceTypeIdentifiers` (extends), `properties`,
`customCode`, `customImports`, `decorators`.

For Java interface methods, put **method signatures** in `customCode`
(e.g. `"List<$user> findAll();"`) — do **not** model them as
function-typed properties.

### 3.3 `enums[]` item

| Field | Type | Notes |
|---|---|---|
| `name` | string | Enum type name. |
| `typeIdentifier` | string | Reference id. |
| `fileName` | string | Optional override. |
| `path` | string | Optional sub-path. |
| `comment` | string | Doc comment. |
| `members` | array | Each: `name` (string), `value` (number). |

### 3.4 `properties[]` item (used in classes & interfaces)

| Field | Type | Notes |
|---|---|---|
| `name` | string | Field name. **Avoid Java reserved words** (`class`, `import`, `delete`, `new`, etc.) — use `clazz`, `importData`, `remove`. |
| `primitiveType` | enum | One of `"String" \| "Number" \| "Boolean" \| "Date" \| "Any"`. |
| `type` | string | Raw type expression — use this for non-primitive native types (`List<$user>`, `BigDecimal`, `long`). Combine with `templateRefs` when it embeds a generated type. |
| `typeIdentifier` | string | Reference to another generated type in the same call. |
| `isOptional` | boolean | Marks the field optional (language-specific representation). |
| `isInitializer` | boolean | Generates a default-value initializer for the field. |
| `comment` | string | Field doc comment. |
| `commentTemplateRefs` | array | Template refs used inside the comment. |
| `decorators` | array | Field annotations (`@NotNull`, `@Email`, `@Column`, …). Each: `code`, `templateRefs[]`. |
| `templateRefs` | array | Required when `type` contains `$placeholder` referring to another generated type. |

Exactly one of `primitiveType` / `type` / `typeIdentifier` should be set per
property.

### 3.5 `customCode[]` item

| Field | Type | Notes |
|---|---|---|
| `code` | string | The literal source for ONE member (one method or one initialized field). MetaEngine inserts blank lines between blocks automatically. |
| `templateRefs` | array | List of `{placeholder, typeIdentifier}` pairs. Every reference inside `code` to a *generated* type must use a `$placeholder` that maps to a `typeIdentifier`, so the engine can rewrite the placeholder AND emit the correct import. |

### 3.6 `arrayTypes[]` item

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string **REQUIRED** | Id used by other types to reference this array. |
| `elementPrimitiveType` | enum | `String`/`Number`/`Boolean`/`Date`/`Any`. |
| `elementTypeIdentifier` | string | Element is another generated type. |

Produces NO file. In Java, an `arrayTypes` reference becomes a `List<T>` /
`Collection<T>`-style field — see §6 for the precise mapping caveat.

### 3.7 `dictionaryTypes[]` item

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string **REQUIRED** | Id. |
| `keyPrimitiveType` | enum | Primitive key. |
| `keyType` | string | Raw string key type. |
| `keyTypeIdentifier` | string | Key is a generated type. |
| `valuePrimitiveType` | enum | Primitive value. |
| `valueTypeIdentifier` | string | Value is a generated type. |

Supports all 4 combinations of primitive / custom for key + value. Produces
NO file. In Java this maps to `Map<K, V>` with `java.util.Map` auto-imported.

### 3.8 `concreteGenericClasses[]` / `concreteGenericInterfaces[]`

| Field | Type | Notes |
|---|---|---|
| `identifier` | string | Id for this concrete instantiation (referenced like any other type id). |
| `genericClassIdentifier` | string | Id of the generic template. |
| `genericArguments` | array | Each: `primitiveType` OR `typeIdentifier`. |

Use these to refer to `Repository<User>` as a base class or as a property
type. They produce NO file but trigger correct imports in places that
reference them.

### 3.9 `customFiles[]` item

| Field | Type | Notes |
|---|---|---|
| `name` | string | File base name (no extension). |
| `fileName` | string | Override. |
| `path` | string | Subdirectory. |
| `identifier` | string | Optional id so other files can `customImports` this file. |
| `customCode` | array | Free-form code blocks, each producing one declaration. |
| `customImports` | array | External imports for this file. |

For Java, prefer real `classes`/`interfaces` over `customFiles` — Java has
no top-level type aliases. `customFiles` is best reserved for things like a
`package-info.java` or a small utility class with only static helpers.

---

## 4. The seven critical rules

These are the rules whose violation causes the most failures. Apply them
mechanically.

1. **One call, all related types.** `typeIdentifier` resolution is scoped
   to a single `generate_code` call. Splitting per-domain across calls breaks
   the type graph and silently drops cross-references. **For a DDD spec that
   spans multiple bounded contexts, still emit it in ONE call.** Use `path`
   to segregate files into subpackages.

2. **Properties = type declarations. CustomCode = everything else.** A
   `properties[]` entry declares a field with a type, no logic, no
   initializer expression. Any method, ctor body, initialized field, or
   logic-bearing line goes in `customCode[]`. Each `customCode` block is
   exactly one member.

3. **Internal types in `customCode` MUST use `templateRefs`.** Write
   `Optional<$user> findById(UUID id);` with
   `templateRefs: [{placeholder: "$user", typeIdentifier: "user"}]`,
   not the bare class name. Without `templateRefs`, MetaEngine cannot emit
   the cross-package `import` statement and the file will not compile when
   types live in different packages.

4. **Never add framework imports to `customImports`.** For Java the engine
   auto-imports: `java.util.*`, `java.time.*`, `java.util.stream.*`,
   `java.math.*`, `jakarta.validation.*`, and Jackson packages. Adding any of
   these manually causes duplicate imports / compile errors. Use
   `customImports` only for genuine third-party libs (Spring, Lombok,
   MapStruct, …).

5. **`templateRefs` are ONLY for internal types.** External library types
   must come in via `customImports`. Mixing the two for the same symbol
   breaks both.

6. **Constructor parameters auto-create fields in Java.** Listing the same
   name in both `constructorParameters` and `properties` triggers the error
   *"Sequence contains more than one matching element"*. Put shared fields
   only in `constructorParameters`; put additional non-ctor fields only in
   `properties`.

7. **Virtual types don't generate files.** `arrayTypes`, `dictionaryTypes`,
   `concreteGenericClasses`, and `concreteGenericInterfaces` create reusable
   type references. Their effect is purely on the typegraph — don't expect
   `.java` files for them.

---

## 5. Java-specific behaviour

### 5.1 `packageName` and on-disk layout

- Java default `packageName` = `com.metaengine.generated`.
- `packageName` controls both the `package …;` declaration **and** the
  directory layout. The engine writes files under
  `<outputPath>/src/main/java/<packageName as path>/<class.path>/<file>.java`
  in standard Maven/Gradle layout.
- A class with `path: "services/order"` and `packageName: "com.acme.shop"`
  lands at `src/main/java/com/acme/shop/services/order/<File>.java` and its
  declared package becomes `com.acme.shop.services.order`.
- For a DDD layout, set the root `packageName` to the project root
  (e.g. `com.acme.shop`) and use per-class `path` to segregate aggregates,
  application services, infrastructure, …

### 5.2 Auto-imported packages (DO NOT include in `customImports`)

```
java.util.*            (List, Map, Set, Optional, UUID, Collection, …)
java.time.*            (Instant, LocalDate, LocalDateTime, OffsetDateTime, ZonedDateTime, Duration, Period, …)
java.util.stream.*     (Stream, Collectors, …)
java.math.*            (BigDecimal, BigInteger, MathContext, …)
jakarta.validation.*   (@Valid, @NotNull, @NotBlank, @Email, @Min, @Max, …)
com.fasterxml.jackson.* (ObjectMapper, @JsonProperty, @JsonIgnore, …)
```

Anything else (Spring, Lombok, MapStruct, project-internal helper packages)
must come through `customImports`.

### 5.3 Primitive type mapping

| Spec | Java emission |
|---|---|
| `primitiveType: "String"` | `String` |
| `primitiveType: "Number"` | `int` (assumption — matches the C# documented behaviour; for non-int numerics use `type` explicitly) |
| `primitiveType: "Boolean"` | `boolean` |
| `primitiveType: "Date"` | a `java.time` type (the engine auto-imports `java.time.*`; treat as `Instant` for absolute timestamps and use `type: "LocalDate"` etc. when a specific calendar type is needed) |
| `primitiveType: "Any"` | `Object` |

When the DDD spec calls for a specific Java numeric type, **use the `type`
field** rather than `primitiveType`:

- Money / decimal amounts → `"type": "BigDecimal"`
- 64-bit ids / counts → `"type": "long"` or `"type": "Long"`
- 32-bit floating point → `"type": "double"`
- Long ids that should be wrapper-typed for nullability → `"type": "Long"`

### 5.4 Date / time

`primitiveType: "Date"` is the generic escape hatch but `java.time.*` is
auto-imported, so prefer explicit `type` values:

- Wall-clock timestamp with offset → `"type": "OffsetDateTime"`
- Absolute instant (UTC) → `"type": "Instant"`
- Local civil date → `"type": "LocalDate"`
- Local civil date+time → `"type": "LocalDateTime"`
- Wall-clock w/ zone → `"type": "ZonedDateTime"`
- Duration / period → `"type": "Duration"` / `"type": "Period"`

### 5.5 Collections

- `arrayTypes` → list-style emission. The engine produces `List<T>` (or a
  similar collection); avoid relying on it for Java when you specifically
  need a different collection. For mutable lists when in doubt, declare the
  field with `"type": "List<$x>"` plus `templateRefs`. For sets, use
  `"type": "Set<$x>"`. For ordered maps, `"type": "LinkedHashMap<$k, $v>"`.
- `dictionaryTypes` → `Map<K, V>`. Use it for `Map<String, V>` and
  `Map<Custom, V>` patterns.

### 5.6 Optional / nullability

- `isOptional: true` on a property — language-specific representation. For
  Java, prefer making nullability explicit yourself: use wrapper types
  (`Long`, `Integer`, `Boolean`) and/or `Optional<T>` via the `type` field
  rather than relying on `isOptional`.
- For required-field validation in DDD, attach a `decorators` entry with
  `@NotNull` / `@NotBlank` / `@Valid` (auto-imported from
  `jakarta.validation`).

### 5.7 Class vs record emission

The MetaEngine docs do **not** explicitly document Java `record` emission.
Treat all `classes[]` entries as producing **regular `class`** declarations
(possibly `abstract class` when `isAbstract: true`). To get record-like
immutability, two practical options:

1. Use a regular class with `constructorParameters` listing all fields and
   no extra mutable `properties[]`. Constructor params auto-become fields,
   giving you immutable-ish data carriers.
2. Or, if a true Java record is non-negotiable, fall back to a `customFile`
   that hand-rolls `public record OrderId(UUID value) {}` — but only for
   leaf value objects; you lose typegraph integration.

Default to option (1) for DDD value objects unless the spec explicitly
demands records.

### 5.8 Interface field/method emission

- Interface `properties[]` produce abstract getters/setters in some
  languages; for Java prefer expressing interface members through
  `customCode` with explicit signatures (e.g.
  `"List<$user> findAll();"`).
- `interfaceTypeIdentifiers` on a class generates `implements I1, I2, …`.
- `baseClassTypeIdentifier` on a class generates `extends Base`.

### 5.9 Annotations / decorators

Class-level (`decorators` on the class):
```jsonc
"decorators": [
  {"code": "@Entity"},
  {"code": "@Table(name = \"orders\")"}
]
```

Field-level (`decorators` on a property):
```jsonc
{"name": "email",
 "primitiveType": "String",
 "decorators": [
   {"code": "@NotBlank"},
   {"code": "@Email"}
 ]}
```

`jakarta.validation.*` and Jackson are auto-imported. Annotations from
Spring (`@Service`, `@Component`, `@RestController`, `@Autowired`),
JPA-only-from-Spring, Lombok, etc. require `customImports`.

### 5.10 customCode for method stubs

For method *stubs* on generated services / repositories (where the body
needs to be filled in later by hand or another generator), follow this
idiom:

```jsonc
"customCode": [
  {
    "code": "public Optional<$user> findById(UUID id) {\n    throw new UnsupportedOperationException(\"not implemented\");\n}",
    "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
  }
]
```

Notes:
- Each `customCode` block is exactly one method.
- The engine inserts blank lines between blocks; you don't need leading or
  trailing blank lines inside `code`.
- Indent the body manually (4 spaces) — the engine does not auto-indent
  Java method bodies.
- `Optional`, `UUID`, `List`, `Map` etc. are auto-imported. Don't add them
  to `customImports`.
- For any reference to *another generated type* (`$user` above), you MUST
  use `templateRefs` so the engine emits the correct cross-package
  `import`.
- Use `throw new UnsupportedOperationException("not implemented")` (the
  Java equivalent of `NotImplementedException`) for stubs. It's in
  `java.lang`, so no import needed.
- For void methods, an empty body `{}` is fine; for methods returning a
  collection, prefer `return List.of();` / `return Map.of();` over
  `return null;` to keep the generated code immediately compilable.

### 5.11 Constructor body / parameters

- `constructorParameters` list creates `public Foo(Type a, Type b) { … }`.
  Each param auto-becomes a `private final` (or similar) field — do not
  re-declare in `properties[]`.
- A constructor body beyond simple field assignment must go in `customCode`
  as a literal constructor declaration (matching the class name) — but
  prefer letting MetaEngine generate the trivial `this.x = x;` body
  automatically when possible.

### 5.12 Enums

```jsonc
"enums": [{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "members": [
    {"name": "PENDING", "value": 0},
    {"name": "PAID", "value": 1},
    {"name": "SHIPPED", "value": 2}
  ]
}]
```

Java emission is a standard `public enum OrderStatus { PENDING, PAID, SHIPPED }`.
The numeric `value` is metadata — do not assume it surfaces unless you also
emit a `customCode` block for the int field + getter.

### 5.13 Reserved words to avoid as identifiers

Java keywords that crop up in DDD specs and will fail compilation if used
as field/parameter names: `class`, `interface`, `enum`, `package`, `import`,
`new`, `return`, `default`, `final`, `static`, `public`, `private`,
`protected`, `abstract`, `synchronized`, `volatile`, `transient`, `extends`,
`implements`, `void`, `boolean`, `byte`, `short`, `int`, `long`, `float`,
`double`, `char`. Rename to `clazz`, `iface`, `enumeration`, `pkg`,
`importData`, `created`, etc.

---

## 6. Output layout

For Java, with `packageName = "com.acme.shop"` and a class `Order` at
`path: "domain/order"`:

```
<outputPath>/
  src/main/java/com/acme/shop/domain/order/Order.java
```

Each generated `.java` file contains:
1. `package com.acme.shop.domain.order;`
2. Auto-resolved `import …;` lines (one per used type, both internal and
   auto-imported framework packages).
3. The class / interface / enum declaration with `customImports`,
   `decorators`, `properties`, `constructorParameters`, `customCode`
   stitched together in idiomatic order.

Virtual types (`arrayTypes`, `dictionaryTypes`,
`concreteGenericClasses`, `concreteGenericInterfaces`) **do not emit
files** — they only influence the typegraph and the imports / type
expressions inside files that reference them.

---

## 7. End-to-end DDD recipe (Java)

A typical DDD spec-to-Java run looks like this:

1. **Inventory the spec** — list every aggregate, entity, value object,
   domain event, repository interface, application service, command,
   and read model.
2. **Pick a packageName** — the project root, e.g. `com.acme.shop`.
3. **Assign `path`** per type to mirror DDD layers:
   - Aggregates / entities / value objects: `path: "domain/<bounded-context>"`
   - Domain events: `path: "domain/<bounded-context>/events"`
   - Repository **interfaces**: `path: "domain/<bounded-context>"`
     (interfaces live with the domain).
   - Application services / command handlers: `path: "application/<bounded-context>"`
   - DTOs: `path: "application/<bounded-context>/dto"`
   - Infrastructure adapters / repository **implementations**:
     `path: "infrastructure/<bounded-context>"`
4. **Choose representations**:
   - Value objects → classes with all fields in `constructorParameters`
     (no `properties[]` overlap), making them effectively immutable.
   - Entities / aggregates → classes with id + state fields in
     `constructorParameters` and behaviour as `customCode` methods.
   - Domain events → classes with timestamp + payload in
     `constructorParameters`.
   - Repositories → `interfaces[]` entries with method signatures in
     `customCode`. Use `Optional<$entity>` returns and
     `List<$entity>` for collection returns.
   - Application services → `classes[]` entries that declare the
     dependencies via `constructorParameters` (constructor injection),
     with command handler methods in `customCode` (stubbed with
     `UnsupportedOperationException`).
5. **Wire references**:
   - Every generated type that another type uses must have a
     `typeIdentifier`. Use lowercase-kebab-case ids: `"order"`,
     `"order-status"`, `"order-repository"`.
   - In every `customCode` block, replace inline type names with
     `$placeholder` and add the matching `templateRefs` entry.
   - Use `arrayTypes` for `List<X>` style fields you reference in
     multiple places; otherwise inline `"type": "List<$x>"` works too.
6. **Annotations**:
   - Validation: `@NotNull`, `@NotBlank`, `@Valid` — auto-imported.
   - JPA: `@Entity`, `@Table`, `@Column`, `@Id`, `@GeneratedValue` —
     require `customImports` from `jakarta.persistence` (NOT auto-imported).
   - Spring: `@Service`, `@Repository`, `@RestController` — require
     `customImports` from `org.springframework.*`.
7. **Single call**: bundle every entry — classes, interfaces, enums,
   arrayTypes, dictionaryTypes, concreteGenericClasses, customFiles —
   into ONE `generate_code` invocation.

---

## 8. Worked Java example (synthesized from the patterns)

```jsonc
{
  "language": "java",
  "packageName": "com.acme.shop",
  "outputPath": ".",

  "enums": [{
    "name": "OrderStatus",
    "typeIdentifier": "order-status",
    "path": "domain/order",
    "members": [
      {"name": "PENDING", "value": 0},
      {"name": "PAID", "value": 1},
      {"name": "SHIPPED", "value": 2}
    ]
  }],

  "classes": [
    {
      "name": "OrderId",
      "typeIdentifier": "order-id",
      "path": "domain/order",
      "constructorParameters": [
        {"name": "value", "type": "UUID"}
      ]
    },
    {
      "name": "Money",
      "typeIdentifier": "money",
      "path": "domain/shared",
      "constructorParameters": [
        {"name": "amount", "type": "BigDecimal"},
        {"name": "currency", "primitiveType": "String"}
      ]
    },
    {
      "name": "Order",
      "typeIdentifier": "order",
      "path": "domain/order",
      "decorators": [{"code": "@Entity"}],
      "customImports": [
        {"path": "jakarta.persistence", "types": ["Entity", "Id"]}
      ],
      "constructorParameters": [
        {"name": "id", "typeIdentifier": "order-id"},
        {"name": "total", "typeIdentifier": "money"},
        {"name": "status", "typeIdentifier": "order-status"},
        {"name": "createdAt", "type": "Instant"}
      ],
      "customCode": [
        {
          "code": "public void markPaid() {\n    throw new UnsupportedOperationException(\"not implemented\");\n}"
        }
      ]
    }
  ],

  "interfaces": [
    {
      "name": "OrderRepository",
      "typeIdentifier": "order-repository",
      "path": "domain/order",
      "customCode": [
        {
          "code": "Optional<$order> findById($orderId id);",
          "templateRefs": [
            {"placeholder": "$order", "typeIdentifier": "order"},
            {"placeholder": "$orderId", "typeIdentifier": "order-id"}
          ]
        },
        {
          "code": "List<$order> findByStatus($status status);",
          "templateRefs": [
            {"placeholder": "$order", "typeIdentifier": "order"},
            {"placeholder": "$status", "typeIdentifier": "order-status"}
          ]
        },
        {
          "code": "void save($order order);",
          "templateRefs": [
            {"placeholder": "$order", "typeIdentifier": "order"}
          ]
        }
      ]
    }
  ],

  "classes": [
    {
      "name": "PlaceOrderHandler",
      "typeIdentifier": "place-order-handler",
      "path": "application/order",
      "decorators": [{"code": "@Service"}],
      "customImports": [
        {"path": "org.springframework.stereotype", "types": ["Service"]}
      ],
      "constructorParameters": [
        {"name": "orderRepository", "typeIdentifier": "order-repository"}
      ],
      "customCode": [
        {
          "code": "public $orderId handle($placeOrderCommand command) {\n    throw new UnsupportedOperationException(\"not implemented\");\n}",
          "templateRefs": [
            {"placeholder": "$orderId", "typeIdentifier": "order-id"},
            {"placeholder": "$placeOrderCommand", "typeIdentifier": "place-order-command"}
          ]
        }
      ]
    }
  ]
}
```

(In a real call, both `classes` arrays would be merged into one — duplicate
top-level keys are illegal JSON. Above split is just for readability.)

---

## 9. Common mistakes — checklist

1. Referenced `typeIdentifier` not present in the call → silently dropped.
2. Method signatures placed in `properties` instead of `customCode` → they
   compile as fields of function type or get duplicated.
3. Internal type names hard-coded in `customCode` without `templateRefs`
   → missing imports across packages.
4. Adding `java.util.*` / `java.time.*` / `jakarta.validation.*` /
   `jackson.*` to `customImports` → duplicate imports.
5. Repeating constructor parameter names in `properties[]` → "Sequence
   contains more than one matching element" error.
6. Java reserved words used as identifiers → compile failure.
7. Splitting a DDD spec across multiple `generate_code` calls → broken
   typegraph, no cross-package imports.
8. Using `primitiveType: "Number"` for monetary or 64-bit-id fields →
   integer downgrade. Use `"type": "BigDecimal"` / `"type": "long"`.
9. Forgetting to indent Java method bodies inside `customCode` → ugly
   output (engine does not auto-indent Java bodies).
10. Trying to use `customFiles` as a substitute for actual classes — Java
    has no top-level type aliases, prefer real `classes`/`interfaces`.

---

## 10. Operational notes

- `dryRun: true` is invaluable for review — emits no files, returns
  contents in the response for inspection.
- `skipExisting: true` (the default) plays nicely with hand-edited stubs:
  re-running the generator will not clobber files you've filled in.
- For DDD specs, keep `outputPath` set to the project root and let
  `packageName` + per-class `path` drive the layout under
  `src/main/java/`.
- If a generated file looks wrong, pause and decide whether the issue is
  (a) wrong usage on our side or (b) an engine bug — the project has a
  `/triage` skill for the latter.

---

## 11. Quick mental model

```
packageName   → root Java package (and src/main/java/<…> path)
classes[]     → real .java files (concrete or generic templates)
interfaces[]  → real .java files
enums[]       → real .java files
arrayTypes / dictionaryTypes / concreteGeneric* → typegraph only, no files
customFiles[] → escape hatch for free-form .java (rare in Java)

properties[]      → "what fields exist"  (no logic)
constructorParameters[] → "ctor signature + auto-fields" (don't duplicate in properties)
customCode[]      → "everything with logic" (one block = one member)
templateRefs      → "wire $placeholders to typeIdentifiers" (internal types)
customImports     → "external libs" (never JDK / validation / jackson)
decorators        → annotations
```

If in doubt: **one call**, **typeIdentifiers everywhere**, **templateRefs
for every `$placeholder`**, **customImports only for genuine third-party
libraries**.
