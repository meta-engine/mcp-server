# MetaEngine MCP — Knowledge Brief (Self-Contained)

This is the canonical reference for generating code via the MetaEngine MCP. The next session will not see the docs; everything needed to make a correct `generate_code` call is below.

---

## What MetaEngine is

A semantic code generation system exposed via MCP. You describe **types, relationships, and methods** as structured JSON; MetaEngine produces **compilable, correctly-imported source files**. It is *not* a template engine — it resolves cross-references, manages imports, and applies language idioms (e.g. Java `ALL_CAPS` enum members, Python `snake_case` methods) automatically.

Supported languages: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`.

A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools exposed

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns the AI guide (this brief). Optional `language` enum arg. Read-only. |
| `mcp__metaengine__generate_code` | **Primary tool.** Generates files from an inline JSON spec. |
| `mcp__metaengine__load_spec_from_file` | Same generation, but loads the spec from a `.json` file. Args: `specFilePath` (required), `outputPath`, `skipExisting`, `dryRun`. Use to keep large specs out of context. |
| `mcp__metaengine__generate_graphql` | Generate from GraphQL schema. |
| `mcp__metaengine__generate_openapi` | Generate from OpenAPI spec. |
| `mcp__metaengine__generate_protobuf` | Generate from protobuf definitions. |
| `mcp__metaengine__generate_sql` | Generate from SQL DDL. |

For the typical case (describe types directly), use `generate_code`.

---

## generate_code — full input schema

### Top-level fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `language` | enum | **yes** | — | One of `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`. |
| `outputPath` | string | no | `"."` | Output directory path (where files are written). |
| `packageName` | string | no | language-specific* | Namespace/package/module. Go default `github.com/metaengine/demo`; Java/Kotlin/Groovy default `com.metaengine.generated`. For C#, omit or set empty for GlobalUsings (no namespace). |
| `initialize` | boolean | no | `false` | Initialize properties with default values. |
| `skipExisting` | boolean | no | `true` | Skip writing files that already exist (stub pattern). |
| `dryRun` | boolean | no | `false` | Preview mode — returns generated code in response without writing files. |
| `classes` | array | no | — | Class definitions (regular & generic templates). |
| `interfaces` | array | no | — | Interface definitions (regular & generic templates). |
| `enums` | array | no | — | Enum definitions. |
| `arrayTypes` | array | no | — | Reusable array type references. **No files generated.** |
| `dictionaryTypes` | array | no | — | Reusable dictionary type references. **No files generated.** |
| `concreteGenericClasses` | array | no | — | Concrete generic class implementations (e.g. `Repository<User>`). **No files generated** — inline references only. |
| `concreteGenericInterfaces` | array | no | — | Concrete generic interface implementations (e.g. `IRepository<User>`). **No files generated.** |
| `customFiles` | array | no | — | Files without a class wrapper — type aliases, barrel exports, utilities. |

### `classes[]` — fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | **Unique handle** for cross-references in this batch. Use kebab-case. |
| `fileName` | string | Override file name (no extension). |
| `path` | string | Subdirectory (e.g. `"models"`, `"services/auth"`). |
| `comment` | string | Doc comment. |
| `isAbstract` | boolean | |
| `baseClassTypeIdentifier` | string | Reference base class via its `typeIdentifier` (or that of a `concreteGenericClasses` entry). |
| `interfaceTypeIdentifiers` | string[] | Interfaces this class implements. |
| `genericArguments` | array | Makes class a generic template. See below. |
| `properties` | array | Field declarations. See below. |
| `constructorParameters` | array | Items: `{ name, type?, primitiveType?, typeIdentifier? }`. **Auto-create properties in C#/Java/Go/Groovy** — never duplicate them in `properties`. In TypeScript they become `public X` constructor params (also become properties). |
| `customCode` | array | Methods, initialized fields, anything with logic. One block = one member. |
| `customImports` | array | External libraries only. Items: `{ path, types[] }`. |
| `decorators` | array | Items: `{ code, templateRefs? }`. |

### `properties[]` — fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any`. |
| `typeIdentifier` | string | Reference another type in this batch. |
| `type` | string | Free-form type expression (e.g. `"List<$user>"`, `"Map<string, $resp>"`). Use with `templateRefs`. |
| `isOptional` | boolean | Generates nullable (e.g. `string?` in C#). |
| `isInitializer` | boolean | Add default value initialization. |
| `comment` | string | Doc comment. |
| `commentTemplateRefs` | array | Template refs inside the comment. |
| `decorators` | array | Property-level decorators (e.g. `@IsEmail()`). |
| `templateRefs` | array | `{ placeholder, typeIdentifier }`. Required when `type` contains a `$placeholder`. |

A property must specify exactly one of `primitiveType`, `typeIdentifier`, or `type`.

### `customCode[]` — fields

| Field | Type | Notes |
|---|---|---|
| `code` | string | Source for **one** member (method, initialized field, constant, etc.). MetaEngine inserts blank lines between blocks automatically. |
| `templateRefs` | array | `{ placeholder, typeIdentifier }`. Required for every internal type referenced via `$placeholder`. |

### `genericArguments[]` — fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | Generic param name (`"T"`, `"K"`). |
| `constraintTypeIdentifier` | string | Constraint, e.g. `where T : BaseEntity`. |
| `propertyName` | string | If set, generates a property of type `T` with this name. |
| `isArrayProperty` | boolean | If true, the auto-created property is `T[]`. |

### `interfaces[]` — fields

Same shape as `classes[]` (without `isAbstract`, `constructorParameters`, `baseClassTypeIdentifier`). Has `interfaceTypeIdentifiers` for extending other interfaces. Use `customCode` for **method signatures** (terminate with `;`) — *not* function-typed properties.

### `enums[]` — fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | |
| `typeIdentifier` | string | |
| `fileName` | string | |
| `path` | string | |
| `comment` | string | |
| `members` | array | Items: `{ name, value }` (numeric values). |

### `arrayTypes[]` — fields

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string | **Required.** Handle to reference. |
| `elementPrimitiveType` | enum | `String`/`Number`/`Boolean`/`Date`/`Any`. |
| `elementTypeIdentifier` | string | Reference another type. |

(Specify exactly one of the two element fields.) **No file generated.**

### `dictionaryTypes[]` — fields

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string | **Required.** |
| `keyPrimitiveType` / `keyType` / `keyTypeIdentifier` | — | One of these. |
| `valuePrimitiveType` / `valueTypeIdentifier` | — | One of these. |

All four key/value combinations are valid (primitive×primitive, primitive×custom, custom×primitive, custom×custom).

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` — fields

| Field | Type | Notes |
|---|---|---|
| `identifier` | string | The handle to use as a `typeIdentifier` reference / `baseClassTypeIdentifier`. |
| `genericClassIdentifier` | string | Points to the generic template class/interface. |
| `genericArguments` | array | Items: `{ typeIdentifier?, primitiveType? }`. |

Used to create inline `Repository<User>`, `IRepository<User>` references with correct imports.

### `customFiles[]` — fields

| Field | Type | Notes |
|---|---|---|
| `name` | string | File name (no extension). |
| `fileName` | string | Alternative override. |
| `path` | string | Directory. |
| `identifier` | string | Optional — enables `customImports` from other files to reference this one by identifier. |
| `customCode` | array | One block per export/alias/function. |
| `customImports` | array | External imports for this file. |

Perfect for type aliases, helper functions, and barrel exports.

---

## Critical Rules (read these first)

### 1. ONE call with everything related

`typeIdentifier` references resolve **only within the current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting across calls breaks cross-file imports — they will not be generated.

### 2. `properties` = type declarations. `customCode` = everything else.

- `properties[]` declares fields with **types only**, no initialization.
- `customCode[]` handles methods, initialized fields, and any code with logic. **One `customCode` item = one member.**
- Never put methods in `properties`. Never put bare type declarations in `customCode`.

```jsonc
"properties": [{"name": "id", "primitiveType": "String"}],
"customCode": [
  {"code": "private http = inject(HttpClient);"},
  {"code": "getAll(): T[] { return this.items; }"}
]
```

### 3. Use `templateRefs` for every internal type reference inside `customCode`/`type`/`decorators`

Use `$placeholder` syntax with `templateRefs`. This is what triggers MetaEngine to add the import. Raw type names (e.g. `IUserRepository` as a literal string) **will not generate imports** and will compile-fail across namespaces.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

This applies to `properties.type`, `customCode.code`, `decorators.code`, and `comment` (via `commentTemplateRefs`).

**C# in particular:** Cross-namespace references without `templateRefs` will not get a `using` directive and will fail to compile.

### 4. Never add framework imports to `customImports`

MetaEngine auto-imports the standard library for each language. Adding them manually causes duplication or errors.

| Language | Auto-imported (never specify) |
|---|---|
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, +more |
| Swift | `Foundation` (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`, etc.) |
| Rust | `std::collections` (`HashMap`, `HashSet`), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (`UUID`, `Date`), `java.io` (`File`, `InputStream`, `OutputStream`) |
| Scala | `java.time.*`, `scala.math` (`BigDecimal`, `BigInt`), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | (no imports needed — built-ins) |

