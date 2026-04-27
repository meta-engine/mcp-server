# MetaEngine MCP — Knowledge Brief (TypeScript)

This brief is self-contained for a generation session that will NOT have access to the MCP's docs. It captures every rule, schema field, pattern and gotcha needed to issue ONE correct `mcp__metaengine__generate_code` call producing compilable TypeScript files.

---

## Tools exposed by the metaengine MCP

- `mcp__metaengine__metaengine_initialize(language?)` — returns the canonical guide (rules + patterns + language notes). Optional `language` enum: `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php`. Read-only; safe to call but not required if you already have this brief.
- `mcp__metaengine__generate_code(spec)` — the workhorse. Takes a single JSON spec and writes generated source files to disk. **Call ONCE with the FULL spec.** Splitting into multiple calls breaks the cross-file typegraph (typeIdentifier references only resolve within a single call).
- `mcp__metaengine__load_spec_from_file(path)` — load a saved spec from disk instead of inlining it. Useful for very large specs.
- `mcp__metaengine__generate_openapi`, `mcp__metaengine__generate_graphql`, `mcp__metaengine__generate_protobuf`, `mcp__metaengine__generate_sql` — convert spec inputs to those alternate output forms (NOT used in this benchmark).

---

## generate_code — Full Input Schema

The spec is one JSON object. Top-level fields:

