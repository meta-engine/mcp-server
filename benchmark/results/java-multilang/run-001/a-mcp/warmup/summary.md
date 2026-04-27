# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is self-contained. The next session will use it without re-reading docs.

---

## 1. What MetaEngine is

MetaEngine is a **semantic code generation MCP server**. You describe types, relationships, and methods as structured JSON; MetaEngine emits compilable, fully-imported source files. Cross-references (one type referencing another), import resolution, and language idioms are handled automatically. A single well-formed `generate_code` call replaces dozens of manual file writes.

Supported languages: TypeScript, C#, Python, Go, **Java**, Kotlin, Groovy, Scala, Swift, PHP, Rust.

---

## 2. Tools exposed

### `mcp__metaengine__metaengine_initialize`
- Returns the canonical AI guide (markdown). Optional `language` param (`"java"`, etc.) returns language-flavored guidance.
- Already called during warmup. **Do not** call again unless you want to refresh patterns.

### `mcp__metaengine__generate_code`
- The single tool you use to actually emit code.
- Required: `language`. Defaults: `outputPath = "."`, `dryRun = false`, `skipExisting = true`, `initialize = false`.

### Companion tools (only if needed)
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, `load_spec_from_file` — spec-driven generators. Not needed for hand-rolled DDD generation.

---

## 3. `generate_code` — full input schema

Top-level fields (all arrays optional unless noted):

| Field                       | Type                 | Purpose                                                                                       |
|-----------------------------|----------------------|-----------------------------------------------------------------------------------------------|
| `language`                  | string (REQUIRED)    | `"java"` for our purposes                                                                     |
| `packageName`               | string               | Java default: `com.metaengine.generated`. Sets the `package` declaration of every file.      |
| `outputPath`                | string               | Directory root where files are written. Default `"."`.                                        |
| `dryRun`                    | bool                 | If true, returns generated content without writing. Default `false`.                          |
| `skipExisting`              | bool                 | If true, skips files that already exist. Default `true`. Useful for stub patterns.            |
| `initialize`                | bool                 | If true, properties get default-value initializers in languages that support that.            |
| `classes`                   | Class[]              | Regular and generic class templates. Generates one file per class.                            |
| `interfaces`                | Interface[]          | Same shape as classes; generates an `interface`.                                              |
| `enums`                     | Enum[]               | Generates enum types.                                                                         |
| `customFiles`               | CustomFile[]         | Files without a class/interface wrapper (utility files, type aliases, package-level helpers). |
| `arrayTypes`                | ArrayType[]          | Virtual array references — **no files generated**. Reference via `typeIdentifier`.            |
| `dictionaryTypes`           | DictionaryType[]     | Virtual map references — **no files generated**.                                              |
| `concreteGenericClasses`    | ConcreteGeneric[]    | Inline type references like `Repository<User>` — **no files generated**.                      |
| `concreteGenericInterfaces` | ConcreteGeneric[]    | Same, for generic interfaces.                                                                 |

### Class / Interface object

| Field                        | Type                    | Notes                                                                                              |
|------------------------------|-------------------------|----------------------------------------------------------------------------------------------------|
| `name`                       | string                  | Type name (PascalCase for Java).                                                                   |
| `typeIdentifier`             | string                  | Unique key used to reference this type from other types.                                           |
| `path`                       | string                  | Sub-directory under `outputPath`, e.g. `"models"` or `"services/auth"`.                            |
| `fileName`                   | string                  | Override file name (no extension).                                                                 |
| `comment`                    | string                  | Doc comment on the type.                                                                           |
| `isAbstract`                 | bool                    | Class only.                                                                                        |
| `baseClassTypeIdentifier`    | string                  | Reference to parent class to extend.                                                               |
| `interfaceTypeIdentifiers`   | string[]                | Interfaces to implement.                                                                           |
| `genericArguments`           | GenericArg[]            | Makes the class/interface generic (e.g. `Repository<T>`).                                          |
| `constructorParameters`      | Param[]                 | **Auto-creates properties in Java.** Don't duplicate in `properties`.                              |
| `properties`                 | Property[]              | Field declarations. Type-only — no initialization or logic.                                        |
| `customCode`                 | CustomCode[]            | Methods, initialized fields, anything with logic. **One item = exactly one member.**               |
| `customImports`              | CustomImport[]          | External (non-stdlib) imports.                                                                     |
| `decorators`                 | CustomCode[]            | Annotations (Java: `@Service`, `@Entity`, etc.).                                                   |

