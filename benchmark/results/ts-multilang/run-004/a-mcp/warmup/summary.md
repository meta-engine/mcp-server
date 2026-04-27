# MetaEngine MCP — Knowledge Brief

MetaEngine is a **semantic code generation system** exposed via MCP. You describe types, relationships, and methods as structured JSON, and MetaEngine produces **compilable, correctly-imported source files**. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

Supported target languages: **TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust**.

---

## Tools exposed (`mcp__metaengine__*`)

### 1. `mcp__metaengine__metaengine_initialize`
Returns the AI-assistant guide (critical rules, patterns, language notes, common mistakes). Optional `language` param (one of: typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php) returns language-specific patterns. Call once at the start of a generation session.

### 2. `mcp__metaengine__generate_code` — **the core tool**
Generates source files for any of the 11 supported languages from a structured JSON spec. See "Input schema" below.

### 3. `mcp__metaengine__load_spec_from_file`
Same functionality as `generate_code`, but reads the spec from a JSON file on disk. Drastically reduces context usage. Params:
- `specFilePath` (required) — absolute or relative path to JSON spec
- `outputPath` — overrides spec
- `skipExisting` — overrides spec
- `dryRun` — overrides spec

The JSON file uses the exact same structure as `generate_code`'s arguments. Use this for large/reusable specs.

### 4. `mcp__metaengine__generate_openapi`
Generates HTTP clients from OpenAPI specs. Frameworks: `angular | react | typescript-fetch | go-nethttp | java-spring | python-fastapi | csharp-httpclient | kotlin-ktor | rust-reqwest | swift-urlsession`. Provide `openApiSpec` (inline YAML/JSON) OR `openApiSpecUrl`. Per-framework option blocks (e.g. `csharpOptions.namespaceName`, `goOptions.{moduleName,packageName}`, `kotlinOptions.packageName`, `rustOptions.crateName`, `javaSpringOptions.packageName`). Cross-cutting: `bearerAuth`, `basicAuth`, `customHeaders`, `errorHandling`, `retries`, `timeout`, `documentation`, `strictValidation`, `outputPath`, `skipExisting`, `dryRun`.

### 5. `mcp__metaengine__generate_graphql`
Generates HTTP clients from a GraphQL SDL schema (`graphQLSchema` required). Same framework set as openapi (with python-fastapi instead of python-httpx). Per-framework option blocks similar to openapi. Extra: `discriminatedUnions`, `documentation`.

