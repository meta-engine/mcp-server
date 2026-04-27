# MetaEngine MCP — Knowledge Brief (self-contained)

This brief is the *only* documentation the next session will see for the MetaEngine MCP server. It captures the full surface area: exposed tools, the `generate_code` JSON schema, every critical rule, all idiomatic patterns, language-specific quirks, and the most common pitfalls.

---

## 1. Tools exposed by the MetaEngine MCP

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns the AI guide markdown. Optional `language` param. Call at the start of a fresh session if you need a refresher. |
| `mcp__metaengine__generate_code` | **The main tool.** Semantic code generation from a structured JSON spec. Produces compilable, correctly-imported source files for TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code`, but reads the JSON spec from a file path (`specFilePath`). Saves context for large specs. Optional overrides: `outputPath`, `skipExisting`, `dryRun`. |
| `mcp__metaengine__generate_openapi` | OpenAPI (YAML/JSON, inline or URL) → typed HTTP client for `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession`. |
| `mcp__metaengine__generate_graphql` | GraphQL SDL → typed HTTP client (same framework list as OpenAPI, plus `python-fastapi`). |
| `mcp__metaengine__generate_protobuf` | Protocol Buffers `.proto` → typed HTTP client (same framework list, with `python-httpx` for Python). |
| `mcp__metaengine__generate_sql` | SQL DDL (CREATE TABLE) → typed model classes. Languages: typescript, csharp, go, python, java, kotlin, groovy, scala, swift, php, rust. |

Available MCP resources (already inlined into this brief — do not fetch again):
- `metaengine://guide/ai-assistant` (full AI guide)
- `metaengine://guide/examples` (worked examples for all languages)

Linked resources from `metaengine_initialize` are the canonical guide. There is no other documentation to fetch.

---

## 2. `generate_code` — full input schema

Top-level fields (all optional except `language`):

| Field | Type | Notes |
|---|---|---|
| `language` | enum **(required)** | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `packageName` | string | Package/module/namespace. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. **C#: omit/empty → no namespace declaration (GlobalUsings pattern).** |
| `outputPath` | string | Output directory. Default `.`. |
| `skipExisting` | boolean | Default `true`. Skip writing files that already exist (useful for stub pattern). |
| `dryRun` | boolean | Default `false`. Preview only — no files written; contents returned in response. |
| `initialize` | boolean | Default `false`. Whether to initialize properties with default values in generated code. |
| `classes` | array | Class definitions (see schema below). |
| `interfaces` | array | Interface definitions (see schema below). |
| `enums` | array | Enum definitions. |
| `arrayTypes` | array | Reusable array type references. **No files generated.** |
| `dictionaryTypes` | array | Reusable dictionary type references. **No files generated.** |
| `concreteGenericClasses` | array | Concrete generic implementations like `Repository<User>`. **No files generated** — used as type references. |
| `concreteGenericInterfaces` | array | Same as above for interfaces. **No files generated.** |
| `customFiles` | array | Files without a class/interface wrapper (type aliases, barrel exports, utility functions). |

### 2.1 `classes[]` schema

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | **Unique key for cross-references within this batch.** |
| `path` | string | Subdirectory under `outputPath` (e.g., `models`, `services/auth`). |
| `fileName` | string | Custom filename without extension. Useful to disambiguate (e.g., `i-user-repository`). |
| `comment` | string | Documentation comment for the class. |
| `isAbstract` | boolean | |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class (or of a `concreteGenericClasses` identifier for `extends Repository<User>`). |
| `interfaceTypeIdentifiers` | string[] | Interfaces to implement. |
| `genericArguments` | array | Makes this a generic *template* like `Repository<T>`. Each item: `name` (e.g. `T`), `constraintTypeIdentifier`, `propertyName`, `isArrayProperty`. |
| `constructorParameters` | array | Items: `name`, plus one of `primitiveType` / `type` / `typeIdentifier`. **In C#/Java/Go/Groovy these auto-create properties — do NOT also list them in `properties[]`.** |
| `properties` | array | See 2.4 below. |
| `customCode` | array | One item per member. See 2.5 below. |
| `customImports` | array | External library imports only. Items: `path`, `types[]`. |
| `decorators` | array | Items: `code`, optional `templateRefs`. |

### 2.2 `interfaces[]` schema

Same structural fields as classes (`name`, `typeIdentifier`, `path`, `fileName`, `comment`, `properties`, `customCode`, `customImports`, `decorators`, `genericArguments`, `interfaceTypeIdentifiers` = extends list).

For interfaces a class will `implements`, **define method signatures inside `customCode`**, not as function-typed `properties` (otherwise the implementing class duplicates them as property declarations).

### 2.3 `enums[]` schema