### Property object

```jsonc
{
  "name": "email",
  "primitiveType": "String|Number|Boolean|Date|Any",   // OR
  "typeIdentifier": "user",                            // reference to another type in this batch OR
  "type": "List<$user>",                               // raw type expression with placeholders
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}],
  "isOptional": true,
  "isInitializer": true,         // emit default-value init
  "comment": "Doc comment",
  "decorators": [...]            // e.g. [{"code": "@NotNull"}]
}
```

### CustomCode object

```jsonc
{
  "code": "public $user findByEmail(String email) { throw new UnsupportedOperationException(); }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

- `templateRefs` is the ONLY way to reference an internal type from inside `customCode` while still getting an automatic import. Raw class names work only when in the same package.
- One `customCode` entry = one method or one initialized field. Engine inserts blank lines between entries automatically.

### CustomImport object

```jsonc
{ "path": "org.springframework.stereotype", "types": ["Service"] }
```

For Java this becomes `import org.springframework.stereotype.Service;`. Use only for **external** libraries — never for `java.util.*`, `java.time.*`, etc.

### Enum object

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "members": [{"name": "PENDING", "value": 0}, {"name": "SHIPPED", "value": 2}],
  "comment": "Lifecycle of an order"
}
```

### ArrayType / DictionaryType (virtual)

```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
  {"typeIdentifier": "string-list", "elementPrimitiveType": "String"}
],
"dictionaryTypes": [
  {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-by-id", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
]
```

Reference via `"typeIdentifier": "user-list"` in any property. Java emits these as `List<...>` / `Map<...,...>` from `java.util.*` (auto-imported).

### Concrete generic (virtual)

```jsonc
"concreteGenericClasses": [{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}]
```

Used as e.g. `baseClassTypeIdentifier: "user-repo-concrete"` so the engine emits `extends Repository<User>` with full imports.

### CustomFile object (no class wrapper)

```jsonc
{
  "name": "Constants",
  "path": "shared",
  "identifier": "shared-constants",
  "customCode": [
    {"code": "public final class Constants { public static final String API_BASE = \"/api\"; private Constants() {} }"}
  ],
  "customImports": [...]
}
```

Useful in Java for: package-info files, utility classes you want to author by hand, marker interfaces, etc. The optional `identifier` lets other files reference this file by `customImports`.

---

## 4. Java-specific behavior

### Package & path layout
- `packageName` sets the `package x.y.z;` line at the top of every file. Default `com.metaengine.generated`.
- `outputPath` is the root folder. Engine writes Java files under that root using `path` (and the `packageName` is **independent** of folder layout — it does not auto-create `src/main/java/...` from the package). If you want canonical Maven layout, point `outputPath` at `src/main/java/com/metaengine/generated/` or use `path` to nest folders.
- `path` on a class/interface adds a sub-folder under `outputPath`. The engine does **not** rewrite `packageName` per sub-folder; if you nest with `path`, set the appropriate `packageName` on that call (or split into multiple calls only when types are not cross-referenced).
- Practical recipe for a single domain in Java:
  - Put everything in **one** call.
  - `packageName: "com.metaengine.generated"` (or whatever the spec wants).
  - `outputPath: "<repo>/src/main/java/com/metaengine/generated"`.
  - Use `path` only for `models/`, `services/`, etc. sub-packages — but if you do, you need different `packageName` values, which means splitting calls. Easier: keep everything flat.

### Type mapping (Java)
| Spec primitive | Java emitted type           |
|----------------|-----------------------------|
| `String`       | `String`                    |
| `Number`       | `int`  (NOT `double`/`long`) — use `"type": "long"` / `"type": "double"` / `"type": "BigDecimal"` for explicit numerics |
| `Boolean`      | `boolean`                   |
| `Date`         | `java.time.Instant` (auto-imported via `java.time.*`) — use `"type": "LocalDate"` / `"LocalDateTime"` etc. when you need a different temporal |
| `Any`          | `Object`                    |

