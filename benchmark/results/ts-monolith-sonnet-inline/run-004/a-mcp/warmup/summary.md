# MetaEngine MCP — Knowledge Brief

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

### `mcp__metaengine__metaengine_initialize`
- **Purpose**: Returns essential MetaEngine patterns and documentation resources. Call when you need guidance or are generating code for the first time.
- **Parameters**:
  - `language` (optional, enum): `typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php` — returns language-specific patterns when specified.

### `mcp__metaengine__generate_code`
- **Purpose**: Semantic code generation — the primary tool. Generates compilable source files with perfect imports and cross-references from structured JSON specs.
- **Required**: `language`
- **All parameters**: see full schema section below.

### `mcp__metaengine__generate_openapi`, `mcp__metaengine__generate_graphql`, `mcp__metaengine__generate_protobuf`, `mcp__metaengine__generate_sql`
- Spec-to-code converters (not the focus here; they operate on external spec files).

### `mcp__metaengine__load_spec_from_file`
- Loads an OpenAPI/GraphQL/Protobuf/SQL spec from a local file for conversion.

---

## `generate_code` — Full Input Schema

### Top-Level Fields

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `language` | enum | **YES** | — | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | no | `"."` | Directory where files are written |
| `packageName` | string | no | lang-defaults | Package/module/namespace name. Go defaults `github.com/metaengine/demo`, Java/Kotlin/Groovy default `com.metaengine.generated`. C#: omit for GlobalUsings pattern (no namespace declaration). |
| `initialize` | boolean | no | `false` | Initialize properties with default values |
| `dryRun` | boolean | no | `false` | Preview mode — returns generated code without writing to disk |
| `skipExisting` | boolean | no | `true` | Skip writing files that already exist (stub pattern) |
| `classes` | array | no | — | Class definitions (regular and generic class templates) |
| `interfaces` | array | no | — | Interface definitions |
| `enums` | array | no | — | Enum definitions |
| `arrayTypes` | array | no | — | Array type virtual references (NO files generated) |
| `dictionaryTypes` | array | no | — | Dictionary type virtual references (NO files generated) |
| `concreteGenericClasses` | array | no | — | Concrete generic class references like `Repository<User>` (NO files generated) |
| `concreteGenericInterfaces` | array | no | — | Concrete generic interface references (NO files generated) |
| `customFiles` | array | no | — | Utility files, type aliases, barrel exports — generated WITHOUT class wrapper |

---

### `classes[]` — Class Definition Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Class name |
| `typeIdentifier` | string | Unique identifier for referencing this class from other types in the batch |
| `path` | string | Directory path (e.g., `"models"`, `"services/auth"`) |
| `fileName` | string | Custom file name without extension |
| `comment` | string | Documentation comment for the class |
| `isAbstract` | boolean | Whether this is an abstract class |
| `baseClassTypeIdentifier` | string | typeIdentifier of the base class to extend |
| `interfaceTypeIdentifiers` | string[] | Array of interface typeIdentifiers to implement |
| `genericArguments` | array | Generic parameters — makes this a generic class template like `Repository<T>` |
| `constructorParameters` | array | Constructor parameters (auto-become properties; do NOT duplicate in `properties[]`) |
| `properties` | array | Class properties — type declarations only, no logic |
| `customCode` | array | Custom code blocks — one per method or initialized field |
| `customImports` | array | External library imports only |
| `decorators` | array | Class-level decorators (e.g., `@Injectable(...)`) |

#### `classes[].genericArguments[]`

| Field | Type | Description |
|---|---|---|
| `name` | string | Generic parameter name (e.g., `"T"`, `"K"`) |
| `constraintTypeIdentifier` | string | typeIdentifier for the generic constraint (`where T : BaseEntity`) |
| `propertyName` | string | Creates a property with this name of type T |
| `isArrayProperty` | boolean | If true, creates property of type T[] |

