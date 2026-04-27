# MetaEngine MCP — Knowledge Brief (TypeScript focus)

MetaEngine is a semantic code generator exposed via MCP. You describe types,
relationships, and members as structured JSON, and MetaEngine emits compilable
source files with correct cross-file imports, language idioms, and naming
conventions. One well-formed call replaces dozens of file writes and resolves
references the way a compiler would.

Target languages: typescript, csharp, python, go, java, kotlin, groovy, scala,
swift, php, rust.

---

## Tools exposed by the metaengine MCP server

- `mcp__metaengine__metaengine_initialize(language?)` — returns the AI guide
  (rules, patterns, language notes). Free to call; cheap; informational only.
- `mcp__metaengine__generate_code(spec)` — THE main tool. Accepts a single JSON
  spec describing classes/interfaces/enums/customFiles/etc. and writes files.
  Cross-references resolve only within one call → batch the entire model.
- `mcp__metaengine__load_spec_from_file({specFilePath, outputPath?, dryRun?,
  skipExisting?})` — same as generate_code but reads the spec from a JSON file
  on disk. Use this for very large specs to avoid context bloat. Spec file uses
  identical JSON shape as `generate_code`.
- `mcp__metaengine__generate_openapi({framework, openApiSpec|openApiSpecUrl,
  ...frameworkOptions})` — generates a typed HTTP client from OpenAPI for one
  of: angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi,
  csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession.
- `mcp__metaengine__generate_graphql({framework, graphQLSchema, ...})` — same
  framework set, generates from a GraphQL SDL string.
- `mcp__metaengine__generate_protobuf({framework, protoSource, ...})` — same
  idea, from a `.proto` source.
- `mcp__metaengine__generate_sql({language, ddlSource, ...})` — generates typed
  model classes from SQL DDL (CREATE TABLE) for the language list above.

There are also `metaengine-toolkit` MCP tools (`triage`, `backlog`, `explore`,
…) — those are for project workflow, not code generation. Ignore them for the
generation task.

---

## generate_code — full input schema

Top-level fields (all optional except `language`):

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php|rust` |
| `outputPath` | string | Output directory. Default `"."`. |
| `packageName` | string | Module/namespace. Lang-specific defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. For C# omit/empty → no namespace declaration (GlobalUsings). |
| `initialize` | bool (false) | Initialize properties with default values. |
| `skipExisting` | bool (true) | Skip writing files that already exist. |
| `dryRun` | bool (false) | Preview only; returns generated file contents in the response, no disk writes. |
| `classes` | Class[] | Class definitions (regular and generic templates). |
| `interfaces` | Interface[] | Interface definitions (regular and generic templates). |
| `enums` | Enum[] | Enum definitions. |
| `customFiles` | CustomFile[] | Files WITHOUT class wrapper (type aliases, barrels, utilities). |
| `arrayTypes` | ArrayType[] | Reusable array type refs — NO files generated. |
| `dictionaryTypes` | DictionaryType[] | Reusable dict refs — NO files generated. |
| `concreteGenericClasses` | ConcreteGenericClass[] | Inline `Repository<User>` refs — NO files generated. |
| `concreteGenericInterfaces` | ConcreteGenericInterface[] | Inline interface refs — NO files generated. |

### Class object

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | Unique identifier used by other items to reference this class. |
| `path` | string | Directory under `outputPath` (e.g., `services`, `services/auth`). |
| `fileName` | string | Override file name (no extension). |
| `comment` | string | Class-level doc comment. |
| `isAbstract` | bool | |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class (or of a `concreteGenericClasses.identifier`). |
| `interfaceTypeIdentifiers` | string[] | typeIdentifiers of interfaces to implement. |
| `genericArguments` | GenericArg[] | Makes this a generic class template (`Repository<T>`). |
| `constructorParameters` | Param[] | Constructor params. **In C#/Java/Go/Groovy these auto-create properties — do NOT also list them in `properties`.** In TypeScript with `public` modifier the same auto-property emission happens (see Example 6). |
| `properties` | Property[] | Type declarations only (no logic, no initialization). |
| `customCode` | CodeBlock[] | One block per member: methods, initialized fields, anything with logic. |
| `decorators` | Decorator[] | Class-level decorators/attributes. |
| `customImports` | Import[] | External library imports only — never std/framework. |

### Property object

| Field | Notes |
|---|---|
| `name` | Property name. Avoid reserved words (`delete`, `class`, `import`). |
| `primitiveType` | One of `String|Number|Boolean|Date|Any`. |
| `typeIdentifier` | Reference to another generated type (class/enum/array/dict/concreteGeneric). |
| `type` | Raw type expression — use this for complex types like `Map<string, $resp>`. |
| `templateRefs` | `[{placeholder, typeIdentifier}]` — required when `type` contains internal-type placeholders (`$foo`). |
| `isOptional` | Marks property optional/nullable. |
| `isInitializer` | Add default-value initialization. |
| `decorators` | `[{code, templateRefs?}]` — e.g. `@IsEmail()`, `@Required()`. |
| `comment` | Doc comment. |
| `commentTemplateRefs` | templateRefs usable inside the comment. |

### CodeBlock (used by `customCode`, `decorators`, etc.)

```jsonc
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

