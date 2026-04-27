# MetaEngine MCP — Knowledge Brief

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__generate_code` | Main code generator — classes, interfaces, enums, etc. from structured JSON |
| `mcp__metaengine__load_spec_from_file` | Load a JSON spec from disk and run it — reduces context overhead for complex specs |
| `mcp__metaengine__generate_openapi` | Generate typed HTTP client from OpenAPI spec (YAML/JSON or URL) |
| `mcp__metaengine__generate_graphql` | Generate typed HTTP client from GraphQL SDL schema |
| `mcp__metaengine__generate_protobuf` | Generate typed HTTP client from Protocol Buffers (.proto) definitions |
| `mcp__metaengine__generate_sql` | Generate typed model classes from SQL DDL (CREATE TABLE statements) |
| `mcp__metaengine__metaengine_initialize` | Returns documentation + patterns. Call when starting or unsure. |

---

## generate_code — Full Input Schema

### Top-Level Parameters

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| `language` | enum | YES | — | `"typescript"`, `"python"`, `"go"`, `"csharp"`, `"java"`, `"kotlin"`, `"groovy"`, `"scala"`, `"swift"`, `"php"`, `"rust"` |
| `outputPath` | string | no | `"."` | Output directory where files are written |
| `packageName` | string | no | lang-defaults | Package/module/namespace name. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy default: `com.metaengine.generated`. C#: omit/empty = no namespace declaration (GlobalUsings pattern) |
| `initialize` | boolean | no | `false` | Initialize all properties with default values |
| `skipExisting` | boolean | no | `true` | Skip writing files that already exist (stub pattern) |
| `dryRun` | boolean | no | `false` | Preview mode — returns generated code without writing to disk |
| `classes` | array | no | — | Class definitions |
| `interfaces` | array | no | — | Interface definitions |
| `enums` | array | no | — | Enum definitions |
| `customFiles` | array | no | — | Custom files without class wrapper (type aliases, barrel exports) |
| `arrayTypes` | array | no | — | Virtual array type references (NO files generated) |
| `dictionaryTypes` | array | no | — | Virtual dictionary type references (NO files generated) |
| `concreteGenericClasses` | array | no | — | Concrete generic class instances e.g. `Repository<User>` (NO files generated) |
| `concreteGenericInterfaces` | array | no | — | Concrete generic interface instances (NO files generated) |

### classes[] Item Schema

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Class name |
| `typeIdentifier` | string | Unique ID for cross-referencing in same batch |
| `path` | string | Directory path, e.g. `"models"`, `"services/auth"` |
| `fileName` | string | Custom file name without extension |
| `comment` | string | Documentation comment for the class |
| `isAbstract` | boolean | Whether this is an abstract class |
| `baseClassTypeIdentifier` | string | typeIdentifier of the base class to extend |
| `interfaceTypeIdentifiers` | string[] | Array of interface typeIdentifiers to implement |
| `genericArguments` | array | Makes this a generic class template (see below) |
| `constructorParameters` | array | Constructor params — auto-become properties in TypeScript; auto-create properties in C#/Java/Go/Groovy |
| `properties` | array | Field declarations with type only (no logic) |
| `customCode` | array | Methods and initialized fields — one item per member |
| `decorators` | array | Class-level decorators e.g. `@Injectable(...)` |
| `customImports` | array | External library imports only |

**constructorParameters[] item:**
```jsonc
{"name": "email", "primitiveType": "String"}      // primitiveType or
{"name": "repo", "typeIdentifier": "user-repo"}   // typeIdentifier or
{"name": "value", "type": "SomeExternalType"}      // raw type string
```

**properties[] item:**
```jsonc
{
  "name": "id",
  "primitiveType": "String",     // OR typeIdentifier OR type (pick one)
  "typeIdentifier": "user",      // reference to another type in same batch
  "type": "Map<string, string>", // complex/external type as raw string
  "templateRefs": [...],         // if "type" string contains $placeholders
  "isOptional": true,            // generates nullable/optional syntax
  "isInitializer": true,         // add default value initialization
  "comment": "...",              // doc comment
  "decorators": [{"code": "@IsEmail()"}]
}
```

**customCode[] item:**
```jsonc
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

