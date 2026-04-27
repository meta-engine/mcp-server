# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a **semantic code generation system** exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files. Supported languages: TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP.

Unlike template engines, MetaEngine:
- Resolves cross-references between types automatically
- Manages all imports/using-directives
- Handles language idioms (e.g., Java `ALL_CAPS` enums, Python `snake_case`)

One well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

### `mcp__metaengine__generate_code`
Primary tool. Accepts a JSON spec describing types and generates source files.

### `mcp__metaengine__metaengine_initialize`
Returns essential patterns and documentation. Call when you need guidance or are generating code for the first time. Accepts optional `language` parameter.

### `mcp__metaengine__load_spec_from_file`
Loads a spec from a file path instead of inline JSON.

### `mcp__metaengine__generate_graphql`, `mcp__metaengine__generate_openapi`, `mcp__metaengine__generate_protobuf`, `mcp__metaengine__generate_sql`
Spec-conversion tools (not covered in core documentation; use for those specific formats).

---

## `generate_code` — Input Schema (Full)

The top-level object passed to `generate_code` has these fields:

```jsonc
{
  "language": "typescript",          // Required. One of: typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php
  "outputPath": "src/generated",     // Optional. Where to write files.
  "packageName": "com.example",      // Optional. Sets namespace (C#), package (Java/Go), module (Python), etc.

  // Type-generating arrays (each item = one file):
  "interfaces": [...],
  "classes": [...],
  "enums": [...],
  "customFiles": [...],

  // Virtual types (no files generated — used by reference only):
  "arrayTypes": [...],
  "dictionaryTypes": [...],
  "concreteGenericClasses": [...],
  "concreteGenericInterfaces": [...]
}
```

### Interface object fields
```jsonc
{
  "name": "IUserRepository",           // Required. Class name.
  "typeIdentifier": "user-repo",       // Required. Stable cross-reference ID (kebab-case recommended).
  "fileName": "i-user-repository",     // Optional. Overrides the auto-derived filename.
  "path": "repositories",             // Optional. Subdirectory under outputPath.
  "packageName": "...",               // Optional. Overrides top-level packageName for this file.
  "isGeneric": true,                  // Optional. Marks as generic interface.
  "genericArguments": [...],          // Optional. See generic section.
  "properties": [...],               // Optional. Field declarations (type only, no logic).
  "customCode": [...],               // Optional. Method signatures and any code with logic.
  "customImports": [...],            // Optional. External library imports only.
  "decorators": [...]                // Optional. Language decorators/annotations.
}
```

### Class object fields
```jsonc
{
  "name": "UserService",
  "typeIdentifier": "user-service",
  "fileName": "user.service",          // Optional. Override filename.
  "path": "services",
  "packageName": "...",
  "isAbstract": false,                // Optional. Generates abstract class.
  "baseClassTypeIdentifier": "base",  // Optional. Extends this class (must be in same batch).
  "implementsTypeIdentifiers": ["user-repo"],  // Optional. Implements these interfaces.
  "genericArguments": [...],
  "constructorParameters": [...],     // Optional. Constructor params (auto-become properties in C#/Java/Go/Groovy).
  "properties": [...],
  "customCode": [...],
  "customImports": [...],
  "decorators": [...]
}
```

### Enum object fields
```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "path": "enums",
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2},
    {"name": "Delivered", "value": 3}
  ]
}
```
Enums auto-suffix filenames: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

Language idiom: Java/Kotlin enums auto-transform member names to `ALL_CAPS`.

### Property object fields
```jsonc
{
  "name": "userId",
  "primitiveType": "String",         // Use for built-in types. See primitiveType table below.
  // OR:
  "typeIdentifier": "user",          // Use for internal types (must exist in same batch).
  // OR:
  "type": "Map<string, $resp>",      // Use for complex expressions. Use with templateRefs.

  "isOptional": true,                // Optional. Generates nullable/optional syntax.
  "isArray": true,                   // Optional. Wraps in array type.
  "templateRefs": [...]              // Required when "type" contains $placeholders.
}
```

**PrimitiveType values and language mappings:**