For collections: prefer `arrayTypes`/`dictionaryTypes` for `List<T>` / `Map<K,V>`; or use `"type": "Set<$user>"` etc. with templateRefs.

### Auto-imports (NEVER add to `customImports`)
For Java, MetaEngine auto-imports:
- `java.util.*` (`List`, `Map`, `Set`, `Optional`, `UUID`, `Collections`, ...)
- `java.time.*` (`Instant`, `LocalDate`, `LocalDateTime`, `Duration`, ...)
- `java.util.stream.*`
- `java.math.*` (`BigDecimal`, `BigInteger`)
- `jakarta.validation.*` (e.g. `@NotNull`, `@NotBlank` — use as decorators)
- Jackson (`com.fasterxml.jackson.*`)

### Class vs Record emission
- The engine emits **classes** by default. There is **no `isRecord` flag** in the schema.
- If you want a Java record, write the class wrapper as a `customFile` and produce the `record Foo(...) { }` manually inside `customCode`. For DDD value objects, classes with private final fields + constructor are typically what the engine produces, which is fine for Java 8+ targets.
- For abstract classes, set `isAbstract: true`.

### Constructor parameters
- In Java, items in `constructorParameters` automatically become **`private final` fields with a constructor that assigns them**. Do NOT also list them in `properties` — that produces "Sequence contains more than one matching element".
- Only put **additional, non-constructor** fields in `properties`.

### Methods (`customCode`) for stubs
For DDD method stubs, write one `customCode` entry per method body. The engine concatenates them with blank lines. Example:

```jsonc
"customCode": [
  {
    "code": "public $user findById(String id) { throw new UnsupportedOperationException(\"TODO\"); }",
    "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
  },
  {
    "code": "public java.util.List<$user> findAll() { throw new UnsupportedOperationException(\"TODO\"); }",
    "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
  }
]
```

**Tips for Java method stubs:**
- Visibility (`public`, `protected`, `private`) and return type must be in the `code` — engine does not infer.
- Stub bodies idiomatically use `throw new UnsupportedOperationException("Not yet implemented");`.
- Generic method signatures (`<T>`) go inline in the `code`.
- For interface method signatures (no body) inside an `interface` definition, write `Type name(args);` (semicolon, no body) as one `customCode` per method.
- Annotations on methods go inside the `code` string itself (e.g. `@Override\npublic void close() { ... }`), since `decorators` apply to the **type**, not individual methods.

### Property decorators / annotations
For Bean Validation / Jackson on fields, use the `decorators` array on the property:

```jsonc
{
  "name": "email",
  "primitiveType": "String",
  "decorators": [{"code": "@NotBlank"}, {"code": "@Email"}]
}
```

`jakarta.validation.constraints.*` and Jackson are auto-imported, so no `customImports` needed.

### Interface implementation
- `interfaceTypeIdentifiers: ["my-iface"]` → emits `implements MyIface`.
- For interfaces themselves: declare method signatures in `customCode` (semicolon-terminated, no body). Do NOT use function-typed properties.
- `baseClassTypeIdentifier` → emits `extends Parent`.

### Generics
```jsonc
"genericArguments": [{
  "name": "T",
  "constraintTypeIdentifier": "base-entity",   // T extends BaseEntity
  "propertyName": "items",                     // adds property "items" of type T (or T[])
  "isArrayProperty": true                      // makes it List<T>
}]
```
Java emits: `public class Repository<T extends BaseEntity> { protected List<T> items; ... }`.

---

## 5. Critical rules — all of them

1. **ONE call with the full spec.** `typeIdentifier` references resolve only within the current batch. Splitting per-domain or per-aggregate breaks cross-imports and the typegraph silently. Bundle every related class, interface, enum, arrayType, dictionaryType, and concreteGeneric into a single `generate_code` invocation.

2. **Properties = type declarations, customCode = everything with logic.** A property has a name, a type, and (optionally) decorators/comments. Any field that needs an initializer with logic, or any method, goes in `customCode`. Never put method signatures (with bodies) in properties; never put bare uninitialized fields in customCode.