#### `classes[].constructorParameters[]`

| Field | Type | Description |
|---|---|---|
| `name` | string | Parameter name |
| `primitiveType` | enum | `String | Number | Boolean | Date | Any` |
| `type` | string | For complex or external types |
| `typeIdentifier` | string | Reference to another type in the batch |

#### `classes[].properties[]`

| Field | Type | Description |
|---|---|---|
| `name` | string | Property name |
| `primitiveType` | enum | `String | Number | Boolean | Date | Any` |
| `type` | string | Complex type expression (e.g., `"Map<string, $resp>"`) |
| `typeIdentifier` | string | Reference to another type in the batch |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — resolves `$placeholder` to type name + triggers import |
| `isOptional` | boolean | Generates nullable type (e.g., `string?` in C#) |
| `isInitializer` | boolean | Add default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | array | templateRefs for comment text |
| `decorators` | array | Property-level decorators (e.g., `@IsEmail()`) |

#### `classes[].customCode[]`

| Field | Type | Description |
|---|---|---|
| `code` | string | One method or initialized field. Use `\n` for multi-line (auto-indented). |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — resolves `$placeholder` in `code` + triggers import |

#### `classes[].customImports[]`

| Field | Type | Description |
|---|---|---|
| `path` | string | Import path (e.g., `"@angular/core"`, `"rxjs"`) |
| `types` | string[] | Named types to import from path |

#### `classes[].decorators[]`

| Field | Type | Description |
|---|---|---|
| `code` | string | Decorator expression (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | array | templateRefs for the decorator code |

---

### `interfaces[]` — Interface Definition Fields

Same structure as `classes[]` except:
- No `isAbstract`, no `baseClassTypeIdentifier`, no `constructorParameters`
- Has `interfaceTypeIdentifiers` for extending other interfaces
- In TypeScript: MetaEngine **strips the `I` prefix** from exported names. `IUserRepository` → exported as `UserRepository`. Use `fileName` to avoid file name collisions.
- In C#: `I` prefix is preserved.
- Interface properties generate `{ get; }` in C#. Class properties generate `{ get; set; }`.
- **Method signatures on interfaces**: put in `customCode`, NOT as function-typed properties, or implementing classes will duplicate them as property declarations.

---

### `enums[]` — Enum Definition Fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Enum name |
| `typeIdentifier` | string | Unique identifier for referencing this enum |
| `path` | string | Directory path |
| `fileName` | string | Custom file name without extension |
| `comment` | string | Documentation comment |
| `members` | array | `[{name: string, value: number}]` |

**File naming**: Enums auto-suffix filenames — `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).
**Language idioms**: Java generates `ALL_CAPS` enum member names automatically.

---

### `arrayTypes[]` — Virtual Array Type References (NO files generated)

| Field | Type | Description |
|---|---|---|
| `typeIdentifier` | string | **Required.** Identifier to reference this array type elsewhere |
| `elementTypeIdentifier` | string | Reference to a custom type in the batch |
| `elementPrimitiveType` | enum | `String | Number | Boolean | Date | Any` |

**Usage**: reference via `"typeIdentifier": "user-list"` in class/interface properties.
**TypeScript output**: `Array<T>` / `new Array<T>()`
**C# note**: generates `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs instead.

---

### `dictionaryTypes[]` — Virtual Dictionary Type References (NO files generated)

| Field | Type | Description |
|---|---|---|
| `typeIdentifier` | string | **Required.** Identifier to reference this dictionary type |
| `keyPrimitiveType` | enum | `String | Number | Boolean | Date | Any` |
| `keyTypeIdentifier` | string | Reference to custom key type |
| `keyType` | string | String literal for key type |
| `valuePrimitiveType` | enum | `String | Number | Boolean | Date | Any` |
| `valueTypeIdentifier` | string | Reference to custom value type |

Supports all 4 key/value combinations: primitive/primitive, primitive/custom, custom/primitive, custom/custom.
**TypeScript output**: `Record<K, V>` initialized to `{}`.

---

### `concreteGenericClasses[]` — Concrete Generic Class References (NO files generated)

| Field | Type | Description |
|---|---|---|
| `identifier` | string | Identifier for this concrete implementation |
| `genericClassIdentifier` | string | References the generic class definition |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` |

Creates a virtual `Repository<User>` type reference. Reference via `typeIdentifier` (e.g., as `baseClassTypeIdentifier` on a class, or via `templateRefs` in customCode).
**Output**: MetaEngine generates `extends Repository<User>` with correct imports automatically.

---

### `concreteGenericInterfaces[]` — Concrete Generic Interface References (NO files generated)

Same structure as `concreteGenericClasses[]` but for interfaces.

| Field | Type | Description |
|---|---|---|
| `identifier` | string | Identifier for this concrete implementation |
| `genericClassIdentifier` | string | References the generic interface definition |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` |

---

### `customFiles[]` — Custom Files (type aliases, barrel exports, utilities)

Generates files **WITHOUT** a class wrapper — raw code blocks only.

| Field | Type | Description |
|---|---|---|
| `name` | string | File name (without extension) |
| `path` | string | Directory path |
| `fileName` | string | Custom file name without extension |
| `identifier` | string | Optional — enables other files to import this via customImports path resolution |
| `customCode` | array | `[{code, templateRefs}]` — one per export/type alias/function |
| `customImports` | array | External imports for this file |

**Import resolution**: when `identifier` is set, other files can use `{path: "<identifier>"}` in their `customImports` and MetaEngine resolves the relative path automatically.

---

## Critical Rules (Must Not Violate)

### Rule 1 — ONE call for all related types
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both MUST be in the same `generate_code` call. Cross-call references silently drop the property.

### Rule 2 — properties[] = type declarations only; customCode[] = everything else
- `properties[]`: field declarations with types only. No initialization, no logic.
- `customCode[]`: methods, initialized fields, any code with logic. **One item = exactly one member.**
- Never put methods in `properties[]`. Never put uninitialized type declarations in `customCode[]`.

### Rule 3 — templateRefs for internal types in customCode and complex type expressions
When `customCode` or a `type` string references a type from the same batch, use `$placeholder` syntax with `templateRefs`. This is what triggers automatic import resolution.
```jsonc
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```
**C# critical**: Every internal type reference in customCode MUST use templateRefs or `using` directives won't be generated → compile-fail across namespaces.

### Rule 4 — Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors. Only use `customImports` for external libraries.

| Language | Auto-imported (never specify in customImports) |
|---|---|
| TypeScript | (no imports needed — built-in types are automatic) |
| C# | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.) |
| Rust | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream) |
| Scala | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |

### Rule 5 — templateRefs are ONLY for internal types
- Internal batch type → use `typeIdentifier` in properties, or `templateRefs` in customCode
- External library type → use `customImports`
- Never mix these.

### Rule 6 — Constructor parameters auto-create properties (C#, Java, Go, Groovy)
In these languages, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]`. Only put additional non-constructor properties in `properties[]`.
```jsonc
// WRONG: causes "Sequence contains more than one matching element"
"constructorParameters": [{"name": "email", "type": "string"}],
"properties": [{"name": "email", "type": "string"}]  // DUPLICATE!

