# MetaEngine MCP — Knowledge Brief (TypeScript focus)

MetaEngine is a semantic code generator exposed over MCP. You describe types,
relationships, and methods as structured JSON and the engine emits compilable
files with all imports/cross-references resolved. For TypeScript it produces
`.ts` files with `import { … } from './…';` statements wired automatically.

## Tools exposed by `metaengine` MCP server

- `mcp__metaengine__metaengine_initialize` — returns the canonical guide. Optional `language` parameter (`"typescript"`, `"python"`, `"go"`, `"csharp"`, `"java"`, `"kotlin"`, `"groovy"`, `"scala"`, `"swift"`, `"php"`).
- `mcp__metaengine__generate_code` — the workhorse. Takes a structured JSON spec and writes source files. Schema fully described below.
- `mcp__metaengine__load_spec_from_file` — same as `generate_code` but reads the JSON spec from a file path. Args: `specFilePath` (required), `outputPath`, `skipExisting`, `dryRun` (each overrides what's in the file).
- `mcp__metaengine__generate_openapi` — generates an HTTP client from an OpenAPI spec for one of: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession`. Spec is provided inline (`openApiSpec`) or by URL (`openApiSpecUrl`). Per-framework options object (e.g. `fetchOptions`, `csharpOptions.namespaceName`, `javaSpringOptions.packageName`). Auth/header/retry/timeout/error-handling configurable.
- `mcp__metaengine__generate_graphql` — generates a typed client from a GraphQL SDL string (`graphQLSchema`) for the same set of frameworks (minus `python-fastapi`; uses `python-fastapi` here too actually).
- `mcp__metaengine__generate_protobuf` — generates a typed client from `.proto` source (`protoSource`) for similar frameworks (Python is `python-httpx` here).
- `mcp__metaengine__generate_sql` — generates typed model classes from SQL DDL (`ddlSource`) for `typescript`, `csharp`, `go`, `python`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`. Optional flags: `generateInterfaces`, `generateNavigationProperties`, `generateValidationAnnotations`, `initializeProperties`. Per-language options (Python `modelStyle`: `dataclass`/`pydantic`/`plain`).

For semantic code generation in TypeScript, **use `generate_code`** with a single comprehensive call.

---

## Cardinal rules (read first — these cause the most failures)

### 1. ONE call with the full spec
`typeIdentifier` references only resolve **within the same `generate_code` call**. If `UserService` references `User`, both must be in the same call. Splitting per domain breaks the type graph and silently drops references.

### 2. `properties[]` = type declarations. `customCode[]` = everything else.
- `properties[]` declares fields with **type only** (no initializer, no logic).
- `customCode[]` contains methods, initialized fields, and any code with logic. **One `customCode` item = exactly one member.** Auto-newlines between blocks.

### 3. Use `templateRefs` for internal types in `customCode` (and complex `type` strings)
When custom code references a type generated in the same batch, write `$placeholder` in the code and add a `templateRefs` entry mapping it to a `typeIdentifier`. This is what triggers automatic import resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

Without `templateRefs`, the import won't be generated. (For C# this is critical for cross-namespace `using` directives. TypeScript still needs it for the `import` statement.)

### 4. NEVER add framework imports to `customImports`
Standard library types are auto-imported. For TypeScript: nothing needs to be imported (built-ins). Only use `customImports` for **external libraries** (`@angular/core`, `rxjs`, `@nestjs/common`, etc.).

Per-language auto-imports:
| Language   | Auto-imported (NEVER specify)                                                                    |
|------------|--------------------------------------------------------------------------------------------------|
| C#         | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*    |
| Python     | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses                 |
| Java       | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*       |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*                                |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more  |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, …)                   |
| Rust       | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde                           |
| Groovy     | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream)      |
| Scala      | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.*         |
| PHP        | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable              |
| TypeScript | (no imports needed — built-in types)                                                             |

### 5. `templateRefs` is ONLY for internal (same-batch) types
External library types must use `customImports`. If it's in the same MCP call → `typeIdentifier`/`templateRefs`. If it's an external library → `customImports`. Never mix.

### 6. Constructor parameters auto-create properties
In **C#, Java, Go, Groovy, AND TypeScript** (because of `constructor(public x: …)` syntax) the engine auto-promotes constructor parameters to properties. **Do NOT also list them in `properties[]`** — duplicating triggers `"Sequence contains more than one matching element"`. Put only *additional* (non-constructor) fields in `properties[]`.

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references only — never files. Reference them via their `typeIdentifier` from `properties` or `templateRefs`.

### 8. Don't reference a `typeIdentifier` that doesn't exist in the batch
If you do, the property is silently dropped. Cross-check every reference before submitting.

