# MetaEngine MCP — Knowledge Brief

## Overview

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. It resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

### `mcp__metaengine__generate_code`
Primary tool. Accepts a structured JSON spec and writes source files to disk.  
**Required**: `language`  
**Optional**: `outputPath` (default `.`), `skipExisting` (default `true`), `dryRun` (default `false`), `initialize` (default `false`), `packageName`

### `mcp__metaengine__load_spec_from_file`
Same as `generate_code` but reads the spec from a `.json` file. Drastically reduces AI context usage for large specs.  
**Required**: `specFilePath` (absolute or relative path to a JSON file with the same structure as `generate_code`)  
**Optional**: `outputPath`, `skipExisting`, `dryRun` (all override values in the spec file)

### `mcp__metaengine__generate_graphql` / `generate_openapi` / `generate_protobuf` / `generate_sql`
Spec-conversion tools (not the focus here). Convert existing specs to MetaEngine format or target schema formats.

### `mcp__metaengine__metaengine_initialize`
Returns the canonical guide and linked resources for the AI session. Call when uncertain. Accepts optional `language` parameter for language-specific patterns.

---

## `generate_code` — Full Input Schema

```
{
  language:               string (required) — "typescript" | "python" | "go" | "csharp" | "java" | "kotlin" | "groovy" | "scala" | "swift" | "php" | "rust"
  outputPath:             string (optional, default ".") — directory where files are written
  packageName:            string (optional) — namespace/package/module. For C#: omit for GlobalUsings. Go default: "github.com/metaengine/demo". Java/Kotlin/Groovy default: "com.metaengine.generated"
  skipExisting:           boolean (optional, default true) — skip files that already exist
  dryRun:                 boolean (optional, default false) — preview mode, returns code without writing
  initialize:             boolean (optional, default false) — initialize properties with default values

  interfaces:             Interface[]
  classes:                Class[]
  enums:                  Enum[]
  customFiles:            CustomFile[]
  arrayTypes:             ArrayType[]         — virtual, NO files generated
  dictionaryTypes:        DictionaryType[]    — virtual, NO files generated
  concreteGenericClasses: ConcreteGeneric[]   — virtual, NO files generated
  concreteGenericInterfaces: ConcreteGenericInterface[] — virtual, NO files generated
}
```

### Interface shape
```
{
  name:                   string (required)
  typeIdentifier:         string (optional) — unique ID for cross-referencing
  path:                   string (optional) — subdirectory (e.g. "models", "services/auth")
  fileName:               string (optional) — override generated file name (no extension)
  comment:                string (optional) — documentation comment
  properties:             Property[]
  customCode:             CustomCodeItem[]
  customImports:          ImportItem[]
  decorators:             Decorator[]
  genericArguments:       GenericArgument[]
  interfaceTypeIdentifiers: string[] — extend other interfaces by typeIdentifier
}
```

### Class shape
```
{
  name:                   string (required)
  typeIdentifier:         string (optional) — unique ID for cross-referencing
  path:                   string (optional)
  fileName:               string (optional)
  comment:                string (optional)
  isAbstract:             boolean (optional)
  properties:             Property[]
  customCode:             CustomCodeItem[]
  customImports:          ImportItem[]
  decorators:             Decorator[]
  genericArguments:       GenericArgument[]
  constructorParameters:  ConstructorParam[]
  baseClassTypeIdentifier: string (optional) — typeIdentifier of the class to extend
  interfaceTypeIdentifiers: string[] — typeIdentifiers of interfaces to implement
}
```

### Enum shape
```
{
  name:           string (required)
  typeIdentifier: string (optional)
  path:           string (optional)
  fileName:       string (optional)
  comment:        string (optional)
  members:        [{ name: string, value: number }]
}
```
Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### Property shape
```
{
  name:           string (required)
  primitiveType:  "String" | "Number" | "Boolean" | "Date" | "Any"  (use for built-in types)
  typeIdentifier: string  (use to reference another type in the batch)
  type:           string  (use for complex/external types, e.g. "List<$user>", "Map<string, $resp>")
  templateRefs:   [{ placeholder: string, typeIdentifier: string }]  (required when using $placeholder in type)
  isOptional:     boolean
  isInitializer:  boolean — add default value initialization
  comment:        string
  commentTemplateRefs: object[]
  decorators:     Decorator[]
}
```

### CustomCodeItem shape
```
{
  code:         string (required) — one method, one initialized field, one type alias, etc.
  templateRefs: [{ placeholder: string, typeIdentifier: string }]  (required when code uses $placeholder)
}
```

