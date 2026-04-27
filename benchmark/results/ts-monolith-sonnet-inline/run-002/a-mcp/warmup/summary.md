# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, and PHP. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

- `mcp__metaengine__generate_code`: Main code generation tool. Takes a JSON spec describing types, classes, interfaces, enums, etc. and produces compilable source files with automatic imports.
- `mcp__metaengine__generate_graphql`: Generates GraphQL schemas.
- `mcp__metaengine__generate_openapi`: Generates OpenAPI specs.
- `mcp__metaengine__generate_protobuf`: Generates Protobuf definitions.
- `mcp__metaengine__generate_sql`: Generates SQL schemas.
- `mcp__metaengine__load_spec_from_file`: Loads an existing spec from a file for generation.
- `mcp__metaengine__metaengine_initialize`: Returns essential MetaEngine patterns and documentation resources. Call this before generating code for the first time.

---

## generate_code — Input Schema (Full)

The top-level input object accepts the following keys:

### Top-level fields
| Field | Type | Description |
|-------|------|-------------|
| `language` | string (enum) | Required. One of: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php` |
| `outputPath` | string | Directory where files are written |
| `packageName` | string | Sets namespace (C#), package (Java/Kotlin/Go), module prefix |
| `classes` | array | Class definitions (see below) |
| `interfaces` | array | Interface definitions (see below) |
| `enums` | array | Enum definitions (see below) |
| `arrayTypes` | array | Virtual array type references (no files generated) |
| `dictionaryTypes` | array | Virtual dictionary type references (no files generated) |
| `concreteGenericClasses` | array | Virtual concrete-generic type references (no files generated) |
| `concreteGenericInterfaces` | array | Virtual concrete-generic interface references (no files generated) |
| `customFiles` | array | Arbitrary files with custom code (barrel exports, type aliases) |

### Class object fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Class name |
| `typeIdentifier` | string | Unique key used to reference this type within the batch (kebab-case recommended) |
| `fileName` | string | Override the generated file name (without extension) |
| `path` | string | Subdirectory within outputPath |
| `packageName` | string | Override package/namespace for this file |
| `isAbstract` | boolean | Generates abstract class |
| `baseClassTypeIdentifier` | string | `typeIdentifier` of the parent class (extends) |
| `implementsTypeIdentifiers` | array of string | `typeIdentifier`s of interfaces this class implements |
| `genericArguments` | array | Generic type parameters (see below) |
| `constructorParameters` | array | Constructor params — auto-creates properties in C#/Java/Go/Groovy (do NOT also list in `properties[]`) |
| `properties` | array | Field declarations (type only, no logic) |
| `customCode` | array | Methods and initialized fields — one member per item |
| `decorators` | array | Class-level decorators/annotations |
| `customImports` | array | Imports for external libraries only |

### Interface object fields
Same as class but no `baseClassTypeIdentifier`, `constructorParameters`, or `isAbstract`. Has `implementsTypeIdentifiers` for interface inheritance.

### Enum object fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Enum name |
| `typeIdentifier` | string | Unique key for referencing |
| `fileName` | string | Override file name |
| `path` | string | Subdirectory |
| `members` | array | `[{name: string, value: number|string}]` |

Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### Property object fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Property name |
| `primitiveType` | string | One of: `String`, `Number`, `Boolean`, `Date`, `Any` |
| `typeIdentifier` | string | Reference to an internal type (from same batch) |
| `type` | string | Raw type string — use with `templateRefs` for complex expressions |
| `isOptional` | boolean | Makes property optional/nullable |
| `isArray` | boolean | Wraps type in array |
| `templateRefs` | array | Placeholder resolution for `$placeholder` in `type` field |

### CustomCode object fields
| Field | Type | Description |
|-------|------|-------------|
| `code` | string | The source code for exactly one member (method or initialized field) |
| `templateRefs` | array | `[{placeholder: "$name", typeIdentifier: "some-id"}]` — resolves `$placeholder` in code and generates imports |

### templateRefs object fields
| Field | Type | Description |
|-------|------|-------------|
| `placeholder` | string | The `$placeholder` string in code/type to replace |
| `typeIdentifier` | string | The `typeIdentifier` of the internal type to resolve |

### Decorator object fields
| Field | Type | Description |
|-------|------|-------------|
| `code` | string | Full decorator string e.g. `@Injectable({ providedIn: 'root' })` |
| `templateRefs` | array | Optional placeholder resolution within decorator code |

### CustomImport object fields
| Field | Type | Description |
|-------|------|-------------|
| `path` | string | Import path (e.g. `@angular/core`, `rxjs/operators`) |
| `types` | array of string | Named imports from that path |

### arrayTypes object fields
| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string | Unique key to reference this array type |
| `elementTypeIdentifier` | string | Internal type identifier for the element type |
| `elementPrimitiveType` | string | Primitive type for element (String, Number, etc.) |

### dictionaryTypes object fields
| Field | Type | Description |
|-------|------|-------------|
| `typeIdentifier` | string | Unique key to reference this dictionary type |
| `keyPrimitiveType` | string | Primitive type for keys |
| `valuePrimitiveType` | string | Primitive type for values |
| `valueTypeIdentifier` | string | Internal type identifier for values |

### concreteGenericClasses / concreteGenericInterfaces object fields
| Field | Type | Description |
|-------|------|-------------|
| `identifier` | string | Unique key to reference this concrete generic (used in baseClassTypeIdentifier) |
| `genericClassIdentifier` | string | The `typeIdentifier` of the generic class |
| `genericArguments` | array | `[{typeIdentifier: "some-id"}]` — the type arguments to fill in |

### customFiles object fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | File name (without extension) |
| `path` | string | Subdirectory |
| `identifier` | string | Unique key so other files can import this via customImports |
| `customCode` | array | Code items (same structure as class customCode) |

### genericArguments object fields (on classes)
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The generic type parameter name (e.g. `T`) |
| `constraintTypeIdentifier` | string | Constraint type (e.g. `base-entity` → `T extends BaseEntity`) |
| `propertyName` | string | Auto-generates a property of this generic type on the class |
| `isArrayProperty` | boolean | Makes the auto-generated property an array |

---

## Critical Rules

### Rule 1 — Generate ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Never split related types into separate calls — cross-file imports only resolve within a single batch.

### Rule 2 — Properties = type declarations only; CustomCode = everything else
`properties[]` declares fields with types only (no initialization, no logic). `customCode[]` handles methods, initialized fields, and any code with logic. One `customCode` item = exactly one member.

```jsonc
// Property: type only, no initialization
"properties": [{"name": "id", "primitiveType": "String"}]