| PrimitiveType | TypeScript | C#      | Python | Java   | Go      |
|---------------|------------|---------|--------|--------|---------|
| `String`      | `string`   | `string`| `str`  | `String`| `string`|
| `Number`      | `number`   | `int`   | `int`  | `int`  | `int`   |
| `Boolean`     | `boolean`  | `bool`  | `bool` | `boolean`| `bool`|
| `Date`        | `Date`     | `DateTime`| `datetime`| `LocalDateTime`| `time.Time`|
| `Any`         | `unknown`  | `object`| `Any`  | `Object`| `interface{}`|
| `Decimal`     | `number`   | `decimal`| `Decimal`| `BigDecimal`| `float64`|

**Important C# note:** `Number` → `int` (NOT `double`). Use `"type": "double"` or `"type": "decimal"` explicitly for non-integer numbers.

### CustomCode object fields
```jsonc
{
  "code": "getUser(id: string): Promise<$user | null> { ... }",
  "templateRefs": [
    {"placeholder": "$user", "typeIdentifier": "user"}
  ]
}
```
One `customCode` item = exactly one class/interface member. Each method or initialized field is its own item.

### CustomImports object fields
```jsonc
{
  "path": "@angular/core",           // Import path / module name.
  "types": ["Injectable", "inject"]  // Named imports (optional for some languages).
}
```
Only for **external** libraries. Never for framework standard library types.

### Decorators object fields
```jsonc
{
  "code": "@Injectable({ providedIn: 'root' })",
  "templateRefs": [...]  // Optional, same syntax as customCode templateRefs.
}
```

### ConstructorParameters object fields
```jsonc
{
  "name": "userRepository",
  "typeIdentifier": "user-repo",   // Internal type (from same batch).
  // OR:
  "primitiveType": "String",
  // OR:
  "type": "string"
}
```
**Critical:** In C#, Java, Go, and Groovy, constructor parameters automatically become class properties. Do NOT also list them in `properties[]` — causes "Sequence contains more than one matching element" errors.

### Virtual types (no files generated)

**arrayTypes:**
```jsonc
{
  "typeIdentifier": "user-list",
  "elementTypeIdentifier": "user",       // Internal type reference.
  // OR:
  "elementPrimitiveType": "String"       // Primitive element type.
}
```
Referenced via `"typeIdentifier": "user-list"` in properties. In C#, generates `IEnumerable<T>`. For `List<T>` in C#, use `"type": "List<$user>"` with templateRefs instead.

**dictionaryTypes:**
```jsonc
{
  "typeIdentifier": "user-lookup",
  "keyPrimitiveType": "String",
  "valueTypeIdentifier": "user"          // or valuePrimitiveType
}
```

**concreteGenericClasses:**
```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}
```
Creates a virtual `Repository<User>` type. Classes extend it via `baseClassTypeIdentifier`. MetaEngine generates `extends Repository<User>` with correct imports.

**concreteGenericInterfaces:** Same pattern as concreteGenericClasses but for interfaces.

### GenericArguments object fields (on classes/interfaces)
```jsonc
{
  "name": "T",
  "constraintTypeIdentifier": "base-entity",  // Optional. T extends BaseEntity.
  "propertyName": "items",                    // Optional. Auto-creates array property of T.
  "isArrayProperty": true
}
```

### CustomFiles
```jsonc
{
  "name": "types",
  "path": "shared",
  "identifier": "shared-types",   // Enables import resolution by other files.
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"}
  ]
}
```
The `identifier` allows other files to reference it in `customImports` using `{"path": "shared-types"}` — MetaEngine resolves to the relative path automatically.

---

## Critical Rules (Must Follow)

### Rule 1: Generate ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both MUST be in the same `generate_code` call. Split calls = broken imports.

### Rule 2: Properties = type declarations; CustomCode = everything else
- `properties[]` = field declarations with types only, NO initialization, NO logic
- `customCode[]` = methods, initialized fields, any code with logic
- Never put methods in properties; never put uninitialized type declarations in customCode