One `customCode` entry = exactly one member (method, getter, initialized field).
MetaEngine inserts blank lines between blocks automatically.

### Interface object

Same shape as Class but no `constructorParameters`/`baseClassTypeIdentifier`.
`interfaceTypeIdentifiers` extends other interfaces. Interface method *signatures*
go in `customCode`, not as function-typed properties (see Common Mistakes).

### Enum object

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 2}],
  "fileName": "order-status",
  "path": "models",
  "comment": "Lifecycle states for orders"
}
```

Enums get a language-appropriate filename suffix automatically (`order-status.enum.ts`,
`OrderStatus.cs`, etc.).

### CustomFile object

Files without a class wrapper. Use for type aliases, barrel exports, utility modules.

```jsonc
{
  "name": "types",
  "path": "shared",
  "identifier": "shared-types",   // optional; lets other files import via this id
  "customCode": [{"code": "export type UserId = string;"}],
  "customImports": [...]
}
```

Other files reference it via `customImports: [{ path: "shared-types" }]` (the
identifier resolves to the right relative path automatically).

### ArrayType / DictionaryType (virtual, no files)

```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
  {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
]
```

```jsonc
"dictionaryTypes": [
  {"typeIdentifier": "scores",       "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-lookup",  "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
  {"typeIdentifier": "by-user",      "keyTypeIdentifier": "user",  "valuePrimitiveType": "String"},
  {"typeIdentifier": "rich-meta",    "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata"}
]
```

Reference them via `typeIdentifier` in a property — they don't produce files,
they only let you say "this property is `Array<User>`" or `"Record<string, User>"`.

In TypeScript these emit `Array<T>` and `Record<K, V>`.
In **C#**, `arrayTypes` emit `IEnumerable<T>`. If you need `List<T>`, skip the
arrayType and use `"type": "List<$user>", "templateRefs": [...]` directly.

### concreteGenericClasses / concreteGenericInterfaces (virtual, no files)

Materializes `Repository<User>` as a referenceable type:

```jsonc
"concreteGenericClasses": [{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}]
```

A class can then `extends Repository<User>` via
`"baseClassTypeIdentifier": "user-repo-concrete"`. customCode can reference it
via templateRefs. No file is produced for the concrete instantiation itself.

### GenericArg (used by `genericArguments`)

```jsonc
{
  "name": "T",
  "constraintTypeIdentifier": "base-entity",   // emits `T extends BaseEntity`
  "propertyName": "items",                      // creates a property `items: T[]` (or `T`)
  "isArrayProperty": true                       // makes that property `T[]`
}
```

### customImports

```jsonc
"customImports": [
  {"path": "@angular/core", "types": ["Injectable", "inject"]},
  {"path": "rxjs",          "types": ["Observable"]}
]
```

Only for **external libraries**. Never list standard-library types — see the
auto-import table below.

---

## Critical rules (most failures violate one of these)

### 1. ONE `generate_code` call for the whole batch
`typeIdentifier` cross-references resolve only inside the current call. Two
calls → broken/missing imports between them. Build the entire spec, then call
once. (The benchmark explicitly enforces a single call.)

### 2. `properties` = type declarations. `customCode` = everything else.
- A property describes a typed field with no body and no initializer.
- A customCode block is a method, an initialized field, or anything containing
  logic. Exactly one member per block.
- Never declare methods as function-typed properties. Never declare bare typed
  fields inside customCode.

### 3. `templateRefs` for every internal type used inside `customCode`/`type`/decorators
Whenever a string of code references a type defined in this same call, write
the reference as `$placeholder` and add a `templateRefs` entry mapping the
placeholder → typeIdentifier. This is what triggers MetaEngine to add the
correct import/using statement.

In **C#** this is non-negotiable: a raw type name in customCode that crosses
namespaces will compile-fail because no `using` is generated.

In **TypeScript** raw inline names sometimes work for same-folder refs but are
fragile — always use templateRefs to be safe.

### 4. Never list framework/std-lib types in `customImports`
MetaEngine auto-imports per language:

| Language | Auto-imported (don't specify) |
|---|---|
| C# | System.\*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.\* |
| Python | typing.\*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | java.util.\*, java.time.\*, java.util.stream.\*, java.math.\*, jakarta.validation.\*, jackson.\* |
| Kotlin | java.time.\*, java.math.\*, java.util.UUID, kotlinx.serialization.\* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, … |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, …) |
| Rust | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy | java.time.\*, java.math.\*, java.util (UUID, Date), java.io (File, InputStream, OutputStream) |
| Scala | java.time.\*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.\* |
| PHP | DateTime\*, DateTimeImmutable, Exception\*, ArrayObject, JsonSerializable, Stringable |
| TypeScript | (no imports needed — built-in types) |

`customImports` is **only** for external libraries (`@angular/core`,
`FluentValidation`, `rxjs`, etc.).

### 5. `templateRefs` are ONLY for internal (same-batch) types
External library types must come in via `customImports`. Never mix the two
mechanisms.

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy and TS-public)
Listing the same name in both `constructorParameters` and `properties` throws
"Sequence contains more than one matching element". Put shared fields only in
`constructorParameters`, and add unrelated fields only in `properties`.

### 7. Virtual types never produce files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`,
`concreteGenericInterfaces` are reference-only. They exist solely to be cited by
`typeIdentifier` from a property or `baseClassTypeIdentifier` of a real type.

### 8. Interface method signatures go in `customCode`, not in `properties`
If a class will `implements` an interface and the interface method is declared
as a function-typed property, the implementing class will then re-declare those
signatures as properties side-by-side with the customCode methods → duplicate
members. Always put method signatures in the interface's `customCode`.

### 9. Avoid reserved words as property names
`delete`, `class`, `import`, etc. Use safe alternatives (`remove`, `clazz`,
`importData`).

---

## Pattern cookbook

### Two interfaces, cross-referencing

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
Two files, automatic `import { Address } from './address'` in `user.ts`.

### Class with inheritance + a method

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
Generates `class UserRepository extends Repository<User>` with all imports.

### Array + dictionary plumbing

```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"}
],
"dictionaryTypes": [
  {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String",
   "valueTypeIdentifier": "user"}
]
```
Then on a class: `"properties": [{"name": "users", "typeIdentifier": "user-list"}]`.

### Complex inline type expression

```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

### Enum + a class that uses it

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
    "name": "ApiService", "typeIdentifier": "api-service", "path": "services",
    "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
    "customImports": [
      {"path": "@angular/core", "types": ["Injectable", "inject"]},
      {"path": "@angular/common/http", "types": ["HttpClient"]},
      {"path": "rxjs", "types": ["Observable"]}
    ],
    "customCode": [
      {"code": "private http = inject(HttpClient);"},
      {"code": "private baseUrl = '/api/users';"},
      {"code": "getAll(): Observable<$list> { return this.http.get<$list>(this.baseUrl); }",
       "templateRefs": [{"placeholder": "$list", "typeIdentifier": "user-array"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}]
}
```

### customFiles for type aliases / barrel exports

```jsonc
{
  "customFiles": [{
    "name": "types", "path": "utils", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"}
    ]
  }],
  "classes": [{
    "name": "UserService", "path": "services",
    "customImports": [{"path": "shared-types"}],
    "customCode": [
      {"code": "format(id: UserId): string { return id.trim(); }"}
    ]
  }]
}
```

### Interface with method signatures (for a class to implement)

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
Use `fileName` to dodge collisions with the implementing class file in TS
(MetaEngine strips the `I` prefix from the exported name).

### Constructor parameters — the right way (TS Example 6)

WRONG (errors with "Sequence contains more than one matching element"):
```jsonc
"constructorParameters": [{"name": "email", "type": "string"}],
"properties":            [{"name": "email", "type": "string"}]
```
RIGHT — list shared fields only in `constructorParameters`, additional fields
only in `properties`:
```jsonc
"constructorParameters": [
  {"name": "email", "type": "string"},
  {"name": "status", "typeIdentifier": "status"}
],
"properties": [
  {"name": "createdAt", "primitiveType": "Date"}
]
```
Output:
```ts
import { Status } from './status.enum';

export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

---

## Language-specific notes

### TypeScript (primary for this run)
- `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` →
  `Date`, `Any` → `unknown`.
- Interface names get the leading `I` stripped from the **exported** name
  (`IUserRepository` → `UserRepository`). To prevent file-name collisions with
  an implementing class, set `"fileName": "i-user-repository"` on the
  interface.
- File names are kebab-case (`user-repository.ts`, `order-status.enum.ts`).
- Method names typically remain camelCase; arrayTypes emit `Array<T>`;
  dictionaryTypes emit `Record<K, V>`.
- Customcode newlines are auto-indented; you don't need to pad.
- TS classes do not need framework imports for built-in types.
- Constructor params with `public`/`private` auto-emit properties (Example 6).

### C#
- Interface `I` prefix is **preserved**.
- `Number` → `int` (not `double`!). Use `"type": "decimal"` or
  `"type": "double"` explicitly when needed.
- `packageName` becomes the namespace; omit/empty → no namespace declaration
  (use with GlobalUsings).
- Interface properties → `{ get; }`; class properties → `{ get; set; }`.
- `arrayTypes` → `IEnumerable<T>`. For `List<T>`, use
  `"type": "List<$user>"` with templateRefs.
- `isOptional` → nullable reference type (`string?`).

### Python
- You **must** include explicit indentation (4 spaces) after `\n` in customCode
  blocks.
- typing imports (`List`, `Dict`, `Optional`, …) are automatic; pydantic
  (`BaseModel`, `Field`) is automatic.
- The judge in this benchmark tolerates idiomatic transformations (e.g.
  `snake_case` method names).

### Java
- `packageName` defaults to `com.metaengine.generated`.
- Constructor params auto-emit properties (don't duplicate in `properties`).
- `java.util.*`, `java.time.*`, `jakarta.validation.*`, `jackson.*` are auto-imported.
- The judge tolerates `ALL_CAPS` enum names per Java idiom.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions inside `customCode`.
- Constructor params auto-emit fields when used.

### Other languages
Same general patterns; let MetaEngine's auto-imports handle stdlib. Use
`packageName` where the language demands a package/namespace declaration
(Kotlin/Groovy/Scala/Java/Rust crateName/etc.).

---

## Output structure

- One file per file-emitting type (class, interface, enum, customFile).
- File location: `<outputPath>/<path>/<fileName-or-derived-name>.<ext>`.
- File name is derived from the type name in language-idiomatic style if
  `fileName` is not set (TS: kebab-case, C#: PascalCase, Python: snake_case,
  Go: lower_snake, etc.).
- Cross-file imports are added automatically based on `typeIdentifier` /
  `templateRefs` references.
- `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`,
  `concreteGenericInterfaces` produce **no files** — they are pure references.
- With `dryRun: true`, no files are written; the response contains the file
  contents for inspection.
- With `skipExisting: true` (default), pre-existing files on disk are not
  overwritten — useful for stub/scaffold patterns where humans have edited
  generated files.

---

## Common mistakes — checklist before calling generate_code

1. Referenced a `typeIdentifier` that doesn't exist in this batch → the
   property/reference is silently dropped. Verify every typeIdentifier matches
   a defined item.
2. Declared interface methods as function-typed properties → implementing class
   double-declares them. Put method sigs in `customCode`.
3. Wrote raw internal type names inside `customCode` strings → missing imports
   (always fatal in C# across namespaces). Use `$placeholder` + `templateRefs`.
4. Used `arrayTypes` in C# but expected `List<T>`. Use `"type": "List<$x>"`
   with templateRefs instead.
5. Listed std-lib types (`System.*`, `typing.*`, `java.util.*`, …) in
   `customImports`. Don't — they're auto-imported.
6. Duplicated constructor parameters in `properties` (C#/Java/Go/Groovy/TS
   public params) → "Sequence contains more than one matching element".
7. Used reserved words (`delete`, `class`, `import`) as property names.
8. Split related types across multiple `generate_code` calls — cross-batch refs
   never resolve. Build everything, then call once.
9. Expected `Number` to mean `double` in C#. It maps to `int`.
10. In TypeScript, an `I`-prefixed interface and its implementing class
    collide on file name. Set the interface's `fileName` (e.g.
    `i-user-repository`).

---

## Operational notes for the upcoming generation session

- This benchmark intentionally enforces **a single `generate_code` call** with
  the full spec. Don't iterate per-domain — splitting breaks the typegraph.
- Idiomatic name transforms (Java `ALL_CAPS` enum members, Python `snake_case`
  method names) are **expected** behavior; the judge tolerates them.
- Use `dryRun: true` only if you want to inspect output before committing it
  to disk. Default behavior writes files into `outputPath`.
- For TypeScript runs: no `packageName` needed; `customImports` are only for
  third-party libraries.
- If the spec is large, you can pre-write it to a JSON file and call
  `load_spec_from_file` to keep the conversation context lean. Same JSON shape.