### 9. Reserved-word property names are dangerous
Don't name properties `delete`, `class`, `import`. Use `remove`, `clazz`, `importData`.

### 10. Interface methods that will be `implements`-ed → put in `customCode`, NOT as function-typed properties
Otherwise the implementing class duplicates them as property declarations.

---

## `generate_code` — full input schema

Top-level fields:

| Field | Type | Notes |
|---|---|---|
| `language` | string (required) | One of: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`. |
| `outputPath` | string | Default `"."`. Where files are written. |
| `packageName` | string | Namespace/package. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C#: omit/empty → no namespace declaration (GlobalUsings). TypeScript: usually omit. |
| `skipExisting` | boolean | Default `true`. If `true`, files that already exist are not overwritten. |
| `dryRun` | boolean | Default `false`. If `true`, returns generated source in the response without writing to disk. **Use for previewing.** |
| `initialize` | boolean | Default `false`. If `true`, properties get default-value initialization (TypeScript: `id = ''` instead of `id!: string`). |
| `classes[]` | array | See class schema below. |
| `interfaces[]` | array | See interface schema below. |
| `enums[]` | array | See enum schema below. |
| `arrayTypes[]` | array | Virtual; reusable array type definitions. |
| `dictionaryTypes[]` | array | Virtual; reusable map/dict type definitions. |
| `concreteGenericClasses[]` | array | Virtual; concrete generic class instantiations like `Repository<User>`. |
| `concreteGenericInterfaces[]` | array | Virtual; concrete generic interface instantiations. |
| `customFiles[]` | array | Files without a class wrapper — type aliases, barrel exports, utility code. |

### `classes[]` — class definition

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | Unique identifier used for cross-references. Convention: kebab-case. |
| `path` | string | Subdirectory (e.g. `"models"`, `"services/auth"`). |
| `fileName` | string | Override file name (without extension). |
| `comment` | string | Doc comment for the class. |
| `isAbstract` | boolean | Whether the class is abstract. |
| `baseClassTypeIdentifier` | string | `typeIdentifier` of base class (or of a `concreteGenericClasses` entry to extend `Repository<User>` etc.). |
| `interfaceTypeIdentifiers` | string[] | List of interface `typeIdentifier`s to implement. |
| `genericArguments[]` | array | Makes the class a generic template (`Repository<T>`). Each entry: `name` (e.g. `"T"`), optional `constraintTypeIdentifier` (`extends BaseEntity`), optional `propertyName` + `isArrayProperty` (auto-creates `items: T[]`). |
| `constructorParameters[]` | array | Constructor parameters. Each entry: `name`, plus one of `primitiveType` (`String`/`Number`/`Boolean`/`Date`/`Any`), `typeIdentifier`, or `type` (raw string). **Auto-promoted to properties.** |
| `properties[]` | array | Field declarations. See property schema below. (Don't duplicate constructor params.) |
| `customCode[]` | array | Methods and initialized fields. Each entry: `code` (string) + optional `templateRefs[]` (each: `placeholder`, `typeIdentifier`). |
| `decorators[]` | array | Class decorators. Each entry: `code` + optional `templateRefs[]`. |
| `customImports[]` | array | External-library imports only. Each entry: `path` (e.g. `"@angular/core"`) + `types[]` (e.g. `["Injectable", "inject"]`). For TypeScript, `types` may be omitted for default imports/identifier-only references. |

### Property schema (used in `classes[].properties` and `interfaces[].properties`)

| Field | Type | Notes |
|---|---|---|
| `name` | string | Property name. |
| `primitiveType` | string | One of: `String`, `Number`, `Boolean`, `Date`, `Any`. (TypeScript: `Number`→`number`, `String`→`string`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`.) |
| `typeIdentifier` | string | Reference to a type generated in this same batch (class/interface/enum/arrayType/dictionaryType/concreteGenericClass). |
| `type` | string | Raw type expression for complex/external types (e.g. `"Map<string, $resp>"`, `"Observable<User>"`). Combine with `templateRefs` for `$placeholder` substitution. |
| `templateRefs[]` | array | `[{placeholder, typeIdentifier}]` — substitutes `$placeholder` in `type` and triggers imports. |
| `isOptional` | boolean | TS: `string?` style; C#: nullable reference. |
| `isInitializer` | boolean | Add a default value. |
| `comment` | string | JSDoc/XMLdoc comment on the property. |
| `commentTemplateRefs[]` | array | Same shape as `templateRefs`, but for comments. |
| `decorators[]` | array | Property-level decorators (e.g. `@IsEmail()`, `@Required()`). Each: `code` + optional `templateRefs`. |

