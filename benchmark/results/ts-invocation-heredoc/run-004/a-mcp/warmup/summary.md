# MetaEngine MCP — Knowledge Brief (TypeScript Focus)

MetaEngine is a **semantic code generator** exposed via MCP. You describe types, relationships, and method bodies as structured JSON; the engine emits compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templating, it resolves cross-references, manages imports, and applies language idioms automatically. **One well-formed JSON call replaces dozens of hand-written file writes.**

---

## Tools Exposed

- **`mcp__metaengine__generate_code`** — The primary tool. Takes a structured JSON spec (classes, interfaces, enums, arrayTypes, dictionaryTypes, concreteGenericClasses/Interfaces, customFiles) plus `language`, optional `packageName`, `outputPath`, `initialize`, `dryRun`, `skipExisting`. Writes files to disk (or returns them when `dryRun: true`).
- **`mcp__metaengine__load_spec_from_file`** — Loads a JSON spec from a `.json` file on disk and runs it. Same surface as `generate_code`. Use for large/complex specs to avoid bloating context.
- **`mcp__metaengine__metaengine_initialize`** — Returns the AI-assistant guide and pattern reference (already consumed in this warmup).
- **`mcp__metaengine__generate_openapi`** — Generates HTTP clients from OpenAPI specs (Angular, React, TS Fetch, Go, Java Spring, Python FastAPI, C# HttpClient, Kotlin Ktor, Rust Reqwest, Swift URLSession).
- **`mcp__metaengine__generate_graphql`** — Generates HTTP clients from GraphQL SDL (same framework set).
- **`mcp__metaengine__generate_protobuf`** — Generates HTTP clients from `.proto` definitions (same framework set, Python uses `python-httpx`).
- **`mcp__metaengine__generate_sql`** — Generates typed model classes from SQL DDL (CREATE TABLE statements). Supports all 11 languages.

For this benchmark we use **`generate_code`** with the full spec in **a single call**.

---

## Cardinal Rule: ONE call, full spec

`typeIdentifier` references resolve **only within the current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks the typegraph: cross-file imports won't be generated, references silently drop. Bundle every interface/class/enum/customFile that needs to interlink.

---

## `generate_code` — Full Input Schema

### Top-level fields

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `typescript` / `python` / `go` / `csharp` / `java` / `kotlin` / `groovy` / `scala` / `swift` / `php` / `rust` |
| `packageName` | string | Namespace/module/package. Defaults vary: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. Omit for C# to skip namespace declaration. TypeScript ignores. |
| `outputPath` | string | Default `.` — where files are written. |
| `initialize` | boolean | Default `false`. If `true`, properties get default value initializers (`= ''`, `= 0`, `= new Array<T>()`, etc.). |
| `dryRun` | boolean | Default `false`. Returns generated file contents instead of writing them. |
| `skipExisting` | boolean | Default `true`. Don't overwrite existing files (stub pattern). |
| `classes` | array | Class definitions (regular and generic). |
| `interfaces` | array | Interface definitions (regular and generic). |
| `enums` | array | Enum definitions. |
| `arrayTypes` | array | Reusable array type aliases. **No files generated.** |
| `dictionaryTypes` | array | Reusable dictionary/map type aliases. **No files generated.** |
| `concreteGenericClasses` | array | Inline generic instantiations like `Repository<User>`. **No files.** |
| `concreteGenericInterfaces` | array | Inline generic interface instantiations. **No files.** |
| `customFiles` | array | Free-form files (type aliases, barrel exports, utility functions). |

### `classes[]` shape

| Field | Notes |
|---|---|
| `name` | Class name. |
| `typeIdentifier` | Unique key for cross-references (kebab-case convention). |
| `path` | Subdirectory (e.g. `models`, `services/auth`). |
| `fileName` | Override file name (no extension). |
| `comment` | Doc comment for the class. |
| `isAbstract` | Boolean. |
| `baseClassTypeIdentifier` | Identifier of class to extend. Reference an internal class OR a `concreteGenericClasses` identifier to extend `Repository<User>`. |
| `interfaceTypeIdentifiers` | Array of interface identifiers to implement. |
| `genericArguments` | Makes this a generic class template. Each item: `{name, constraintTypeIdentifier?, propertyName?, isArrayProperty?}`. `propertyName` auto-creates a property of type `T`; `isArrayProperty: true` makes it `T[]`. |
| `properties` | Array of property descriptors (see below). Type declarations only — no logic. |
| `constructorParameters` | Array of `{name, type?, primitiveType?, typeIdentifier?}`. **In C#/Java/Go/Groovy these auto-become properties — do NOT duplicate in `properties[]`.** |
| `customCode` | Array of `{code, templateRefs?}`. ONE per method/initialized field. Engine adds blank-line separation. |
| `decorators` | Array of `{code, templateRefs?}`. e.g. `@Injectable({ providedIn: 'root' })`. |
| `customImports` | Array of `{path, types?}` — only for **external** libraries. |

### `interfaces[]` shape
Same structure as classes (path, fileName, properties, customCode, decorators, customImports, genericArguments, interfaceTypeIdentifiers for inheritance). No `constructorParameters` or `baseClassTypeIdentifier`. **For interfaces that a class will `implements`, define method signatures in `customCode`, not as function-typed properties** — otherwise the implementing class will duplicate them.

### `enums[]` shape
`{name, typeIdentifier, path?, fileName?, comment?, members: [{name, value:number}]}`. Filenames auto-suffixed: `order-status.enum.ts` in TS, `OrderStatus.cs` in C#.

### `properties[]` shape

| Field | Notes |
|---|---|
| `name` | Property name. **Avoid reserved words** (`delete`, `class`, `import`, etc.) — use `remove`, `clazz`, `importData`. |
| `primitiveType` | One of `String` / `Number` / `Boolean` / `Date` / `Any`. |
| `typeIdentifier` | Reference to another type (class, interface, enum, arrayType, dictionaryType, concreteGeneric…). |
| `type` | Raw type expression — used for complex literal types (e.g. `"Map<string, $resp>"`, `"List<$user>"`, `"decimal"`, `"double"`). Pair with `templateRefs` when it embeds `$placeholders`. |
| `isOptional` | Boolean. In C# generates nullable reference type (`string?`). |
| `isInitializer` | Boolean. Adds default value initialization. |
| `comment` | Doc comment. Supports `commentTemplateRefs` for cross-referencing. |
| `decorators` | Array of `{code, templateRefs?}` — e.g. `@IsEmail()`, `@Required()`. |
| `templateRefs` | Array of `{placeholder, typeIdentifier}` for `$placeholder` substitutions in `type`. |

### `customCode[]` shape
`{code: string, templateRefs?: [{placeholder: string, typeIdentifier: string}]}`. ONE item = exactly ONE class member (method or initialized field). Multiple items get blank lines between them automatically.

### `customImports[]` shape
`{path: string, types?: string[]}`. Path is the import source. **Only for external libraries** — never use for stdlib types or for types defined in the same batch.

### `arrayTypes[]` shape
`{typeIdentifier, elementTypeIdentifier? | elementPrimitiveType?}`. **No file generated.** Reference via `typeIdentifier` in properties. TS output: `Array<T>`. C# output: `IEnumerable<T>` (use raw `type: "List<$x>"` for mutable lists).

### `dictionaryTypes[]` shape
`{typeIdentifier, keyPrimitiveType? | keyTypeIdentifier? | keyType?, valuePrimitiveType? | valueTypeIdentifier?}`. All four primitive/custom permutations supported. TS output: `Record<K, V>`. **No file generated.**

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` shape
`{identifier, genericClassIdentifier, genericArguments: [{typeIdentifier? | primitiveType?}]}`. Creates a virtual `Repository<User>` reference you can use as `baseClassTypeIdentifier` or in `templateRefs`. **No file generated.**

### `customFiles[]` shape
`{name, path?, fileName?, identifier?, customCode: [{code, templateRefs?}], customImports?}`. Generates a file **without** any class/interface wrapper — perfect for type aliases, barrel exports, utility functions. The optional `identifier` lets other types' `customImports` reference the file by identifier (auto-resolves the relative path).

---

## Critical Rules (failure modes)

### 1. Properties = type declarations. customCode = methods + initialized fields.
- `properties[]` only declares typed fields — never put methods or initializers there.
- `customCode[]` is for methods and any field that has an assignment (`private http = inject(HttpClient);`) or any code with logic.
- **One customCode item = one class member.**

### 2. templateRefs are for INTERNAL types only.
When `customCode` (or a property `type` string, or a decorator) references another type from the same batch, write `$placeholder` and add `templateRefs: [{placeholder: "$x", typeIdentifier: "x"}]`. This triggers the engine to generate the import. Without templateRefs, no import is emitted (works in TS at runtime if same file, fails cross-namespace in C#).

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

### 3. customImports are for EXTERNAL libraries only.
Never use customImports for types defined in the same batch (use templateRefs/typeIdentifier instead). Never use for stdlib types — those are auto-imported.

### 4. Never add framework/stdlib imports to customImports
| Language | Auto-imported (do not specify) |
|---|---|
| TypeScript | (no built-in imports needed) |
| C# | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder) |
| Rust | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream) |
| Scala | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |

`customImports` is for `@angular/core`, `rxjs`, `FluentValidation`, etc. only.

### 5. Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Putting the same name in both `constructorParameters` and `properties` raises **"Sequence contains more than one matching element"**. Put shared fields ONLY in `constructorParameters`; put additional non-constructor fields in `properties`. (TypeScript behaves the same way: constructor params with `public` modifier become properties — don't duplicate them.)

### 6. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references **only**. They produce no files. They exist solely to be referenced by `typeIdentifier` from real types.

### 7. Interface method signatures go in customCode (not properties)
For interfaces a class will `implements`, define methods in `customCode` with trailing semicolons:

```jsonc
"customCode": [
  {"code": "findAll(): Promise<$user[]>;",
   "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
]
```

If you use function-typed properties (`"type": "() => Promise<User[]>"`), the implementing class will create them as property declarations, duplicating your real methods.

### 8. Reserved words
Avoid `delete`, `class`, `import`, etc. as property/parameter names. Use safe alternatives.

### 9. Verify every typeIdentifier
A `typeIdentifier` reference that doesn't exist in the batch is **silently dropped** — the property simply disappears from output. Cross-check every reference against a defined type in the same call.

---

## Pattern Reference (TypeScript-flavored examples)

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

### Class with inheritance + method
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

### Enum + class that uses it
```jsonc
{
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 2}]
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

### Array & dictionary types
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

Reference via `"typeIdentifier": "user-list"` in properties.

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

The `concreteGenericClasses` entry creates a virtual `Repository<User>` reference; the class extends it via `baseClassTypeIdentifier`. Engine emits `extends Repository<User>` with correct imports.

### Service with external DI
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
      {"code": "getUsers(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
       "templateRefs": [{"placeholder": "$list", "typeIdentifier": "user-array"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}]
}
```

### CustomFiles for type aliases / barrel exports
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

### Complex type expressions in properties
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

`templateRefs` work in **properties.type**, **customCode.code**, and **decorators.code**.

### Interface with method signatures (TS/C#)
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

---

## Language-Specific Notes

### TypeScript (this benchmark's target)
- MetaEngine **strips the `I` prefix** from interface names. `IUserRepository` exports as `UserRepository`. Use `fileName: "i-user-repository"` to disambiguate file collisions when an `I`-prefixed interface and its implementing class share a name.
- Primitive mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- Auto-indent for newlines (`\n`) inside `customCode`.
- Decorators supported directly in `decorators[]`.
- Files are kebab-case by default; classes are PascalCase. Generated extensions: `.ts`, with `.enum.ts` for enums.

### C#
- `I` prefix is **preserved** on interface names.
- `Number` → `int` (NOT `double`). Use `"type": "decimal"` or `"type": "double"` for non-integer numbers.
- `packageName` becomes the namespace. Omit it for the GlobalUsings pattern (no namespace declaration).
- Interface properties → `{ get; }`; class properties → `{ get; set; }`.
- `arrayTypes` → `IEnumerable<T>`. For `List<T>`, use `"type": "List<$x>"` with templateRefs.
- `isOptional` on a property → `string?` (nullable reference type).
- **Every internal type reference in customCode MUST use templateRefs** or `using` directives won't be emitted across namespaces.

### Python
- **Must provide explicit indentation (4 spaces) after `\n`** in customCode bodies.
- `typing.*`, pydantic, datetime, decimal, enum, abc, dataclasses are auto-imported.
- Idiomatic transformations: methods become `snake_case`.

### Java
- Constructor parameters auto-create properties (don't duplicate).
- Idiomatic transformation: enum members become `ALL_CAPS`.
- `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` all auto-imported.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions in `customCode`.
- Constructor parameters auto-create struct fields.

### Swift / Rust / Kotlin / Groovy / Scala / PHP
- Each has its own auto-import set (see table above).
- All follow the same JSON spec shape — language-specific idiomatic emission is automatic.

---

## Output Structure

For each `class` / `interface` / `enum` / `customFile`:
- Files written under `outputPath` + `path` (default `outputPath` is current dir).
- File names default to language convention (kebab-case for TS, PascalCase for C#, snake_case for Python, etc.). Override with `fileName`.
- Imports are **fully auto-generated** from typeIdentifier/templateRef references plus explicit `customImports`.
- Each `customCode` item becomes one class member with a blank line separator.
- `dryRun: true` returns generated content in the response without writing.
- `skipExisting: true` (default) preserves any pre-existing file at the same path — set to `false` to overwrite.

---

## Common Mistakes — Top 10

1. **Missing typeIdentifier** in a referenced type → property silently dropped. Verify every reference resolves in the batch.
2. **Function-typed properties on interfaces** that classes will `implements` → duplicate method declarations. Use `customCode` with trailing `;` instead.
3. **Internal type names as raw strings** in customCode (e.g. `IUserRepository`) → no import, fails across namespaces. Use `$placeholder` + `templateRefs`.
4. **Using `arrayTypes` in C# when `List<T>` is required** → get `IEnumerable<T>`. Use `"type": "List<$x>"` with templateRefs.
5. **Adding stdlib imports** (`System.*`, `typing.*`, `java.util.*`) to `customImports` → duplicates / errors. Engine auto-imports all stdlib.
6. **Duplicating constructor params in `properties`** (C#/Java/Go/Groovy) → "Sequence contains more than one matching element". Put shared fields only in `constructorParameters`.
7. **Reserved words as property names** (`delete`, `class`, `import`) → compile errors. Use `remove`, `clazz`, `importData`.
8. **Splitting related types across multiple MCP calls** → cross-file imports break, references drop. **Always batch in ONE call.**
9. **Expecting `Number` → `double` in C#** → it maps to `int`. Use `"type": "decimal"` or `"type": "double"` explicitly.
10. **TS interface/class file-name collision** when interface starts with `I` → set `"fileName": "i-user-repository"` on the interface to disambiguate.

---

## Workflow for This Task

1. Read the entire spec.
2. Plan the typegraph: every entity, DTO, enum, service, request/response shape, array/dictionary alias, generic instantiation.
3. Construct **one** JSON spec containing **every** type, with consistent `typeIdentifier` keys (kebab-case).
4. For methods that reference internal types → wrap them in `customCode` with `$placeholder` + `templateRefs`.
5. For external libs (`@angular/...`, `rxjs`, `axios`, `zod`, etc.) → use `customImports`.
6. Call `mcp__metaengine__generate_code` ONCE with the full spec, target language `typescript`, appropriate `outputPath`.
7. Inspect the returned file list / dryRun output; if a property silently disappeared, the most likely cause is an unresolved `typeIdentifier`.