### Rule 3: Use templateRefs for internal types in customCode
When customCode references a type from the same batch, use `$placeholder` syntax with `templateRefs`. Without this, MetaEngine cannot generate the import/using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```
**Critical in C#**: Every internal type reference in customCode MUST use templateRefs or `using` directives for cross-namespace types won't be generated.

### Rule 4: Never add framework imports to customImports
Auto-imported types by language:
- **TypeScript**: No imports needed — built-in types
- **C#**: System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*
- **Python**: typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses
- **Java**: java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*
- **Kotlin**: java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*
- **Go**: time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, + more
- **Swift**: Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)

### Rule 5: templateRefs ONLY for internal types
- Internal type (same MCP call) → use `typeIdentifier` in properties or `templateRefs` in customCode
- External library type → use `customImports`
- Never mix these

### Rule 6: Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Do NOT list constructor parameter names again in `properties[]` — duplicate = runtime error.

### Rule 7: Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references only. They never produce files.

---

## TypeScript-Specific Notes

- MetaEngine strips `I` prefix from interface names for the exported symbol. `IUserRepository` interface → exported as `UserRepository`. Use `fileName` to control the file name if collisions arise (e.g., `"fileName": "i-user-repository"`).
- Primitive mappings: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for customCode newlines (`\n`)
- Decorators are supported directly
- For interface method signatures that a class will `implements`, put them in `customCode`, NOT as function-typed properties. If you use function-typed properties (e.g. `"type": "() => Promise<User[]>"`), the implementing class will duplicate them as property declarations alongside your customCode methods.

---

## Output Structure

MetaEngine generates one file per `interfaces`, `classes`, `enums`, and `customFiles` item. Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) generate no files.

File naming conventions:
- TypeScript: `user.ts`, `user.service.ts`, `order-status.enum.ts`
- C#: `UserRepository.cs`, `OrderStatus.cs`
- Java: `UserRepository.java`, `OrderStatus.java`
- Python: `user_repository.py`, `order_status.py`

All cross-file imports are generated automatically when `typeIdentifier` references are used correctly.

---

## Complete Example — TypeScript Service Layer

```jsonc
{
  "language": "typescript",
  "outputPath": "src",
  "enums": [
    {
      "name": "UserRole",
      "typeIdentifier": "user-role",
      "path": "enums",
      "members": [
        {"name": "Admin", "value": 0},
        {"name": "User", "value": 1},
        {"name": "Guest", "value": 2}
      ]
    }
  ],
  "interfaces": [
    {
      "name": "IUser",
      "typeIdentifier": "user",
      "path": "models",
      "fileName": "i-user",
      "properties": [
        {"name": "id", "primitiveType": "String"},
        {"name": "email", "primitiveType": "String"},
        {"name": "role", "typeIdentifier": "user-role"}
      ]
    },
    {
      "name": "IUserRepository",
      "typeIdentifier": "user-repo",
      "path": "repositories",
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
    }
  ],
  "classes": [
    {
      "name": "UserService",
      "typeIdentifier": "user-service",
      "path": "services",
      "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
      "customImports": [
        {"path": "@angular/core", "types": ["Injectable", "inject"]}
      ],
      "customCode": [
        {
          "code": "private repo = inject($repo);",
          "templateRefs": [{"placeholder": "$repo", "typeIdentifier": "user-repo"}]
        },
        {
          "code": "async getAll(): Promise<$user[]> { return this.repo.findAll(); }",
          "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
        }
      ]
    }
  ],
  "arrayTypes": [
    {"typeIdentifier": "user-array", "elementTypeIdentifier": "user"}
  ]
}
```

---

## Common Mistakes & How to Avoid Them

| Don't | Do |
|---|---|
| Reference a `typeIdentifier` not in the batch | Verify every typeIdentifier matches a defined type in the same call — missing refs are silently dropped |
| Put method signatures as function-typed properties on interfaces | Use `customCode` for interface method signatures |
| Write internal type names as raw strings in customCode | Use templateRefs: `"code": "private repo: $repo"` |
| Use `arrayTypes` in C# when you need `List<T>` | Use `"type": "List<$user>"` with templateRefs |
| Add `System.*`, `typing.*`, `java.util.*` to customImports | Let MetaEngine handle all framework imports automatically |
| Duplicate constructor parameter names in `properties[]` (C#/Java/Go/Groovy) | Put shared fields only in `constructorParameters` |
| Use reserved words as property names (`delete`, `class`, `import`) | Use safe alternatives (`remove`, `clazz`, `importData`) |
| Generate related types in separate MCP calls | Batch everything in one call — cross-file imports only resolve within a single batch |
| Assume `Number` → `double` in C# | Use `"type": "double"` or `"type": "decimal"` explicitly |
| Forget `fileName` when `I`-prefixed interface and implementing class collide in TypeScript | Set `"fileName": "i-user-repository"` on the interface |
