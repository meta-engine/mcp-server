# MetaEngine MCP — Knowledge Brief (TypeScript)

This brief is self-contained. It is the only documentation the generation session will have for the metaengine MCP. Read it end-to-end before composing any `generate_code` call.

---

## What MetaEngine is

MetaEngine is a **semantic** code generator (not a templating engine). You hand it structured JSON describing types, fields, relationships, decorators, methods, and external dependencies. It returns **compilable source files** with cross-references resolved, imports written, generics expanded, and language idioms applied. Targets: `typescript`, `csharp`, `python`, `go`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`.

A single well-formed JSON call replaces dozens of error-prone Write/Edit calls. The whole point is **one call** with the complete typegraph.

---

## Tools exposed by this MCP

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns this guide. Optional `language` arg. Already called in warmup; do **not** re-call. |
| `mcp__metaengine__generate_code` | **The main tool.** Takes the structured JSON spec and writes source files. |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code`, but reads the spec from a JSON file path (`specFilePath` arg). Also supports `outputPath`, `skipExisting`, `dryRun` overrides. Use when a spec is large enough that putting it in the tool call is expensive. |
| `mcp__metaengine__generate_openapi` | Generate HTTP client from an OpenAPI spec (URL or inline). Frameworks: angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi, csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession. |
| `mcp__metaengine__generate_graphql` | Generate HTTP client from a GraphQL SDL schema. Same frameworks as openapi. |
| `mcp__metaengine__generate_protobuf` | Generate HTTP client from `.proto` source. Same frameworks (Python uses `python-httpx`). |
| `mcp__metaengine__generate_sql` | Generate model classes from SQL DDL (`CREATE TABLE`). Languages: typescript, csharp, go, python, java, kotlin, groovy, scala, swift, php, rust. |

For an inline-spec TypeScript generation task, the tool you will use is **`mcp__metaengine__generate_code`**.

---

## `generate_code` — full input schema

Top-level fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **yes** | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | no (default `.`) | Output directory for generated files |
| `packageName` | string | no | Package/module/namespace. For TypeScript not needed. C# omits namespace if empty. Java/Kotlin/Groovy default `com.metaengine.generated`, Go default `github.com/metaengine/demo`. |
| `skipExisting` | bool | no (default `true`) | Skip files that already exist |
| `dryRun` | bool | no (default `false`) | Don't write files; return contents in response |
| `initialize` | bool | no (default `false`) | Initialize properties with default values |
| `interfaces` | array | no | Interface definitions (and generic interface templates) |
| `classes` | array | no | Class definitions (and generic class templates) |
| `enums` | array | no | Enum definitions |
| `arrayTypes` | array | no | Reusable array type **references** (no files generated) |
| `dictionaryTypes` | array | no | Reusable dictionary type **references** (no files generated) |
| `concreteGenericClasses` | array | no | Concrete generic implementations e.g. `Repository<User>` (no files generated) |
| `concreteGenericInterfaces` | array | no | Concrete generic interface implementations (no files generated) |
| `customFiles` | array | no | Files without a class wrapper (type aliases, barrel exports, utilities) |

### `interfaces[]` and `classes[]` — fields

- `name` (string) — type name as it appears in source
- `typeIdentifier` (string) — **unique identifier** used to reference this type from elsewhere in the same call
- `fileName` (string, optional) — override generated filename (no extension)
- `path` (string, optional) — directory under `outputPath`, e.g. `models`, `services/auth`
- `comment` (string, optional) — doc comment for the type
- `isAbstract` (bool, classes only)
- `baseClassTypeIdentifier` (string, classes only) — extends another class in the batch (or a `concreteGenericClasses` identifier)
- `interfaceTypeIdentifiers` (string[]) — implements/extends these interfaces
- `genericArguments[]` — makes this a generic template:
  - `name` (e.g. `T`, `K`)
  - `constraintTypeIdentifier` — generic constraint (e.g. `T extends BaseEntity`)
  - `propertyName` — auto-create a property of type `T` with this name
  - `isArrayProperty` — make that property `T[]`