### 6. `mcp__metaengine__generate_protobuf`
Generates HTTP clients from `.proto` source (`protoSource` required). Frameworks same as openapi but Python flavor is `python-httpx`. Per-framework option blocks (Go requires `moduleName`+`packageName`, C# requires `namespaceName`, etc.).

### 7. `mcp__metaengine__generate_sql`
Generates typed model classes from SQL DDL (`ddlSource` required). Languages: typescript, csharp, go, python, java, kotlin, groovy, scala, swift, php, rust. Flags: `generateInterfaces`, `generateNavigationProperties`, `generateValidationAnnotations`, `initializeProperties`. Per-language option blocks (e.g. `csharpOptions.namespace`, `goOptions.moduleName`, `pythonOptions.modelStyle` ∈ `dataclass|pydantic|plain`, `phpOptions.{rootNamespace,useStrictTypes}`, etc.).

All generators support `outputPath` (default `.`), `skipExisting` (default `true`), and `dryRun` (default `false`).

---

## `generate_code` — full input schema

Top-level fields:

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php | rust` |
| `outputPath` | string | Output dir, default `.` |
| `packageName` | string | Package/module/namespace. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C#: omit/empty → no namespace declaration (good for GlobalUsings). |
| `initialize` | bool | If true, properties are initialized with default values. |
| `skipExisting` | bool, default `true` | Skip writing files that already exist (stub pattern) |
| `dryRun` | bool, default `false` | Preview mode — files NOT written; contents returned in response. |
| `classes[]` | array | Class definitions. |
| `interfaces[]` | array | Interface definitions. |
| `enums[]` | array | Enum definitions. |
| `customFiles[]` | array | Files without class wrapper (type aliases, barrels, util fns). |
| `arrayTypes[]` | array | Reusable IArrayType refs. **No files generated.** |
| `dictionaryTypes[]` | array | Reusable IDictionaryType refs. **No files generated.** |
| `concreteGenericClasses[]` | array | Concrete generic class refs (e.g. `Repository<User>`). **No files generated.** |
| `concreteGenericInterfaces[]` | array | Concrete generic interface refs (e.g. `IRepository<User>`). **No files generated.** |

### `classes[]` item

| Field | Notes |
|---|---|
| `name` | Class name |
| `typeIdentifier` | Unique id used for cross-references in this batch |
| `path` | Directory path (e.g. `models`, `services/auth`) |
| `fileName` | Custom file name without extension |
| `comment` | Documentation comment |
| `isAbstract` | Boolean |
| `baseClassTypeIdentifier` | typeIdentifier of base class (or of a `concreteGenericClasses[].identifier`) |
| `interfaceTypeIdentifiers[]` | typeIdentifiers of interfaces to implement |
| `genericArguments[]` | If present, makes this a generic class template. Each item: `{ name, constraintTypeIdentifier?, propertyName?, isArrayProperty? }` |
| `constructorParameters[]` | Each: `{ name, type? | primitiveType? | typeIdentifier? }`. **Auto-becomes properties in C#/Java/Go/Groovy/TS** — don't duplicate in `properties[]`. |
| `properties[]` | See properties schema below |
| `customCode[]` | Method bodies, initialized fields. Each: `{ code, templateRefs?[] }`. ONE per member; auto-newlines between blocks. |
| `customImports[]` | External library imports. Each: `{ path, types?[] }` |
| `decorators[]` | Class-level decorators. Each: `{ code, templateRefs?[] }` |

### `properties[]` item

| Field | Notes |
|---|---|
| `name` | Property name |
| `primitiveType` | enum: `String | Number | Boolean | Date | Any` |
| `typeIdentifier` | Reference to another type in this batch |
| `type` | Raw type expression (e.g. `List<$user>`, `decimal`, `() => void`) — for complex/external types |
| `isOptional` | Nullable / `?` |
| `isInitializer` | Add default value initialization |
| `templateRefs[]` | When `type` contains `$placeholder` tokens. Each: `{ placeholder, typeIdentifier }` |
| `decorators[]` | Property decorators (e.g. `@IsEmail()`, `@Required()`). Each: `{ code, templateRefs?[] }` |
| `comment` / `commentTemplateRefs[]` | Doc comment + template refs inside the comment |

### `interfaces[]` item
Same structure as classes (name, typeIdentifier, path, fileName, comment, properties[], customCode[], customImports[], decorators[], genericArguments[], `interfaceTypeIdentifiers[]` to extend other interfaces). No `constructorParameters`, no `baseClassTypeIdentifier`.

### `enums[]` item
`{ name, typeIdentifier, path, fileName, comment, members[]: { name, value (number) } }`. Filenames auto-suffixed: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### `customFiles[]` item
Files without a class wrapper. `{ name, path, fileName, identifier?, customCode[]: { code, templateRefs?[] }, customImports[]: { path, types?[] } }`. The optional `identifier` lets other files reference it via `customImports[].path: <identifier>` (auto-resolves to relative path).

### `arrayTypes[]` item — virtual, no file
`{ typeIdentifier (required), elementPrimitiveType? (String|Number|Boolean|Date|Any), elementTypeIdentifier? }`. Reference via `typeIdentifier` in properties.

### `dictionaryTypes[]` item — virtual, no file
`{ typeIdentifier (required), keyPrimitiveType? | keyTypeIdentifier? | keyType? (string literal), valuePrimitiveType? | valueTypeIdentifier? }`. All 4 prim/custom combos for key/value supported.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` — virtual, no file
`{ identifier, genericClassIdentifier, genericArguments[]: { primitiveType? | typeIdentifier? } }`. Use `identifier` as a `baseClassTypeIdentifier`/`interfaceTypeIdentifiers` value or in `templateRefs`.

### `customCode[]` item structure
`{ code: string, templateRefs?: [{ placeholder: "$name", typeIdentifier: "..." }] }`. `code` is a single member (one method, one initialized field, one signature). Auto-newlines added between items.

### `customImports[]` item structure
`{ path: string, types?: string[] }`. For external libraries only. May reference a `customFile.identifier` instead of a real path — resolves automatically.

### `decorators[]` item structure
`{ code: string, templateRefs?: [{ placeholder, typeIdentifier }] }`. Available on classes, properties, and interfaces.

---

## The 7 Critical Rules

### Rule 1 — Generate ALL related types in ONE call
`typeIdentifier` references resolve **only within the current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks the typegraph and silently drops cross-file imports. The standard pattern is one big call per logical "system".

### Rule 2 — `properties` = type declarations. `customCode` = everything else.
- `properties[]` declares fields with types only (no logic, no init expressions).
- `customCode[]` is for methods, initialized fields, anything with logic. **One `customCode` item = exactly one member.**
- Never put method signatures in `properties` (e.g. `"type": "() => Promise<User[]>"`) — implementing classes will then duplicate them.
- Never put uninitialized type declarations in `customCode`.

```jsonc
"properties": [{"name": "id", "primitiveType": "String"}]
"customCode": [
  {"code": "private http = inject(HttpClient);"},
  {"code": "getAll(): T[] { return this.items; }"}
]
```

### Rule 3 — Use `templateRefs` for internal types in `customCode`
When `customCode` references a type from the same batch, use `$placeholder` syntax with `templateRefs`. This triggers automatic import resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**Critical in C#**: every internal type reference in `customCode` MUST use `templateRefs`, or `using` directives won't be generated. Raw strings like `IUserRepository` will compile-fail across namespaces.

### Rule 4 — Never add framework imports to `customImports`
MetaEngine auto-imports standard library types per-language. Adding them manually duplicates or breaks.

| Language | Auto-imported (NEVER specify) |
|---|---|
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, jackson.* |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, +more |
| Swift | Foundation (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, JSON encoders/decoders, etc.) |
| Rust | `std::collections` (HashMap/HashSet), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream) |
| Scala | `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | (no imports needed — built-in types) |

`customImports` is ONLY for external libraries (e.g. `@angular/core`, `FluentValidation`, `rxjs`, `@nestjs/common`).

### Rule 5 — `templateRefs` are ONLY for internal types
- Internal type (defined in this MCP call) → `typeIdentifier` (in properties) or `templateRefs` (in customCode/decorators/comments)
- External library → `customImports`
- Never mix.

### Rule 6 — Constructor parameters auto-create properties
In **C#, Java, Go, Groovy** (and TypeScript with `public` params), `constructorParameters[]` automatically become properties. **DO NOT** also list them in `properties[]` — causes "Sequence contains more than one matching element" errors.

```jsonc
// WRONG (duplicate)
"constructorParameters": [{"name": "email", "type": "string"}],
"properties": [{"name": "email", "type": "string"}]  // DUPLICATE!

