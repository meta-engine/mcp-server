# MetaEngine MCP — Knowledge Brief

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike template engines, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

### `mcp__metaengine__metaengine_initialize`
Call this first (with `language` param) to get current patterns and guidance. Returns the canonical guide. Use before generating code for the first time in a session.
- `language` (optional enum): `typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php`

### `mcp__metaengine__generate_code`
The primary code-generation tool. Takes a structured JSON spec and writes compilable source files.
- Required: `language`
- All other fields optional arrays/objects

### `mcp__metaengine__load_spec_from_file`
Loads a JSON spec file from disk and runs generation. Identical capability to `generate_code` but reads the spec from a `.json` file instead of inline JSON. Drastically reduces AI context usage for large specs.
- Required: `specFilePath` (absolute or relative path to the `.json` spec)
- Optional overrides: `outputPath`, `skipExisting`, `dryRun`

### `mcp__metaengine__generate_openapi`
Generates fully-typed HTTP clients from OpenAPI specs (YAML or JSON, inline or URL).
- Required: `framework`
- Provide either `openApiSpec` (inline) or `openApiSpecUrl`
- Supported frameworks: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `python-fastapi`, `csharp-httpclient`, `kotlin-ktor`, `rust-reqwest`, `swift-urlsession`

### `mcp__metaengine__generate_graphql`
Generates fully-typed HTTP clients from a GraphQL SDL schema.
- Required: `framework`, `graphQLSchema`
- Supported frameworks: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-fastapi`, `rust-reqwest`, `swift-urlsession`

### `mcp__metaengine__generate_protobuf`
Generates fully-typed HTTP clients from Protocol Buffers (`.proto`) definitions.
- Required: `framework`, `protoSource`
- Supported frameworks: `angular`, `react`, `typescript-fetch`, `go-nethttp`, `java-spring`, `csharp-httpclient`, `kotlin-ktor`, `python-httpx`, `rust-reqwest`, `swift-urlsession`

### `mcp__metaengine__generate_sql`
Generates typed model classes from SQL DDL (`CREATE TABLE` statements).
- Required: `language`, `ddlSource`
- Supported languages: `typescript`, `csharp`, `go`, `python`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`
- Options: `generateInterfaces`, `generateNavigationProperties`, `generateValidationAnnotations`, `initializeProperties`

---

## `generate_code` — Full Input Schema

### Top-level fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `language` | enum (required) | — | `typescript \| python \| go \| csharp \| java \| kotlin \| groovy \| scala \| swift \| php \| rust` |
| `outputPath` | string | `"."` | Directory where files are written |
| `packageName` | string | — | Package/namespace/module name. Go default: `github.com/metaengine/demo`. Java/Kotlin/Groovy default: `com.metaengine.generated`. C#: omit for GlobalUsings (no namespace declaration) |
| `initialize` | boolean | `false` | Initialize all properties with default values |
| `skipExisting` | boolean | `true` | Skip files that already exist (stub pattern) |
| `dryRun` | boolean | `false` | Preview mode — returns generated code in response, no files written |
| `classes` | array | — | Class definitions (see below) |
| `interfaces` | array | — | Interface definitions (see below) |
| `enums` | array | — | Enum definitions (see below) |
| `customFiles` | array | — | Custom files without class wrapper (barrel exports, type aliases) |
| `arrayTypes` | array | — | Virtual array type refs — NO files generated |
| `dictionaryTypes` | array | — | Virtual dictionary type refs — NO files generated |
| `concreteGenericClasses` | array | — | Virtual concrete generic class refs (e.g. `Repository<User>`) — NO files generated |
| `concreteGenericInterfaces` | array | — | Virtual concrete generic interface refs — NO files generated |

---