| Field | Type | Required | Purpose |
|---|---|---|---|
| `language` | enum string | yes | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `initialize` | bool | no | Set true on first call to clear/seed output workspace |
| `packageName` | string | optional (required for Go, sets C# namespace) | Module/namespace |
| `outputPath` / `outputDir` | string | optional | Output root |
| `interfaces` | array | no | Interface declarations |
| `classes` | array | no | Class declarations |
| `enums` | array | no | Enum declarations |
| `arrayTypes` | array | no | Virtual array references (no files generated) |
| `dictionaryTypes` | array | no | Virtual dictionary references (no files generated) |
| `concreteGenericClasses` | array | no | Virtual `Generic<T>` references (no files generated) |
| `concreteGenericInterfaces` | array | no | Virtual generic interface references |
| `customFiles` | array | no | Free-form files (e.g., type aliases, barrel exports) |

NOTE: per the docs, when an example shows `"classes": [...]` appearing TWICE in the same spec, that's pseudocode for "all classes go in this single array" — in real JSON, merge them into one array. Use one array per top-level kind.

### Common element fields (interfaces, classes, enums, customFiles)

| Field | Notes |
|---|---|
| `name` | PascalCase type name (TS strips a leading `I` from interfaces — use `fileName` if collisions) |
| `typeIdentifier` | kebab-case unique key used to reference this type elsewhere in the same call |
| `path` | Subdirectory under output root (e.g., `"services"`, `"models/dto"`) |
| `fileName` | Override default file naming (e.g., `i-user-repository`) |
| `isAbstract` | Class only |
| `baseClassTypeIdentifier` | Class extends another class (must exist in same call) |
| `implementsTypeIdentifiers` | Array of interface typeIdentifiers a class implements |
| `genericArguments` | Array of generic-arg descriptors (see below) |
| `properties` | Field declarations (TYPE ONLY, no logic, no init) |
| `customCode` | Methods, initialized fields, getters/setters — one item = ONE member |
| `customImports` | External-library imports only (see below) |
| `decorators` | Array of `{code: "@Decorator(...)"}` |
| `comment` | JSDoc/XML doc comment text |
| `constructorParameters` | C#/Java/Go/Groovy: param list that auto-becomes properties |

### `properties[]` item

```jsonc
{
  "name": "fieldName",          // identifier
  "primitiveType": "String",    // OR
  "typeIdentifier": "user",     // OR (reference another type in the call)
  "type": "Map<string, $resp>", // OR (raw type expression with templateRefs)
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}],
  "isOptional": true,           // → emits TS optional / nullable / etc
  "isArray": true,              // simple array wrapper around primitive/typeIdentifier
  "comment": "JSDoc text",
  "decorators": [{"code": "@Column()"}]
}
```

`primitiveType` enum (canonical names): `String`, `Number`, `Boolean`, `Date`, `Any`, `Decimal`, `Long`, `Integer`, `Double`, `Float`, `UUID`, `Bytes`. The engine maps these per-language (e.g., TS: `String`→`string`, `Number`→`number`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`).

### `customCode[]` item — ONE member per item

```jsonc
{
  "code": "getUser(id: string): Promise<$user> { return this.repo.find(id); }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

Rules:
- Each item is exactly one method, getter/setter, or initialized field.
- Newlines between items are inserted automatically — DON'T add blank-line padding inside `code`.
- Internal type references inside `code` MUST use `$placeholder` + `templateRefs`. Raw type names like `User` will not trigger import resolution.
- For interface method signatures (no body), end with `;` — `findAll(): Promise<$user[]>;`.
- TS auto-indents continuation lines; Python REQUIRES explicit 4-space indentation after `\n`.

### `customImports[]` item — EXTERNAL libraries ONLY

```jsonc
{ "path": "@angular/core", "types": ["Injectable", "inject"] }
```

Or a side-effect import:
```jsonc
{ "path": "reflect-metadata" }
```

Or a customFile barrel (use the customFile's `identifier` or relative path):
```jsonc
{ "path": "shared-types" }
{ "path": "../utils/types", "types": ["UserId", "Status"] }
```

NEVER add stdlib/framework imports here — see auto-import table below.

### `arrayTypes[]` — virtual, no file output

```jsonc
{ "typeIdentifier": "user-array", "elementTypeIdentifier": "user" }
{ "typeIdentifier": "string-array", "elementPrimitiveType": "String" }
```

TS emits `Array<User>` / `Array<string>`. (C# emits `IEnumerable<T>` — for `List<T>` use raw `type` + templateRefs.)

### `dictionaryTypes[]` — virtual, all 4 key×value combos

```jsonc
{ "typeIdentifier": "scores",       "keyPrimitiveType": "String", "valuePrimitiveType": "Number" }
{ "typeIdentifier": "user-lookup",  "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
{ "typeIdentifier": "user-names",   "keyTypeIdentifier": "user",  "valuePrimitiveType": "String" }
{ "typeIdentifier": "user-meta",    "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata" }
```

TS emits `Record<K, V> = {}`.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` — virtual

```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{ "typeIdentifier": "user" }]
}
```

This creates a virtual `Repository<User>` reference. Use its `identifier` as a `baseClassTypeIdentifier` or in `templateRefs` to extend or refer to the concrete instantiation. No file is generated.

### `genericArguments[]` (on a class/interface that IS generic)

```jsonc
{
  "name": "T",
  "constraintTypeIdentifier": "base-entity",   // optional T extends BaseEntity
  "constraintPrimitiveType": "String",         // alternative
  "propertyName": "items",                     // optional: generates a property of type T (or T[])
  "isArrayProperty": true                      // makes it T[]
}
```

### `enums[]` item

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "members": [
    { "name": "Pending", "value": 0, "comment": "Not yet shipped" },
    { "name": "Shipped", "value": 2 }
  ]
}
```

TS files become `order-status.enum.ts`. The engine applies language-aware idiomatic transforms (Java emits `ALL_CAPS`, Python may snake_case method names).

### `customFiles[]` item

```jsonc
{
  "name": "types",
  "path": "utils",
  "identifier": "shared-types",   // enables import resolution by id
  "customCode": [
    { "code": "export type UserId = string;" },
    { "code": "export type Status = 'active' | 'inactive';" }
  ]
}
```

Use these for type aliases, union types, barrel re-exports, constants files. Don't model these as classes.

---

## CRITICAL Rules (most-violated)

1. **ONE call with the FULL spec.** typeIdentifier references resolve only within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks the typegraph and causes missing imports / dropped properties.

2. **`properties` = type declarations only. `customCode` = everything else.**
   - `properties`: name + type, no init, no logic.
   - `customCode`: methods, initialized fields (`private http = inject(HttpClient);`), getters/setters. One item = one member.
   - Never put methods in `properties`. Never put bare uninitialized fields in `customCode`.

3. **Use `templateRefs` for internal type refs in `customCode` and complex `type` strings.** `$placeholder` syntax. Without it, no import is generated. Especially critical in C# where missing `using` directives cause cross-namespace compile failures. In TS the imports are also required for correctness.

4. **Never add framework/stdlib imports to `customImports`.** Auto-import table:
   - **TypeScript**: built-ins (`string`, `number`, `Date`, `Promise`, `Array`, `Map`, `Record`) need no imports
   - **C#**: `System.*`, `System.Collections.Generic`, `System.Linq`, `System.Threading.Tasks`, `System.Text`, `System.IO`, `System.Net.Http`, `System.ComponentModel.DataAnnotations`, `Microsoft.Extensions.*`
   - **Python**: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`
   - **Java**: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, jackson
   - **Kotlin**: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`
   - **Go**: `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`
   - **Swift**: Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder/Decoder)
   - **Rust**: `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde`
   - Use `customImports` ONLY for external libs (`@angular/core`, `rxjs`, `FluentValidation`, etc.) and internal `customFiles`.

5. **`templateRefs` are ONLY for INTERNAL types.** External library types must come via `customImports`. If it's defined in this same spec → `typeIdentifier`/`templateRefs`. If it's an npm/nuget/pypi lib → `customImports`. Never mix.

6. **Constructor parameters auto-create properties (C#/Java/Go/Groovy).** Don't list them again in `properties[]`. TS does NOT have this constraint to the same degree, but TS `constructorParameters` with `public` modifier also become properties — don't duplicate.

7. **Virtual types don't generate files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reusable references only. They appear via their `typeIdentifier` in `properties` of file-generating types.

8. **Reserved words.** Never use `delete`, `class`, `import`, etc. as property names. Use `remove`, `clazz`, `importData`.

9. **Method signatures on interfaces go in `customCode`, not as function-typed properties.** If you put `{ "name": "findAll", "type": "() => Promise<User[]>" }` on an interface, an implementing class will end up with a duplicated property declaration. Instead:
   ```jsonc
   "customCode": [{
     "code": "findAll(): Promise<$user[]>;",
     "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
   }]
   ```

10. **`fileName` collision avoidance**: in TS the `I` prefix is stripped from interface names, so `IUserRepository` interface and `UserRepository` class would collide. Set `"fileName": "i-user-repository"` on the interface.

---

## TypeScript-specific notes

- Interface `I` prefix stripped from exported name. Use `fileName` to avoid file collisions.
- Primitive mapping: `String`→`string`, `Number`→`number`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`, `Decimal`→`number`, `UUID`→`string`.
- `arrayTypes` emits `Array<T>`. Properties of array type emit `items = new Array<T>()` (initialized) for classes, `items!: Array<T>` for required-no-default.
- `dictionaryTypes` emits `Record<K, V> = {}`.
- Classes with simple `properties` initialize primitives (`id = ''`, `count = 0`) and use `!:` for non-primitive required fields.
- `customCode` newlines auto-indent.
- Decorators emitted directly above the class/property.
- File names: kebab-case derived from class name. `UserService` → `user-service.ts`. Enums → `*.enum.ts`.
- For `Map<K, V>`, use raw `type` with templateRefs:
  ```jsonc
  { "name": "cache", "type": "Map<string, $resp>", "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}] }
  ```
- For `Promise<T>`, raw `type` is fine, no import needed.
- For `Observable<T>` (rxjs), use raw `type` + templateRefs for T, plus `customImports: [{"path":"rxjs","types":["Observable"]}]`.

---

## Output structure

`generate_code` writes files under `outputPath` (or default), one file per file-generating type:
- Each `class`, `interface`, `enum`, and `customFile` becomes its own file.
- File naming = `{kebab(name)}.ts` for TS, `*.enum.ts` for enums (TS), `{PascalName}.cs` for C#, `{snake_name}.py` for Python, etc.
- Imports between files are computed automatically from `typeIdentifier`/`templateRefs` graph.
- Subdirectories created from each item's `path` field.
- Virtual types (`arrayTypes`, etc.) produce NO files but contribute imports.
- Result: a working compilable source tree with idiomatic per-language formatting.

---

## Worked patterns

### Pattern A — interfaces with cross-references

```jsonc
{
  "language": "typescript",
  "initialize": true,
  "interfaces": [
    { "name": "Address", "typeIdentifier": "address",
      "properties": [
        {"name": "street", "primitiveType": "String"},
        {"name": "city",   "primitiveType": "String"}
      ]},
    { "name": "User", "typeIdentifier": "user",
      "properties": [
        {"name": "id",      "primitiveType": "String"},
        {"name": "address", "typeIdentifier": "address"}
      ]}
  ]
}
```

### Pattern B — class with inheritance & method

```jsonc
{
  "language": "typescript",
  "classes": [
    { "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [{"name": "id", "primitiveType": "String"}] },
    { "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{"name": "email", "primitiveType": "String"}],
      "customCode": [
        {"code": "getDisplayName(): string { return this.email; }"}
      ]}
  ]
}
```

### Pattern C — generic class + concrete generic + extending class

```jsonc
{
  "language": "typescript",
  "classes": [
    { "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [{"name": "id", "primitiveType": "String"}] },
    { "name": "Repository", "typeIdentifier": "repo-generic",
      "genericArguments": [{
        "name": "T", "constraintTypeIdentifier": "base-entity",
        "propertyName": "items", "isArrayProperty": true
      }],
      "customCode": [
        {"code": "add(item: T): void { this.items.push(item); }"},
        {"code": "getAll(): T[] { return this.items; }"},
        {"code": "findById(id: string): T | undefined { return this.items.find(i => i.id === id); }"}
      ]},
    { "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{"name": "email", "primitiveType": "String"}] },
    { "name": "UserRepository", "typeIdentifier": "user-repo-class",
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

### Pattern D — array & dictionary types referenced from a class

```jsonc
{
  "language": "typescript",
  "classes": [
    {"name": "Product", "typeIdentifier": "product",
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Cart", "typeIdentifier": "cart",
     "properties": [
       {"name": "items", "typeIdentifier": "product-array", "comment": "Products in cart"},
       {"name": "tags",  "typeIdentifier": "string-array",  "comment": "Cart tags"},
       {"name": "scores","typeIdentifier": "score-dict"}
     ]}
  ],
  "arrayTypes": [
    {"typeIdentifier": "product-array", "elementTypeIdentifier": "product"},
    {"typeIdentifier": "string-array",  "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "score-dict", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"}
  ]
}
```

### Pattern E — service with DI and external imports + templateRefs

```jsonc
{
  "language": "typescript",
  "classes": [
    {"name": "Pet", "typeIdentifier": "pet",
     "properties": [{"name": "name", "primitiveType": "String"}]},
    {"name": "PetService", "typeIdentifier": "pet-service", "path": "services",
     "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
     "customImports": [
       {"path": "@nestjs/common", "types": ["Injectable", "inject"]},
       {"path": "@nestjs/common/http", "types": ["HttpClient"]},
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
     ]}
  ],
  "arrayTypes": [
    {"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}
  ]
}
```

### Pattern F — type aliases via customFiles + barrel import

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
    "customImports": [
      {"path": "../utils/types", "types": ["UserId", "Status", "ResultSet"]}
    ],
    "customCode": [
      {"code": "async getUser(id: UserId): Promise<unknown> { return null; }"},
      {"code": "updateStatus(id: UserId, status: Status): void { }"},
      {"code": "getResults<T>(data: T[]): ResultSet<T> { return {data, total: data.length, page: 1}; }"}
    ]
  }]
}
```

### Pattern G — interface with method signatures + class implementing it

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
    {"name": "UserRepository", "typeIdentifier": "user-repository",
     "implementsTypeIdentifiers": ["user-repo"],
     "customCode": [
       {"code": "async findAll(): Promise<$user[]> { return []; }",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
       {"code": "async findById(id: string): Promise<$user | null> { return null; }",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
     ]}
  ]
}
```

### Pattern H — enum + class consuming it

```jsonc
{
  "language": "typescript",
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [
      {"name": "Pending", "value": 0},
      {"name": "Shipped", "value": 2}
    ]}],
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

---

## Common mistakes (do NOT repeat)

1. Referencing a `typeIdentifier` not defined in the same call → property is silently dropped.
2. Putting interface method signatures as function-typed properties → implementing class duplicates them.
3. Writing internal type names as raw strings inside `customCode` (e.g., `"private repo: User"`) → no import generated. Use `$placeholder` + `templateRefs`.
4. Mixing `arrayTypes` with C#-style `List<T>` expectations → `arrayTypes` emits `IEnumerable<T>` in C# (in TS it's `Array<T>` which is fine).
5. Adding stdlib (`System`, `typing`, `java.util`, etc.) to `customImports` → duplicates/errors.
6. Duplicating `constructorParameters` in `properties[]` (C#/Java/Go/Groovy) → "Sequence contains more than one matching element".
7. Reserved words as property names (`delete`, `class`, `import`).
8. Splitting one logical schema into multiple `generate_code` calls → cross-file imports broken.
9. Expecting `Number` to map to floating-point in C# (it maps to `int`); use `"type": "double"` or `"type": "decimal"`.
10. Forgetting `fileName` when an `I`-prefixed TS interface and its impl class would collide on disk.
11. Putting blank-line padding inside `customCode.code` — newlines between members are auto-inserted.
12. Using `customCode` for plain field declarations without init — those belong in `properties[]`.

---

## Workflow for the next session

1. Parse the input spec (e.g., the OpenAPI/GraphQL/etc. described in the prompt) into the conceptual list: enums, interfaces (DTOs/contracts), classes (services/clients), arrayTypes, dictionaryTypes, concreteGenericClasses, customFiles.
2. Choose stable kebab-case `typeIdentifier`s. Make sure every reference (`baseClassTypeIdentifier`, `implementsTypeIdentifiers`, `typeIdentifier` in property, `templateRefs.typeIdentifier`) points to one defined in this same spec.
3. Decide field placement:
   - Pure type-only field → `properties[]`.
   - Anything with logic, init, decorators on a method, getter/setter, method signature → `customCode[]` (one item per member).
4. For every internal type used inside a `customCode.code` string, add a matching `templateRefs` entry with `$placeholder`.
5. For every external lib used inside a `customCode.code` string, add a `customImports` entry with the package path and named imports.
6. Do NOT add stdlib imports.
7. Issue a SINGLE `mcp__metaengine__generate_code` call with `language: "typescript"`, the full set of arrays, and (for the first call) `initialize: true`.
8. If the engine reports errors, fix the spec and call again — but never split into multiple partial calls.

---

## Key takeaways (one-liners)

- ONE call, ALL related types.
- `properties` = types only; `customCode` = members with bodies; one item per member.
- `templateRefs` for internal refs; `customImports` for externals; never mix.
- Auto-imports cover the language stdlib — don't duplicate.
- Virtual types (arrayTypes, dictionaryTypes, concreteGenerics) generate no files but enable correct imports.
- Constructor params auto-become properties in C#/Java/Go/Groovy; don't duplicate.
- TS strips `I` from interface export names; use `fileName` to avoid collisions.
