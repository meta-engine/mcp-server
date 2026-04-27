# MetaEngine MCP — Knowledge Brief (Java focus)

This brief is the only knowledge the next session will have about the MetaEngine MCP. It must be read end-to-end before producing any `generate_code` call. Everything below is distilled from the canonical `metaengine://guide/ai-assistant` and `metaengine://guide/examples` resources, plus the live JSON Schema returned by `mcp__metaengine__metaengine_initialize(language: "java")`.

---

## 1. What MetaEngine is

MetaEngine is a **semantic** code generator (not a template engine). You describe types, their members, relationships, and methods as JSON. MetaEngine resolves cross-references between types in the batch, manages all imports, picks language-correct collection/optional/numeric idioms, names files using each language's convention, and writes compilable source files to disk.

For Java specifically it produces `.java` files with `package` declarations, automatic `import` statements (for both stdlib and intra-batch types), and PascalCase class/interface/enum names that match the file name.

---

## 2. Tools exposed by the server

The MetaEngine MCP server exposes exactly two tools:

### 2.1 `mcp__metaengine__metaengine_initialize`
- Purpose: Returns the canonical AI-assistant guide (the same content available at `metaengine://guide/ai-assistant`). Optional argument `language` (`typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php`) — when supplied, the server may layer in language-specific patterns. **Pass `language: "java"` for this run.**
- Idempotent and side-effect free. Call once at session start; do not call repeatedly.

### 2.2 `mcp__metaengine__generate_code`
- The actual generator. Single call → many files.
- **Required parameter:** `language` (must be `"java"` for this run).
- Returns: list of generated file paths (or, when `dryRun: true`, the file contents inline).

There are also (per the server manifest) `generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, and `load_spec_from_file` tools — these are spec-conversion utilities and are **not** what we use for arbitrary code generation. Stick to `generate_code`.

There are two MCP **resources** the server exposes (do not call `generate_code` to read these — use `ReadMcpResourceTool`):
- `metaengine://guide/ai-assistant` — the master guide (already inlined here).
- `metaengine://guide/examples` — six full input/output examples (also distilled below).

---

## 3. Top-level input schema for `generate_code`

All arrays are optional except where noted. Order of keys does not matter; MetaEngine resolves the typegraph after the whole payload is parsed.

| Field | Type | Notes |
|---|---|---|
| `language` | enum | **REQUIRED.** `"java"` for this run. |
| `packageName` | string | Java/Kotlin/Groovy default = `com.metaengine.generated`. Becomes the `package` declaration AND determines the output directory layout (dots → slashes). Always set it explicitly. |
| `outputPath` | string | Root directory on disk. Default `"."`. The package path is appended underneath. |
| `dryRun` | bool | Default `false`. When `true`, files are not written; contents are returned in the response. Useful for sanity-checking a large spec before committing. |
| `skipExisting` | bool | Default `true`. When `true`, an already-existing file is left untouched. When `false`, files are overwritten. **For greenfield generation runs, set `skipExisting: false` so a re-run truly regenerates everything.** |
| `initialize` | bool | Default `false`. When `true`, primitive properties get default initializers (e.g. `String name = "";`). Generally leave `false` for Java unless you specifically want zero-value initializers. |
| `classes[]` | array | Class definitions. Generates one file per entry. |
| `interfaces[]` | array | Interface definitions. Generates one file per entry. |
| `enums[]` | array | Enum definitions. Generates one file per entry. |
| `arrayTypes[]` | array | **Virtual** — declares a reusable list/array type alias. Generates NO files. |
| `dictionaryTypes[]` | array | **Virtual** — declares a reusable map type alias. Generates NO files. |
| `concreteGenericClasses[]` | array | **Virtual** — declares a reusable bound generic class type (`Repository<User>`). Generates NO files. |
| `concreteGenericInterfaces[]` | array | **Virtual** — same idea for interfaces. Generates NO files. |
| `customFiles[]` | array | Free-form files (utility/helper/aliases). Generates files WITHOUT a class wrapper. |

### 3.1 Shape of a `classes[]` entry