// CORRECT
"constructorParameters": [{"name": "email", "type": "string"}]
// only ADDITIONAL non-constructor fields go in properties[]
```

### Rule 7 — Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are **reusable type references only**. Reference their `typeIdentifier` (or `identifier`) in properties / `baseClassTypeIdentifier` / `interfaceTypeIdentifiers` / `templateRefs`.

---

## Pattern Reference (verified examples)

### Cross-referenced interfaces
```jsonc
{
  "language": "typescript",
  "interfaces": [
    {"name": "Address", "typeIdentifier": "address", "properties": [
      {"name": "street", "primitiveType": "String"},
      {"name": "city", "primitiveType": "String"}
    ]},
    {"name": "User", "typeIdentifier": "user", "properties": [
      {"name": "id", "primitiveType": "String"},
      {"name": "address", "typeIdentifier": "address"}
    ]}
  ]
}
```
Produces two files with auto-imports between them.

### Class with inheritance + methods
```jsonc
{
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}],
     "customCode": [
       {"code": "getDisplayName(): string { return this.email; }"}
     ]}
  ]
}
```

### Generic class + concrete implementation
```jsonc
{
  "classes": [
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{
       "name": "T",
       "constraintTypeIdentifier": "base-entity",
       "propertyName": "items",
       "isArrayProperty": true
     }],
     "customCode": [
       {"code": "add(item: T): void { this.items.push(item); }"},
       {"code": "getAll(): T[] { return this.items; }"}
     ]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}]},
    {"name": "UserRepository", "typeIdentifier": "user-repo-class",
     "baseClassTypeIdentifier": "user-repo-concrete",
     "customCode": [{
       "code": "findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
     }]}
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{"typeIdentifier": "user"}]
  }]
}
```
The `concreteGenericClasses` entry creates a virtual `Repository<User>` type, and the class extends it via `baseClassTypeIdentifier`.

### Array & dictionary types
```jsonc
{
  "arrayTypes": [
    {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
  ]
}
```
Then reference via `"typeIdentifier": "user-list"` in properties.
**C# note**: `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with `templateRefs` in the property.

### Complex type expressions with `templateRefs`
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
`templateRefs` work in `properties`, `customCode`, `decorators`, and `comment`.

### Enum + class that uses it
```jsonc
{
  "enums": [{"name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 2}]}],
  "classes": [{"name": "Order", "typeIdentifier": "order",
    "properties": [{"name": "status", "typeIdentifier": "order-status"}],
    "customCode": [{
      "code": "updateStatus(s: $status): void { this.status = s; }",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]}]
}
```

### Service with external DI (Angular/NestJS pattern)
```jsonc
{
  "classes": [{
    "name": "ApiService", "typeIdentifier": "api-service",
    "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
    "customImports": [
      {"path": "@angular/core", "types": ["Injectable", "inject"]},
      {"path": "@angular/common/http", "types": ["HttpClient"]},
      {"path": "rxjs", "types": ["Observable"]}
    ],
    "customCode": [
      {"code": "private http = inject(HttpClient);"},
      {"code": "getUsers(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
       "templateRefs": [{"placeholder": "$list", "typeIdentifier": "user-array"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}]
}
```

### `customFiles` for type aliases / barrels
```jsonc
{
  "customFiles": [{
    "name": "types", "path": "shared", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Email = string;"}
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers",
    "customImports": [{"path": "shared-types"}],
    "customCode": [{"code": "static format(email: Email): string { return email.trim(); }"}]
  }]
}
```
Setting `identifier` lets `customImports` reference it by id (auto-resolves to relative path).

### Interface with method signatures (for `implements`)
For interfaces that a class will `implements`/`:`, define method signatures in `customCode`, NOT as function-typed properties:
```jsonc
{
  "interfaces": [{
    "name": "IUserRepository", "typeIdentifier": "user-repo",
    "fileName": "i-user-repository",
    "customCode": [
      {"code": "findAll(): Promise<$user[]>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "findById(id: string): Promise<$user | null>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }]
}
```
Function-typed properties (`"type": "() => Promise<User[]>"`) cause implementing classes to duplicate them as property declarations.

---

## Language-Specific Notes

### TypeScript
- MetaEngine **strips `I` prefix** from interface names: `IUserRepository` → exported as `UserRepository`. Use `fileName` to control file naming when collisions arise.
- Primitive map: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- Auto-indent for `\n` in `customCode`.
- Decorators supported directly.
- `arrayTypes` → `Array<T>` (e.g. `new Array<Pet>()`); `dictionaryTypes` → `Record<K, V>`.

### C#
- **`I` prefix preserved** on interface names.
- `Number` → `int` (NOT `double`). For non-integer numerics, use `"type": "decimal"` or `"type": "double"`.
- `packageName` sets the namespace. Omit/empty → no namespace declaration (good for GlobalUsings).
- Interface properties → `{ get; }`. Class properties → `{ get; set; }`.
- `arrayTypes` → `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with `templateRefs`.
- `isOptional` on properties → `string?` (nullable reference type).
- **Every internal type ref in `customCode` MUST use `templateRefs`** (else `using` directives are missing across namespaces).

### Python
- Must provide **explicit indentation (4 spaces)** after `\n` in `customCode`.
- `typing.*`, `pydantic.*`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses` auto-imported.
- `pythonOptions.modelStyle` (in `generate_sql`) ∈ `dataclass | pydantic | plain`.

### Go
- `packageName` required for multi-file projects (default `github.com/metaengine/demo`).
- No constructors — use factory functions in `customCode`.
- Constructor parameters auto-become struct fields.

### Java / Kotlin / Groovy / Scala
- `packageName` required (default `com.metaengine.generated`).
- Constructor parameters auto-become properties (Java, Groovy specifically; Kotlin uses primary constructor).
- Java: jakarta validation + jackson auto-imports.

### Swift
- Foundation auto-imported. `swiftOptions.strictEnums` (in client generators) → fail decoding on unknown cases. `typedThrows` → Swift 6 typed throws.

### Rust
- `rustOptions.crateName` required for HTTP-client generators.
- chrono, uuid, rust_decimal, serde, std::collections auto-imported.

### PHP
- `phpOptions.rootNamespace` required (e.g. `App\\Models`). `useStrictTypes` → adds `declare(strict_types=1);`.

---

## Common Mistakes (with Do/Don't)

1. **Don't** reference a `typeIdentifier` not present in this batch — the property is silently dropped. **Do** verify every `typeIdentifier` matches a defined type in the same call.
2. **Don't** put method signatures as function-typed properties on interfaces meant for `implements`. **Do** use `customCode` for interface method signatures.
3. **Don't** write internal type names as raw strings in `customCode` (e.g. `"private repo: IUserRepository"`). **Do** use `templateRefs`: `"private repo: $repo"` + `templateRefs: [{placeholder: "$repo", typeIdentifier: "user-repo"}]`.
4. **Don't** use `arrayTypes` in C# when you need `List<T>`. **Do** use `"type": "List<$user>"` with `templateRefs`.
5. **Don't** add `System.*`, `typing.*`, `java.util.*` etc. to `customImports`. **Do** let MetaEngine auto-import.
6. **Don't** duplicate constructor-parameter names in `properties[]` (C#/Java/Go/Groovy/TS). **Do** put shared fields only in `constructorParameters` and additional fields in `properties[]`.
7. **Don't** use language-reserved words (`delete`, `class`, `import`, etc.) as property names. **Do** use safe alternatives.
8. **Don't** generate related types in separate MCP calls. **Do** batch everything in one call.
9. **Don't** expect `Number` to map to `double` in C# — it maps to `int`. **Do** use `"type": "double"` or `"type": "decimal"` explicitly.
10. **Don't** forget `fileName` when an `I`-prefixed TS interface and its impl class would collide. **Do** set `"fileName": "i-user-repository"` on the interface.

---

## Output structure

For each `class`/`interface`/`enum`/`customFile` defined, MetaEngine writes one source file under `outputPath` (and its `path` subdir if specified). File naming follows the language convention (kebab-case in TS, PascalCase in C#, snake_case in Python/Rust/Go, etc.). Imports/usings/use statements are auto-generated from the resolved type graph.

Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) **never produce files**.

`dryRun: true` returns the contents in the response without writing.

`skipExisting: true` (default) only writes files that don't exist — useful for "scaffold once, edit by hand" flows.

---

## Decision Quick-Reference

| You want… | Use this |
|---|---|
| A field with a simple type | `properties[]` with `primitiveType` or `typeIdentifier` |
| A field with a complex/external type expression | `properties[]` with `type` + `templateRefs` |
| A method or initialized field | `customCode[]` (one entry per member) |
| To reference a type from the same batch in code/comments | `templateRefs` with `$placeholder` |
| To import an external library | `customImports[]` |
| A reusable `T[]` type | `arrayTypes[]` |
| A reusable `Map<K, V>`/`Dict[K, V]` type | `dictionaryTypes[]` |
| A `Repository<User>`-style concrete generic | `concreteGenericClasses[]` (then use as `baseClassTypeIdentifier`) |
| A type alias / utility / barrel file | `customFiles[]` (with optional `identifier`) |
| To skip files already on disk | leave `skipExisting: true` |
| To preview output | `dryRun: true` |
| To generate from a HTTP-spec instead of hand-rolled JSON | `generate_openapi` / `generate_graphql` / `generate_protobuf` |
| To generate model classes from SQL | `generate_sql` |
| To re-use a large spec | `load_spec_from_file` |

---

## Workflow Heuristics

1. **Analysis first**: identify ALL related types up front (a "domain"). Build the typegraph mentally — base entities, value objects, interfaces, services, controllers, DTOs, enums.
2. **One big call** per domain: every `typeIdentifier` referenced must be defined in this same JSON.
3. **Properties for shape, customCode for behavior** — check each member fits the right bucket.
4. **Internal refs use templateRefs**, external refs use customImports — no exceptions.
5. **Don't duplicate constructor params in properties** for C#/Java/Go/Groovy/TS.
6. **Don't import framework/std-lib types** — they're auto-injected.
7. Use `dryRun: true` first when uncertain; verify file structure; then run for real.
8. For very large specs, write a `.json` file and call `load_spec_from_file` to keep context lean.
