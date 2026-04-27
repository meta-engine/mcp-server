# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike raw file writes, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns essential patterns and linked resources. Call when uncertain or generating for the first time. |
| `mcp__metaengine__generate_code` | **Primary tool.** Generates compilable source files from structured JSON spec. |
| `mcp__metaengine__load_spec_from_file` | Like `generate_code` but reads spec from a `.json` file — avoids context bloat for large specs. |
| `mcp__metaengine__generate_openapi` | Generates fully typed HTTP clients from OpenAPI specs (inline YAML/JSON or URL). |
| `mcp__metaengine__generate_graphql` | Generates fully typed HTTP clients from GraphQL SDL schemas. |
| `mcp__metaengine__generate_protobuf` | Generates fully typed HTTP clients from `.proto` definitions. |
| `mcp__metaengine__generate_sql` | Generates typed model classes from SQL DDL (`CREATE TABLE` statements). |

---

## `generate_code` — Full Input Schema

### Top-level fields

| Field | Type | Default | Notes |
|---|---|---|---|
| `language` | enum (required) | — | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | `"."` | Directory where files are written |
| `packageName` | string | language-default | Package / namespace / module name. C#: omit for GlobalUsings pattern. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy default: `com.metaengine.generated`. |
| `initialize` | boolean | `false` | Initialize properties with default values |
| `dryRun` | boolean | `false` | Preview mode — returns code without writing files |
| `skipExisting` | boolean | `true` | Skip writing files that already exist (stub pattern) |
| `interfaces` | array | — | Interface definitions |
| `classes` | array | — | Class definitions (regular and generic templates) |
| `enums` | array | — | Enum definitions |
| `customFiles` | array | — | Files without class wrapper (type aliases, barrel exports, utilities) |
| `arrayTypes` | array | — | Virtual array type references (no files generated) |
| `dictionaryTypes` | array | — | Virtual dictionary type references (no files generated) |
| `concreteGenericClasses` | array | — | Virtual concrete generic class references (no files generated) |
| `concreteGenericInterfaces` | array | — | Virtual concrete generic interface references (no files generated) |

---

### `interfaces[]` — Interface definition

| Field | Type | Notes |
|---|---|---|
| `name` | string (required) | Interface name |
| `typeIdentifier` | string | Unique ID for cross-referencing within the batch |
| `fileName` | string | Custom file name without extension |
| `path` | string | Subdirectory path (e.g., `"models"`, `"services/auth"`) |
| `comment` | string | Documentation comment for the interface |
| `properties` | array | Field/property declarations (type-only, no logic) |
| `customCode` | array | Method signatures and other code members |
| `customImports` | array | External library imports |
| `decorators` | array | Decorator/annotation expressions |
| `genericArguments` | array | Makes this a generic interface template |
| `interfaceTypeIdentifiers` | string[] | Identifiers of interfaces this one extends |

---

### `classes[]` — Class definition

| Field | Type | Notes |
|---|---|---|
| `name` | string (required) | Class name |
| `typeIdentifier` | string | Unique ID for cross-referencing within the batch |
| `fileName` | string | Custom file name without extension |
| `path` | string | Subdirectory path |
| `comment` | string | Documentation comment |
| `isAbstract` | boolean | Whether the class is abstract |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class to extend |
| `interfaceTypeIdentifiers` | string[] | typeIdentifiers of interfaces to implement |
| `properties` | array | Field declarations (type only, no initialization, no methods) |
| `constructorParameters` | array | Constructor params — auto-become properties in C#/Java/Go/Groovy (do NOT duplicate in `properties`) |
| `customCode` | array | Methods, initialized fields, any logic |
| `customImports` | array | External library imports |
| `decorators` | array | Class-level decorators/annotations |
| `genericArguments` | array | Makes this a generic class template |

---

### `properties[]` — Property/field declaration (within interfaces or classes)