```jsonc
{
  "name": "User",                       // PascalCase class name → filename User.java
  "typeIdentifier": "user",             // Stable id used by other entries to refer to this class
  "path": "domain/user",                // (Optional) sub-path relative to packageName / outputPath
  "fileName": "User",                   // (Optional) override file basename (no extension)
  "comment": "Aggregate root for user", // (Optional) JavaDoc on the class
  "isAbstract": false,
  "baseClassTypeIdentifier": "base-entity",
  "interfaceTypeIdentifiers": ["serializable-thing"],
  "genericArguments": [ /* see §4.5 */ ],
  "constructorParameters": [
    { "name": "id", "primitiveType": "String" }
    // In Java, these AUTO-BECOME final fields + a constructor that assigns them.
    // Do NOT also list them in properties[].
  ],
  "properties": [
    { "name": "createdAt", "primitiveType": "Date", "comment": "When created", "isOptional": false }
  ],
  "decorators": [
    { "code": "@Entity" },
    { "code": "@Table(name = \"users\")" }
  ],
  "customCode": [
    { "code": "public String displayName() { return id; }" },
    {
      "code": "public $repo asRepo() { throw new UnsupportedOperationException(\"TODO\"); }",
      "templateRefs": [ { "placeholder": "$repo", "typeIdentifier": "user-repo" } ]
    }
  ],
  "customImports": [
    { "path": "jakarta.persistence", "types": ["Entity", "Table"] }
  ]
}
```

### 3.2 Shape of a `properties[]` entry

```jsonc
{
  "name": "amount",
  "primitiveType": "Number",       // one of String | Number | Boolean | Date | Any
  // OR
  "typeIdentifier": "address",     // reference to another type in the same batch
  // OR
  "type": "Map<String, $resp>",    // free-form type expression (use templateRefs for $)
  "templateRefs": [ { "placeholder": "$resp", "typeIdentifier": "api-response" } ],
  "isOptional": true,              // Java: wraps in java.util.Optional<...> (or makes nullable; verify)
  "isInitializer": true,           // Add a default initializer (engine picks the zero/empty value)
  "comment": "Total in cents",
  "decorators": [ { "code": "@NotNull" } ]
}
```

**Three mutually exclusive ways to express a type** on a property: `primitiveType`, `typeIdentifier`, or `type` (with optional `templateRefs`). Always pick exactly one.

### 3.3 Shape of a `customCode[]` entry

```jsonc
{
  "code": "public List<$user> findActive() { return List.of(); }",
  "templateRefs": [ { "placeholder": "$user", "typeIdentifier": "user" } ]
}
```

**One `customCode` entry == exactly one member.** MetaEngine inserts blank lines between entries automatically. Methods, constructors, initialized fields, static blocks — all go here. Type-only declarations (no body, no initializer) belong in `properties[]` instead.

### 3.4 Shape of a `customImports[]` entry

```jsonc
{ "path": "com.fasterxml.jackson.annotation", "types": ["JsonProperty", "JsonIgnore"] }
```

Used for **external libraries only**. Never list intra-batch types here (use `typeIdentifier`/`templateRefs` instead). Never list framework auto-imports (see §5.4).

### 3.5 Shape of `decorators[]` (a.k.a. annotations in Java)

```jsonc
{ "code": "@RestController" }
{ "code": "@RequestMapping(\"/users\")" }
{
  "code": "@Autowired private $repo repo;",                        // unusual but legal
  "templateRefs": [ { "placeholder": "$repo", "typeIdentifier": "user-repo" } ]
}
```

In Java, annotations live on classes, methods, and fields. Class-level annotations go in the class entry's `decorators[]`; field-level annotations go in the property's `decorators[]`; method-level annotations need to be inlined inside the `customCode` `code` string just before the method signature.

