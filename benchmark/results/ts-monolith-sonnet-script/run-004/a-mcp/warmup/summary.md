# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, and PHP.

Unlike templates, it:
- Resolves cross-references between types automatically
- Manages imports/using directives across files
- Handles language idioms automatically (e.g., Java `ALL_CAPS` enums, Python `snake_case` methods, TypeScript `I`-prefix stripping)

A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

### `mcp__metaengine__metaengine_initialize`
Returns essential MetaEngine patterns and documentation resources. Call when you need guidance or are generating code for the first time. Optionally pass `language` (one of: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`) to get language-specific patterns.

### `mcp__metaengine__generate_code`
The primary generation tool. Takes a JSON payload describing types, their relationships, and their code, and produces compilable source files with correct imports. Full schema detailed below.

### `mcp__metaengine__load_spec_from_file`
Loads a spec (OpenAPI, GraphQL, Protobuf, SQL) from a file path for subsequent generation. Used before calling a spec-specific generator.

### `mcp__metaengine__generate_openapi`
Generate code from an OpenAPI spec.

### `mcp__metaengine__generate_graphql`
Generate code from a GraphQL schema.

### `mcp__metaengine__generate_protobuf`
Generate code from a Protobuf schema.

### `mcp__metaengine__generate_sql`
Generate code from a SQL schema.

---

## `generate_code` — Input Schema (Full)

The top-level object for `generate_code` contains:

### Top-level fields

| Field | Type | Description |
|---|---|---|
| `language` | string (required) | Target language: `typescript`, `csharp`, `python`, `go`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php` |
| `classes` | Class[] | Class definitions (generate files) |
| `interfaces` | Interface[] | Interface definitions (generate files) |
| `enums` | Enum[] | Enum definitions (generate files) |
| `customFiles` | CustomFile[] | Arbitrary files (type aliases, barrel exports, etc.) |
| `arrayTypes` | ArrayType[] | Virtual array type refs — NO file generated |
| `dictionaryTypes` | DictionaryType[] | Virtual dictionary type refs — NO file generated |
| `concreteGenericClasses` | ConcreteGenericClass[] | Virtual concrete-generic type refs — NO file generated |
| `concreteGenericInterfaces` | ConcreteGenericInterface[] | Virtual concrete-generic interface refs — NO file generated |

---

### Class definition fields

| Field | Type | Description |
|---|---|---|
| `name` | string (required) | Class name |
| `typeIdentifier` | string (required) | Unique ID within this batch — used for cross-references |
| `path` | string | Output subdirectory (optional) |
| `fileName` | string | Override generated filename (optional) |
| `packageName` | string | Namespace (C#) / package (Java, Kotlin, Go) (optional) |
| `isAbstract` | boolean | Marks the class abstract |
| `properties` | Property[] | Type declarations only (no logic, no initialization) |
| `customCode` | CustomCodeItem[] | Methods and initialized fields — one member per item |
| `customImports` | CustomImport[] | External library imports only |
| `decorators` | Decorator[] | Class-level decorators/annotations |
| `baseClassTypeIdentifier` | string | typeIdentifier of the parent class (extends) |
| `implementsInterfaceTypeIdentifiers` | string[] | typeIdentifiers of implemented interfaces |
| `constructorParameters` | ConstructorParam[] | Constructor params; auto-creates class properties in C#/Java/Go/Groovy |
| `genericArguments` | GenericArgument[] | Makes the class generic (defines `<T>` etc.) |

---

### Interface definition fields

Same as Class but no `baseClassTypeIdentifier`. Has `implementsInterfaceTypeIdentifiers`. Method signatures go in `customCode`, not as function-typed properties.

---

### Enum definition fields

| Field | Type | Description |
|---|---|---|
| `name` | string (required) | Enum name |
| `typeIdentifier` | string (required) | Unique ID for cross-references |
| `members` | EnumMember[] | Each has `name` and `value` (integer) |
| `path` | string | Output subdirectory |
| `fileName` | string | Override filename |
| `packageName` | string | Namespace/package |

Enums auto-suffix filenames: `order-status.enum.ts` (TypeScript), `OrderStatus.cs` (C#).

---

### Property definition fields

| Field | Type | Description |
|---|---|---|
| `name` | string (required) | Property name |
| `primitiveType` | string | One of: `String`, `Number`, `Boolean`, `Date`, `Any` |
| `typeIdentifier` | string | Reference to another type in this batch |
| `type` | string | Raw type string (for complex expressions; combine with `templateRefs`) |
| `templateRefs` | TemplateRef[] | Placeholder-to-typeIdentifier mappings for import resolution |
| `isOptional` | boolean | Makes field optional/nullable |
| `isArray` | boolean | Wraps type in array |

**Only one of** `primitiveType`, `typeIdentifier`, or `type` should be set per property.

---

### CustomCodeItem fields

| Field | Type | Description |
|---|---|---|
| `code` | string (required) | The exact source code for one member (method or initialized field) |
| `templateRefs` | TemplateRef[] | Placeholder-to-typeIdentifier for import resolution |

One CustomCodeItem = exactly one class/interface member. Use `\n` for line breaks (MetaEngine auto-indents).

---

### CustomImport fields

| Field | Type | Description |
|---|---|---|
| `path` | string (required) | Import path or package name (e.g., `@angular/core`) |
| `types` | string[] | Named imports from that path |

Only for **external** libraries. Never use for framework stdlib (auto-imported) or internal types (use templateRefs).

---

### Decorator fields

| Field | Type | Description |
|---|---|---|
| `code` | string (required) | Full decorator text (e.g., `@Injectable({ providedIn: 'root' })`) |
| `templateRefs` | TemplateRef[] | Placeholder resolution for decorators with internal type refs |

---

### TemplateRef fields

| Field | Type | Description |
|---|---|---|
| `placeholder` | string (required) | The `$placeholder` token in `code` or `type` |
| `typeIdentifier` | string (required) | The batch typeIdentifier to resolve to |

---

### ArrayType fields (virtual — no file generated)

| Field | Type | Description |
|---|---|---|
| `typeIdentifier` | string (required) | ID to reference this array type from properties |
| `elementTypeIdentifier` | string | typeIdentifier of element type (internal type) |
| `elementPrimitiveType` | string | Primitive element type (`String`, `Number`, etc.) |

---

### DictionaryType fields (virtual — no file generated)

| Field | Type | Description |
|---|---|---|
| `typeIdentifier` | string (required) | ID to reference this dictionary type from properties |
| `keyPrimitiveType` | string | Key primitive type |
| `valuePrimitiveType` | string | Value primitive type |
| `valueTypeIdentifier` | string | Value typeIdentifier (internal type) |

---

### ConcreteGenericClass fields (virtual — no file generated)

| Field | Type | Description |
|---|---|---|
| `identifier` | string (required) | ID to reference this concrete generic from baseClassTypeIdentifier |
| `genericClassIdentifier` | string | typeIdentifier of the generic class to instantiate |
| `genericArguments` | GenericTypeArg[] | Each has `typeIdentifier` or `primitiveType` |

---

### GenericArgument fields (on Class/Interface)

| Field | Type | Description |
|---|---|---|
| `name` | string | The type parameter name (e.g., `T`) |
| `constraintTypeIdentifier` | string | typeIdentifier for the constraint (`T extends BaseEntity`) |
| `propertyName` | string | Auto-creates a property of type `T[]` on the class |
| `isArrayProperty` | boolean | Whether the auto-created property is an array |

---

### ConstructorParameter fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Parameter name |
| `primitiveType` | string | Primitive type |
| `typeIdentifier` | string | Internal type reference |
| `type` | string | Raw type string |
| `templateRefs` | TemplateRef[] | Placeholder resolution |

In C#/Java/Go/Groovy: constructor parameters **auto-create** class properties. Do NOT also list them in `properties[]` — this causes errors.

---

### CustomFile fields

| Field | Type | Description |
|---|---|---|
| `name` | string (required) | File base name |
| `path` | string | Output subdirectory |
| `identifier` | string | ID enabling other files to import this via customImports |
| `customCode` | CustomCodeItem[] | File content |
| `customImports` | CustomImport[] | External imports for this file |

---

## Critical Rules (Must Follow)

### Rule 1: Generate ALL related types in ONE call

`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Cross-file imports only resolve within a single batch — **never split related types across multiple calls**.

### Rule 2: properties[] = type declarations only; customCode[] = everything else

- `properties[]` declares fields with types only. No logic, no initialization.
- `customCode[]` handles methods and initialized fields.
- One `customCode` item = exactly one member.
- **Never put methods in properties.** Never put uninitialized type declarations in customCode.

### Rule 3: Use templateRefs for internal types in customCode

When customCode references a type from the same batch, use `$placeholder` syntax with `templateRefs`. Without templateRefs, MetaEngine cannot generate the import/using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**Critical in C#**: Every internal type reference in customCode MUST use templateRefs, or `using` directives for cross-namespace types won't be generated. Raw strings like `IUserRepository` without templateRefs will cause compile failures across namespaces.

### Rule 4: Never add framework imports to customImports

MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

| Language | Auto-imported (never specify) |
|---|---|
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
| TypeScript | (no imports needed — built-in types) |

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5: templateRefs are ONLY for internal types

- Internal type (same batch) → use `typeIdentifier` in properties or `templateRefs` in customCode
- External library type → use `customImports`
- Never mix these

### Rule 6: Constructor parameters auto-create properties (C#, Java, Go, Groovy)

In C#, Java, Go, and Groovy, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]` — this causes "Sequence contains more than one matching element" errors. Put shared fields only in `constructorParameters`; additional non-constructor properties go in `properties[]`.

### Rule 7: Virtual types don't generate files

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, and `concreteGenericInterfaces` create reusable type references only. They never produce files. They're used by referencing their `typeIdentifier` in properties of file-generating types.

---

## Output Structure

MetaEngine produces one source file per `class`, `interface`, `enum`, and `customFile` entry. Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) produce no files.

File paths follow: `<path>/<fileName>.<ext>` where:
- `path` is the optional subdirectory
- `fileName` defaults to a generated form of `name` (e.g., `UserService` → `user-service.ts` in TS)
- Extension is determined by `language`

All imports/using directives between generated files are resolved automatically.

---

## Language-Specific Notes

### TypeScript
- MetaEngine **strips the `I` prefix** from interface names. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control the file name if collisions arise (e.g., set `"fileName": "i-user-repository"` on the interface).
- Primitive mappings: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators supported directly

### C#
- `I` prefix preserved on interface names
- `Number` → `int` (NOT `double`). Use `"type": "decimal"` or `"type": "double"` for non-integer numbers.
- `packageName` sets the namespace. Omit for GlobalUsings pattern.
- Interface properties generate `{ get; }`. Class properties generate `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `type` with templateRefs: `"type": "List<$user>"`
- `isOptional` on properties generates `string?` (nullable reference type)

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode
- `typing` imports are automatic

### Go
- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode

### Java
- `ALL_CAPS` enum members are idiomatic; engine applies this automatically

---

## Pattern Examples

### Basic interfaces with cross-references (TypeScript)
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
The `concreteGenericClasses` entry creates a virtual `Repository<User>` type. The class extends it via `baseClassTypeIdentifier`. MetaEngine generates `extends Repository<User>` with correct imports.

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

### Complex type expressions with templateRefs in properties
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

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

### Service with Angular DI
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

### CustomFiles for type aliases / barrel exports
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

### Interface with method signatures (for implementing classes)
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
Use `customCode` for method signatures on interfaces that classes will implement. If you use function-typed properties instead (e.g. `"type": "() => Promise<User[]>"`), the implementing class will duplicate them as property declarations alongside your customCode methods.

---

## Common Mistakes Checklist

1. **Missing type in batch**: Referencing a `typeIdentifier` that doesn't exist in the batch → property is silently dropped. Verify every typeIdentifier matches a defined type in the same call.

2. **Interface method signatures as properties**: Don't put method signatures as function-typed properties on interfaces you'll `implements`. Use `customCode` instead.

3. **Raw internal type strings in customCode**: Don't write `"code": "private repo: IUserRepository"`. Use templateRefs: `"code": "private repo: $repo"` with `"templateRefs": [{"placeholder": "$repo", "typeIdentifier": "user-repo"}]`.

4. **arrayTypes in C# when you need List<T>**: Don't use `arrayTypes` in C# when you need `List<T>`. Use `"type": "List<$user>"` with templateRefs.

5. **Adding stdlib to customImports**: Don't add `System.*`, `typing.*`, `java.util.*` etc. to customImports. MetaEngine handles these automatically.

6. **Duplicate constructor params in properties** (C#/Java/Go/Groovy): Don't list constructor parameter names again in `properties[]`. This causes "Sequence contains more than one matching element" errors.

7. **Reserved words as property names**: Don't use `delete`, `class`, `import`. Use `remove`, `clazz`, `importData` instead.

8. **Splitting related types across calls**: Don't generate related types in separate MCP calls. Batch everything in one call — cross-file imports only resolve within a single batch.

9. **Number → double in C#**: `Number` maps to `int`, not `double`. Use `"type": "double"` or `"type": "decimal"` explicitly when needed.

10. **Interface/class file name collision in TypeScript**: When both an `I`-prefixed interface and its implementing class would collide, set `"fileName": "i-user-repository"` on the interface.
