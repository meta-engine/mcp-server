# MetaEngine MCP — Knowledge Brief (TypeScript focus)

MetaEngine is a semantic code generator exposed as an MCP server. You describe types, relationships, and methods as a structured JSON spec; the engine produces compilable, correctly-imported source files. Cross-references, imports, language idioms, and file naming are handled automatically — so a single well-formed call replaces dozens of error-prone Write/Edit operations.

Targets: TypeScript, Python, Go, C#, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust.

---

## Tools exposed by this MCP server

- `mcp__metaengine__metaengine_initialize(language?)` — returns the AI guide. Already called during warmup.
- `mcp__metaengine__generate_code(...)` — main tool. Generates source files from a typed spec. **Use this**.
- `mcp__metaengine__load_spec_from_file({specFilePath, outputPath?, skipExisting?, dryRun?})` — load a spec from a `.json` file instead of inline.
- `mcp__metaengine__generate_openapi(...)` — HTTP clients from OpenAPI for many frameworks (angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi, csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession).
- `mcp__metaengine__generate_graphql(...)` — HTTP clients from GraphQL SDL.
- `mcp__metaengine__generate_protobuf(...)` — HTTP clients from `.proto`.
- `mcp__metaengine__generate_sql({language, ddlSource, ...})` — model classes from `CREATE TABLE` DDL.

For arbitrary code (DTOs, services, controllers, repositories, etc.), `generate_code` is the right tool.

Two MCP resources exist (already read):
- `metaengine://guide/ai-assistant` — the guide (mirrors `metaengine_initialize` output)
- `metaengine://guide/examples` — input/output worked examples

---

## generate_code — full input schema

Top-level (only `language` is strictly required):

| Field | Type | Notes |
|---|---|---|
| `language` | enum | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `packageName` | string | Namespace/package/module. For C#: omit/empty → no namespace (GlobalUsings). Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. Not used by TypeScript. |
| `outputPath` | string | Output directory. Default `.`. |
| `skipExisting` | bool | Default `true`. Skip overwriting existing files (stub pattern). |
| `dryRun` | bool | Default `false`. If `true`, returns file contents in response without writing. |
| `initialize` | bool | Default `false`. Initialize properties with default values. |
| `classes[]` | array | Class definitions (regular and generic templates). |
| `interfaces[]` | array | Interface definitions (regular and generic templates). |
| `enums[]` | array | Enum definitions. |
| `arrayTypes[]` | array | **Virtual** reusable array references — NO files generated. |
| `dictionaryTypes[]` | array | **Virtual** reusable map references — NO files generated. |
| `concreteGenericClasses[]` | array | **Virtual** `Repository<User>`-style references — NO files generated. |
| `concreteGenericInterfaces[]` | array | Same as above for interfaces. |
| `customFiles[]` | array | Files without a class wrapper (type aliases, barrel exports, utility funcs). |

### `classes[]` item

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | Unique handle used by every other reference. |
| `path` | string | Subdirectory (e.g. `models`, `services/auth`). |
| `fileName` | string | Override file name (no extension). |
| `comment` | string | Doc comment. |
| `isAbstract` | bool | |
| `baseClassTypeIdentifier` | string | Refers to a class or `concreteGenericClasses` identifier. |
| `interfaceTypeIdentifiers` | string[] | Interfaces (or `concreteGenericInterfaces` identifiers) to implement. |
| `genericArguments[]` | array | Makes this a generic class template. Each entry: `{name, constraintTypeIdentifier?, propertyName?, isArrayProperty?}`. `propertyName`+`isArrayProperty` auto-creates a property of type `T` or `T[]`. |
| `properties[]` | array | See below. **Type-only declarations.** |
| `constructorParameters[]` | array | `{name, primitiveType?|type?|typeIdentifier?}`. In C#/Java/Go/Groovy these auto-become properties — DO NOT also list them in `properties[]`. |
| `customCode[]` | array | Method bodies, initialized fields. **One member per item.** Each: `{code, templateRefs?[]}`. |
| `customImports[]` | array | External lib imports only. Each: `{path, types?[]}`. |
| `decorators[]` | array | `{code, templateRefs?[]}`. |

