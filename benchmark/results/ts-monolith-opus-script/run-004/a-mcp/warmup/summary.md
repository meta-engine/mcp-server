# MetaEngine MCP — Knowledge Brief (TypeScript focus)

This brief is the *only* documentation the next session will have. It is comprehensive on purpose.

MetaEngine is a **semantic code generation system** exposed over MCP. You describe types, relationships, and methods as structured JSON; MetaEngine produces compilable, correctly-imported source files. Unlike string templates, it resolves cross-references, manages imports, and applies language idioms. **A single well-formed JSON call replaces dozens of error-prone file writes.** Supported languages: TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust.

---

## Tools exposed

- `mcp__metaengine__metaengine_initialize` — returns the AI guide; optional `language` arg for language-specific tips. Pure documentation; no code generation.
- `mcp__metaengine__generate_code` — **the workhorse**. Single entry point for generating files for any supported language.
- `mcp__metaengine__load_spec_from_file` — loads a JSON spec from disk (for prepared specs).
- `mcp__metaengine__generate_openapi` — generate from an OpenAPI spec.
- `mcp__metaengine__generate_graphql` — generate from a GraphQL schema.
- `mcp__metaengine__generate_protobuf` — generate from a Protobuf definition.
- `mcp__metaengine__generate_sql` — generate from a SQL schema.

For free-form code generation (the typical case), use **`generate_code`** with a structured spec.

---

## `generate_code` — full input schema

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **yes** | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | no | Output dir. Default `"."`. |
| `packageName` | string | no | Package/module/namespace. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C#: omit/empty → no namespace declaration (good for GlobalUsings). |
| `initialize` | bool | no, default `false` | Initialize properties with default values. |
| `dryRun` | bool | no, default `false` | Preview mode — returns code in response, does not write files. |
| `skipExisting` | bool | no, default `true` | Skip files that already exist (stub-friendly). |
| `classes` | array | no | Class definitions (regular + generic templates). |
| `interfaces` | array | no | Interface definitions (regular + generic templates). |
| `enums` | array | no | Enum definitions. |
| `customFiles` | array | no | Files without a class wrapper (type aliases, barrel exports, utilities). |
| `arrayTypes` | array | no | Reusable array type *references* — **no files generated**. |
| `dictionaryTypes` | array | no | Reusable dictionary type *references* — **no files generated**. |
| `concreteGenericClasses` | array | no | Concrete generics like `Repository<User>` — **no files generated**, type reference only. |
| `concreteGenericInterfaces` | array | no | Concrete generic interfaces like `IRepository<User>` — **no files generated**. |

### `classes[]` schema

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | **Unique** id used to reference this class from other types. |
| `path` | string | Directory under outputPath (e.g. `models`, `services/auth`). |
| `fileName` | string | Override file name (no extension). |
| `comment` | string | Class-level doc comment. |
| `isAbstract` | bool | Abstract class. |
| `baseClassTypeIdentifier` | string | Type id of base class to extend. |
| `interfaceTypeIdentifiers` | string[] | Interface ids to implement. |
| `genericArguments` | array | Makes this a generic *template* like `Repository<T>`. See generic args below. |
| `constructorParameters` | array | See constructor params below. |
| `properties` | array | Field declarations (types only). See property schema below. |
| `customCode` | array | Methods, initialized fields, anything with logic. One block = one member. See customCode schema below. |
| `decorators` | array | Class decorators (`{code, templateRefs?}`). |
| `customImports` | array | External library imports. `[{path: "...", types: ["..."]}]`. |

### `interfaces[]` schema
Same shape as classes (subset): `name`, `typeIdentifier`, `path`, `fileName`, `comment`, `genericArguments`, `interfaceTypeIdentifiers` (extend other interfaces), `properties`, `customCode`, `customImports`, `decorators`.

### `enums[]` schema
- `name`, `typeIdentifier`, `path`, `fileName`, `comment`
- `members[]`: `{name: string, value: number}`
- Auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### `customFiles[]` schema (type aliases, barrel exports, utilities)
- `name`, `path`, `fileName`, `identifier` (optional id for `customImports` from other files)
- `customCode[]`: one block per export/alias/function
- `customImports[]`