`name`, `typeIdentifier`, `path`, `fileName`, `comment`, and `members[]` where each member has `name` and (optional) numeric `value`.

Filename auto-suffixing: TS gets `.enum.ts`, C# gets `.cs`. Java applies `ALL_CAPS` to enum member names idiomatically.

### 2.4 Property schema (used in `classes[].properties`, `interfaces[].properties`)

| Field | Type | Notes |
|---|---|---|
| `name` | string | |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any`. |
| `typeIdentifier` | string | Reference to another type in *this same batch*. |
| `type` | string | Free-form type expression. Combine with `templateRefs` for placeholder substitution. |
| `templateRefs` | array | Items: `placeholder` (e.g. `$user`), `typeIdentifier`. |
| `isOptional` | boolean | Generates `string?` (C# nullable), `Optional<T>`, `T | undefined` etc. depending on language. |
| `isInitializer` | boolean | Add default value initialization. |
| `decorators` | array | Items: `code`, optional `templateRefs` (e.g., `@IsEmail()`, validation attributes). |
| `comment` | string | Documentation comment. |
| `commentTemplateRefs` | array | templateRefs usable in the comment text. |

**Properties = type declarations only. No logic, no initializers with code, no methods.**

### 2.5 customCode schema

Each item is one member (one method, one initialized field, one property with default, one interface signature):

| Field | Type | Notes |
|---|---|---|
| `code` | string | The literal source text (one member per item — automatic newlines added between blocks). |
| `templateRefs` | array | Items: `placeholder` (e.g. `$user`), `typeIdentifier`. Resolves placeholders to real type names AND auto-imports them. |

### 2.6 `arrayTypes[]` schema

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string **(required)** | Identifier to reference this array type. |
| `elementPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any`. |
| `elementTypeIdentifier` | string | Reference to a custom type in this batch. |

**No files are generated.** Reference via `typeIdentifier` from a property. **C# emits `IEnumerable<T>` for arrayTypes — for `List<T>` use `"type": "List<$user>"` with `templateRefs` instead.**

### 2.7 `dictionaryTypes[]` schema

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string **(required)** | |
| `keyPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any`. |
| `keyType` | string | String literal type, e.g. `'string'`. |
| `keyTypeIdentifier` | string | Reference to custom key type. |
| `valuePrimitiveType` | enum | Same enum. |
| `valueTypeIdentifier` | string | Reference to custom value type. |

All four key×value combinations (prim/prim, prim/custom, custom/prim, custom/custom) are valid. Generates `Record<K, V>` (TS), `Dictionary<K, V>` (C#), `dict[K, V]` (Python), `map[K]V` (Go), etc.

### 2.8 `concreteGenericClasses[]` and `concreteGenericInterfaces[]`

| Field | Type | Notes |
|---|---|---|
| `identifier` | string | Reference id for this concrete combination. |
| `genericClassIdentifier` | string | Points at the generic class/interface template's `typeIdentifier`. |
| `genericArguments` | array | Items: `typeIdentifier` or `primitiveType` per generic slot. |

**No files generated.** Use the `identifier` as a `baseClassTypeIdentifier` (to extend) or in `templateRefs` (to reference inline as `Repository<User>`).

### 2.9 `customFiles[]` schema

| Field | Type | Notes |
|---|---|---|
| `name` | string | Filename without extension. |
| `path` | string | Subdirectory. |
| `fileName` | string | Alternate filename without extension (overrides `name` for output). |
| `identifier` | string | Optional id used by other files' `customImports` to auto-resolve relative paths. |
| `customCode` | array | One item per export/type alias/function. |
| `customImports` | array | External imports for this file. |

Used for type aliases, barrel exports, util modules. **No class/interface wrapper.**

---

## 3. The seven critical rules

These cause the most failures when violated.

### Rule 1 — One call, all related types
`typeIdentifier` only resolves *within the current batch*. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks the typegraph and silently drops cross-references.

### Rule 2 — Properties are type declarations, customCode is everything else
- `properties[]`: type-only field declarations (no initializers with logic, no methods).
- `customCode[]`: methods, initialized fields with logic, interface method signatures. **One member per `customCode` item** (newlines between blocks are automatic).

Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

### Rule 3 — Use `templateRefs` for internal types in customCode
When `customCode` references a type from the same batch, use `$placeholder` syntax + a `templateRefs` entry. This drives the import resolver. Without it the import line is not generated.

```json
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

**C# is unforgiving here**: every internal cross-namespace reference in customCode must use `templateRefs`, or the `using` directive will be missing and compilation fails.

### Rule 4 — Never add framework imports to `customImports`
The engine auto-imports every standard-library type. Adding them manually causes duplicates or errors.

