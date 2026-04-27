# MetaEngine MCP — Knowledge Brief

This summary is self-contained. The generation session that reads it will NOT have access to the original docs.

---

## Tools Exposed

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__metaengine_initialize` | Returns doc guide + linked resources. Call first for guidance. |
| `mcp__metaengine__generate_code` | **Primary tool.** Generates compilable source files from structured JSON spec. |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code` but reads the spec from a `.json` file — avoids context bloat for large specs. |
| `mcp__metaengine__generate_openapi` | Generates typed HTTP client from an OpenAPI spec (YAML/JSON or URL). |
| `mcp__metaengine__generate_graphql` | Generates typed HTTP client from a GraphQL SDL schema. |
| `mcp__metaengine__generate_protobuf` | Generates typed HTTP client from a `.proto` definition. |
| `mcp__metaengine__generate_sql` | Generates typed model classes from SQL DDL (`CREATE TABLE` statements). |

---

## generate_code — Full Input Schema

**Required:** `language`

### Top-level fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `language` | enum (required) | — | `typescript` \| `python` \| `go` \| `csharp` \| `java` \| `kotlin` \| `groovy` \| `scala` \| `swift` \| `php` \| `rust` |
| `outputPath` | string | `"."` | Directory where files are written |
| `packageName` | string | lang-specific | Package/module/namespace. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy: `com.metaengine.generated`. C#: omit for GlobalUsings pattern (no namespace declaration generated). |
| `initialize` | boolean | `false` | Initialize all properties with default values |
| `skipExisting` | boolean | `true` | Skip writing files that already exist (stub pattern) |
| `dryRun` | boolean | `false` | Preview mode — returns generated code in response without writing to disk |

### `classes[]`

Each entry produces one source file.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string (required) | Class name |
| `typeIdentifier` | string | Unique ID for cross-referencing this class from other types in the same call |
| `path` | string | Subdirectory (e.g., `"models"`, `"services/auth"`) |
| `fileName` | string | Custom file name without extension (overrides default) |
| `comment` | string | Documentation comment for the class |
| `isAbstract` | boolean | Marks class as abstract |
| `baseClassTypeIdentifier` | string | `typeIdentifier` of the base class to extend |
| `interfaceTypeIdentifiers` | string[] | Array of interface `typeIdentifier`s to implement |
| `genericArguments` | object[] | Makes this a generic class template (see below) |
| `constructorParameters` | object[] | Constructor params — **auto-become properties** in TypeScript, C#, Java, Go, Groovy (do NOT duplicate in `properties`) |
| `properties` | object[] | Field declarations with types only (see below) |
| `customCode` | object[] | Methods, initialized fields, any code with logic (see below) |
| `customImports` | object[] | External library imports (see below) |
| `decorators` | object[] | Class-level decorators (see below) |

#### `genericArguments[]` (makes a class a generic template like `Repository<T>`)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Generic param name (e.g., `"T"`) |
| `constraintTypeIdentifier` | string | typeIdentifier for constraint (`where T : BaseEntity`) |
| `propertyName` | string | Creates a property of type T with this name |
| `isArrayProperty` | boolean | If true, property is of type `T[]` |

#### `constructorParameters[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Parameter name |
| `primitiveType` | enum | `String` \| `Number` \| `Boolean` \| `Date` \| `Any` |
| `type` | string | Complex/external type as string literal |
| `typeIdentifier` | string | Reference to internal type |

#### `properties[]`