- `properties[]` — declared fields **with type only, no logic**:
  - `name`, `comment`
  - one of `primitiveType` (`String|Number|Boolean|Date|Any`), `typeIdentifier` (ref to another type in the batch), or `type` (raw string for complex/external types)
  - `templateRefs[]` — `{placeholder, typeIdentifier}` pairs to resolve `$placeholder` tokens inside `type`
  - `decorators[]` — `{code, templateRefs}`
  - `commentTemplateRefs[]`
  - `isOptional` (bool) — generates `?` (TS) / nullable (C#)
  - `isInitializer` (bool) — emit a default-value initializer
- `constructorParameters[]` (classes) — `{name, primitiveType|typeIdentifier|type}`. **In C#/Java/Go/Groovy these auto-become properties — do NOT also list them in `properties[]`.** In TypeScript constructor parameters also auto-become properties.
- `customCode[]` — methods, initialized fields, anything with logic; **one item = one member**:
  - `code` — raw source text for that one member
  - `templateRefs[]` — `{placeholder, typeIdentifier}` pairs to resolve `$foo` tokens inside `code` and to trigger import resolution
- `customImports[]` — **external libraries only** (`{path, types[]}`). Never list framework imports here.
- `decorators[]` — class-level decorators `{code, templateRefs}`

### `enums[]`

- `name`, `typeIdentifier`, `fileName?`, `path?`, `comment?`
- `members[]` — `{name, value:number}`

### `arrayTypes[]` (virtual; no files)

- `typeIdentifier` (required) — referenceable identifier
- `elementPrimitiveType` OR `elementTypeIdentifier`

### `dictionaryTypes[]` (virtual; no files)

- `typeIdentifier` (required)
- key: `keyPrimitiveType` OR `keyType` (raw string) OR `keyTypeIdentifier`
- value: `valuePrimitiveType` OR `valueTypeIdentifier`

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` (virtual; no files)

- `identifier` — referenceable id (used as `baseClassTypeIdentifier` etc.)
- `genericClassIdentifier` — references the generic template's `typeIdentifier`
- `genericArguments[]` — `{primitiveType}` OR `{typeIdentifier}`

### `customFiles[]`

- `name`, `path?`, `fileName?`, `identifier?` (so other files can `customImports` it)
- `customCode[]` — `{code, templateRefs[]}`
- `customImports[]` — `{path, types[]}`

---

## The 10 critical rules (rule-violation = generation failure)

### 1. **ONE call with the entire typegraph.**
`typeIdentifier` references **only resolve within the current batch.** If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks cross-file imports. Do **not** call `generate_code` more than once for related types.

### 2. **`properties` = type declarations. `customCode` = everything else.**
Properties hold field declarations *with type only, no initialization, no logic*. CustomCode holds methods, initialized fields, getters, anything else. **One `customCode` item = exactly one member.** Never put methods inside `properties`. Never put uninitialized type declarations inside `customCode`.

### 3. **Use `templateRefs` for internal types referenced from `customCode` / `type` strings.**
When code or a type-string references another type from the same batch, write a placeholder like `$user` and add a `templateRefs` entry mapping it to the `typeIdentifier`. This is what triggers MetaEngine to write the import. Without it, the import is missing and compilation breaks (especially in C# across namespaces).

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

### 4. **Never add framework imports to `customImports`.**
MetaEngine auto-imports stdlib for every language. Adding them manually causes duplicates/errors.

| Language   | Auto-imported (do NOT specify)                                                                   |
|------------|--------------------------------------------------------------------------------------------------|
| TypeScript | (no imports needed — built-ins) |
| C#         | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*    |
| Python     | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses                 |
| Java       | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*       |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*                                |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more  |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)                |
| Rust       | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde                           |
| Groovy     | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream)      |
| Scala      | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.*         |
| PHP        | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable              |

`customImports` is for external libs only (e.g. `@angular/core`, `rxjs`, `FluentValidation`).

### 5. **`templateRefs` are ONLY for internal types.**
External library types must use `customImports`. Same-batch types must use `typeIdentifier`/`templateRefs`. Never mix the two for one reference.

### 6. **Constructor parameters auto-create properties (C#/Java/Go/Groovy).**
Don't duplicate them in `properties[]` or you get `Sequence contains more than one matching element` errors. (TypeScript also auto-creates properties from constructor parameters.) Only put **non-constructor** fields into `properties[]`.

### 7. **Virtual types don't generate files.**
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create *type references only*. They produce no files. They become useful when another type references their `typeIdentifier`.

### 8. **Don't reference a non-existent `typeIdentifier`.**
If a property/customCode references an identifier that's not in the batch, the property is silently dropped. Verify every `typeIdentifier`.

### 9. **Reserved words must be avoided as property names** (`delete`, `class`, `import`). Use `remove`, `clazz`, `importData`.

### 10. **For interfaces that classes will `implements`, put method signatures in `customCode` — not as function-typed properties.**
If you write `"type": "() => Promise<User[]>"` on a property, the implementing class will duplicate them as property declarations next to your customCode methods. Always use `customCode` for interface method signatures.

---

## Pattern reference

### Cross-referencing types in one batch

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

Two files, with import from `User` to `Address` resolved automatically.

### Inheritance + methods on a class

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

The concrete generic creates a virtual `Repository<User>` that `UserRepository` extends.

### Array / dictionary types

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

Reference via `"typeIdentifier": "user-list"` from a property.

### Complex type expressions with `templateRefs`

```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

`templateRefs` work in `properties`, `customCode`, and `decorators`.

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

Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### Service with external dependency injection

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

### `customFiles` for type aliases / barrel exports

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

The customFile's `identifier` enables import resolution from other files.

### Interface with method signatures (TypeScript / C#)

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

Always use `customCode` (with trailing `;`) for signatures on interfaces that classes will implement. If you set a `fileName`, that's the on-disk name; this is critical when the I-prefixed interface and its implementing class would otherwise collide in TypeScript.

---

## Language-specific notes

### TypeScript (this run's target)
- MetaEngine **strips the `I` prefix** from interface names: `IUserRepository` is exported as `UserRepository`. Set `fileName` (e.g. `i-user-repository`) on the interface to avoid collisions with an implementing class.
- Primitive type mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- No `customImports` are needed for built-ins.
- Auto-indent for newlines (`\n`) inside `customCode`.
- Decorators are emitted directly.
- Constructor parameters auto-create properties.
- Idiomatic transformations: methods stay camelCase, classes/interfaces PascalCase, files kebab-case.

### C#
- `I` prefix is preserved on interface names.
- `Number` → `int` (not `double`!). Use `"type": "decimal"` or `"type": "double"` explicitly when needed.
- `packageName` sets the namespace; omit for GlobalUsings.
- Interface properties → `{ get; }`; class properties → `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with `templateRefs`.
- `isOptional` → nullable reference type (`string?`).
- **Every internal type reference in customCode MUST use `templateRefs`** or `using` directives won't be generated for cross-namespace types.

### Python
- **You must provide explicit indentation (4 spaces) after `\n` in `customCode`** — Python doesn't auto-indent.
- typing imports are automatic.
- Idiomatic: methods become `snake_case`.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions inside `customCode`.
- Constructor parameters auto-create properties.

### Java
- Idiomatic: enum members emitted as `ALL_CAPS`.
- Constructor parameters auto-create properties.

### Other languages
- Kotlin/Groovy/Scala/Swift/PHP/Rust supported with their own auto-imports (see table in rule #4). Constructor parameters auto-create properties in Groovy.

---

## Common mistakes (cheat sheet)

1. **Don't** reference a `typeIdentifier` that doesn't exist in the batch → silently dropped property. **Do** verify every identifier.
2. **Don't** put method signatures as function-typed properties on interfaces. **Do** use `customCode` for them.
3. **Don't** write internal type names as raw strings in `customCode` (e.g., `"private repo: IUserRepository"`). **Do** use `$placeholder` + `templateRefs`.
4. **Don't** use `arrayTypes` in C# when you need `List<T>`. **Do** use `"type": "List<$user>"`.
5. **Don't** add stdlib imports (`System.*`, `typing.*`, `java.util.*`) to `customImports`.
6. **Don't** duplicate constructor parameter names in `properties[]` for C#/Java/Go/Groovy.
7. **Don't** use reserved words (`delete`, `class`, `import`) as property names.
8. **Don't** generate related types in separate MCP calls — cross-file imports only resolve within one batch.
9. **Don't** expect `Number` to map to `double` in C# (it maps to `int`).
10. **Don't** forget `fileName` when an `I`-prefixed interface and its implementing class would collide in TypeScript.

---

## Output structure

- Each interface, class, and enum produces **one source file** at `outputPath/path/<fileName>.<ext>`.
- Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) produce **no files**.
- `customFiles[]` produce one file each, without a class wrapper (good for type aliases, barrel exports, utility functions).
- Imports between same-batch files are written automatically when references go through `typeIdentifier` or `templateRefs`.
- `dryRun: true` returns generated content in the response without writing — useful to verify shape before committing.

---

## Workflow checklist for a generation task

1. **Inventory** every type the spec mentions (entities, enums, requests, responses, services).
2. **Assign `typeIdentifier`s** to all of them — these are your wires.
3. Decide which are **classes**, which are **interfaces**, which are **enums**, which are **virtual** (array/dict/concrete-generic).
4. Decide where logic lives: **methods always go in `customCode`** (one item per member); **fields without logic go in `properties`**.
5. Whenever code or a type-string references an internal type, replace the name with `$placeholder` and add a `templateRefs` entry.
6. Add `customImports` only for **external** libraries.
7. Bundle **everything in ONE `generate_code` call** — language `typescript`, plus `interfaces` / `classes` / `enums` / `arrayTypes` / `dictionaryTypes` / `concreteGenericClasses` / `customFiles` as needed.
8. Pick `outputPath` so files land where the consumer wants them.
9. (Optional) `dryRun: true` first to inspect, then real run.

If you find yourself preparing a second `generate_code` call for the same project, stop — merge them into one.

---

## Quick syntax reminder for TypeScript `customCode`

- Class methods: `methodName(arg: Type): Return { /* body */ }`
- Initialized fields: `private items: User[] = [];`
- Interface signatures: `methodName(arg: Type): Return;` (semicolon, no body)
- Async: `async fetchAll(): Promise<$list> { ... }` with templateRefs
- Constructor: prefer `constructorParameters[]` over hand-writing `constructor(...)` in customCode.
