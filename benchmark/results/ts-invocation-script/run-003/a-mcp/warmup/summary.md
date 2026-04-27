# MetaEngine MCP — Knowledge Brief (TypeScript focus)

MetaEngine is a **semantic code generator** exposed via MCP. You describe types, relationships, and methods as a structured JSON spec; MetaEngine emits compilable source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, it resolves cross-references, manages imports, and applies language idioms automatically. **One well-formed JSON call replaces dozens of manual file writes.**

---

## Tools exposed (the MCP server)

- `mcp__metaengine__metaengine_initialize(language?)` — returns the same guide content this brief is built from. **Already done in warmup.** Do not call again in the gen session.
- `mcp__metaengine__generate_code(...)` — **the main tool.** Takes a structured JSON spec (classes, interfaces, enums, customFiles, arrayTypes, dictionaryTypes, concreteGenericClasses, concreteGenericInterfaces) plus `language`, `outputPath`, `packageName`, `initialize`, `skipExisting`, `dryRun`. Writes one file per generating type to disk.
- `mcp__metaengine__load_spec_from_file({specFilePath, outputPath?, skipExisting?, dryRun?})` — same as `generate_code`, but the spec is read from a JSON file on disk. Use this when the spec is large to keep it out of context. Overrides for outputPath / skipExisting / dryRun apply on top of values inside the file.
- `mcp__metaengine__generate_graphql({framework, graphQLSchema, ...})` — HTTP client from a GraphQL SDL.
- `mcp__metaengine__generate_openapi({framework, openApiSpec | openApiSpecUrl, ...})` — HTTP client from OpenAPI YAML/JSON.
- `mcp__metaengine__generate_protobuf({framework, protoSource, ...})` — HTTP client from `.proto` definitions.
- `mcp__metaengine__generate_sql({language, ddlSource, ...})` — model classes from `CREATE TABLE` DDL.

For arbitrary domain code (the case the gen session is asked to do), you almost always want **`generate_code`** (or `load_spec_from_file` if the JSON gets long).

---

## Cardinal rule: ONE call with the full spec

`typeIdentifier` references **only resolve within the current batch.** If `UserService` references `User`, both must be in the same `generate_code` call. Splitting a domain into multiple calls breaks the typegraph — cross-file imports won't be generated. **Always batch the entire model, all related interfaces, all services, all DTOs into a single call.** This is the single most important rule.

---

## generate_code — full input schema

Top-level fields:

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | Defaults to `.`. Directory where files are written. |
| `packageName` | string | Namespace/package/module. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C#: empty → no namespace declared (GlobalUsings pattern). |
| `initialize` | boolean | When true, properties get default-value initialization. |
| `skipExisting` | boolean (default `true`) | Don't overwrite existing files (stub pattern). |
| `dryRun` | boolean (default `false`) | Return file contents in response, don't write to disk. Useful for preview. |
| `classes` | array | Class definitions (regular + generic templates). |
| `interfaces` | array | Interface definitions (regular + generic templates). |
| `enums` | array | Enum definitions. |
| `customFiles` | array | Files without a class wrapper — type aliases, barrel exports, utility code. |
| `arrayTypes` | array | Reusable array type references. **No files generated.** |
| `dictionaryTypes` | array | Reusable dictionary type references. **No files generated.** |
| `concreteGenericClasses` | array | Concrete generic instantiations (`Repository<User>`). **No files generated.** |
| `concreteGenericInterfaces` | array | Concrete generic interface instantiations (`IRepository<User>`). **No files generated.** |