Used for type declarations ONLY — no initialization, no methods.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | enum | `String` \| `Number` \| `Boolean` \| `Date` \| `Any` |
| `type` | string | Complex type as string literal (e.g., `"Map<string, $resp>"`) |
| `typeIdentifier` | string | Reference to internal type in this batch |
| `templateRefs` | object[] | `[{placeholder, typeIdentifier}]` — required when `type` contains `$placeholders` |
| `isOptional` | boolean | Generates nullable type (e.g., `string?` in C#) |
| `isInitializer` | boolean | Add default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | object[] | templateRefs for comment text |
| `decorators` | object[] | Property-level decorators |

#### `customCode[]`

One entry = exactly one member (method, initialized field, etc.). Gets automatic newlines between blocks.

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | The code text. Use `\n` for line breaks (auto-indented). Use `$placeholder` for internal types. |
| `templateRefs` | object[] | `[{placeholder: "$user", typeIdentifier: "user"}]` — triggers import resolution for internal types |

**CRITICAL:** Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

#### `customImports[]`

For external library imports ONLY (not internal types — those use `typeIdentifier`/`templateRefs`).

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (e.g., `"@angular/core"`) or `identifier` of a `customFile` |
| `types` | string[] | Named imports (e.g., `["Injectable", "inject"]`) |

#### `decorators[]`

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Decorator text (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | object[] | templateRefs for `$placeholders` in decorator code |

---

### `interfaces[]`

Same structure as `classes` but generates interface files. Key differences:
- In TypeScript, MetaEngine **strips the `I` prefix** from interface names when generating. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control file name if collision with a class.
- Interface properties generate `{ get; }` in C# (vs `{ get; set; }` for classes).
- For interfaces that will be `implements`/`:` by a class, define method signatures in `customCode` (NOT as function-typed properties). Using function-typed properties causes implementing classes to duplicate them as property declarations.

Fields: `name`, `typeIdentifier`, `path`, `fileName`, `comment`, `properties[]`, `customCode[]`, `customImports[]`, `decorators[]`, `genericArguments[]`, `interfaceTypeIdentifiers[]` (extends other interfaces).

---

### `enums[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Cross-reference ID |
| `path` | string | Subdirectory |
| `fileName` | string | Custom file name |
| `comment` | string | Documentation comment |
| `members[]` | object[] | `[{name: string, value: number}]` |

Enum filenames auto-suffix: `.enum.ts` (TS), `OrderStatus.cs` (C#).

Language-specific idioms: Java generates `ALL_CAPS` enum names; Python generates `UPPER_CASE`; MetaEngine applies these automatically.

---

### `arrayTypes[]`

**Virtual only — no files generated.** Creates a reusable array type reference.

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference in properties |
| `elementTypeIdentifier` | string | Reference to custom element type |
| `elementPrimitiveType` | enum | `String` \| `Number` \| `Boolean` \| `Date` \| `Any` |

**C# note:** `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with `templateRefs` instead.

---

### `dictionaryTypes[]`

**Virtual only — no files generated.**

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference in properties |
| `keyPrimitiveType` | enum | Key as primitive |
| `keyTypeIdentifier` | string | Key as internal type ref |
| `keyType` | string | Key as string literal |
| `valuePrimitiveType` | enum | Value as primitive |
| `valueTypeIdentifier` | string | Value as internal type ref |

Supports all 4 combinations (primitive/custom × key/value).

---

### `concreteGenericClasses[]`

**Virtual only — no files generated.** Creates a concrete generic type like `Repository<User>`.

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID for this concrete implementation |
| `genericClassIdentifier` | string | References the generic class definition |
| `genericArguments[]` | object[] | `[{typeIdentifier?, primitiveType?}]` — the concrete type arguments |

Usage: A class uses `"baseClassTypeIdentifier": "user-repo-concrete"` to extend it. MetaEngine generates `extends Repository<User>` with correct imports.

---

### `concreteGenericInterfaces[]`

Same as `concreteGenericClasses` but for interfaces.

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID for this concrete interface |
| `genericClassIdentifier` | string | References the generic interface definition |
| `genericArguments[]` | object[] | `[{typeIdentifier?, primitiveType?}]` |

---

### `customFiles[]`

Generates files WITHOUT a class wrapper. Used for type aliases, barrel exports, utility functions.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (without extension) |
| `path` | string | Subdirectory |
| `fileName` | string | Custom file name override |
| `identifier` | string | Optional — makes this file importable by other files via `customImports` path |
| `customCode[]` | object[] | Code blocks (same structure as class `customCode`) |
| `customImports[]` | object[] | External imports |

When `identifier` is set, other types can reference it via `customImports: [{path: "<identifier>"}]` and MetaEngine resolves to the correct relative path automatically.

---

## load_spec_from_file — Input Schema

| Field | Type | Description |
|-------|------|-------------|
| `specFilePath` | string (required) | Absolute or relative path to `.json` spec file |
| `outputPath` | string | Overrides `outputPath` in spec file |
| `skipExisting` | boolean | Overrides `skipExisting` in spec file |
| `dryRun` | boolean | Overrides `dryRun` in spec file |

The spec file has the same structure as `generate_code` parameters. Use this tool when the spec is large — it avoids sending the whole JSON through the context window.

---

## generate_openapi — Key Fields

**Required:** `framework` + one of `openApiSpec` (inline YAML/JSON string) or `openApiSpecUrl`.

**`framework` options:** `angular` | `react` | `typescript-fetch` | `go-nethttp` | `java-spring` | `python-fastapi` | `csharp-httpclient` | `kotlin-ktor` | `rust-reqwest` | `swift-urlsession`

Language-specific required sub-options:
- `csharpOptions.namespaceName` (required for C#)
- `goOptions.{moduleName, packageName}` (required for Go)
- `javaSpringOptions.packageName` (required for Java)
- `kotlinOptions.packageName` (required for Kotlin)
- `rustOptions.crateName` (required for Rust)

Common optional fields: `outputPath`, `skipExisting`, `dryRun`, `documentation`, `errorHandling`, `bearerAuth`, `basicAuth`, `customHeaders[]`, `retries`, `timeout`, `optionsObjectThreshold`.

TypeScript-fetch extras: `fetchOptions.{baseUrlEnvVar, useImportMetaEnv, useMiddleware, useResultPattern, useTypesBarrel}`.

Angular extras: `angularOptions.{baseUrlToken, providedIn, useInjectFunction, useHttpResources, httpResourceTrigger, responseDateTransformation}`.

React extras: `reactOptions.{baseUrlEnvVar, useTanStackQuery, useTypesBarrel, responseDateTransformation}`.

---

## generate_graphql — Key Fields

**Required:** `framework` + `graphQLSchema` (SDL content string).

**`framework` options:** `angular` | `react` | `typescript-fetch` | `go-nethttp` | `java-spring` | `csharp-httpclient` | `kotlin-ktor` | `python-fastapi` | `rust-reqwest` | `swift-urlsession`

Same required sub-options as `generate_openapi` per language. Optional extras: `discriminatedUnions`, `documentation`. Common fields: `outputPath`, `skipExisting`, `dryRun`, `bearerAuth`, `basicAuth`, `customHeaders`, `retries`, `timeout`, `errorHandling`.

---

## generate_protobuf — Key Fields

**Required:** `framework` + `protoSource` (`.proto` content string).

**`framework` options:** `angular` | `react` | `typescript-fetch` | `go-nethttp` | `java-spring` | `csharp-httpclient` | `kotlin-ktor` | `python-httpx` | `rust-reqwest` | `swift-urlsession`

Note: Python uses `python-httpx` (not `python-fastapi`). Fetch extras: `fetchOptions.{baseUrlEnvVar, useImportMetaEnv, useTypesBarrel}`. React extras: `reactOptions.{useTanStackQuery, useTypesBarrel}`.

---

## generate_sql — Key Fields

**Required:** `language` + `ddlSource` (SQL `CREATE TABLE` statements as string).

**`language` options:** `typescript` | `csharp` | `go` | `python` | `java` | `kotlin` | `groovy` | `scala` | `swift` | `php` | `rust`

Language-specific required sub-options:
- `goOptions.moduleName` (required for Go)
- `javaOptions.packageName` (required for Java)
- `kotlinOptions.packageName` (required for Kotlin)
- `groovyOptions.packageName` (required for Groovy)
- `scalaOptions.packageName` (required for Scala)
- `phpOptions.rootNamespace` (required for PHP)
- C#: `csharpOptions.namespace`

Optional flags: `generateInterfaces`, `generateNavigationProperties` (FK relationships), `generateValidationAnnotations` (from column constraints), `initializeProperties`. Python: `pythonOptions.modelStyle` = `"dataclass"` | `"pydantic"` | `"plain"`.

---

## Critical Rules (Must Not Violate)

### 1. ONE call for all related types
`typeIdentifier` references only resolve **within the current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting across calls means cross-file imports won't resolve.

### 2. Properties = type declarations only. CustomCode = everything else.
- `properties[]` → field declarations with types. No initialization, no methods.
- `customCode[]` → methods, initialized fields, logic. One entry = one member.

### 3. templateRefs for internal types in customCode
When `customCode` references a type from the same batch, use `$placeholder` syntax + `templateRefs`. Without this, imports won't be generated.

```json
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

**In C#:** EVERY internal type reference in customCode MUST use templateRefs, or `using` directives for cross-namespace types won't be generated.

### 4. Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication.

| Language | Auto-imported (NEVER specify) |
|----------|-------------------------------|
| TypeScript | All built-in types (no imports needed at all) |
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, and more |
| Swift | Foundation (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`, etc.) |
| Rust | `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream) |
| Scala | `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### 5. templateRefs ONLY for internal types
- Internal type (in same MCP call) → `typeIdentifier` or `templateRefs`
- External library type → `customImports`
- Never mix these.

### 6. Constructor parameters auto-create properties (C#, Java, Go, Groovy)
Do NOT also list them in `properties[]` — this causes errors. Only put additional (non-constructor) fields in `properties[]`.

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references only. They NEVER produce files. Use their `typeIdentifier`/`identifier` in properties of file-generating types.

---

## TypeScript-Specific Notes

- `I` prefix stripped from interface names: `IUserRepository` → exported as `UserRepository`. Use `fileName` to avoid collisions with implementing classes (e.g., `"fileName": "i-user-repository"`).
- Primitive mappings: `String` → `string`, `Number` → `number`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- `customCode` strings with `\n` are auto-indented.
- Decorators supported directly on classes and properties.
- No imports needed for built-in types.
- Constructor parameters automatically become class properties (do not duplicate in `properties[]`).

---

## Output Structure

MetaEngine produces **compilable, correctly-imported source files** for each `classes`, `interfaces`, `enums`, and `customFiles` entry. Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) do NOT produce files — they only produce type references used by other files.

Files are written to `outputPath / (entry.path /) (entry.fileName || derived-name) . (lang-extension)`.

When `dryRun: true`, no files are written and the generated code is returned in the response for review.

When `skipExisting: true` (default), existing files are not overwritten — useful for the stub pattern.

---

## Key Patterns (TypeScript)

### Basic interfaces with cross-references
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
Produces two files with automatic imports between them.

### Class extending another class with methods
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

### Interface with method signatures (for implementing classes)
```json
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
Note: Use `customCode` (NOT function-typed properties) for method signatures on interfaces that classes will implement.

### Generic class + concrete implementation
```json
{
  "classes": [
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{"name": "T", "constraintTypeIdentifier": "base-entity",
       "propertyName": "items", "isArrayProperty": true}],
     "customCode": [
       {"code": "add(item: T): void { this.items.push(item); }"},
       {"code": "getAll(): T[] { return this.items; }"}
     ]},
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

### Array and dictionary virtual types
```json
{
  "arrayTypes": [
    {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
    {"typeIdentifier": "id-list", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
  ]
}
```
Reference via `"typeIdentifier": "user-list"` in any property.

### Complex type expression in properties
```json
{
  "properties": [{
    "name": "cache",
    "type": "Map<string, $resp>",
    "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
  }]
}
```

### Angular service with external DI
```json
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

### Enum + class that uses it
```json
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

### Custom file (type aliases / barrel exports)
```json
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

---

## Common Mistakes to Avoid

1. **Splitting related types across multiple calls.** All types that reference each other must be in ONE `generate_code` call. typeIdentifiers only resolve within the batch.

2. **Putting method signatures as function-typed properties on interfaces.** Use `customCode` for method signatures when a class will `implement` the interface. Function-typed properties cause the implementing class to duplicate them as property declarations alongside customCode methods.

3. **Writing internal type names as raw strings in customCode.** Use `templateRefs` with `$placeholder` syntax, not raw strings like `"private repo: IUserRepository"`. Raw strings won't trigger import generation.

4. **Using `arrayTypes` in C# when you need `List<T>`.** Use `"type": "List<$user>"` with templateRefs for mutable list types.

5. **Adding `System.*`, `typing.*`, `java.util.*` etc. to customImports.** MetaEngine auto-handles all framework imports — adding them manually causes duplication.

6. **Duplicating constructor parameters in `properties[]`** (C#/Java/Go/Groovy). Constructor params auto-become properties; only add extra non-constructor fields in `properties[]`.

7. **Using reserved words as property names** (`delete`, `class`, `import`). Use safe alternatives (`remove`, `clazz`, `importData`).

8. **Expecting `Number` → `double` in C#.** It maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.

9. **Forgetting `fileName` when a TypeScript `I`-prefixed interface collides with its implementing class.** Set `"fileName": "i-user-repository"` on the interface.

10. **Referencing a `typeIdentifier` that doesn't exist in the batch.** The property is silently dropped. Verify every typeIdentifier matches a defined type in the same call.

11. **templateRefs on external library types.** External types must use `customImports`. Only internal (same-batch) types use templateRefs.

12. **Expecting virtual types to produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` produce NO files — they are type references only.