3. **One `customCode` block = one member.** The engine inserts blank lines between blocks. Do not pack multiple methods into a single `code` string.

4. **`templateRefs` for internal type references in customCode.** `"$placeholder"` placeholders trigger import resolution. If you write the type's plain name as a raw string, the engine cannot generate a cross-package import.

5. **`templateRefs` only for internal types.** External library types go in `customImports`. Don't mix.

6. **Never auto-add framework imports.** For Java: don't put `java.util.*`, `java.time.*`, `java.math.*`, `java.util.stream.*`, `jakarta.validation.*`, or Jackson into `customImports`. They are auto-imported.

7. **Constructor parameters auto-create properties (Java).** Never list the same field both in `constructorParameters` and `properties`. Only add **additional** non-constructor fields to `properties`.

8. **Virtual types don't produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` only create reusable references. They appear nowhere in the output until referenced via `typeIdentifier` from a real class/interface.

9. **Verify every `typeIdentifier`.** A reference to an undefined `typeIdentifier` is silently dropped — the property disappears from the generated file.

10. **Avoid reserved words as field/property names** (Java: `class`, `package`, `interface`, `int`, `default`, `enum`, `synchronized`, etc.). Pick safe alternatives.

11. **`Number` → `int` in Java.** For `long`, `double`, or `BigDecimal`, use `"type": "long"` / `"type": "double"` / `"type": "BigDecimal"` (with no templateRefs, since `BigDecimal` is auto-imported).

12. **`Date` → `java.time.Instant` in Java.** For other temporals, use raw `"type": "LocalDate"` / `"LocalDateTime"` / `"OffsetDateTime"` etc.

13. **`packageName` is independent of `path`.** Don't rely on `path: "models/foo"` to put files in package `...models.foo`; the engine writes the same `package` line everywhere. If you want true sub-packages, do separate calls per package — but **only** when those packages have no cross-references.

---

## 6. Output structure for Java

For a call like:
```jsonc
{
  "language": "java",
  "packageName": "com.metaengine.generated",
  "outputPath": "/repo/src/main/java/com/metaengine/generated",
  "classes": [
    {"name": "User", "typeIdentifier": "user",
      "properties": [{"name": "id", "primitiveType": "String"}, {"name": "email", "primitiveType": "String"}]},
    {"name": "UserRepository", "typeIdentifier": "user-repo",
      "customCode": [{
        "code": "public $user findById(String id) { throw new UnsupportedOperationException(); }",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
      }]}
  ]
}
```

You get:

```
/repo/src/main/java/com/metaengine/generated/
├── User.java
└── UserRepository.java
```

`User.java`:
```java
package com.metaengine.generated;

public class User {
    private String id;
    private String email;
    // standard getters/setters generated automatically
}
```

`UserRepository.java`:
```java
package com.metaengine.generated;

public class UserRepository {

    public User findById(String id) {
        throw new UnsupportedOperationException();
    }
}
```

(Same package → no explicit `import`, but the engine still tracks the dependency for cross-package cases.)

---

## 7. Java DDD generation playbook

Recommended approach for the next session:

1. **Plan once, generate once.** Read the entire DDD spec first. Build a single mental list of: aggregates, entities, value objects, enums, repositories, application services, domain services. Assign each a `typeIdentifier`.
2. **Use the canonical Maven path.** `outputPath: "<repoRoot>/src/main/java/<package-as-folders>"` and `packageName: "<dotted.package.name>"`. Keep `packageName` consistent across the whole call.
3. **Model entities/value objects as classes.**
   - Use `constructorParameters` for required immutable fields → auto-emits `private final` + constructor.
   - Use `properties` only for additional mutable fields (rare in DDD; usually none).
   - Add `decorators` like `@NotBlank`, `@NotNull` directly on properties.
   - Skip `isRecord` — it doesn't exist; classes are the path.
4. **Model enums via the `enums` array** with explicit numeric `value` for each member.
5. **Use `arrayTypes` / `dictionaryTypes` for collection-typed fields** (`List<OrderLine>`, `Map<String, Money>`, etc.). Define the virtual type once and reference its `typeIdentifier`.
6. **Repositories and services as classes/interfaces** with method stubs in `customCode`:
   - Interfaces (`interfaces[]`): one `customCode` per method signature, semicolon-terminated, no body.
   - Concrete classes (`classes[]`) implementing them: `interfaceTypeIdentifiers: [...]`, with full method bodies in `customCode` (typically `throw new UnsupportedOperationException("Not yet implemented")`).