`customImports` is **only** for external libraries (`@angular/core`, `rxjs`, `FluentValidation`, etc.).

### 5. `templateRefs` are ONLY for internal types

If the type is in this batch → use `typeIdentifier` or `templateRefs`. If it's an external library → use `customImports`. Don't mix them.

### 6. Constructor parameters auto-create properties in C#/Java/Go/Groovy

Don't duplicate them in `properties[]` — causes `"Sequence contains more than one matching element"` error. Put shared/initialized fields in `constructorParameters` and additional-only fields in `properties`.

```jsonc
// CORRECT
"constructorParameters": [{"name": "email", "type": "string"}],
"properties": [{"name": "createdAt", "primitiveType": "Date"}]
```

(In TypeScript, `constructorParameters` produces `public email: string` syntax, also acting as properties — same de-duplication rule applies.)

### 7. Virtual types don't generate files

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create **reusable type references only**. They never produce files. Reference them via their `typeIdentifier` from `properties`/`customCode`.

---

## Pattern reference

### Cross-referenced types

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

### Class with inheritance + methods

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

Reference via `"typeIdentifier": "user-list"` in a property.

### Complex type expression with `templateRefs`

```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

Works in `properties`, `customCode`, `decorators`. The `$placeholder` is replaced with the resolved type and triggers the import.

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

Enums auto-suffix file names: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### Service with external dependency injection

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

### customFiles for type aliases / barrel exports

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

`identifier` lets other files use `customImports: [{path: "shared-types"}]` and have it resolve to the right relative path.

### Interface with method signatures (TS / C#)

When a class will `implements` the interface, declare method **signatures** in `customCode` (terminated with `;`), NOT as function-typed properties:

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

Function-typed properties (`"type": "() => Promise<User[]>"`) get duplicated as property declarations in implementing classes — avoid.

---

## Language-specific notes

### TypeScript
- MetaEngine **strips `I` prefix** from interface names: `IUserRepository` is exported as `UserRepository`. If both an `I…` interface and its implementation collide on file name, set `"fileName": "i-user-repository"` on the interface.
- Primitives: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- Auto-indent for `\n` inside `customCode`.
- Decorators directly supported.
- No imports needed for built-ins.
- `arrayTypes` produce `Array<T>`; dictionaries produce `Record<K, V>`.
- `customCode` blocks separated by automatic blank lines.

### C#
- `I` prefix **preserved** on interface names.
- `Number` → `int`. For decimals/doubles, set `"type": "decimal"` or `"type": "double"` explicitly.
- `packageName` sets the namespace. Omit for GlobalUsings.
- Interface properties → `{ get; }`. Class properties → `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with `templateRefs`.
- `isOptional` → `string?` (nullable reference type).
- **Every internal type reference inside `customCode` MUST use `templateRefs`** — otherwise no `using` directive is generated and cross-namespace builds fail.