// CustomCode: method or initialized field
"customCode": [
  {"code": "private http = inject(HttpClient);"},
  {"code": "getAll(): T[] { return this.items; }"}
]
```

Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

### Rule 3 — Use templateRefs for internal types in customCode
When customCode references a type from the same batch, use `$placeholder` syntax with `templateRefs`. This triggers automatic import resolution. Without templateRefs, MetaEngine cannot generate the import/using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

Critical in C#: every internal type reference in customCode MUST use templateRefs, or `using` directives for cross-namespace types won't be generated. Raw strings like `IUserRepository` without templateRefs will compile-fail across namespaces.

### Rule 4 — Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

| Language   | Auto-imported (never specify manually)                                                           |
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

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5 — templateRefs are ONLY for internal types
External library types must use `customImports`. If it's in the same MCP call → use `typeIdentifier` or `templateRefs`. If it's an external library → use `customImports`. Never mix these.

### Rule 6 — Constructor parameters auto-create properties (C#/Java/Go/Groovy)
In C#, Java, Go, and Groovy, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]` — this causes "Sequence contains more than one matching element" errors.

```jsonc
// WRONG for C#/Java/Go/Groovy
"constructorParameters": [{"name": "email", "type": "string"}],
"properties": [{"name": "email", "type": "string"}]  // DUPLICATE!

// CORRECT — only in constructorParameters
"constructorParameters": [{"name": "email", "type": "string"}]
// additional non-constructor properties go in properties[] only
```

### Rule 7 — Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, and `concreteGenericInterfaces` create reusable type references only. They never produce files. They're used by referencing their `typeIdentifier` in properties of file-generating types.

---

## Output Structure

