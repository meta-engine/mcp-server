# MetaEngine MCP — Knowledge Brief (TypeScript-focused)

## What MetaEngine is

MetaEngine is a **semantic code generator** exposed via MCP. You describe types, relationships, and methods as a single structured JSON document; MetaEngine emits compilable, correctly-imported source files. Unlike templating, it resolves cross-references, manages imports, and applies language idioms automatically.

The competitive advantage for an AI caller: **one well-formed JSON call replaces dozens of file writes** that would otherwise each have to get import paths, naming conventions, and cross-references right.

Supported languages: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` (the `language` enum on `generate_code`).

---

## MCP tools exposed

### 1. `mcp__metaengine__generate_code` — the core tool

Takes a JSON spec and writes source files. Full schema below.

### 2. `mcp__metaengine__load_spec_from_file`

Reads the same spec shape from a `.json` file path. Useful for very large specs where embedding the JSON inline would bloat the call. Parameters:

- `specFilePath` (required, string) — absolute or relative path to a `.json` file shaped like `generate_code` input.
- `outputPath` (optional, string) — overrides spec's outputPath.
- `skipExisting` (optional, bool) — overrides spec.
- `dryRun` (optional, bool) — overrides spec.

### 3. `mcp__metaengine__metaengine_initialize`

Returns the AI guide. Parameter: `language` (optional enum). Call once for orientation.

### 4. Spec converters (single-call, do NOT take the same JSON shape — they take the source spec)

- **`mcp__metaengine__generate_openapi`** — generates HTTP clients from OpenAPI YAML/JSON or URL, for `angular | react | typescript-fetch | go-nethttp | java-spring | python-fastapi | csharp-httpclient | kotlin-ktor | rust-reqwest | swift-urlsession`. Inputs: `framework` (required), `openApiSpec` or `openApiSpecUrl` (one required), per-framework option blocks (e.g. `csharpOptions.namespaceName`, `goOptions.moduleName/packageName`, `javaSpringOptions.packageName`, `kotlinOptions.packageName`, `rustOptions.crateName`, `fetchOptions.baseUrlEnvVar`, etc.), plus `bearerAuth`, `basicAuth`, `customHeaders`, `errorHandling`, `retries`, `timeout`, `documentation`, `strictValidation`, `optionsObjectThreshold`, `outputPath`, `skipExisting`, `dryRun`.
- **`mcp__metaengine__generate_graphql`** — same idea from GraphQL SDL. Inputs: `framework` (same enum minus `python-fastapi`, plus `python-fastapi`), `graphQLSchema` (required), `discriminatedUnions`, plus the same auth/error/retry/timeout/per-framework option blocks.
- **`mcp__metaengine__generate_protobuf`** — from `.proto` source. Inputs: `framework` (note: `python-httpx` instead of `python-fastapi`), `protoSource`.
- **`mcp__metaengine__generate_sql`** — DDL → typed models. Inputs: `language` (full language enum), `ddlSource` (required), plus `generateInterfaces`, `generateNavigationProperties`, `generateValidationAnnotations`, `initializeProperties`, and per-language option blocks (e.g. `csharpOptions.namespace`, `javaOptions.packageName`, `goOptions.moduleName`, `pythonOptions.modelStyle: dataclass|pydantic|plain`, `phpOptions.rootNamespace/useStrictTypes`, `rustOptions.crateName`).

For a benchmark scenario where the input is an arbitrary domain spec (not OpenAPI/GraphQL/proto/DDL), the right tool is **`generate_code`**.

---

## `generate_code` — full input schema

Top-level fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum: `typescript \| python \| go \| csharp \| java \| kotlin \| groovy \| scala \| swift \| php \| rust` | **yes** | |
| `outputPath` | string | no | default `"."` — directory where files are written |
| `packageName` | string | no | namespace/module/package. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C# without it = no namespace declaration (GlobalUsings-friendly). |
| `initialize` | bool | no | initialize properties with default values (`= ''`, `= 0`, etc. in TS) |
| `skipExisting` | bool | no | default `true`. When true, never overwrite existing files (stub pattern). |
| `dryRun` | bool | no | default `false`. When true, returns generated code in response, writes nothing. |
| `interfaces` | array | no | interface definitions (regular & generic templates) |
| `classes` | array | no | class definitions (regular & generic templates) |
| `enums` | array | no | enum definitions |
| `customFiles` | array | no | files without a class wrapper (type aliases, barrel exports, free functions) |
| `arrayTypes` | array | no | **virtual** — declares reusable array references; no files emitted |
| `dictionaryTypes` | array | no | **virtual** — declares reusable dictionary references; no files emitted |
| `concreteGenericClasses` | array | no | **virtual** — concrete generic class refs like `Repository<User>` |
| `concreteGenericInterfaces` | array | no | **virtual** — concrete generic interface refs like `IRepository<User>` |

### `interfaces[]` and `classes[]` items

Common fields:

- `name` (string) — type name (e.g. `User`, `IUserRepository`).
- `typeIdentifier` (string) — **unique stable id** used for cross-referencing within this batch. **All references between types use this, never the `name`.** Convention: kebab-case (`user`, `user-repo`, `base-entity`).
- `path` (string) — directory under `outputPath` (e.g. `"models"`, `"services/auth"`).
- `fileName` (string) — override the generated file name (without extension).
- `comment` (string) — doc comment for the type.
- `properties` (array) — type declarations. **No methods, no initialized fields here.**
- `customCode` (array) — methods, initialized fields, every member with logic. **One item = exactly one member.**
- `customImports` (array) — external library imports (NEVER framework/stdlib).
- `decorators` (array) — class/interface-level decorators (`@Injectable`, `[ApiController]`, etc.).
- `genericArguments` (array) — makes this a generic template (`Repository<T>`).
- `interfaceTypeIdentifiers` (array of typeIdentifier strings) — interfaces this type implements/extends.
- `baseClassTypeIdentifier` (string, classes only) — base class to extend (can point to a `concreteGenericClasses` identifier).
- `isAbstract` (bool, classes only).
- `constructorParameters` (array, classes only) — auto-create properties in C#/Java/Go/Groovy. In TypeScript they emit `public foo: T` constructor params.

#### `properties[]` item

| Field | Notes |
|---|---|
| `name` | property name |
| `primitiveType` | enum: `String \| Number \| Boolean \| Date \| Any` — for primitive fields |
| `typeIdentifier` | reference another type from the same batch (a class, interface, enum, arrayType, dictionaryType, concreteGenericClass, concreteGenericInterface) |
| `type` | raw string for complex/external types (`"List<User>"`, `"Promise<string>"`); pair with `templateRefs` to inject internal type names |
| `templateRefs` | array of `{placeholder, typeIdentifier}` to substitute `$placeholder` inside `type` and trigger import resolution |
| `isOptional` | bool — emits `string?` (C#), `string \| undefined` (TS), etc. |
| `isInitializer` | bool — emit a default initializer |
| `comment` | doc comment |
| `commentTemplateRefs` | template refs valid inside the comment |
| `decorators` | property-level decorators (`@IsEmail()`, `@Required()`, `@Column()`, etc.) — each `{code, templateRefs}` |

Use **exactly one** of `primitiveType` / `typeIdentifier` / `type` per property.

#### `customCode[]` item

```jsonc
{ "code": "<one member, optionally with $placeholders>",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}, ...] }
```

- One method/initialized-field per item. MetaEngine inserts blank lines between items automatically.
- Use `$placeholder` syntax for **every internal type reference**. The placeholder is replaced with the resolved type name AND triggers automatic import generation.
- Raw type names (`User`, `IUserRepository`) inside `code` strings will compile-fail across files in C#, and across modules/files in any language that requires explicit imports — always use templateRefs for in-batch types.
- For Python: explicitly indent (4 spaces) after `\n` inside the code string. For TS: indentation is auto-applied.

#### `decorators[]` item

```jsonc
{ "code": "@Injectable({ providedIn: 'root' })", "templateRefs": [...] }
```

#### `customImports[]` item

```jsonc
{ "path": "@angular/core", "types": ["Injectable", "inject"] }
```

- `path` only — for path-based imports without named symbols (e.g., a customFile barrel via its `identifier`).
- **Never** include framework/stdlib paths here (see auto-import table below).

#### `genericArguments[]` item

```jsonc
{ "name": "T",
  "constraintTypeIdentifier": "base-entity",
  "propertyName": "items",
  "isArrayProperty": true }
