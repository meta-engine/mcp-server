# MetaEngine MCP — Knowledge Brief (TypeScript focus)

This is a self-contained brief built from the metaengine MCP's `linkedResources`
(the `metaengine_initialize` tool output, the `metaengine://guide/ai-assistant`
resource, and the `metaengine://guide/examples` resource). The next session will
NOT have access to those docs — everything needed to call `generate_code`
correctly is captured here.

## What MetaEngine is

MetaEngine is a *semantic* code generator exposed over MCP. You describe **types,
relationships, and methods** as structured JSON; the engine emits compilable,
correctly-imported source files for **TypeScript, C#, Python, Go, Java, Kotlin,
Groovy, Scala, Swift, Rust, and PHP**. Unlike templates it:

- Resolves cross-file `typeIdentifier` references inside the batch.
- Manages imports / `using` / namespace directives automatically.
- Applies language idioms (e.g. naming, prefix stripping, default file naming).

A single well-formed JSON call replaces dozens of error-prone file writes.

## Tools exposed by the MCP

- `mcp__metaengine__metaengine_initialize` — returns this guide. Optional
  `language` param ∈ {typescript, python, go, csharp, java, kotlin, groovy,
  scala, swift, php}. Already used; no need to call again.
- `mcp__metaengine__generate_code` — the workhorse. Takes a single JSON spec
  with arrays of types and writes generated source files to disk.
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`,
  `generate_sql` — schema-format generators (out of scope for this run).
- `mcp__metaengine__load_spec_from_file` — load a spec JSON from disk.

For this benchmark only `generate_code` matters.

---

## THE CARDINAL RULES (memorize before generating)

### Rule 1 — ONE call, ALL related types

`typeIdentifier` references resolve **only within the current batch**. If
`UserService` references `User`, both must live in the *same* `generate_code`
call. Splitting per-domain (one call for models, one for services) BREAKS the
typegraph — references silently drop and imports won't generate.

### Rule 2 — Properties = type declarations only. CustomCode = everything else

- `properties[]` declares fields with **types only** (no initializer, no logic).
- `customCode[]` handles methods, initialized fields, constants, accessors —
  any code with logic. **One `customCode` item = exactly one member.**

```jsonc
"properties": [{"name": "id", "primitiveType": "String"}]            // type-only
"customCode": [
  {"code": "private http = inject(HttpClient);"},                    // initialized field
  {"code": "getAll(): T[] { return this.items; }"}                   // method
]
```

Never put methods in `properties`. Never put uninitialized type declarations
in `customCode`.

### Rule 3 — Use `templateRefs` for internal types referenced inside `customCode`

When a `customCode` snippet (or a `properties` `type` string) references a type
that is **also generated in this batch**, use `$placeholder` syntax with a
`templateRefs` array. This is what triggers automatic import resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

Without `templateRefs`, MetaEngine cannot generate the import/using directive,
even if the textual name happens to be correct. In C# this is *especially*
strict — raw type names in customCode produce compile failures across
namespaces.

### Rule 4 — Never add framework imports to `customImports`

The engine auto-imports the standard library for every supported language. Do
not list these manually (it causes duplicates / errors):

| Language   | Auto-imported (never specify in customImports) |
|------------|------------------------------------------------|
| TypeScript | (built-in types — no imports needed)            |
| C#         | `System.*`, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python     | `typing.*`, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java       | `java.util.*`, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, … |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder/Decoder…) |
| Rust       | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy     | java.time.*, java.math.*, java.util (UUID, Date), java.io |
| Scala      | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP        | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |

`customImports` is for **external libraries only** (`@angular/core`,
`@nestjs/common`, `rxjs`, `FluentValidation`, etc.).

### Rule 5 — `templateRefs` are ONLY for internal types

If a referenced type is in this same MCP call → use `typeIdentifier` (in
properties) or `templateRefs` (in customCode). If it is from an external
library → use `customImports`. Never mix the two for one type.

### Rule 6 — Constructor parameters auto-create properties (C#/Java/Go/Groovy)

In **C#, Java, Go, Groovy**, listing a name in `constructorParameters[]` already
declares a property. **Do not also list it in `properties[]`** or you get
"Sequence contains more than one matching element". TypeScript also follows
this pattern: `constructor(public email: string)` is generated, so don't
duplicate. Only put **additional, non-constructor** fields in `properties`.

### Rule 7 — Virtual types don't generate files

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`,
`concreteGenericInterfaces` create reusable **type references only**. They
never produce files. Reference them from `properties` or `templateRefs`.