### `interfaces[]` item
Same shape as classes but typically lighter. Method **signatures** go in `customCode` (as `methodName(...): T;`) — not as function-typed properties. `interfaceTypeIdentifiers` extends other interfaces.

### `enums[]` item
`{name, typeIdentifier, members[{name, value(number)}], path?, fileName?, comment?}`. Filename auto-suffix: `*.enum.ts` (TS), `Foo.cs` (C#).

### `properties[]` item

| Field | Notes |
|---|---|
| `name` | Property name. |
| `primitiveType` | One of: `String`, `Number`, `Boolean`, `Date`, `Any`. |
| `typeIdentifier` | Reference to a class/interface/enum/arrayType/dictionaryType/concreteGeneric defined in this same call. |
| `type` | Raw string type expression — used with `templateRefs` for complex generics, or for external/built-in types. |
| `templateRefs[]` | `{placeholder: "$x", typeIdentifier: "x"}` — substitutes `$x` and triggers an auto-import. |
| `decorators[]` | `{code, templateRefs?}`. |
| `comment` | Doc comment. |
| `commentTemplateRefs[]` | templateRefs for the comment. |
| `isOptional` | bool. C#: yields `string?`. |
| `isInitializer` | bool. Add a default initializer. |

Exactly one of `primitiveType` / `typeIdentifier` / `type` should be present.

### `customCode[]` item
`{code: "<one member's source>", templateRefs?: [{placeholder, typeIdentifier}]}`. The engine inserts blank lines between blocks automatically. **Python**: explicit 4-space indent required after `\n` inside `code`. **TypeScript**: indentation auto-applied.

### `customImports[]` item
`{path: "@angular/core", types: ["Injectable", "inject"]}` — for **external** libraries only. Or reference a `customFiles[].identifier` to auto-resolve a relative path.

### `arrayTypes[]` item
`{typeIdentifier, elementPrimitiveType?|elementTypeIdentifier?}`. Generates no file — referenced via `typeIdentifier` in properties. TS output: `Array<T>` / `T[]`. **C# caveat**: emits `IEnumerable<T>`; for `List<T>` use a property with `"type": "List<$user>"` + templateRefs instead.

### `dictionaryTypes[]` item
`{typeIdentifier, keyPrimitiveType?|keyTypeIdentifier?|keyType?, valuePrimitiveType?|valueTypeIdentifier?}`. All four key/value combinations of primitive vs custom are supported. TS output: `Record<K, V>`.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` item
`{identifier, genericClassIdentifier, genericArguments: [{typeIdentifier?|primitiveType?}]}`. Creates a virtual `Repository<User>` reference. Use the `identifier` in another class's `baseClassTypeIdentifier` or in templateRefs.

### `customFiles[]` item
`{name, path?, fileName?, identifier?, customCode[], customImports?[]}`. Generates a file with no class wrapper — perfect for type aliases, barrel exports, utility constants. Set `identifier` so other generated files can `customImports` against it.

---

## The seven critical rules

1. **One call, all related types.** `typeIdentifier` references resolve only inside the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks the typegraph and silently drops references.

2. **Properties = declarations only. CustomCode = everything with logic.** `properties[]` declares typed fields — no initializers, no methods. Any method body, any initialized field (`private http = inject(...)`), any logic goes in `customCode[]`. **One `customCode` entry = exactly one member.**

3. **Use templateRefs for internal types inside customCode.** Reference internal types via `$placeholder` syntax, then declare `templateRefs: [{placeholder: "$user", typeIdentifier: "user"}]`. Without templateRefs, the engine cannot generate the required import. Raw type names embedded in `code` strings will compile-fail across files/namespaces (especially in C#).

4. **Never declare framework imports in `customImports`.** Standard-lib types are auto-imported. Adding them manually causes duplication or errors. Auto-imported per language:
   - **TypeScript**: nothing needs importing for built-ins.
   - **C#**: `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*`.
   - **Python**: `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`.
   - **Java**: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, jackson.
   - **Kotlin**: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`.
   - **Go**: `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, more.
   - **Swift**: Foundation (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`).
   - **Rust**: `std::collections` (`HashMap`, `HashSet`), `chrono`, `uuid`, `rust_decimal`, `serde`.
   - **Groovy**: `java.time.*`, `java.math.*`, `java.util` (`UUID`, `Date`), `java.io`.
   - **Scala**: `java.time.*`, `scala.math` (`BigDecimal`, `BigInt`), `java.util.UUID`, `scala.collection.mutable.*`.
   - **PHP**: `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable`.
   Use `customImports` only for genuine external libs (`@angular/core`, `rxjs`, `FluentValidation`, etc.).