**decorators[] item:**
```jsonc
{
  "code": "@Injectable({ providedIn: 'root' })",
  "templateRefs": []   // optional
}
```

**customImports[] item:**
```jsonc
{"path": "@angular/core", "types": ["Injectable", "inject"]}
```

**genericArguments[] item (on a class definition):**
```jsonc
{
  "name": "T",                                    // Generic param name
  "constraintTypeIdentifier": "base-entity",      // where T : BaseEntity
  "propertyName": "items",                        // Creates property named 'items' of type T
  "isArrayProperty": true                         // Property is T[] instead of T
}
```

### interfaces[] Item Schema

Same fields as classes, minus `isAbstract`, `baseClassTypeIdentifier`, `constructorParameters`. Additional field:
- `interfaceTypeIdentifiers`: extend other interfaces

### enums[] Item Schema

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "path": "models",
  "fileName": "order-status",    // optional custom file name
  "comment": "...",
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2}
  ]
}
```

Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#), `OrderStatus.java` (Java).

Language idioms: Java uses `ALL_CAPS` enum members; Python uses `UPPER_SNAKE_CASE`. Judge has tolerance for these transformations.

### customFiles[] Item Schema

For utility files, type aliases, barrel exports — generates a file WITHOUT a class wrapper.

```jsonc
{
  "name": "types",              // file name (without extension)
  "fileName": "types",          // optional override
  "path": "shared",
  "identifier": "shared-types", // enables import resolution from other files
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"}
  ],
  "customImports": [...]
}
```

Other files can reference via `customImports: [{"path": "shared-types"}]` — auto-resolves to relative path.

### arrayTypes[] Item Schema

**Creates a reusable type reference only — no file generated.**

```jsonc
{
  "typeIdentifier": "user-list",          // reference this ID elsewhere
  "elementTypeIdentifier": "user",        // custom type element
  // OR
  "elementPrimitiveType": "String"        // primitive element: String|Number|Boolean|Date|Any
}
```

### dictionaryTypes[] Item Schema

**Creates a reusable type reference only — no file generated.**

```jsonc
{
  "typeIdentifier": "scores",
  "keyPrimitiveType": "String",           // key as primitive
  "keyTypeIdentifier": "...",             // OR key as custom type
  "keyType": "string",                    // OR key as raw string literal
  "valuePrimitiveType": "Number",         // value as primitive
  "valueTypeIdentifier": "..."            // OR value as custom type
}
```

### concreteGenericClasses[] Item Schema

**Creates a concrete instantiation of a generic class — no file generated.**

```jsonc
{
  "identifier": "user-repo-concrete",          // used in baseClassTypeIdentifier
  "genericClassIdentifier": "repo-generic",    // references the generic class
  "genericArguments": [
    {"typeIdentifier": "user"}                 // OR "primitiveType": "String"
  ]
}
```

### concreteGenericInterfaces[] Item Schema

Same structure as concreteGenericClasses but for interfaces.

---

## Critical Rules (Failures Happen When Violated)

### Rule 1: ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, BOTH must be in the same `generate_code` call. Never split related types across calls.

### Rule 2: properties[] = type declarations only; customCode[] = everything else
- `properties[]`: fields with type declarations only — no initialization, no logic
- `customCode[]`: methods, initialized fields, anything with logic — exactly ONE member per item
- **Never put methods in properties. Never put uninitialized type declarations in customCode.**

### Rule 3: Use templateRefs for internal types in customCode
When customCode references a type from the same batch, use `$placeholder` syntax + `templateRefs`. Without this, MetaEngine cannot generate the import/using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**Critical in C#**: Every internal type reference in customCode MUST use templateRefs or `using` directives for cross-namespace types won't be generated.

templateRefs also work in `properties[].type` and `decorators[].code` with the same `$placeholder` pattern.

### Rule 4: Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

| Language | Auto-imported (NEVER specify manually) |
|----------|----------------------------------------|
| C# | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.) |
| Rust | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy | java.time.*, java.math.*, java.util (UUID, Date), java.io |
| Scala | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |
| TypeScript | (no imports needed — built-in types) |

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5: templateRefs are ONLY for internal types (same batch)
- Same batch type → use `typeIdentifier` or `templateRefs`
- External library → use `customImports`
- Never mix these.

### Rule 6: Constructor parameters auto-create properties (C#, Java, Go, Groovy)
Do NOT duplicate constructor parameter names in `properties[]` — this causes "Sequence contains more than one matching element" errors. Only put additional non-constructor properties in `properties[]`.

### Rule 7: Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references ONLY. They never produce files. Reference their `typeIdentifier` in properties of file-generating types.

---

## Primitive Type Mapping

| MetaEngine primitive | TS | C# | Python | Java | Go |
|---------------------|----|----|--------|------|----|
| `String` | `string` | `string` | `str` | `String` | `string` |
| `Number` | `number` | `int` (NOT double!) | `int` | `Integer` | `int` |
| `Boolean` | `boolean` | `bool` | `bool` | `Boolean` | `bool` |
| `Date` | `Date` | `DateTime` | `datetime` | `LocalDateTime` | `time.Time` |
| `Any` | `unknown` | `object` | `Any` | `Object` | `interface{}` |

**C# gotcha**: `Number` maps to `int`, not `double`. Use `"type": "double"` or `"type": "decimal"` explicitly for non-integer numbers.

---

## Output Structure

- Each class/interface/enum → one file
- File naming follows language conventions (e.g. `user.ts`, `User.cs`, `User.java`)
- Enums auto-suffix: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#)
- TypeScript: strips `I` prefix from interface names for the export. `IUserRepository` → exported as `UserRepository`. Use `fileName: "i-user-repository"` to control file name and prevent collisions.
- Imports between files in the same batch are resolved automatically
- `path` field controls subdirectory placement

---

## Pattern Reference

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

### Interface implementing another interface
```jsonc
{
  "interfaces": [
    {"name": "IBase", "typeIdentifier": "i-base", "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "IUser", "typeIdentifier": "i-user",
     "interfaceTypeIdentifiers": ["i-base"],
     "properties": [{"name": "email", "primitiveType": "String"}]}
  ]
}
```

### Class implementing interface (correct way for interface method signatures)
Use `customCode` for interface method signatures when a class will implement them:
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
  }],
  "classes": [{
    "name": "UserRepository", "typeIdentifier": "user-repo-impl",
    "interfaceTypeIdentifiers": ["user-repo"],
    "customCode": [
      {"code": "async findAll(): Promise<$user[]> { return []; }",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "async findById(id: string): Promise<$user | null> { return null; }",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }]
}
```