// CORRECT:
"constructorParameters": [{"name": "email", "type": "string"}]
"properties": [{"name": "createdAt", "primitiveType": "Date"}]  // only ADDITIONAL fields
```
**Note**: In TypeScript, `constructorParameters` also auto-become `public` properties via constructor shorthand.

### Rule 7 — Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references ONLY. No files are emitted. Use them by referencing their `typeIdentifier` in properties of file-generating types.

---

## TypeScript-Specific Notes

- MetaEngine **strips `I` prefix** from interface exported names: `IUserRepository` → exported class name `UserRepository`. Use `fileName: "i-user-repository"` to control file name and avoid collisions.
- Primitive type mappings: `String` → `string`, `Number` → `number`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for `\n` in customCode strings.
- Decorators supported directly on classes and properties.
- TypeScript has NO auto-imports — all built-in types are available without any import.
- `arrayTypes` generate `Array<T>` / `new Array<T>()` (with `initialize: true`).
- `dictionaryTypes` generate `Record<K, V>` initialized to `{}`.
- Constructor parameters become `public` constructor shorthand.
- Interface method signatures → use `customCode`, not function-typed `properties`.
- `initialize: true` fills in default values (`''` for string, `0` for number, `false` for bool, `new Date()` for Date, `new Array<T>()` for arrays, `{}` for records).
- Without `initialize`, properties use `!` non-null assertion: `email!: string`.

---

## Output Structure

For each file-generating type (class, interface, enum, customFile), MetaEngine produces:
- One source file per type (following the path and fileName fields)
- Correct import/using/require statements based on cross-references
- Language-idiomatic code (Java ALL_CAPS enums, Python snake_case, etc.)

The tool response contains the list of generated file paths (and file contents when `dryRun: true`).

---

## Complete Working Examples

### Example A — Basic interfaces with cross-references (TypeScript)

```json
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