5. **templateRefs are ONLY for internal types.** Same call → `typeIdentifier`/`templateRefs`. External library → `customImports`. Never substitute one for the other.

6. **Constructor params auto-create properties** in C#/Java/Go/Groovy. Don't list them again in `properties[]` — that yields "Sequence contains more than one matching element". Only put *additional* (non-constructor) fields in `properties[]`.

7. **Virtual types don't produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` exist only to be referenced. They never appear in the file list.

---

## TypeScript-specific notes

- Built-in primitives map: `String`→`string`, `Number`→`number`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`.
- **`I` prefix on interfaces is stripped** from the exported name (`IUserRepository` → exported as `UserRepository`). To avoid file-name collision with an implementing class of the same logical name, set `fileName: "i-user-repository"` on the interface.
- Decorators are emitted directly (no special TS-specific config).
- Auto indentation for `\n` inside customCode — write methods naturally on one line or with raw newlines; engine formats them.
- `arrayTypes` output is `Array<T>` / `T[]`. `dictionaryTypes` output is `Record<K, V>`.
- Constructor parameters in TS produce parameter properties: `constructor(public email: string, public status: Status) {}`.
- Filenames default to kebab-case from the class/interface name (`UserService` → `user-service.ts`).
- Enum filenames suffix with `.enum.ts`.
- `packageName` is unused for TS.

---

## Pattern catalogue (TypeScript-flavoured)

### Cross-referenced interfaces
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
Two files; the import from `User` to `Address` is generated automatically.

### Inheritance + a method
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

### Generic class + concrete instantiation
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
       {"code": "getAll(): T[] { return this.items; }"},
       {"code": "findById(id: string): T | undefined { return this.items.find(i => i.id === id); }"}
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
Yields `Repository<T extends BaseEntity>` plus `class UserRepository extends Repository<User>` with imports.

### Array / dictionary virtual types
```jsonc
{
  "arrayTypes": [
    {"typeIdentifier": "user-list",    "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
    {"typeIdentifier": "by-user",     "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata"}
  ]
}
```
Reference via `"typeIdentifier": "user-list"` in a property. TS emits `Array<User>` / `Record<string, number>` / `Record<string, User>` / `Record<User, Metadata>`.

### Complex type expressions
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
templateRefs work in `properties.type`, `properties.comment` (via `commentTemplateRefs`), `customCode.code`, and `decorators.code`.

### Enum + class using it
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

### Service with external DI imports (Angular/NestJS-style)
```jsonc
{
  "classes": [{
    "name": "PetService", "typeIdentifier": "pet-service", "path": "services",
    "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
    "customImports": [
      {"path": "@angular/core",            "types": ["Injectable", "inject"]},
      {"path": "@angular/common/http",     "types": ["HttpClient"]},
      {"path": "rxjs",                     "types": ["Observable"]}
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
  }],
  "arrayTypes": [{"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}]
}
```

### Type aliases via customFiles
```jsonc
{
  "customFiles": [{
    "name": "types", "path": "utils", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Timestamp = number;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"},
      {"code": "export type ResultSet<T> = { data: T[]; total: number; page: number; };"}
    ]
  }],
  "classes": [{
    "name": "UserService", "path": "services",
    "customImports": [{"path": "../utils/types", "types": ["UserId", "Status", "ResultSet"]}],
    "customCode": [
      {"code": "async getUser(id: UserId): Promise<User> { return null as any; }"},
      {"code": "updateStatus(id: UserId, status: Status): void { }"}
    ]
  }]
}
```
You can also reference the customFile's `identifier` instead of a relative `path` for auto-resolution.

### Interface that a class implements (TS/C#)
Define method signatures in `customCode`, NOT as function-typed properties:
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
Function-typed properties on an interface (`"type": "() => Promise<User[]>"`) cause the implementing class to duplicate them as fields alongside the methods you write — don't do that.

---

## Output structure

- One file per `class`, `interface`, `enum`, or `customFile`.
- File names default to kebab-case (TypeScript) or PascalCase (C#) of the entity name; override with `fileName`. Enums get a `.enum.ts` suffix in TS.
- Files land under `outputPath` (default `.`) plus the entity's `path` (subdir). When `dryRun: true`, file contents are returned in the response body and nothing is written.
- Imports are resolved automatically: relative paths between generated files; auto-imports for stdlib types (per the language table); explicit imports from `customImports` for external libs.
- Constructor params become parameter properties (TS): `constructor(public email: string) {}`. In C#/Java/Go/Groovy they become regular properties.
- `arrayTypes`/`dictionaryTypes`/`concreteGeneric*` produce **no files** — they're handles only.

---

## Common mistakes (verbatim)

1. Referencing a `typeIdentifier` that isn't in the batch → property silently dropped. Verify every identifier exists.
2. Putting method signatures as function-typed properties on an interface that a class will `implements`. Use `customCode` for signatures.
3. Writing internal type names as raw strings in `customCode` (`"private repo: IUserRepository"`). Use templateRefs.
4. Using `arrayTypes` in C# expecting `List<T>`. It emits `IEnumerable<T>`. Use `"type": "List<$user>"` + templateRefs.
5. Adding `System.*`, `typing.*`, `java.util.*` to `customImports`. Let the engine handle stdlib.
6. Duplicating constructor params in `properties` for C#/Java/Go/Groovy.
7. Reserved-word property names (`delete`, `class`, `import`). Rename to `remove`, `clazz`, `importData`.
8. Splitting related types across multiple `generate_code` calls. Cross-file imports only resolve within one batch.
9. Expecting `Number` to map to `double` in C#. It maps to `int`. Use `"type": "decimal"` or `"type": "double"`.
10. Filename collision between `IFoo` interface and `Foo` class in TS. Set `fileName: "i-foo"` on the interface.

---

## Generation workflow (recommended)

1. **Inventory the spec.** Identify every type, enum, array/dictionary virtual, generic, customFile, and external import.
2. **Assign `typeIdentifier`s.** Stable kebab-case handles (`user`, `user-repo`, `user-array`).
3. **Decide where each member lives.** Plain typed field → `properties`. Initialized field, method body, parameter property assignment → `customCode`. Constructor params (which auto-promote in C#/Java/Go/Groovy) → `constructorParameters`.
4. **Wire references.** Same-batch types via `typeIdentifier` (in props) or `templateRefs` (in `customCode`/`type`/`decorators`). External libs only via `customImports`.
5. **Build virtuals.** `arrayTypes`/`dictionaryTypes` for collection shapes; `concreteGenericClasses` for `Repository<User>` etc.
6. **Single call.** Pass everything to `mcp__metaengine__generate_code` once. Never split.
7. **Set `dryRun: true`** during exploration to inspect output without writing. Set `outputPath` to control where files land.

If something looks wrong in the output, don't hand-patch — re-run with a corrected spec or escalate as MetaEngine feedback (`/triage`).
