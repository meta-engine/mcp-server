# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files. It resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

Supported languages: TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP.

---

## Tools Exposed

### `mcp__metaengine__metaengine_initialize`
- **Purpose**: Returns critical MetaEngine concepts, patterns, and documentation resources.
- **When to call**: Before generating code for the first time, or when guidance is needed.
- **Parameters**: `language` (optional enum) — if specified, returns language-specific patterns.

### `mcp__metaengine__generate_code`
- **Purpose**: Main code generation tool. Takes structured JSON describing types and produces source files.
- **Input**: A JSON object with top-level arrays (`classes`, `interfaces`, `enums`, `customFiles`, `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) plus a `language` field.

### `mcp__metaengine__generate_graphql`
- Generates GraphQL schema from spec.

### `mcp__metaengine__generate_openapi`
- Generates OpenAPI spec from description.

### `mcp__metaengine__generate_protobuf`
- Generates Protobuf definitions from spec.

### `mcp__metaengine__generate_sql`
- Generates SQL schema from spec.

### `mcp__metaengine__load_spec_from_file`
- Loads a spec from a file path for use as input to other generation tools.

---

## `generate_code` — Input Schema (Full)

Top-level object fields:

| Field | Type | Description |
|-------|------|-------------|
| `language` | string (enum) | Target language: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php` |
| `classes` | array | Class definitions that produce files |
| `interfaces` | array | Interface definitions that produce files |
| `enums` | array | Enum definitions that produce files |
| `customFiles` | array | Freeform files (type aliases, barrel exports, utility code) |
| `arrayTypes` | array | Virtual — define reusable `T[]` type references, produce NO files |
| `dictionaryTypes` | array | Virtual — define reusable `Map<K,V>` type references, produce NO files |
| `concreteGenericClasses` | array | Virtual — define `Repository<User>` specializations, produce NO files |
| `concreteGenericInterfaces` | array | Virtual — define `IRepository<User>` specializations, produce NO files |

### Class / Interface fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Class/interface name (e.g. `"UserService"`) |
| `typeIdentifier` | string | Stable slug for cross-referencing within the batch (e.g. `"user-service"`) |
| `fileName` | string | Override the generated filename (important when TS strips `I` from interface names) |
| `path` | string | Subdirectory where file is placed |
| `packageName` | string | Namespace (C#) or package (Go/Java/Kotlin) |
| `isAbstract` | boolean | Marks class/interface as abstract |
| `baseClassTypeIdentifier` | string | `typeIdentifier` of the parent class (sets `extends`) |
| `implementsTypeIdentifiers` | string[] | `typeIdentifier`s of implemented interfaces (sets `implements`) |
| `genericArguments` | array | Generic type parameters (see Generic section) |
| `properties` | array | Field/property declarations (type only, no logic) |
| `customCode` | array | Methods, initialized fields, any code with logic |
| `customImports` | array | External library imports |
| `decorators` | array | Class-level decorators/annotations |
| `constructorParameters` | array | Constructor params — auto-become properties in C#/Java/Go/Groovy |

### Property fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | string enum | `String`, `Number`, `Boolean`, `Date`, `Any` — auto-mapped per language |
| `typeIdentifier` | string | References another type in the batch |
| `type` | string | Raw type string (use with `templateRefs` for internal refs) |
| `templateRefs` | array | `{placeholder, typeIdentifier}` pairs — replaces `$placeholder` in `type` and triggers import |
| `isOptional` | boolean | Makes the property optional/nullable |
| `isArray` | boolean | Wraps type in array |
| `decorators` | array | Property-level decorators/annotations |

### CustomCode fields

| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Full member code (method, initialized field, etc.). One item = one member. |
| `templateRefs` | array | `{placeholder, typeIdentifier}` — replaces `$placeholder` in `code` and generates import |

### CustomImports fields (for external libraries only)

| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (e.g. `"@angular/core"`) or file identifier |
| `types` | string[] | Named imports from the path |

### Enum fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Slug for cross-references |
| `members` | array | `{name, value}` pairs |

Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).
In Java/Kotlin, enum member names are auto-UPPERCASED.

### ArrayType fields

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string | Slug to reference this array type in properties |
| `elementTypeIdentifier` | string | `typeIdentifier` of element type (internal) |
| `elementPrimitiveType` | string | Primitive type of elements (`String`, `Number`, etc.) |

### DictionaryType fields

| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string | Slug to reference this dict type |
| `keyPrimitiveType` | string | Key primitive type |
| `valuePrimitiveType` | string | Value primitive type |
| `keyTypeIdentifier` | string | Key from internal type |
| `valueTypeIdentifier` | string | Value from internal type |

### ConcreteGenericClass / ConcreteGenericInterface fields

| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | Slug for the concrete specialization (used as `baseClassTypeIdentifier`) |
| `genericClassIdentifier` | string | `typeIdentifier` of the generic class template |
| `genericArguments` | array | `{typeIdentifier}` list of type arguments to fill generic params |

### CustomFile fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name |
| `path` | string | Subdirectory |
| `identifier` | string | Slug — enables other files to `customImport` this file by identifier |
| `customCode` | array | Code items (same structure as class customCode) |

### Generic argument fields (on classes/interfaces)

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Type parameter name (e.g. `"T"`) |
| `constraintTypeIdentifier` | string | Bound: `T extends BaseEntity` |
| `propertyName` | string | Auto-creates a property of type `T[]` with this name |
| `isArrayProperty` | boolean | Whether the auto-property is an array of T |

---

## Critical Rules

### Rule 1: Generate ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting across calls silently drops cross-references and imports.

### Rule 2: properties[] = type declarations only; customCode[] = everything else
- `properties[]` — field declarations with type only, no initialization, no logic.
- `customCode[]` — methods, initialized fields, any code with logic. One item = exactly one member.
- Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

### Rule 3: Use templateRefs for internal types in customCode
When `customCode` references a type from the same batch, use `$placeholder` syntax with `templateRefs`. Without this, MetaEngine cannot generate the import/using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**Critical in C#**: Every internal type reference in customCode MUST use templateRefs, or `using` directives for cross-namespace types won't be generated. Raw strings like `IUserRepository` without templateRefs will compile-fail across namespaces.

### Rule 4: Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

Auto-imported (never specify manually):
- **C#**: System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*
- **Python**: typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses
- **Java**: java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*
- **Kotlin**: java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*
- **Go**: time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more
- **Swift**: Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)
- **TypeScript**: no imports needed — built-in types
- **Groovy**: java.time.*, java.math.*, java.util (UUID, Date), java.io.*
- **Scala**: java.time.*, scala.math.*, java.util.UUID, scala.collection.mutable.*
- **PHP**: DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable

Only use `customImports` for **external** libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5: templateRefs are ONLY for internal types
- Internal (same MCP call) → use `typeIdentifier` or `templateRefs`
- External library → use `customImports`
- Never mix these two mechanisms.

### Rule 6: Constructor parameters auto-create properties (C#/Java/Go/Groovy)
In these languages, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]` — causes "Sequence contains more than one matching element" errors.

### Rule 7: Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, and `concreteGenericInterfaces` create reusable type references only. They never produce output files. Use their `typeIdentifier` in properties of file-generating types.

---

## TypeScript-Specific Notes

- MetaEngine **strips `I` prefix** from interface names for the exported symbol. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control the filename if collisions arise with an implementing class.
- Primitive type mappings: `String` → `string`, `Number` → `number`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly on classes and properties
- No `customImports` needed for built-in TypeScript types
- Enum files auto-suffixed: `order-status.enum.ts`
- Interface method signatures belong in `customCode`, not as function-typed properties, when a class will `implements` the interface (otherwise the implementing class duplicates them as property declarations)

---

## Output Structure

MetaEngine returns an array of generated files. Each file has:
- A relative `path` (e.g., `src/models/user.ts`)
- The `content` string of the generated source code

Files include:
- Correct imports/using directives for all cross-referenced types in the batch
- Language-idiomatic transformations (TypeScript lowercase primitives, Java ALL_CAPS enums, Python snake_case methods)
- Proper file naming conventions per language

---

## Pattern Examples (TypeScript)

### Basic interface cross-reference
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

### Array and dictionary virtual types
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
Then reference via `"typeIdentifier": "user-list"` in properties of file-generating types.

### Complex type expressions with templateRefs in properties
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
templateRefs work in `properties`, `customCode`, and `decorators`.

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

### Service with Angular DI
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

### Custom files (type aliases, barrel exports)
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
The `identifier` on `customFile` enables import resolution via `customImports` path reference — MetaEngine resolves to the relative file path automatically.

### Interface with method signatures (for `implements`)
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
Use `customCode` for method signatures on interfaces that will be implemented (not function-typed properties), otherwise implementing classes duplicate them as property declarations.

---

## Common Mistakes to Avoid

1. **Referencing a typeIdentifier that doesn't exist in the batch** → property silently dropped. Verify every typeIdentifier matches a defined type in the same call.

2. **Putting method signatures as function-typed properties on interfaces** you'll `implements` → implementing class duplicates them. Use `customCode` instead.

3. **Writing internal type names as raw strings in customCode** (e.g., `"code": "private repo: IUserRepository"`) → no import generated. Use templateRefs: `"code": "private repo: $repo"` with `"templateRefs": [{"placeholder": "$repo", "typeIdentifier": "user-repo"}]`.

4. **Using `arrayTypes` in C# when you need `List<T>`** → arrayTypes generates `IEnumerable<T>`. Use `"type": "List<$user>"` with templateRefs for mutable list types.

5. **Adding System.*, typing.*, java.util.* etc. to customImports** → duplication errors. Let MetaEngine handle framework imports automatically.

6. **Duplicating constructor parameter names in `properties[]`** (C#/Java/Go/Groovy) → "Sequence contains more than one matching element" error. Put shared fields only in `constructorParameters`.

7. **Using reserved words as property names** (`delete`, `class`, `import`) → use safe alternatives (`remove`, `clazz`, `importData`).

8. **Generating related types in separate MCP calls** → cross-file imports only resolve within a single batch. Always batch everything in one call.

9. **Expecting `Number` to map to `double` in C#** → it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.

10. **Forgetting `fileName` when both an `I`-prefixed interface and its implementing class would collide in TypeScript** → set `"fileName": "i-user-repository"` on the interface to prevent file name conflicts.

---

## Summary Checklist Before Calling generate_code

- [ ] All cross-referenced `typeIdentifier`s exist in the same call
- [ ] `properties[]` contains only type declarations (no methods, no initialized fields)
- [ ] `customCode[]` has one item per member
- [ ] Internal type references in `customCode` use `$placeholder` + `templateRefs`
- [ ] `customImports` only lists external libraries
- [ ] Constructor params not duplicated in `properties[]` (C#/Java/Go/Groovy)
- [ ] Virtual types (arrayTypes, dictionaryTypes, concreteGeneric*) are referenced by typeIdentifier in real types
- [ ] TypeScript interfaces that will be implemented use `customCode` for method signatures, not function-typed properties
- [ ] `fileName` set on TypeScript `I`-prefixed interfaces when a same-named implementing class exists