### `classes[]` — full shape

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | Unique ID used by other types to reference this class. |
| `fileName` | string | Override file name (no extension). Use for collision avoidance. |
| `path` | string | Subdirectory (e.g., `services`, `models/auth`). |
| `comment` | string | Doc comment for the class. |
| `isAbstract` | boolean | Abstract class. |
| `baseClassTypeIdentifier` | string | Type ID of base class to extend (resolves within batch). |
| `interfaceTypeIdentifiers` | string[] | IDs of interfaces this class implements. |
| `genericArguments` | array | Makes this a generic template. Each: `{ name: "T", constraintTypeIdentifier?, propertyName?, isArrayProperty? }`. `propertyName` auto-creates a field of type `T` (or `T[]` if `isArrayProperty`). |
| `properties` | array | Field declarations only — no logic, no initialization. See property shape below. |
| `constructorParameters` | array | TS/C#/Java/Go/Groovy: each entry **auto-becomes a property**. **Don't duplicate in `properties[]`** (causes "Sequence contains more than one matching element"). Shape: `{ name, primitiveType?, type?, typeIdentifier? }`. |
| `customCode` | array | Methods, initialized fields, anything with logic. ONE entry per member. Shape: `{ code: string, templateRefs?: [{ placeholder, typeIdentifier }] }`. Auto-newlines between entries. |
| `customImports` | array | External library imports only. Shape: `{ path, types?: string[] }`. |
| `decorators` | array | Class-level decorators/attributes. Shape: `{ code, templateRefs? }`. |

### `interfaces[]` — full shape

Same as classes but: no `constructorParameters`, no `isAbstract`, no `baseClassTypeIdentifier`. `interfaceTypeIdentifiers` extends other interfaces. Method signatures go in `customCode` (NOT as function-typed properties — see Common Mistakes).

### `enums[]` — full shape