### `classes[]` — Class definition schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string (required) | Class name |
| `typeIdentifier` | string | Unique ID for cross-referencing this class in the same batch |
| `path` | string | Subdirectory for the output file (e.g., `"models"`, `"services/auth"`) |
| `fileName` | string | Custom file name without extension (overrides default derivation) |
| `comment` | string | Documentation comment |
| `isAbstract` | boolean | Generate as abstract class |
| `baseClassTypeIdentifier` | string | typeIdentifier of the class to extend |
| `interfaceTypeIdentifiers` | string[] | typeIdentifiers of interfaces to implement |
| `genericArguments` | array | Makes this a generic class template (see below) |
| `constructorParameters` | array | Constructor parameters (auto-become properties in TS; auto-create fields in C#/Java/Go/Groovy — do NOT duplicate in `properties`) |
| `properties` | array | Field declarations — type only, no initialization (see below) |
| `customCode` | array | Methods and initialized fields — one item per member (see below) |
| `decorators` | array | Class-level decorators (e.g., `@Injectable(...)`) |
| `customImports` | array | External library imports only (see below) |

#### `classes[].genericArguments[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Generic param name (e.g. `"T"`, `"K"`) |
| `constraintTypeIdentifier` | string | typeIdentifier for the constraint (`where T : BaseEntity`) |
| `propertyName` | string | Creates a property with this name of type T |
| `isArrayProperty` | boolean | If true, property is `T[]` instead of `T` |

#### `classes[].constructorParameters[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Parameter name |
| `primitiveType` | enum | `String \| Number \| Boolean \| Date \| Any` |
| `type` | string | Raw type string for complex/external types |
| `typeIdentifier` | string | Reference to internal type |

#### `classes[].properties[]`

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | enum | `String \| Number \| Boolean \| Date \| Any` |
| `type` | string | Raw type string (e.g. `"Map<string, $resp>"`) |
| `typeIdentifier` | string | Reference to another type in the same batch |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — used with `type` containing `$placeholder` |
| `isOptional` | boolean | Mark as optional (`?`) |
| `isInitializer` | boolean | Add default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | array | templateRefs for comment text |
| `decorators` | array | Property decorators (e.g. `@IsEmail()`) |

#### `classes[].customCode[]`

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | The method or initialized field code. One item = one member. Use `\n` for multi-line. |
| `templateRefs` | array | `[{placeholder: "$name", typeIdentifier: "some-id"}]` — resolves imports for internal types used in code string |

#### `classes[].customImports[]`

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (e.g. `"@angular/core"`, `"rxjs"`) — for external libs only |
| `types` | string[] | Named imports from that path |

---

### `interfaces[]` — Interface definition schema

Same shape as `classes[]` minus `isAbstract`, `baseClassTypeIdentifier`, `constructorParameters`. Key differences:
- `interfaceTypeIdentifiers`: extend other interfaces
- Properties generate `{ get; }` in C#
- Method signatures go in `customCode`, NOT as function-typed properties (to avoid duplication when a class implements the interface)
- TypeScript strips `I` prefix from name when generating the export — use `fileName` to prevent collisions

---

### `enums[]` — Enum definition schema

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Cross-reference ID |
| `path` | string | Output subdirectory |
| `fileName` | string | Custom file name |
| `comment` | string | Documentation comment |
| `members` | array | `[{name: string, value: number}]` |

Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

---

### `customFiles[]` — Custom file (no class wrapper)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (without extension) |
| `fileName` | string | Alternative custom file name |
| `path` | string | Output subdirectory |
| `identifier` | string | Optional ID so other files can reference this via `customImports` path resolution |
| `customCode` | array | Code blocks — one per export/type alias/function |
| `customImports` | array | External imports |

---

### `arrayTypes[]` — Virtual array type (NO file generated)

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference this array type in properties |
| `elementTypeIdentifier` | string | Reference to a custom element type |
| `elementPrimitiveType` | enum | `String \| Number \| Boolean \| Date \| Any` |

**C# note**: arrayTypes generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs.

---

### `dictionaryTypes[]` — Virtual dictionary type (NO file generated)

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string (required) | ID to reference in properties |
| `keyPrimitiveType` | enum | Key primitive |
| `keyType` | string | String literal for key type |
| `keyTypeIdentifier` | string | Custom type for key |
| `valuePrimitiveType` | enum | Value primitive |
| `valueTypeIdentifier` | string | Custom type for value |

---

### `concreteGenericClasses[]` — Virtual concrete generic (NO file generated)

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID used in `baseClassTypeIdentifier` |
| `genericClassIdentifier` | string | References the generic class template |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` — the type args to fill in |

Use: define a generic class with `genericArguments`, create a concrete via `concreteGenericClasses`, then have a class extend it via `baseClassTypeIdentifier`. MetaEngine generates `extends Repository<User>` with correct imports.

---

### `concreteGenericInterfaces[]` — Virtual concrete generic interface (NO file generated)

Same shape as `concreteGenericClasses` but for interfaces.

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | ID used in `interfaceTypeIdentifiers` |
| `genericClassIdentifier` | string | References the generic interface template |
| `genericArguments` | array | `[{typeIdentifier?, primitiveType?}]` |

---

## Critical Rules (must not violate)

### Rule 1 — ONE call for all related types
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both MUST be in the same `generate_code` call. Splitting across multiple calls means cross-references silently drop.

### Rule 2 — properties = type declarations only; customCode = everything else
- `properties[]`: field names with types only. No initialization, no logic.
- `customCode[]`: methods, initialized fields, any code with logic. One item = exactly one member.
- Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

### Rule 3 — Use templateRefs for internal types in customCode/properties with raw `type` strings
When `code` or `type` contains a reference to a type in the same batch, use `$placeholder` syntax with `templateRefs`. This triggers automatic import resolution. Without templateRefs, MetaEngine cannot generate the import/using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**Critical in C#**: Every internal type in customCode MUST use templateRefs or `using` directives for cross-namespace types won't be generated — causing compile failures.

### Rule 4 — Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication/errors.

Auto-imported per language (never specify these in `customImports`):
- **TypeScript**: no imports needed — built-in types
- **C#**: `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*`
- **Python**: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`
- **Java**: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, jackson
- **Kotlin**: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`
- **Go**: `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, and more
- **Swift**: Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)
- **Rust**: `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde`
- **Groovy**: `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream)
- **Scala**: `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*`
- **PHP**: `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable`

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5 — templateRefs are ONLY for internal types
External library types → `customImports`. Same-batch type → `typeIdentifier` or `templateRefs`. Never mix.

### Rule 6 — Constructor parameters auto-create properties (C#, Java, Go, Groovy)
In C#, Java, Go, and Groovy, constructor parameters automatically become class properties. Do NOT also list them in `properties[]` — this causes "Sequence contains more than one matching element" errors.
- Put shared fields only in `constructorParameters`
- Put additional-only fields (not constructor params) in `properties[]`
- TypeScript: constructorParameters do NOT auto-create properties (you may duplicate in properties if needed)

### Rule 7 — Virtual types (arrayTypes, dictionaryTypes, concreteGenericClasses, concreteGenericInterfaces) NEVER generate files
They create reusable type references only. They are consumed by referencing their `typeIdentifier` in file-generating types.

---

## Output Structure

MetaEngine writes one file per class/interface/enum/customFile. Files are placed at `outputPath/path/fileName.ext`. For TypeScript:
- Class: `user.ts`
- Interface: `user-repository.ts` (I-prefix stripped from export name, not from file unless you set `fileName`)
- Enum: `order-status.enum.ts`

The engine:
1. Resolves all `typeIdentifier` cross-references within the batch
2. Generates correct import statements between files
3. Applies language-specific idioms (Java `ALL_CAPS` enums, Python `snake_case` methods, etc.)
4. Writes files to disk (unless `dryRun: true`)

When `dryRun: true`: file contents are returned in the response for review — nothing written to disk.
When `skipExisting: true` (default): only new files are created; existing files are untouched.

---

## TypeScript-Specific Notes

- MetaEngine strips `I` prefix from interface names: `IUserRepository` → exported as `UserRepository`. Use `fileName: "i-user-repository"` to prevent file name collisions when both the interface and its implementing class exist.
- Primitive mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent applied for `\n` in customCode
- Decorators supported directly on classes/properties
- Constructor parameters do NOT auto-create properties in TypeScript (unlike C#/Java)
- No framework imports needed — all built-in types resolved automatically

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
Produces two files with automatic imports between them.

### Class with inheritance and methods
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

### Generic class + concrete implementation
```jsonc
{
  "classes": [
    {
      "name": "Repository", "typeIdentifier": "repo-generic",
      "genericArguments": [{
        "name": "T",
        "constraintTypeIdentifier": "base-entity",
        "propertyName": "items",
        "isArrayProperty": true
      }],
      "customCode": [
        {"code": "add(item: T): void { this.items.push(item); }"},
        {"code": "getAll(): T[] { return this.items; }"}
      ]
    },
    {
      "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{"name": "email", "primitiveType": "String"}]
    },
    {
      "name": "UserRepository", "typeIdentifier": "user-repo-class",
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

### Complex type expressions with templateRefs (in properties)
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
templateRefs work in: properties, customCode, and decorators.

### Enum + class that uses it
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

### Angular service with external DI
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

### Interface with method signatures (for implements)
Use `customCode` for method signatures on interfaces that will be implemented by a class:
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
Do NOT use function-typed properties (e.g. `"type": "() => Promise<User[]>"`) — the implementing class will duplicate them as property declarations.

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
The `identifier` on customFile enables import path auto-resolution. `customImports` referencing the identifier resolves to relative path.

### load_spec_from_file pattern
For complex architectures, write the spec to a `.json` file first, then call:
```jsonc
// specs/user-system.json contains the full generate_code spec
mcp__metaengine__load_spec_from_file({
  "specFilePath": "specs/user-system.json",
  "outputPath": "src"
})
```
This avoids bloating AI context with large JSON payloads.

---

## Common Mistakes — Quick Reference

| Don't | Do instead |
|-------|-----------|
| Reference a `typeIdentifier` not in the current batch | Every cross-referenced type must be in the same call |
| Put method signatures as function-typed properties on interfaces | Use `customCode` for interface method signatures |
| Write internal type names as raw strings in customCode | Use templateRefs: `"code": "repo: $repo"` + `templateRefs` |
| Use `arrayTypes` in C# when you need `List<T>` | Use `"type": "List<$user>"` with templateRefs |
| Add `System.*`, `typing.*`, `java.util.*` to `customImports` | Let MetaEngine handle all framework imports automatically |
| Duplicate constructor params in `properties[]` (C#/Java/Go/Groovy) | Constructor params only in `constructorParameters`; extras in `properties` |
| Use reserved words as property names (`delete`, `class`, `import`) | Use safe alternatives: `remove`, `clazz`, `importData` |
| Split related types across multiple MCP calls | Batch everything in one call |
| Expect `Number` → `double` in C# | `Number` → `int` in C#; use `"type": "double"` or `"type": "decimal"` explicitly |
| Omit `fileName` when I-prefixed interface and implementing class would collide | Set `"fileName": "i-user-repository"` on the interface |
| Put methods in `properties[]` | Methods go in `customCode[]` |
| Put uninitialized type declarations in `customCode[]` | Uninitialized declarations go in `properties[]` |
| Generate related types in separate MCP calls | One call — cross-file imports only resolve within a single batch |

---

## `generate_openapi` Key Options (TypeScript-focused)

For `typescript-fetch` framework:
- `fetchOptions.baseUrlEnvVar`: env var for base URL (e.g. `"API_BASE_URL"`)
- `fetchOptions.useImportMetaEnv`: use `import.meta.env` (Vite/SvelteKit) instead of `process.env`
- `fetchOptions.useMiddleware`: emit middleware hooks (`onRequest`, `onResponse`, `onError`)
- `fetchOptions.useResultPattern`: result pattern instead of throwing
- `fetchOptions.useTypesBarrel`: generate barrel file re-exporting all types
- `documentation`: generate JSDoc comments
- `bearerAuth.envVarName`: env var for bearer token
- `errorHandling.throwForStatusCodes`: array of status codes that throw
- `retries.maxAttempts`, `retries.baseDelaySeconds`, `retries.retryStatusCodes`
- `timeout.seconds`

For `angular` framework:
- `angularOptions.useInjectFunction`: use `inject()` instead of constructor injection
- `angularOptions.providedIn`: `@Injectable` scope
- `angularOptions.baseUrlToken`: injection token name for base URL
- `angularOptions.useHttpResources`: use Angular HTTP resources API
- `angularOptions.responseDateTransformation`: transform date strings to Date objects

---

## Summary Decision Tree

1. **Need to generate TypeScript classes/interfaces/enums?** → `generate_code` with `language: "typescript"`, batch all related types in ONE call.
2. **Spec is large / complex?** → Write spec to a `.json` file, use `load_spec_from_file`.
3. **Have an OpenAPI spec?** → `generate_openapi` with appropriate framework.
4. **Have a GraphQL SDL?** → `generate_graphql`.
5. **Have `.proto` files?** → `generate_protobuf`.
6. **Have SQL DDL?** → `generate_sql`.
7. **Unknown patterns or first use?** → Call `metaengine_initialize` with `language` first.

