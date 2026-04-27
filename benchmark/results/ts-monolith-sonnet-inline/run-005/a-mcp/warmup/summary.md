# MetaEngine MCP — Knowledge Brief

## Overview

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. It resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

### `mcp__metaengine__generate_code`
The primary tool. Accepts a structured JSON spec and generates compilable source files with correct imports and cross-references.

**Required parameters:**
- `language` (string, required): Target language — `"typescript"`, `"python"`, `"go"`, `"csharp"`, `"java"`, `"kotlin"`, `"groovy"`, `"scala"`, `"swift"`, `"php"`, `"rust"`

**Optional top-level parameters:**
- `outputPath` (string, default `"."`) — directory where files are written
- `packageName` (string) — package/module/namespace name. For C#: omit for GlobalUsings pattern. For Go default: `github.com/metaengine/demo`. For Java/Kotlin/Groovy default: `com.metaengine.generated`
- `initialize` (boolean, default `false`) — initialize all properties with default values
- `skipExisting` (boolean, default `true`) — skip files that already exist (stub pattern)
- `dryRun` (boolean, default `false`) — preview mode; returns generated code without writing files

**Top-level array parameters (all optional):**
- `classes[]`
- `interfaces[]`
- `enums[]`
- `arrayTypes[]`
- `dictionaryTypes[]`
- `concreteGenericClasses[]`
- `concreteGenericInterfaces[]`
- `customFiles[]`

---

### `mcp__metaengine__load_spec_from_file`
Load a JSON spec from a file instead of passing inline. Same generation capability as `generate_code` but with zero memory/context overhead. Ideal for complex architectures.

**Parameters:**
- `specFilePath` (string, required) — absolute or relative path to the JSON spec file (same structure as `generate_code`)
- `outputPath` (string, optional) — overrides `outputPath` in the spec file
- `skipExisting` (boolean, optional) — overrides `skipExisting` in the spec file
- `dryRun` (boolean, optional) — overrides `dryRun` in the spec file

**Usage pattern:**
1. Write a `.json` file with the same structure as `generate_code`
2. Call `load_spec_from_file` with the file path
3. Optionally override `outputPath`, `skipExisting`, or `dryRun`

---

### `mcp__metaengine__metaengine_initialize`
Returns essential patterns and documentation resources. Call this before generating code for the first time or when you need guidance.

**Parameters:**
- `language` (string, optional) — if specified, returns language-specific patterns. Accepts same enum as `generate_code`.

---

### Other Tools (spec conversion — not used for TypeScript generation)
- `mcp__metaengine__generate_graphql` — converts GraphQL schema to code
- `mcp__metaengine__generate_openapi` — converts OpenAPI spec to code
- `mcp__metaengine__generate_protobuf` — converts Protobuf schema to code
- `mcp__metaengine__generate_sql` — converts SQL schema to code

---

## `generate_code` — Full Input Schema

### `classes[]` items

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | Class name |
| `typeIdentifier` | string | no | Unique ID for cross-referencing this class in the same batch |
| `path` | string | no | Directory path (e.g., `"models"`, `"services/auth"`) |
| `fileName` | string | no | Custom file name without extension |
| `comment` | string | no | Documentation comment |
| `isAbstract` | boolean | no | Makes class abstract |
| `baseClassTypeIdentifier` | string | no | typeIdentifier of base class to extend |
| `interfaceTypeIdentifiers` | string[] | no | Array of typeIdentifiers of interfaces to implement |
| `genericArguments` | object[] | no | Generic parameters — makes this a generic class template (e.g., `Repository<T>`) |
| `constructorParameters` | object[] | no | Constructor parameters; auto-become properties in TypeScript |
| `properties` | object[] | no | Field/property declarations (type only — no logic) |
| `customCode` | object[] | no | Methods, initialized fields, any code with logic. ONE item = ONE member. |
| `decorators` | object[] | no | Class-level decorators |
| `customImports` | object[] | no | External library imports |