**Wrong**: Function-typed properties on interfaces you'll implement will cause the implementing class to duplicate them as property declarations alongside your customCode methods.

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
    {"name": "BaseEntity", "typeIdentifier": "base-entity",
     "properties": [{"name": "id", "primitiveType": "String"}]},
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

**C# note**: `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs instead.

### Complex type expressions with templateRefs
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

### Service with Angular dependency injection
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

---

## Language-Specific Notes

### TypeScript
- MetaEngine strips `I` prefix from interface exports. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control file name if collisions arise (e.g. `"fileName": "i-user-repository"`).
- Primitive mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly on classes and properties
- No framework imports needed — TypeScript built-ins require nothing

### C#
- `I` prefix PRESERVED on interface names
- `Number` → `int` (NOT double). Use `"type": "decimal"` or `"type": "double"` for non-integer numbers.
- `packageName` sets the namespace. Omit for GlobalUsings pattern.
- Interface properties generate `{ get; }`. Class properties generate `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs.
- `isOptional` on properties generates `string?` (nullable reference type)
- Constructor parameters auto-create properties — NEVER duplicate in `properties[]`

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode
- typing imports are automatic (don't add manually)

### Go
- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode
- Constructor parameters auto-create properties — don't duplicate in `properties[]`

### Java/Kotlin/Groovy
- Constructor parameters auto-create properties — don't duplicate in `properties[]`
- Java: enum members get `ALL_CAPS` transformation (judge tolerates this)

---

## Common Mistakes (Top 10)

1. **Don't** reference a `typeIdentifier` that doesn't exist in the batch → property silently dropped. **Do** verify every typeIdentifier matches a defined type in the same call.

2. **Don't** put method signatures as function-typed properties on interfaces you'll `implements`. **Do** use `customCode` for interface method signatures.

3. **Don't** write internal type names as raw strings in customCode (e.g., `"code": "private repo: IUserRepository"`). **Do** use templateRefs: `"code": "private repo: $repo"` with `"templateRefs": [{"placeholder": "$repo", "typeIdentifier": "user-repo"}]`.

4. **Don't** use `arrayTypes` in C# when you need `List<T>`. **Do** use `"type": "List<$user>"` with templateRefs.

5. **Don't** add `System.*`, `typing.*`, `java.util.*` etc. to customImports. **Do** let MetaEngine handle all framework imports automatically.

6. **Don't** duplicate constructor parameter names in `properties[]` (C#/Java/Go/Groovy). **Do** put shared fields only in `constructorParameters`.

7. **Don't** use reserved words (`delete`, `class`, `import`) as property names. **Do** use safe alternatives (`remove`, `clazz`, `importData`).

8. **Don't** generate related types in separate MCP calls. **Do** batch everything in one call — cross-file imports only resolve within a single batch.

9. **Don't** expect `Number` to map to `double` in C# — it maps to `int`. **Do** use `"type": "double"` or `"type": "decimal"` explicitly.

10. **Don't** forget `fileName` when both an `I`-prefixed interface and its implementing class would collide in TypeScript. **Do** set `"fileName": "i-user-repository"` on the interface.

---

## load_spec_from_file Tool

For complex architectures, write the spec JSON to a file and call this tool instead of `generate_code`. Drastically reduces AI context usage.

```jsonc
// Call:
{"specFilePath": "specs/user-system.json", "outputPath": "src"}
// or override specific fields:
{"specFilePath": "specs/user-system.json", "outputPath": "src", "dryRun": true}
```

Parameters:
- `specFilePath` (required): Path to JSON spec file (absolute or relative to CWD). Same structure as `generate_code`.
- `outputPath` (optional): Overrides `outputPath` in spec file.
- `skipExisting` (optional): Overrides `skipExisting` in spec file.
- `dryRun` (optional): Overrides `dryRun` in spec file.

The JSON spec file uses the same schema as `generate_code` (includes `language`, `classes`, `interfaces`, etc.).

---

## generate_openapi Tool

Generate typed HTTP clients from OpenAPI specs.

**Required**: `framework` (enum) + one of `openApiSpec` (inline YAML/JSON string) or `openApiSpecUrl` (URL).

**Supported frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession`