| Language | Auto-imported (never specify) |
|---|---|
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, +more |
| Swift | `Foundation` (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`, …) |
| Rust | `std::collections` (`HashMap`, `HashSet`), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (`UUID`, `Date`), `java.io` (`File`, `InputStream`, `OutputStream`) |
| Scala | `java.time.*`, `scala.math` (`BigDecimal`, `BigInt`), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | (no imports needed — built-in types) |

`customImports` is for **external libraries only** (`@angular/core`, `rxjs`, `FluentValidation`, etc.).

### Rule 5 — `templateRefs` are ONLY for internal types
External library types must use `customImports`. If a type is generated in this same call → use `typeIdentifier` (in properties) or `templateRefs` (in customCode/decorators). If it's an external library → use `customImports`. **Never mix.**

### Rule 6 — Constructor parameters auto-create properties (C#, Java, Go, Groovy)
Listing a name in both `constructorParameters[]` and `properties[]` causes:
> "Sequence contains more than one matching element"

In TypeScript, constructor parameters with `public`/`private` also become properties. Put shared ctor-backed fields in `constructorParameters` only; use `properties[]` only for *additional* fields.

### Rule 7 — Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reusable type references. They never produce files. Reference them by `typeIdentifier`/`identifier` from properties, customCode, or `baseClassTypeIdentifier`.

---

## 4. Pattern reference

### 4.1 Cross-referenced interfaces (perfect imports)
```json
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

### 4.2 Inheritance + methods
```json
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

### 4.3 Generic class + concrete implementation
```json
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
The `concreteGenericClasses` entry produces a virtual `Repository<User>` type. The class `extends` it via `baseClassTypeIdentifier`.

### 4.4 Array and dictionary types
```json
{
  "arrayTypes": [
    {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
    {"typeIdentifier": "by-user", "keyTypeIdentifier": "user", "valuePrimitiveType": "String"},
    {"typeIdentifier": "user-meta", "keyTypeIdentifier": "user", "valueTypeIdentifier": "metadata"}
  ]
}
```
Reference via `"typeIdentifier": "user-list"` in properties.

### 4.5 Complex type expressions with `templateRefs` in properties
```json
{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}
```
`templateRefs` work in properties (`type` field), `customCode`, decorators, and comments.

### 4.6 Enum + class that uses it
```json
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
Filename auto-suffixing: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### 4.7 Service with external DI (Angular/NestJS)
```json
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

### 4.8 `customFiles` for type aliases / barrel exports
```json
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
The `identifier` on the customFile lets other files import from it via that id; the engine resolves the relative path.

### 4.9 Interface with method signatures (TS / C#)
For interfaces a class will `implements`:
```json
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
**Don't** model these as function-typed properties — the implementing class would duplicate them as property declarations.

### 4.10 Constructor params — correct vs. wrong
```json
// ❌ WRONG (C#/Java/Go/Groovy — also problematic in TS with public/private params):
{
  "constructorParameters": [{"name": "email", "type": "string"}],
  "properties": [{"name": "email", "type": "string"}]
}

// ✅ CORRECT:
{
  "constructorParameters": [{"name": "email", "type": "string"}],
  "properties": [{"name": "createdAt", "primitiveType": "Date"}]
}
```

---

## 5. Language-specific notes

### TypeScript
- Strips `I` prefix from interface names — `IUserRepository` → exported as `UserRepository`. Set `fileName` (e.g., `i-user-repository`) to disambiguate when a class with the same base name exists.
- Primitive mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- Auto-indents customCode newlines (`\n`).
- Decorators supported directly.

### C#
- `I` prefix preserved on interface names.
- `Number` → `int` (NOT `double`). Use `"type": "decimal"` or `"type": "double"` when needed.
- `packageName` → namespace. Omit/empty → no namespace declaration (GlobalUsings pattern).
- Interface properties → `{ get; }`. Class properties → `{ get; set; }`.
- `arrayTypes` produce `IEnumerable<T>`. For `List<T>` use `"type": "List<$user>"` with templateRefs.
- `isOptional` → nullable reference type (`string?`).
- Internal cross-namespace references in `customCode` MUST use `templateRefs` — otherwise the `using` directive is missing.

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode.
- `typing.*` imports are automatic.
- Engine applies `snake_case` to method names idiomatically.
- pydantic `BaseModel`, `Field`, `dataclasses`, `datetime`, `decimal`, `enum`, `abc` are auto-imported.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — write factory functions in `customCode`.
- Constructor parameters (if used) auto-become struct fields.

### Java
- `packageName` defaults to `com.metaengine.generated`.
- Enum members are emitted in `ALL_CAPS` idiomatically.
- `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` auto-imported.
- Constructor parameters auto-become fields.

### Kotlin / Groovy / Scala
- Standard `java.time.*`, `java.math.*`, `java.util.UUID` auto-imported.
- Kotlin: `kotlinx.serialization.*` auto-imported.
- Scala: `scala.math` (`BigDecimal`, `BigInt`), `scala.collection.mutable.*` auto-imported.
- Groovy: constructor parameters auto-become fields.

### Swift
- `Foundation` types (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`) auto-imported.

### Rust
- `std::collections` (`HashMap`, `HashSet`), `chrono`, `uuid`, `rust_decimal`, `serde` auto-imported.

### PHP
- `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` auto-imported.

---

## 6. Top common mistakes

1. **Dangling `typeIdentifier`** — referenced but not defined in the batch → silently dropped. Verify every reference.
2. **Function-typed interface properties** — instead of customCode signatures → implementing class duplicates them as property declarations.
3. **Raw type names in customCode** (e.g. `private repo: IUserRepository`) → no import generated. Use `$repo` + `templateRefs`.
4. **`arrayTypes` in C# when you need `List<T>`** — they produce `IEnumerable<T>`. Use `"type": "List<$user>"` + templateRefs.
5. **Adding framework types to `customImports`** (`System.*`, `typing.*`, `java.util.*`) → duplicates/errors. They're auto-imported.
6. **Duplicating constructor parameters in `properties`** in C#/Java/Go/Groovy/TS → "Sequence contains more than one matching element".
7. **Reserved words as property names** (`delete`, `class`, `import`) — use safe names (`remove`, `clazz`, `importData`).
8. **Splitting related types across multiple MCP calls** → cross-imports unresolved. Always one batch.
9. **Expecting `Number` to be `double` in C#** — it's `int`. Use `"type": "decimal"` / `"type": "double"`.
10. **TS file-name collisions with `I`-prefixed interfaces and their implementing classes** — set `"fileName": "i-user-repository"` on the interface.

---

## 7. Output structure

- `generate_code` writes one file per file-generating type (classes, interfaces, enums, customFiles) under `outputPath` (subdirectoried by `path`).
- Filenames follow language conventions: TS `kebab-case.ts` (with `.enum.ts` for enums), C# `PascalCase.cs`, Python `snake_case.py`, etc.
- Imports are deduplicated and grouped per language idiom.
- Virtual types (arrayTypes, dictionaryTypes, concreteGenericClasses/Interfaces) generate **no files** — they are inlined wherever referenced.
- With `dryRun: true`, the response payload contains generated file contents instead of writing to disk — useful for review.
- With `skipExisting: true` (default), existing files are not overwritten — useful for the "stub then customize" flow.

---

## 8. Workflow checklist for a generation task

1. **Inventory all types** the spec demands (entities, DTOs, services, enums, repositories, type aliases). Classify each: class, interface, enum, customFile, arrayType, dictionaryType, concreteGeneric.
2. **Assign a unique `typeIdentifier`** to every type. Use kebab-case ids.
3. **Plan cross-references** — every referenced id must exist in the same batch. Reference internal types by `typeIdentifier`/`templateRefs`, never by raw string.
4. **Properties for type-only declarations**, `customCode` for methods/initialized fields/interface signatures (one member per item).
5. **External libraries → `customImports`** with `path` + `types[]`. Never list framework/stdlib types here.
6. **For C#: every internal type reference in customCode → `templateRefs`** (or imports break).
7. **Constructor parameters do NOT go in `properties`** for C#/Java/Go/Groovy (and TS public/private ctor params).
8. **For mutable lists in C#, use `"type": "List<$x>"` + templateRefs**, not `arrayTypes`.
9. **One single `generate_code` call** containing the entire spec. Don't chunk by domain — typeIdentifier resolution is batch-local.
10. **Optionally `dryRun: true`** first if you want to inspect output before writing.

---

## 9. Quick reference — when to use which top-level array

| Need | Use |
|---|---|
| Class file with fields/methods | `classes[]` |
| Interface file (with extends/implements support) | `interfaces[]` |
| Enum file | `enums[]` |
| Reusable `T[]` reference | `arrayTypes[]` |
| Reusable `Map<K,V>` / `Record<K,V>` reference | `dictionaryTypes[]` |
| Reusable `Repository<User>` inline reference | `concreteGenericClasses[]` |
| Reusable `IRepository<User>` inline reference | `concreteGenericInterfaces[]` |
| Type aliases, barrel exports, util modules (no class wrapper) | `customFiles[]` |

---

## 10. The single most important takeaway

**Build the entire spec mentally first. Make ONE `generate_code` call with all classes, interfaces, enums, arrayTypes, dictionaryTypes, customFiles, etc. populated in the same payload. Cross-references only resolve within a single call — splitting by domain breaks the typegraph.**
