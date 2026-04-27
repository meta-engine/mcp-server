# MetaEngine MCP — Knowledge Brief (TypeScript focus)

MetaEngine is a *semantic* code generator (not a template engine) exposed as an MCP server. You describe types, relationships, and methods as structured JSON; MetaEngine emits compilable, correctly-imported source files. It resolves cross-references, manages imports, and applies language idioms automatically. Languages supported: TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust.

The next session will use this brief to call `mcp__metaengine__generate_code` exactly once with the full spec. Read everything below before constructing the JSON.

---

## Tools exposed by the metaengine MCP

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns this guide + linked resource pointers. Optional `language` filter. Pure docs helper — no code generation. |
| `mcp__metaengine__generate_code` | The main tool. Generates source files from a structured spec (classes, interfaces, enums, arrays, dictionaries, generics, custom files). Required: `language`. |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code` but loads the spec from a `.json` file path. Useful when the spec is large. Args: `specFilePath` (required), optional `outputPath`, `dryRun`, `skipExisting`. |
| `mcp__metaengine__generate_openapi` | Generates a typed HTTP client from an OpenAPI spec. Frameworks: angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi, csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession. |
| `mcp__metaengine__generate_graphql` | Same idea, but from a GraphQL SDL schema. |
| `mcp__metaengine__generate_protobuf` | Same idea, but from `.proto` definitions. |
| `mcp__metaengine__generate_sql` | Generates typed model classes from SQL DDL (CREATE TABLE). Supports validation annotations, navigation properties, etc. |

For arbitrary domain code (DTOs, services, controllers, repositories, generic types) **use `generate_code`**. The other generators are for spec-driven HTTP clients / DB models.

---

## CARDINAL RULES — read these before building the spec

### Rule 1 — Single call, one batch
`typeIdentifier` cross-references resolve **only within the same call**. Splitting types across multiple calls breaks imports. Put **every** related type into one `generate_code` invocation.

### Rule 2 — `properties[]` vs `customCode[]`
- `properties[]` = field declarations only (name + type, optionally `comment`, `decorators`, `isOptional`, `isInitializer`).
- `customCode[]` = anything with logic: methods, getters, setters, *initialized* fields (e.g. `private http = inject(HttpClient);`), interface method signatures.
- One `customCode` block = exactly one member. Blocks get auto-newlines between them.
- **Never** put a method in `properties`. **Never** put an uninitialized field in `customCode`.

### Rule 3 — `templateRefs` for internal type references inside strings
When a `customCode` snippet, a property `type` string, a decorator, or a comment references a type defined *in the same batch*, write a `$placeholder` and add a `templateRefs` entry mapping it to a `typeIdentifier`. This triggers correct import generation.

```jsonc
{
  "code": "getUser(id: string): Promise<$user> { return this.http.get<$user>(`/users/${id}`); }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

Without `templateRefs`, the engine cannot resolve the import and the generated file may not compile (especially in C#).

### Rule 4 — Never re-import framework / stdlib types via `customImports`
The engine auto-imports the standard library for each language. `customImports` is **only** for external/3rd-party libraries (e.g. `@angular/core`, `rxjs`, `FluentValidation`, `@nestjs/common`).

Auto-imported per language (do NOT list these in customImports):
- TypeScript: built-ins (no imports needed)
- C#: System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*
- Python: typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses
- Java: java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*
- Kotlin: java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*
- Go: time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http
- Swift: Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder)
- Rust: std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde
- Groovy: java.time.*, java.math.*, java.util (UUID, Date), java.io
- Scala: java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.*
- PHP: DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable

### Rule 5 — `templateRefs` are for *internal* types only
External library symbols → `customImports`. Same-batch types → `typeIdentifier` (in property/array/dict definitions) or `templateRefs` (inside string literals). Never mix.

### Rule 6 — Constructor parameters auto-create properties
In **C#, Java, Go, and Groovy**, fields in `constructorParameters[]` automatically become class fields. Do NOT also list them in `properties[]` — that throws "Sequence contains more than one matching element". Only put **additional** non-constructor fields in `properties`.
(In TypeScript, the `public email: string` parameter syntax is also generated automatically when you use `constructorParameters`.)

### Rule 7 — Virtual types do not produce files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are *type references only*. They never produce files. They exist so other types can reference them via `typeIdentifier`.

---

## `generate_code` — full input schema

Top-level fields:

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `typescript` \| `python` \| `go` \| `csharp` \| `java` \| `kotlin` \| `groovy` \| `scala` \| `swift` \| `php` \| `rust` |
| `outputPath` | string | Output directory. Default `"."`. |
| `packageName` | string | Module/namespace. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C#: omit/empty → no namespace declaration (GlobalUsings). |
| `initialize` | boolean (default false) | If true, properties get default-value initialization in generated output. |
| `skipExisting` | boolean (default true) | Skip overwriting files that already exist (stub pattern). |
| `dryRun` | boolean (default false) | If true, returns generated code in the response *without* writing to disk. |
| `classes[]` | array | Class definitions. |
| `interfaces[]` | array | Interface definitions. |
| `enums[]` | array | Enum definitions. |
| `arrayTypes[]` | array | Reusable array type references (no files). |
| `dictionaryTypes[]` | array | Reusable dictionary/map type references (no files). |
| `concreteGenericClasses[]` | array | Concrete instantiations of generic classes (e.g. `Repository<User>`), virtual. |
| `concreteGenericInterfaces[]` | array | Concrete instantiations of generic interfaces, virtual. |
| `customFiles[]` | array | Files with no class wrapper — type aliases, barrels, helpers. |

### Class object

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | Unique id for cross-references. |
| `fileName` | string | Override file name (no extension). |
| `path` | string | Subdir under outputPath, e.g. `"services"`, `"models/auth"`. |
| `comment` | string | Doc comment. |
| `isAbstract` | boolean | |
| `baseClassTypeIdentifier` | string | Identifier of base class (real or `concreteGenericClasses` entry). |
| `interfaceTypeIdentifiers` | string[] | Identifiers of interfaces to implement. |
| `genericArguments[]` | array | Makes this a generic template. Each: `name` (e.g. `"T"`), `constraintTypeIdentifier`, `propertyName` (auto-creates a `T` field), `isArrayProperty` (`T[]`). |
| `constructorParameters[]` | array | `{name, type|primitiveType|typeIdentifier}`. Auto-becomes properties (see Rule 6). |
| `properties[]` | array | See property schema below. |
| `customCode[]` | array | `{code, templateRefs?}`. One per member. |
| `customImports[]` | array | `{path, types?}`. **External libs only.** |
| `decorators[]` | array | `{code, templateRefs?}`. Class-level decorators. |

### Property object

| Field | Type | Notes |
|---|---|---|
| `name` | string | Field name. Avoid reserved words (`delete`, `class`, `import`). |
| `primitiveType` | enum | `String` \| `Number` \| `Boolean` \| `Date` \| `Any`. Use this for built-in scalars. |
| `typeIdentifier` | string | Reference another generated type (or virtual array/dict/concrete-generic). |
| `type` | string | Free-form type expression for complex shapes (use with `templateRefs`), e.g. `"Map<string, $user>"`, `"List<$user>"`, `"decimal"`, `"double"`. |
| `templateRefs[]` | array | `[{placeholder, typeIdentifier}]` — required when `type` mentions internal `$xxx`. |
| `isOptional` | boolean | TS → `?:`, C# → `T?`. |
| `isInitializer` | boolean | Adds default-value initialization. |
| `comment` | string | Doc comment. |
| `commentTemplateRefs[]` | array | Same shape as templateRefs, for type names referenced inside the doc comment. |
| `decorators[]` | array | Property-level decorators (e.g. `@IsEmail()`, `@Required()`). |

### Interface object
Same shape as Class but with `properties[]`, `customCode[]` (for method signatures), `customImports[]`, `decorators[]`, `genericArguments[]`, `interfaceTypeIdentifiers[]` (extends), `fileName`, `path`, `name`, `typeIdentifier`, `comment`.

### Enum object
`{name, typeIdentifier, fileName?, path?, comment?, members: [{name, value}]}`. Filenames auto-suffix in some langs (TS: `order-status.enum.ts`; C#: `OrderStatus.cs`).

### ArrayType
`{typeIdentifier, elementTypeIdentifier?, elementPrimitiveType?}`. Provide exactly one of element source. Generates `Array<T>` (TS), `IEnumerable<T>` (C#), `List<T>` (Java/Kotlin), etc.

### DictionaryType
`{typeIdentifier, keyPrimitiveType? | keyTypeIdentifier? | keyType?, valuePrimitiveType? | valueTypeIdentifier?}`. All four key/value combinations supported.

### ConcreteGenericClass / ConcreteGenericInterface
`{identifier, genericClassIdentifier, genericArguments: [{typeIdentifier? | primitiveType?}]}`. Use these so a class can `baseClassTypeIdentifier: "user-repo-concrete"` and the generator emits `extends Repository<User>` with imports.

### CustomFile
`{name, path?, fileName?, identifier?, customCode: [...], customImports?: [...]}`. Files without a class wrapper. Use `identifier` if you want other files to import from this one via `customImports: [{path: "<identifier>"}]`.

---

## TypeScript-specific notes (this benchmark is TS)

- `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- The `I` prefix on interface names is **stripped** in the export name (`IUserRepository` exports as `UserRepository`). To prevent file-name collisions with the implementing class, set `"fileName": "i-user-repository"` on the interface.
- Decorators are supported directly (e.g. `@Injectable({ providedIn: 'root' })`).
- customCode newlines (`\n`) get auto-indented.
- `arrayTypes` produce `Array<T>` (i.e. `new Array<T>()` initializers when `initialize: true`).
- For `Map<string, T>` style, use a property with `type: "Map<string, $user>"` + `templateRefs`.
- TS constructor parameters using `constructorParameters[]` emit `constructor(public email: string, ...)` style — DO NOT also list those names in `properties[]`.
- Reserved words like `delete`, `class`, `import` will collide if used as property names — pick safe alternates.

---

## Patterns that are easy to get right (and easy to get wrong)

### Pattern A — Two interfaces with cross-reference
```json
{
  "language": "typescript",
  "interfaces": [
    {"name": "Address", "typeIdentifier": "address",
      "properties": [{"name": "street", "primitiveType": "String"}, {"name": "city", "primitiveType": "String"}]},
    {"name": "User", "typeIdentifier": "user",
      "properties": [{"name": "id", "primitiveType": "String"}, {"name": "address", "typeIdentifier": "address"}]}
  ]
}
```

### Pattern B — Class extends class
```json
{
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "User", "typeIdentifier": "user", "baseClassTypeIdentifier": "base-entity",
      "properties": [{"name": "email", "primitiveType": "String"}],
      "customCode": [{"code": "getDisplayName(): string { return this.email; }"}]}
  ]
}
```

### Pattern C — Generic + concrete instantiation
```json
{
  "classes": [
    {"name": "Repository", "typeIdentifier": "repo-generic",
      "genericArguments": [{"name": "T", "constraintTypeIdentifier": "base-entity",
        "propertyName": "items", "isArrayProperty": true}],
      "customCode": [
        {"code": "add(item: T): void { this.items.push(item); }"},
        {"code": "getAll(): T[] { return this.items; }"}
      ]},
    {"name": "UserRepository", "typeIdentifier": "user-repo",
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

### Pattern D — Array & dictionary virtual types
```json
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
Then reference with `{"name": "users", "typeIdentifier": "user-list"}`.

### Pattern E — Enum + class that uses it
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

### Pattern F — Service with external DI
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
      {"code": "getAll(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
        "templateRefs": [{"placeholder": "$list", "typeIdentifier": "user-array"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}]
}
```

### Pattern G — customFiles for type aliases / barrels
```json
{
  "customFiles": [{
    "name": "types", "path": "shared", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Email = string;"},
      {"code": "export type ResultSet<T> = { data: T[]; total: number; page: number; };"}
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers", "typeIdentifier": "user-helper",
    "customImports": [{"path": "shared-types", "types": ["UserId", "Email"]}],
    "customCode": [{"code": "static format(email: Email): string { return email.trim(); }"}]
  }]
}
```
The `identifier` on the customFile lets `customImports.path` resolve relative to it automatically.

### Pattern H — Interface with method signatures (so a class can `implements` it)
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
**Important**: write method signatures as `customCode` strings ending in `;`. Do NOT use function-typed properties (`type: "() => Promise<User[]>"`) — implementing classes will then get duplicate property declarations.

---

## Output structure (generate_code response)

When `dryRun: false` (default), files are written under `outputPath`. The response is a textual summary listing each generated file.

When `dryRun: true`, the response includes the file contents inline so you can review without touching the disk. **Use `dryRun: true` for benchmark / preview runs** if you don't want to write files.

Each generated file is named by the `fileName` (override) or by deriving kebab/PascalCase from `name` per language convention. Path prefixes come from `path`. Imports between generated files are computed automatically from the relative paths, so `path` matters for the resulting import statements.

---

## Common mistakes (each one ruins a generation; check before submitting)

1. Referencing a `typeIdentifier` that doesn't exist anywhere in the batch → property silently dropped.
2. Putting method signatures as function-typed properties on an interface that a class will implement → duplicate property declarations on the impl.
3. Writing internal type names as raw strings inside `customCode` (e.g. `"private repo: IUserRepository"`) → no import generated, especially fatal in C#. Use templateRefs.
4. Adding stdlib imports (`System.*`, `typing.*`, `java.util.*`) to `customImports` → duplication / errors. Only external libs go here.
5. Listing constructor-parameter names in `properties[]` (C#/Java/Go/Groovy) → "Sequence contains more than one matching element".
6. Splitting related types across multiple `generate_code` calls → cross-references silently break.
7. Using reserved words as property names (`delete`, `class`, `import`) → compile errors.
8. Forgetting `fileName` on an `I`-prefixed interface in TS when its impl class would collide.
9. C#: assuming `Number` → `double`. It's `int`. Use `"type": "decimal"` or `"type": "double"` explicitly.
10. C#: using `arrayTypes` when you actually want a mutable `List<T>`. ArrayTypes → `IEnumerable<T>` in C#. Use `"type": "List<$user>"` + `templateRefs` instead.

---

## Decision flow when receiving a spec

1. Identify every entity (class, interface, enum, type alias, generic, collection).
2. Assign each one a unique `typeIdentifier` (kebab-case is conventional).
3. Decide for each whether it is: class, interface, enum, arrayType, dictionaryType, concreteGenericClass/Interface, or customFile.
4. For classes: list scalar/typed fields in `properties[]`; constructor-injected fields in `constructorParameters[]`; methods, initialized DI fields, getters/setters in `customCode[]`.
5. Anywhere a string literal mentions another batched type, write `$placeholder` and add a `templateRefs` entry.
6. Build one JSON object with `language` + the relevant arrays and call `mcp__metaengine__generate_code` exactly once.
7. If you hit "type was not generated" or import is missing, the cause is almost always a missing `typeIdentifier` or a missing `templateRefs` entry — never a need for a second call.

---

## Tools you should NOT use during generation

- `mcp__metaengine__metaengine_initialize` is a docs helper. Don't call it again at gen time — the brief above is the substitute.
- Don't call `generate_code` more than once per spec. Don't split by domain, by file, or by layer. One batch.
- Don't manually `Write` files when MetaEngine can produce them — that's the whole point.