### ImportItem shape
```
{
  path:  string (required) — external package path OR identifier of a customFile in the same batch
  types: string[] (optional) — named imports from that path
}
```

### Decorator shape
```
{
  code:         string (required)
  templateRefs: object[] (optional)
}
```

### GenericArgument shape
```
{
  name:                    string — generic parameter name (e.g. "T", "K")
  constraintTypeIdentifier: string (optional) — typeIdentifier for "where T : X" constraint
  propertyName:            string (optional) — creates a property of type T with this name
  isArrayProperty:         boolean (optional) — if true, the property is T[]
}
```

### ConstructorParam shape
```
{
  name:           string
  primitiveType:  "String" | "Number" | "Boolean" | "Date" | "Any"
  typeIdentifier: string
  type:           string
}
```
**WARNING (C#/Java/Go/Groovy)**: Constructor parameters auto-create properties. Do NOT also list them in `properties[]` — causes duplicate errors.

### ArrayType shape (virtual — no file generated)
```
{
  typeIdentifier:       string (required) — ID to reference this array type
  elementTypeIdentifier: string (optional) — for custom element type
  elementPrimitiveType: "String" | "Number" | "Boolean" | "Date" | "Any" (optional)
}
```

### DictionaryType shape (virtual — no file generated)
```
{
  typeIdentifier:    string (required)
  keyPrimitiveType:  "String" | "Number" | "Boolean" | "Date" | "Any"
  keyTypeIdentifier: string
  keyType:           string — raw string literal for key type
  valuePrimitiveType: "String" | "Number" | "Boolean" | "Date" | "Any"
  valueTypeIdentifier: string
}
```

### ConcreteGenericClass shape (virtual — no file generated)
```
{
  identifier:             string (required) — ID for this concrete type
  genericClassIdentifier: string — references the generic class definition
  genericArguments:       [{ typeIdentifier: string, primitiveType: string }]
}
```

### ConcreteGenericInterface shape (virtual — no file generated)
```
{
  identifier:             string
  genericClassIdentifier: string — references the generic interface definition
  genericArguments:       [{ typeIdentifier: string, primitiveType: string }]
}
```

### CustomFile shape
```
{
  name:          string (required) — file name (without extension)
  path:          string (optional) — directory path
  fileName:      string (optional) — override file name
  identifier:    string (optional) — enables referencing this file from customImports in other items
  customCode:    CustomCodeItem[]
  customImports: ImportItem[]
}
```
CustomFiles generate files WITHOUT a class wrapper. Perfect for: type aliases, barrel exports (`export * from ...`), standalone utility functions.

---

## Critical Rules (must follow — most failures come from violating these)

### Rule 1: ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting related types across calls causes missing imports and unresolved references.

### Rule 2: properties[] = type declarations ONLY; customCode[] = everything with logic
- `properties[]` → field declarations (name + type, no initialization, no logic)
- `customCode[]` → methods, initialized fields, anything with `=` or `{ }` body
- One `customCode` item = exactly one member (method or initialized field)
- NEVER put methods in `properties[]`. NEVER put uninitialized type declarations in `customCode[]`.

### Rule 3: Use templateRefs for ALL internal type references in customCode
When `customCode` or `type` strings reference a type from the same batch, use `$placeholder` + `templateRefs`. Without it, MetaEngine cannot generate the import/using directive.
```jsonc
"code": "getUser(): Promise<$user> { ... }",
"templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
```
**This is especially critical in C#** — every internal type in customCode must use templateRefs or `using` directives won't be generated, causing compile failures across namespaces.

### Rule 4: Never add framework/stdlib imports to customImports
MetaEngine auto-imports standard library types per language (see table below). Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

Auto-imported (NEVER specify in customImports):
| Language   | Auto-imported                                                                                    |
|------------|--------------------------------------------------------------------------------------------------|
| C#         | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*   |
| Python     | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses                 |
| Java       | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*       |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*                               |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)                |
| Rust       | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde                           |
| Groovy     | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream)     |
| Scala      | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.*         |
| PHP        | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable              |
| TypeScript | (no imports needed — built-in types)                                                             |

### Rule 5: templateRefs ONLY for internal types; customImports ONLY for external
- Type in same batch → use `typeIdentifier` or `templateRefs`
- External library → use `customImports`
- Never mix these

### Rule 6: No duplicate constructor parameters in properties[] (C#/Java/Go/Groovy)
In these languages, constructor parameters automatically become class properties. Listing the same name in `properties[]` causes "Sequence contains more than one matching element" errors. Only add to `properties[]` fields that are NOT in `constructorParameters`.

