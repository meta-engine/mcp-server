# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a **semantic code generation system** exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically.

The key value proposition: a **single well-formed JSON call** replaces dozens of error-prone file writes, because all imports between generated files are resolved within the batch automatically.

---

## Tools Exposed

### `mcp__metaengine__generate_code`
Main tool. Generates source files from a JSON spec. Accepts classes, interfaces, enums, customFiles, arrayTypes, dictionaryTypes, concreteGenericClasses, concreteGenericInterfaces — all in one call.

### `mcp__metaengine__load_spec_from_file`
Like `generate_code` but reads the spec from a JSON file on disk. Useful for large/complex architectures to avoid context bloat. Same output behavior.

### `mcp__metaengine__generate_openapi`
Generates a fully typed HTTP client from an OpenAPI spec (YAML/JSON inline or URL). Supports: angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi, csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession.

### `mcp__metaengine__generate_graphql`
Generates a fully typed HTTP client from a GraphQL SDL schema. Same framework targets as generate_openapi (except python-fastapi → python-fastapi).

### `mcp__metaengine__generate_protobuf`
Generates a fully typed HTTP client from Protocol Buffers (.proto) definitions. Same framework targets.

### `mcp__metaengine__generate_sql`
Generates typed model classes from SQL DDL (CREATE TABLE statements). Supports TypeScript, C#, Go, Python, Java, Kotlin, Groovy, Scala, Swift, PHP, Rust.

### `mcp__metaengine__metaengine_initialize`
Returns documentation/patterns. Call this when generating code for the first time or when you need guidance. Accepts optional `language` parameter.

---

## `generate_code` — Full Input Schema

### Top-level fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `language` | enum | YES | — | Target language: typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php, rust |
| `outputPath` | string | no | `"."` | Directory where files are written |
| `packageName` | string | no | lang-default | Package/namespace name. For C#: omit for GlobalUsings pattern. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy default: `com.metaengine.generated` |
| `initialize` | boolean | no | `false` | Initialize all properties with default values |
| `skipExisting` | boolean | no | `true` | Skip files that already exist (stub pattern) |
| `dryRun` | boolean | no | `false` | Preview mode — returns generated code without writing to disk |
| `classes` | array | no | — | Class definitions |
| `interfaces` | array | no | — | Interface definitions |
| `enums` | array | no | — | Enum definitions |
| `customFiles` | array | no | — | Files without a class wrapper (type aliases, barrel exports, utilities) |
| `arrayTypes` | array | no | — | Virtual array type references (no files generated) |
| `dictionaryTypes` | array | no | — | Virtual dictionary type references (no files generated) |
| `concreteGenericClasses` | array | no | — | Virtual concrete generic class (e.g., `Repository<User>`) — no files |
| `concreteGenericInterfaces` | array | no | — | Virtual concrete generic interface — no files |

---