#### `classes[].genericArguments[]` items
| Field | Type | Description |
|---|---|---|
| `name` | string | Generic parameter name (e.g., `"T"`, `"K"`) |
| `constraintTypeIdentifier` | string | typeIdentifier for generic constraint (`where T : BaseEntity`) |
| `propertyName` | string | Creates a property of type T with this name |
| `isArrayProperty` | boolean | If true, property is T[] instead of T |

#### `classes[].constructorParameters[]` items
| Field | Type | Description |
|---|---|---|
| `name` | string | Parameter name |
| `primitiveType` | enum | `"String"`, `"Number"`, `"Boolean"`, `"Date"`, `"Any"` |
| `type` | string | For complex/external types |
| `typeIdentifier` | string | Reference to an internal type in the batch |

#### `classes[].properties[]` items
| Field | Type | Description |
|---|---|---|
| `name` | string | Property name |
| `primitiveType` | enum | `"String"`, `"Number"`, `"Boolean"`, `"Date"`, `"Any"` |
| `typeIdentifier` | string | Reference to another type in the batch |
| `type` | string | For complex types or external types (e.g., `"Map<string, $resp>"`) |
| `templateRefs` | object[] | `[{"placeholder": "$resp", "typeIdentifier": "api-response"}]` — for $placeholders in `type` |
| `isOptional` | boolean | Makes property optional (`string?` in C#, `?` in TS) |
| `isInitializer` | boolean | Add default value initialization |
| `comment` | string | Documentation comment |
| `commentTemplateRefs` | object[] | templateRefs for comment placeholders |
| `decorators` | object[] | Property-level decorators |

#### `classes[].customCode[]` items
| Field | Type | Description |
|---|---|---|
| `code` | string | The code for exactly one member (method or initialized field) |
| `templateRefs` | object[] | `[{"placeholder": "$user", "typeIdentifier": "user"}]` for internal type refs |

#### `classes[].decorators[]` items
| Field | Type | Description |
|---|---|---|
| `code` | string | Decorator code (e.g., `"@Injectable({ providedIn: 'root' })"`) |
| `templateRefs` | object[] | templateRefs for $placeholders in the decorator code |

#### `classes[].customImports[]` items
| Field | Type | Description |
|---|---|---|
| `path` | string | Import path (e.g., `"@angular/core"`, `"rxjs"`) |
| `types` | string[] | Named imports from that path (e.g., `["Injectable", "inject"]`) |

---

### `interfaces[]` items

Same structure as `classes[]` with these differences:
- No `isAbstract`, no `constructorParameters`, no `baseClassTypeIdentifier`
- Has `interfaceTypeIdentifiers[]` for extending other interfaces
- Interface properties generate `{ get; }` in C#, type-only in TypeScript
- **Method signatures go in `customCode`** — do NOT use function-typed properties if a class will implement the interface

| Field | Type | Description |
|---|---|---|
| `name` | string | Interface name |
| `typeIdentifier` | string | Unique ID for cross-referencing |
| `path` | string | Directory path |
| `fileName` | string | Custom file name (important: TypeScript strips `I` prefix from name) |
| `comment` | string | Documentation comment |
| `interfaceTypeIdentifiers` | string[] | Interfaces this interface extends |
| `genericArguments` | object[] | Generic parameters |
| `properties` | object[] | Same structure as class properties |
| `customCode` | object[] | Method signatures |
| `decorators` | object[] | Interface-level decorators |
| `customImports` | object[] | External library imports |

---

### `enums[]` items

| Field | Type | Description |
|---|---|---|
| `name` | string | Enum name |
| `typeIdentifier` | string | Unique ID for cross-referencing |
| `path` | string | Directory path |
| `fileName` | string | Custom file name |
| `comment` | string | Documentation comment |
| `members` | object[] | `[{"name": "Pending", "value": 0}, ...]` |

**Note:** Enums auto-suffix filenames: `order-status.enum.ts` (TypeScript), `OrderStatus.cs` (C#).

---

### `arrayTypes[]` items — VIRTUAL (no files generated)

| Field | Type | Description |
|---|---|---|
| `typeIdentifier` | string (required) | Unique ID to reference this array type |
| `elementTypeIdentifier` | string | Reference to custom type (User, Order, etc.) |
| `elementPrimitiveType` | enum | `"String"`, `"Number"`, `"Boolean"`, `"Date"`, `"Any"` |

Use by referencing `typeIdentifier` in properties of file-generating types.

**C# note:** `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs instead.

---

### `dictionaryTypes[]` items — VIRTUAL (no files generated)

| Field | Type | Description |
|---|---|---|
| `typeIdentifier` | string (required) | Unique ID to reference this dictionary type |
| `keyPrimitiveType` | enum | `"String"`, `"Number"`, `"Boolean"`, `"Date"`, `"Any"` |
| `keyTypeIdentifier` | string | Reference to custom key type |
| `keyType` | string | String literal for key type |
| `valuePrimitiveType` | enum | `"String"`, `"Number"`, `"Boolean"`, `"Date"`, `"Any"` |
| `valueTypeIdentifier` | string | Reference to custom value type |

Supports all 4 combinations (primitive/custom × primitive/custom) for key and value.

---

### `concreteGenericClasses[]` items — VIRTUAL (no files generated)

| Field | Type | Description |
|---|---|---|
| `identifier` | string | Unique ID for this concrete implementation |
| `genericClassIdentifier` | string | References the generic class definition |
| `genericArguments` | object[] | `[{"typeIdentifier": "user"}]` or `[{"primitiveType": "String"}]` |

Creates a virtual `Repository<User>` type. Use `baseClassTypeIdentifier` on a class to extend it. MetaEngine generates `extends Repository<User>` with correct imports.

---

### `concreteGenericInterfaces[]` items — VIRTUAL (no files generated)

| Field | Type | Description |
|---|---|---|
| `identifier` | string | Unique ID |
| `genericClassIdentifier` | string | References the generic interface definition |
| `genericArguments` | object[] | `[{"typeIdentifier": "..."}]` or `[{"primitiveType": "..."}]` |

---

### `customFiles[]` items — generates files WITHOUT a class wrapper

| Field | Type | Description |
|---|---|---|
| `name` | string | File name (without extension) |
| `identifier` | string | Optional ID; enables import resolution from other files via `customImports` |
| `path` | string | Directory path |
| `fileName` | string | Custom file name override |
| `customCode` | object[] | One item per export/type alias/function |
| `customImports` | object[] | External library imports |

Perfect for: type aliases, barrel exports, utility functions, constants.

---

## Critical Rules (Failures Most Commonly Caused By Violations)

### Rule 1: Generate ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Cross-file imports only resolve within a single batch — never split related types across calls.

### Rule 2: Properties = type declarations. CustomCode = everything else.
- `properties[]`: field declarations with types only. No initialization, no logic.
- `customCode[]`: methods, initialized fields, any code with logic. ONE item = exactly one member.
- **Never put methods in properties. Never put uninitialized type declarations in customCode.**

### Rule 3: Use templateRefs for internal types in customCode
When `customCode` references a type from the same batch, use `$placeholder` syntax with `templateRefs`. This triggers automatic import resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

Without templateRefs, MetaEngine cannot generate the import. **This is especially critical in C#** — every internal type reference in customCode MUST use templateRefs or `using` directives for cross-namespace types won't be generated.

### Rule 4: Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

| Language | Auto-imported (never specify) |
|---|---|
| TypeScript | (no imports needed — built-in types) |
| C# | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.) |

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5: templateRefs are ONLY for internal types
- Internal type (same MCP call) → use `typeIdentifier` or `templateRefs`
- External library type → use `customImports`
- Never mix these two mechanisms.

### Rule 6: Constructor parameters auto-create properties (C#, Java, Go, Groovy)
In C#, Java, Go, and Groovy, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]` — causes "Sequence contains more than one matching element" errors.

```jsonc
// WRONG (C#/Java/Go/Groovy)
"constructorParameters": [{"name": "email", "type": "string"}],
"properties": [{"name": "email", "type": "string"}]  // DUPLICATE!

// CORRECT
"constructorParameters": [{"name": "email", "type": "string"}]
// Additional non-constructor properties go in properties[] only
```

Note: In **TypeScript**, constructorParameters also auto-become properties.

### Rule 7: Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, and `concreteGenericInterfaces` create reusable type references only. They never produce files. Reference their `typeIdentifier` in properties of file-generating types.

---

## TypeScript-Specific Notes

- MetaEngine strips `I` prefix from interface names. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control the file name if collisions arise (e.g., `"fileName": "i-user-repository"`).
- Primitive type mapping: `String` → `string`, `Number` → `number`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n` in code strings gets indented correctly)
- Decorators are fully supported
- No customImports needed for TypeScript built-ins

---

## Output Structure

MetaEngine returns generated file contents. For each type that generates a file:
- `classes` → `<name>.ts` (or `<fileName>.ts` if specified)
- `interfaces` → `<name>.ts` with `I` prefix stripped from the exported name
- `enums` → `<name>.enum.ts`
- `customFiles` → `<name>.ts` (no class wrapper)
- `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` → NO files

Files are written to `outputPath` (default: current directory), preserving `path` subdirectory structure.

---

## Pattern Reference — TypeScript

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

### Enum + class that uses it
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

### Service with external dependency injection (Angular example)
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

### Interface with method signatures (for implementing class)
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

### Complex type expressions with templateRefs in properties
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
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

### CustomFiles for type aliases and barrel exports
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

The `identifier` on the customFile enables import resolution. `customImports` referencing the identifier auto-resolves to the relative path.

---

## Common Mistakes to Avoid

1. **Don't** reference a `typeIdentifier` that doesn't exist in the batch → the property is silently dropped. Verify every typeIdentifier matches a defined type in the same call.

2. **Don't** put method signatures as function-typed properties on interfaces you'll `implements`. Use `customCode` for interface method signatures when a class will implement them.

3. **Don't** write internal type names as raw strings in customCode (e.g., `"code": "private repo: IUserRepository"`). Use templateRefs: `"code": "private repo: $repo"` with `"templateRefs": [{"placeholder": "$repo", "typeIdentifier": "user-repo"}]`.

4. **Don't** use `arrayTypes` in C# when you need `List<T>`. Use `"type": "List<$user>"` with templateRefs for mutable list types.

5. **Don't** add `System.*`, `typing.*`, `java.util.*` etc. to customImports. MetaEngine handles all framework imports automatically.

6. **Don't** duplicate constructor parameter names in the `properties` array (C#/Java/Go/Groovy/TypeScript). Put shared fields only in `constructorParameters`.

7. **Don't** use reserved words (`delete`, `class`, `import`) as property names. Use safe alternatives (`remove`, `clazz`, `importData`).

8. **Don't** generate related types in separate MCP calls. Batch everything in one call — cross-file imports only resolve within a single batch.

9. **Don't** expect `Number` to map to `double` in C# — it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly when needed.

10. **Don't** forget `fileName` when both an `I`-prefixed interface and its implementing class would collide in TypeScript. Set `"fileName": "i-user-repository"` on the interface to prevent file name conflicts.

---

## Summary of Key Concepts

- **One call rule**: All cross-referencing types MUST be in the same `generate_code` call.
- **typeIdentifier**: The linking mechanism. Set it on any type you want others to reference.
- **templateRefs**: The import trigger for internal types inside `customCode`, `type` strings, and `decorators`. Format: `[{"placeholder": "$name", "typeIdentifier": "some-id"}]`.
- **Virtual types**: `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` — reusable type references only, no files produced.
- **customFiles**: File-generating container without a class/interface wrapper — use for utilities, aliases, and barrels.
- **Properties vs customCode**: Properties = type-only field declarations. CustomCode = one method or initialized field per item.
- **Auto-imports**: Framework/standard library types are always auto-imported. Never add them to `customImports`.
