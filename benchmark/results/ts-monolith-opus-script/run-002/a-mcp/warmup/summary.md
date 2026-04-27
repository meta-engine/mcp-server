# MetaEngine MCP — Knowledge Brief (TypeScript)

MetaEngine is a **semantic code-generation system** exposed over MCP. You describe types, relationships, and methods as structured JSON; MetaEngine emits compilable, correctly-imported source files. It resolves cross-references, manages imports, and applies language idioms automatically. **One well-formed JSON call replaces dozens of hand-edited file writes.**

Supported languages: TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust.

---

## Tools exposed by the metaengine MCP server

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns this guide + examples. Optional `language` param. Pure read; no side effects. |
| `mcp__metaengine__generate_code` | **The primary tool.** Generates source files from a structured spec (classes/interfaces/enums/etc.). |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code` but loads the spec JSON from a file path (`specFilePath`). Saves context for huge specs; can override `outputPath` / `skipExisting` / `dryRun`. |
| `mcp__metaengine__generate_openapi` | OpenAPI spec → typed HTTP client. Frameworks: angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi, csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession. |
| `mcp__metaengine__generate_graphql` | GraphQL SDL → typed HTTP client (same framework set). |
| `mcp__metaengine__generate_protobuf` | `.proto` → typed HTTP client (same framework set; python-httpx instead of fastapi). |
| `mcp__metaengine__generate_sql` | SQL DDL (CREATE TABLE) → typed model classes. |

For this task, **use `generate_code`** unless the spec source is OpenAPI/GraphQL/protobuf/SQL.

---

## generate_code — Full Input Schema

Top-level fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **yes** | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | no (default `.`) | Where files are written |
| `packageName` | string | no | Namespace/package. Defaults: Go=`github.com/metaengine/demo`; Java/Kotlin/Groovy=`com.metaengine.generated`; C# omitted = no namespace (GlobalUsings). |
| `initialize` | boolean | no (default false) | Initialize properties with default values |
| `skipExisting` | boolean | no (default true) | Skip writing files that already exist |
| `dryRun` | boolean | no (default false) | Preview only — returns generated code in response, doesn't write |
| `classes` | array | no | Class definitions (regular or generic templates) |
| `interfaces` | array | no | Interface definitions (regular or generic templates) |
| `enums` | array | no | Enum definitions |
| `arrayTypes` | array | no | **Virtual** array type references (no files generated) |
| `dictionaryTypes` | array | no | **Virtual** dictionary type references (no files generated) |
| `concreteGenericClasses` | array | no | **Virtual** `Repository<User>`-style references (no files) |
| `concreteGenericInterfaces` | array | no | **Virtual** `IRepository<User>`-style references (no files) |
| `customFiles` | array | no | Files without a class wrapper (type aliases, barrel exports, utilities) |

### `classes[]` shape

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name |
| `typeIdentifier` | string | **Unique batch-local id** used for cross-references |
| `path` | string | Subdirectory (e.g. `models`, `services/auth`) |
| `fileName` | string | Override file name (without extension) |
| `comment` | string | Class-level doc comment |
| `isAbstract` | boolean | |
| `baseClassTypeIdentifier` | string | Reference to base class's `typeIdentifier` (or to a `concreteGenericClasses.identifier` to extend `Repository<User>`) |
| `interfaceTypeIdentifiers` | string[] | Interfaces this class implements |
| `genericArguments` | array | Makes this a generic template like `Repository<T>`. Each: `{name, constraintTypeIdentifier?, propertyName?, isArrayProperty?}` |
| `constructorParameters` | array | `{name, type? \| primitiveType? \| typeIdentifier?}`. **In C#/Java/Go/Groovy these auto-create properties — don't duplicate in `properties[]`** |
| `properties` | array | See properties shape below |
| `customCode` | array | Methods, initialized fields. **One block = one member.** See custom-code shape below |
| `customImports` | array | `[{path, types?}]`. External libs only |
| `decorators` | array | `[{code, templateRefs?}]` — class-level decorators |

### Properties shape (used by classes & interfaces)

```jsonc
{
  "name": "email",
  "primitiveType": "String",        // OR
  "typeIdentifier": "user",         // OR
  "type": "Map<string, $resp>",     // for free-form expressions
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}],
  "isOptional": true,                // generates `email?: string` / nullable
  "isInitializer": true,             // emit default-value initialization
  "comment": "User email",
  "commentTemplateRefs": [...],
  "decorators": [{"code": "@IsEmail()", "templateRefs": [...]}]
}
```

**`primitiveType` enum**: `String`, `Number`, `Boolean`, `Date`, `Any`.

Pick exactly one of `primitiveType` / `typeIdentifier` / `type` per property. When using `type` with a generated-type reference, you MUST also supply `templateRefs` so imports are resolved.

### CustomCode shape

```jsonc
{
  "code": "getUser(id: string): Promise<$user> { return this.repo.findById(id); }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

- **One method (or one initialized field) per `customCode` block.** Auto-newlines are inserted between blocks.
- `$placeholder` tokens are replaced with the resolved type name AND trigger automatic imports.
- Use templateRefs for **every** internal-type reference inside `code`. (In C# this is mandatory — raw type names won't get cross-namespace `using` directives.)

### `interfaces[]` shape

Same structure as `classes` (without `isAbstract`, `baseClassTypeIdentifier`, `constructorParameters`). Supports `genericArguments`, `interfaceTypeIdentifiers` (interface extension), `properties`, `customCode`, `customImports`, `decorators`, `path`, `fileName`, `comment`.

### `enums[]` shape

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 2}],
  "path": "models",
  "fileName": "order-status",
  "comment": "Order lifecycle states"
}
```

Enums auto-suffix filenames in some languages (`order-status.enum.ts` in TS).

### Virtual types

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create **reusable type references only — they never produce files.** Reference them via `typeIdentifier` in properties, customCode (with templateRefs), or via `baseClassTypeIdentifier`/`interfaceTypeIdentifiers`.

```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
  {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
],
"dictionaryTypes": [
  {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
  {"typeIdentifier": "user-names", "keyTypeIdentifier": "user", "valuePrimitiveType": "String"},
  {"typeIdentifier": "user-meta", "keyTypeIdentifier": "user", "valueTypeIdentifier": "metadata"}
],
"concreteGenericClasses": [{
  "identifier": "user-repository",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}],
"concreteGenericInterfaces": [{
  "identifier": "i-user-repo",
  "genericClassIdentifier": "i-repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}]
```

`genericArguments[]` items accept `typeIdentifier` OR `primitiveType`.

### `customFiles[]` shape

```jsonc
{
  "name": "types",                 // file name (no ext)
  "path": "shared",                // subdir
  "identifier": "shared-types",    // optional; lets other files import via customImports {path: "shared-types"}
  "fileName": "types",             // optional override
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"}
  ],
  "customImports": [{"path": "...", "types": ["..."]}]
}
```

Used for type aliases, barrel exports, helper functions — anything not class/interface/enum-shaped.

---

## Critical Rules (the ones that bite you)

### 1. Generate ALL related types in ONE call.
`typeIdentifier` references resolve **only within the current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. **Do not split per-domain.** Cross-file imports only resolve within a single batch.

### 2. Properties = type declarations. CustomCode = everything else.
`properties[]` declares a typed field. **Never put methods or initialized expressions in properties.**
`customCode[]` carries methods and initialized fields. **One block = exactly one member.**

```jsonc
"properties": [{"name": "id", "primitiveType": "String"}],
"customCode": [
  {"code": "private http = inject(HttpClient);"},
  {"code": "getAll(): T[] { return this.items; }"}
]
```

### 3. Use `templateRefs` for every internal-type reference inside `customCode` / `type`.
Without templateRefs, MetaEngine cannot generate the import. Use `$placeholder` syntax and bind it to the `typeIdentifier`:

```jsonc
{"code": "getUser(): Promise<$user> { ... }",
 "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
```

In C# this is **mandatory** for cross-namespace `using` directives.

### 4. Never add framework imports to `customImports`.
MetaEngine auto-imports the standard library. Adding them duplicates or errors out.

| Language | Auto-imported (do NOT specify) |
|---|---|
| C# | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, ... |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, ...) |
| Rust | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream) |
| Scala | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |
| TypeScript | (no imports needed — built-in types) |

`customImports` is **only** for external libraries: `@angular/core`, `rxjs`, `FluentValidation`, etc.

### 5. templateRefs are ONLY for internal types in the same batch.
External library types → `customImports`. Same-batch types → `typeIdentifier` or `templateRefs`. Don't mix.

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy).
**Do NOT duplicate** them in `properties[]` — causes `Sequence contains more than one matching element`. Put shared fields in `constructorParameters` and additional-only fields in `properties`. (TypeScript also benefits — `public email: string` ctor params become public properties automatically.)

### 7. Virtual types don't generate files.
`arrayTypes` / `dictionaryTypes` / `concreteGenericClasses` / `concreteGenericInterfaces` create only references. Use them by `typeIdentifier`/`identifier`.

### 8. Don't reference unknown `typeIdentifier`s.
Silently dropped → property disappears in output. Verify every reference exists in the batch.

### 9. For interface methods: use `customCode`, not function-typed properties.
If a class will `implements` the interface, define method signatures in `customCode`. Function-typed properties cause the implementing class to duplicate them as property declarations alongside your customCode methods.

```jsonc
"interfaces": [{
  "name": "IUserRepository", "typeIdentifier": "user-repo", "fileName": "i-user-repository",
  "customCode": [
    {"code": "findAll(): Promise<$user[]>;",
     "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
  ]
}]
```

### 10. Avoid reserved-word property names (`delete`, `class`, `import`).

---

## TypeScript-Specific Notes

- **`I`-prefix on interfaces is stripped** from the exported name. `IUserRepository` exports as `UserRepository`. To avoid file-name collisions with the implementing class, set `"fileName": "i-user-repository"` on the interface.
- Primitive mapping: `Number`→`number`, `String`→`string`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`.
- `customCode` newlines (`\n`) are auto-indented.
- Decorators are emitted directly (`@Injectable({...})`).
- `arrayTypes` produce `Array<T>` / `T[]` properties.
- `dictionaryTypes` produce `Record<K, V>` properties.
- Constructor parameters with access modifiers (`public email: string`) auto-become properties — don't duplicate.

---

## Output Structure

The engine returns a description of the generated files. With `dryRun: true` the generated source is included in the response (no disk write). With `dryRun: false` (default) files are written under `outputPath`, organized by `path` per type. File names derive from `name` (kebab-cased for TS) or from `fileName` if provided. Imports between files are resolved automatically based on the batch graph.

---

## Canonical Patterns (TypeScript)

### A. Cross-referencing classes/interfaces

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

### B. Inheritance + methods

```jsonc
{
  "language": "typescript",
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

### C. Generic class + concrete usage

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

### D. Service with external DI + array refs

```jsonc
{
  "language": "typescript",
  "classes": [
    {"name": "Pet", "typeIdentifier": "pet",
     "properties": [{"name": "name", "primitiveType": "String"}]},
    {
      "name": "PetService", "typeIdentifier": "pet-service", "path": "services",
      "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
      "customImports": [
        {"path": "@angular/core", "types": ["Injectable", "inject"]},
        {"path": "@angular/common/http", "types": ["HttpClient"]},
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
    }
  ],
  "arrayTypes": [{"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}]
}
```

### E. Type aliases via customFiles

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
      {"code": "updateStatus(id: UserId, status: Status): void { }"},
      {"code": "getResults<T>(data: T[]): ResultSet<T> { return {data, total: data.length, page: 1}; }"}
    ]
  }]
}
```

### F. Enum + class consuming it

```jsonc
{
  "language": "typescript",
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

### G. Interface (with method signatures) + implementing class

```jsonc
{
  "language": "typescript",
  "interfaces": [{
    "name": "IUserRepository", "typeIdentifier": "i-user-repo", "fileName": "i-user-repository",
    "customCode": [
      {"code": "findAll(): Promise<$user[]>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "findById(id: string): Promise<$user | null>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }],
  "classes": [
    {"name": "User", "typeIdentifier": "user",
     "properties": [{"name": "id", "primitiveType": "String"}, {"name": "email", "primitiveType": "String"}]},
    {"name": "UserRepository", "typeIdentifier": "user-repo",
     "interfaceTypeIdentifiers": ["i-user-repo"],
     "customCode": [
       {"code": "private items: $user[] = [];",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
       {"code": "async findAll(): Promise<$user[]> { return this.items; }",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
       {"code": "async findById(id: string): Promise<$user | null> { return this.items.find(u => u.id === id) ?? null; }",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
     ]}
  ]
}
```

---

## Common Mistakes — Quick Checklist

1. ❌ Reference a `typeIdentifier` not defined in the batch → property silently dropped.
2. ❌ Define interface methods as function-typed properties → implementing class duplicates them.
3. ❌ Raw type names in `customCode` strings → missing imports.
4. ❌ Use `arrayTypes` in C# when you wanted `List<T>` → you got `IEnumerable<T>` instead. Use `"type": "List<$user>"` with templateRefs.
5. ❌ Add `System.*`, `typing.*`, `java.util.*`, etc. to `customImports` → duplication.
6. ❌ Duplicate constructor params in `properties[]` (C#/Java/Go/Groovy) → "Sequence contains more than one matching element".
7. ❌ Use reserved words (`delete`, `class`, `import`) as property names.
8. ❌ Split related types across multiple `generate_code` calls → cross-file imports break.
9. ❌ Expect `Number` → `double` in C# → it's `int`. Use `"type": "decimal"` / `"type": "double"`.
10. ❌ TS interface and implementing class file-name collision → set `"fileName": "i-user-repository"` on the interface.

---

## Decision Tree (use this when generating)

1. **One call.** Put every related type into a single `generate_code` invocation.
2. **What is each thing?**
   - Class / interface / enum → its own array.
   - Type alias, barrel, helper function → `customFiles`.
   - Reusable `T[]`, `Record<K,V>`, `Repository<User>` → `arrayTypes` / `dictionaryTypes` / `concreteGenericClasses` / `concreteGenericInterfaces`.
3. **For each member of a class/interface:**
   - Just a typed field? → `properties[]` (use `primitiveType` / `typeIdentifier` / `type`+`templateRefs`).
   - A method or an initialized field? → `customCode[]` (one block per member). Wrap any internal type with `$placeholder` + `templateRefs`.
4. **For each external-library import:** put it in `customImports` with explicit `types`.
5. **For framework/standard-library types:** do nothing — auto-imported.
6. **Verify before submitting:** every `typeIdentifier` referenced exists in the batch; every `$placeholder` has a matching `templateRefs` entry; constructor params aren't duplicated in `properties[]`.

---

## Tool-Call Skeleton (TypeScript)

```jsonc
mcp__metaengine__generate_code({
  "language": "typescript",
  "outputPath": "<target dir>",
  "skipExisting": false,            // overwrite when iterating
  "dryRun": false,
  "enums":     [ /* ... */ ],
  "interfaces":[ /* ... */ ],
  "classes":   [ /* ... */ ],
  "arrayTypes":[ /* ... */ ],
  "dictionaryTypes": [ /* ... */ ],
  "concreteGenericClasses": [ /* ... */ ],
  "concreteGenericInterfaces": [ /* ... */ ],
  "customFiles": [ /* ... */ ]
})
```

If the spec is large, write it to a `.json` file and call `mcp__metaengine__load_spec_from_file({specFilePath: "..."})` instead — same semantics, no context bloat.