### Python
- Must provide **explicit indentation** (4 spaces) after `\n` in `customCode`.
- `typing.*` imports automatic.
- Engine applies `snake_case` to method names automatically.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions in `customCode`.

### Java / Kotlin / Groovy / Scala
- Engine applies `ALL_CAPS` to enum members where idiomatic (notably Java).
- Constructor parameters auto-become properties (Java, Groovy).

### Rust / Swift / PHP
- Standard library auto-imports per the table in Rule 4.

---

## Output structure

- One file per `class`, `interface`, `enum`, `customFile`. (Virtual types — `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` — produce no files.)
- File names follow language conventions: `kebab-case.ts` for TS, `PascalCase.cs` for C#, etc.
- Files placed under `outputPath` (default `"."`) inside subdirectories from the `path` field.
- Imports/usings are auto-resolved across the batch.
- `dryRun: true` returns the generated code in the response without writing to disk — useful for inspection.
- `skipExisting: true` (default) leaves existing files untouched — useful for stub patterns.

---

## Common mistakes (anti-patterns)

1. **Don't** reference a `typeIdentifier` not present in the batch — the property is silently dropped. **Do** verify every `typeIdentifier` resolves.
2. **Don't** declare interface methods as function-typed properties on interfaces a class will `implements`. **Do** put method signatures in `customCode` ending with `;`.
3. **Don't** write internal type names as raw strings in `customCode` (e.g. `private repo: IUserRepository`). **Do** use `templateRefs` with `$placeholder`.
4. **Don't** use `arrayTypes` in C# when you need `List<T>`. **Do** use `"type": "List<$user>"` + `templateRefs`.
5. **Don't** add framework imports (`System.*`, `typing.*`, `java.util.*`, etc.) to `customImports`.
6. **Don't** duplicate constructor parameter names in `properties[]` (C#/Java/Go/Groovy → "Sequence contains more than one matching element"). **Do** put shared fields only in `constructorParameters`.
7. **Don't** use reserved words (`delete`, `class`, `import`) as property names. **Do** use `remove`, `clazz`, `importData`.
8. **Don't** split related types across multiple `generate_code` calls — cross-file imports won't resolve.
9. **Don't** expect `Number` to map to `double` in C# — it maps to `int`. Use `"type": "double"` / `"type": "decimal"`.
10. **Don't** forget `fileName` when an `I`-prefixed interface and its TS implementation would collide. **Do** set `"fileName": "i-user-repository"`.

