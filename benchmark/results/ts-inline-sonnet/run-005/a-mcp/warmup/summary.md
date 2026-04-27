# MetaEngine MCP — Knowledge Brief

MetaEngine is a **semantic code generation system** exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__generate_code` | Generate typed source files from structured JSON spec (classes, interfaces, enums, etc.) |
| `mcp__metaengine__load_spec_from_file` | Load a JSON spec from disk and generate — avoids context bloat for large specs |
| `mcp__metaengine__generate_openapi` | Generate typed HTTP client from OpenAPI spec (YAML/JSON or URL) |
| `mcp__metaengine__generate_graphql` | Generate typed HTTP client from GraphQL SDL schema |
| `mcp__metaengine__generate_protobuf` | Generate typed HTTP client from Protocol Buffers (.proto) definitions |
| `mcp__metaengine__generate_sql` | Generate typed model classes from SQL DDL (CREATE TABLE statements) |
| `mcp__metaengine__metaengine_initialize` | Returns patterns and documentation; call when starting or unsure |

---

## `generate_code` — Full Input Schema

### Top-level fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `language` | enum (required) | — | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | `"."` | Directory where files are written |
| `packageName` | string | optional | Package/module/namespace. C#: omit for GlobalUsings. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy default: `com.metaengine.generated` |
| `initialize` | boolean | `false` | Initialize properties with default values |
| `skipExisting` | boolean | `true` | Skip files that already exist (stub pattern) |
| `dryRun` | boolean | `false` | Preview mode — returns code without writing to disk |
| `classes` | array | — | Class definitions (see below) |
| `interfaces` | array | — | Interface definitions (see below) |
| `enums` | array | — | Enum definitions (see below) |
| `arrayTypes` | array | — | Virtual array type refs — NO files generated |
| `dictionaryTypes` | array | — | Virtual dictionary type refs — NO files generated |
| `concreteGenericClasses` | array | — | Virtual `Repository<User>` style refs — NO files generated |
| `concreteGenericInterfaces` | array | — | Virtual `IRepository<User>` style refs — NO files generated |
| `customFiles` | array | — | Raw files without class wrapper (type aliases, barrel exports) |

---

### `classes[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string (required) | Class name |
| `typeIdentifier` | string | Unique ID for referencing this class from other types in same batch |
| `path` | string | Subdirectory path (e.g., `"services/auth"`) |
| `fileName` | string | Custom file name without extension |
| `comment` | string | Documentation comment for the class |
| `isAbstract` | boolean | Makes class abstract |
| `baseClassTypeIdentifier` | string | typeIdentifier of the parent class to extend |
| `interfaceTypeIdentifiers` | string[] | Array of interface typeIdentifiers to implement |
| `properties` | array | Field declarations (type-only, no logic) |
| `constructorParameters` | array | Constructor params — **auto-become properties** in TS, C#, Java, Go, Groovy (do NOT duplicate in `properties`) |
| `customCode` | array | Methods, initialized fields, any logic — one item = one member |
| `customImports` | array | External library imports only (e.g., `@angular/core`) |
| `decorators` | array | Class decorators (e.g., `@Injectable(...)`) |
| `genericArguments` | array | Makes this a generic class template (like `Repository<T>`) |

#### `classes[].properties[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `typeIdentifier` | string | Reference to another type in the same batch |
| `type` | string | Complex or external type literal (e.g., `"Map<string, $resp>"`) |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — resolves `$placeholder` to type + generates import |
| `isOptional` | boolean | Marks property optional (C#: generates nullable `?`) |
| `isInitializer` | boolean | Add default value initialization |
| `decorators` | array | Property decorators (e.g., `@IsEmail()`) |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | array | templateRefs for the comment |

#### `classes[].constructorParameters[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Parameter name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `typeIdentifier` | string | Reference to another type in batch |
| `type` | string | Complex/external type literal |

#### `classes[].customCode[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | The method or initialized field. Use `$placeholder` for internal type refs. |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — triggers import generation for `$placeholder` |

#### `classes[].customImports[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (e.g., `"@angular/core"`, `"rxjs"`) |
| `types` | string[] | Named exports to import (e.g., `["Injectable", "inject"]`) |

#### `classes[].decorators[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Decorator text (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | array | templateRefs for `$placeholder` inside decorator code |

#### `classes[].genericArguments[]` item schema (makes class generic like `Repository<T>`)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Generic param name (e.g., `"T"`, `"K"`) |
| `constraintTypeIdentifier` | string | typeIdentifier for generic constraint (`where T : BaseEntity`) |
| `propertyName` | string | Creates a property of type `T` with this name |
| `isArrayProperty` | boolean | If true, property is `T[]` |

---

### `interfaces[]` item schema

Same structure as `classes[]` minus `isAbstract`, `baseClassTypeIdentifier`, `constructorParameters`, `genericArguments`. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string (required) | Interface name |
| `typeIdentifier` | string | Unique ID for referencing this interface |
| `path` | string | Subdirectory path |
| `fileName` | string | Custom file name (use to prevent TypeScript name collision when `I` prefix is stripped) |
| `comment` | string | Documentation comment |
| `properties` | array | Same as class properties schema |
| `customCode` | array | Method signatures — use for methods when a class will `implements` this interface |
| `customImports` | array | External library imports |
| `decorators` | array | Decorators |
| `interfaceTypeIdentifiers` | string[] | Extend other interfaces |
| `genericArguments` | array | Makes this a generic interface template |

---

### `enums[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Unique ID for referencing this enum |
| `path` | string | Subdirectory path |
| `fileName` | string | Custom file name |
| `comment` | string | Documentation comment |
| `members` | array | `[{name: string, value: number}]` |

Enums auto-suffix filenames: `order-status.enum.ts` (TypeScript), `OrderStatus.cs` (C#).

---

### `arrayTypes[]` item schema (virtual — NO files generated)

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference this array type elsewhere |
| `elementTypeIdentifier` | string | Reference to custom element type |
| `elementPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |

Reference via `"typeIdentifier": "user-list"` in properties. **C# note**: arrayTypes generate `IEnumerable<T>`, not `List<T>`.

---

### `dictionaryTypes[]` item schema (virtual — NO files generated)

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference this dictionary type |
| `keyPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `keyTypeIdentifier` | string | Reference to custom key type |
| `keyType` | string | String literal for key type (e.g., `"string"`) |
| `valuePrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `valueTypeIdentifier` | string | Reference to custom value type |

---

### `concreteGenericClasses[]` item schema (virtual — NO files generated)

Creates a `Repository<User>` type reference for use as a base class.

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID for this concrete type (used as `baseClassTypeIdentifier` in a class) |
| `genericClassIdentifier` | string | References the generic class definition |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` — the type arguments to fill in |

---

### `concreteGenericInterfaces[]` item schema (virtual — NO files generated)

Same as `concreteGenericClasses` but for interfaces. Used as `interfaceTypeIdentifiers` entry.

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID for this concrete interface type |
| `genericClassIdentifier` | string | References the generic interface definition |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` |

---

### `customFiles[]` item schema

Generates raw files without a class wrapper. For type aliases, barrel exports, utility functions.

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (without extension) |
| `path` | string | Directory path |
| `fileName` | string | Custom file name override |
| `identifier` | string | Optional ID enabling import resolution from other files via `customImports` |
| `customCode` | array | Code blocks — one per export/type alias/function |
| `customImports` | array | External imports |

---

## `load_spec_from_file` — Input Schema

| Field | Type | Description |
|-------|------|-------------|
| `specFilePath` | string (required) | Absolute or relative path to the JSON spec file |
| `outputPath` | string | Overrides `outputPath` in spec file |
| `skipExisting` | boolean | Overrides `skipExisting` in spec file |
| `dryRun` | boolean | Overrides `dryRun` in spec file |

The JSON spec file has the same structure as `generate_code` parameters. Use this for large architectures to avoid context bloat.

---

## `generate_openapi` — Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `framework` | enum (required) | `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession` |
| `openApiSpec` | string | Inline YAML or JSON spec content |
| `openApiSpecUrl` | string | URL to fetch the spec (one of `openApiSpec` or `openApiSpecUrl` required) |
| `outputPath` | string | Output directory (default: `"."`) |
| `dryRun` | boolean | Preview mode |
| `skipExisting` | boolean | Skip existing files |
| `documentation` | boolean | Generate JSDoc/XML doc comments |
| `errorHandling` | object | `{enabled, throwForStatusCodes[], returnNullForStatusCodes[]}` |
| `bearerAuth` | object | `{envVarName, headerName}` |
| `basicAuth` | object | `{usernameEnvVar, passwordEnvVar}` |
| `customHeaders` | array | `[{headerName, envVarName}]` |
| `retries` | object | `{maxAttempts, baseDelaySeconds, maxDelaySeconds, retryStatusCodes[]}` |
| `timeout` | object | `{seconds, connect, read, write}` |
| `optionsObjectThreshold` | number | Min params before grouping into options object |
| `strictValidation` | boolean | Strict OpenAPI spec validation |
| `angularOptions` | object | `{baseUrlToken, providedIn, useInjectFunction, useHttpResources, httpResourceTrigger, responseDateTransformation}` |
| `reactOptions` | object | `{baseUrlEnvVar, useTanStackQuery, useTypesBarrel, responseDateTransformation}` |
| `fetchOptions` | object | `{baseUrlEnvVar, useImportMetaEnv, useMiddleware, useResultPattern, useTypesBarrel}` |
| `goOptions` | object (required for go) | `{moduleName, packageName, baseUrlEnvVar, jsonLibrary, useContext}` |
| `javaSpringOptions` | object (required for java) | `{packageName, beanValidation, nonNullSerialization, baseUrlProperty, useComponentAnnotation}` |
| `kotlinOptions` | object (required for kotlin) | `{packageName}` |
| `csharpOptions` | object (required for csharp) | `{namespaceName}` |
| `pythonOptions` | object | `{baseUrlEnvVar, generateSyncMethods, useCamelCaseAliases}` |
| `rustOptions` | object (required for rust) | `{crateName, strictEnums}` |
| `swiftOptions` | object | `{strictEnums, typedThrows}` |

---

## `generate_graphql` — Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `framework` | enum (required) | `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-fastapi`, `rust-reqwest`, `swift-urlsession` |
| `graphQLSchema` | string (required) | GraphQL SDL schema content |
| `outputPath` | string | Output directory |
| `dryRun` | boolean | Preview mode |
| `skipExisting` | boolean | Skip existing files |
| `documentation` | boolean | Generate doc comments from schema descriptions |
| `discriminatedUnions` | boolean | Generate discriminated unions for GraphQL union types |
| `errorHandling` | object | `{mode: "throw" | "result"}` |
| `bearerAuth` | object | `{enabled}` |
| `basicAuth` | object | `{enabled}` |
| `customHeaders` | object | `{headers: [{name, value}]}` |
| `retries` | object | `{maxRetries}` |
| `timeout` | object | `{seconds}` |
| Framework-specific options | — | Same pattern as `generate_openapi` (angularOptions, reactOptions, fetchOptions, goOptions, javaSpringOptions, etc.) |

---

## `generate_protobuf` — Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `framework` | enum (required) | `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-httpx`, `rust-reqwest`, `swift-urlsession` |
| `protoSource` | string (required) | Protocol Buffers `.proto` definition content |
| `outputPath` | string | Output directory |
| `dryRun` | boolean | Preview mode |
| `skipExisting` | boolean | Skip existing files |
| `documentation` | boolean | Generate doc comments from proto comments |
| `errorHandling` | object | `{mode: "throw" | "result"}` |
| `bearerAuth` | object | `{enabled}` |
| `basicAuth` | object | `{enabled}` |
| `customHeaders` | object | `{headers: [{name, value}]}` |
| `retries` | object | `{maxRetries}` |
| `timeout` | object | `{seconds}` |
| Framework-specific options | — | `angularOptions`, `reactOptions`, `fetchOptions` (with `useTypesBarrel`, `useImportMetaEnv`), `goOptions`, `javaSpringOptions`, `kotlinOptions`, `csharpOptions`, `pythonOptions`, `rustOptions`, `swiftOptions` |

---

## `generate_sql` — Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `language` | enum (required) | `typescript`, `csharp`, `go`, `python`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `ddlSource` | string (required) | SQL DDL source (CREATE TABLE statements) |
| `outputPath` | string | Output directory |
| `dryRun` | boolean | Preview mode |
| `skipExisting` | boolean | Skip existing files |
| `generateInterfaces` | boolean | Generate interfaces alongside model classes |
| `generateNavigationProperties` | boolean | Navigation properties for FK relationships |
| `generateValidationAnnotations` | boolean | Validation annotations from column constraints |
| `initializeProperties` | boolean | Initialize properties with defaults |
| `javaOptions` | object | `{packageName}` (required for Java) |
| `kotlinOptions` | object | `{packageName}` (required for Kotlin) |
| `groovyOptions` | object | `{packageName}` (required for Groovy) |
| `scalaOptions` | object | `{packageName}` (required for Scala) |
| `csharpOptions` | object | `{namespace}` |
| `goOptions` | object | `{moduleName}` (required for Go) |
| `pythonOptions` | object | `{modelStyle: "dataclass" | "pydantic" | "plain"}` |
| `phpOptions` | object | `{rootNamespace, useStrictTypes}` (required for PHP) |
| `rustOptions` | object | `{crateName}` |

---

## Critical Rules (Must Not Violate)

### Rule 1 — ONE call for all related types
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, **both must be in the same `generate_code` call**. Splitting into multiple calls breaks cross-type imports.

### Rule 2 — Properties vs CustomCode distinction
- `properties[]` = type declarations only (no logic, no initialization with `=`)
- `customCode[]` = methods, initialized fields, anything with logic
- One `customCode` item = exactly one member
- **Never put methods in properties. Never put uninitialized type declarations in customCode.**

### Rule 3 — templateRefs for internal types in customCode
When customCode references a type from the same batch, use `$placeholder` syntax + `templateRefs`. Without this, MetaEngine cannot generate import/using directives.
```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```
**Critical in C#**: Every internal type reference in customCode MUST use templateRefs or `using` directives for cross-namespace types won't be generated.

### Rule 4 — Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

Auto-imported per language (never specify in `customImports`):
- **TypeScript**: no imports needed — built-in types
- **C#**: `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*`
- **Python**: `typing.*`, `pydantic (BaseModel, Field)`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses`
- **Java**: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*`
- **Kotlin**: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`
- **Go**: `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, + more
- **Swift**: `Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)`
- **Rust**: `std::collections (HashMap, HashSet)`, `chrono`, `uuid`, `rust_decimal`, `serde`
- **Groovy**: `java.time.*`, `java.math.*`, `java.util (UUID, Date)`, `java.io (File, InputStream, OutputStream)`
- **Scala**: `java.time.*`, `scala.math (BigDecimal, BigInt)`, `java.util.UUID`, `scala.collection.mutable.*`
- **PHP**: `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable`

### Rule 5 — templateRefs are ONLY for internal types
- Same batch type → use `typeIdentifier` or `templateRefs`
- External library → use `customImports`
- Never mix these

### Rule 6 — Constructor parameters auto-create properties
In **C#, Java, Go, and Groovy**, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]` — causes "Sequence contains more than one matching element" errors.

### Rule 7 — Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, and `concreteGenericInterfaces` create reusable type references only. They **never produce files**.

---

## Language-Specific Notes

### TypeScript
- MetaEngine **strips `I` prefix** from interface names when generating TypeScript. `IUserRepository` → exported as `UserRepository`. Use `fileName: "i-user-repository"` to control file name and avoid collisions with implementing class.
- Primitive type mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- `constructorParameters` auto-become properties (same as C#/Java)
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly

### C#
- `I` prefix preserved on interface names
- `Number` → `int`. For non-integer use `"type": "decimal"` or `"type": "double"` explicitly
- `packageName` sets the namespace; omit for GlobalUsings pattern
- Interface properties generate `{ get; }`. Class properties generate `{ get; set; }`
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs instead
- `isOptional` on properties generates nullable reference type `string?`

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode
- `typing` imports are automatic

### Go
- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode

### Java / Kotlin / Groovy
- Constructor parameters auto-create properties — do NOT duplicate in `properties[]`
- Java: enums use `ALL_CAPS` naming (idiomatic transformation applied automatically)

---

## Common Mistakes Reference

1. **Don't** reference a `typeIdentifier` not in the same batch → silently dropped.
2. **Don't** use function-typed properties for interface methods the class will implement → creates duplicate property + method. Use `customCode` for interface method signatures.
3. **Don't** write internal type names as raw strings in customCode → use templateRefs.
4. **Don't** use `arrayTypes` in C# when you need `List<T>` → use `"type": "List<$user>"` + templateRefs.
5. **Don't** add `System.*`, `typing.*`, `java.util.*` etc. to customImports → auto-handled.
6. **Don't** duplicate constructor parameters in `properties[]` (C#/Java/Go/Groovy).
7. **Don't** use reserved words (`delete`, `class`, `import`) as property names → use `remove`, `clazz`, `importData`.
8. **Don't** generate related types in separate MCP calls → batch everything in one call.
9. **Don't** assume `Number` → `double` in C# — it maps to `int`.
10. **Don't** forget `fileName` when both an `I`-prefixed interface and its implementing class exist in TypeScript.

---

## Patterns: Complete Working Examples

### Basic interfaces with cross-references (TypeScript)
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

### Class with inheritance and methods
```jsonc
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

### Generic class + concrete implementation
```jsonc
{
  "language": "typescript",
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
  "language": "typescript",
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

### Complex type expressions with templateRefs in properties
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

### Enum + class referencing it
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

### Angular service with DI and external imports
```jsonc
{
  "language": "typescript",
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

### customFiles for type aliases and barrel exports
```jsonc
{
  "language": "typescript",
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

### Interface with method signatures (TypeScript/C#)
Use `customCode` for method signatures on interfaces that will be implemented by a class. If you use function-typed properties instead, the implementing class will produce duplicate declarations.
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
  }]
}
```

---

## Output Structure

Each `generate_code` call:
- Writes one file per class, interface, enum, or customFile to the specified `outputPath`
- Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) contribute type resolution only — no files
- All cross-references within the batch get correct imports/using directives auto-generated
- When `dryRun: true`, returns file contents in the response instead of writing

File naming conventions by language:
- **TypeScript**: `kebab-case.ts`, enums: `name.enum.ts`
- **C#**: `PascalCase.cs`
- **Java/Kotlin**: `PascalCase.java` / `PascalCase.kt`
- **Go**: `snake_case.go`
- **Python**: `snake_case.py`

---

## When to Use `load_spec_from_file` vs inline `generate_code`

Use `load_spec_from_file` when:
- The spec is large (many classes/interfaces) — avoids bloating AI context
- You want version-controlled architecture templates
- Reusing specs across projects

The JSON spec file uses the identical structure as `generate_code` parameters (including `language`, `outputPath`, etc.).

---

## `dryRun` Mode

Set `dryRun: true` on any generation tool to preview output without writing files. The response includes the file contents for review. Use this when you want to inspect before committing.

---

## `skipExisting` Behavior

Default is `true` — files that already exist on disk are not overwritten. This supports the "stub pattern" where you generate scaffolding once and then manually fill in logic. Set to `false` to force regeneration.