### `properties[]` (used in classes & interfaces)

| Field | Notes |
|---|---|
| `name` | Property name. Avoid reserved words (`delete`, `class`, `import`). |
| `primitiveType` | `String`, `Number`, `Boolean`, `Date`, `Any` (mutually exclusive with `type`/`typeIdentifier`). |
| `typeIdentifier` | Reference to a type defined in this batch (or a virtual array/dict/concreteGeneric). |
| `type` | Free-form type expression (e.g. `"List<$user>"`, `"Map<string, $resp>"`) — combine with `templateRefs`. |
| `isOptional` | bool — generates `?` (nullable). |
| `isInitializer` | bool — emit default initializer. |
| `comment` | Doc comment (TSDoc/XmlDoc/etc.). |
| `commentTemplateRefs` | template refs for the comment. |
| `decorators` | Property decorators (`@IsEmail()`, `@Required()`...). |
| `templateRefs` | `[{placeholder: "$x", typeIdentifier: "y"}]` — required if `type` references an internal type. |

### `constructorParameters[]`
- `{name, primitiveType?, typeIdentifier?, type?}`
- TypeScript: become `public X` constructor params (auto-properties).
- C#/Java/Go/Groovy: also auto-create properties — **do NOT duplicate in `properties[]`** (errors with "Sequence contains more than one matching element").

### `customCode[]` blocks

```jsonc
{
  "code": "getUser(): Promise<$user> { return this.fetchUser(); }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

- **One block = one member**. Automatic newlines between blocks.
- Use `$placeholder` syntax for any internal type reference; declare in `templateRefs` so MetaEngine can emit imports.
- TypeScript auto-indents on `\n`. **Python requires explicit 4-space indent** after `\n`.

### `genericArguments[]` (on classes/interfaces)
- `name` (e.g. `"T"`, `"K"`)
- `constraintTypeIdentifier` — generic constraint (e.g. `where T : BaseEntity`)
- `propertyName` — auto-create a property of type `T` with this name
- `isArrayProperty` — make that property `T[]`

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]`
```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}
```
Creates a virtual `Repository<User>` reference. Use it in `baseClassTypeIdentifier`, properties, or via templateRefs. **No files generated.**

### `arrayTypes[]`
```jsonc
{"typeIdentifier": "user-list", "elementTypeIdentifier": "user"}
{"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
```
Reference via `typeIdentifier` in property definitions. No files. In TypeScript renders as `Array<User>`. In **C# renders as `IEnumerable<T>`** — use `"type": "List<$user>"` with templateRefs if you need `List<T>`.

### `dictionaryTypes[]`
All four combinations supported:
```jsonc
{"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"}
{"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
{"typeIdentifier": "by-user", "keyTypeIdentifier": "user", "valuePrimitiveType": "String"}
{"typeIdentifier": "meta", "keyTypeIdentifier": "user", "valueTypeIdentifier": "metadata"}
```
TypeScript renders as `Record<K, V>`.

### `customImports[]`
- `[{path: "@angular/core", types: ["Injectable", "inject"]}]`
- Use **only for external libraries** or for resolving customFile `identifier` references.
- **NEVER** include framework/std-lib imports — see auto-import table.

---

## The seven critical rules (don't violate)

### 1. Generate ALL related types in ONE call
`typeIdentifier` references resolve **only within the current batch**. Splitting `User` and `UserService` across two calls breaks imports. Batch everything that references each other.

### 2. Properties = type declarations. CustomCode = everything else
- `properties[]`: field name + type. **No initialization, no logic.**
- `customCode[]`: methods, initialized fields (`private http = inject(HttpClient);`), any code with logic. **One block = one member**.
- Never put methods in properties. Never put uninitialized type declarations in customCode.