---

## Recipe — typical end-to-end call

For a TypeScript user-management module (User class, IUserRepository interface, in-memory repo):

```jsonc
{
  "language": "typescript",
  "outputPath": "src",
  "interfaces": [{
    "name": "IUserRepository",
    "typeIdentifier": "user-repo-iface",
    "fileName": "i-user-repository",
    "customCode": [
      {"code": "findAll(): Promise<$user[]>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "findById(id: string): Promise<$user | null>;",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }],
  "classes": [
    {
      "name": "User", "typeIdentifier": "user",
      "properties": [
        {"name": "id", "primitiveType": "String"},
        {"name": "email", "primitiveType": "String"},
        {"name": "createdAt", "primitiveType": "Date"}
      ]
    },
    {
      "name": "InMemoryUserRepository",
      "typeIdentifier": "user-repo-impl",
      "interfaceTypeIdentifiers": ["user-repo-iface"],
      "customCode": [
        {"code": "private users: $user[] = [];",
         "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
        {"code": "async findAll(): Promise<$user[]> { return this.users; }",
         "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
        {"code": "async findById(id: string): Promise<$user | null> { return this.users.find(u => u.id === id) ?? null; }",
         "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
      ]
    }
  ]
}
```

Produces three files (`user.ts`, `i-user-repository.ts`, `in-memory-user-repository.ts`) with all imports correctly wired.

---

## Decision quick-reference

- Need a **field with a type** → `properties`.
- Need a **method**, **initialized field**, or **logic** → `customCode` (one block per member).
- Internal type used inside a `customCode`/`type`/`decorator` string → use `$placeholder` + `templateRefs`.
- External library type → `customImports` (NOT `templateRefs`).
- Reusable `T[]` or `Record<K, V>` → `arrayTypes` / `dictionaryTypes` (no files).
- Inline `Repository<User>` → `concreteGenericClasses`.
- File without a class wrapper (type aliases, barrel) → `customFiles`.
- Stdlib types → never list — auto-imported per language.
- Multiple related types → batch in **ONE** `generate_code` call.