7. **Cross-references everywhere**: every time a method or property mentions another generated type, use `templateRefs` with `$placeholder` syntax — even for same-package types it's safer (engine still resolves it correctly).
8. **Don't add `customImports` for `java.util.*`, `java.time.*`, `java.math.*`, or Jakarta validation** — auto-imported.
9. **Annotations:**
   - Type-level (`@Service`, `@Entity`, `@Repository`): use the `decorators` array on the class, with `customImports` for the framework if it's not Jackson/Jakarta.
   - Field-level (`@NotNull`, `@JsonProperty`): `decorators` on the property.
   - Method-level: write the annotation inline in the method's `code` string (since there's no per-method decorator field).
10. **One call.** Verify the JSON parses, every `typeIdentifier` referenced exists, and there are no duplicates between `constructorParameters` and `properties`. Then submit.

---

## 8. Common Java pitfalls — checklist

- [ ] Did you add `java.util.*` or `java.time.*` to `customImports`? Remove it.
- [ ] Did you put `Number` for a value that's actually a long/decimal? Switch to `"type": "long"` / `"BigDecimal"`.
- [ ] Did you put `Date` for what should be a `LocalDate`? Switch to `"type": "LocalDate"`.
- [ ] Did you duplicate a constructor param in `properties`? Remove the duplicate.
- [ ] Did you reference a `typeIdentifier` that you never defined? Either add the type or fix the reference.
- [ ] Did you split related types across multiple calls? Merge them.
- [ ] Did you write a method body inside a `properties` entry? Move it to `customCode`.
- [ ] Did you write multiple methods in one `customCode.code`? Split into separate entries.
- [ ] Did you reference an internal type by raw class name in `customCode` and forget `templateRefs`? Add `templateRefs`.
- [ ] Did you use a Java reserved word (`class`, `default`, etc.) as a field name? Rename.
- [ ] Did you set `path` expecting the package to change? It won't — `packageName` is global per call.

---

## 9. Quick reference card

```jsonc
{
  "language": "java",
  "packageName": "com.example.domain",
  "outputPath": "/abs/path/src/main/java/com/example/domain",
  "dryRun": false,
  "skipExisting": true,
  "initialize": false,

  "enums": [
    {"name": "OrderStatus", "typeIdentifier": "order-status",
     "members": [{"name": "PENDING", "value": 0}, {"name": "SHIPPED", "value": 1}]}
  ],

  "arrayTypes": [
    {"typeIdentifier": "order-line-list", "elementTypeIdentifier": "order-line"}
  ],

  "classes": [
    {"name": "Money", "typeIdentifier": "money",
     "constructorParameters": [
       {"name": "amount", "type": "BigDecimal"},
       {"name": "currency", "primitiveType": "String"}
     ]},
    {"name": "OrderLine", "typeIdentifier": "order-line",
     "constructorParameters": [
       {"name": "sku", "primitiveType": "String"},
       {"name": "quantity", "primitiveType": "Number"},
       {"name": "price", "typeIdentifier": "money"}
     ]},
    {"name": "Order", "typeIdentifier": "order",
     "constructorParameters": [
       {"name": "id", "primitiveType": "String"},
       {"name": "lines", "typeIdentifier": "order-line-list"},
       {"name": "status", "typeIdentifier": "order-status"}
     ],
     "customCode": [
       {"code": "public void ship() { throw new UnsupportedOperationException(); }"}
     ]}
  ],

  "interfaces": [
    {"name": "OrderRepository", "typeIdentifier": "order-repo",
     "customCode": [
       {"code": "$order findById(String id);",
        "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]},
       {"code": "void save($order order);",
        "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]}
     ]}
  ]
}
```

That single call yields `OrderStatus.java`, `Money.java`, `OrderLine.java`, `Order.java`, `OrderRepository.java` — all in `com.example.domain`, with correct cross-references and zero `customImports` needed.
