# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a **semantic code generation system** exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files. It resolves cross-references, manages imports, and handles language idioms automatically. One well-formed JSON call replaces dozens of error-prone file writes.

**Supported languages**: TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust

---

## Tools Exposed

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__metaengine_initialize` | Returns essential patterns and docs. Call first for guidance. |
| `mcp__metaengine__generate_code` | Main tool: generates source files from JSON spec. |
| `mcp__metaengine__load_spec_from_file` | Loads a JSON spec from disk and generates (same as generate_code but from file). |
| `mcp__metaengine__generate_openapi` | Generates HTTP clients from OpenAPI specs (YAML/JSON inline or URL). |
| `mcp__metaengine__generate_graphql` | Generates typed HTTP clients from GraphQL SDL schemas. |
| `mcp__metaengine__generate_protobuf` | Generates typed HTTP clients from .proto definitions. |
| `mcp__metaengine__generate_sql` | Generates typed model classes from SQL DDL (CREATE TABLE statements). |

---

## generate_code — Complete Input Schema

### Top-level parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `language` | enum | **YES** | — | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | no | `"."` | Directory where files are written |
| `packageName` | string | no | language-dependent | Package/module/namespace. For C# omit for GlobalUsings pattern. Go defaults to `github.com/metaengine/demo`, Java/Kotlin/Groovy to `com.metaengine.generated`. |
| `initialize` | boolean | no | `false` | Initialize properties with default values |
| `skipExisting` | boolean | no | `true` | Skip writing files that already exist |
| `dryRun` | boolean | no | `false` | Preview mode — returns generated code without writing files |
| `classes` | array | no | — | Class definitions |
| `interfaces` | array | no | — | Interface definitions |
| `enums` | array | no | — | Enum definitions |
| `arrayTypes` | array | no | — | Virtual array type refs (no files generated) |
| `dictionaryTypes` | array | no | — | Virtual dictionary type refs (no files generated) |
| `concreteGenericClasses` | array | no | — | Virtual concrete generic class refs (no files generated) |
| `concreteGenericInterfaces` | array | no | — | Virtual concrete generic interface refs (no files generated) |
| `customFiles` | array | no | — | Files without class wrapper (barrel exports, type aliases, utilities) |

---

### classes[] item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Class name |
| `typeIdentifier` | string | Unique identifier for cross-references within this batch |
| `path` | string | Directory path (e.g., `"models"`, `"services/auth"`) |
| `fileName` | string | Custom file name without extension |
| `isAbstract` | boolean | Mark class as abstract |
| `comment` | string | Documentation comment |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class to extend |
| `interfaceTypeIdentifiers` | string[] | Array of interface typeIdentifiers to implement |
| `genericArguments` | array | Makes this a generic class template (see below) |
| `constructorParameters` | array | Constructor params (auto-become properties in TS; in C#/Java/Go/Groovy also auto-create props — do NOT duplicate in `properties[]`) |
| `properties` | array | Type declarations only (no logic, no initialization unless `isInitializer`) |
| `customCode` | array | Methods, initialized fields, any code with logic — ONE item per member |
| `customImports` | array | External library imports only (never framework/stdlib) |
| `decorators` | array | Class-level decorators |

**genericArguments[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Generic param name (e.g., `"T"`) |
| `constraintTypeIdentifier` | string | typeIdentifier for generic constraint (e.g., `where T : BaseEntity`) |
| `propertyName` | string | Creates a property of type T with this name |
| `isArrayProperty` | boolean | If true, property type is T[] |

**constructorParameters[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Parameter name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `type` | string | Complex type expression |
| `typeIdentifier` | string | Reference to another type in this batch |

**properties[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `typeIdentifier` | string | Reference to another type in this batch |
| `type` | string | Complex type expression (e.g., `"Map<string, $resp>"`) |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` for import resolution in `type` |
| `isOptional` | boolean | Marks field optional (generates `?` in TS, `?` nullable in C#) |
| `isInitializer` | boolean | Add default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | array | Template refs inside comment |
| `decorators` | array | Property-level decorators `[{code, templateRefs}]` |

**customCode[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `code` | string | The method/field code. Use `$placeholder` for internal type refs. Use `\n` for newlines (auto-indented). |
| `templateRefs` | array | `[{placeholder: "$foo", typeIdentifier: "foo"}]` triggers import resolution |

**customImports[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (e.g., `"@angular/core"`, `"rxjs"`) |
| `types` | string[] | Named types to import from that path |

**decorators[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Decorator code (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | array | Template refs for import resolution inside decorator |

---

### interfaces[] item schema

Same fields as `classes[]` minus `isAbstract`, `baseClassTypeIdentifier`, `constructorParameters`, `genericArguments`. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Interface name |
| `typeIdentifier` | string | Unique cross-ref identifier |
| `path` | string | Directory path |
| `fileName` | string | Custom file name without extension |
| `comment` | string | Documentation comment |
| `interfaceTypeIdentifiers` | string[] | Extend other interfaces |
| `genericArguments` | array | Makes this a generic interface template |
| `properties` | array | Property signatures |
| `customCode` | array | Method signatures (preferred over function-typed properties when a class will implement) |
| `customImports` | array | External imports |
| `decorators` | array | Decorators |

---

### enums[] item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Cross-ref identifier |
| `path` | string | Directory path |
| `fileName` | string | Custom file name |
| `comment` | string | Documentation comment |
| `members` | array | `[{name: string, value: number}]` |

Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

---

### arrayTypes[] item schema (virtual — NO files generated)

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string | **Required.** Identifier for referencing |
| `elementTypeIdentifier` | string | Custom element type reference |
| `elementPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |

**C# note**: arrayTypes generate `IEnumerable<T>`. For `List<T>` use `"type": "List<$user>"` with templateRefs instead.

---

### dictionaryTypes[] item schema (virtual — NO files generated)

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string | **Required.** Identifier for referencing |
| `keyPrimitiveType` | enum | Primitive key type |
| `keyType` | string | String literal key type (e.g., `"string"`) |
| `keyTypeIdentifier` | string | Custom key type reference |
| `valuePrimitiveType` | enum | Primitive value type |
| `valueTypeIdentifier` | string | Custom value type reference |

Supports all 4 combinations of primitive/custom for key/value.

---

### concreteGenericClasses[] item schema (virtual — NO files generated)

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | Identifier for this concrete implementation |
| `genericClassIdentifier` | string | References the generic class definition |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` |

Usage: class sets `baseClassTypeIdentifier` to this `identifier`. MetaEngine generates `extends Repository<User>` with correct imports.

---

### concreteGenericInterfaces[] item schema (virtual — NO files generated)

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | Identifier for this concrete interface implementation |
| `genericClassIdentifier` | string | References the generic interface definition |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` |

---

### customFiles[] item schema (generates files WITHOUT class wrapper)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (without extension) |
| `fileName` | string | Custom file name override without extension |
| `path` | string | Directory path |
| `identifier` | string | Optional. Enables import resolution — other files can reference via `customImports[].path` |
| `customCode` | array | Code blocks — one per export/type alias/function |
| `customImports` | array | External imports |

---

## load_spec_from_file — Input Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `specFilePath` | string | **YES** | Path to JSON spec file (absolute or relative). Same JSON structure as generate_code. |
| `outputPath` | string | no | Overrides outputPath in spec file |
| `skipExisting` | boolean | no | Overrides skipExisting in spec file |
| `dryRun` | boolean | no | Overrides dryRun in spec file |

Benefit: drastically reduces AI context usage for complex architectures. Use for large specs or reusable templates.

---

## generate_openapi — Input Schema Summary

Generates HTTP clients from OpenAPI specs (YAML/JSON). Either `openApiSpec` (inline) or `openApiSpecUrl` is required.

**Supported frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession`

**Key fields**:
- `framework` (required): target framework
- `openApiSpec`: inline YAML/JSON content
- `openApiSpecUrl`: URL to fetch spec from
- `outputPath` (default `"."`): output directory
- `dryRun` / `skipExisting`: standard flags
- `documentation`: generate JSDoc/XML doc comments
- `bearerAuth`: `{envVarName, headerName}` — bearer token auth
- `basicAuth`: `{usernameEnvVar, passwordEnvVar}` — basic auth
- `customHeaders`: `[{headerName, envVarName}]` — custom HTTP headers
- `errorHandling`: `{enabled, throwForStatusCodes[], returnNullForStatusCodes[]}`
- `retries`: `{maxAttempts, baseDelaySeconds, maxDelaySeconds, retryStatusCodes[]}`
- `timeout`: `{seconds, connect, read, write}`
- `optionsObjectThreshold`: min params before grouping into options object
- `strictValidation`: enable strict OpenAPI spec validation

**Framework-specific options**:
- `angularOptions`: `{providedIn, baseUrlToken, useInjectFunction, useHttpResources, httpResourceTrigger, responseDateTransformation}`
- `reactOptions`: `{baseUrlEnvVar, useTanStackQuery, useTypesBarrel, responseDateTransformation}`
- `fetchOptions`: `{baseUrlEnvVar, useImportMetaEnv, useMiddleware, useResultPattern, useTypesBarrel}`
- `goOptions` (requires `moduleName`, `packageName`): `{baseUrlEnvVar, jsonLibrary, useContext}`
- `javaSpringOptions` (requires `packageName`): `{baseUrlProperty, beanValidation, nonNullSerialization, useComponentAnnotation}`
- `kotlinOptions` (requires `packageName`): `{packageName}`
- `pythonOptions`: `{baseUrlEnvVar, generateSyncMethods, useCamelCaseAliases}`
- `csharpOptions` (requires `namespaceName`): `{namespaceName}`
- `rustOptions` (requires `crateName`): `{crateName, strictEnums}`
- `swiftOptions`: `{strictEnums, typedThrows}`

---

## generate_graphql — Input Schema Summary

Generates typed HTTP clients from GraphQL SDL schema content.

**Supported frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-fastapi`, `rust-reqwest`, `swift-urlsession`

**Key fields**:
- `framework` (required): target framework
- `graphQLSchema` (required): GraphQL SDL schema content as string
- `outputPath` (default `"."`): output directory
- `dryRun` / `skipExisting`: standard flags
- `documentation`: generate doc comments from schema descriptions
- `discriminatedUnions`: generate discriminated unions for GraphQL union types
- `bearerAuth`: `{enabled}`
- `basicAuth`: `{enabled}`
- `customHeaders`: `{headers: [{name, value}]}`
- `errorHandling`: `{mode: "throw" | "result"}`
- `retries`: `{maxRetries}`
- `timeout`: `{seconds}`
- Framework-specific options same pattern as generate_openapi (angularOptions, reactOptions, fetchOptions, goOptions, javaSpringOptions, kotlinOptions, pythonOptions, csharpOptions, rustOptions, swiftOptions)

---

## generate_protobuf — Input Schema Summary

Generates typed HTTP clients from .proto definitions.

**Supported frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-httpx`, `rust-reqwest`, `swift-urlsession`

**Key fields**:
- `framework` (required): target framework
- `protoSource` (required): .proto definition content as string
- `outputPath` (default `"."`): output directory
- `dryRun` / `skipExisting`: standard flags
- `documentation`: generate doc comments from proto comments
- `bearerAuth`: `{enabled}`
- `basicAuth`: `{enabled}`
- `customHeaders`: `{headers: [{name, value}]}`
- `errorHandling`: `{mode: "throw" | "result"}`
- `retries`: `{maxRetries}`
- `timeout`: `{seconds}`
- Framework-specific options same pattern as others
- `fetchOptions` includes `useImportMetaEnv`, `useTypesBarrel`
- `reactOptions` includes `baseUrlEnvVar`, `useTanStackQuery`, `useTypesBarrel`
- Python framework is `python-httpx` (not `python-fastapi` as in openapi/graphql)

---

## generate_sql — Input Schema Summary

Generates typed model classes from SQL DDL (CREATE TABLE statements).

**Supported languages**: `typescript`, `csharp`, `go`, `python`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`

**Key fields**:
- `language` (required): target language
- `ddlSource` (required): SQL DDL content (CREATE TABLE statements)
- `outputPath` (default `"."`): output directory
- `dryRun` / `skipExisting`: standard flags
- `generateInterfaces`: generate interfaces alongside model classes
- `generateNavigationProperties`: generate navigation props for FK relationships
- `generateValidationAnnotations`: generate validation annotations from column constraints
- `initializeProperties`: initialize model properties with default values
- Language-specific required options:
  - `csharpOptions`: `{namespace}`
  - `goOptions` (requires `moduleName`): `{moduleName}`
  - `javaOptions` (requires `packageName`): `{packageName}`
  - `kotlinOptions` (requires `packageName`): `{packageName}`
  - `groovyOptions` (requires `packageName`): `{packageName}`
  - `scalaOptions` (requires `packageName`): `{packageName}`
  - `phpOptions` (requires `rootNamespace`): `{rootNamespace, useStrictTypes}`
  - `pythonOptions`: `{modelStyle: "dataclass" | "pydantic" | "plain"}`
  - `rustOptions`: `{crateName}`

---

## Critical Rules (must not violate)

### Rule 1: ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, BOTH must be in the same `generate_code` call. Splitting calls breaks cross-references — imports won't be generated.

### Rule 2: properties[] vs customCode[]
- `properties[]` = **type declarations only** (name + type, no logic, no initialization unless `isInitializer: true`)
- `customCode[]` = **everything else**: methods, initialized fields, any code with logic
- One `customCode` item = exactly ONE member
- **Never put methods in properties. Never put uninitialized type declarations in customCode.**

### Rule 3: templateRefs for internal types in customCode
When `customCode` references a type from the same batch, use `$placeholder` syntax with `templateRefs`. This is what triggers automatic import resolution.

```json
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

Without templateRefs, no import is generated. **C# critical**: every internal type in customCode MUST use templateRefs or cross-namespace `using` directives won't be generated → compile failure.

### Rule 4: Never add framework imports to customImports
MetaEngine auto-imports stdlib/framework types. Adding them manually causes duplication.

**Auto-imported (never specify in customImports)**:
- **C#**: `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*`
- **Python**: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`
- **Java**: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, jackson.*
- **Kotlin**: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`
- **Go**: `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, and more
- **Swift**: Foundation (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`, etc.)
- **Rust**: `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde`
- **Groovy**: `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream)
- **Scala**: `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*`
- **PHP**: `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable`
- **TypeScript**: no imports needed — built-in types

Only use `customImports` for **external libraries** (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5: templateRefs are ONLY for internal types
- Same-batch type → use `typeIdentifier` or `templateRefs`
- External library type → use `customImports`
- Never mix these two mechanisms.

### Rule 6: Constructor parameters auto-create properties (C#, Java, Go, Groovy)
In these languages, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]` — causes "Sequence contains more than one matching element" error.

```json
// CORRECT for C#/Java/Go/Groovy
"constructorParameters": [{"name": "email", "primitiveType": "String"}]
// Additional non-constructor properties only:
"properties": [{"name": "createdAt", "primitiveType": "Date"}]
```

In **TypeScript**, constructor parameters also auto-become properties.

### Rule 7: Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create **reusable type references only** — they never produce files. Reference their `typeIdentifier` from properties/customCode of file-generating types.

---

## Output Structure

MetaEngine writes one file per class/interface/enum/customFile. Files are placed at `outputPath/[path]/[name].[ext]`:
- TypeScript: `user.ts`, `user.service.ts`, `order-status.enum.ts`
- C#: `User.cs`, `IUserRepository.cs`, `OrderStatus.cs`
- Python: `user.py`, `order_status.py`
- Go: `user.go`

All cross-file imports are generated automatically. No manual import management needed.

When `dryRun: true`, file contents are returned in the response for review without writing to disk.

---

## TypeScript-Specific Notes

- MetaEngine strips `I` prefix from interface names for the exported symbol: `IUserRepository` → exported as `UserRepository`. Use `fileName: "i-user-repository"` to control the file name and prevent collisions with implementing classes.
- Primitive type mapping: `String` → `string`, `Number` → `number`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly
- No imports needed for built-in types

---

## C#-Specific Notes

- `I` prefix preserved on interface names
- `Number` → `int` (not `double`). Use `"type": "decimal"` or `"type": "double"` for non-integer numbers.
- `packageName` sets the namespace. Omit for GlobalUsings pattern.
- Interface properties generate `{ get; }`. Class properties generate `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs.
- `isOptional` on properties generates `string?` (nullable reference type)
- Every internal type in customCode MUST use templateRefs (critical for cross-namespace using directives)

---

## Python-Specific Notes

- Must provide explicit indentation (4 spaces) after `\n` in customCode
- typing imports are automatic

---

## Go-Specific Notes

- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode
- Constructor parameters still supported for struct field generation

---

## Java/Kotlin/Groovy-Specific Notes

- `ALL_CAPS` enum members auto-generated (language-idiomatic transformation)
- Constructor parameters auto-create properties — do NOT duplicate in `properties[]`

---

## Common Mistakes (top 10)

1. **Referencing a typeIdentifier that doesn't exist in the batch** → property silently dropped. Verify every typeIdentifier matches a defined type in the same call.

2. **Method signatures as function-typed properties on interfaces** → implementing class duplicates them. Use `customCode` for interface method signatures when a class will implement them.

3. **Raw internal type strings in customCode** (e.g., `"code": "private repo: IUserRepository"`) → no import generated. Use templateRefs: `"code": "private repo: $repo"` with `templateRefs: [{placeholder: "$repo", typeIdentifier: "user-repo"}]`.

4. **Using `arrayTypes` in C# when you need `List<T>`** → generates `IEnumerable<T>` instead. Use `"type": "List<$user>"` with templateRefs.

5. **Adding `System.*`, `typing.*`, `java.util.*` etc. to customImports** → duplication/errors. Let MetaEngine handle stdlib imports automatically.

6. **Duplicating constructor parameter names in `properties[]`** (C#/Java/Go/Groovy) → "Sequence contains more than one matching element" error. Constructor params auto-create properties.

7. **Using reserved words as property names** (`delete`, `class`, `import`) → compile errors. Use safe alternatives (`remove`, `clazz`, `importData`).

8. **Generating related types in separate MCP calls** → cross-file imports only resolve within a single batch. Batch everything in one call.

9. **Expecting `Number` to map to `double` in C#** → it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.

10. **Forgetting `fileName` when both an `I`-prefixed interface and its implementing class would collide in TypeScript** → set `"fileName": "i-user-repository"` on the interface.

---

## Patterns Reference

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

### Class with inheritance and methods
```json
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
```json
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
```json
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

### Complex type expressions with templateRefs in properties
```json
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
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

### Angular service with DI
```json
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

### Interface with method signatures (TypeScript/C#)
Use `customCode` for interface method signatures when a class will implement, NOT function-typed properties:
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

If you use function-typed properties instead, the implementing class will duplicate them as property declarations alongside your customCode methods.

---

## Primitive Type Mapping Reference

| Schema primitive | TypeScript | C# | Python | Go | Java | Kotlin |
|---|---|---|---|---|---|---|
| `String` | `string` | `string` | `str` | `string` | `String` | `String` |
| `Number` | `number` | `int` | `int` | `int` | `int` | `Int` |
| `Boolean` | `boolean` | `bool` | `bool` | `bool` | `boolean` | `Boolean` |
| `Date` | `Date` | `DateTime` | `datetime` | `time.Time` | `LocalDateTime` | `LocalDateTime` |
| `Any` | `unknown` | `object` | `Any` | `interface{}` | `Object` | `Any` |

**C# number caveat**: `Number` → `int`. Use `"type": "double"` or `"type": "decimal"` for non-integers.

---

## load_spec_from_file Usage Pattern

Create a JSON file with the same structure as `generate_code` input:
```json
{
  "language": "typescript",
  "outputPath": "src",
  "classes": [...],
  "interfaces": [...]
}
```

Then call:
```
load_spec_from_file({
  "specFilePath": "specs/user-system.json",
  "outputPath": "src"  // optional override
})
```

Use this for complex architectures to avoid context bloat. The spec file is version-controllable and reusable.