---

## `generate_code` — Top-level input shape

A `generate_code` call is a single JSON object. The relevant top-level fields:

- `language` *(string, required)* — `"typescript" | "python" | "go" | "csharp" |
  "java" | "kotlin" | "groovy" | "scala" | "swift" | "php"` (and `"rust"` is
  supported per the auto-import table).
- `initialize` *(bool, optional)* — set `true` when starting a fresh batch
  (resets engine context). Seen in examples; safe to include on first call.
- `packageName` *(string, optional)* — language-dependent meaning:
  - C#: namespace (omit for GlobalUsings pattern).
  - Java/Kotlin/Groovy/Scala: package.
  - Go: package name (REQUIRED for multi-file Go projects).
  - Python: package/module path.
- `classes[]` — class definitions (file-generating).
- `interfaces[]` — interface definitions (file-generating).
- `enums[]` — enum definitions (file-generating; auto file suffixing).
- `customFiles[]` — arbitrary files (type aliases, barrel exports, etc).
- `arrayTypes[]` — virtual array type aliases (no file).
- `dictionaryTypes[]` — virtual dictionary/map type aliases (no file).
- `concreteGenericClasses[]` — virtual closed-generic class aliases (no file).
- `concreteGenericInterfaces[]` — virtual closed-generic interface aliases
  (no file).

(Multiple `classes` arrays may appear in the docs' examples; in practice merge
them into a single `classes` array for one call.)

## Type definition shape — `classes[]` / `interfaces[]`

Per-item fields (superset; not all apply to every language):

- `name` *(string, required)* — type name (TypeScript strips an `I` prefix on
  interfaces — see TS notes).
- `typeIdentifier` *(string, required)* — stable ID used by other entries to
  reference this type. Convention: kebab-case (`user`, `user-repo`).
- `path` *(string, optional)* — sub-path for the generated file (e.g.
  `"services"`).
- `fileName` *(string, optional)* — explicit filename override (use for TS
  interface/class collisions, e.g. `"i-user-repository"`).
- `isAbstract` *(bool)* — abstract class.
- `baseClassTypeIdentifier` *(string)* — extends another type by identifier
  (may point at a virtual `concreteGenericClasses` entry to extend a closed
  generic).
- `implementsTypeIdentifiers` *(string[])* — implemented interfaces.
- `genericArguments[]` — generic parameter declarations (for generic type
  *definitions*). Each may carry:
  - `name` (e.g. `"T"`),
  - `constraintTypeIdentifier` (constrains `T` to a known type),
  - `propertyName` + `isArrayProperty` to also auto-declare a backing field
    of type `T` / `T[]`.
- `decorators[]` — `[{"code": "@Injectable({ providedIn: 'root' })"}]`.
- `customImports[]` — external library imports:
  `[{"path": "@angular/core", "types": ["Injectable", "inject"]}, …]`.
  May reference a `customFiles[].identifier` to import from a generated file
  by identifier (auto resolves to relative path).
- `constructorParameters[]` — `{name, primitiveType|typeIdentifier|type, …}`.
  Auto-create properties (see Rule 6).
- `properties[]` — see "Property shape" below.
- `customCode[]` — `[{code, templateRefs?}]`, one entry per member.

### Property shape (`properties[]` items)

A property uses **exactly one** of these to specify its type:

- `primitiveType` — one of `"String" | "Number" | "Boolean" | "Date" | "Any"`
  (also `"Decimal"`, `"Long"`, etc — language mapped). For TypeScript:
  `Number → number`, `String → string`, `Boolean → boolean`, `Date → Date`,
  `Any → unknown`.