### `interfaces[]` — interface definition

Same shape as a class (minus `isAbstract`, `constructorParameters`, `baseClassTypeIdentifier`):
- `name`, `typeIdentifier`, `path`, `fileName`, `comment`
- `interfaceTypeIdentifiers[]` — interfaces this one extends
- `genericArguments[]`, `properties[]`, `customCode[]`, `decorators[]`, `customImports[]`

For TypeScript, MetaEngine **strips the `I` prefix** (`IUserRepository` exports as `UserRepository`). To avoid file collisions with the implementing class, set `fileName: "i-user-repository"`. (C# preserves `I` prefix.)

### `enums[]`

| Field | Notes |
|---|---|
| `name` | Enum name. |
| `typeIdentifier` | Cross-reference identifier. |
| `members[]` | `[{name, value}]` (numeric values). |
| `comment` | Doc comment. |
| `path`, `fileName` | Optional. |

Enums get a file-name suffix per language (TS: `order-status.enum.ts`).

### `arrayTypes[]` (virtual — no files)

Each entry:
- `typeIdentifier` (required)
- One of: `elementPrimitiveType` (`String`/`Number`/`Boolean`/`Date`/`Any`) or `elementTypeIdentifier` (a generated type's identifier).

TS output: `Array<T>`. C# note: arrayTypes generate `IEnumerable<T>` — for `List<T>` use `"type": "List<$user>"` with templateRefs instead.

### `dictionaryTypes[]` (virtual — no files)

Each entry:
- `typeIdentifier` (required)
- Key: one of `keyPrimitiveType` / `keyTypeIdentifier` / `keyType` (raw).
- Value: one of `valuePrimitiveType` / `valueTypeIdentifier`.

All four primitive/custom combinations are supported for key/value. TS output: `Record<K, V>`.

### `concreteGenericClasses[]` (virtual — no files)

Use this to materialize a concrete generic instantiation (e.g. `Repository<User>`) you can extend or reference.

| Field | Notes |
|---|---|
| `identifier` | New identifier for this concrete type (e.g. `"user-repo-concrete"`). |
| `genericClassIdentifier` | The generic class's `typeIdentifier` (e.g. `"repo-generic"`). |
| `genericArguments[]` | `[{typeIdentifier}]` or `[{primitiveType}]` — the type args. |

Then a class can `baseClassTypeIdentifier: "user-repo-concrete"` to get `extends Repository<User>` with imports.

### `concreteGenericInterfaces[]` (virtual)

Same shape as `concreteGenericClasses` but for interfaces (`IRepository<User>`).

### `customFiles[]` (real files, no class wrapper)

For type aliases, barrel exports, utility files. Each entry:
- `name` — file name (no extension)
- `path` — directory
- `fileName` — explicit file name override
- `identifier` — optional, lets other files refer to this file via `customImports[].path = "<identifier>"` (auto-resolves to relative path)
- `customCode[]` — one entry per export/alias/function (each `code` + optional `templateRefs`)
- `customImports[]` — external imports (or by `identifier` of another customFile)

---

## TypeScript-specific notes

- `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- Interface name `I` prefix is **stripped** from the exported symbol (`IUser` → `User`). Set `fileName` to control the file path.
- Auto-indents `\n` inside `customCode` blocks; one method per `customCode` entry (blocks are separated by blank lines automatically).
- Decorators are emitted directly (`@Injectable({…})`).
- Constructor parameters use `constructor(public x: T)` syntax — same auto-property-promotion gotcha as C#/Java/Go/Groovy: don't duplicate them in `properties[]`.
- No imports needed for primitives or `Date`; only `customImports` for npm packages (`@angular/core`, `rxjs`, `@nestjs/common`, etc.).
- Type aliases (`type UserId = string`) and union types (`'active' | 'inactive'`) belong in `customFiles`, not `classes`.

---

## Worked patterns (TypeScript)

### Two related interfaces with cross-references
```jsonc
{
  "language": "typescript",
  "interfaces": [
    {"name": "Address", "typeIdentifier": "address", "properties": [
      {"name": "street", "primitiveType": "String"},
      {"name": "city",   "primitiveType": "String"}
    ]},
    {"name": "User", "typeIdentifier": "user", "properties": [
      {"name": "id",      "primitiveType": "String"},
      {"name": "address", "typeIdentifier": "address"}
    ]}
  ]
}
```
Produces `address.ts` and `user.ts` with `import { Address } from './address';` automatically.

### Class with abstract base, methods, templateRef in customCode
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

### Generic class + concrete generic + class extending it
```jsonc
{
  "language": "typescript",
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
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

### Array & dictionary types
```jsonc
{
  "arrayTypes": [
    {"typeIdentifier": "user-list",   "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array","elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
    {"typeIdentifier": "user-names",  "keyTypeIdentifier": "user",  "valuePrimitiveType": "String"},
    {"typeIdentifier": "user-meta",   "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata"}
  ]
}
```
TS output uses `Array<T>` and `Record<K,V>`.

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
    "name": "PetService", "typeIdentifier": "pet-service", "path": "services",
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
       "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}]
}
```

### customFiles for type aliases + reference from another file
```jsonc
{
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
      {"code": "updateStatus(id: UserId, status: Status): void { }"}
    ]
  }]
}
```

### Constructor parameters — RIGHT and WRONG
WRONG (causes `"Sequence contains more than one matching element"`):
```jsonc
{"classes": [{
  "name": "User", "typeIdentifier": "user",
  "constructorParameters": [{"name": "email", "type": "string"}],
  "properties":           [{"name": "email", "type": "string"}]   // ❌ duplicate
}]}
```
RIGHT:
```jsonc
{"classes": [{
  "name": "User", "typeIdentifier": "user",
  "constructorParameters": [
    {"name": "email",  "type": "string"},
    {"name": "status", "typeIdentifier": "status"}
  ],
  "properties": [
    {"name": "createdAt", "primitiveType": "Date"}
  ]
}]}
```
Generated TS:
```ts
import { Status } from './status.enum';
export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