| Field | Type | Notes |
|---|---|---|
| `name` | string (required) | Field name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `typeIdentifier` | string | Reference to another type in the batch |
| `type` | string | Complex or external type literal (e.g., `"Map<string, $resp>"`) |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — resolves `$placeholder` in `type` string |
| `isOptional` | boolean | Generates nullable/optional annotation |
| `isInitializer` | boolean | Adds default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | array | templateRefs for the comment field |
| `decorators` | array | Property-level decorators (`@IsEmail()`, `@Required()`, etc.) |

**Rule**: `properties` = type declarations only. No initialization, no methods. Use `customCode` for anything with logic.

---

### `customCode[]` — Code member (method, initialized field, etc.)

| Field | Type | Notes |
|---|---|---|
| `code` | string | The code text. One `customCode` item = exactly one member. |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — resolves `$placeholder` in `code`, triggers import generation |

**Rule**: Each internal type referenced in `code` MUST use `templateRefs` with `$placeholder` syntax. Otherwise, MetaEngine cannot generate the import/using directive.

---

### `customImports[]` — External library import

| Field | Type | Notes |
|---|---|---|
| `path` | string | Import path (e.g., `"@angular/core"`, `"rxjs"`) or an `identifier` of a `customFile` in the batch |
| `types` | string[] | Named exports to import |

**Rule**: Only for external libraries. Never add framework/stdlib imports (see auto-import table below). Internal types use `typeIdentifier` or `templateRefs`.

---

### `decorators[]` — Decorator/annotation

