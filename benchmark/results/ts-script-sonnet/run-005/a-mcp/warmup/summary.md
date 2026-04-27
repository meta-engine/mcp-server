# MetaEngine MCP — Knowledge Brief

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, and PHP. It resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

- `mcp__metaengine__generate_code` — primary tool: takes a JSON spec and generates one or more source files
- `mcp__metaengine__generate_graphql` — generates GraphQL schema files
- `mcp__metaengine__generate_openapi` — generates OpenAPI specs
- `mcp__metaengine__generate_protobuf` — generates Protobuf definitions
- `mcp__metaengine__generate_sql` — generates SQL DDL
- `mcp__metaengine__load_spec_from_file` — loads a spec from a file path (alternative input method)
- `mcp__metaengine__metaengine_initialize` — returns this documentation; call when you need guidance

---

## generate_code — Input Schema (full)

The root object passed to `generate_code` has the following top-level fields:

```jsonc
{
  "language": "typescript",         // required: target language
  "outputPath": "src/",             // optional: root output directory

  // File-generating types (each produces one source file):
  "interfaces": [...],
  "classes": [...],
  "enums": [...],
  "customFiles": [...],

  // Virtual types (NO files produced — only usable as typeIdentifier references):
  "arrayTypes": [...],
  "dictionaryTypes": [...],
  "concreteGenericClasses": [...],
  "concreteGenericInterfaces": [...]
}
```

### `interfaces[]` — Interface schema

```jsonc
{
  "name": "IUserRepository",            // required: interface name
  "typeIdentifier": "user-repo",        // required: unique ID for cross-references
  "fileName": "i-user-repository",      // optional: overrides auto-generated file name
  "path": "repositories",              // optional: subdirectory within outputPath
  "packageName": "MyApp.Repositories", // optional: namespace/package (C#/Java/Kotlin)
  "properties": [...],                 // optional: field declarations (type only)
  "customCode": [...],                 // optional: method signatures and other members
  "customImports": [...]               // optional: external library imports
}
```

### `classes[]` — Class schema

```jsonc
{
  "name": "UserService",
  "typeIdentifier": "user-service",
  "fileName": "user-service",          // optional
  "path": "services",                  // optional
  "packageName": "MyApp.Services",     // optional
  "isAbstract": false,                 // optional
  "baseClassTypeIdentifier": "base",   // optional: extends/inherits from another class
  "implementsTypeIdentifiers": ["user-repo"], // optional: implements interfaces
  "genericArguments": [...],           // optional: makes the class generic
  "constructorParameters": [...],      // optional: constructor params (also become properties in C#/Java/Go/Groovy)
  "properties": [...],                 // optional: field declarations
  "customCode": [...],                 // optional: methods and initialized fields
  "decorators": [...],                 // optional: decorators/annotations
  "customImports": [...]               // optional: external library imports
}
```

### `enums[]` — Enum schema

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "path": "models",                    // optional
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2},
    {"name": "Delivered", "value": 3}
  ]
}
```

- TypeScript: auto-suffixes filename as `order-status.enum.ts`
- Java/Kotlin: names are transformed to `ALL_CAPS` automatically (idiomatic)
- Python: names are transformed to `UPPER_SNAKE_CASE` automatically

### `customFiles[]` — Arbitrary file schema

```jsonc
{
  "name": "types",
  "identifier": "shared-types",        // enables import resolution by other types
  "path": "shared",                    // optional: subdirectory
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"}
  ],
  "customImports": [...]               // optional
}
```

### `arrayTypes[]` — Virtual array type

```jsonc
{
  "typeIdentifier": "user-list",
  "elementTypeIdentifier": "user"      // reference internal type
  // OR
  // "elementPrimitiveType": "String"  // use primitive
}
```

- C# note: produces `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs instead.

### `dictionaryTypes[]` — Virtual dictionary type

```jsonc
{
  "typeIdentifier": "user-lookup",
  "keyPrimitiveType": "String",
  "valueTypeIdentifier": "user"
  // keys and values can mix primitive / typeIdentifier
}
```

### `concreteGenericClasses[]` — Virtual concrete generic class

```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}
```

This creates a virtual `Repository<User>` type. A class can then extend it via `"baseClassTypeIdentifier": "user-repo-concrete"`, and MetaEngine generates `extends Repository<User>` with correct imports.

### `concreteGenericInterfaces[]` — Virtual concrete generic interface

Same pattern as `concreteGenericClasses` but for interfaces.

---

## Properties Schema

`properties[]` declares fields with types only. No logic, no initialization.

