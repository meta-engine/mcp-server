# MetaEngine MCP — Knowledge Brief (self-contained)

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as one structured JSON spec; MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. It resolves cross-references, manages imports, and applies language idioms automatically. **One well-formed JSON call replaces dozens of file writes.**

---

## Tools exposed

- **`mcp__metaengine__metaengine_initialize`** — Returns the AI Code Generation Guide (this brief was built from it). Optional input: `language` (one of typescript/python/go/csharp/java/kotlin/groovy/scala/swift/php).
- **`mcp__metaengine__generate_code`** — The main code generator. Takes a structured JSON spec; writes files (or returns previews when `dryRun: true`). Schema documented in full below.
- **`mcp__metaengine__load_spec_from_file`** — Same as `generate_code`, but loads the spec from a `.json` file path. Useful for large specs to avoid context bloat. Inputs: `specFilePath` (required), optional overrides for `outputPath`, `skipExisting`, `dryRun`.
- **`mcp__metaengine__generate_openapi`**, **`generate_graphql`**, **`generate_protobuf`**, **`generate_sql`** — Format-specific entry points (not detailed here; same spec philosophy).

Linked resources from `metaengine_initialize`:
- `metaengine://guide/ai-assistant` — Critical rules, patterns, language notes, common mistakes.
- `metaengine://guide/examples` — Real-world spec→output examples.

---

## CRITICAL RULES (read before generating)

### 1. Generate ALL related types in ONE call
`typeIdentifier` references resolve **only within the current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks the typegraph; cross-file imports won't resolve.

### 2. `properties[]` = type declarations. `customCode[]` = everything else.
- `properties[]` = field declarations with types only (no logic, no init).
- `customCode[]` = methods, initialized fields, decorators-with-logic. **One `customCode` item = exactly one member.**
- Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

### 3. Use `templateRefs` for internal types in customCode
When `customCode` references a generated type, use `$placeholder` syntax with `templateRefs`. This triggers automatic import resolution. Without it, no import/using directive is generated.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**C# is strict**: every internal type reference in `customCode` MUST use `templateRefs`, or `using` directives won't be generated → cross-namespace compile fail.

### 4. NEVER add framework imports to `customImports`
MetaEngine auto-imports standard library types. Adding them manually causes duplication/errors.

| Language   | Auto-imported (DO NOT specify)                                                                  |
|------------|--------------------------------------------------------------------------------------------------|
| C#         | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*    |
| Python     | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses                 |
| Java       | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*       |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*                                |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more  |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)                |
| Rust       | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde                           |
| Groovy     | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream)      |
| Scala      | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.*         |
| PHP        | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable              |
| TypeScript | (no imports needed — built-in types)                                                             |

Use `customImports` ONLY for external libraries (`@angular/core`, `rxjs`, `FluentValidation`, etc.).

### 5. `templateRefs` are ONLY for internal (in-batch) types
External library types must use `customImports`. Same call → `typeIdentifier` / `templateRefs`. External library → `customImports`. Never mix.

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Do NOT duplicate constructor params in `properties[]` — causes "Sequence contains more than one matching element" error. Put shared fields ONLY in `constructorParameters`; only put non-constructor extras in `properties[]`. (TypeScript also auto-promotes constructor params with `public` modifier.)

### 7. Virtual types do NOT generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references only. They never produce files; they're meant to be referenced via `typeIdentifier` from properties of file-generating types.

### 8. Reserved words break property names
Avoid `delete`, `class`, `import`, etc. as property names. Use `remove`, `clazz`, `importData`.

---

## `generate_code` — full input schema

Top-level keys (only `language` is required):