### `classes[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Class name |
| `typeIdentifier` | string | Unique ID for cross-referencing in the same batch |
| `path` | string | Directory path (e.g., `"models"`, `"services/auth"`) |
| `fileName` | string | Custom file name without extension |
| `comment` | string | Documentation comment |
| `isAbstract` | boolean | Abstract class |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class to extend |
| `interfaceTypeIdentifiers` | string[] | typeIdentifiers of interfaces to implement |
| `genericArguments` | array | Generic parameters — makes this a generic class template |
| `constructorParameters` | array | Constructor parameters (auto-become properties in TS; auto-become fields in C#/Java/Go/Groovy — do NOT also put in properties[]) |
| `properties` | array | Field declarations (type only, no logic) |
| `customCode` | array | Methods and initialized fields — one item = one member |
| `customImports` | array | External library imports |
| `decorators` | array | Class-level decorators |

#### `classes[].genericArguments[]` item

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Generic parameter name (e.g., `"T"`, `"K"`) |
| `constraintTypeIdentifier` | string | typeIdentifier for the generic constraint (e.g., `where T : BaseEntity`) |
| `propertyName` | string | Creates a property of type T with this name |
| `isArrayProperty` | boolean | If true, makes the property type `T[]` |

#### `classes[].constructorParameters[]` item

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Parameter name |
| `primitiveType` | enum | String, Number, Boolean, Date, Any |
| `type` | string | Complex/external type as raw string |
| `typeIdentifier` | string | Reference to another type in the batch |

#### `classes[].properties[]` item

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | enum | String, Number, Boolean, Date, Any |
| `typeIdentifier` | string | Reference to another type in the batch |
| `type` | string | Complex types or external types as raw string (use with templateRefs for internal refs) |
| `isOptional` | boolean | Nullable/optional (generates `string?` in C#, `T \| undefined` in TS) |
| `isInitializer` | boolean | Add default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | array | templateRefs for the comment field |
| `decorators` | array | Property decorators (e.g., `@IsEmail()`) |
| `templateRefs` | array | Resolves `$placeholder` tokens in `type` to internal types |

#### `classes[].customCode[]` item

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Raw code string — one method or initialized field |
| `templateRefs` | array | Resolves `$placeholder` in code to internal types + generates import |

#### `classes[].customImports[]` item

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (e.g., `"@angular/core"`) |
| `types` | string[] | Named imports from that path |

#### `classes[].decorators[]` item

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Decorator string (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | array | templateRefs for placeholder resolution in decorator code |

---

### `interfaces[]` item schema

Same fields as `classes[]` except: no `isAbstract`, no `baseClassTypeIdentifier`, no `constructorParameters`. Has `interfaceTypeIdentifiers` for extending other interfaces.

**Important for TypeScript**: MetaEngine strips `I` prefix from interface names when exporting. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control the file name if collisions arise with implementing classes.

**Important for methods**: Define method signatures in `customCode`, NOT as function-typed properties, when a class will implement the interface. Function-typed properties cause duplicate declarations.

---

### `enums[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Unique ID for referencing |
| `members` | array | `{name: string, value: number}` items |
| `path` | string | Directory path |
| `fileName` | string | Custom file name |
| `comment` | string | Documentation comment |

Enum filenames auto-suffix: `.enum.ts` (TS), `OrderStatus.cs` (C#), etc.

---

### `customFiles[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (without extension) |
| `identifier` | string | Optional ID so other files can `customImport` this file by identifier |
| `path` | string | Directory path |
| `fileName` | string | Custom file name override |
| `customCode` | array | Code blocks — one per export/type alias/function |
| `customImports` | array | External imports |

---

### `arrayTypes[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference this array type |
| `elementTypeIdentifier` | string | For custom element types |
| `elementPrimitiveType` | enum | For primitive elements (String, Number, Boolean, Date, Any) |

**No files generated.** Reference by typeIdentifier in properties.
**C# note**: arrayTypes generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs.

---

### `dictionaryTypes[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference this dictionary type |
| `keyPrimitiveType` | enum | Primitive key type |
| `keyTypeIdentifier` | string | Custom key type reference |
| `keyType` | string | String literal for key type |
| `valuePrimitiveType` | enum | Primitive value type |
| `valueTypeIdentifier` | string | Custom value type reference |

**No files generated.**

---

### `concreteGenericClasses[]` item schema

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID for this concrete implementation |
| `genericClassIdentifier` | string | References the generic class definition |
| `genericArguments` | array | `{typeIdentifier?: string, primitiveType?: enum}` items |

**No files generated.** Creates a virtual `Repository<User>` type. Classes reference it via `baseClassTypeIdentifier`.

---

### `concreteGenericInterfaces[]` item schema

Same structure as `concreteGenericClasses` but for interfaces.

---

### `templateRefs[]` item schema (used inside customCode, properties, decorators)

| Field | Type | Description |
|-------|------|-------------|
| `placeholder` | string | Token in code string (e.g., `"$user"`) |
| `typeIdentifier` | string | Internal type from the same batch |

The `$placeholder` in the code string gets replaced with the resolved type name AND triggers automatic import generation.

---

## `load_spec_from_file` — Full Input Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `specFilePath` | string | YES | Path to JSON spec file (absolute or relative to cwd) |
| `outputPath` | string | no | Override outputPath from spec |
| `skipExisting` | boolean | no | Override skipExisting from spec |
| `dryRun` | boolean | no | Override dryRun from spec |

The JSON file has the same structure as the `generate_code` input.

---

## `generate_openapi` — Key Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `framework` | enum | YES | angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi, csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession |
| `openApiSpec` | string | one of | Inline OpenAPI YAML/JSON |
| `openApiSpecUrl` | string | one of | URL to fetch spec from |
| `outputPath` | string | no | Output directory |
| `dryRun` | boolean | no | Preview without writing |
| `skipExisting` | boolean | no | Default true |
| `documentation` | boolean | no | Generate JSDoc/XML comments |
| `angularOptions` | object | no | `{baseUrlToken, providedIn, useInjectFunction, useHttpResources, httpResourceTrigger, responseDateTransformation, useInjectFunction}` |
| `fetchOptions` | object | no | `{baseUrlEnvVar, useImportMetaEnv, useMiddleware, useResultPattern, useTypesBarrel}` |
| `reactOptions` | object | no | `{baseUrlEnvVar, useTanStackQuery, useTypesBarrel, responseDateTransformation}` |
| `goOptions` | object | if go | `{moduleName (req), packageName (req), baseUrlEnvVar, useContext, jsonLibrary}` |
| `javaSpringOptions` | object | if java | `{packageName (req), baseUrlProperty, beanValidation, nonNullSerialization, useComponentAnnotation}` |
| `kotlinOptions` | object | if kotlin | `{packageName (req)}` |
| `csharpOptions` | object | if csharp | `{namespaceName (req)}` |
| `pythonOptions` | object | no | `{baseUrlEnvVar, generateSyncMethods, useCamelCaseAliases}` |
| `rustOptions` | object | if rust | `{crateName (req), strictEnums}` |
| `swiftOptions` | object | no | `{strictEnums, typedThrows}` |
| `bearerAuth` | object | no | `{envVarName, headerName}` |
| `basicAuth` | object | no | `{usernameEnvVar, passwordEnvVar}` |
| `customHeaders` | array | no | `[{headerName (req), envVarName (req)}]` |
| `errorHandling` | object | no | `{enabled, throwForStatusCodes[], returnNullForStatusCodes[]}` |
| `retries` | object | no | `{maxAttempts, baseDelaySeconds, maxDelaySeconds, retryStatusCodes[]}` |
| `timeout` | object | no | `{seconds, connect, read, write}` |
| `optionsObjectThreshold` | number | no | Min params before grouping into options object |
| `strictValidation` | boolean | no | Strict OpenAPI validation |

---

## `generate_sql` — Key Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `language` | enum | YES | typescript, csharp, go, python, java, kotlin, groovy, scala, swift, php, rust |
| `ddlSource` | string | YES | SQL DDL (CREATE TABLE statements) |
| `outputPath` | string | no | Output directory |
| `dryRun` | boolean | no | Preview without writing |
| `skipExisting` | boolean | no | Default true |
| `generateInterfaces` | boolean | no | Also generate interfaces |
| `generateNavigationProperties` | boolean | no | Navigation properties for FK relationships |
| `generateValidationAnnotations` | boolean | no | Validation annotations from column constraints |
| `initializeProperties` | boolean | no | Initialize with defaults |
| `javaOptions` | object | if java | `{packageName (req)}` |
| `kotlinOptions` | object | if kotlin | `{packageName (req)}` |
| `groovyOptions` | object | if groovy | `{packageName (req)}` |
| `scalaOptions` | object | if scala | `{packageName (req)}` |
| `goOptions` | object | if go | `{moduleName (req)}` |
| `csharpOptions` | object | no | `{namespace}` |
| `pythonOptions` | object | no | `{modelStyle: 'dataclass'\|'pydantic'\|'plain'}` |
| `phpOptions` | object | if php | `{rootNamespace (req), useStrictTypes}` |
| `rustOptions` | object | no | `{crateName}` |

---

## Critical Rules (Failures When Violated)

### Rule 1: ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. **Never split related types across multiple calls.**

### Rule 2: properties[] = type declarations only; customCode[] = everything with logic
- `properties[]` → field declarations with types only. No initialization, no methods.
- `customCode[]` → methods, initialized fields, any code with logic. One item = exactly one member.
- **Never put methods in properties. Never put uninitialized type declarations in customCode.**

### Rule 3: templateRefs for internal types in customCode (and properties with `type` field)
When customCode or a `type`-string property references a type from the same batch, use `$placeholder` syntax + `templateRefs`. This triggers automatic import generation.
```jsonc
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```
**In C#**: Every internal type in customCode MUST use templateRefs or cross-namespace `using` directives won't be generated.

### Rule 4: Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

| Language | Auto-imported (NEVER add manually) |
|----------|-------------------------------------|
| TypeScript | (no imports needed — built-ins) |
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

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5: templateRefs ONLY for internal types; customImports ONLY for external
- Same-batch type → `typeIdentifier` or `templateRefs`
- External library → `customImports`
- Never mix these.

### Rule 6: Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Do NOT also put constructor parameters in `properties[]`. This causes "Sequence contains more than one matching element" errors. Only put non-constructor additional fields in `properties[]`.
```jsonc
// WRONG — duplicate:
"constructorParameters": [{"name": "email", "type": "string"}],
"properties": [{"name": "email", "type": "string"}]

// CORRECT:
"constructorParameters": [{"name": "email", "type": "string"}]
// extra-only fields go in properties[]
```

### Rule 7: Virtual types (arrayTypes, dictionaryTypes, concreteGenericClasses, concreteGenericInterfaces) do NOT generate files
They create reusable type references only. Reference their `typeIdentifier` in properties of file-generating types.

---

## Primitive Type Mappings

| MetaEngine primitive | TypeScript | C# | Python | Java | Go |
|---------------------|-----------|-----|--------|------|-----|
| `String` | `string` | `string` | `str` | `String` | `string` |
| `Number` | `number` | `int` | `int` | `int` | `int` |
| `Boolean` | `boolean` | `bool` | `bool` | `boolean` | `bool` |
| `Date` | `Date` | `DateTime` | `datetime` | `LocalDate` | `time.Time` |
| `Any` | `unknown` | `object` | `Any` | `Object` | `interface{}` |

**C# note**: `Number` → `int`, not `double`. Use `"type": "double"` or `"type": "decimal"` explicitly for non-integer numbers.

---

## TypeScript-Specific Notes

- MetaEngine strips `I` prefix from interface names in exports. `IUserRepository` → exported as `UserRepository`. Use `fileName: "i-user-repository"` on the interface to avoid file name collisions with the implementing class.
- `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly on classes and properties
- Interfaces with methods: put method signatures in `customCode`, not as function-typed properties

---

## Output Structure

- One file per class/interface/enum/customFile
- Files placed at `outputPath/path/fileName.ext`
- All imports between files in the same batch are auto-resolved
- `dryRun: true` returns file contents in response without writing

---

## Common Mistakes Checklist

1. **Don't** reference a `typeIdentifier` not defined in the same batch → silently dropped. **Do** verify every `typeIdentifier` matches a defined type in the same call.

2. **Don't** put method signatures as function-typed properties on interfaces you'll `implements`. **Do** use `customCode` for interface method signatures.

3. **Don't** write internal type names as raw strings in customCode (e.g., `"code": "private repo: IUserRepository"`). **Do** use templateRefs: `"code": "private repo: $repo"` with matching templateRefs entry.

4. **Don't** use `arrayTypes` in C# when you need `List<T>`. **Do** use `"type": "List<$user>"` with templateRefs.

5. **Don't** add `System.*`, `typing.*`, `java.util.*` etc. to customImports. **Do** let MetaEngine handle framework imports.

6. **Don't** duplicate constructor parameter names in `properties[]` for C#/Java/Go/Groovy. **Do** put shared fields only in `constructorParameters`.

7. **Don't** use reserved words (`delete`, `class`, `import`) as property names. **Do** use alternatives (`remove`, `clazz`, `importData`).

8. **Don't** generate related types in separate MCP calls. **Do** batch everything in one call.

9. **Don't** expect `Number` to map to `double` in C# — it maps to `int`. **Do** use `"type": "double"` or `"type": "decimal"` explicitly.

10. **Don't** forget `fileName` when both an `I`-prefixed interface and its implementing class would collide in TypeScript. **Do** set `"fileName": "i-user-repository"` on the interface.

---

## Representative Patterns

### Basic: Two interfaces with cross-references (TypeScript)

```jsonc
{
  "language": "typescript",
  "interfaces": [
    {
      "name": "Address", "typeIdentifier": "address",
      "properties": [
        {"name": "street", "primitiveType": "String"},
        {"name": "city", "primitiveType": "String"}
      ]
    },
    {
      "name": "User", "typeIdentifier": "user",
      "properties": [
        {"name": "id", "primitiveType": "String"},
        {"name": "address", "typeIdentifier": "address"}
      ]
    }
  ]
}
```

### Abstract base + extending class

```jsonc
{
  "classes": [
    {
      "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [{"name": "id", "primitiveType": "String"}]
    },
    {
      "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{"name": "email", "primitiveType": "String"}],
      "customCode": [
        {"code": "getDisplayName(): string { return this.email; }"}
      ]
    }
  ]
}
```

### Generic class + concreteGenericClass + implementing class

```jsonc
{
  "classes": [
    {
      "name": "Repository", "typeIdentifier": "repo-generic",
      "genericArguments": [{
        "name": "T", "constraintTypeIdentifier": "base-entity",
        "propertyName": "items", "isArrayProperty": true
      }],
      "customCode": [
        {"code": "add(item: T): void { this.items.push(item); }"},
        {"code": "getAll(): T[] { return this.items; }"}
      ]
    },
    {
      "name": "UserRepository", "typeIdentifier": "user-repo",
      "baseClassTypeIdentifier": "user-repo-concrete",
      "customCode": [{
        "code": "findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
      }]
    }
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{"typeIdentifier": "user"}]
  }]
}
```

### Service with external dependencies (Angular)

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
      {
        "code": "getUsers(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
        "templateRefs": [{"placeholder": "$list", "typeIdentifier": "user-array"}]
      }
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user"}]
}
```

### Enum + class using it

```jsonc
{
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 2}]
  }],
  "classes": [{
    "name": "Order", "typeIdentifier": "order",
    "properties": [{"name": "status", "typeIdentifier": "order-status"}],
    "customCode": [{
      "code": "updateStatus(s: $status): void { this.status = s; }",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]
  }]
}
```

### Interface with method signatures (when a class will implement it)

```jsonc
{
  "interfaces": [{
    "name": "IUserRepository", "typeIdentifier": "user-repo-iface",
    "fileName": "i-user-repository",
    "customCode": [
      {
        "code": "findAll(): Promise<$user[]>;",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
      },
      {
        "code": "findById(id: string): Promise<$user | null>;",
        "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
      }
    ]
  }]
}
```

### CustomFile for type aliases / barrel exports

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

### Complex type expression with templateRefs in property

```jsonc
{
  "properties": [{
    "name": "cache",
    "type": "Map<string, $resp>",
    "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
  }]
}
```

### Dictionary type

```jsonc
{
  "dictionaryTypes": [
    {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
  ]
}
```

---

## Language-Specific Gotchas

### TypeScript
- Interface `I`-prefix stripped in export name; use `fileName` to avoid file collision with implementing class
- `Number`→`number`, `String`→`string`, `Boolean`→`boolean`, `Date`→`Date`, `Any`→`unknown`
- Auto-indent on `\n` in customCode

### C#
- `Number`→`int` (not double). Use explicit `"type": "double"` / `"type": "decimal"` when needed.
- `packageName` sets the namespace; omit for GlobalUsings pattern
- Interface properties generate `{ get; }`, class properties `{ get; set; }`
- `arrayTypes` → `IEnumerable<T>`. Need `List<T>`? Use `"type": "List<$t>"` + templateRefs.
- `isOptional` → `string?` (nullable reference type)
- Every internal type in customCode MUST use templateRefs or cross-namespace `using` won't be generated

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode
- `typing` imports auto-generated

### Go
- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode

### Java/Kotlin/Groovy
- Constructor parameters auto-become fields — never duplicate in properties[]
- Language-aware idioms: Java uses `ALL_CAPS` enum members, Python uses `snake_case` methods