`{ name, typeIdentifier, fileName?, path?, comment?, members: [{ name, value: number }] }`. Filenames auto-suffix per language (TS: `order-status.enum.ts`, C#: `OrderStatus.cs`).

### `properties[]` — full shape

| Field | Type | Notes |
|---|---|---|
| `name` | string | Field name. **Avoid reserved words** (`delete`, `class`, `import`) — use safe alternatives. |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any`. |
| `type` | string | Free-form type expression for complex/external types. Combine with `templateRefs` to inject internal types. |
| `typeIdentifier` | string | Reference to another generated type (or arrayType/dictionaryType). |
| `templateRefs` | array | `[{ placeholder: "$x", typeIdentifier: "..." }]` — for use inside `type` strings. |
| `comment` | string | Doc comment. |
| `commentTemplateRefs` | array | templateRefs usable inside the comment. |
| `isOptional` | boolean | Generates `string?` (C#), `string \| undefined` (TS). |
| `isInitializer` | boolean | Add default-value initialization. |
| `decorators` | array | Property-level decorators (`@IsEmail()`, `@Required()`, etc.). |

Use **exactly one** of `primitiveType`, `type`, or `typeIdentifier` per property.

### `customCode[]` entry shape

`{ code: string, templateRefs?: [{ placeholder: "$x", typeIdentifier: "..." }] }`. **One member per entry.** The engine inserts newlines between blocks. Reference internal types with `$placeholder` — never bare type names — so imports auto-resolve.

### `customFiles[]` — full shape

`{ name, fileName?, path?, identifier?, customCode: [{ code, templateRefs? }], customImports?: [{ path, types? }] }`. `identifier` lets *other* files reference this one via `customImports: [{ path: "<identifier>" }]`, and the engine resolves the relative path automatically.

### `arrayTypes[]` — virtual

`{ typeIdentifier, elementTypeIdentifier?, elementPrimitiveType? }`. No file generated. Reference via `typeIdentifier` in property/customCode.
- **C# gotcha:** `arrayTypes` produces `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with `templateRefs` instead.

### `dictionaryTypes[]` — virtual

`{ typeIdentifier, keyPrimitiveType? | keyTypeIdentifier? | keyType?, valuePrimitiveType? | valueTypeIdentifier? }`. All four combinations of primitive/custom for key/value are supported. TS output: `Record<K, V>`.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` — virtual

`{ identifier, genericClassIdentifier, genericArguments: [{ typeIdentifier? | primitiveType? }] }`. Creates an inline reference like `Repository<User>` that other classes can extend via `baseClassTypeIdentifier` or use as a property type. No file generated.

---

## The seven critical rules (ordered by frequency of failure)

1. **One call, all related types.** `typeIdentifier` only resolves inside the same call. Split it and imports break.

2. **`properties[]` = type declarations only. `customCode[]` = everything else.**
   - Property: type only, no init. `{ "name": "id", "primitiveType": "String" }`
   - CustomCode: methods, initialized fields. `{ "code": "private http = inject(HttpClient);" }`
   - **Never put methods in properties. Never put uninitialized declarations in customCode.**

3. **Use `templateRefs` for internal types in `customCode`.** Without them MetaEngine can't generate the import. Pattern:
   ```jsonc
   "customCode": [{
     "code": "getUser(): Promise<$user> { ... }",
     "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
   }]
   ```
   In C#, this is **mandatory** — bare `IUserRepository` strings cross-namespace won't compile.

4. **Never add framework imports to `customImports`.** Auto-imported per-language (don't specify):
   - **TypeScript:** none — built-in types only.
   - C#: `System.*`, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*
   - Python: `typing.*`, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses
   - Java: `java.util.*`, `java.time.*`, stream, math, jakarta.validation, jackson
   - Kotlin: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`
   - Go: time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http
   - Swift: Foundation
   - Rust: `std::collections`, chrono, uuid, rust_decimal, serde
   - Groovy: `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io`
   - Scala: `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*`
   - PHP: DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable

   `customImports` is for **external libraries only** (`@angular/core`, `rxjs`, `FluentValidation`, etc.).

5. **`templateRefs` are ONLY for internal types** (defined in the same call). External library types use `customImports`. Never mix.

6. **Constructor parameters auto-create properties** in C#, Java, Go, Groovy. Don't duplicate them in `properties[]` (TypeScript also auto-creates from `constructorParameters` with `public` modifier — same rule).

7. **Virtual types don't produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reference-only. Use them as property types via `typeIdentifier`.

---

## TypeScript specifics

- **`I` prefix on interfaces is stripped.** `IUserRepository` exports as `UserRepository`. If both an `I`-prefixed interface and a same-stem class would collide on filename, set `fileName: "i-user-repository"` on the interface.
- Primitive map: `String`→`string`, `Number`→`number`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`.
- Decorators are emitted directly (e.g., `@Injectable({ providedIn: 'root' })`).
- `customCode` newlines (`\n`) are auto-indented.
- **For interface method signatures** (interface that a class will `implements`), put them in `customCode` (e.g. `"findById(id: string): Promise<$user | null>;"`), NOT as function-typed properties (`"type": "() => Promise<User[]>"`). Otherwise the implementing class duplicates them as property declarations alongside its real methods.
- **Built-in types need no imports.** Don't add `customImports` for `Promise`, `Array`, `Map`, `Record`, etc.

### Other languages — quick gotchas (in case the spec drifts)

- **C#:** `Number` maps to `int`, not `double`. Use `"type": "decimal"` or `"type": "double"` explicitly. Interface props → `{ get; }`; class props → `{ get; set; }`. `isOptional` → `string?`. arrayTypes → `IEnumerable<T>`; for `List<T>` use `"type": "List<$user>"` + templateRefs.
- **Python:** Must include explicit 4-space indentation after `\n` in `customCode` (no auto-indent). typing imports are automatic.
- **Go:** Requires `packageName` for multi-file projects. No constructors — use factory functions in `customCode`.
- **Java/Kotlin/Groovy:** `packageName` required for proper folder layout.

---

## Pattern cookbook (copy-paste targets)

### Basic interfaces with cross-references
```jsonc
{
  "language": "typescript",
  "interfaces": [
    { "name": "Address", "typeIdentifier": "address",
      "properties": [
        { "name": "street", "primitiveType": "String" },
        { "name": "city",   "primitiveType": "String" }
      ]
    },
    { "name": "User", "typeIdentifier": "user",
      "properties": [
        { "name": "id",      "primitiveType": "String" },
        { "name": "address", "typeIdentifier": "address" }
      ]
    }
  ]
}
```
→ Two `.ts` files with auto-imports.

### Class with inheritance and methods
```jsonc
{
  "classes": [
    { "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [{ "name": "id", "primitiveType": "String" }] },
    { "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{ "name": "email", "primitiveType": "String" }],
      "customCode": [
        { "code": "getDisplayName(): string { return this.email; }" }
      ]
    }
  ]
}
```

### Generic class + concrete instantiation
```jsonc
{
  "classes": [
    { "name": "Repository", "typeIdentifier": "repo-generic",
      "genericArguments": [{
        "name": "T", "constraintTypeIdentifier": "base-entity",
        "propertyName": "items", "isArrayProperty": true
      }],
      "customCode": [
        { "code": "add(item: T): void { this.items.push(item); }" },
        { "code": "getAll(): T[] { return this.items; }" }
      ]
    },
    { "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{ "name": "email", "primitiveType": "String" }] },
    { "name": "UserRepository", "typeIdentifier": "user-repo-class",
      "baseClassTypeIdentifier": "user-repo-concrete",
      "customCode": [{
        "code": "findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
        "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
      }]
    }
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{ "typeIdentifier": "user" }]
  }]
}
```

### Array & dictionary types
```jsonc
{
  "arrayTypes": [
    { "typeIdentifier": "user-list",  "elementTypeIdentifier": "user" },
    { "typeIdentifier": "string-arr", "elementPrimitiveType": "String" }
  ],
  "dictionaryTypes": [
    { "typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number" },
    { "typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
  ]
}
```
TS output: `new Array<User>()`, `Record<string, number>`, etc.

### Complex type expression with templateRefs in `type`
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{ "placeholder": "$resp", "typeIdentifier": "api-response" }]
}]
```
templateRefs work in `properties.type`, `customCode.code`, and `decorators.code`.

### Enum + class that uses it
```jsonc
{
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [
      { "name": "Pending", "value": 0 },
      { "name": "Shipped", "value": 2 }
    ]
  }],
  "classes": [{
    "name": "Order", "typeIdentifier": "order",
    "properties": [{ "name": "status", "typeIdentifier": "order-status" }],
    "customCode": [{
      "code": "updateStatus(s: $status): void { this.status = s; }",
      "templateRefs": [{ "placeholder": "$status", "typeIdentifier": "order-status" }]
    }]
  }]
}
```

### Service with external DI (Angular/NestJS pattern)
```jsonc
{
  "classes": [{
    "name": "ApiService", "typeIdentifier": "api-service",
    "decorators": [{ "code": "@Injectable({ providedIn: 'root' })" }],
    "customImports": [
      { "path": "@angular/core",            "types": ["Injectable", "inject"] },
      { "path": "@angular/common/http",     "types": ["HttpClient"] },
      { "path": "rxjs",                     "types": ["Observable"] }
    ],
    "customCode": [
      { "code": "private http = inject(HttpClient);" },
      { "code": "getUsers(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
        "templateRefs": [{ "placeholder": "$list", "typeIdentifier": "user-array" }] }
    ]
  }],
  "arrayTypes": [{ "typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto" }]
}
```

### Type aliases / barrels via `customFiles`
```jsonc
{
  "customFiles": [{
    "name": "types", "path": "shared", "identifier": "shared-types",
    "customCode": [
      { "code": "export type UserId = string;" },
      { "code": "export type Email  = string;" }
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers",
    "customImports": [{ "path": "shared-types" }],
    "customCode": [
      { "code": "static format(email: Email): string { return email.trim(); }" }
    ]
  }]
}
```
The `identifier` enables import resolution; the importing file gets a correct relative path.

### Interface method signatures (NOT function-typed properties)
```jsonc
{
  "interfaces": [{
    "name": "IUserRepository", "typeIdentifier": "user-repo",
    "fileName": "i-user-repository",
    "customCode": [
      { "code": "findAll(): Promise<$user[]>;",
        "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] },
      { "code": "findById(id: string): Promise<$user | null>;",
        "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
    ]
  }]
}
```

### Constructor parameters (don't duplicate in properties)
```jsonc
{
  "enums": [{ "name": "Status", "typeIdentifier": "status",
    "members": [{ "name": "Active", "value": 1 }] }],
  "classes": [{
    "name": "User", "typeIdentifier": "user",
    "constructorParameters": [
      { "name": "email",  "type": "string" },
      { "name": "status", "typeIdentifier": "status" }
    ],
    "properties": [
      { "name": "createdAt", "primitiveType": "Date" }   // additional fields ONLY
    ]
  }]
}
```
TS output: `constructor(public email: string, public status: Status) {}`, plus `createdAt!: Date;` declaration.

---

## Output structure

- One file per `class`, `interface`, `enum`, and `customFile` entry. Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) emit no file.
- File names follow language conventions: TS uses kebab-case (`user-service.ts`); C# uses PascalCase (`UserService.cs`); enums get language-specific suffix (`order-status.enum.ts` in TS).
- `path` puts the file in a subdirectory under `outputPath`.
- Imports/usings are auto-generated for every internal-type reference made through `typeIdentifier` or `templateRefs`. External-library imports come from `customImports`. Standard-library imports are auto-injected.
- Constructor parameters in TS emit `public` shorthand: `constructor(public email: string) {}`.
- `dryRun: true` returns file contents in the response without writing — use this for verification before writing for real.

---

## Common-mistake checklist (read before generating)

1. **Don't** reference a `typeIdentifier` not defined in the batch → property is silently dropped. **Verify every ID exists.**
2. **Don't** use function-typed properties for interface methods. **Use `customCode` with method-signature strings.**
3. **Don't** write internal type names as raw strings in `customCode`. **Use `$placeholder` + `templateRefs`.**
4. **Don't** use `arrayTypes` in C# when you need `List<T>` (it produces `IEnumerable<T>`). **Use `"type": "List<$x>"` + templateRefs.**
5. **Don't** add `System.*`, `typing.*`, `java.util.*`, `Promise`, `Array`, `Map` etc. to `customImports`. **Let the engine handle them.**
6. **Don't** duplicate constructor parameter names in `properties[]` for C#/Java/Go/Groovy. (TS also auto-creates from constructorParameters with `public` shorthand — same rule.) **Only put additional, non-constructor fields in `properties[]`.**
7. **Don't** use reserved words (`delete`, `class`, `import`) as property names. **Use safe alternatives.**
8. **Don't** generate related types in separate calls. **Batch everything.**
9. **Don't** assume `Number` → `double` in C#. **It maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.**
10. **Don't** let `I`-prefixed interfaces and same-stem classes collide on filenames in TS. **Set `fileName` on the interface.**

---

## Workflow recommendation for the gen session

1. **Plan the spec on paper / in head first.** Enumerate every class, interface, enum, array type, dictionary type, concrete generic. Pick `typeIdentifier`s up front.
2. **Build a single JSON object** with `language: "typescript"`, an `outputPath`, and arrays for each kind. If the spec is large, write it to a `.json` file and call `load_spec_from_file`.
3. **Verify all `typeIdentifier` references** point to defined IDs. Missing IDs are silently dropped.
4. **Use `dryRun: true` first** to inspect file contents in the response. When the output looks right, call again with `dryRun: false` to write to disk.
5. **One MCP call.** Don't loop, don't split per-domain. The whole graph in one shot.

---

## Quick decision rules

- Need a method, an initialized field, or any code with logic? → `customCode`.
- Need a plain field with just a type? → `properties`.
- Field references another generated type? → use `typeIdentifier` on the property.
- Field type is a complex expression that mentions a generated type? → `type: "Map<string, $x>"` + `templateRefs`.
- Code references a generated type? → `$placeholder` + `templateRefs` inside `customCode.code`.
- Code references an external library? → bare type name, plus a `customImports` entry.
- Need `Repository<User>` as a base class? → `concreteGenericClasses` with an `identifier`, then `baseClassTypeIdentifier: "<that-identifier>"`.
- Need a `User[]` field? → an `arrayTypes` entry, then `typeIdentifier` on the property.
- Need a type alias / utility export? → `customFiles` (with an `identifier` if other files import it).
- Need an interface that a class will `implements`? → method **signatures** in the interface's `customCode`, not as function-typed properties.

This brief is self-contained; the docs are not available in the gen session.
