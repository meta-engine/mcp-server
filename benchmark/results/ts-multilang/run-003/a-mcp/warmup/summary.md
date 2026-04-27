# MetaEngine MCP — Knowledge Brief

> Self-contained reference for code generation. The next session will only have this file.
> All facts here are extracted verbatim from `metaengine://guide/ai-assistant`,
> `metaengine://guide/examples`, and the live JSONSchema of each MCP tool.

---

## What MetaEngine is

MetaEngine is a **semantic** code generator (not template-based). You describe types,
relationships, and methods as structured JSON. It produces compilable source files for:

- TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust

It auto-resolves cross-references, manages imports/`using` directives, and handles
language idioms. **One well-formed JSON call replaces dozens of error-prone file writes.**

---

## Tools exposed by the MCP server

There are two MCP servers exposed — `metaengine` (engine) and `metaengine-toolkit`
(workflow tools). The generation API is in `metaengine`.

### `mcp__metaengine__metaengine_initialize`
Returns the AI guide. Optional `language` arg (one of typescript, python, go, csharp, java,
kotlin, groovy, scala, swift, php) for language-specific patterns. Call once at the start
of a generation session if the guide isn't already loaded.

### `mcp__metaengine__generate_code`  ← MAIN TOOL
Semantic code generation for all 11 supported languages. Takes a JSON spec describing
classes/interfaces/enums/etc. and writes files. **See full schema below.**

### `mcp__metaengine__load_spec_from_file`
Same as `generate_code` but loads the spec from a `.json` file path. Use for large specs
to keep AI context lean. Inputs:
- `specFilePath` (required): path to `.json` file (absolute or relative to cwd)
- `outputPath` (optional): override spec's `outputPath`
- `skipExisting` (optional): override spec's `skipExisting`
- `dryRun` (optional): override spec's `dryRun`

### `mcp__metaengine__generate_openapi`
HTTP client from an OpenAPI 3 spec (inline YAML/JSON or URL). Frameworks:
`angular | react | typescript-fetch | go-nethttp | java-spring | python-fastapi |
csharp-httpclient | kotlin-ktor | rust-reqwest | swift-urlsession`. Each framework has its
own options object (e.g. `csharpOptions.namespaceName` is required for C#,
`goOptions` requires `moduleName`+`packageName`, `rustOptions.crateName`, etc.). Supports
`bearerAuth`, `basicAuth`, `customHeaders`, `errorHandling`, `retries`, `timeout`,
`documentation`, `optionsObjectThreshold`, `strictValidation`, `dryRun`,
`skipExisting`, `outputPath`. Provide either `openApiSpec` (inline) OR `openApiSpecUrl`.

### `mcp__metaengine__generate_graphql`
Typed HTTP client from a GraphQL SDL schema (`graphQLSchema` required). Same framework set
as openapi minus python-fastapi alt naming (`python-fastapi`). Supports
`discriminatedUnions`, `documentation`, framework-specific option blocks,
auth/retries/timeout/errorHandling, `dryRun`, `skipExisting`, `outputPath`.

### `mcp__metaengine__generate_protobuf`
Typed HTTP client from `.proto` source (`protoSource` required). Frameworks identical
list to openapi but Python is `python-httpx`. Same auth/options/timeout/error-handling
schema as openapi/graphql.

### `mcp__metaengine__generate_sql`
Typed model classes from SQL DDL (`CREATE TABLE` statements). `ddlSource` + `language`
required. Languages: typescript, csharp, go, python, java, kotlin, groovy, scala, swift,
php, rust. Optional: `generateInterfaces`, `generateNavigationProperties`,
`generateValidationAnnotations`, `initializeProperties`, plus per-language option blocks
(`csharpOptions.namespace`, `goOptions.moduleName` (required),
`javaOptions.packageName` (required), `kotlinOptions.packageName` (required),
`scalaOptions.packageName` (required), `groovyOptions.packageName` (required),
`phpOptions.rootNamespace` (required) + `useStrictTypes`,
`pythonOptions.modelStyle` ('dataclass'|'pydantic'|'plain'), `rustOptions.crateName`).
Standard `dryRun` / `skipExisting` / `outputPath` flags.

---