```jsonc
{
  "name": "email",
  "primitiveType": "String",        // use one of: primitiveType OR typeIdentifier OR type
  // OR "typeIdentifier": "user",
  // OR "type": "Map<string, $resp>",  (with templateRefs for placeholders)
  "isOptional": true,               // optional: generates nullable / optional type
  "isArray": true,                  // optional: wraps type in array
  "templateRefs": [...]             // optional: required when "type" contains $placeholder
}
```

**Primitive type values** (language-mapped automatically):
- `String` → `string` (TS), `string` (C#), `str` (Python), `string` (Go), `String` (Java/Kotlin)
- `Number` → `number` (TS), `int` (C#), `int` (Python), `int` (Go), `int` (Java/Kotlin)
- `Boolean` → `boolean` (TS), `bool` (C#), `bool` (Python), `bool` (Go), `boolean` (Java/Kotlin)
- `Date` → `Date` (TS), `DateTime` (C#), `datetime` (Python), `time.Time` (Go)
- `Any` → `unknown` (TS), `object` (C#), `Any` (Python), `interface{}` (Go)

---

## customCode Schema

One item = exactly one member (method, initialized field, etc.).

```jsonc
{
  "code": "getUser(): Promise<$user> { return this.repo.find(); }",
  "templateRefs": [
    {"placeholder": "$user", "typeIdentifier": "user"}
  ]
}
```

- `code`: the raw code string; use `\n` for newlines (MetaEngine auto-indents in TS)
- `templateRefs`: array of placeholder → typeIdentifier mappings for internal types

**Python-specific**: must include explicit 4-space indentation after `\n` in code strings.

---

## customImports Schema

Only for external library imports. Never for standard library / framework types (those are auto-managed).

```jsonc
{
  "path": "@angular/core",
  "types": ["Injectable", "inject"]
}
```

For a `customFile` identifier reference (internal barrel import):
```jsonc
{"path": "shared-types"}   // resolves to relative path automatically
```

---

## templateRefs — Complete Rules

`templateRefs` is an array on `properties`, `customCode`, and `decorators` items.

```jsonc
"templateRefs": [
  {"placeholder": "$user", "typeIdentifier": "user"}
]
```

- The `$placeholder` appears verbatim in `code` or `type`
- MetaEngine replaces it with the resolved type name and generates the import
- **Only** for types defined in the same batch — external types use `customImports`
- Without templateRefs, MetaEngine cannot generate the import directive → compile failures

**C# critical**: every cross-namespace internal type reference in customCode MUST use templateRefs or the `using` directive won't be generated.

---

## constructorParameters Schema

```jsonc
"constructorParameters": [
  {
    "name": "userRepository",
    "typeIdentifier": "user-repo",    // or primitiveType
    "templateRefs": [...]             // optional
  }
]
```

- C#/Java/Go/Groovy: constructor params **automatically become class properties** — do NOT duplicate in `properties[]`
- TypeScript/Python: constructor params do NOT auto-create properties (declare separately if needed)

---

## genericArguments Schema (on classes/interfaces)

Makes a class/interface generic:

```jsonc
"genericArguments": [
  {
    "name": "T",
    "constraintTypeIdentifier": "base-entity",  // optional: T extends BaseEntity
    "propertyName": "items",                     // optional: auto-creates a T-typed property
    "isArrayProperty": true                      // optional: makes it T[]
  }
]
```

---

## decorators Schema

```jsonc
"decorators": [
  {
    "code": "@Injectable({ providedIn: 'root' })",
    "templateRefs": [...]   // optional, if decorator references internal types
  }
]
```

---

## Output Structure

MetaEngine returns:
- An array of generated files, each with its path and content
- All imports are automatically resolved and injected
- Files are placed according to `path` + `outputPath` fields
- TypeScript: strips `I` prefix from interface names in generated output (use `fileName` to prevent collisions)

---

## Critical Rules (full list)

### 1. Generate ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting across calls = silently broken imports.

### 2. Properties = type declarations only. CustomCode = everything else.
- `properties[]`: fields with types, no initialization, no logic
- `customCode[]`: methods, initialized fields, computed members — one item per member
- **Never put methods in properties. Never put uninitialized declarations in customCode.**

### 3. Use templateRefs for internal types in customCode and properties with type expressions
When customCode or a `"type"` string references a type from the same batch, use `$placeholder` syntax with `templateRefs`. Without it, imports won't be generated.

### 4. Never add framework imports to customImports
Standard library types (System.*, typing.*, java.util.*, etc.) are auto-imported. Adding them manually causes duplication or errors. See auto-import table above.

### 5. templateRefs are ONLY for internal types
- Internal types (same batch) → `typeIdentifier` or `templateRefs`
- External library types → `customImports`
- Never mix these.

### 6. Constructor parameters auto-create properties (C#, Java, Go, Groovy)
Do NOT duplicate constructor parameters in `properties[]`. This causes "Sequence contains more than one matching element" errors.

### 7. Virtual types never generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reference helpers only. They produce no files. Use their `typeIdentifier` in other types' properties.

### 8. Interface method signatures go in customCode
For interfaces that will be implemented by a class, put method signatures in `customCode` (not as function-typed properties). Using function-typed properties causes implementing classes to duplicate them as property declarations.

### 9. Don't use reserved words as property names
Avoid `delete`, `class`, `import`. Use `remove`, `clazz`, `importData` instead.

### 10. `Number` maps to `int` in C#
Use `"type": "double"` or `"type": "decimal"` explicitly when non-integer numbers are needed.

### 11. TypeScript: use `fileName` when I-prefix interface would collide with its implementation
`IUserRepository` → MetaEngine strips `I` → file would be `user-repository.ts`. If both an interface and its implementation exist, set `"fileName": "i-user-repository"` on the interface.

---

## Common Mistakes (quick reference)

| Don't | Do |
|---|---|
| Reference a typeIdentifier not in the current batch | Verify every typeIdentifier matches a type in the same call |
| Put method signatures as function-typed properties on interfaces | Use `customCode` for interface method signatures |
| Write internal type names as raw strings in customCode | Use `templateRefs` with `$placeholder` |
| Use `arrayTypes` in C# when you need `List<T>` | Use `"type": "List<$user>"` with templateRefs |
| Add System.*, typing.*, java.util.* to customImports | Let MetaEngine handle framework imports |
| Duplicate constructor params in `properties[]` (C#/Java/Go/Groovy) | Put shared fields only in `constructorParameters` |
| Generate related types in separate MCP calls | Batch everything in one call |
| Expect `Number` → `double` in C# | Use explicit `"type": "double"` or `"type": "decimal"` |

---

## Language Notes for TypeScript (primary target)

- `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- No framework imports needed in `customImports` (built-in types need no imports)
- MetaEngine strips `I` prefix from interface names in generated output
- Auto-indents customCode newlines (`\n`) automatically
- Decorators supported directly via `decorators[]`
- Enums auto-suffixed: `order-status.enum.ts`
- Use `fileName` on interfaces to prevent file name collisions with implementing classes
- TypeScript constructor params do NOT auto-create properties (unlike C#/Java)

---

## Complete Working Examples

### Interfaces with cross-references

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

### Class with inheritance and methods

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

### Enum + class using it

```jsonc
{
  "language": "typescript",
  "enums": [
    {
      "name": "OrderStatus",
      "typeIdentifier": "order-status",
      "members": [
        {"name": "Pending", "value": 0},
        {"name": "Shipped", "value": 2}
      ]
    }
  ],
  "classes": [
    {
      "name": "Order",
      "typeIdentifier": "order",
      "properties": [{"name": "status", "typeIdentifier": "order-status"}],
      "customCode": [
        {
          "code": "updateStatus(s: $status): void { this.status = s; }",
          "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
        }
      ]
    }
  ]
}
```

### Service with external DI (Angular-style)

```jsonc
{
  "language": "typescript",
  "classes": [
    {
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
    }
  ],
  "arrayTypes": [
    {"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}
  ]
}
```

### Generic repository + concrete implementation

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
      "customCode": [
        {
          "code": "findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
          "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
        }
      ]
    }
  ],
  "concreteGenericClasses": [
    {
      "identifier": "user-repo-concrete",
      "genericClassIdentifier": "repo-generic",
      "genericArguments": [{"typeIdentifier": "user"}]
    }
  ]
}
```

### Interface with method signatures (correct pattern)

```jsonc
{
  "language": "typescript",
  "interfaces": [
    {
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
    }
  ]
}
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

### Complex type expressions with templateRefs in properties

```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

### CustomFiles for barrel exports / type aliases

```jsonc
{
  "language": "typescript",
  "customFiles": [
    {
      "name": "types",
      "path": "shared",
      "identifier": "shared-types",
      "customCode": [
        {"code": "export type UserId = string;"},
        {"code": "export type Email = string;"}
      ]
    }
  ],
  "classes": [
    {
      "name": "UserHelper",
      "path": "helpers",
      "customImports": [{"path": "shared-types"}],
      "customCode": [
        {"code": "static format(email: Email): string { return email.trim(); }"}
      ]
    }
  ]
}
```