### 3. Use `templateRefs` for internal types in customCode (and in `type` strings)
Without templateRefs, MetaEngine **cannot** emit the import/using directive. Raw type names in `code` strings will compile-fail across files.
```jsonc
{"code": "getUser(): Promise<$user> { ... }",
 "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
```
**Critical in C#**: every internal type in customCode MUST use templateRefs.

### 4. Never add framework imports to `customImports`
MetaEngine auto-imports the standard library per language:

| Language   | Auto-imported (never specify) |
|------------|---|
| C#         | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python     | `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java       | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, jackson |
| Kotlin     | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, etc. |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder…) |
| Rust       | `std::collections` (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy     | `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` |
| Scala      | `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP        | DateTime\*, DateTimeImmutable, Exception\*, ArrayObject, JsonSerializable, Stringable |
| TypeScript | (no imports needed — built-in types) |

`customImports` is **only** for external libraries (`@angular/core`, `rxjs`, `FluentValidation`, etc.) or for cross-customFile references via `identifier`.

### 5. templateRefs are ONLY for internal types
External library types use `customImports`. Internal types in this batch use `typeIdentifier` (in property fields) or `templateRefs` (in `code`/`type` strings). **Never mix.**

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Don't duplicate in `properties[]` → "Sequence contains more than one matching element" error. Only put **non-constructor** properties in `properties[]`.

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are **reference-only** — used by referencing their `typeIdentifier` in properties or templateRefs of file-generating types.

---

## TypeScript-specific notes

- **`I` prefix is stripped** from interface names. `IUserRepository` → exported as `UserRepository`. If this collides with the implementing class file, set `fileName: "i-user-repository"` on the interface.
- Primitive mappings: `String`→`string`, `Number`→`number`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`.
- Auto-indent for customCode `\n`. (Python is the exception — it requires manual 4-space indent.)
- Decorators are emitted directly above the member.
- No imports for built-in types — TS column in the table above is empty.
- `arrayTypes` render as `Array<T>` (not `T[]`). Both work in TS.
- `dictionaryTypes` render as `Record<K, V>`.
- For interfaces a class will `implements`, define **method signatures in `customCode` with trailing `;`**, NOT as function-typed properties (function-typed properties get duplicated as fields on the implementing class).
- `initialize: true` at top level emits property initializers (`id = ''`, `tags = new Array<string>()`, etc.). With `initialize` off you get `id!: string;` style.

## C#-specific notes (for completeness)
- `I` prefix kept on interfaces.
- `Number` → `int` (not `double`). Use explicit `"type": "decimal"` or `"type": "double"` for non-integer numbers.
- Interface props → `{ get; }`; class props → `{ get; set; }`.
- `arrayTypes` → `IEnumerable<T>`; for `List<T>` use `"type": "List<$user>"` + templateRefs.
- `isOptional` on a property → `string?` (nullable reference type).
- Empty/missing `packageName` → no namespace declaration emitted.

## Python-specific notes
- **You must indent customCode bodies with 4 spaces after `\n`** — auto-indent is not applied.
- `typing.*`, pydantic, datetime, decimal, enum, abc, dataclasses are auto-imported.
- Engine applies idiomatic transformations (snake_case method names).

## Java-specific notes
- Constructor params auto-create properties (don't duplicate).
- Engine applies idiomatic transformations (e.g. `ALL_CAPS` enum members).
- `java.util.*`, `java.time.*`, jakarta.validation, jackson auto-imported.

## Go-specific notes
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions in `customCode`.

---

## Output structure

`generate_code` produces one `.ts`/`.cs`/`.py`/etc. file per `class`, `interface`, `enum`, and `customFile` definition. Files are placed under `outputPath` (default `.`), inside any per-type `path` subdirectory. Imports between files are emitted automatically using relative paths derived from `path`. With `dryRun: true`, file contents come back in the response instead of being written.

---

## Patterns the next session is most likely to need

### A. Plain DTO interfaces with cross-references (very common for TS)
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
→ Two files, mutual import resolved.

### B. Class with array property + cross-type
```jsonc
{
  "language": "typescript",
  "classes": [
    {"name": "Product", "typeIdentifier": "product",
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Cart", "typeIdentifier": "cart",
     "properties": [
       {"name": "items", "typeIdentifier": "product-array", "comment": "Products in cart"},
       {"name": "tags",  "typeIdentifier": "string-array",  "comment": "Cart tags"}
     ]}
  ],
  "arrayTypes": [
    {"typeIdentifier": "product-array", "elementTypeIdentifier": "product"},
    {"typeIdentifier": "string-array",  "elementPrimitiveType": "String"}
  ]
}
```

### C. Enum + class that uses it
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

### D. Service with external DI (NestJS/Angular shape)
```jsonc
{
  "classes": [{
    "name": "PetService", "typeIdentifier": "pet-service", "path": "services",
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
       "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}]
}
```

### E. Generic base + concrete implementation
```jsonc
{
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

### F. Type aliases via `customFiles`
```jsonc
{
  "customFiles": [{
    "name": "types", "path": "shared", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Email = string;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"}
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers",
    "customImports": [{"path": "shared-types"}],
    "customCode": [{"code": "static format(email: Email): string { return email.trim(); }"}]
  }]
}
```

### G. Interface a class implements
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
Note: signatures end with `;`, declared in `customCode` (not as function-typed properties).

---

## Top-10 mistakes to avoid (memorize these)

1. **Referencing a `typeIdentifier` that doesn't exist in the batch** — the property is silently dropped. Verify every id matches a defined type in the same call.
2. Putting method signatures as **function-typed properties** on interfaces a class will `implements` — they get duplicated as fields. Use `customCode` instead.
3. Writing **internal type names as raw strings** in customCode (`"private repo: IUserRepository"`). Use templateRefs: `"$repo"` + `templateRefs`.
4. Using `arrayTypes` in C# when you need `List<T>`. Use `"type": "List<$user>"` + templateRefs.
5. Adding **framework/std-lib imports** to `customImports` (`System.*`, `typing.*`, `java.util.*`). MetaEngine auto-handles these.
6. Duplicating constructor parameter names in `properties[]` for **C#/Java/Go/Groovy** → "Sequence contains more than one matching element".
7. Using **reserved words** as property names (`delete`, `class`, `import`). Use `remove`, `clazz`, `importData`.
8. **Generating related types in separate calls.** Cross-file imports only resolve within a single batch.
9. Expecting `Number` → `double` in C#. It maps to `int`. Use explicit `"type": "double"` or `"decimal"` when needed.
10. **Forgetting `fileName`** when an `I`-prefixed interface and its implementing class would collide in TypeScript (because the `I` prefix is stripped from the *exported name* but not necessarily the *file*).

---

## Strategy for the gen session

1. **Plan first.** Identify every type the spec needs (entities, DTOs, enums, services, interfaces, repositories, helpers). Sketch the relationship graph mentally.
2. **One `generate_code` call.** Put **all** classes/interfaces/enums/customFiles/arrayTypes/dictionaryTypes/concreteGenericClasses into a single call so cross-references resolve.
3. **Pick a `typeIdentifier` naming convention** and stick with it (kebab-case is conventional). Each id must be unique across the batch.
4. **Use properties for type declarations only.** Use customCode for methods and initialized fields. One customCode block per member.
5. **Every internal type used inside a `code` or `type` string requires a `templateRefs` entry.** No exceptions.
6. **Don't include framework imports.** Only external libraries belong in `customImports`.
7. For TypeScript specifically: rely on built-in types, no imports for `string`/`number`/`Date`. Use `Array<T>`/`Record<K,V>` mental model. Watch for the `I`-prefix-stripping behavior.
8. **If something needs default values** (e.g. `new Array<Pet>()`), set `initialize: true` at the top level *or* express the initializer explicitly via customCode.
9. **Set `dryRun: true`** if you want to preview without writing files; otherwise it writes under `outputPath`.
10. **Trust the engine.** Idiomatic transformations (e.g. snake_case in Python, ALL_CAPS enum members in Java) are intentional; don't fight them.