**Common options** (all optional):
- `outputPath` (default `"."`)
- `skipExisting` (default `true`)
- `dryRun` (default `false`)
- `documentation`: Generate JSDoc/XML doc comments
- `strictValidation`: Enable strict OpenAPI spec validation
- `optionsObjectThreshold`: Min params before grouping into options object
- `bearerAuth`: `{"envVarName": "...", "headerName": "..."}`
- `basicAuth`: `{"usernameEnvVar": "...", "passwordEnvVar": "..."}`
- `customHeaders`: `[{"headerName": "X-Api-Key", "envVarName": "API_KEY"}]`
- `errorHandling`: `{"enabled": true, "throwForStatusCodes": [400, 500], "returnNullForStatusCodes": [404]}`
- `retries`: `{"maxAttempts": 3, "retryStatusCodes": [429, 503], "baseDelaySeconds": 1, "maxDelaySeconds": 30}`
- `timeout`: `{"seconds": 30}` or `{"connect": 5, "read": 30, "write": 30}`

**Framework-specific options:**
- `angularOptions`: `{baseUrlToken, providedIn, useInjectFunction, useHttpResources, httpResourceTrigger, responseDateTransformation}`
- `reactOptions`: `{baseUrlEnvVar, useTanStackQuery, useTypesBarrel, responseDateTransformation}`
- `fetchOptions`: `{baseUrlEnvVar, useImportMetaEnv, useMiddleware, useResultPattern, useTypesBarrel}`
- `goOptions` (required for go): `{moduleName, packageName, baseUrlEnvVar, jsonLibrary, useContext}`
- `javaSpringOptions` (required for java): `{packageName, baseUrlProperty, beanValidation, nonNullSerialization, useComponentAnnotation}`
- `csharpOptions` (required for csharp): `{namespaceName}`
- `kotlinOptions` (required for kotlin): `{packageName}`
- `rustOptions` (required for rust): `{crateName, strictEnums}`
- `pythonOptions`: `{baseUrlEnvVar, generateSyncMethods, useCamelCaseAliases}`
- `swiftOptions`: `{strictEnums, typedThrows}`

