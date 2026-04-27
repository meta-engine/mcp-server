# MetaEngine MCP — Knowledge Brief

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files. It resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

Supported languages: TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust.

---

## Tools Exposed

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__metaengine_initialize` | Returns patterns and documentation. Call when generating for the first time or needing guidance. Optional `language` param (enum). |
| `mcp__metaengine__generate_code` | Main code generation tool. Generates compilable source files from structured JSON spec. |
| `mcp__metaengine__load_spec_from_file` | Load a JSON spec file from disk and generate from it. Same power as `generate_code` but zero context overhead. |
| `mcp__metaengine__generate_openapi` | Generate typed HTTP clients from OpenAPI specs (YAML/JSON inline or URL). |
| `mcp__metaengine__generate_graphql` | Generate typed HTTP clients from GraphQL SDL schemas. |
| `mcp__metaengine__generate_protobuf` | Generate typed HTTP clients from Protocol Buffers (.proto) definitions. |
| `mcp__metaengine__generate_sql` | Generate typed model classes from SQL DDL (CREATE TABLE statements). |

---

## generate_code — Full Input Schema

### Top-level parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | enum (required) | — | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | `"."` | Directory where files are written |
| `packageName` | string | — | Package/module/namespace. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy default: `com.metaengine.generated`. C#: omit for GlobalUsings pattern (no namespace declaration). |
| `skipExisting` | boolean | `true` | Skip files that already exist (stub pattern) |
| `dryRun` | boolean | `false` | Preview: returns generated code in response without writing to disk |
| `initialize` | boolean | `false` | Initialize properties with default values |
| `interfaces` | array | — | Interface definitions |
| `classes` | array | — | Class definitions (regular and generic templates) |
| `enums` | array | — | Enum definitions |
| `customFiles` | array | — | Utility files, type aliases, barrel exports — generate files WITHOUT a class wrapper |
| `arrayTypes` | array | — | Array type references — NO files generated, virtual types only |
| `dictionaryTypes` | array | — | Dictionary type references — NO files generated, virtual types only |
| `concreteGenericClasses` | array | — | Concrete generic class instantiations (e.g., `Repository<User>`) — NO files generated |
| `concreteGenericInterfaces` | array | — | Concrete generic interface instantiations — NO files generated |

### `interfaces[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Interface name |
| `typeIdentifier` | string | Unique ID for referencing this interface elsewhere in the batch |
| `fileName` | string | Custom file name without extension |
| `path` | string | Directory path (e.g., `"models"`, `"services/auth"`) |
| `comment` | string | Documentation comment |
| `properties` | array | Property declarations (type only, no logic) |
| `customCode` | array | Method signatures, initialized members — one item = one member |
| `customImports` | array | External library imports only |
| `decorators` | array | Decorator/annotation objects with `code` and optional `templateRefs` |
| `genericArguments` | array | Generic parameters (makes this a generic interface template) |
| `interfaceTypeIdentifiers` | string[] | Extend other interfaces (by their `typeIdentifier`) |

### `classes[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Class name |
| `typeIdentifier` | string | Unique ID for referencing this class elsewhere in the batch |
| `fileName` | string | Custom file name without extension |
| `path` | string | Directory path |
| `comment` | string | Documentation comment |
| `isAbstract` | boolean | Whether this is an abstract class |
| `baseClassTypeIdentifier` | string | `typeIdentifier` of the base class to extend |
| `interfaceTypeIdentifiers` | string[] | Interfaces to implement (by `typeIdentifier`) |
| `constructorParameters` | array | Constructor params (auto-become properties in TS, C#, Java, Go, Groovy — do NOT duplicate in `properties[]`) |
| `properties` | array | Property declarations (non-constructor properties only for C#/Java/Go/Groovy) |
| `customCode` | array | Methods, initialized fields — one item = one member |
| `customImports` | array | External library imports only |
| `decorators` | array | Class-level decorators/annotations |
| `genericArguments` | array | Generic parameters (makes this a generic class template) |

### `properties[]` item schema (used in both interfaces and classes)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `typeIdentifier` | string | Reference to another type in the batch |
| `type` | string | Complex/external type literal (e.g., `"List<$user>"`, `"Map<string, $resp>"`) |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — used when `type` contains `$placeholder` syntax |
| `isOptional` | boolean | Marks field as optional (generates `?` in TS, `?` nullable in C#) |
| `isInitializer` | boolean | Add default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | array | templateRefs for comments |
| `decorators` | array | Property-level decorators/annotations |

### `customCode[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | The code text for exactly one member (method, initialized field, etc.). Use `\n` for newlines — auto-indented. |
| `templateRefs` | array | `[{placeholder: "$name", typeIdentifier: "some-id"}]` — triggers import resolution for internal types referenced in the code string |

### `constructorParameters[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Parameter name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `typeIdentifier` | string | Reference to another type in the batch |
| `type` | string | Complex/external type literal |

### `enums[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Unique ID |
| `fileName` | string | Custom file name |
| `path` | string | Directory path |
| `comment` | string | Documentation comment |
| `members` | array | `[{name: string, value: number}]` |

Auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#). Java enums: ALL_CAPS names automatically.

### `customFiles[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (without extension) |
| `fileName` | string | Alternative custom file name |
| `path` | string | Directory path |
| `identifier` | string | Optional — enables other files to import this via `customImports` path resolution |
| `customCode` | array | Code blocks (exports, type aliases, utility functions) |
| `customImports` | array | External library imports |

### `arrayTypes[]` item schema (virtual — no files generated)

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference this array type in properties |
| `elementTypeIdentifier` | string | Reference to custom element type |
| `elementPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |

C# note: `arrayTypes` generates `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs instead.

### `dictionaryTypes[]` item schema (virtual — no files generated)

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference this dictionary type |
| `keyPrimitiveType` | enum | Primitive key type |
| `keyTypeIdentifier` | string | Custom key type reference |
| `keyType` | string | String literal for key type |
| `valuePrimitiveType` | enum | Primitive value type |
| `valueTypeIdentifier` | string | Custom value type reference |

### `concreteGenericClasses[]` item schema (virtual — no files generated)

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID for this concrete type (used in `baseClassTypeIdentifier`) |
| `genericClassIdentifier` | string | References the generic class definition |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` — type arguments to fill in |

### `concreteGenericInterfaces[]` item schema (virtual — no files generated)

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID for this concrete type |
| `genericClassIdentifier` | string | References the generic interface definition |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` |

### `genericArguments[]` item schema (on classes/interfaces — makes them generic templates)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Generic parameter name (e.g., `"T"`, `"K"`) |
| `constraintTypeIdentifier` | string | Type identifier for generic constraint (e.g., `where T : BaseEntity`) |
| `propertyName` | string | Creates a property with this name of type T |
| `isArrayProperty` | boolean | If true, creates property of type T[] |

### `customImports[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (external library path OR customFile identifier for internal resolution) |
| `types` | string[] | Named imports from that path |

### `decorators[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Decorator/annotation code (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | array | templateRefs for internal type references within the decorator code |

---

## load_spec_from_file — Schema

| Parameter | Type | Description |
|-----------|------|-------------|
| `specFilePath` | string (required) | Absolute or relative path to JSON spec file. Same structure as `generate_code` input. |
| `outputPath` | string | Overrides `outputPath` in spec file |
| `skipExisting` | boolean | Overrides `skipExisting` in spec file |
| `dryRun` | boolean | Overrides `dryRun` in spec file |

Use this when the spec is too large for inline JSON in the MCP call — write the spec to a `.json` file first, then call `load_spec_from_file`. Drastically reduces AI context usage.

---

## generate_openapi — Schema Summary

Generates typed HTTP clients from OpenAPI specs (YAML/JSON).

**Required:** `framework` (enum)
**One of required:** `openApiSpec` (inline content) OR `openApiSpecUrl` (URL string)

**Frameworks:** `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession`

**Common options:** `outputPath`, `skipExisting`, `dryRun`, `documentation` (JSDoc/XML comments), `strictValidation`, `optionsObjectThreshold` (min params before options object grouping)

**Auth options:**
- `bearerAuth`: `{envVarName, headerName}`
- `basicAuth`: `{usernameEnvVar, passwordEnvVar}`
- `customHeaders`: `[{headerName, envVarName}]`

**Error handling:** `{enabled, throwForStatusCodes: number[], returnNullForStatusCodes: number[]}`

**Retry:** `{maxAttempts, retryStatusCodes, baseDelaySeconds, maxDelaySeconds}`

**Timeout:** `{seconds, connect, read, write}`

**Framework-specific options:**
- `angularOptions`: `{baseUrlToken, providedIn, useInjectFunction, useHttpResources, httpResourceTrigger, responseDateTransformation}`
- `reactOptions`: `{baseUrlEnvVar, useTanStackQuery, useTypesBarrel, responseDateTransformation}`
- `fetchOptions`: `{baseUrlEnvVar, useImportMetaEnv, useMiddleware, useResultPattern, useTypesBarrel}`
- `goOptions` (required: `moduleName`, `packageName`): `{baseUrlEnvVar, jsonLibrary, useContext}`
- `javaSpringOptions` (required: `packageName`): `{baseUrlProperty, beanValidation, nonNullSerialization, useComponentAnnotation}`
- `kotlinOptions` (required: `packageName`)
- `csharpOptions` (required: `namespaceName`)
- `pythonOptions`: `{baseUrlEnvVar, generateSyncMethods, useCamelCaseAliases}`
- `rustOptions` (required: `crateName`): `{strictEnums}`
- `swiftOptions`: `{strictEnums, typedThrows}`

---

## generate_graphql — Schema Summary

Generates typed HTTP clients from GraphQL SDL schemas.

**Required:** `framework` (enum), `graphQLSchema` (string — GraphQL SDL content)

**Frameworks:** `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-fastapi`, `rust-reqwest`, `swift-urlsession`

**Common options:** `outputPath`, `skipExisting`, `dryRun`, `documentation`, `discriminatedUnions` (generate discriminated unions for GraphQL union types)

**Auth:** `bearerAuth: {enabled}`, `basicAuth: {enabled}`, `customHeaders: {headers: [{name, value}]}`

**Error handling:** `{mode: "throw" | "result"}`

**Retry:** `{maxRetries}`

**Timeout:** `{seconds}`

Framework-specific options follow same pattern as `generate_openapi` (angularOptions, reactOptions, fetchOptions, goOptions, javaSpringOptions, kotlinOptions, csharpOptions, pythonOptions, rustOptions, swiftOptions).

---

## generate_protobuf — Schema Summary

Generates typed HTTP clients from Protocol Buffers (.proto) definitions.

**Required:** `framework` (enum), `protoSource` (string — .proto file content)

**Frameworks:** `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-httpx` (note: httpx not fastapi), `rust-reqwest`, `swift-urlsession`

**fetchOptions** additionally supports: `useTypesBarrel`, `useImportMetaEnv`

**pythonOptions** additionally supports: `generateSyncMethods`, `useCamelCaseAliases`, `baseUrlEnvVar`

Otherwise same pattern as `generate_graphql`.

---

## generate_sql — Schema Summary

Generates typed model classes from SQL DDL (CREATE TABLE statements).

**Required:** `language` (enum), `ddlSource` (string — SQL DDL content)

**Languages:** `typescript`, `csharp`, `go`, `python`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`

**Common options:** `outputPath`, `skipExisting`, `dryRun`

**Generation flags:**
- `generateInterfaces` — generate interfaces alongside model classes
- `generateNavigationProperties` — navigation properties for foreign key relationships
- `generateValidationAnnotations` — validation annotations from column constraints
- `initializeProperties` — initialize with default values

**Language-specific options:**
- `csharpOptions`: `{namespace}`
- `goOptions` (required: `moduleName`)
- `javaOptions` (required: `packageName`)
- `kotlinOptions` (required: `packageName`)
- `groovyOptions` (required: `packageName`)
- `scalaOptions` (required: `packageName`)
- `phpOptions` (required: `rootNamespace`): `{useStrictTypes}`
- `pythonOptions`: `{modelStyle: "dataclass" | "pydantic" | "plain"}`
- `rustOptions`: `{crateName}`

---

## Critical Rules (Must Follow)

### Rule 1: ONE call with ALL related types

`typeIdentifier` references only resolve **within the current batch**. If `UserService` references `User`, both MUST be in the same `generate_code` call. Cross-file imports only resolve within a single batch. Never split related types across multiple calls.

### Rule 2: properties[] = type declarations only; customCode[] = everything else

- `properties[]`: fields with types only, NO initialization, NO logic
- `customCode[]`: methods, initialized fields, anything with logic — ONE item = ONE member
- Never put methods in `properties[]`
- Never put uninitialized type declarations in `customCode[]`

### Rule 3: Use templateRefs for internal types in customCode

When customCode references a type from the same batch, use `$placeholder` syntax with `templateRefs`. This triggers automatic import resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

Critical in C#: Every internal type reference in customCode MUST use templateRefs, or `using` directives for cross-namespace types won't be generated.

### Rule 4: Never add framework imports to customImports

MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

**Auto-imported (NEVER specify in customImports):**
- TypeScript: built-ins (no imports needed at all)
- C#: `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*`
- Python: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`
- Java: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*`
- Kotlin: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`
- Go: `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, and more
- Swift: Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)
- Rust: `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde`
- Groovy: `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream)
- Scala: `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*`
- PHP: `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable`

Only use `customImports` for **external libraries** (e.g., `@angular/core`, `FluentValidation`, `rxjs`).

### Rule 5: templateRefs are ONLY for internal types

- Same MCP call type → use `typeIdentifier` or `templateRefs`
- External library type → use `customImports`
- Never mix these

### Rule 6: Constructor parameters auto-create properties (C#, Java, Go, Groovy)

In C#, Java, Go, and Groovy, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]` — causes "Sequence contains more than one matching element" errors.

```jsonc
// WRONG
"constructorParameters": [{"name": "email", "type": "string"}],
"properties": [{"name": "email", "type": "string"}]  // DUPLICATE!

// CORRECT — only in constructorParameters; additional-only fields go in properties[]
"constructorParameters": [{"name": "email", "type": "string"}]
```

### Rule 7: Virtual types don't generate files

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, and `concreteGenericInterfaces` create reusable type references only. They NEVER produce files. Reference their `typeIdentifier` in properties of file-generating types.

---

## Output Structure

Each file-generating item (`interfaces`, `classes`, `enums`, `customFiles`) produces one source file written to `outputPath / item.path / filename`. The engine:
- Resolves cross-references within the batch and generates correct import/using directives
- Handles language-specific idioms (Java ALL_CAPS enums, Python snake_case methods, TypeScript I-prefix stripping on interfaces, etc.)
- Auto-indents `\n` sequences in customCode

When `dryRun: true`, file contents are returned in the response for review (no disk writes).

When `skipExisting: true` (default), only new files are created — existing files are untouched (useful for stub pattern).

---

## Patterns and Examples

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

Reference via `"typeIdentifier": "user-list"` in properties.

### Complex type expressions with templateRefs in properties

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

### CustomFiles for type aliases and barrel exports

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

The `identifier` on the customFile enables import path resolution when referenced by other files via `customImports`.

### Interface with method signatures (for implementing classes)

Use `customCode` for interface method signatures — NOT function-typed properties. If you use function-typed properties, the implementing class will duplicate them as property declarations alongside your customCode methods.

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

---

## Language-Specific Notes

### TypeScript
- MetaEngine strips `I` prefix from interface names for the export. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control file name if collisions arise (e.g., `"fileName": "i-user-repository"`).
- Primitive mappings: `String` → `string`, `Number` → `number`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly

### C#
- `I` prefix preserved on interface names (unlike TypeScript)
- `Number` → `int` (NOT `double`). Use `"type": "decimal"` or `"type": "double"` for non-integer numbers.
- `packageName` sets the namespace. Omit for GlobalUsings pattern (no namespace declaration generated).
- Interface properties generate `{ get; }`. Class properties generate `{ get; set; }`.
- `arrayTypes` generates `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs.
- `isOptional` on properties generates nullable reference type `string?`
- Every internal type reference in customCode MUST use templateRefs or cross-namespace `using` directives won't be generated.

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode
- `typing` imports are automatic

### Go
- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode
- Constructor parameters are NOT supported in Go (Go has no constructors)

### Java
- Enum member names are automatically converted to ALL_CAPS idiom

---

## Common Mistakes and Fixes

1. **DON'T** reference a `typeIdentifier` that doesn't exist in the batch → the property is silently dropped.
   **DO** verify every `typeIdentifier` matches a defined type in the same call.

2. **DON'T** put method signatures as function-typed properties on interfaces you'll `implements`.
   **DO** use `customCode` for interface method signatures when a class will implement them.

3. **DON'T** write internal type names as raw strings in customCode (e.g., `"code": "private repo: IUserRepository"`).
   **DO** use templateRefs: `"code": "private repo: $repo"` with `"templateRefs": [{"placeholder": "$repo", "typeIdentifier": "user-repo"}]`.

4. **DON'T** use `arrayTypes` in C# when you need `List<T>`.
   **DO** use `"type": "List<$user>"` with templateRefs for mutable list types.

5. **DON'T** add `System.*`, `typing.*`, `java.util.*` etc. to `customImports`.
   **DO** let MetaEngine handle all framework imports automatically.

6. **DON'T** duplicate constructor parameter names in the `properties[]` array (C#/Java/Go/Groovy).
   **DO** put shared fields only in `constructorParameters` and additional-only fields in `properties[]`.

7. **DON'T** use reserved words (`delete`, `class`, `import`) as property names.
   **DO** use safe alternatives (`remove`, `clazz`, `importData`).

8. **DON'T** generate related types in separate MCP calls.
   **DO** batch everything in one call — cross-file imports only resolve within a single batch.

9. **DON'T** expect `Number` to map to `double` in C# — it maps to `int`.
   **DO** use `"type": "double"` or `"type": "decimal"` explicitly when needed.

10. **DON'T** forget `fileName` when both an `I`-prefixed interface and its implementing class would collide in TypeScript (MetaEngine strips the `I` from interface export names).
    **DO** set `"fileName": "i-user-repository"` on the interface to prevent file name conflicts.

11. **DON'T** put templateRefs for external library types.
    **DO** use templateRefs only for types defined in the same batch; use `customImports` for external libraries.

12. **DON'T** expect `concreteGenericClasses`, `arrayTypes`, `dictionaryTypes`, or `concreteGenericInterfaces` to produce files.
    **DO** treat them as virtual type references only — they're used in `baseClassTypeIdentifier` or `typeIdentifier` property references.

---

## When to Use load_spec_from_file vs generate_code inline

- Use `generate_code` inline for small-to-medium specs that fit comfortably in the MCP call
- Use `load_spec_from_file` for large or complex architectures: write the JSON spec to a file first, then pass the file path. This drastically reduces AI context usage — you only pass the file path in the tool call.
- The spec file format is identical to the `generate_code` input schema (same fields, same structure).
- `load_spec_from_file` accepts `outputPath`, `skipExisting`, and `dryRun` as overrides that take precedence over values in the spec file.