### Rule 7: Virtual types never generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` — these create reusable type references only. They produce no source files. Use them by referencing their `typeIdentifier` in other types' `properties`.

---

## TypeScript-Specific Notes

- MetaEngine **strips `I` prefix** from interface names. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control the file name if the interface and its implementation class would collide.
- Primitive type mapping: `String` → `string`, `Number` → `number`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly on classes and properties
- No imports needed for built-in types — TypeScript section of customImports is only for external packages
- Interface method signatures belong in `customCode`, NOT as function-typed `properties`. If you use function-typed properties (e.g. `"type": "() => Promise<User[]>"`), the implementing class will duplicate them as property declarations alongside your `customCode` methods.

---

## Output Structure

Each item in `interfaces`, `classes`, `enums`, `customFiles` generates exactly one source file. The file is written to `{outputPath}/{path}/{fileName}.{ext}`. MetaEngine determines the file extension from the `language` field.

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, and `concreteGenericInterfaces` generate NO files — they only create type tokens usable by other items in the same call.

The engine:
1. Resolves all `typeIdentifier` cross-references within the batch
2. Generates correct import statements / using directives / from clauses automatically
3. Applies language-idiomatic transformations (Java `ALL_CAPS` enums, Python `snake_case` methods, etc.)
4. Writes files (or returns content if `dryRun: true`)

With `dryRun: true`, file contents are returned in the response for review without touching disk.

With `skipExisting: true` (default), existing files are not overwritten — useful for stub/scaffold patterns.

---

## Common Patterns

### Two interfaces with cross-reference (TypeScript)
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

### Generic class + concrete instantiation
```jsonc
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

### Interface with method signatures (not function-typed properties)
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

### Complex type expression with templateRefs
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

### CustomFile for type aliases and barrel exports
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
Note: `identifier` on the customFile enables import resolution via path — MetaEngine resolves the relative path automatically.

### Array and dictionary virtual types
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

---

## `load_spec_from_file` — Usage

Write the same JSON structure as `generate_code` to a `.json` file, then call:
```jsonc
{
  "specFilePath": "specs/user-system.json",
  "outputPath": "src"
}
```
The `language`, all type arrays, and generation options live inside the spec file. `outputPath`, `skipExisting`, and `dryRun` passed to `load_spec_from_file` override whatever is in the spec file.

**Benefit**: Avoids context bloat for large architectures. The spec file can be version-controlled and reused.

---

## Common Mistakes (Top 10)

1. **Referencing a typeIdentifier not in the batch** → property silently dropped. Verify every `typeIdentifier` matches a defined type in the SAME call.

2. **Interface method signatures as function-typed properties** → implementing class duplicates them as property declarations. Use `customCode` for interface method signatures.

3. **Raw internal type names in customCode strings** (e.g., `"code": "private repo: IUserRepository"`) → missing imports. Use `"code": "private repo: $repo"` with templateRefs.

4. **Using arrayTypes for C# List<T>** → generates `IEnumerable<T>` not `List<T>`. Use `"type": "List<$user>"` with templateRefs instead.

5. **Adding stdlib/framework types to customImports** → duplication or errors. Let MetaEngine handle all standard library imports.

6. **Duplicate constructor parameters in properties[] for C#/Java/Go/Groovy** → "Sequence contains more than one matching element" error.

7. **Using reserved words as property names** (`delete`, `class`, `import`) → use safe alternatives (`remove`, `clazz`, `importData`).

8. **Splitting related types across multiple calls** → cross-file imports only resolve within a single batch. Batch everything in one call.

9. **Expecting Number → double in C#** → it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.

10. **IUserRepository interface and UserRepository class colliding filenames in TypeScript** (MetaEngine strips `I` prefix) → set `"fileName": "i-user-repository"` on the interface.

---

## Key Summary for Generation

- **One call per cohesive feature** — all types that reference each other must be in the same `generate_code` call.
- **`typeIdentifier`** is your cross-reference key — assign to every type you want to reference elsewhere.
- **`templateRefs`** is how you get imports generated for internal types inside `customCode` or complex `type` strings.
- **Virtual types** (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) exist only to be referenced — they produce no files.
- **`customFiles`** produce files without class wrappers — use for type aliases, utilities, barrel exports.
- **`customImports`** is only for external libraries — MetaEngine handles all standard library imports itself.
- **`dryRun: true`** for preview; `skipExisting: true` (default) for scaffold/stub patterns.