Output: `address.ts` and `user.ts` with automatic import of Address in user.ts.

---

### Example B — Class with inheritance and methods

```json
{
  "language": "typescript",
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

---

### Example C — Enum + class using it

```json
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

---

### Example D — Array and dictionary virtual types

```json
{
  "language": "typescript",
  "classes": [
    {"name": "User", "typeIdentifier": "user", "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Metadata", "typeIdentifier": "metadata", "properties": [{"name": "value", "primitiveType": "Any"}]}
  ],
  "arrayTypes": [
    {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
    {"typeIdentifier": "user-meta", "keyTypeIdentifier": "user", "valueTypeIdentifier": "metadata"}
  ],
  "classes": [{"name": "DataStore", "typeIdentifier": "store",
    "properties": [
      {"name": "users", "typeIdentifier": "user-list"},
      {"name": "tags", "typeIdentifier": "string-array"},
      {"name": "scores", "typeIdentifier": "scores"},
      {"name": "byId", "typeIdentifier": "user-lookup"}
    ]}]
}
```

Output: `Record<string, number>`, `Record<string, User>`, `Array<User>`, `Array<string>` — all with correct imports.

---

### Example E — Generic repository pattern + concreteGenericClasses

```json
{
  "language": "typescript",
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{"name": "T", "constraintTypeIdentifier": "base-entity",
       "propertyName": "items", "isArrayProperty": true}],
     "customCode": [
       {"code": "add(item: T): void { this.items.push(item); }"},
       {"code": "getAll(): T[] { return this.items; }"},
       {"code": "findById(id: string): T | undefined { return this.items.find(i => i.id === id); }"}
     ]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}]},
    {"name": "UserController", "typeIdentifier": "controller",
     "customCode": [{
       "code": "private repo: $userRepo = new Repository<User>();",
       "templateRefs": [{"placeholder": "$userRepo", "typeIdentifier": "user-repository"}]
     }]}
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repository",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{"typeIdentifier": "user"}]
  }]
}
```

Output: 4 files — `base-entity.ts`, `repository.ts`, `user.ts`, `user-controller.ts` — all with correct `extends`/`import` wiring.

---

### Example F — Service with external DI + templateRefs in customCode

```json
{
  "language": "typescript",
  "classes": [
    {"name": "Pet", "typeIdentifier": "pet", "properties": [{"name": "name", "primitiveType": "String"}]}
  ],
  "arrayTypes": [{"typeIdentifier": "pet-array", "elementTypeIdentifier": "pet"}],
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
       "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]},
      {"code": "create(pet: $pet): Observable<$pet> { return this.http.post<$pet>(this.baseUrl, pet); }",
       "templateRefs": [{"placeholder": "$pet", "typeIdentifier": "pet"}]}
    ]
  }]
}
```

