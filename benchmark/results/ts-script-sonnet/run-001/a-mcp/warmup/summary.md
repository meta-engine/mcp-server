# MetaEngine MCP — Knowledge Brief

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__generate_code` | Semantic code gen from structured JSON spec (classes, interfaces, enums, etc.) |
| `mcp__metaengine__load_spec_from_file` | Same as generate_code but reads the JSON spec from a file path |
| `mcp__metaengine__generate_openapi` | HTTP client from OpenAPI (YAML/JSON) spec or URL |
| `mcp__metaengine__generate_graphql` | HTTP client from GraphQL SDL schema |
| `mcp__metaengine__generate_protobuf` | HTTP client from Protocol Buffers (.proto) definitions |
| `mcp__metaengine__generate_sql` | Typed model classes from SQL DDL (CREATE TABLE) |
| `mcp__metaengine__metaengine_initialize` | Returns documentation/patterns; call when learning or generating for the first time |

---

## generate_code — Full Input Schema

### Top-level fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `language` | enum | **yes** | — | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | no | `"."` | Directory where files are written |
| `packageName` | string | no | language-dependent | Package/module/namespace. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy default: `com.metaengine.generated`. For C#: omit for no namespace declaration (GlobalUsings pattern). |
| `initialize` | boolean | no | `false` | Initialize properties with default values |
| `skipExisting` | boolean | no | `true` | Skip writing files that already exist (stub pattern) |
| `dryRun` | boolean | no | `false` | Preview mode — returns generated code without writing to disk |
| `classes` | array | no | — | Class definitions |
| `interfaces` | array | no | — | Interface definitions |
| `enums` | array | no | — | Enum definitions |
| `customFiles` | array | no | — | Custom files (type aliases, barrel exports, utility functions) |
| `arrayTypes` | array | no | — | Virtual array type references — NO files generated |
| `dictionaryTypes` | array | no | — | Virtual dictionary type references — NO files generated |
| `concreteGenericClasses` | array | no | — | Virtual concrete generics like `Repository<User>` — NO files generated |
| `concreteGenericInterfaces` | array | no | — | Virtual concrete generic interfaces — NO files generated |

### classes[] item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Class name |
| `typeIdentifier` | string | Unique ID for cross-referencing within this batch |
| `path` | string | Subdirectory path (e.g., `"models"`, `"services/auth"`) |
| `fileName` | string | Custom file name without extension |
| `comment` | string | Documentation comment |
| `isAbstract` | boolean | Makes this an abstract class |
| `baseClassTypeIdentifier` | string | Type identifier of base class to extend |
| `interfaceTypeIdentifiers` | string[] | Array of interface identifiers to implement |
| `genericArguments` | array | Makes this a generic class template (e.g., `Repository<T>`) |
| `constructorParameters` | array | Constructor parameters — auto-become properties in TypeScript; auto-create properties in C#/Java/Go/Groovy (do NOT duplicate in `properties[]`) |
| `properties` | array | Field declarations (type only, no logic) |
| `customCode` | array | Methods and initialized fields — one item per member |
| `decorators` | array | Class-level decorators |
| `customImports` | array | External library imports only |

**genericArguments[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Generic param name (e.g., `"T"`) |
| `constraintTypeIdentifier` | string | Constraint type (e.g., `where T : BaseEntity`) |
| `propertyName` | string | Creates a property of type T with this name |
| `isArrayProperty` | boolean | If true, property is T[] |

**constructorParameters[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Parameter name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `type` | string | Raw type string for complex types |
| `typeIdentifier` | string | Reference to another generated type |

**properties[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `type` | string | Raw type string (for complex/external types) |
| `typeIdentifier` | string | Reference to another type in the same batch |
| `templateRefs` | array | `{placeholder, typeIdentifier}` — for `$placeholder` syntax in `type` field |
| `isOptional` | boolean | Nullable/optional property |
| `isInitializer` | boolean | Add default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | array | Template refs for comment placeholders |
| `decorators` | array | Property decorators (e.g., `@IsEmail()`) |

**customCode[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `code` | string | The code for exactly one member (method or initialized field) |
| `templateRefs` | array | `{placeholder: "$name", typeIdentifier: "my-type"}` — resolves internal type references and triggers import generation |

**decorators[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Decorator code (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | array | Template refs for placeholders within decorator code |

**customImports[] item:**
| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (e.g., `"@angular/core"`) or identifier of a customFile |
| `types` | string[] | Named imports (e.g., `["Injectable", "inject"]`) |

### interfaces[] item schema

Same fields as `classes[]` except: no `isAbstract`, no `baseClassTypeIdentifier` (use `interfaceTypeIdentifiers` to extend other interfaces). `customCode` is supported for method signatures.

### enums[] item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Unique ID for referencing |
| `path` | string | Subdirectory |
| `fileName` | string | Custom file name |
| `comment` | string | Documentation comment |
| `members` | array | `{name: string, value: number}` |

Enums auto-suffix filenames: `order-status.enum.ts` (TypeScript), `OrderStatus.cs` (C#), etc.

### customFiles[] item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (without extension) |
| `path` | string | Directory path |
| `fileName` | string | Override file name |
| `identifier` | string | Optional — enables other files to import this via `customImports[].path` |
| `customCode` | array | Code blocks — one per export/type alias/function |
| `customImports` | array | External imports for this file |

### arrayTypes[] item schema

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string | **required** — ID to reference this array type |
| `elementTypeIdentifier` | string | Reference to a custom type element |
| `elementPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |

**Never generates files.** Used to represent `User[]`, `string[]`, etc. as reusable virtual types. Reference by `typeIdentifier` in `properties[]`. In C# generates `IEnumerable<T>` — for `List<T>` use `"type": "List<$user>"` with templateRefs instead.

### dictionaryTypes[] item schema

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string | **required** — ID to reference |
| `keyPrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `keyType` | string | Raw string for key type |
| `keyTypeIdentifier` | string | Reference to custom key type |
| `valuePrimitiveType` | enum | `String`, `Number`, `Boolean`, `Date`, `Any` |
| `valueTypeIdentifier` | string | Reference to custom value type |

All 4 combinations (primitive/custom for key/value) are supported.

### concreteGenericClasses[] item schema

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID for this concrete type (e.g., `"user-repo-concrete"`) |
| `genericClassIdentifier` | string | References the generic class template |
| `genericArguments` | array | `{typeIdentifier, primitiveType}` — the type arguments |

Creates a virtual `Repository<User>` type. Reference via `baseClassTypeIdentifier` in a class. MetaEngine generates `extends Repository<User>` with correct imports. **No files generated.**

### concreteGenericInterfaces[] item schema

Same structure as `concreteGenericClasses` but for interfaces. `genericClassIdentifier` references a generic interface.

---

## load_spec_from_file — Input Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `specFilePath` | string | **yes** | Path to JSON spec file (absolute or relative to cwd) |
| `outputPath` | string | no | Overrides `outputPath` in the spec file |
| `skipExisting` | boolean | no | Overrides `skipExisting` in the spec file |
| `dryRun` | boolean | no | Overrides `dryRun` in the spec file |

The spec file uses the exact same JSON structure as `generate_code`. Use this to avoid context bloat for complex multi-file generations.

---

## generate_openapi — Input Schema Summary

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `framework` | enum | **yes** | `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession` |
| `openApiSpec` | string | one of | Inline OpenAPI spec (YAML or JSON) |
| `openApiSpecUrl` | string | one of | URL to fetch spec from |
| `outputPath` | string | no | Default `"."` |
| `skipExisting` | boolean | no | Default `true` |
| `dryRun` | boolean | no | Default `false` |
| `documentation` | boolean | no | Generate JSDoc/XML comments |
| `strictValidation` | boolean | no | Enable strict OpenAPI validation |
| `optionsObjectThreshold` | number | no | Min params before grouping into options object |
| `bearerAuth` | object | no | `{envVarName, headerName}` |
| `basicAuth` | object | no | `{usernameEnvVar, passwordEnvVar}` |
| `customHeaders` | array | no | `[{headerName, envVarName}]` |
| `errorHandling` | object | no | `{enabled, throwForStatusCodes, returnNullForStatusCodes}` |
| `retries` | object | no | `{maxAttempts, retryStatusCodes, baseDelaySeconds, maxDelaySeconds}` |
| `timeout` | object | no | `{seconds, connect, read, write}` |
| `angularOptions` | object | no | `{baseUrlToken, providedIn, useInjectFunction, useHttpResources, httpResourceTrigger, responseDateTransformation}` |
| `fetchOptions` | object | no | `{baseUrlEnvVar, useImportMetaEnv, useMiddleware, useResultPattern, useTypesBarrel}` |
| `reactOptions` | object | no | `{baseUrlEnvVar, useTanStackQuery, useTypesBarrel, responseDateTransformation}` |
| `goOptions` | object | no (required if go) | `{moduleName, packageName, baseUrlEnvVar, useContext, jsonLibrary}` |
| `javaSpringOptions` | object | no (required if java) | `{packageName, baseUrlProperty, beanValidation, nonNullSerialization, useComponentAnnotation}` |
| `csharpOptions` | object | no (required if csharp) | `{namespaceName}` |
| `kotlinOptions` | object | no (required if kotlin) | `{packageName}` |
| `pythonOptions` | object | no | `{baseUrlEnvVar, generateSyncMethods, useCamelCaseAliases}` |
| `rustOptions` | object | no (required if rust) | `{crateName, strictEnums}` |
| `swiftOptions` | object | no | `{strictEnums, typedThrows}` |

---

## generate_graphql — Input Schema Summary

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `framework` | enum | **yes** | `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-fastapi`, `rust-reqwest`, `swift-urlsession` |
| `graphQLSchema` | string | **yes** | GraphQL SDL schema content |
| `outputPath` | string | no | Default `"."` |
| `dryRun` | boolean | no | Default `false` |
| `skipExisting` | boolean | no | Default `true` |
| `documentation` | boolean | no | Generate docs from schema descriptions |
| `discriminatedUnions` | boolean | no | Generate discriminated unions for GraphQL union types |
| `bearerAuth` | object | no | `{enabled}` |
| `basicAuth` | object | no | `{enabled}` |
| `customHeaders` | object | no | `{headers: [{name, value}]}` |
| `errorHandling` | object | no | `{mode: "throw" | "result"}` |
| `retries` | object | no | `{maxRetries}` |
| `timeout` | object | no | `{seconds}` |
| `angularOptions` | object | no | `{baseUrlToken, providedIn, useInjectFunction}` |
| `fetchOptions` | object | no | `{baseUrlEnvVar}` |
| `reactOptions` | object | no | `{baseUrlEnvVar, useTanStackQuery}` |
| `goOptions` | object | required if go | `{moduleName, packageName}` |
| `javaSpringOptions` | object | required if java | `{packageName, beanValidation, nonNullSerialization}` |
| `csharpOptions` | object | required if csharp | `{namespaceName}` |
| `kotlinOptions` | object | required if kotlin | `{packageName}` |
| `pythonOptions` | object | no | `{baseUrlEnvVar}` |
| `rustOptions` | object | required if rust | `{crateName}` |
| `swiftOptions` | object | no | `{strictEnums, typedThrows}` |

---

## generate_protobuf — Input Schema Summary

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `framework` | enum | **yes** | `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-httpx`, `rust-reqwest`, `swift-urlsession` |
| `protoSource` | string | **yes** | Protocol Buffers (.proto) definition content |
| `outputPath` | string | no | Default `"."` |
| `dryRun` | boolean | no | Default `false` |
| `skipExisting` | boolean | no | Default `true` |
| `documentation` | boolean | no | Generate docs from proto comments |
| `bearerAuth` | object | no | `{enabled}` |
| `basicAuth` | object | no | `{enabled}` |
| `customHeaders` | object | no | `{headers: [{name, value}]}` |
| `errorHandling` | object | no | `{mode: "throw" | "result"}` |
| `retries` | object | no | `{maxRetries}` |
| `timeout` | object | no | `{seconds}` |
| Framework-specific options | — | see openapi/graphql for same pattern |

Python framework here is `python-httpx` (not fastapi, unlike openapi/graphql).
Fetch options add: `{useImportMetaEnv, useTypesBarrel}`.

---

## generate_sql — Input Schema Summary

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `language` | enum | **yes** | `typescript`, `csharp`, `go`, `python`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `ddlSource` | string | **yes** | SQL DDL (CREATE TABLE statements) |
| `outputPath` | string | no | Default `"."` |
| `dryRun` | boolean | no | Default `false` |
| `skipExisting` | boolean | no | Default `true` |
| `generateInterfaces` | boolean | no | Generate interfaces alongside model classes |
| `generateNavigationProperties` | boolean | no | Navigation props for FK relationships |
| `generateValidationAnnotations` | boolean | no | Validation annotations from column constraints |
| `initializeProperties` | boolean | no | Initialize properties with default values |
| `csharpOptions` | object | no | `{namespace}` |
| `goOptions` | object | required if go | `{moduleName}` |
| `javaOptions` | object | required if java | `{packageName}` |
| `kotlinOptions` | object | required if kotlin | `{packageName}` |
| `groovyOptions` | object | required if groovy | `{packageName}` |
| `scalaOptions` | object | required if scala | `{packageName}` |
| `phpOptions` | object | required if php | `{rootNamespace, useStrictTypes}` |
| `pythonOptions` | object | no | `{modelStyle: "dataclass" | "pydantic" | "plain"}` |
| `rustOptions` | object | no | `{crateName}` |

---

## Critical Rules (must not violate)

### 1. ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks the type graph and imports.

### 2. properties[] = type declarations only; customCode[] = everything with logic
- `properties[]`: field with type, no initialization, no methods
- `customCode[]`: methods, initialized fields — one item = exactly one member
- **Never** put methods in `properties[]`. **Never** put uninitialized type declarations in `customCode[]`.

### 3. Use templateRefs for internal types in customCode
When `customCode` references a type from the same batch, use `$placeholder` syntax with `templateRefs`:
```json
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```
Without `templateRefs`, MetaEngine cannot generate the import. This is **critical in C#**: every internal type reference in `customCode` MUST use `templateRefs`, or `using` directives for cross-namespace types won't be generated.

### 4. Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

| Language | Auto-imported (never specify) |
|----------|------------------------------|
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, and more |
| Swift | Foundation (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`, etc.) |
| Rust | `std::collections` (`HashMap`, `HashSet`), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream) |
| Scala | `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | No imports needed — built-in types |

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### 5. templateRefs are ONLY for internal types
External library types → `customImports`. Same MCP call types → `typeIdentifier` or `templateRefs`. Never mix.

### 6. Constructor parameters auto-create properties (C#, Java, Go, Groovy)
Do NOT duplicate constructor parameters in `properties[]` — causes "Sequence contains more than one matching element" errors. Put shared fields only in `constructorParameters`, additional-only fields in `properties[]`.

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references ONLY. They produce no source files. Use their `typeIdentifier`/`identifier` in properties of file-generating types.

### 8. Interface method signatures go in customCode, not properties
For interfaces that will be `implements`/`:` by a class, define method signatures in `customCode`, not as function-typed properties. Function-typed properties cause the implementing class to duplicate them as property declarations alongside customCode methods.

---

## Primitive Type Mappings

| MetaEngine | TypeScript | C# | Python | Go | Java |
|-----------|-----------|-----|--------|-----|------|
| `String` | `string` | `string` | `str` | `string` | `String` |
| `Number` | `number` | `int` (NOT double!) | `int` | `int` | `int` |
| `Boolean` | `boolean` | `bool` | `bool` | `bool` | `boolean` |
| `Date` | `Date` | `DateTime` | `datetime` | `time.Time` | `LocalDateTime` |
| `Any` | `unknown` | `object` | `Any` | `interface{}` | `Object` |

**C# critical**: `Number` → `int`, not `double`. Use `"type": "decimal"` or `"type": "double"` explicitly.

---

## Output Structure

For each generated type, MetaEngine writes one file. File naming conventions:
- **TypeScript**: kebab-case with suffix. `UserService` → `user-service.ts`. Enums: `order-status.enum.ts`. Interfaces: `I` prefix stripped — `IUserRepository` → file `user-repository.ts` (use `fileName: "i-user-repository"` to avoid collision with implementing class).
- **C#**: PascalCase, one class per file.
- **Python**: snake_case filenames.
- **Java/Kotlin**: PascalCase.
- **Go**: snake_case, package determined by `packageName`.

The engine generates correct imports/using directives for all cross-references automatically.

---

## Key Patterns

### Basic cross-referencing
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

### Enum + class using it
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

### Array/dictionary virtual types
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
Reference via `"typeIdentifier": "user-list"` in any property.

### Complex type with templateRefs in property
```json
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
`templateRefs` work in `properties`, `customCode`, and `decorators`.