| Key                          | Type     | Notes |
|------------------------------|----------|-------|
| `language`                   | enum     | **Required.** one of: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath`                 | string   | Output directory. Defaults to `.` |
| `packageName`                | string   | Namespace/package/module. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy default: `com.metaengine.generated`. C#: omit/empty → no namespace declaration (good for GlobalUsings). |
| `initialize`                 | bool     | Default `false`. If true, properties get default-value initialization. |
| `skipExisting`               | bool     | Default `true`. If true, existing files aren't overwritten (stub pattern). |
| `dryRun`                     | bool     | Default `false`. If true, returns generated file contents in response, doesn't write. |
| `classes`                    | object[] | Class definitions (regular and generic templates). |
| `interfaces`                 | object[] | Interface definitions (regular and generic templates). |
| `enums`                      | object[] | Enum definitions. |
| `arrayTypes`                 | object[] | Reusable array type references (NO files generated). |
| `dictionaryTypes`            | object[] | Reusable map/dict type references (NO files generated). All 4 prim/custom key/value combos supported. |
| `concreteGenericClasses`     | object[] | Concrete generic class instances like `Repository<User>` (NO files generated). |
| `concreteGenericInterfaces`  | object[] | Concrete generic interface instances like `IRepository<User>` (NO files generated). |
| `customFiles`                | object[] | Files without a class wrapper (type aliases, barrel exports, free functions). |

### `classes[]` item

| Field                       | Type     | Notes |
|-----------------------------|----------|-------|
| `name`                      | string   | Class name. |
| `typeIdentifier`            | string   | Unique identifier for cross-references. |
| `path`                      | string   | Subdirectory (e.g., `models`, `services/auth`). |
| `fileName`                  | string   | Override file name (without extension). |
| `comment`                   | string   | Class-level doc comment. |
| `isAbstract`                | bool     | Marks class abstract. |
| `baseClassTypeIdentifier`   | string   | Type identifier of base class to extend. |
| `interfaceTypeIdentifiers`  | string[] | Interface identifiers to implement. |
| `genericArguments`          | object[] | Makes this a generic template. Each: `{ name, constraintTypeIdentifier?, propertyName?, isArrayProperty? }`. `propertyName`+`isArrayProperty` auto-creates a property of type `T`/`T[]`. |
| `constructorParameters`     | object[] | Each: `{ name, primitiveType? \| type? \| typeIdentifier? }`. Auto-create properties in C#/Java/Go/Groovy/TS — don't duplicate. |
| `properties`                | object[] | See properties schema below. |
| `customCode`                | object[] | Each: `{ code: string, templateRefs?: [{placeholder, typeIdentifier}] }`. ONE method/init-field per item. |
| `customImports`             | object[] | Each: `{ path: string, types?: string[] }`. External libs only. |
| `decorators`                | object[] | Each: `{ code, templateRefs? }`. Class-level decorators. |

### `properties[]` item

| Field                | Type     | Notes |
|----------------------|----------|-------|
| `name`               | string   | Property name. |
| `primitiveType`      | enum     | `String`, `Number`, `Boolean`, `Date`, `Any`. |
| `typeIdentifier`     | string   | Reference to another generated type. |
| `type`               | string   | Raw type expression for complex/external types (use with `templateRefs` for `$placeholder` substitution). |
| `isOptional`         | bool     | Generates nullable type (e.g., `string?` in C#, `string \| undefined` in TS). |
| `isInitializer`      | bool     | Adds default value initialization. |
| `comment`            | string   | Doc comment. |
| `commentTemplateRefs`| object[] | Template refs inside the comment. |
| `decorators`         | object[] | Property-level decorators (e.g., `@IsEmail()`, `@Required()`). |
| `templateRefs`       | object[] | `[{placeholder, typeIdentifier}]` — substitutes `$placeholder` in `type` string. |

### `interfaces[]` item
Same shape as `classes[]` but no `constructorParameters`, no `baseClassTypeIdentifier` (use `interfaceTypeIdentifiers` to extend other interfaces). For methods that an implementing class will provide, put method **signatures** in `customCode` (NOT as function-typed properties — see Common Mistake #2).

### `enums[]` item

| Field            | Type | Notes |
|------------------|------|-------|
| `name`           | string | Enum name. |
| `typeIdentifier` | string | Cross-ref id. |
| `path`           | string | Subdir. |
| `fileName`       | string | File name override. |
| `comment`        | string | Doc comment. |
| `members`        | object[] | Each: `{ name, value: number }`. |

Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### `arrayTypes[]` item

| Field                    | Type   | Notes |
|--------------------------|--------|-------|
| `typeIdentifier`         | string | **Required.** Reference id. |
| `elementPrimitiveType`   | enum   | `String` / `Number` / `Boolean` / `Date` / `Any`. |
| `elementTypeIdentifier`  | string | Reference to a generated type. |

Use one of `elementPrimitiveType` or `elementTypeIdentifier`.
**C# note**: `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use a property `type` of `"List<$user>"` with `templateRefs` instead.

### `dictionaryTypes[]` item

| Field                    | Type   | Notes |
|--------------------------|--------|-------|
| `typeIdentifier`         | string | **Required.** |
| `keyPrimitiveType`       | enum   | Primitive key. |
| `keyType`                | string | Raw string key type (e.g., `"string"`). |
| `keyTypeIdentifier`      | string | Generated-type key. |
| `valuePrimitiveType`     | enum   | Primitive value. |
| `valueTypeIdentifier`    | string | Generated-type value. |