- `typeIdentifier` — references a type/enum/array/dict in the batch.
- `type` — raw type expression string. Use with `templateRefs` for placeholders:
  `"type": "Map<string, $resp>", "templateRefs": [{"placeholder": "$resp",
  "typeIdentifier": "api-response"}]`. In C# this is the way to get `List<T>`
  instead of `IEnumerable<T>`: `"type": "List<$user>"` + templateRefs.

Other property fields:

- `comment` — emitted as JSDoc/XML doc comment.
- `isOptional` — emits `?` (TS) / nullable (C#).
- `templateRefs` — placeholder→typeIdentifier map for `$placeholder` syntax in
  the `type` string.

### CustomCode shape (`customCode[]` items)

- `code` *(string)* — exactly **one** member's source: a method, an initialized
  field, a constant, a getter, etc. TypeScript: auto-indents on `\n` and adds
  blank lines between blocks. Python: you MUST provide explicit 4-space
  indentation after `\n`.
- `templateRefs` *(array, optional)* — `[{"placeholder": "$x", "typeIdentifier":
  "..."}]`. Required for any internal type reference inside `code`.

## Enum shape (`enums[]` items)

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2}
  ]
}
```

File naming auto-suffixes: `order-status.enum.ts` for TS, `OrderStatus.cs` for
C#, etc. The engine applies idiomatic transformations per language (Java
`ALL_CAPS`, Python `snake_case` for methods, etc.) — do not fight these.

## Virtual type shapes

### `arrayTypes[]`

```jsonc
{"typeIdentifier": "user-list", "elementTypeIdentifier": "user"}
{"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
```

Reference via `"typeIdentifier": "user-list"` in a property. TS emits
`Array<User>`. **C# emits `IEnumerable<T>`**; for `List<T>` use a `type` +
`templateRefs` instead.

### `dictionaryTypes[]`

All four key/value combinations supported:

```jsonc
{"typeIdentifier": "scores",        "keyPrimitiveType": "String", "valuePrimitiveType": "Number"}
{"typeIdentifier": "user-lookup",   "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
{"typeIdentifier": "rev-lookup",    "keyTypeIdentifier": "user",  "valuePrimitiveType": "String"}
{"typeIdentifier": "user-metadata", "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata"}
```

TS emits `Record<K, V> = {}`.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]`

Closes a generic with concrete arguments to produce a virtual nameable type:

```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}
```

A class can then `"baseClassTypeIdentifier": "user-repo-concrete"` and the
engine emits `extends Repository<User>` with proper imports.

## CustomFiles (`customFiles[]`)

For type-aliases, barrel exports, anything that isn't a class/interface/enum:

```jsonc
{
  "name": "types",
  "path": "shared",
  "identifier": "shared-types",        // makes the file referenceable from customImports
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"}
  ]
}
```

Then a class can `"customImports": [{"path": "shared-types"}]` (or use a
relative path string). The `identifier` form auto-resolves the relative path.

---

## Output structure — what the engine writes

The engine writes **multiple source files** to disk under the project. Per
type:

- TypeScript: `kebab-case.ts` (`user.ts`, `pet-service.ts`); enums get
  `.enum.ts` suffix.
- C#: `PascalCase.cs`; interfaces keep `I` prefix; `packageName` becomes the
  namespace.
- Python: `snake_case.py`; methods become `snake_case`.
- Java/Kotlin/Groovy/Scala: `PascalCase.java/.kt/.groovy/.scala`; package
  directory layout from `packageName`.
- Go: `snake_case.go` files inside `packageName`.

Imports/`using`/`import` directives are generated automatically based on
`typeIdentifier` references and `templateRefs`.

The engine applies **language-aware idiomatic transformations** — Java enum
members may upcase to `ALL_CAPS`, Python method names may shift to
`snake_case`, etc. These are intentional; downstream judges expect them.

---

## TypeScript-specific notes (this benchmark's target)

- **Interface name `I` prefix is stripped**: `IUserRepository` exports as
  `UserRepository`. If both exist in the batch, set `fileName` on the
  interface to disambiguate (e.g. `"fileName": "i-user-repository"` produces
  `i-user-repository.ts`).
- Primitive mapping: `Number → number`, `String → string`, `Boolean → boolean`,
  `Date → Date`, `Any → unknown`.
- TypeScript needs **no** `customImports` for built-in types.
- Decorators are supported directly via `decorators[]`.
- Auto-indent applies inside customCode `code` strings on `\n`.
- For interfaces a class will `implements`: declare the method signatures as
  `customCode` items (NOT as function-typed properties). Function-typed
  properties get duplicated as fields when the class implements the interface.

---

## Idiomatic patterns (worked examples)

### A. Plain interface graph with cross-references

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

### B. Class inheritance + method

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

### C. Generic + concrete generic + sub-class extending it

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

### D. Service with external DI (Angular/NestJS shape)

```jsonc
{
  "language": "typescript",
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
       "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]},
      {"code": "create(pet: $pet): Observable<$pet> { return this.http.post<$pet>(this.baseUrl, pet); }",
       "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}]
}
```

### E. Type aliases via customFiles

```jsonc
{
  "language": "typescript",
  "customFiles": [{
    "name": "types", "path": "utils",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"},
      {"code": "export type ResultSet<T> = { data: T[]; total: number; page: number; };"}
    ]
  }],
  "classes": [{
    "name": "UserService", "typeIdentifier": "service", "path": "services",
    "customImports": [{"path": "../utils/types", "types": ["UserId", "Status", "ResultSet"]}],
    "customCode": [
      {"code": "async getUser(id: UserId): Promise<User> { return null as any; }"},
      {"code": "updateStatus(id: UserId, status: Status): void { }"}
    ]
  }]
}
```

### F. Enum + class that uses it

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

### G. Constructor parameters — RIGHT vs WRONG

WRONG (duplicates → "Sequence contains more than one matching element"):

```jsonc
"constructorParameters": [{"name": "email", "type": "string"}],
"properties":            [{"name": "email", "type": "string"}]   // ❌ DUPLICATE
```

RIGHT:

```jsonc
"constructorParameters": [{"name": "email", "type": "string"}],
"properties":            [{"name": "createdAt", "primitiveType": "Date"}]   // ✅ extras only
```

---

## Top 10 mistakes — quick checklist before calling `generate_code`

1. ❌ Referencing a `typeIdentifier` not in the batch → property silently dropped.
   ✅ Verify every `typeIdentifier` matches a defined type in the same call.
2. ❌ Function-typed properties on an interface a class will implement → duplicated members.
   ✅ Put method signatures in interface `customCode`.
3. ❌ Raw internal type names in `customCode` strings → no imports.
   ✅ Use `$placeholder` + `templateRefs`.
4. ❌ `arrayTypes` in C# when you actually need `List<T>` (you'll get `IEnumerable<T>`).
   ✅ Use `"type": "List<$user>"` + templateRefs.
5. ❌ Adding `System.*`, `typing.*`, `java.util.*` to `customImports` → duplicates.
   ✅ Let the engine auto-import standard library types.
6. ❌ Duplicating constructor params in `properties[]` (C#/Java/Go/Groovy/TS).
   ✅ Only put non-constructor extras in `properties[]`.
7. ❌ Reserved words as property names (`delete`, `class`, `import`).
   ✅ Use `remove`, `clazz`, `importData`.
8. ❌ Splitting related types across multiple MCP calls → cross-file imports break.
   ✅ Generate everything in ONE call.
9. ❌ Expecting C# `Number` → `double` (it maps to `int`).
   ✅ Use `"type": "double"` or `"type": "decimal"` explicitly.
10. ❌ TS interface + class collision (`UserRepository` vs `IUserRepository` both → `user-repository.ts`).
    ✅ Set `"fileName": "i-user-repository"` on the interface.

---

## How to invoke `generate_code`

The tool takes a single JSON object matching the structure above and writes
files into the current project. Provide `language`, optionally `initialize:
true` on the first call, and the relevant arrays (`classes`, `interfaces`,
`enums`, `customFiles`, `arrayTypes`, `dictionaryTypes`,
`concreteGenericClasses`, `concreteGenericInterfaces`).

**Build the entire batch in your head first.** Then emit ONE call with all of
it. That single-call discipline is the whole reason MetaEngine exists: a
well-formed batch becomes a perfect, mutually-imported set of files in one
shot.
