# MetaEngine MCP — Knowledge Brief (TypeScript focus)

MetaEngine is a *semantic* code generation system exposed over MCP. You describe types, relationships, and methods as structured JSON; MetaEngine emits compilable, correctly-imported source files. Unlike templates, it resolves cross-references, manages imports, and applies language idioms automatically. The big win for AI use: ONE well-formed JSON call replaces dozens of error-prone file writes (and the engine creates the imports for you).

---

## Tools exposed by the MCP server

The MetaEngine MCP exposes these tools (`mcp__metaengine__*`):

- `metaengine_initialize(language?)` — Returns this guide. Optional `language` enum: typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php. Call once at the start; not needed afterward.
- `generate_code(spec)` — THE main tool. Takes a JSON spec describing classes, interfaces, enums, etc. Produces source files. **One batched call per related type-graph.**
- `generate_openapi(...)` — Generate from OpenAPI spec.
- `generate_graphql(...)` — Generate from GraphQL spec.
- `generate_protobuf(...)` — Generate from Protobuf spec.
- `generate_sql(...)` — SQL generation.
- `load_spec_from_file(...)` — Load a spec from disk.

For this benchmark / TypeScript work, **`generate_code` is what you'll use**.

---

## CARDINAL RULES (violations cause silent failures)

### 1. Generate ALL related types in ONE call
`typeIdentifier` references resolve only within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting the call by domain breaks the typegraph and cross-file imports won't be created.

### 2. `properties[]` = type declarations only. `customCode[]` = everything else (methods, initialized fields, logic). One `customCode` item == exactly one member.
```jsonc
"properties": [{"name": "id", "primitiveType": "String"}]            // type-only
"customCode": [
  {"code": "private http = inject(HttpClient);"},                    // initialized field
  {"code": "getAll(): T[] { return this.items; }"}                   // method
]
```
Never put methods in `properties`. Never put uninitialized type-only declarations in `customCode`.

### 3. Use `templateRefs` for internal type references inside `customCode` (and in `type` strings)
When code text inside `customCode` (or a property's `type` string) references a type from the same batch, use `$placeholder` syntax with `templateRefs`. This is what triggers automatic import resolution. Without it MetaEngine cannot generate the correct import.
```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```
**In C#**: every internal type reference inside customCode MUST use templateRefs across namespaces, or `using` directives won't be generated. In TS this matters most when files are in different folders.

### 4. Never add framework imports to `customImports`
MetaEngine auto-imports stdlib/runtime types. Adding them manually causes duplication or compile errors.

| Language   | Auto-imported (DO NOT specify)                                                                  |
|------------|--------------------------------------------------------------------------------------------------|
| TypeScript | (none — built-in types)                                                                          |
| C#         | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*    |
| Python     | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses                 |
| Java       | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*       |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*                                |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more  |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)                |
| Rust       | std::collections, chrono, uuid, rust_decimal, serde                                              |
| Groovy     | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream)      |
| Scala      | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.*         |
| PHP        | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable              |

`customImports` is ONLY for external libraries (e.g. `@angular/core`, `rxjs`, `FluentValidation`).

### 5. `templateRefs` are for internal types ONLY
External library types must use `customImports`.
- Same MCP call → use `typeIdentifier` / `templateRefs`.
- External library → use `customImports`.
Never mix.

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Do NOT also list those names in `properties[]`. Causes "Sequence contains more than one matching element" errors. (Less relevant for pure TypeScript, but be aware if porting.)

### 7. "Virtual" types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` — these only create reusable type references. They never produce files. Reference them via `typeIdentifier` from properties of file-generating types.

---

## `generate_code` — input schema

Top-level fields of the spec object:

- `language` (string, **required**): `typescript` | `csharp` | `python` | `go` | `java` | `kotlin` | `groovy` | `scala` | `swift` | `php` | `rust`.
- `packageName` (string, optional): namespace / package. Required for Go multi-file. In C# sets namespace; omit for GlobalUsings pattern. Generally not needed for TS.
- `classes[]` — file-generating type definitions (see schema below).
- `interfaces[]` — file-generating interface definitions.
- `enums[]` — file-generating enum definitions.
- `customFiles[]` — arbitrary code files (type aliases, barrel exports, helpers).
- `arrayTypes[]` — virtual array type references (no file).
- `dictionaryTypes[]` — virtual dictionary/map type references (no file).
- `concreteGenericClasses[]` — virtual `Foo<Bar>` references.
- `concreteGenericInterfaces[]` — virtual generic interface references.

