# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, and PHP. It resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

### `mcp__metaengine__metaengine_initialize`
Returns essential MetaEngine patterns and documentation resources.
- **Input**: `language` (optional enum): `"typescript"`, `"python"`, `"go"`, `"csharp"`, `"java"`, `"kotlin"`, `"groovy"`, `"scala"`, `"swift"`, `"php"`
- **Output**: The full guide (patterns, critical rules, language-specific notes, common mistakes).
- **When to call**: Before generating code for the first time, or when you need guidance.

### `mcp__metaengine__generate_code`
Generates source files from a JSON spec.
- Accepts the full structured JSON payload (see schema below).
- Produces compilable files with all imports/using directives resolved automatically.

### `mcp__metaengine__generate_graphql`
Generates GraphQL schema files from a structured spec.

### `mcp__metaengine__generate_openapi`
Generates OpenAPI spec files from a structured spec.

### `mcp__metaengine__generate_protobuf`
Generates Protocol Buffer definition files from a structured spec.

### `mcp__metaengine__generate_sql`
Generates SQL DDL or migration files from a structured spec.

### `mcp__metaengine__load_spec_from_file`
Loads a MetaEngine spec from a local file and executes it.

---

## `generate_code` — Input Schema (Full)

The top-level object contains one or more of these arrays, plus a `language` field:

```jsonc
{
  "language": "typescript",   // required — one of the supported language strings

  // File-generating constructs:
  "interfaces": [ /* InterfaceDef[] */ ],
  "classes": [ /* ClassDef[] */ ],
  "enums": [ /* EnumDef[] */ ],
  "customFiles": [ /* CustomFileDef[] */ ],

  // Virtual (no-file) constructs — for type referencing only:
  "arrayTypes": [ /* ArrayTypeDef[] */ ],
  "dictionaryTypes": [ /* DictionaryTypeDef[] */ ],
  "concreteGenericClasses": [ /* ConcreteGenericClassDef[] */ ],
  "concreteGenericInterfaces": [ /* ConcreteGenericInterfaceDef[] */ ]
}
```

---

### InterfaceDef

```jsonc
{
  "name": "IUserRepository",        // string, required — interface name
  "typeIdentifier": "user-repo",    // string, required — internal reference key (kebab-case recommended)
  "fileName": "i-user-repository",  // string, optional — override generated file name (use when TS strips 'I' prefix causing collision)
  "path": "repositories",           // string, optional — subdirectory within output
  "packageName": "com.example",     // string, optional — namespace/package (C# / Java / Kotlin)
  "isAbstract": false,              // boolean, optional
  "properties": [ /* PropertyDef[] */ ],
  "customCode": [ /* CustomCodeDef[] */ ],
  "customImports": [ /* CustomImportDef[] */ ],
  "decorators": [ /* DecoratorDef[] */ ],
  "baseInterfaceTypeIdentifiers": ["base-repo"]  // string[], optional — extends other interfaces
}
```

**TypeScript note**: MetaEngine strips the `I` prefix from interface names in TypeScript. `IUserRepository` → exported as `UserRepository`. Set `fileName: "i-user-repository"` to avoid file-name collisions with a class of the same base name.

---

### ClassDef

```jsonc
{
  "name": "UserService",                          // string, required
  "typeIdentifier": "user-service",               // string, required
  "fileName": "user-service",                     // string, optional
  "path": "services",                             // string, optional
  "packageName": "com.example.services",          // string, optional
  "isAbstract": false,                            // boolean, optional
  "baseClassTypeIdentifier": "base-service",      // string, optional — extends
  "baseInterfaceTypeIdentifiers": ["user-repo"],  // string[], optional — implements
  "genericArguments": [ /* GenericArgumentDef[] */ ],
  "constructorParameters": [ /* ConstructorParamDef[] */ ],
  "properties": [ /* PropertyDef[] */ ],
  "customCode": [ /* CustomCodeDef[] */ ],
  "customImports": [ /* CustomImportDef[] */ ],
  "decorators": [ /* DecoratorDef[] */ ]
}
```

---

### EnumDef

```jsonc
{
  "name": "OrderStatus",            // string, required
  "typeIdentifier": "order-status", // string, required
  "path": "enums",                  // string, optional
  "packageName": "...",             // string, optional
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2}
  ]
}
```