---

## generate_graphql Tool

Generate typed HTTP clients from GraphQL SDL schemas.

**Required**: `framework` + `graphQLSchema` (SDL content string)

**Supported frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-fastapi`, `rust-reqwest`, `swift-urlsession`

**Common options** (all optional):
- `outputPath`, `skipExisting`, `dryRun`
- `documentation`: Generate docs from schema descriptions
- `discriminatedUnions`: Generate discriminated unions for GraphQL union types
- `bearerAuth`: `{"enabled": true}`
- `basicAuth`: `{"enabled": true}`
- `customHeaders`: `{"headers": [{"name": "X-Header", "value": "val"}]}`
- `errorHandling`: `{"mode": "throw" | "result"}`
- `retries`: `{"maxRetries": 3}`
- `timeout`: `{"seconds": 30}`

**Framework-specific options** (same structure as generate_openapi for angular/react/fetch/go/java/csharp/kotlin/rust/python/swift).

---

## generate_protobuf Tool

Generate typed HTTP clients from Protocol Buffers (.proto) definitions.

**Required**: `framework` + `protoSource` (.proto content string)

**Supported frameworks**: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-httpx` (note: httpx, not fastapi), `rust-reqwest`, `swift-urlsession`

**Common options**: Same as generate_graphql (outputPath, skipExisting, dryRun, documentation, bearerAuth, basicAuth, customHeaders, errorHandling, retries, timeout).

**fetchOptions** has extra: `{baseUrlEnvVar, useImportMetaEnv, useTypesBarrel}`

---

## generate_sql Tool

Generate typed model classes from SQL DDL (CREATE TABLE statements).

**Required**: `language` + `ddlSource` (SQL DDL string)

**Supported languages**: `typescript`, `csharp`, `go`, `python`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`

**Options** (all optional):
- `outputPath`, `skipExisting`, `dryRun`
- `generateInterfaces`: Generate interfaces alongside model classes
- `generateNavigationProperties`: Generate navigation properties for FK relationships
- `generateValidationAnnotations`: Generate validation annotations from column constraints
- `initializeProperties`: Initialize model properties with default values

**Language-specific options:**
- `csharpOptions`: `{namespace}`
- `goOptions` (required for go): `{moduleName}`
- `javaOptions` (required for java): `{packageName}`
- `kotlinOptions` (required for kotlin): `{packageName}`
- `groovyOptions` (required for groovy): `{packageName}`
- `scalaOptions` (required for scala): `{packageName}`
- `phpOptions` (required for php): `{rootNamespace, useStrictTypes}`
- `pythonOptions`: `{modelStyle: "dataclass" | "pydantic" | "plain"}`
- `rustOptions`: `{crateName}`

---

## Summary of Key Principles

1. **ONE call** for all related types — splitting breaks cross-reference resolution.
2. **properties** = type declarations only; **customCode** = methods and logic.
3. **templateRefs** required whenever internal types appear in customCode/type strings.
4. **customImports** = external libraries ONLY — never framework/stdlib imports.
5. **Virtual types** (arrayTypes, dictionaryTypes, concreteGenericClasses/Interfaces) = type references only, no files.
6. **Constructor params** auto-become properties in C#/Java/Go/Groovy — never duplicate in properties[].
7. **dryRun: true** for previewing output without writing files.
8. **load_spec_from_file** for large/complex specs to save context.