### Common shape for `classes[]` items
```jsonc
{
  "name": "User",                              // declared identifier in the source
  "typeIdentifier": "user",                    // unique key referenced by other types
  "fileName": "user",                          // optional override; else derived from name
  "path": "models",                            // optional sub-directory
  "isAbstract": false,                         // optional
  "baseClassTypeIdentifier": "base-entity",    // optional; refs another typeIdentifier or virtual generic
  "implementsInterfaceTypeIdentifiers": ["i-user"],  // optional
  "genericArguments": [                        // optional — declares this class as generic
    {
      "name": "T",
      "constraintTypeIdentifier": "base-entity",  // optional
      "propertyName": "items",                    // optional — auto-generates a property typed T (or T[])
      "isArrayProperty": true                     // optional
    }
  ],
  "constructorParameters": [                   // C#/Java/Go/Groovy primarily
    {"name": "email", "type": "string"}
  ],
  "decorators": [                              // class-level decorators / attributes
    {"code": "@Injectable({ providedIn: 'root' })"}
  ],
  "customImports": [                           // external libs ONLY
    {"path": "@angular/core", "types": ["Injectable", "inject"]},
    {"path": "rxjs", "types": ["Observable"]}
  ],
  "properties": [                              // type-only field declarations
    {"name": "id", "primitiveType": "String"},
    {"name": "address", "typeIdentifier": "address"},          // ref same-batch type
    {"name": "tags", "type": "string[]"},                      // raw type expression
    {"name": "cache", "type": "Map<string, $resp>",            // type with templateRefs
       "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]},
    {"name": "email", "primitiveType": "String", "isOptional": true}
  ],
  "customCode": [                              // methods, initialized fields, anything with logic
    {"code": "private http = inject(HttpClient);"},
    {"code": "getUser(id: string): Promise<$user> { return this.http.get<$user>(`/users/${id}`).toPromise(); }",
     "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
  ]
}
```

### Property item schema
- `name` (string, required)
- One of:
  - `primitiveType`: `"String" | "Number" | "Boolean" | "Date" | "Any" | "Guid"` (case-sensitive PascalCase)
  - `typeIdentifier`: ref to another item in the same batch (file or virtual)
  - `type`: a raw type expression string (e.g. `"Map<string, $resp>"`, `"List<$user>"`, `"decimal"`, `"double"`). Use this with `templateRefs` when referencing internal types.
- `isOptional` (bool, optional) — TS: makes prop optional / nullable; C#: nullable reference type.
- `templateRefs` (when used with `type` strings).
- `decorators` (optional, e.g. validation attributes).

### CustomCode item schema
- `code` (string, required) — exactly ONE member: a method, an initialized field, a property accessor block, etc.
- `templateRefs` (array, optional) — `[{ "placeholder": "$x", "typeIdentifier": "..." }, ...]`.
- For Python: must provide explicit 4-space indentation after `\n`. For TS: auto-indents.