All 4 combinations of primitive/custom for key/value supported.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` item

| Field                      | Type     | Notes |
|----------------------------|----------|-------|
| `identifier`               | string   | New ref id for this concrete instance. |
| `genericClassIdentifier`   | string   | Refers to the generic class/interface template. |
| `genericArguments`         | object[] | Each: `{ typeIdentifier? \| primitiveType? }`. |

Used to refer to inline types like `Repository<User>` from properties or `baseClassTypeIdentifier`. Generates no file itself.

### `customFiles[]` item

| Field            | Type     | Notes |
|------------------|----------|-------|
| `name`           | string   | File name (no extension). |
| `path`           | string   | Subdir. |
| `fileName`       | string   | Override file name. |
| `identifier`     | string   | Optional — lets other files reference via `customImports.path: "<identifier>"` for auto-relative resolution. |
| `customCode`     | object[] | One export/alias/function per item. |
| `customImports`  | object[] | External imports. |

### `genericArguments[]` (for class/interface)

| Field                       | Type    | Notes |
|-----------------------------|---------|-------|
| `name`                      | string  | Generic param name (`T`, `K`). |
| `constraintTypeIdentifier`  | string  | Constraint (e.g., `where T : BaseEntity`). |
| `propertyName`              | string  | Auto-creates property of type `T` with this name. |
| `isArrayProperty`           | bool    | If true, property is `T[]`. |

### `customImports[]` item
`{ path: string, types?: string[] }`. `path` is the import source (npm package / module / namespace, or a `customFile.identifier`). `types` lists named imports.

### `customCode[]` item
`{ code: string, templateRefs?: [{placeholder: string, typeIdentifier: string}] }`. Each item is exactly ONE method or initialized field. Newlines between items are added automatically.

### `decorators[]` item
`{ code: string, templateRefs?: [{placeholder, typeIdentifier}] }`.

---

## Pattern reference (canonical examples)

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

### Generic class + concrete implementation via `concreteGenericClasses`
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

### Complex type expression with templateRefs
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

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

### Service with external DI (NestJS/Angular style)
```jsonc
{
  "classes": [{
    "name": "ApiService", "typeIdentifier": "api-service",
    "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
    "customImports": [
      {"path": "@angular/core", "types": ["Injectable", "inject"]},
      {"path": "@angular/common/http", "types": ["HttpClient"]}
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

### customFiles for type aliases / barrels
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
The `identifier` lets `customImports.path` resolve to a relative path automatically.

### Interface method signatures (TS/C#)
For interfaces a class will `implements`, declare method signatures in `customCode`, **NOT** as function-typed properties:
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
If you use function-typed properties, the implementing class will duplicate them as property declarations alongside your customCode methods.

### Constructor parameters — CORRECT vs WRONG (C#/Java/Go/Groovy)
WRONG (causes "Sequence contains more than one matching element"):
```jsonc
{"constructorParameters": [{"name": "email", "type": "string"}],
 "properties": [{"name": "email", "type": "string"}]}  // duplicate!
```
CORRECT:
```jsonc
{"constructorParameters": [{"name": "email", "type": "string"}],
 "properties": [{"name": "createdAt", "primitiveType": "Date"}]}  // only extras
```

---

## Output structure

- Each class/interface/enum becomes one source file in the appropriate language. File names follow language convention (`UserService.cs`, `user-service.ts`, `user_service.py`, etc.).
- `path` on a class places it under that subdirectory inside `outputPath`.
- Cross-references between in-batch types produce correct relative imports (TS), `using` directives (C#), `import` statements (Java/Python/Go/Kotlin), etc.
- Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) materialize inline at use sites; no files produced.
- `customFiles` produce raw files without a class wrapper.
- With `dryRun: true`, file contents are returned in the tool response; no disk writes.
- With `skipExisting: true` (default), files that already exist are not overwritten.

### Generated example outputs (sanity check)

For the basic interfaces example (TS):
```typescript
// address.ts
export interface Address { street: string; city: string; }
// user.ts
import { Address } from './address';
export interface User { id: string; address: Address; }
```

For the NestJS service example:
```typescript
// services/pet-service.ts
import { Injectable, inject } from '@nestjs/common';
import { HttpClient } from '@nestjs/common/http';
import { Observable } from 'rxjs';
import { Pet } from '../pet';

@Injectable({ providedIn: 'root' })
export class PetService {
  private http = inject(HttpClient);
  private baseUrl = '/api/pets';
  getAll(): Observable<Array<Pet>> { return this.http.get<Array<Pet>>(this.baseUrl); }
  getById(id: string): Observable<Pet> { return this.http.get<Pet>(`${this.baseUrl}/${id}`); }
  create(pet: Pet): Observable<Pet> { return this.http.post<Pet>(this.baseUrl, pet); }
}
```

For the dictionary-types example, all 4 key/value combos render to TS `Record<K,V>`.

---

## Language-specific notes

### TypeScript
- MetaEngine **strips `I` prefix** from interface names: `IUserRepository` exports as `UserRepository`. Use `fileName` (e.g., `"i-user-repository"`) to avoid file-name collisions when both the interface and an implementing class would share a name.
- Primitive maps: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- Auto-indents `customCode` newlines (`\n`).
- Decorators supported directly.
- Constructor params with `public` modifier auto-promote to properties.

### C#
- `I` prefix is **preserved** on interface names.
- `Number` → `int` (NOT `double`). For non-integer numbers, use `"type": "decimal"` or `"type": "double"` explicitly.
- `packageName` sets the namespace. Omit for GlobalUsings pattern.
- Interface properties → `{ get; }`; class properties → `{ get; set; }`.
- `arrayTypes` → `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with `templateRefs`.
- `isOptional` on a property generates nullable reference type (`string?`).
- Every internal type ref in `customCode` MUST use `templateRefs` (otherwise no `using` directive).

### Python
- Must provide explicit indentation (4 spaces) after `\n` in `customCode`.
- `typing.*`, pydantic, datetime, decimal, enum, abc, dataclasses are auto-imported.
- Method names will be transformed to `snake_case` idiomatically.

### Go
- Requires `packageName` for multi-file projects (default `github.com/metaengine/demo`).
- No constructors — use factory functions in `customCode`.
- Constructor parameters auto-create struct fields like other languages.

### Java / Kotlin / Groovy / Scala
- Default `packageName` is `com.metaengine.generated`.
- Java: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` auto-imported. Java enums use `ALL_CAPS` member names idiomatically.
- Kotlin: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` auto-imported.
- Groovy/Scala: see auto-import table above.

### Swift / PHP / Rust
- Swift: Foundation auto-imported.
- PHP: DateTime/Exception/JsonSerializable/Stringable etc. auto-imported.
- Rust: `std::collections`, `chrono`, `uuid`, `rust_decimal`, `serde` auto-imported.

---

## Common mistakes (anti-patterns)

1. Don't reference a `typeIdentifier` that doesn't exist in the batch → property is silently dropped. Verify every id matches.
2. Don't put method signatures as function-typed properties on interfaces a class will `implements`. Use `customCode` for method signatures.
3. Don't write internal type names as raw strings in `customCode` (e.g., `"private repo: IUserRepository"`). Use templateRefs.
4. Don't use `arrayTypes` in C# when you need `List<T>`. Use `"type": "List<$user>"` with templateRefs.
5. Don't add `System.*`, `typing.*`, `java.util.*` etc. to `customImports`.
6. Don't duplicate constructor parameter names in `properties[]` (C#/Java/Go/Groovy).
7. Don't use reserved words (`delete`, `class`, `import`) as property names.
8. Don't generate related types in separate MCP calls — cross-file imports only resolve inside one batch.
9. Don't expect `Number` → `double` in C#; it's `int`.
10. Don't forget `fileName` when an `I`-prefixed interface and its implementing class would collide in TypeScript.

---

## Quick mental model for one-call generation

1. Enumerate every type the spec needs (DTOs, enums, helpers, services).
2. Assign each a unique `typeIdentifier`.
3. Decide: file-generating (classes/interfaces/enums/customFiles) vs virtual (arrayTypes/dictionaryTypes/concreteGenericClasses/concreteGenericInterfaces).
4. Put plain field declarations in `properties[]`. Put any code with logic, init, or method body in `customCode[]` (one item per member).
5. For any internal type referenced inside a string in `customCode`, `type`, or `decorators` → use `$placeholder` + `templateRefs`.
6. For external libs only → use `customImports`.
7. Constructor params: place ONLY in `constructorParameters` (no duplication in `properties[]`).
8. Set `language`, optional `packageName`, `outputPath`, `dryRun`, `skipExisting`.
9. Submit one `generate_code` (or `load_spec_from_file`) call. Do not split.