## CRITICAL RULES — these cause the most failures when violated

### 1. Generate ALL related types in ONE call
`typeIdentifier` references resolve **only within the current batch**. If `UserService`
references `User`, both must be in the same `generate_code` call. Splitting per-domain
breaks the typegraph and silently drops the unresolved property.

### 2. Properties = type declarations. CustomCode = everything else
- `properties[]` → declares a field with a type. NO initialization, NO logic.
- `customCode[]` → methods, initialized fields, decorators with logic.
- **One `customCode` item = exactly one member.** Each block gets automatic newlines
  between blocks in the output.
- Never put methods in properties. Never put uninitialized type declarations in customCode.

### 3. Use `templateRefs` for internal type references inside `customCode` / `properties.type` / decorators
Inline a `$placeholder` token in the code string and add a matching
`templateRefs: [{placeholder: "$user", typeIdentifier: "user"}]` entry. This triggers
import/`using`/namespace resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**Critical in C#**: every internal type reference in customCode MUST use templateRefs,
or `using` directives for cross-namespace types won't be generated. Raw strings like
`IUserRepository` will compile-fail across namespaces.

### 4. NEVER add framework imports to `customImports`
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

| Language   | Auto-imported (NEVER specify in customImports)                                                  |
|------------|-------------------------------------------------------------------------------------------------|
| C#         | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*  |
| Python     | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses                |
| Java       | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*      |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*                              |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more|
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)               |
| Rust       | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde                          |
| Groovy     | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream)    |
| Scala      | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.*        |
| PHP        | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable             |
| TypeScript | (no imports needed — built-in types)                                                            |

Use `customImports` ONLY for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### 5. `templateRefs` are ONLY for internal types
- Internal type (defined in same MCP call) → `typeIdentifier` or `templateRefs`.
- External library type → `customImports`.
- Never mix.

### 6. Constructor parameters auto-create properties (C#, Java, Go, Groovy)
DO NOT also list the same name in `properties[]`. Doing so triggers
`"Sequence contains more than one matching element"`.

```jsonc
// WRONG
"constructorParameters": [{"name": "email", "type": "string"}],
"properties": [{"name": "email", "type": "string"}]   // DUPLICATE

// CORRECT
"constructorParameters": [{"name": "email", "type": "string"}]
// extra non-constructor fields go in properties[]
```