Enums auto-suffix filenames: `order-status.enum.ts` (TypeScript), `OrderStatus.cs` (C#).

**Java/Kotlin note**: Enum member names are automatically transformed to `ALL_CAPS` (e.g., `Pending` → `PENDING`).

---

### CustomFileDef

```jsonc
{
  "name": "types",              // string, required — logical name
  "path": "shared",             // string, optional — subdirectory
  "identifier": "shared-types", // string, optional — enables import resolution by identifier
  "customCode": [ /* CustomCodeDef[] */ ],
  "customImports": [ /* CustomImportDef[] */ ]
}
```

Use for type aliases, barrel exports, constants, or any freeform code. If `identifier` is set, other files can reference it in `customImports` by identifier instead of relative path.

---

### PropertyDef

```jsonc
{
  "name": "email",                // string, required
  "primitiveType": "String",      // string — use for built-in types (see primitiveType values below)
  "typeIdentifier": "user",       // string — use for internal types (mutually exclusive with primitiveType)
  "type": "Map<string, $resp>",  // string — raw type expression; combine with templateRefs for internal refs
  "isOptional": true,             // boolean, optional — generates nullable/optional type
  "isArray": true,                // boolean, optional — wraps type in array
  "templateRefs": [ /* TemplateRefDef[] */ ]  // required when `type` contains $placeholder
}
```

**primitiveType values** (use these exact strings — MetaEngine maps them per-language):
- `"String"` → `string` (TS), `string` (C#), `str` (Python), `string` (Go), `String` (Java)
- `"Number"` → `number` (TS), `int` (C#!), `int` (Python), `int` (Go), `Integer` (Java)
- `"Boolean"` → `boolean` (TS), `bool` (C#), `bool` (Python), `bool` (Go), `Boolean` (Java)
- `"Date"` → `Date` (TS), `DateTime` (C#), `datetime` (Python), `time.Time` (Go), `LocalDate` (Java)
- `"Any"` → `unknown` (TS), `object` (C#), `Any` (Python), `interface{}` (Go), `Object` (Java)

**C# important**: `Number` maps to `int`, NOT `double`. Use `"type": "double"` or `"type": "decimal"` explicitly for non-integer numbers.

---

### CustomCodeDef

```jsonc
{
  "code": "getUser(): Promise<$user> { ... }",  // string, required — one member per item
  "templateRefs": [                              // required when code contains $placeholder
    {"placeholder": "$user", "typeIdentifier": "user"}
  ]
}
```

One `customCode` item = exactly one member (method, initialized field, property with logic).

For multi-line code, use `\n` — MetaEngine auto-indents continuation lines.

**Python note**: Must provide explicit 4-space indentation after `\n` in customCode.

---

### TemplateRefDef

```jsonc
{
  "placeholder": "$user",     // string, required — the $placeholder string in code/type
  "typeIdentifier": "user"    // string, required — must match a typeIdentifier in this batch
}
```

`templateRefs` work in: `properties[].type`, `customCode[].code`, `decorators[].code`.

---

### CustomImportDef

```jsonc
{
  "path": "@angular/core",              // string, required — module path or identifier
  "types": ["Injectable", "inject"]     // string[], optional — named imports
}
```

Use **only** for external libraries. Never for internal types (use `typeIdentifier` / `templateRefs` instead). Never for framework types that MetaEngine auto-imports.

---

### DecoratorDef

```jsonc
{
  "code": "@Injectable({ providedIn: 'root' })",
  "templateRefs": [ /* TemplateRefDef[] */ ]  // optional, if decorator references internal types
}
```

---

### GenericArgumentDef (for generic classes/interfaces)

```jsonc
{
  "name": "T",                                  // string, required — type parameter name
  "constraintTypeIdentifier": "base-entity",    // string, optional — extends constraint
  "propertyName": "items",                      // string, optional — auto-generated backing property name
  "isArrayProperty": true                       // boolean, optional — property is T[] instead of T
}
```

---

### ConstructorParamDef

```jsonc
{
  "name": "userRepository",        // string, required
  "typeIdentifier": "user-repo",   // string — internal type
  "primitiveType": "String",       // string — primitive type (mutually exclusive)
  "type": "string",                // string — raw type expression
  "isOptional": false              // boolean, optional
}
```

**Critical**: In C#, Java, Go, and Groovy, constructor parameters **automatically become class properties**. Do NOT duplicate them in `properties[]` — this causes errors.

---

### ArrayTypeDef (virtual — no file generated)

```jsonc
{
  "typeIdentifier": "user-list",          // string, required — reference key
  "elementTypeIdentifier": "user",        // string — element is an internal type
  "elementPrimitiveType": "String"        // string — element is a primitive (mutually exclusive)
}
```

Reference via `"typeIdentifier": "user-list"` in properties. **C# note**: arrayTypes generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs instead.

---

### DictionaryTypeDef (virtual — no file generated)

```jsonc
{
  "typeIdentifier": "user-lookup",       // string, required
  "keyPrimitiveType": "String",          // string — key type (usually primitive)
  "keyTypeIdentifier": "...",            // string — key as internal type (rare)
  "valuePrimitiveType": "Number",        // string — value type
  "valueTypeIdentifier": "user"          // string — value as internal type
}
```

---

### ConcreteGenericClassDef (virtual — no file generated)

```jsonc
{
  "identifier": "user-repo-concrete",          // string, required — reference key
  "genericClassIdentifier": "repo-generic",    // string, required — the generic class
  "genericArguments": [
    {"typeIdentifier": "user"}                 // resolved type arguments
  ]
}
```

Creates a virtual `Repository<User>` type. Classes extend it via `baseClassTypeIdentifier`. MetaEngine generates `extends Repository<User>` with correct imports.

---

## Critical Rules

### 1. ONE call for ALL related types

`typeIdentifier` references only resolve within the **current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting into multiple calls breaks cross-file import resolution.

### 2. Properties = type declarations. CustomCode = everything else.

- `properties[]`: declares fields with types **only** — no initialization, no logic.
- `customCode[]`: handles methods, initialized fields, and any code with logic. **One item = one member.**

Never put methods in `properties[]`. Never put uninitialized type declarations in `customCode[]`.

### 3. Use templateRefs for internal types in customCode

When `customCode` references a type from the same batch, use `$placeholder` syntax with `templateRefs`. Without `templateRefs`, MetaEngine cannot generate the import/using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**C# critical**: Every internal type reference in customCode MUST use templateRefs, or `using` directives for cross-namespace types won't be generated. Raw strings without templateRefs will cause compile failures across namespaces.

### 4. Never add framework imports to customImports

MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

| Language   | Auto-imported — never specify manually                                                          |
|------------|--------------------------------------------------------------------------------------------------|
| TypeScript | (no imports needed — built-in types)                                                             |
| C#         | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*   |
| Python     | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses                 |
| Java       | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.*       |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.*                               |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http        |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)                |

Only use `customImports` for external libraries (`@angular/core`, `rxjs`, `FluentValidation`, etc.).

### 5. templateRefs are ONLY for internal types

External library types → `customImports`. Same-batch types → `typeIdentifier` or `templateRefs`. Never mix.

### 6. Constructor parameters auto-create properties (C#, Java, Go, Groovy)

Do NOT duplicate constructor parameter names in `properties[]`. This causes "Sequence contains more than one matching element" errors.

### 7. Virtual types don't generate files

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references only. They never produce files. Reference their `typeIdentifier` from properties of file-generating types.

---

## TypeScript-Specific Notes

- MetaEngine strips `I` prefix from interface names: `IUserRepository` → exported as `UserRepository`. Use `fileName` to control file name if collisions arise (e.g., `"fileName": "i-user-repository"`).
- Primitive type mapping: `String` → `string`, `Number` → `number`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- `customCode` `\n` sequences are auto-indented.
- Decorators (e.g., `@Component`, `@Injectable`) are supported directly.
- For interface method signatures that a class will `implement`, use `customCode` (NOT function-typed properties). Function-typed properties cause duplicate declarations in implementing classes.

---

## Output Structure

MetaEngine generates:
- One file per `interface`, `class`, `enum`, or `customFile` entry.
- No files for virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`).
- All imports/using directives are resolved automatically — you never write import statements manually.
- Files are placed at the specified `path` subdirectory within the output root.
- Language-specific file naming conventions are applied automatically (e.g., `order-status.enum.ts` for TypeScript enums).
- Language-specific idiom transformations are applied (e.g., Java enum members become `ALL_CAPS`, Python methods become `snake_case`).

---

## Common Mistakes (Top 10)

1. **Missing type in batch** — referencing a `typeIdentifier` that doesn't exist in the same call → property silently dropped. Always verify every typeIdentifier matches a type defined in the same call.

2. **Interface method signatures as function-typed properties** — use `customCode` for method signatures on interfaces that will be implemented/extended.

3. **Raw string internal type names in customCode** — e.g., `"code": "private repo: IUserRepository"`. Always use templateRefs: `"code": "private repo: $repo"` with `"templateRefs": [...]`.

4. **C# arrayTypes when List<T> is needed** — `arrayTypes` → `IEnumerable<T>`. Use `"type": "List<$user>"` with templateRefs for mutable lists.

5. **Manual framework imports in customImports** — never add `System.*`, `typing.*`, `java.util.*`, etc.

6. **Duplicate constructor parameters in properties** (C#/Java/Go/Groovy) — put shared fields only in `constructorParameters`.

7. **Reserved words as property names** — avoid `delete`, `class`, `import`; use `remove`, `clazz`, `importData`.

8. **Splitting related types across multiple MCP calls** — cross-file imports only resolve within a single batch.

9. **Expecting Number → double in C#** — it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.

10. **Forgetting `fileName` for I-prefixed TypeScript interfaces** — when both an interface and its implementing class would collide, set `"fileName": "i-user-repository"` on the interface.

---

## Full Working Examples

### Example 1: Interfaces with cross-references (TypeScript)

```jsonc
{
  "language": "typescript",
  "interfaces": [
    {
      "name": "Address",
      "typeIdentifier": "address",
      "properties": [
        {"name": "street", "primitiveType": "String"},
        {"name": "city", "primitiveType": "String"}
      ]
    },
    {
      "name": "User",
      "typeIdentifier": "user",
      "properties": [
        {"name": "id", "primitiveType": "String"},
        {"name": "address", "typeIdentifier": "address"}
      ]
    }
  ]
}
```

Produces two files: `address.ts` and `user.ts`, with `user.ts` automatically importing `Address`.

---

### Example 2: Class with inheritance and methods

```jsonc
{
  "language": "typescript",
  "classes": [
    {
      "name": "BaseEntity",
      "typeIdentifier": "base-entity",
      "isAbstract": true,
      "properties": [{"name": "id", "primitiveType": "String"}]
    },
    {
      "name": "User",
      "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{"name": "email", "primitiveType": "String"}],
      "customCode": [
        {"code": "getDisplayName(): string { return this.email; }"}
      ]
    }
  ]
}
```

---

### Example 3: Generic class + concrete implementation

```jsonc
{
  "language": "typescript",
  "classes": [
    {
      "name": "Repository",
      "typeIdentifier": "repo-generic",
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
      "name": "User",
      "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{"name": "email", "primitiveType": "String"}]
    },
    {
      "name": "UserRepository",
      "typeIdentifier": "user-repo-class",
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

---

### Example 4: Enum + class that uses it

```jsonc
{
  "language": "typescript",
  "enums": [{
    "name": "OrderStatus",
    "typeIdentifier": "order-status",
    "members": [
      {"name": "Pending", "value": 0},
      {"name": "Shipped", "value": 2}
    ]
  }],
  "classes": [{
    "name": "Order",
    "typeIdentifier": "order",
    "properties": [
      {"name": "id", "primitiveType": "String"},
      {"name": "status", "typeIdentifier": "order-status"}
    ],
    "customCode": [{
      "code": "updateStatus(s: $status): void { this.status = s; }",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]
  }]
}
```

Generates: `order-status.enum.ts` and `order.ts` with automatic import.

---

### Example 5: Angular service with external DI

```jsonc
{
  "language": "typescript",
  "classes": [{
    "name": "ApiService",
    "typeIdentifier": "api-service",
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
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}]
}
```

---

### Example 6: CustomFiles for type aliases

```jsonc
{
  "language": "typescript",
  "customFiles": [{
    "name": "types",
    "path": "shared",
    "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Email = string;"}
    ]
  }],
  "classes": [{
    "name": "UserHelper",
    "path": "helpers",
    "customImports": [{"path": "shared-types"}],
    "customCode": [{"code": "static format(email: Email): string { return email.trim(); }"}]
  }]
}
```

---

### Example 7: Interface with method signatures (for implementation)

```jsonc
{
  "language": "typescript",
  "interfaces": [{
    "name": "IUserRepository",
    "typeIdentifier": "user-repo",
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

---

### Example 8: Array and dictionary virtual types

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
  ],
  "classes": [{
    "name": "DataStore",
    "typeIdentifier": "data-store",
    "properties": [
      {"name": "users", "typeIdentifier": "user-list"},
      {"name": "scores", "typeIdentifier": "scores"},
      {"name": "userLookup", "typeIdentifier": "user-lookup"}
    ]
  }]
}
```

---

### Example 9: Complex type expression with templateRefs in property

```jsonc
{
  "language": "typescript",
  "classes": [{
    "name": "ResponseCache",
    "typeIdentifier": "response-cache",
    "properties": [{
      "name": "cache",
      "type": "Map<string, $resp>",
      "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
    }]
  }]
}
```

---

## Decision Checklist Before Calling generate_code

1. **All referenced typeIdentifiers defined in this batch?** → Yes: proceed. No: add missing types.
2. **Methods → customCode, fields → properties?** → Check each item.
3. **Internal type refs in customCode use $placeholder + templateRefs?** → Verify every one.
4. **External library imports in customImports, not internal?** → Check.
5. **Constructor params NOT duplicated in properties (C#/Java/Go/Groovy)?** → Verify.
6. **Framework types NOT in customImports?** → Check.
7. **C# Number fields that should be decimal/double use explicit `"type"`?** → Verify.
8. **TypeScript I-prefixed interface has `fileName` to avoid collision?** → Check if needed.
9. **Interface method signatures in customCode (not function-typed properties)?** → Verify.
10. **All related types in ONE call (not split across calls)?** → Confirm.