### 3.6 Shape of an `enums[]` entry

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "comment": "Lifecycle state of an order",
  "fileName": "OrderStatus",
  "path": "domain/order",
  "members": [
    { "name": "PENDING",  "value": 0 },
    { "name": "SHIPPED",  "value": 1 },
    { "name": "DELIVERED","value": 2 }
  ]
}
```

Enum member names are emitted as written. Use `SCREAMING_SNAKE_CASE` for idiomatic Java. The `value` is numeric; whether MetaEngine wires it as a backing int/ordinal in Java is engine-internal — do not depend on it for serialization without verifying.

### 3.7 Shape of an `interfaces[]` entry

Identical schema to `classes[]` but generates a Java `interface`. For interface methods that a class will implement, declare the signatures in `customCode` (without bodies, terminated by `;`), e.g.:

```jsonc
"customCode": [
  { "code": "$user findById(String id);",
    "templateRefs": [ { "placeholder": "$user", "typeIdentifier": "user" } ] }
]
```

Do NOT model methods as function-typed properties — implementing classes will then duplicate them as fields.

### 3.8 Virtual types

```jsonc
"arrayTypes": [
  { "typeIdentifier": "user-list", "elementTypeIdentifier": "user" },          // → List<User>
  { "typeIdentifier": "tag-list",  "elementPrimitiveType": "String" }          // → List<String>
],
"dictionaryTypes": [
  { "typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number" }, // → Map<String,Integer>
  { "typeIdentifier": "user-by-id",  "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }   // → Map<String,User>
],
"concreteGenericClasses": [
  { "identifier": "user-repo-bound",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [ { "typeIdentifier": "user" } ] }
],
"concreteGenericInterfaces": [ /* same shape as above */ ]
```

These are referred to from properties / `baseClassTypeIdentifier` / `interfaceTypeIdentifiers` / `customCode` `templateRefs`. They never produce a file by themselves.

### 3.9 Shape of `customFiles[]`

```jsonc
{
  "name": "Constants",         // file basename
  "fileName": "Constants",     // optional override
  "path": "shared",            // sub-path under packageName
  "identifier": "shared-consts",
  "customCode": [
    { "code": "public final class Constants { public static final String API = \"/api/v1\"; private Constants(){} }" }
  ],
  "customImports": [ { "path": "java.util", "types": [] } ]   // (rarely needed; auto-imported)
}
```

`customFiles` is the escape hatch for content that does not fit the `class`/`interface`/`enum` mold (mixed top-level declarations, package-private helpers, a `package-info.java`, etc.). The `identifier` lets other entries import it via `customImports: [{ "path": "shared-consts" }]`.

---

## 4. Java-specific generation behavior

### 4.1 `packageName` and file paths

- `packageName` becomes the Java `package` declaration verbatim.
- It also becomes the output directory: dots → slashes, appended under `outputPath`.
- A `path` on an individual class/interface/enum is appended **after** the package directory and **becomes part of the package** (i.e. `path: "domain/user"` under package `com.example` produces `com/example/domain/user/User.java` with `package com.example.domain.user;`).
- Default if you omit `packageName`: `com.metaengine.generated`. **Always set it explicitly** to something matching the spec's domain (e.g. `com.metaengine.demo.<bounded-context>`), otherwise files land in a generic package.
- Conventional Maven/Gradle layout (`src/main/java/...`) is **not** automatically inserted — set `outputPath: "src/main/java"` if you want it, otherwise files land at `<outputPath>/<package-as-path>/<path>/Foo.java`.

### 4.2 Filenames

- Class/interface/enum file basename = the `name` field, used as-is. So a `class` named `User` → `User.java`. Java requires this match, and MetaEngine respects it.
- `fileName` overrides the basename (no extension). Rarely needed in Java; useful only if you want a name that differs from the type name (which makes the file uncompilable as a public class — use sparingly).

### 4.3 Primitive type mapping (Java)

Documented mapping from the table is partial; verified mappings:

| `primitiveType` | Likely Java type (verify in dryRun) |
|---|---|
| `String` | `String` |
| `Boolean` | `boolean` (or `Boolean` when `isOptional`) |
| `Number` | **Watch out** — in C# this maps to `int`, not `double`. Java very likely follows the same convention: `Number` → `int` / `Integer`. If you need a non-integer numeric, use the explicit `type` form: `"type": "double"`, `"type": "java.math.BigDecimal"`, `"type": "long"`, etc. **Do not assume `Number` gives you a decimal.** |
| `Date` | Maps via the `java.time.*` auto-import set, so most likely `java.time.LocalDateTime` or `java.time.Instant`. Verify with a one-class `dryRun` if it matters; otherwise prefer the explicit `type` form, e.g. `"type": "java.time.Instant"`, when you need certainty. |
| `Any` | Likely `Object`. |

**Rule of thumb for Java numeric/temporal precision:** when a DDD spec calls for `BigDecimal`, `LocalDate`, `OffsetDateTime`, `UUID`, `long`, or `double` — use the explicit `"type"` form. Reserve `primitiveType` for cases where the engine's default is fine (typically `String` and `Boolean`).

### 4.4 Class vs record emission

The schema does **not** expose a "record" toggle. MetaEngine emits Java **classes** by default. There is no documented `isRecord` flag. If a Java record is required:

- Best path: emit a regular class (with `constructorParameters` so fields + constructor are auto-generated) and accept the class form.
- If a record is strictly required, drop the class entry and emit the record source manually via `customFiles[]`, e.g.:
  ```jsonc
  {
    "name": "Money",
    "path": "domain/shared",
    "customCode": [
      { "code": "public record Money(java.math.BigDecimal amount, String currency) { }" }
    ]
  }
  ```
  This loses cross-reference auto-imports — you must declare external types fully qualified or via `customImports`.

Default: prefer the regular class form; only reach for `customFiles` records when the spec mandates them.

### 4.5 Generics

```jsonc
"genericArguments": [
  {
    "name": "T",                                // generic parameter name
    "constraintTypeIdentifier": "base-entity",  // → "T extends BaseEntity"
    "propertyName": "items",                    // creates a field of type T (or T[])
    "isArrayProperty": true                     // makes it List<T> instead of T
  }
]
```

For a `Repository<T extends BaseEntity>` with a `List<T> items` field plus `findById(String id): T`, you'd combine `genericArguments` (for `T extends BaseEntity` + the `items` field) with `customCode` for the methods, using `T` as a raw token in the code strings (no templateRef needed because `T` is a generic parameter, not an internal type).

To bind a generic to a concrete type from elsewhere in the batch (e.g. `Repository<User>` as a base class), use `concreteGenericClasses`:

```jsonc
"concreteGenericClasses": [{
  "identifier": "user-repo-bound",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [ { "typeIdentifier": "user" } ]
}],
"classes": [{
  "name": "UserRepository",
  "typeIdentifier": "user-repo",
  "baseClassTypeIdentifier": "user-repo-bound"   // → extends Repository<User>
}]
```

### 4.6 Constructor parameters auto-create properties (Java is in the list)

- `constructorParameters[]` on a class entry generates BOTH the constructor and the corresponding fields automatically.
- **Do not also list those names in `properties[]`** — you'll get a "Sequence contains more than one matching element" error.
- Additional fields that should NOT be constructor parameters go in `properties[]`.
- If a class has **no** `constructorParameters`, MetaEngine still emits a Java class but you may need to add a no-arg/parameterized constructor yourself via `customCode` if your spec requires one.

### 4.7 `customCode` interaction with Java method stubs

This is the primary mechanism for emitting method bodies in Java. Patterns:

```jsonc
// Stub method that throws — the safe DDD/spec convention
{ "code": "public $user create($cmd cmd) { throw new UnsupportedOperationException(\"TODO: implement\"); }",
  "templateRefs": [
    { "placeholder": "$user", "typeIdentifier": "user" },
    { "placeholder": "$cmd",  "typeIdentifier": "create-user-command" }
  ]
}

// Method with annotations inline (annotations cannot live in a separate decorator entry for methods)
{ "code": "@Override\npublic String toString() { return id + \":\" + name; }" }

// Initialized field (NOT a property — has logic on the right-hand side)
{ "code": "private final java.util.UUID instanceId = java.util.UUID.randomUUID();" }

// Static factory
{ "code": "public static $self of(String email) { return new $self(email); }",
  "templateRefs": [ { "placeholder": "$self", "typeIdentifier": "user" } ]
}
```

**Indentation note:** Java is brace-scoped, so unlike Python, you don't have to pre-indent multi-line bodies — the engine wraps them with class-body braces and inserts blank-line separators. For multi-line methods, use `\n` in the `code` string between lines; that's fine.

**Annotation note:** Method-level annotations cannot use a per-method `decorators[]` slot — class/property `decorators[]` only apply to the class itself or to a property. To annotate a method, prepend the annotation lines inside the `code` string, e.g. `"@Override\npublic String toString() { ... }"`.

### 4.8 `isOptional` in Java

- The C# behavior is documented as nullable reference type (`string?`). For Java the natural choices are `java.util.Optional<T>` or simply nullable `T`. The engine likely emits `Optional<T>` (since `java.util.*` is auto-imported) but **verify** before depending on it. If you need a guaranteed shape, use the explicit `type`: `"type": "java.util.Optional<String>"` or `"type": "@Nullable String"` plus a `customImport` for the `@Nullable` annotation.

### 4.9 Auto-imported packages (Java)

Never list these in `customImports[]` — duplicates cause errors:

- `java.util.*` (List, Map, Set, UUID, Optional, ArrayList, HashMap, …)
- `java.time.*` (Instant, LocalDate, LocalDateTime, OffsetDateTime, ZoneId, Duration, …)
- `java.util.stream.*` (Stream, Collectors)
- `java.math.*` (BigDecimal, BigInteger)
- `jakarta.validation.*` (`@NotNull`, `@Size`, `@Email`, `@Valid`, …)
- Jackson (`com.fasterxml.jackson.*`) — `@JsonProperty`, `@JsonIgnore`, `ObjectMapper`, etc.

Do list everything else (`org.springframework.*`, `lombok.*`, `org.slf4j.*`, your own package imports outside the batch, etc.) via `customImports`.

### 4.10 Reserved words

Java reserved words (`class`, `interface`, `enum`, `package`, `import`, `default`, `new`, `delete` is NOT reserved but `default` is, `case`, `switch`, `final`, `static`, `volatile`, `synchronized`, `record`, `yield` (contextual), `var` (contextual)) cannot be used as property/parameter names. Use safe alternatives (`clazz`, `defaultValue`, `kase`, `recordValue`).

---

## 5. The Critical Rules (verbatim, ordered by frequency of failure)

1. **Generate ALL related types in ONE `generate_code` call.** `typeIdentifier` cross-references resolve only within a single batch. If you split a DDD spec by bounded context across multiple calls, imports between contexts will silently break and the typegraph collapses.
2. **`properties[]` = type declarations only. `customCode[]` = everything else.** Never put methods in properties; never put uninitialized type-only declarations in customCode. One customCode entry = one member.
3. **Use `templateRefs` for every intra-batch type reference inside `customCode`, `decorators`, or free-form `type` expressions.** Without a templateRef, the engine cannot generate the cross-package `import`. Pattern: `"$alias"` in the code string + `{ "placeholder": "$alias", "typeIdentifier": "..." }` in `templateRefs`.
4. **Never add framework imports to `customImports`.** See the Java auto-import list in §4.9.
5. **`templateRefs` are ONLY for intra-batch types. External library types ALWAYS go through `customImports`.** Don't mix.
6. **Do not duplicate `constructorParameters` names in `properties[]`** (Java is in the auto-property-creation list along with C#/Go/Groovy).
7. **Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) never produce files.** They exist purely to be referenced.
8. **A `typeIdentifier` that does not exist in the same batch is silently dropped from the property** — the engine does not error. Audit every reference before submitting.
9. **For interfaces that will be implemented by a class, model methods in `customCode` (signature ending in `;`), not as function-typed properties.** Otherwise the implementor duplicates them as fields.
10. **Reserved words as property names will compile-fail.** Pick a safe alternative.

---

## 6. Distilled examples (cross-language patterns; apply the Java mapping rules above)

### Example A — Two interfaces with cross-references (TS shown; Java analog: two `interfaces[]` entries, the second referencing the first by `typeIdentifier`).

### Example B — Class with abstract base + method:

```jsonc
{
  "language": "java",
  "packageName": "com.metaengine.demo.user",
  "classes": [
    { "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [ { "name": "id", "primitiveType": "String" } ] },
    { "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [ { "name": "email", "primitiveType": "String" } ],
      "customCode": [
        { "code": "public String getDisplayName() { return email; }" }
      ] }
  ]
}
```

### Example C — Generic repository + concrete generic + class extending it:

```jsonc
{
  "language": "java",
  "packageName": "com.metaengine.demo",
  "classes": [
    { "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [ { "name": "id", "primitiveType": "String" } ] },

    { "name": "Repository", "typeIdentifier": "repo-generic",
      "genericArguments": [ {
        "name": "T", "constraintTypeIdentifier": "base-entity",
        "propertyName": "items", "isArrayProperty": true
      } ],
      "customCode": [
        { "code": "public void add(T item) { items.add(item); }" },
        { "code": "public java.util.List<T> getAll() { return items; }" }
      ] },

    { "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [ { "name": "email", "primitiveType": "String" } ] },

    { "name": "UserRepository", "typeIdentifier": "user-repo",
      "baseClassTypeIdentifier": "user-repo-bound",
      "customCode": [
        { "code": "public $user findByEmail(String email) { for ($user u : getAll()) { if (u.getEmail().equals(email)) return u; } return null; }",
          "templateRefs": [ { "placeholder": "$user", "typeIdentifier": "user" } ] }
      ] }
  ],
  "concreteGenericClasses": [
    { "identifier": "user-repo-bound", "genericClassIdentifier": "repo-generic",
      "genericArguments": [ { "typeIdentifier": "user" } ] }
  ]
}
```

### Example D — Enum + class that uses it:

```jsonc
{
  "enums": [ {
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [
      { "name": "PENDING",   "value": 0 },
      { "name": "SHIPPED",   "value": 1 },
      { "name": "DELIVERED", "value": 2 }
    ]
  } ],
  "classes": [ {
    "name": "Order", "typeIdentifier": "order",
    "properties": [ { "name": "status", "typeIdentifier": "order-status" } ],
    "customCode": [
      { "code": "public void updateStatus($status s) { this.status = s; }",
        "templateRefs": [ { "placeholder": "$status", "typeIdentifier": "order-status" } ] }
    ]
  } ]
}
```

### Example E — Service with annotations + external library imports (Spring-flavoured):

```jsonc
{
  "language": "java",
  "packageName": "com.metaengine.demo.user",
  "classes": [
    { "name": "UserService", "typeIdentifier": "user-service",
      "decorators": [
        { "code": "@org.springframework.stereotype.Service" }
      ],
      "customImports": [
        { "path": "org.springframework.stereotype", "types": ["Service"] }
      ],
      "constructorParameters": [
        { "name": "repo", "typeIdentifier": "user-repo" }
      ],
      "customCode": [
        { "code": "public $user create(String email) { throw new UnsupportedOperationException(\"TODO\"); }",
          "templateRefs": [ { "placeholder": "$user", "typeIdentifier": "user" } ] }
      ] }
  ]
}
```

Note how the constructor parameter `repo` auto-creates a `private final UserRepository repo` field plus an assigning constructor.

### Example F — Constructor parameters: the WRONG vs RIGHT pattern.

```jsonc
// WRONG — duplicates email between constructorParameters and properties
"constructorParameters": [ { "name": "email", "primitiveType": "String" } ],
"properties":            [ { "name": "email", "primitiveType": "String" }, { "name": "createdAt", "primitiveType": "Date" } ]

// RIGHT — only additional fields in properties
"constructorParameters": [ { "name": "email", "primitiveType": "String" } ],
"properties":            [ { "name": "createdAt", "primitiveType": "Date" } ]
```

---

## 7. Common mistakes to actively avoid

1. **Splitting a DDD spec into per-bounded-context calls.** The typegraph and import resolution only see types within a single batch. → ONE `generate_code` call with EVERY type.
2. **Referencing a non-existent `typeIdentifier`.** It silently drops the property — no error, just a hole.
3. **Method signatures expressed as function-typed properties on interfaces.** Implementing classes will duplicate them as fields.
4. **Internal type names as raw strings inside `customCode`.** No templateRef → no `import` → cross-package compile failure. Always use `$alias` + `templateRefs`.
5. **Listing `java.util.*`, `java.time.*`, jakarta-validation, jackson in `customImports`.** Already auto-imported; will duplicate or error.
6. **Duplicating `constructorParameters` in `properties[]`.** Sequence-contains-more-than-one-element error.
7. **Reserved-word property/parameter names** (`class`, `default`, `package`, etc.).
8. **Assuming `Number` → `double`.** It maps to `int`/`Integer`. For decimals use `"type": "java.math.BigDecimal"` or `"type": "double"`.
9. **Assuming `Date` is a specific Java type.** Verify with a small `dryRun` first or use the explicit `type` form.
10. **Forgetting to set `packageName` and `outputPath`.** You'll get `com.metaengine.generated` written into `./com/metaengine/generated/...` — usually not what a Java project wants.

---

## 8. Recommended workflow for a Java DDD-spec generation run

1. Read the DDD spec end to end. Inventory every entity, value object, aggregate root, domain event, command, repository interface, application service, and enum.
2. Assign each one a stable `typeIdentifier` (kebab-case is the convention used in all examples).
3. Decide the package layout: typically `<base>.domain.<context>`, `<base>.application.<context>`, `<base>.infrastructure.<context>`. Set `packageName` to the base, and use per-class `path` to push individual classes into sub-packages.
4. Build ONE giant payload combining `enums`, `interfaces`, `classes`, `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`, `customFiles` as needed.
5. For repository interfaces, define method signatures as `customCode` ending in `;`. The implementing classes (if generated) reference the interface via `interfaceTypeIdentifiers` and provide method bodies (typically stubs that `throw new UnsupportedOperationException("TODO")`).
6. Use `dryRun: true` on the first attempt for a large spec to surface schema problems before writing files. Then re-run with `dryRun: false` and `skipExisting: false`.
7. Set `outputPath` to the Java source root (e.g. `"src/main/java"`).
8. After generation, do NOT hand-edit cross-cutting things like imports — re-run with the corrected spec instead.

---

## 9. Output structure (Java)

For `language: "java"`, `packageName: "com.example.demo"`, `outputPath: "src/main/java"`, a `class { name: "User", path: "domain/user" }` produces:

```
src/main/java/com/example/demo/domain/user/User.java
```

Containing:

```java
package com.example.demo.domain.user;

import com.example.demo.domain.shared.BaseEntity;     // intra-batch reference, auto-resolved
import java.time.Instant;                              // auto-imported as needed
// ... etc

public class User extends BaseEntity {
    private final String email;
    private Instant createdAt;

    public User(String email) {
        this.email = email;
    }

    // customCode methods, blank-line separated:

    public String getDisplayName() { return email; }
}
```

The generator returns a list of every file path it wrote (or, with `dryRun: true`, the contents).

---

## 10. Quick checklist before submitting a `generate_code` call

- [ ] `language: "java"`
- [ ] `packageName` set explicitly (NOT the default `com.metaengine.generated`)
- [ ] `outputPath` set to the Java source root
- [ ] `skipExisting: false` for a regeneration; `true` if augmenting
- [ ] `dryRun: true` for the first run on a large spec
- [ ] Every `typeIdentifier` referenced somewhere actually exists in the batch
- [ ] No duplicate names between `constructorParameters` and `properties` on the same class
- [ ] Every intra-batch reference inside `customCode` / `decorators` / free-form `type` strings uses `templateRefs`
- [ ] No `java.util.*`/`java.time.*`/jakarta/jackson entries in `customImports`
- [ ] All Java reserved words avoided in property/parameter names
- [ ] `Number` → only used where you actually want `int`/`Integer`; otherwise explicit `"type"` (`"double"`, `"long"`, `"java.math.BigDecimal"`)
- [ ] `Date` → either accepted as engine default or replaced by explicit `"type": "java.time.Instant"` etc. when precision matters
- [ ] Repository/service interfaces use `customCode` for method signatures (ending `;`), not function-typed properties
- [ ] All related types in ONE call

If every box is checked, you can submit. Otherwise, fix before calling — the engine will silently swallow some errors (missing identifiers, missing templateRefs) and that's harder to debug than an upfront audit.
