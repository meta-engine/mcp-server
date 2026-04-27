# MetaEngine MCP — Knowledge Brief (self-contained)

This brief is the operating manual for a generation session that has NO access to MetaEngine docs. Read top-to-bottom before calling any `mcp__metaengine__*` tool.

MetaEngine is a **semantic** code generator: you submit a structured JSON describing types, members, relationships and methods; MetaEngine resolves cross-references, produces idiomatic source files for the chosen language, and writes correct imports/usings automatically. It supports: **TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust**.

A single well-formed `generate_code` call replaces dozens of error-prone manual file writes — but only if the spec is complete and rules below are followed.

---

## 1. Tools exposed by the MCP server `metaengine`

### `mcp__metaengine__metaengine_initialize`
Returns the MetaEngine guide markdown. Optional `language` param (one of `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php`). Call once before generating if no docs are cached. Also exposes two MCP resources:
- `metaengine://guide/ai-assistant` — full guide (rules + patterns + language notes + common mistakes)
- `metaengine://guide/examples` — six worked examples with input + generated output

### `mcp__metaengine__generate_code`
The main tool. Generates source files from a structured spec. **One call should contain ALL related types** (see Critical Rule #1). Full schema in §2.

### `mcp__metaengine__load_spec_from_file`
Same generation engine, but loads spec JSON from disk. Saves AI context for big specs.
- `specFilePath` (required) — absolute or relative path to spec JSON
- `outputPath` (optional override)
- `skipExisting` (optional override)
- `dryRun` (optional override)

### `mcp__metaengine__generate_openapi`
Generates a fully typed HTTP **client** from an OpenAPI spec.
- `framework` (required) — one of: `angular | react | typescript-fetch | go-nethttp | java-spring | python-fastapi | csharp-httpclient | kotlin-ktor | rust-reqwest | swift-urlsession`
- Either `openApiSpec` (inline YAML/JSON) or `openApiSpecUrl` is required
- Per-framework option blocks (see §6)
- Cross-cutting: `basicAuth`, `bearerAuth`, `customHeaders`, `errorHandling`, `retries`, `timeout`, `documentation`, `optionsObjectThreshold`, `strictValidation`
- Output controls: `outputPath` (default `.`), `skipExisting` (default true), `dryRun` (default false)

### `mcp__metaengine__generate_graphql`
HTTP client from a GraphQL SDL schema. Same 10 frameworks as OpenAPI.
- `framework` + `graphQLSchema` (SDL string) required
- Per-framework option blocks; auth/headers/retries/timeout/documentation/errorHandling
- `discriminatedUnions: bool` for union handling

### `mcp__metaengine__generate_protobuf`
HTTP client from `.proto` source. Same 10 frameworks (Python uses `python-httpx`).
- `framework` + `protoSource` required
- Same option/auth/retry/timeout/dry-run pattern

### `mcp__metaengine__generate_sql`
Typed model classes from SQL DDL (CREATE TABLE).
- `language` (required) — one of `typescript|csharp|go|python|java|kotlin|groovy|scala|swift|php|rust`
- `ddlSource` (required) — DDL string
- Toggles: `generateInterfaces`, `generateNavigationProperties`, `generateValidationAnnotations`, `initializeProperties`
- Per-language options: `csharpOptions.namespace`, `goOptions.moduleName`, `javaOptions.packageName`, `kotlinOptions.packageName`, `groovyOptions.packageName`, `scalaOptions.packageName`, `phpOptions.{rootNamespace, useStrictTypes}`, `pythonOptions.modelStyle` (`dataclass|pydantic|plain`), `rustOptions.crateName`
- `outputPath` / `skipExisting` / `dryRun`

---

## 2. `generate_code` — full input schema

Top-level fields:

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php | rust` |
| `packageName` | string | Namespace/module/package. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. **C#: omit/empty → no namespace declaration (GlobalUsings pattern)**. |
| `outputPath` | string (default `.`) | Where files are written. |
| `skipExisting` | bool (default `true`) | Don't overwrite existing files (stub pattern). |
| `dryRun` | bool (default `false`) | If true, returns generated code in response without writing files. |
| `initialize` | bool (default `false`) | Initialize properties with default values. |
| `classes[]` | array | Class definitions (regular and generic templates). |
| `interfaces[]` | array | Interface definitions (regular and generic templates). |
| `enums[]` | array | Enum definitions. |
| `arrayTypes[]` | array | **Virtual** array type refs (no files). |
| `dictionaryTypes[]` | array | **Virtual** dictionary type refs (no files). |
| `concreteGenericClasses[]` | array | **Virtual** concrete generics e.g. `Repository<User>` (no files). |
| `concreteGenericInterfaces[]` | array | **Virtual** concrete generic interfaces (no files). |
| `customFiles[]` | array | Free-form files: type aliases, barrel exports, utility funcs (no class wrapper). |

### `classes[]` items

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | Unique ID used to reference this class from other types in the same call. |
| `path` | string | Subdir e.g. `services/auth`. |
| `fileName` | string | Override file name (no extension). |
| `comment` | string | Class-level doc comment. |
| `isAbstract` | bool | |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class (can be a `concreteGenericClasses` identifier). |
| `interfaceTypeIdentifiers[]` | string[] | Implemented interface IDs. |
| `genericArguments[]` | array | Makes class a generic template. Each item: `{ name, constraintTypeIdentifier?, propertyName?, isArrayProperty? }`. `propertyName`+`isArrayProperty` causes a property of type `T` or `T[]` to be auto-generated. |
| `constructorParameters[]` | array | `{ name, type? | typeIdentifier? | primitiveType? }`. **In C#/Java/Go/Groovy these auto-create properties — do not duplicate in `properties[]`.** |
| `properties[]` | array | See "property item" below. |
| `customCode[]` | array | `{ code, templateRefs? }`. ONE item == ONE member (method or initialized field). Auto-newlines between blocks. |
| `customImports[]` | array | `{ path, types[] }`. **External libraries only.** Never framework stdlib. |
| `decorators[]` | array | `{ code, templateRefs? }`. |

### Property item (`properties[]`)

| Field | Notes |
|---|---|
| `name` | Property name. **Avoid reserved words** (`delete`, `class`, `import`). |
| `primitiveType` | enum: `String | Number | Boolean | Date | Any` (one of three type-spec strategies). |
| `typeIdentifier` | Reference to another type in same batch (or virtual type). |
| `type` | Free-form string for complex/external expressions, e.g. `"List<$user>"`, `"Map<string,$resp>"`. |
| `templateRefs[]` | `{ placeholder, typeIdentifier }`. Required when `type`/`code` contains `$placeholder` referring to internal types. |
| `isOptional` | bool. C#: produces nullable `string?`. |
| `isInitializer` | bool. Add default value initializer. |
| `decorators[]` | Property decorators (`@IsEmail()`, `@Required()`, etc.). |
| `comment` | Doc comment. |
| `commentTemplateRefs[]` | templateRefs in comments. |

### `interfaces[]` items
Same shape as classes but used to declare interfaces. Method signatures for an interface that will be `implements`-ed go in **`customCode`**, NOT as function-typed properties. `genericArguments[]` and `interfaceTypeIdentifiers[]` (for extends) supported.

### `enums[]` items

| Field | Notes |
|---|---|
| `name`, `typeIdentifier`, `path`, `fileName`, `comment` | usual. |
| `members[]` | `[{ name, value: number }]` |

Enums get auto-suffixed file names (`order-status.enum.ts`, `OrderStatus.cs`).

### `arrayTypes[]` (virtual — NO file)

```jsonc
{ "typeIdentifier": "user-list", "elementTypeIdentifier": "user" }       // ref to internal type
{ "typeIdentifier": "string-array", "elementPrimitiveType": "String" }   // primitive
```
**C#: arrayTypes generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` + templateRefs on the property.**

### `dictionaryTypes[]` (virtual — NO file)

All 4 combinations supported:

```jsonc
{ "typeIdentifier": "scores",   "keyPrimitiveType": "String", "valuePrimitiveType": "Number" }
{ "typeIdentifier": "lookup",   "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
{ "typeIdentifier": "names",    "keyTypeIdentifier": "user",  "valuePrimitiveType": "String" }
{ "typeIdentifier": "metadata", "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata" }
```
Also has a free-form `keyType` string field for unusual key types.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` (virtual — NO file)

```jsonc
{
  "identifier": "user-repository",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{ "typeIdentifier": "user" }]   // or { "primitiveType": "String" }
}
```
Use the resulting `identifier` as `baseClassTypeIdentifier` of a class to extend `Repository<User>` with correct imports. Or reference via `templateRefs` in customCode.

### `customFiles[]`

```jsonc
{
  "name": "types",            // file name (no ext)
  "path": "shared",
  "identifier": "shared-types", // optional — lets other files import via customImports.path == identifier
  "fileName": "...",            // optional override
  "customImports": [...],
  "customCode": [
    { "code": "export type UserId = string;" },
    { "code": "export type Email = string;" }
  ]
}
```
Used for type aliases, barrel exports, plain utility functions — anything that is NOT a class/interface/enum.

### `customCode` block (used in classes/interfaces/customFiles/decorators)

```jsonc
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
}
```
- One block per member. Engine adds blank lines between blocks.
- `$placeholder` tokens in `code` get replaced with the resolved type name and trigger import generation — only when `templateRefs` declares them.
- Python: must include explicit 4-space indentation after `\n`.

### `customImports` block

```jsonc
{ "path": "@angular/core", "types": ["Injectable", "inject"] }
{ "path": "shared-types" }   // when path matches a customFile identifier, auto-resolves to relative path
```
**Only for external libraries** (or customFile identifiers). Never list stdlib types.

---

## 3. The 7 Critical Rules

### Rule 1 — Generate ALL related types in ONE call
`typeIdentifier` references resolve **only within the current batch**. `UserService` referencing `User` requires both in the same `generate_code` call. Splitting per-domain destroys cross-file imports. **One call, full spec.**

### Rule 2 — `properties` declares types only; `customCode` for everything else
- `properties[]`: bare type declarations (no init, no logic).
- `customCode[]`: methods, initialized fields, anything containing logic.
- One `customCode` item == exactly one member.
- Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

```jsonc
"properties": [{ "name": "id", "primitiveType": "String" }]
"customCode": [
  { "code": "private http = inject(HttpClient);" },
  { "code": "getAll(): T[] { return this.items; }" }
]
```

### Rule 3 — Use `templateRefs` for internal types referenced in `customCode`
When customCode references a type generated in the same batch, use `$placeholder` + `templateRefs`. This is what triggers automatic import resolution.

```jsonc
{ "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
```
**C# is strictest here**: every internal type reference in customCode MUST use templateRefs, otherwise cross-namespace `using` directives are not generated and the code fails to compile.

### Rule 4 — NEVER add framework/stdlib imports to `customImports`
MetaEngine auto-imports the language's standard library. Manually adding them causes duplication errors.

| Language | Auto-imported (NEVER specify) |
|---|---|
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, ...` |
| Swift | `Foundation` (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`, ...) |
| Rust | `std::collections` (`HashMap`, `HashSet`), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (`UUID`, `Date`), `java.io` (`File`, `InputStream`, `OutputStream`) |
| Scala | `java.time.*`, `scala.math` (`BigDecimal`, `BigInt`), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | (no imports needed for built-in types) |

`customImports` is only for external libs (`@angular/core`, `rxjs`, `FluentValidation`, ...).

### Rule 5 — `templateRefs` is for INTERNAL types only
- Internal type (in same batch) → `typeIdentifier` (in property) or `templateRefs` (in code).
- External library type → `customImports`.
- Never mix.

### Rule 6 — Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Do NOT duplicate `constructorParameters` in `properties[]`. Causes runtime error: `"Sequence contains more than one matching element"`.

```jsonc
// WRONG
"constructorParameters": [{"name": "email", "type": "string"}],
"properties":            [{"name": "email", "type": "string"}]

// CORRECT
"constructorParameters": [{"name": "email", "type": "string"}]
// Other (non-ctor) fields go in properties[]
```

### Rule 7 — Virtual types do NOT generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` only create reusable type references. They never produce files. Use them by referencing their `typeIdentifier`/`identifier` in properties/customCode/baseClassTypeIdentifier.

---

## 4. Pattern Reference (canonical recipes)

### 4.1 Cross-referencing interfaces

```jsonc
{
  "language": "typescript",
  "interfaces": [
    {"name": "Address", "typeIdentifier": "address",
     "properties": [
       {"name": "street", "primitiveType": "String"},
       {"name": "city",   "primitiveType": "String"}
     ]},
    {"name": "User", "typeIdentifier": "user",
     "properties": [
       {"name": "id",      "primitiveType": "String"},
       {"name": "address", "typeIdentifier": "address"}
     ]}
  ]
}
```
Two files, automatic `import { Address } from './address'` in `user.ts`.

### 4.2 Class with abstract base + method

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

### 4.3 Generic class + concrete instantiation

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
The virtual `user-repo-concrete` represents `Repository<User>`; `UserRepository extends Repository<User>` with imports auto-resolved.

### 4.4 Array & dictionary types

```jsonc
{
  "arrayTypes": [
    {"typeIdentifier": "user-list",    "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array", "elementPrimitiveType":  "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
  ]
}
```
Reference by `"typeIdentifier": "user-list"` in properties.

### 4.5 Complex type expressions with templateRefs in `properties.type`

```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
`templateRefs` are also valid in `decorators[].code` and `comment`/`commentTemplateRefs`.

### 4.6 Enum + class consuming it

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

### 4.7 Service with external DI library

```jsonc
{
  "classes": [{
    "name": "ApiService", "typeIdentifier": "api-service",
    "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
    "customImports": [
      {"path": "@angular/core", "types": ["Injectable", "inject"]},
      {"path": "@angular/common/http", "types": ["HttpClient"]}
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

### 4.8 customFiles for type aliases / barrel exports

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
Setting `identifier` on a customFile lets other files import it via `customImports.path == identifier`; MetaEngine resolves the relative path.

### 4.9 Interface with method signatures (TS / C#)

For interfaces a class will `implements`/`:`, declare methods in `customCode` (NOT as function-typed properties — those would duplicate as property declarations on the implementer).

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

### 4.10 Constructor parameters (C#/Java/Go/Groovy/TS)

```jsonc
// CORRECT
"classes": [{
  "name": "User", "typeIdentifier": "user",
  "constructorParameters": [
    {"name": "email",  "type": "string"},
    {"name": "status", "typeIdentifier": "status"}
  ],
  "properties": [
    {"name": "createdAt", "primitiveType": "Date"}   // additional only
  ]
}]
```
Generated TS:
```ts
import { Status } from './status.enum';
export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

---

## 5. Language-Specific Notes

### TypeScript
- Strips `I` prefix from interface names: `IUserRepository` → exported as `UserRepository`. To avoid file-name collisions with the implementing class, set `fileName: "i-user-repository"` on the interface.
- Primitive mapping: `Number`→`number`, `String`→`string`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`.
- Auto-indent applied for `\n` in customCode.
- Decorators supported directly.
- No imports needed for built-ins.

### C#
- `I` prefix preserved on interface names.
- Primitive `Number` → **`int`** (not `double`). For non-integer numbers use `"type": "decimal"` or `"type": "double"`.
- `packageName` sets the namespace. **Omit/empty** to skip `namespace` declaration (GlobalUsings pattern).
- Interface properties: `{ get; }`. Class properties: `{ get; set; }`.
- `arrayTypes` produce `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs on the property.
- `isOptional` emits nullable reference type (e.g. `string?`).
- Internal type refs in customCode MUST use templateRefs or cross-namespace usings won't be added.

### Python
- Must include explicit 4-space indentation after `\n` in customCode.
- typing/pydantic/datetime/decimal/enum/abc/dataclasses imports auto-applied.

### Go
- `packageName` required for multi-file output (default `github.com/metaengine/demo`).
- No constructors — emit factory functions in `customCode`.
- Constructor parameters in `constructorParameters[]` still auto-become struct fields; don't duplicate in `properties`.

### Java / Kotlin / Groovy / Scala
- Default `packageName`: `com.metaengine.generated`.
- Java/Kotlin/Groovy: constructor parameters auto-create properties — don't duplicate.

### Swift / PHP / Rust
- Standard auto-imports listed in Rule 4 table.

---

## 6. Spec-driven generators (`generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`)

These are higher-level than `generate_code`. They consume an external schema and emit a full HTTP client (or models for SQL).

### Common output controls
`outputPath` (default `.`), `skipExisting` (default true), `dryRun` (default false), `documentation`, `errorHandling`, `retries`, `timeout`, `basicAuth`, `bearerAuth`, `customHeaders`.

### Per-framework option blocks (REQUIRED FIELDS where listed)
- `angularOptions`: `baseUrlToken`, `providedIn`, `useInjectFunction`, `useHttpResources`, `httpResourceTrigger`, `responseDateTransformation` (OpenAPI also has these).
- `reactOptions`: `baseUrlEnvVar`, `useTanStackQuery`, `useTypesBarrel`, `responseDateTransformation`.
- `fetchOptions` (typescript-fetch): `baseUrlEnvVar`, `useImportMetaEnv`, `useMiddleware`, `useResultPattern`, `useTypesBarrel`.
- `goOptions`: **`moduleName` & `packageName` required**; `baseUrlEnvVar`, `jsonLibrary`, `useContext`.
- `javaSpringOptions`: **`packageName` required**; `baseUrlProperty`, `beanValidation`, `nonNullSerialization`, `useComponentAnnotation`.
- `csharpOptions`: **`namespaceName` required**.
- `kotlinOptions`: **`packageName` required**.
- `pythonOptions`: `baseUrlEnvVar`, `generateSyncMethods`, `useCamelCaseAliases`.
- `rustOptions`: **`crateName` required**; `strictEnums`.
- `swiftOptions`: `strictEnums`, `typedThrows`.

### `errorHandling`
- OpenAPI: `{ enabled, returnNullForStatusCodes[], throwForStatusCodes[] }`.
- GraphQL/Protobuf: `{ mode: "throw"|"result" }`.

### `retries`
- OpenAPI: `{ maxAttempts, baseDelaySeconds, maxDelaySeconds, retryStatusCodes[] }`.
- GraphQL/Protobuf: `{ maxRetries }`.

### `timeout`
- OpenAPI: `{ seconds, connect, read, write }`.
- GraphQL/Protobuf: `{ seconds }`.

### `generate_sql` specifics
- Toggles: `generateInterfaces`, `generateNavigationProperties`, `generateValidationAnnotations`, `initializeProperties`.
- `pythonOptions.modelStyle` ∈ `dataclass | pydantic | plain`.
- `phpOptions.useStrictTypes` adds `declare(strict_types=1)`.
- `csharpOptions.namespace` (note: **`namespace`**, not `namespaceName`).

---

## 7. Output structure

For `generate_code`:
- One file per **non-virtual** type (class, interface, enum, customFile).
- `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` → no files (references only).
- File location: `outputPath` + class/interface/enum/customFile `path` + name (kebab/Pascal-case per language convention).
- Imports auto-resolved across the batch; framework stdlib auto-imported.
- `dryRun: true` returns generated file contents in the response without writing.
- `skipExisting: true` (default) skips overwriting existing files — useful for stub patterns (regenerate only new files).

For schema-driven generators: emits a full client tree (models + services + auth helpers + sometimes hooks/middleware) appropriate to the framework.

---

## 8. Common Mistakes Cheat-Sheet

1. **Dangling `typeIdentifier`** — referencing a type not in the batch silently drops the property. Always verify every ID has a matching definition in the same call.
2. **Function-typed properties on interfaces** — implementer will get a duplicate property. Use `customCode` for interface methods that will be implemented.
3. **Raw type names in customCode** — `private repo: IUserRepository` without templateRefs → no import. Use `$repo` + templateRefs.
4. **Using `arrayTypes` in C# when you need `List<T>`** — produces `IEnumerable<T>`. Use `"type": "List<$user>"` + templateRefs.
5. **Adding stdlib to `customImports`** — duplicates / errors. Trust auto-imports.
6. **Duplicating ctor params in `properties` (C#/Java/Go/Groovy)** — `"Sequence contains more than one matching element"`. Put shared fields only in `constructorParameters`.
7. **Reserved-word property names** (`delete`, `class`, `import`) — rename (`remove`, `clazz`, `importData`).
8. **Splitting per-domain into multiple calls** — cross-references break. ONE call, full spec.
9. **Expecting `Number` to map to `double` in C#** — it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.
10. **Interface vs class file-name collision in TS** — `IUserRepository` strips `I` → file collides with `UserRepository`. Set `fileName: "i-user-repository"` on the interface.

---

## 9. Hard rules summary (one-liners)

- **One call, full spec.** Cross-references resolve only inside a single `generate_code` invocation.
- **Properties = types only. customCode = members.** One customCode block per member.
- **`$placeholder` + `templateRefs` for internal types in code/decorators/complex `type` strings.** Required for imports.
- **`customImports` only for external libs** (or customFile identifiers). Never stdlib.
- **Virtual types (`arrayTypes` / `dictionaryTypes` / `concreteGeneric*`) never make files** — they're reference helpers.
- **Don't duplicate ctor params in properties** (C#/Java/Go/Groovy).
- **C# customCode internal type refs MUST use templateRefs** or usings won't be generated.
- **C# `Number` → `int`.** Use explicit `"type": "double"` or `"type": "decimal"` for non-integer.
- **TS `I`-prefixed interfaces strip the `I` from the export.** Use `fileName` to avoid collisions.
- **Python customCode requires explicit 4-space indentation after `\n`.**
- **Reserved words are not safe property names.**
- **Set `dryRun: true`** when you want to inspect output without writing files. Default `skipExisting: true` (stub-friendly).

---

## 10. End-to-end example (NestJS service)

```jsonc
{
  "language": "typescript",
  "classes": [
    {"name": "Pet", "typeIdentifier": "pet",
     "properties": [{"name": "name", "primitiveType": "String"}]}
  ],
  "arrayTypes": [
    {"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}
  ],
  "classes": [{
    "name": "PetService", "typeIdentifier": "pet-service", "path": "services",
    "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
    "customImports": [
      {"path": "@nestjs/common", "types": ["Injectable", "inject"]},
      {"path": "@nestjs/common/http", "types": ["HttpClient"]},
      {"path": "rxjs", "types": ["Observable"]}
    ],
    "customCode": [
      {"code": "private http = inject(HttpClient);"},
      {"code": "private baseUrl = '/api/pets';"},
      {"code": "getAll(): Observable<$petArray> { return this.http.get<$petArray>(this.baseUrl); }",
       "templateRefs": [{"placeholder": "$petArray", "typeIdentifier": "pet-array"}]},
      {"code": "getById(id: string): Observable<$pet> { return this.http.get<$pet>(`${this.baseUrl}/${id}`); }",
       "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]},
      {"code": "create(pet: $pet): Observable<$pet> { return this.http.post<$pet>(this.baseUrl, pet); }",
       "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]}
    ]
  }]
}
```
Produces `pet.ts` and `services/pet-service.ts` with all imports auto-resolved (Pet, Array<Pet> via the arrayType, `@nestjs/common`, `rxjs`).

---

## 11. Workflow guidance (for the gen session)

1. **Plan first, then one call.** Identify every type (entities, DTOs, services, enums, interfaces) for the whole feature. Map each to a `typeIdentifier`. Confirm every reference has a definition.
2. **Decide the type-spec strategy per property**:
   - simple primitive → `primitiveType`
   - reference to another generated type → `typeIdentifier`
   - complex/external/expression → `type` (+ `templateRefs` for internal placeholders)
3. **Decide imports**: stdlib → none; external lib → `customImports`; internal generated → `templateRefs` / `typeIdentifier`.
4. **Use virtual types** (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`) for collections and concrete generics rather than typing them inline — improves reuse and import accuracy.
5. **Default `dryRun: false`** for real output. Use `dryRun: true` to inspect before writing.
6. **For very large specs, switch to `load_spec_from_file`** to keep AI context lean.
7. **Don't iterate file-by-file.** Add missing types to the same call and regenerate.
8. **For OpenAPI/GraphQL/Protobuf/SQL**, prefer the dedicated tools — they understand schema semantics (auth, error handling, retries, validation) that `generate_code` would only emit by hand.