---

### Example G — Interface with method signatures (correct pattern)

```json
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
  "classes": [{"name": "User", "typeIdentifier": "user",
    "properties": [{"name": "id", "primitiveType": "String"}]}]
}
```

Note `fileName: "i-user-repository"` prevents collision since TypeScript strips the `I` prefix from the export name.

---

### Example H — Constructor parameters (correct pattern for TypeScript)

```json
{
  "language": "typescript",
  "enums": [{"name": "Status", "typeIdentifier": "status",
    "members": [{"name": "Active", "value": 1}]}],
  "classes": [{"name": "User", "typeIdentifier": "user",
    "constructorParameters": [
      {"name": "email", "type": "string"},
      {"name": "status", "typeIdentifier": "status"}
    ],
    "properties": [
      {"name": "createdAt", "primitiveType": "Date"}
    ]
  }]
}
```

Output:
```typescript
import { Status } from './status.enum';
export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

---

### Example I — customFiles for type aliases

```json
{
  "language": "typescript",
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
    "customImports": [{"path": "shared-types", "types": ["UserId", "Email"]}],
    "customCode": [{"code": "static format(email: Email): string { return email.trim(); }"}]
  }]
}
```

The `identifier: "shared-types"` allows other files to import via the identifier; MetaEngine resolves the relative path automatically.

---

### Example J — Complex type expression with templateRefs in properties

```json
{
  "language": "typescript",
  "classes": [
    {"name": "ApiResponse", "typeIdentifier": "api-response",
     "properties": [{"name": "data", "primitiveType": "Any"}]},
    {"name": "Cache", "typeIdentifier": "cache",
     "properties": [{
       "name": "store",
       "type": "Map<string, $resp>",
       "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
     }]}
  ]
}
```

templateRefs work in `properties[].type` strings too, not just in customCode.

---

## Common Mistakes — Quick Reference

| ❌ Wrong | ✅ Correct |
|---|---|
| Reference a typeIdentifier not in this batch | Every referenced typeIdentifier must be defined in the same call |
| Interface method signatures as function-typed properties | Put method signatures in `customCode` for interfaces |
| Internal type names as raw strings in customCode | Use `templateRefs` with `$placeholder` for internal types in customCode |
| `arrayTypes` in C# when you need `List<T>` | Use `"type": "List<$user>"` with templateRefs |
| Add `System.*`, `typing.*`, `java.util.*` to customImports | Let MetaEngine auto-import those; only add external libs |
| Duplicate constructor params in `properties[]` (C#/Java/Go/Groovy) | Only put ADDITIONAL non-constructor properties in `properties[]` |
| Reserved words as property names (`delete`, `class`, `import`) | Use safe alternatives (`remove`, `clazz`, `importData`) |
| Generate related types in separate MCP calls | Batch everything in ONE call |
| Expect `Number` → `double` in C# | Use `"type": "double"` or `"type": "decimal"` explicitly |
| `IFoo` interface and its class generate colliding filenames in TS | Set `"fileName": "i-foo"` on the interface |
| Putting multiple methods/members in a single customCode item | One item = one method/member |

---

## Key Mental Model

MetaEngine operates on a **type graph within a single call**:
1. All types with `typeIdentifier` become nodes.
2. All `typeIdentifier` references in properties, `baseClassTypeIdentifier`, `interfaceTypeIdentifiers`, `templateRefs`, `constructorParameters`, `genericArguments.constraintTypeIdentifier`, and virtual type definitions become edges.
3. MetaEngine walks the graph to determine imports and generates all files in one shot.

**If a node is missing from the graph (not in the call), references to it are silently dropped.**

This is why the cardinal rule is: **ONE call with ALL related types.**