### Interface with method signatures intended to be `implements`-ed
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
**Don't** model these as `properties` with `type: "() => Promise<User[]>"` — implementing classes will then duplicate them as property declarations.

---

## Output structure

- For each `classes[]`/`interfaces[]`/`enums[]`/`customFiles[]` entry, one file is written under `outputPath/path/<filename>.<ext>`.
- File name = kebab-case of `name` unless `fileName` is set. Enums get a `.enum` suffix in TS.
- Imports are computed from the typegraph: any `typeIdentifier`/`templateRefs` reference becomes a relative `import` statement to the right file. `customImports` are emitted verbatim.
- Constructor parameters become `constructor(public x: T)` declarations (TS) or equivalent properties (other langs).
- `customCode` entries are emitted in order, separated by blank lines.
- Virtual entries (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) produce no files; they only modify how other types render.
- `dryRun: true` returns generated source in the response without writing — useful for verifying before commit.
- `skipExisting: true` (default) won't overwrite existing files. Set `false` to regenerate.

---

## Common mistakes — quick checklist

1. Referencing a `typeIdentifier` that isn't defined in the same call → silently dropped. **Cross-check every reference.**
2. Function-typed properties on interfaces meant to be implemented → duplicated members. **Use `customCode` instead.**
3. Internal type names as raw strings in `customCode` (no `templateRefs`) → no import. **Use `$placeholder` + `templateRefs`.**
4. (C#) `arrayTypes` when you need `List<T>` → use `"type": "List<$user>"` with templateRefs.
5. Adding `System.*`, `typing.*`, `java.util.*` (etc.) to `customImports` → duplication/errors. **Let MetaEngine handle them.**
6. Duplicating constructor params in `properties[]` → "Sequence contains more than one matching element". **Constructor params auto-become properties.**
7. Reserved words (`delete`, `class`, `import`) as property names → compile error. Use `remove`/`clazz`/`importData`.
8. Splitting related types across multiple `generate_code` calls → cross-file imports break. **One call.**
9. (C#) Expecting `Number`→`double`. It maps to `int`. Use `"type": "decimal"`/`"type": "double"`.
10. (TS) `IFoo` interface and `Foo` implementing class collide on file name. Set `fileName: "i-foo"` on the interface.

---

## Decision flow for "what field do I use?"

1. Does it produce a file? → `classes` / `interfaces` / `enums` / `customFiles`.
2. Just a reusable type alias for a list/map? → `arrayTypes` / `dictionaryTypes`.
3. Need `Repository<User>` as a referenceable name? → `concreteGenericClasses`.
4. Does the field have a type but no logic? → `properties[]`.
5. Does it have logic, an initializer, or is it a method? → `customCode[]` (one entry per member).
6. Is the referenced type defined in this same call? → `typeIdentifier` (in `properties`) or `$placeholder` + `templateRefs` (in `customCode`/complex `type` strings).
7. Is the referenced type from an npm/external package? → `customImports[]`.
8. Is it a TS type alias / union / barrel re-export? → `customFiles[]`.
9. Want to inspect output before writing? → `dryRun: true`.

When in doubt: model EVERYTHING in a single call, lean on `templateRefs` for any internal reference inside string code, and never specify standard-library imports.