In TypeScript, ctor params auto-become `public` properties as well; same rule applies.

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`
create reusable type references only. They never produce files. Reference them by
their `typeIdentifier` in `properties[]`, `baseClassTypeIdentifier`, etc.

### 8. Reserved words: avoid
Don't use `delete`, `class`, `import`, etc. as property names. Use `remove`, `clazz`,
`importData`.

### 9. `Number` in C# maps to `int`, NOT double
For non-integer numbers in C# use `"type": "decimal"` or `"type": "double"` explicitly.

### 10. TypeScript strips `I` prefix from interface names
`IUserRepository` exports as `UserRepository`. To prevent file-name collisions when
both an interface and its implementing class exist, set `"fileName":
"i-user-repository"` on the interface.

---

## `generate_code` — FULL INPUT SCHEMA

Top-level fields (the ONLY required field is `language`):

| Field | Type | Description |
|---|---|---|
| `language` | enum (required) | `typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php | rust` |
| `packageName` | string | Package/module/namespace. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C#: omit/empty → no namespace declaration (GlobalUsings). |
| `outputPath` | string (default `.`) | Directory to write files into. |
| `skipExisting` | bool (default `true`) | Skip files that already exist (stub pattern). |
| `dryRun` | bool (default `false`) | Preview only — returns generated code in response, no files written. |
| `initialize` | bool (default `false`) | Initialize properties with default values (e.g. `id = ''` instead of `id!: string`). |
| `classes[]` | array | Class definitions (regular + generic templates). |
| `interfaces[]` | array | Interface definitions (regular + generic templates). |
| `enums[]` | array | Enum definitions. |
| `arrayTypes[]` | array | Array type aliases — virtual, no files. |
| `dictionaryTypes[]` | array | Dictionary type aliases — virtual, no files. |
| `concreteGenericClasses[]` | array | `Repository<User>` style references — virtual, no files. |
| `concreteGenericInterfaces[]` | array | `IRepository<User>` style references — virtual, no files. |
| `customFiles[]` | array | Files without class wrapper (type aliases, barrels, util fns). |

### `classes[].*`
| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | UNIQUE id used by other types to reference this one. |
| `path` | string | Subdirectory (e.g. `services/auth`). |
| `fileName` | string | Override file name (no extension). |
| `comment` | string | Doc comment. |
| `isAbstract` | bool | |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class. |
| `interfaceTypeIdentifiers[]` | string[] | typeIdentifiers of implemented interfaces. |
| `genericArguments[]` | array | Makes this a generic template. Each: `{name, constraintTypeIdentifier?, propertyName?, isArrayProperty?}`. `propertyName` creates a field of type `T`; `isArrayProperty=true` makes it `T[]`. |
| `constructorParameters[]` | array | `{name, primitiveType? | type? | typeIdentifier?}`. Auto-creates properties in C#/Java/Go/Groovy/TS — DON'T duplicate in `properties[]`. |
| `properties[]` | array | See property schema below. |
| `customCode[]` | array | `{code, templateRefs?}`. ONE per member. |
| `customImports[]` | array | `{path, types[]}` — external libs only. |
| `decorators[]` | array | `{code, templateRefs?}` — class-level decorators/attributes. |

### `properties[].*`
| Field | Type | Notes |
|---|---|---|
| `name` | string | |
| `primitiveType` | enum | `String | Number | Boolean | Date | Any` (one of three type sources). |
| `typeIdentifier` | string | Reference to another type in same batch (one of three type sources). |
| `type` | string | Raw type expression for complex/external types, e.g. `"Map<string, $resp>"` or `"List<$user>"` (one of three type sources). |
| `templateRefs[]` | array | `{placeholder, typeIdentifier}` — required when `type` contains `$placeholder` tokens. |
| `comment` | string | Doc comment. Use `commentTemplateRefs[]` if comment references types. |
| `commentTemplateRefs[]` | array | Same shape as templateRefs. |
| `decorators[]` | array | Property-level decorators (`@IsEmail()`, `@Required()` etc.). `{code, templateRefs?}`. |
| `isOptional` | bool | C#: emits `string?` (nullable). |
| `isInitializer` | bool | Add default value initialization. |

### `interfaces[].*`
Same shape as `classes[]` minus `isAbstract`, `constructorParameters`, `baseClassTypeIdentifier`.
Has `interfaceTypeIdentifiers[]` for **extends** semantics. For interfaces a class will
implement, put method signatures in `customCode`, NOT as function-typed properties (else
the implementing class duplicates them as fields).

### `enums[].*`
| Field | Type | Notes |
|---|---|---|
| `name` | string | |
| `typeIdentifier` | string | |
| `path` | string | |
| `fileName` | string | |
| `comment` | string | |
| `members[]` | `{name, value:number}` | |

Auto file-name suffix: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### `arrayTypes[].*` (virtual)
| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` (req) | string | Reference id. |
| `elementPrimitiveType` | enum `String|Number|Boolean|Date|Any` | OR... |
| `elementTypeIdentifier` | string | reference to a custom type. |

C#: produces `IEnumerable<T>`. Want `List<T>`? Use a `properties[].type: "List<$user>"` with templateRefs instead.

### `dictionaryTypes[].*` (virtual) — supports all 4 key/value combinations
| Field | Type |
|---|---|
| `typeIdentifier` (req) | string |
| `keyPrimitiveType` | enum `String|Number|Boolean|Date|Any` |
| `keyType` | string literal e.g. `"string"` |
| `keyTypeIdentifier` | string |
| `valuePrimitiveType` | enum |
| `valueTypeIdentifier` | string |

### `concreteGenericClasses[].*` (virtual)
```jsonc
{
  "identifier": "user-repository",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"} /* or {"primitiveType": "String"} */]
}
```
Used as `baseClassTypeIdentifier` or via templateRefs to produce `Repository<User>`.

### `concreteGenericInterfaces[].*` (virtual)
Same shape, for interfaces (`IRepository<User>`).