### Interface items (`interfaces[]`)
Same shape as classes minus `isAbstract` / `baseClassTypeIdentifier` (use `extendsInterfaceTypeIdentifiers` instead, and they don't have constructor parameters).
- For interface method signatures (TypeScript / C#) define them in `customCode` as method-signature lines (e.g. `"findAll(): Promise<$user[]>;"`). Do NOT use function-typed `properties` — the implementing class would then duplicate them as property declarations alongside your customCode methods.

### Enum items (`enums[]`)
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
Files auto-suffixed: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#), `order_status.py` (Python with snake_case methods, etc.).

### Virtual type entries
```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
  {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
],
"dictionaryTypes": [
  {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
],
"concreteGenericClasses": [
  {"identifier": "user-repo-concrete",
   "genericClassIdentifier": "repo-generic",
   "genericArguments": [{"typeIdentifier": "user"}]}
],
"concreteGenericInterfaces": [
  {"identifier": "user-list-iface",
   "genericInterfaceIdentifier": "list-generic",
   "genericArguments": [{"typeIdentifier": "user"}]}
]
```
Reference these via their `typeIdentifier`/`identifier` from properties or `baseClassTypeIdentifier`.

### customFiles entry
```jsonc
{
  "name": "types",
  "path": "shared",
  "identifier": "shared-types",
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"}
  ]
}
```
The `identifier` enables import resolution: a class can do `"customImports": [{"path": "shared-types"}]` and the engine resolves to the relative path automatically.

---

## TypeScript-specific notes

- **`I` prefix is stripped from interface names.** `IUserRepository` → exported as `UserRepository`. If both `IUserRepository` (interface) and `UserRepository` (class) exist, file names will collide. Set `"fileName": "i-user-repository"` on the interface to avoid collision.
- Primitive mappings: `String → string`, `Number → number`, `Boolean → boolean`, `Date → Date`, `Any → unknown`, `Guid → string`.
- TS auto-indents customCode for newlines (`\n` inside code strings is OK).
- Decorators supported directly (`@Component`, `@Injectable`, etc.).
- No imports needed for built-in JS/TS types (Map, Set, Promise, Date, Array). Use `customImports` only for npm packages (`@angular/core`, `rxjs`, etc.).
- File names default to kebab-case derived from `name` (e.g. `User` → `user.ts`). Override via `fileName`.

## C# notes (for reference)
- `I` prefix preserved on interface names.
- `Number` → `int`! For non-integer: `"type": "decimal"` or `"type": "double"`.
- Interface properties → `{ get; }`; class properties → `{ get; set; }`.
- `arrayTypes` → `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs.
- `isOptional` → nullable reference type (`string?`).

## Python notes
- Must provide explicit 4-space indentation after `\n` in customCode.
- typing imports automatic.
- Methods become `snake_case` (engine applies idiomatic transformation).

## Java notes
- Enum members may be uppercased (`ALL_CAPS`).
- Constructor parameters auto-create properties — don't duplicate.

## Go notes
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions in `customCode`.

---

## Pattern recipes

### Basic interfaces with cross-references (TS)
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
Produces two files (`address.ts`, `user.ts`) with automatic import between them.

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

### Generic class + concrete subclass
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
The `concreteGenericClasses` entry creates a virtual `Repository<User>` reference; `UserRepository` extends it via `baseClassTypeIdentifier: "user-repo-concrete"`.

### Array & dictionary virtual types
```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
  {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
],
"dictionaryTypes": [
  {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
]
```
Reference via `"typeIdentifier": "user-list"` in properties.

### Complex inline type with templateRefs
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
templateRefs work in `properties` (with `type` strings), `customCode`, and `decorators`.

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

### Service with DI / external lib (Angular shape)
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

### customFiles for type aliases + barrel-style import
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

### Interface with method signatures (correct way)
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
Avoid `"properties": [{"name": "findAll", "type": "() => Promise<User[]>"}]` for an interface a class will implement — the implementing class would duplicate them as property declarations.

---

## Output structure

`generate_code` returns a list of generated files (path + content). MetaEngine handles:
- File naming (kebab-case for TS by default; PascalCase for C#).
- Cross-file imports/usings between same-batch types.
- External-package imports from `customImports`.
- Auto-added stdlib imports per language (see table above).
- Language-idiomatic formatting (TS: `string` lowercase; Python: `snake_case` methods; Java: `ALL_CAPS` enums; etc.).

The host then writes these files into the project tree.

---

## Common mistakes (cheat sheet)

1. **Don't** reference a `typeIdentifier` not present in this batch — silently dropped.
2. **Don't** use function-typed properties for interface method signatures — use `customCode` instead.
3. **Don't** write internal type names as raw strings inside `customCode` (e.g. `private repo: IUserRepository`). Use `$placeholder` + `templateRefs`.
4. **Don't** use `arrayTypes` in C# when you need `List<T>` — use `"type": "List<$user>"` + templateRefs.
5. **Don't** add `System.*`, `typing.*`, `java.util.*`, etc. to `customImports`. Stdlib is automatic.
6. **Don't** duplicate constructor parameter names in `properties` (C#/Java/Go/Groovy).
7. **Don't** use reserved words (`delete`, `class`, `import`) as property names.
8. **Don't** split related types across multiple `generate_code` calls — cross-file imports only resolve within a single batch.
9. **Don't** assume `Number` → `double` in C# — it's `int`. Use `"type": "double"` or `"type": "decimal"` for non-integers.
10. **Don't** forget `fileName` overrides when a stripped `I` prefix would cause TS file collisions.

---

## Quick mental model for building a spec

1. **Inventory all types** the task needs (entities, DTOs, services, enums, repositories, interfaces).
2. **Assign each a unique `typeIdentifier`** (kebab-case is conventional, e.g. `user`, `user-repo`, `api-service`).
3. **Decide for each type:**
   - File-generating? → goes in `classes[]`, `interfaces[]`, `enums[]`, or `customFiles[]`.
   - Virtual reference? → goes in `arrayTypes[]`, `dictionaryTypes[]`, `concreteGenericClasses[]`, or `concreteGenericInterfaces[]`.
4. **For each member of a type:**
   - Pure typed field? → `properties[]` with `primitiveType` / `typeIdentifier` / `type`+`templateRefs`.
   - Has logic / initialization / is a method? → `customCode[]` (one entry = one member).
5. **Resolve internal references** with `typeIdentifier` (in properties) or `templateRefs` (in `code` / `type` strings).
6. **External libraries only** go in `customImports`. Stdlib is automatic.
7. **One `generate_code` call** for the whole graph.
8. Spec object minimal shape:
   ```jsonc
   {
     "language": "typescript",
     "classes": [...],
     "interfaces": [...],
     "enums": [...],
     "arrayTypes": [...],
     "customFiles": [...]
   }
   ```

That's it — call `mcp__metaengine__generate_code` once with the full spec and the engine takes care of the rest.