```

- `name` — generic param (`T`, `K`, `V`).
- `constraintTypeIdentifier` — `where T : BaseEntity` / `T extends BaseEntity` constraint.
- `propertyName` — auto-creates a property of type `T` with this name.
- `isArrayProperty` — when true, the auto-property is `T[]` instead of `T`.

### `enums[]` item

```jsonc
{ "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "fileName": "order-status",       // optional
  "path": "models",                  // optional
  "comment": "...",                  // optional
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2}
  ]
}
```

Enum filenames are auto-suffixed per language: TS → `order-status.enum.ts`; C# → `OrderStatus.cs`.

### `customFiles[]` item — for type aliases, barrel exports, free functions

```jsonc
{ "name": "types",                   // file base name
  "path": "shared",                  // directory under outputPath
  "fileName": "types",               // optional override
  "identifier": "shared-types",      // makes the file referenceable from customImports.path
  "customCode": [{"code": "...", "templateRefs": [...]}],
  "customImports": [{"path": "...", "types": [...]}]
}
```

- No class/interface wrapper — code is emitted top-level inside the file.
- The `identifier` lets other types reference this file via `customImports: [{path: "shared-types"}]`, which auto-resolves to a relative import path.

### Virtual types (no files emitted, only used as references)

#### `arrayTypes[]`
```jsonc
{ "typeIdentifier": "user-list",
  "elementTypeIdentifier": "user" }      // OR
{ "typeIdentifier": "string-array",
  "elementPrimitiveType": "String" }     // enum: String|Number|Boolean|Date|Any