### `customFiles[].*`
File without class wrapper — perfect for type aliases, barrel exports, utility functions.
| Field | Type | Notes |
|---|---|---|
| `name` | string | File name (no extension). |
| `path` | string | Directory path. |
| `fileName` | string | Override. |
| `identifier` | string | Optional id; lets other files import via `customImports: [{path: "<identifier>"}]`. |
| `customCode[]` | array | One block per export/type alias/function. |
| `customImports[]` | array | |

### `customImports[].*`
```jsonc
{"path": "@angular/core", "types": ["Injectable", "inject"]}
```
For external libraries OR for pulling from another customFile by `identifier`.

### `templateRefs` mechanics
Token: any string starting with `$` (e.g. `$user`, `$petArray`, `$resp`).
Resolution: replaced inline with the resolved type name; triggers automatic
import/using directive emission. Works in `customCode.code`, `properties.type`,
decorator `code`, and `comment`/`commentTemplateRefs`.

---

## Output structure

Each generated file lands at `<outputPath>/<class.path>/<filename>.<ext>` where
extension follows the `language`. Filenames default to kebab-case of the class name
(TS, Python, Go) or PascalCase (C#, Java, Kotlin); override with `fileName`. Enums get
language-specific suffixes (`.enum.ts` in TS, none in C#).

When `dryRun: true`, no files are written; the file contents are returned in the MCP
response so you can review them without touching disk.

When `skipExisting: true` (default), files that already exist are NOT overwritten —
useful for the "stub pattern" where MetaEngine creates an initial file once, and you
edit it freely afterward without subsequent regenerations clobbering changes.

---

## Pattern Recipes (copy/adapt)

### Basic interfaces with cross-references
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
→ Two files with auto imports.

### Class with inheritance + method
```jsonc
{
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}],
     "customCode": [{"code": "getDisplayName(): string { return this.email; }"}]}
  ]
}
```

### Generic class + concrete generic + extending class
```jsonc
{
  "classes": [
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{
       "name": "T", "constraintTypeIdentifier": "base-entity",
       "propertyName": "items", "isArrayProperty": true
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
→ `UserRepository extends Repository<User>` with all imports correct.

### Array & dictionary types
```jsonc
{
  "arrayTypes": [
    {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
    {"typeIdentifier": "user-names", "keyTypeIdentifier": "user", "valuePrimitiveType": "String"},
    {"typeIdentifier": "user-meta", "keyTypeIdentifier": "user", "valueTypeIdentifier": "metadata"}
  ]
}
```
TS output uses `Array<T>` and `Record<K,V>`. Reference via `typeIdentifier` in property.

### Enum + class consuming enum
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

### Service with external DI (NestJS / Angular pattern)
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
      {"code": "private baseUrl = '/api/users';"},
      {"code": "getUsers(): Observable<$list> { return this.http.get<$list>(this.baseUrl); }",
       "templateRefs": [{"placeholder": "$list", "typeIdentifier": "user-array"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}]
}
```

### customFiles for type aliases + barrels
```jsonc
{
  "customFiles": [{
    "name": "types", "path": "shared", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Email = string;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"},
      {"code": "export type ResultSet<T> = { data: T[]; total: number; page: number; };"}
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers",
    "customImports": [{"path": "shared-types", "types": ["UserId", "Status"]}],
    "customCode": [{"code": "static format(id: UserId, s: Status): string { return `${id}:${s}`; }"}]
  }]
}
```

### Interface that a class will implement
For interfaces destined to be `implements`/`:`, define methods in `customCode`, NOT as
function-typed properties (else implementer duplicates them as fields).
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

### Constructor parameters — RIGHT vs WRONG
```jsonc
// WRONG (TS/C#/Java/Go/Groovy) → "Sequence contains more than one matching element"
{
  "constructorParameters": [{"name": "email", "type": "string"}],
  "properties": [{"name": "email", "type": "string"}, {"name": "createdAt", "primitiveType": "Date"}]
}

// CORRECT — only EXTRA fields in properties
{
  "constructorParameters": [{"name": "email", "type": "string"}, {"name": "status", "typeIdentifier": "status"}],
  "properties": [{"name": "createdAt", "primitiveType": "Date"}]
}
```
TS output:
```typescript
export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

---

## Language-specific notes

### TypeScript
- `I` prefix stripped from interface names → exports as plain name. Use `fileName` to
  control file name when colliding with implementing class.
- Primitives map: `Number→number`, `String→string`, `Boolean→boolean`, `Date→Date`, `Any→unknown`.
- Auto-indents customCode newlines.
- Decorators supported directly.
- Constructor parameters auto-become `public` properties.

### C#
- `I` prefix preserved on interface names.
- `Number → int` (NOT double). For non-integer use `"type": "decimal"` or `"type": "double"` explicitly.
- `packageName` sets the namespace. Omit/empty → no namespace declaration (GlobalUsings pattern).
- Interface properties → `{ get; }`. Class properties → `{ get; set; }`.
- arrayTypes → `IEnumerable<T>`. For mutable `List<T>`, use property `type: "List<$user>"` with templateRefs.
- `isOptional` → `string?` (nullable reference type).
- Every internal type ref in customCode MUST use templateRefs (else missing usings).

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode (no auto-indent).
- typing imports automatic.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions in customCode.
- Exported names must be PascalCase.

### Java / Kotlin / Groovy / Scala
- `packageName` defaults to `com.metaengine.generated` if omitted.
- Constructor parameters auto-create fields (Java/Groovy); Kotlin uses primary
  constructors implicitly.

### Swift / Rust / PHP
- Foundation/std/DateTime auto-imported respectively (see table above).

---

## Common Mistakes Checklist

1. Referencing a `typeIdentifier` not present in the batch → property silently dropped. **Verify every reference.**
2. Putting interface method signatures as function-typed properties → implementer duplicates them. **Use `customCode` for interface methods.**
3. Writing internal type names as raw strings in customCode (`"private repo: IUserRepository"`). **Use `$placeholder` + templateRefs.**
4. Using `arrayTypes` in C# when `List<T>` is required (`arrayTypes` → `IEnumerable<T>`). **Use property `type: "List<$user>"` + templateRefs.**
5. Adding framework types to `customImports` (`System.*`, `typing.*`, `java.util.*`). **Let MetaEngine handle them.**
6. Duplicating constructor parameters in `properties[]` (C#/Java/Go/Groovy/TS). **Constructor params auto-become properties.**
7. Reserved words as property names (`delete`, `class`, `import`). **Use `remove`, `clazz`, `importData`.**
8. Generating related types in separate calls. **Always batch — cross-file imports only resolve within one call.**
9. Expecting `Number → double` in C#. **It's `int`. Use explicit `type: "decimal"` / `"double"` for floats.**
10. TypeScript interface (`I`-prefixed) collides with implementing class file. **Set `fileName: "i-user-repository"` on interface.**

---

## Workflow guidance

1. **Analyze first**: identify ALL types and relationships before any tool call. Map cross-references.
2. **One batched call**: assemble the entire spec — classes, interfaces, enums, arrayTypes,
   dictionaryTypes, concreteGenericClasses, customFiles — into a single `generate_code` call.
3. **Use `dryRun: true` first** if uncertain; review returned files; then call again with `dryRun: false`.
4. **For very large specs**: write spec to a `.json` file and call `load_spec_from_file` to
   keep AI context lean.
5. **For HTTP clients from existing specs**: prefer `generate_openapi`/`generate_graphql`/
   `generate_protobuf` over hand-rolled `generate_code` — they handle auth/retries/timeout/
   error-handling for you.
6. **For DB models**: prefer `generate_sql` from DDL.

---

## Quick-glance type-source rule (properties / constructor params)

A property/parameter declares its type via EXACTLY ONE of:
- `primitiveType` — for `String|Number|Boolean|Date|Any`
- `typeIdentifier` — to reference another type in the same batch
- `type` — raw string for complex/external (use templateRefs if it contains `$tokens`)

Never combine. Never omit all three.

---

## Final reminders

- The `generate_code` tool's only required field is `language`. Everything else is optional.
- Empty arrays for `classes`, `interfaces`, etc. are fine — produce zero files.
- `dryRun: true` is the safest exploratory mode — no disk writes, full output in response.
- `skipExisting: true` (default) prevents accidental clobbering of edited files.
- Always re-read these critical rules before assembling a spec; the failures listed above
  are the ones that occur most often in practice.