### Angular service with DI
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
  }]
}
```

### Custom files (type aliases, barrel exports)
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
The `identifier` on customFile enables import resolution — `customImports[].path` set to that identifier auto-resolves to the relative path.

### Interface with method signatures (implement correctly)
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

---

## Language-Specific Notes

### TypeScript
- MetaEngine strips `I` prefix from interface names in the generated export. `IUserRepository` → exported as `UserRepository`. Use `fileName: "i-user-repository"` to control file name and avoid collisions with implementing classes.
- Primitive mappings: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- Auto-indents `customCode` newlines (`\n`).
- Decorators supported directly.
- Constructor parameters auto-become properties.

### C#
- `I` prefix preserved on interface names.
- `Number` → `int` (NOT `double`). Use `"type": "decimal"` or `"type": "double"` for non-integers.
- `packageName` sets the namespace. Omit for GlobalUsings pattern (no namespace declaration).
- Interface properties generate `{ get; }`. Class properties generate `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>` use `"type": "List<$user>"` with templateRefs.
- `isOptional` generates `string?` (nullable reference types).
- Constructor parameters auto-create properties — do NOT duplicate in `properties[]`.

### Python
- Must provide explicit 4-space indentation after `\n` in `customCode`.
- `typing` imports are automatic.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions in `customCode`.
- Constructor parameters auto-create properties — do NOT duplicate.

### Java / Kotlin / Groovy
- Constructor parameters auto-create properties — do NOT duplicate.
- Java enum members are transformed to `ALL_CAPS` automatically.

---

## Common Mistakes (top 10)

1. **Referencing a typeIdentifier that doesn't exist in the batch** → property silently dropped. Verify every typeIdentifier matches a defined type in the same call.
2. **Method signatures as function-typed properties on interfaces** → implementing class duplicates them. Use `customCode` for interface method signatures.
3. **Internal type names as raw strings in customCode** (e.g., `"private repo: IUserRepository"`) → import not generated. Use templateRefs: `"private repo: $repo"`.
4. **Using `arrayTypes` in C# when you need `List<T>`** → generates `IEnumerable<T>`. Use `"type": "List<$user>"` with templateRefs.
5. **Adding `System.*`, `typing.*`, `java.util.*` etc. to `customImports`** → duplication/errors. Let MetaEngine handle framework imports.
6. **Duplicating constructor parameter names in `properties[]`** (C#/Java/Go/Groovy) → "Sequence contains more than one matching element" error.
7. **Using reserved words as property names** (`delete`, `class`, `import`) → use safe alternatives (`remove`, `clazz`, `importData`).
8. **Generating related types in separate MCP calls** → cross-file imports don't resolve. Batch everything in one call.
9. **Expecting `Number` → `double` in C#** → it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.
10. **Forgetting `fileName` when an `I`-prefixed interface and its implementing class would collide in TypeScript** → set `"fileName": "i-user-repository"` on the interface.

---

## Script-based Generation Pattern (for this benchmark)

When using `load_spec_from_file`:
1. Write the JSON spec to a `.json` file (e.g., `spec.json`) with the full `generate_code` structure.
2. Call `mcp__metaengine__load_spec_from_file` with `specFilePath` pointing to that file.
3. Optionally override `outputPath`, `skipExisting`, or `dryRun`.

This avoids passing large JSON inline and reduces AI context usage significantly.

---

## Summary Decision Tree

- Generating TypeScript/Python/Go/C#/Java/Kotlin/Groovy/Scala/Swift/PHP/Rust types → `generate_code` or `load_spec_from_file`
- Have an OpenAPI spec (YAML/JSON) → `generate_openapi`
- Have a GraphQL SDL → `generate_graphql`
- Have a .proto file → `generate_protobuf`
- Have SQL DDL tables → `generate_sql`
- Complex spec, want to version-control it → write JSON file + `load_spec_from_file`
- Unknown about usage patterns → call `metaengine_initialize` first