MetaEngine produces one source file per class/interface/enum/customFile defined. Files are placed at `outputPath/path/name.ext` (e.g., `src/models/user.ts`). All imports between files in the batch are resolved and injected automatically. The engine:
- Resolves cross-file imports within the batch
- Applies language-specific naming conventions (e.g., Java `ALL_CAPS` enums, Python `snake_case` methods, TypeScript strips `I` prefix from interface names)
- Manages package/namespace declarations
- Handles generic type expressions, inheritance, and interface implementations

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

**C# note**: `arrayTypes` generate `IEnumerable<T>`. If you need `List<T>`, use `"type": "List<$user>"` with templateRefs instead.

### Complex type expressions with templateRefs
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

### Service with external dependency injection (TypeScript/Angular)
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

### Interface with method signatures (TypeScript/C#)
For interfaces that will be `implements`/`:` by a class, define method signatures in `customCode`, NOT as function-typed properties:

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

If you use function-typed properties instead (e.g. `"type": "() => Promise<User[]>"`), the implementing class will duplicate them as property declarations alongside your customCode methods.

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
The `identifier` on the customFile enables import resolution. `customImports` referencing the identifier auto-resolves to the relative path.

---

## Language-Specific Notes

### TypeScript
- MetaEngine strips `I` prefix from interface names for the exported symbol: `IUserRepository` → exported as `UserRepository`. Use `fileName` to control the file name if collisions arise (e.g., `"fileName": "i-user-repository"`).
- `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly on classes
- No manual imports needed — all built-in types are available

### C#
- `I` prefix preserved on interface names
- `Number` → `int` (not `double`). Use `"type": "decimal"` or `"type": "double"` for non-integer numbers.
- `packageName` sets the namespace. Omit for GlobalUsings pattern.
- Interface properties generate `{ get; }`. Class properties generate `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `type` with templateRefs: `"type": "List<$user>"`
- `isOptional` on properties generates `string?` (nullable reference type)
- Every internal type reference in customCode MUST use templateRefs or `using` directives won't be generated

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode
- `typing` imports are automatic
- snake_case methods are applied automatically by the engine

### Go
- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode
- Constructor parameters auto-create properties/fields

### Java
- Constructor parameters auto-create properties
- `ALL_CAPS` enum member names are applied automatically by the engine
- `java.util.*`, `java.time.*` etc. are auto-imported

---

## Common Mistakes to Avoid

1. **Referencing a `typeIdentifier` that doesn't exist in the batch** → the property is silently dropped. Verify every typeIdentifier matches a defined type in the same call.

2. **Putting method signatures as function-typed properties on interfaces you'll `implements`** → use `customCode` for interface method signatures when a class will implement them.

3. **Writing internal type names as raw strings in customCode** (e.g., `"code": "private repo: IUserRepository"`) → use templateRefs: `"code": "private repo: $repo"` with `"templateRefs": [{"placeholder": "$repo", "typeIdentifier": "user-repo"}]`.

4. **Using `arrayTypes` in C# when you need `List<T>`** → use `"type": "List<$user>"` with templateRefs for mutable list types.

5. **Adding `System.*`, `typing.*`, `java.util.*` etc. to `customImports`** → let MetaEngine handle all framework imports automatically.

6. **Duplicating constructor parameter names in the `properties` array** (C#/Java/Go/Groovy) → put shared fields only in `constructorParameters`; add non-constructor fields in `properties[]`.

7. **Using reserved words** (`delete`, `class`, `import`) as property names → use safe alternatives (`remove`, `clazz`, `importData`).

8. **Generating related types in separate MCP calls** → batch everything in one call; cross-file imports only resolve within a single batch.

9. **Expecting `Number` to map to `double` in C#** → it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.

10. **Forgetting `fileName` when both an `I`-prefixed interface and its implementing class would collide in TypeScript** → set `"fileName": "i-user-repository"` on the interface to prevent file name conflicts.

---

## Key Takeaway for Generation Sessions

- **ONE call with the full spec.** Splitting per-domain breaks the typegraph and causes missing imports.
- **Analysis-first**: Identify all needed types → understand relationships → batch everything into one `generate_code` call.
- **templateRefs are the import bridge**: any internal type used in `customCode` or complex `type` strings needs a `$placeholder` + `templateRefs` entry, or imports won't be generated.
- **Virtual types** (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`) never produce files — they're only referenced by real types via `typeIdentifier`.
- When in doubt, include more types in the batch rather than fewer.