```
TS emits `Array<User>`. **C# emits `IEnumerable<T>`** — for mutable `List<T>`, skip arrayTypes and use `"type": "List<$user>"` with templateRefs instead.

#### `dictionaryTypes[]`
All four key/value combinations of primitive vs custom:
```jsonc
{ "typeIdentifier": "scores",
  "keyPrimitiveType": "String",
  "valuePrimitiveType": "Number" }

{ "typeIdentifier": "user-lookup",
  "keyPrimitiveType": "String",
  "valueTypeIdentifier": "user" }

{ "typeIdentifier": "user-names",
  "keyTypeIdentifier": "user",
  "valuePrimitiveType": "String" }

{ "typeIdentifier": "user-meta",
  "keyTypeIdentifier": "user",
  "valueTypeIdentifier": "metadata" }
```
TS emits `Record<K, V>`. There is also a `keyType` string-literal escape hatch (`"keyType": "string"`).

#### `concreteGenericClasses[]` and `concreteGenericInterfaces[]`
```jsonc
{ "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}] }
```
Creates a virtual `Repository<User>` reference. Use as `baseClassTypeIdentifier` or in `templateRefs`/`typeIdentifier` slots. Generic args may be `{primitiveType}` or `{typeIdentifier}`.

---

## Critical rules (causes of most failures, learn cold)

### Rule 1 — ONE call with the FULL spec

`typeIdentifier` references resolve **only within the current batch**. Splitting domains across multiple `generate_code` calls breaks cross-references and imports. Generate everything related in one invocation.

### Rule 2 — `properties` vs `customCode` is strict

- `properties[]` = bare type declarations only (no `=`, no body, no logic).
- `customCode[]` = methods, initialized fields, anything with content. **One item = one member.**

Putting a method in `properties` (e.g. `"type": "() => Promise<User[]>"`) on an interface causes the implementing class to duplicate the field as a property declaration alongside its real method. Use `customCode` for interface method signatures.

### Rule 3 — `templateRefs` are MANDATORY for internal type references inside `customCode`/`type` strings

Plain type names like `IUserRepository` inside a `code` string will NOT trigger import generation. Always use `$placeholder` + `templateRefs`. This is non-negotiable in C# (will compile-fail across namespaces), and required in TS for cross-file imports.

### Rule 4 — `customImports` is for EXTERNAL libraries only

MetaEngine auto-imports stdlib/framework types. Adding them manually creates duplicate-import errors. Auto-imported sets:

| Language | Auto-imported (do NOT specify in customImports) |
|---|---|
| C# | `System.*`, `System.Collections.Generic`, `System.Linq`, `System.Threading.Tasks`, `System.Text`, `System.IO`, `System.Net.Http`, `System.ComponentModel.DataAnnotations`, `Microsoft.Extensions.*` |
| Python | `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, etc. |
| Swift | `Foundation` (Date, UUID, URL, Decimal, URLSession, JSONEncoder/Decoder, etc.) |
| Rust | `std::collections::{HashMap, HashSet}`, `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream) |
| Scala | `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | (no imports needed — built-in types) |

`customImports` is correct for: `@angular/core`, `@nestjs/common`, `rxjs`, `FluentValidation`, in-batch `customFile` identifiers, etc.

### Rule 5 — `templateRefs` are ONLY for in-batch internal types

External library types → `customImports`. In-batch types → `typeIdentifier` (in properties) or `templateRefs` (in code/type/comment strings). Never mix.

### Rule 6 — Constructor parameters auto-create properties (C#/Java/Go/Groovy)

```jsonc
// WRONG (duplicate -> "Sequence contains more than one matching element")
"constructorParameters": [{"name": "email", "type": "string"}],
"properties":            [{"name": "email", "type": "string"}]

// RIGHT
"constructorParameters": [{"name": "email", "type": "string"}],
"properties":            [{"name": "createdAt", "primitiveType": "Date"}]  // additional only
```

In TypeScript, constructor parameters become `public email: string` constructor params (which are also class fields). Same rule: don't duplicate them in `properties`.

### Rule 7 — Virtual types never produce files

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reference factories. They appear via their `typeIdentifier`/`identifier` in other types' `properties`/`customCode`/`baseClassTypeIdentifier`. Listing one without referencing it is a no-op.

### Rule 8 — Reserved words

Don't use `delete`, `class`, `import`, `function`, `default`, etc. as property names — use `remove`, `clazz`, `importData`, etc.

### Rule 9 — Interface method signatures go in `customCode`, not `properties`

Function-typed properties on an interface become **fields** of the implementing class, duplicating real methods. Always:
```jsonc
"customCode": [
  {"code": "findById(id: string): Promise<$user | null>;",
   "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
]
```
(The trailing `;` is required for TS/C# interface signatures.)

### Rule 10 — `Number` is `int` in C# but `number` in TypeScript

Type-mapping cheat-sheet for `primitiveType`:

| primitiveType | TypeScript | C# | Python | Java | Go | Rust |
|---|---|---|---|---|---|---|
| `String` | `string` | `string` | `str` | `String` | `string` | `String` |
| `Number` | `number` | `int` | `int` | `int`/`Integer` | `int` | `i32` |
| `Boolean` | `boolean` | `bool` | `bool` | `boolean` | `bool` | `bool` |
| `Date` | `Date` | `DateTime` | `datetime` | `LocalDateTime` | `time.Time` | `DateTime<Utc>` |
| `Any` | `unknown` | `object` | `Any` | `Object` | `interface{}` | `serde_json::Value` |

For non-integer C# numbers use `"type": "decimal"` or `"type": "double"`. For TS, `Number` already maps to the right thing.

---

## TypeScript-specific behavior

- MetaEngine **strips the `I` prefix from interface names** when emitting (file content): `IUserRepository` → exported as `UserRepository`. To prevent file-name collision with an implementing class, set `"fileName": "i-user-repository"` on the interface.
- File names are **kebab-case** based on the type's `name` (or override with `fileName`). Example: `OrderStatus` → `order-status.ts`; enum gets `.enum.ts` suffix.
- Property defaults when `initialize: true` (or property `isInitializer: true`):
  - `String` → `= ''`
  - `Number` → `= 0`
  - `Boolean` → `= false`
  - `Date` → `= new Date()`
  - arrays → `= new Array<T>()`
  - dictionaries → `= {}`
  - Otherwise the engine emits `!:` definite-assignment (e.g. `id!: string`).
- `isOptional: true` → `field?: type`.
- `customCode` newlines auto-indent; emit one method per item.
- Decorators emit verbatim (`@Injectable({ providedIn: 'root' })`).
- For `List<T>`-style mutable collections in TS, `arrayTypes` is fine (emits `Array<T>`).

---

## Output structure (what you get back)

`generate_code` writes files under `outputPath`, namespaced by each type's `path`. For the spec
```jsonc
{ "language": "typescript", "outputPath": "src",
  "classes": [{"name": "PetService", "path": "services", ...}],
  "enums":   [{"name": "PetKind", "path": "models", ...}] }
```
files land at `src/services/pet-service.ts` and `src/models/pet-kind.enum.ts`.

Response: a summary of files written (paths + sizes). With `dryRun: true`, the response includes the **full file contents inline** instead of writing to disk — useful for previewing.

`skipExisting: true` (default) means re-runs won't overwrite. Set `false` to overwrite, or pre-delete the directory.

---

## Pattern playbook (copy-paste-ready shapes)

### Cross-referenced models (interface → interface)
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

### Class with inheritance + method
```jsonc
{
  "language": "typescript",
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

### Generic repository + concrete instance
```jsonc
{
  "language": "typescript",
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{
       "name": "T", "constraintTypeIdentifier": "base-entity",
       "propertyName": "items", "isArrayProperty": true
     }],
     "customCode": [
       {"code": "add(item: T): void { this.items.push(item); }"},
       {"code": "getAll(): T[] { return this.items; }"},
       {"code": "findById(id: string): T | undefined { return this.items.find(i => i.id === id); }"}
     ]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}]},
    {"name": "UserController", "typeIdentifier": "controller",
     "customCode": [{
       "code": "private repo: $userRepo = new Repository<User>();",
       "templateRefs": [{"placeholder": "$userRepo", "typeIdentifier": "user-repository"}]
     }]}
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repository",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{"typeIdentifier": "user"}]
  }]
}
```

### Service with external DI (Angular/NestJS pattern)
```jsonc
{
  "language": "typescript",
  "classes": [
    {"name": "Pet", "typeIdentifier": "pet",
     "properties": [{"name": "name", "primitiveType": "String"}]},
    {"name": "PetService", "typeIdentifier": "pet-service", "path": "services",
     "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
     "customImports": [
       {"path": "@nestjs/common",      "types": ["Injectable", "inject"]},
       {"path": "@nestjs/common/http", "types": ["HttpClient"]},
       {"path": "rxjs",                "types": ["Observable"]}
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
     ]}
  ],
  "arrayTypes": [{"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}]
}
```

### Type aliases via `customFiles` + cross-file import
```jsonc
{
  "language": "typescript",
  "customFiles": [{
    "name": "types", "path": "utils", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"},
      {"code": "export type ResultSet<T> = { data: T[]; total: number; page: number; };"}
    ]
  }],
  "classes": [{
    "name": "UserService", "typeIdentifier": "user-service", "path": "services",
    "customImports": [{"path": "../utils/types", "types": ["UserId", "Status", "ResultSet"]}],
    "customCode": [
      {"code": "async getUser(id: UserId): Promise<User> { return null as any; }"},
      {"code": "updateStatus(id: UserId, status: Status): void { }"}
    ]
  }]
}
```

### Enum + class that uses it
```jsonc
{
  "language": "typescript",
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [
      {"name": "Pending", "value": 0},
      {"name": "Shipped", "value": 2}
    ]
  }],
  "classes": [{
    "name": "Order", "typeIdentifier": "order",
    "properties": [{"name": "status", "typeIdentifier": "order-status"}],
    "customCode": [{
      "code": "updateStatus(s: $status): void { this.status = s; }",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]
  }]
}
```

### Interface that a class implements
```jsonc
{
  "language": "typescript",
  "interfaces": [{
    "name": "IUserRepository", "typeIdentifier": "user-repo",
    "fileName": "i-user-repository",
    "customCode": [
      {"code": "findAll(): Promise<$user[]>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "findById(id: string): Promise<$user | null>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }],
  "classes": [
    {"name": "User", "typeIdentifier": "user",
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "UserRepository", "typeIdentifier": "user-repo-impl",
     "interfaceTypeIdentifiers": ["user-repo"],
     "customCode": [
       {"code": "async findAll(): Promise<$user[]> { return []; }",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
       {"code": "async findById(id: string): Promise<$user | null> { return null; }",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
     ]}
  ]
}
```

---

## Common mistake checklist (verify before calling)

1. ✅ Every `typeIdentifier` referenced anywhere is **defined** somewhere in this same call. Unknown refs are silently dropped (the property disappears).
2. ✅ No internal type names appear as raw strings inside `customCode.code` — they all use `$placeholder` with `templateRefs`.
3. ✅ `properties[]` contains no methods and no initialized fields.
4. ✅ `customImports` contains zero stdlib/framework paths (see auto-import table).
5. ✅ Constructor parameters are not duplicated in `properties` (C#/Java/Go/Groovy/TS).
6. ✅ For TypeScript, `I`-prefixed interfaces with implementing classes have explicit `fileName` to avoid file collisions.
7. ✅ All related types (cross-references, base classes, interfaces, generic args) are in the **same** call.
8. ✅ Interface method signatures live in `customCode` (with trailing `;` for TS/C#), not as function-typed `properties`.
9. ✅ Reserved words (`delete`, `class`, `import`) are not used as property names.
10. ✅ For non-integer C# numbers, use `"type": "decimal"`/`"double"` not `primitiveType: "Number"`.

---

## Calling pattern recap

For a benchmark scenario where you receive a domain spec (entities, services, methods) and must produce a TypeScript codebase:

1. Plan the full type graph: list every entity/interface/class/enum, decide their `typeIdentifier` slugs, identify cross-references.
2. Build **one** JSON object — `language: "typescript"`, all `interfaces`, `classes`, `enums`, `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses` populated.
3. For every method, write it as a single `customCode` item with `templateRefs` for every internal-type mention.
4. Set `outputPath` to the destination directory and `skipExisting: false` if you want clean re-runs.
5. Call `mcp__metaengine__generate_code` **once**.
6. Optionally call once more with `dryRun: true` first to inspect the file list before committing.

The single-call invariant is the most important property: do NOT split a related domain across multiple calls — cross-file imports only resolve within a single batch.