| Field | Type | Notes |
|---|---|---|
| `code` | string | Decorator expression (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | array | templateRefs if decorator references internal types |

---

### `constructorParameters[]` — Constructor parameter

| Field | Type | Notes |
|---|---|---|
| `name` | string | Parameter name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `type` | string | Complex type literal |
| `typeIdentifier` | string | Reference to internal type |

**C#/Java/Go/Groovy**: constructor parameters auto-create class properties. DO NOT duplicate them in `properties[]`.

---

### `genericArguments[]` — Generic type parameter (on class or interface)

| Field | Type | Notes |
|---|---|---|
| `name` | string | Generic parameter name (`"T"`, `"K"`, etc.) |
| `constraintTypeIdentifier` | string | typeIdentifier for constraint (`where T : BaseEntity`) |
| `propertyName` | string | Creates a property of type T with this name |
| `isArrayProperty` | boolean | If true, the property is `T[]` |

---

### `enums[]` — Enum definition

| Field | Type | Notes |
|---|---|---|
| `name` | string (required) | Enum name |
| `typeIdentifier` | string | Unique ID for cross-referencing |
| `fileName` | string | Custom file name |
| `path` | string | Subdirectory path |
| `comment` | string | Documentation comment |
| `members` | array | `[{name: string, value: number}]` |

Enum file naming: TypeScript → `order-status.enum.ts`, C# → `OrderStatus.cs`. Java/Kotlin: `ALL_CAPS` member names. Python: `snake_case`.

---

### `customFiles[]` — File without class wrapper

| Field | Type | Notes |
|---|---|---|
| `name` | string (required) | File name (without extension) |
| `identifier` | string | Optional ID for import resolution from other files in the batch |
| `path` | string | Subdirectory path |
| `fileName` | string | Overrides file name |
| `customCode` | array | Code blocks (one per export/type alias/function) |
| `customImports` | array | External imports |

Use for: type aliases, barrel exports, utility functions, constants. When `identifier` is set, other types can import via `customImports: [{path: "identifier-value"}]` and MetaEngine resolves the relative path automatically.

---

### `arrayTypes[]` — Virtual array type reference (NO files generated)

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string (required) | Unique ID to reference in properties |
| `elementTypeIdentifier` | string | Internal type as element |
| `elementPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |

C# note: `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs instead.

---

### `dictionaryTypes[]` — Virtual dictionary type reference (NO files generated)

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string (required) | Unique ID to reference in properties |
| `keyPrimitiveType` | enum | Primitive key type |
| `keyType` | string | String literal for key type |
| `keyTypeIdentifier` | string | Internal type as key |
| `valuePrimitiveType` | enum | Primitive value type |
| `valueTypeIdentifier` | string | Internal type as value |

---

### `concreteGenericClasses[]` — Virtual concrete generic class (NO files generated)

| Field | Type | Notes |
|---|---|---|
| `identifier` | string (required) | ID for referencing (e.g., as `baseClassTypeIdentifier`) |
| `genericClassIdentifier` | string | typeIdentifier of the generic class template |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` — the type arguments to bind |

Creates a virtual `Repository<User>` type. A class extends it via `baseClassTypeIdentifier: "user-repo-concrete"`. MetaEngine generates `extends Repository<User>` with correct imports.

---

### `concreteGenericInterfaces[]` — Virtual concrete generic interface (NO files generated)

Same structure as `concreteGenericClasses` but for interfaces. Used with `interfaceTypeIdentifiers` on a class.

---

## Auto-Imported Types (NEVER add to `customImports`)

| Language | Auto-imported (never specify) |
|---|---|
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
| TypeScript | (no imports needed — built-in types) |

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

---

## Primitive Type Mapping

| MetaEngine enum | TS | C# | Python | Go | Java |
|---|---|---|---|---|---|
| `String` | `string` | `string` | `str` | `string` | `String` |
| `Number` | `number` | `int` | `int` | `int` | `int` |
| `Boolean` | `boolean` | `bool` | `bool` | `bool` | `boolean` |
| `Date` | `Date` | `DateTime` | `datetime` | `time.Time` | `LocalDateTime` |
| `Any` | `unknown` | `object` | `Any` | `interface{}` | `Object` |

**C# gotcha**: `Number` → `int`, NOT `double`. Use `"type": "double"` or `"type": "decimal"` explicitly for non-integer numbers.

---

## Critical Rules (causes most failures when violated)

### 1. Generate ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both MUST be in the same `generate_code` call. Splitting into separate calls breaks the typegraph — cross-file imports won't be generated.

### 2. Properties = type declarations. CustomCode = everything else.
- `properties[]` → uninitialized field declarations with types only
- `customCode[]` → methods, initialized fields, any code with logic
- One `customCode` item = exactly one member
- **Never put methods in properties. Never put uninitialized type declarations in customCode.**

### 3. Use templateRefs for internal types in customCode
When `customCode` or `type` strings reference a type from the same batch, use `$placeholder` syntax with `templateRefs`. This triggers automatic import resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**C# critical**: Every internal type reference in `customCode` MUST use templateRefs, or `using` directives for cross-namespace types won't be generated.

### 4. Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

### 5. templateRefs are ONLY for internal types
- Same MCP call types → `typeIdentifier` or `templateRefs`
- External library types → `customImports`
- Never mix these.

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Do NOT duplicate constructor parameter names in `properties[]` — causes "Sequence contains more than one matching element" errors.

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references only. They never produce files.

### 8. Interface method signatures go in customCode, not properties
For interfaces that will be `implements`/`:` by a class, put method signatures in `customCode`. If you use function-typed properties (e.g., `"type": "() => Promise<User[]>"`), the implementing class will duplicate them as property declarations alongside your customCode methods.

### 9. Don't reference non-existent typeIdentifiers
A property referencing a `typeIdentifier` that doesn't exist in the batch is silently dropped. Verify every typeIdentifier matches a defined type in the same call.

### 10. Don't use reserved words as property names
Avoid `delete`, `class`, `import` etc. Use safe alternatives (`remove`, `clazz`, `importData`).

---

## Language-Specific Notes

### TypeScript
- MetaEngine strips `I` prefix from interface names. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control the file name if collisions arise (set `"fileName": "i-user-repository"` on the interface).
- `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly
- No imports needed for built-in types

### C#
- `I` prefix preserved on interface names
- `Number` → `int` (NOT `double`). Use `"type": "decimal"` or `"type": "double"` for non-integer numbers.
- `packageName` sets the namespace. Omit for GlobalUsings pattern.
- Interface properties generate `{ get; }`. Class properties generate `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs.
- `isOptional` on properties generates `string?` (nullable reference type)
- Every internal cross-namespace type in customCode MUST use templateRefs or `using` directives won't be generated.

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode
- typing imports are automatic

### Go
- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode
- Constructor parameters don't apply the same way as C#/Java

### Java/Kotlin/Groovy
- Constructor parameters auto-create class properties — don't duplicate in `properties[]`
- Enum members use `ALL_CAPS` naming convention (MetaEngine handles this automatically)

---

## Pattern Examples

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
Produces two files with automatic imports between them.

### Class with inheritance and methods
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

### Array and dictionary types
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
Then reference via `"typeIdentifier": "user-list"` in properties.

### Complex type expressions with templateRefs
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
templateRefs work in `properties`, `customCode`, and `decorators`.

### Service with external dependency injection (Angular example)
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

### Interface with method signatures (correct pattern)
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

### customFiles for type aliases and barrel exports
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

---

## `load_spec_from_file` Tool

Use instead of `generate_code` when the spec is large or when you want version-controlled, reusable architecture templates.

| Parameter | Type | Notes |
|---|---|---|
| `specFilePath` | string (required) | Absolute or relative path to `.json` spec file |
| `outputPath` | string | Overrides `outputPath` in spec file |
| `skipExisting` | boolean | Overrides `skipExisting` in spec file |
| `dryRun` | boolean | Overrides `dryRun` in spec file |

The spec file has the same structure as the `generate_code` input (all the same fields: `language`, `classes`, `interfaces`, `enums`, etc.).

**Workflow**: Write spec to `specs/user-system.json`, then call `load_spec_from_file({specFilePath: "specs/user-system.json", outputPath: "src"})`.

---

## `generate_openapi` Tool

Generates fully typed HTTP clients from OpenAPI specs.

**Frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession`

Required: `framework` + either `openApiSpec` (inline YAML/JSON) or `openApiSpecUrl` (URL).

Key options:
- `outputPath`, `dryRun`, `skipExisting` — standard
- `documentation` — generate JSDoc/XML comments
- `errorHandling` — `{enabled, throwForStatusCodes, returnNullForStatusCodes}`
- `bearerAuth` / `basicAuth` / `customHeaders` — auth configuration
- `retries` — `{maxAttempts, retryStatusCodes, baseDelaySeconds, maxDelaySeconds}`
- `timeout` — `{seconds, connect, read, write}`
- `optionsObjectThreshold` — min params before grouping into options object
- `strictValidation` — enable strict OpenAPI spec validation

Framework-specific options:
- **Angular**: `angularOptions.baseUrlToken`, `angularOptions.providedIn`, `angularOptions.useInjectFunction`, `angularOptions.useHttpResources`, `angularOptions.httpResourceTrigger`, `angularOptions.responseDateTransformation`
- **React**: `reactOptions.useTanStackQuery`, `reactOptions.baseUrlEnvVar`, `reactOptions.responseDateTransformation`, `reactOptions.useTypesBarrel`
- **TypeScript Fetch**: `fetchOptions.baseUrlEnvVar`, `fetchOptions.useImportMetaEnv` (Vite/SvelteKit), `fetchOptions.useMiddleware`, `fetchOptions.useResultPattern`, `fetchOptions.useTypesBarrel`
- **Go**: `goOptions.moduleName` (required), `goOptions.packageName` (required), `goOptions.baseUrlEnvVar`, `goOptions.useContext`, `goOptions.jsonLibrary`
- **Java Spring**: `javaSpringOptions.packageName` (required), `javaSpringOptions.beanValidation`, `javaSpringOptions.nonNullSerialization`, `javaSpringOptions.baseUrlProperty`, `javaSpringOptions.useComponentAnnotation`
- **C#**: `csharpOptions.namespaceName` (required)
- **Kotlin**: `kotlinOptions.packageName` (required)
- **Rust**: `rustOptions.crateName` (required), `rustOptions.strictEnums`
- **Swift**: `swiftOptions.strictEnums`, `swiftOptions.typedThrows`
- **Python**: `pythonOptions.baseUrlEnvVar`, `pythonOptions.generateSyncMethods`, `pythonOptions.useCamelCaseAliases`

---

## `generate_graphql` Tool

Generates fully typed HTTP clients from GraphQL SDL schemas.

**Frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-fastapi`, `rust-reqwest`, `swift-urlsession`

Required: `framework` + `graphQLSchema` (SDL content string).

Key options (similar to openapi):
- `documentation` — generate comments from schema descriptions
- `discriminatedUnions` — generate discriminated unions for GraphQL union types
- `errorHandling.mode` — `"throw"` or `"result"`
- `bearerAuth`, `basicAuth`, `customHeaders.headers[]` (array of `{name, value}`)
- `retries.maxRetries`
- `timeout.seconds`
- Framework-specific options same structure as `generate_openapi` (Angular, React, Fetch, Go, Java, C#, Kotlin, Rust, Swift, Python options)

---

## `generate_protobuf` Tool

Generates fully typed HTTP clients from `.proto` definitions.

**Frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-httpx`, `rust-reqwest`, `swift-urlsession`

Required: `framework` + `protoSource` (proto definition content string).

Note: Python framework here is `python-httpx` (not `python-fastapi`).

TypeScript Fetch extras: `fetchOptions.useTypesBarrel`, `fetchOptions.useImportMetaEnv`

---

## `generate_sql` Tool

Generates typed model classes from SQL DDL (`CREATE TABLE` statements).

Required: `language` + `ddlSource` (DDL string).

**Languages**: `typescript`, `csharp`, `go`, `python`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`

Key options:
- `generateInterfaces` — generate interfaces alongside model classes
- `generateNavigationProperties` — navigation properties for FK relationships
- `generateValidationAnnotations` — validation annotations from column constraints
- `initializeProperties` — initialize model properties with defaults
- `dryRun`, `skipExisting`, `outputPath` — standard

Language-specific options:
- `csharpOptions.namespace`
- `goOptions.moduleName` (required for Go)
- `javaOptions.packageName` (required for Java)
- `kotlinOptions.packageName` (required for Kotlin)
- `groovyOptions.packageName` (required for Groovy)
- `scalaOptions.packageName` (required for Scala)
- `phpOptions.rootNamespace` (required for PHP), `phpOptions.useStrictTypes`
- `pythonOptions.modelStyle` — `"dataclass"`, `"pydantic"`, or `"plain"`
- `rustOptions.crateName`

---

## Output Structure

MetaEngine writes one source file per type (interface, class, enum). `customFiles` get their own file too. Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) produce NO files.

When `dryRun: true`, file contents are returned in the response for review without writing to disk.

When `skipExisting: true` (default), existing files are not overwritten — useful for stub pattern (generate once, then customize).

File naming conventions:
- TypeScript: kebab-case (e.g., `user-service.ts`, `order-status.enum.ts`)
- C#: PascalCase (e.g., `UserService.cs`, `OrderStatus.cs`)
- Java/Kotlin: PascalCase (e.g., `UserService.java`)
- Python: snake_case (e.g., `user_service.py`)
- Go: snake_case (e.g., `user_service.go`)

---

## Common Mistakes Quick Reference

1. **Splitting related types across multiple calls** → cross-references fail silently. Always batch in ONE call.
2. **Putting method signatures as function-typed properties on interfaces** → implementing class duplicates them. Use `customCode` for interface method signatures.
3. **Raw internal type names in customCode strings** (e.g., `"private repo: IUserRepository"`) → import not generated. Use `templateRefs` with `$placeholder`.
4. **Using `arrayTypes` in C# when you need `List<T>`** → `arrayTypes` generates `IEnumerable<T>`. Use `"type": "List<$user>"` with templateRefs.
5. **Adding stdlib imports to `customImports`** → duplication or errors. Let MetaEngine handle them.
6. **Duplicating constructor parameters in `properties[]`** for C#/Java/Go/Groovy → "Sequence contains more than one matching element" error.
7. **Expecting `Number` → `double` in C#** → it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.
8. **Forgetting `fileName` when I-prefixed interface and its class collide in TypeScript** → set `"fileName": "i-user-repository"` on the interface.
9. **Referencing a typeIdentifier not defined in the batch** → property silently dropped.
10. **Using reserved words as property names** → use safe alternatives.
