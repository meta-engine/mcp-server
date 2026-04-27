# MetaEngine MCP — Knowledge Brief

## What MetaEngine Is

MetaEngine is a **semantic code generation system** exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files. It resolves cross-references, manages imports, and handles language idioms automatically.

**Supported languages**: TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP.

**Key advantage over file writes**: a single well-formed JSON call replaces dozens of error-prone file edits. The engine handles all import resolution, file naming, and language-specific idioms.

---

## Tools Exposed

### `mcp__metaengine__generate_code`
Main tool — generates source files from a structured JSON spec. Takes a top-level object with:
- `language` (required): target language string
- `interfaces[]`, `classes[]`, `enums[]`, `customFiles[]` (file-generating types)
- `arrayTypes[]`, `dictionaryTypes[]`, `concreteGenericClasses[]`, `concreteGenericInterfaces[]` (virtual/reference-only types — never produce files)

### `mcp__metaengine__load_spec_from_file`
Loads a generation spec from a file path instead of inline JSON.

### `mcp__metaengine__generate_graphql`, `mcp__metaengine__generate_openapi`, `mcp__metaengine__generate_protobuf`, `mcp__metaengine__generate_sql`
Spec-conversion variants — convert schema formats to target language code.

### `mcp__metaengine__metaengine_initialize`
Returns this documentation and language-specific guidance. Call when you need the guide or are generating for the first time.

---

## generate_code — Input Schema (Full Detail)

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | string | Yes | `"typescript"`, `"csharp"`, `"python"`, `"go"`, `"java"`, `"kotlin"`, `"groovy"`, `"scala"`, `"swift"`, `"php"` |
| `interfaces` | Interface[] | No | File-generating interface definitions |
| `classes` | Class[] | No | File-generating class definitions |
| `enums` | Enum[] | No | File-generating enum definitions |
| `customFiles` | CustomFile[] | No | Arbitrary files (barrel exports, type aliases, etc.) |
| `arrayTypes` | ArrayType[] | No | Virtual array type references (no files generated) |
| `dictionaryTypes` | DictionaryType[] | No | Virtual dict/map type references (no files generated) |
| `concreteGenericClasses` | ConcreteGenericClass[] | No | Virtual concrete instantiation of generic class (no files generated) |
| `concreteGenericInterfaces` | ConcreteGenericInterface[] | No | Virtual concrete instantiation of generic interface (no files generated) |

### Interface object

| Field | Type | Notes |
|---|---|---|
| `name` | string | Interface name. TypeScript: strips `I` prefix from export name (use `fileName` to avoid collisions). C#: `I` prefix preserved. |
| `typeIdentifier` | string | Unique string key for cross-referencing within the batch. Kebab-case recommended. |
| `fileName` | string | Optional override for the output file name. Use when TS would collide (e.g. `IUserRepo` interface and `UserRepo` class). |
| `path` | string | Subdirectory path within the output folder. |
| `packageName` | string | Namespace (C#) / package (Java, Go, Kotlin). |
| `properties` | Property[] | Field declarations (type only, no initialization). |
| `customCode` | CustomCode[] | Method signatures (in interfaces), and any code with logic. One item = one member. |
| `customImports` | CustomImport[] | External library imports only (NOT framework/stdlib — those are auto-injected). |
| `decorators` | Decorator[] | Language decorators / annotations. |
| `genericArguments` | GenericArgument[] | For generic interfaces. |
| `baseInterfaceTypeIdentifiers` | string[] | Extends/implements other interfaces (by typeIdentifier). |
| `isOptional` | boolean | Marks all properties optional (TypeScript `?`). |

### Class object

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | Unique string key for cross-referencing. |
| `fileName` | string | Optional file name override. |
| `path` | string | Subdirectory within output folder. |
| `packageName` | string | Namespace / package. |
| `isAbstract` | boolean | Marks class abstract. |
| `properties` | Property[] | Field declarations (type-only, no init). DO NOT duplicate constructor params here. |
| `customCode` | CustomCode[] | Methods and initialized fields. One item = one member. |
| `customImports` | CustomImport[] | External imports only. |
| `decorators` | Decorator[] | Class-level decorators / annotations. |
| `genericArguments` | GenericArgument[] | For generic classes. |
| `baseClassTypeIdentifier` | string | Extends a class (by typeIdentifier, including concreteGenericClasses). |
| `interfaceTypeIdentifiers` | string[] | Implements interfaces (by typeIdentifier). |
| `constructorParameters` | ConstructorParameter[] | Constructor args. In C#/Java/Go/Groovy these AUTO-CREATE properties — do NOT duplicate in `properties[]`. |
| `isOptional` | boolean | Makes all properties optional. |

### Enum object

| Field | Type | Notes |
|---|---|---|
| `name` | string | Enum name. |
| `typeIdentifier` | string | Reference key. |
| `fileName` | string | Optional file name. Engine auto-suffixes: `.enum.ts` (TS), standard for others. |
| `path` | string | Subdirectory. |
| `packageName` | string | Namespace / package. |
| `members` | EnumMember[] | Each member has `name` and `value`. Java/Kotlin: names conventionally `ALL_CAPS`. |

### CustomFile object

| Field | Type | Notes |
|---|---|---|
| `name` | string | File name (without extension). |
| `path` | string | Subdirectory. |
| `identifier` | string | Unique key — other types can `customImport` this by identifier to get auto-resolved relative paths. |
| `customCode` | CustomCode[] | Arbitrary code members. |
| `customImports` | CustomImport[] | Imports for this file. |

### Property object

| Field | Type | Notes |
|---|---|---|
| `name` | string | Property/field name. |
| `primitiveType` | string | One of: `String`, `Number`, `Boolean`, `Date`, `Any`. Language-specific mapping applies (see below). |
| `typeIdentifier` | string | Reference to another type in the batch. Mutually exclusive with `primitiveType` and `type`. |
| `type` | string | Raw type string with optional `$placeholder` templateRefs. Use for complex types (`List<$user>`, `Map<string, $resp>`). |
| `templateRefs` | TemplateRef[] | Required when `type` contains `$placeholder` references. |
| `isOptional` | boolean | Makes this property optional (`?` in TS, `?` nullable in C#). |
| `isArray` | boolean | Wraps the type in an array. |
| `decorators` | Decorator[] | Property-level decorators / annotations. |

### CustomCode object

| Field | Type | Notes |
|---|---|---|
| `code` | string | The code string. One member per item. Newlines (`\n`) auto-indented (Python requires explicit 4-space indent after `\n`). |
| `templateRefs` | TemplateRef[] | Required when `code` contains `$placeholder` references to batch types. Triggers import generation. |
| `decorators` | Decorator[] | Decorators applied above this member. |

### CustomImport object

| Field | Type | Notes |
|---|---|---|
| `path` | string | Import path (e.g. `@angular/core`, `rxjs`, or the `identifier` of a `customFile` in the batch). |
| `types` | string[] | Named exports to import. |
| `isDefault` | boolean | Import as default. |

### TemplateRef object

| Field | Type | Notes |
|---|---|---|
| `placeholder` | string | The `$token` string appearing in `code` or `type`. |
| `typeIdentifier` | string | The batch type it resolves to. |

### Decorator object

| Field | Type | Notes |
|---|---|---|
| `code` | string | Full decorator string (e.g. `@Injectable({ providedIn: 'root' })`). |
| `templateRefs` | TemplateRef[] | If the decorator references batch types via `$placeholder`. |

### ArrayType object (virtual — no file generated)

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string | Key for referencing this array type in properties. |
| `elementTypeIdentifier` | string | Batch type for element. Mutually exclusive with `elementPrimitiveType`. |
| `elementPrimitiveType` | string | Primitive element type (`String`, `Number`, etc.). |

### DictionaryType object (virtual — no file generated)

| Field | Type | Notes |
|---|---|---|
| `typeIdentifier` | string | Key for referencing this dict type in properties. |
| `keyPrimitiveType` | string | Key primitive type. |
| `valuePrimitiveType` | string | Value primitive type. Mutually exclusive with `valueTypeIdentifier`. |
| `valueTypeIdentifier` | string | Batch type for value. |

### ConcreteGenericClass object (virtual — no file generated)

| Field | Type | Notes |
|---|---|---|
| `identifier` | string | Key used as `baseClassTypeIdentifier` by a class. |
| `genericClassIdentifier` | string | The generic class being instantiated. |
| `genericArguments` | `{typeIdentifier: string}[]` | Type arguments resolving the generic parameters. |

### ConcreteGenericInterface object (virtual — no file generated)

Same shape as ConcreteGenericClass but for interfaces; referenced via `baseInterfaceTypeIdentifiers`.

### GenericArgument object (on classes/interfaces)

| Field | Type | Notes |
|---|---|---|
| `name` | string | Generic parameter name (e.g. `T`). |
| `constraintTypeIdentifier` | string | `extends` constraint — batch type. |
| `propertyName` | string | If MetaEngine should auto-create a property of type `T` (or `T[]`) on the class. |
| `isArrayProperty` | boolean | Makes the auto-created property `T[]`. |

---

## Critical Rules

### Rule 1 — ONE call with ALL related types
`typeIdentifier` references only resolve within the **current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting into multiple calls breaks cross-file import resolution — the second call cannot see types from the first.

### Rule 2 — Properties vs CustomCode distinction
- `properties[]` = **field declarations with types only, no initialization, no logic**
- `customCode[]` = **methods, initialized fields, any code with logic** (one item = exactly one member)
- Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

### Rule 3 — templateRefs for internal types in customCode/type
When `customCode` or a `type` field references a batch type, use `$placeholder` + `templateRefs`. Without this, MetaEngine cannot generate the import/using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**Critical in C#**: every internal type in customCode MUST use templateRefs or `using` directives for cross-namespace types won't be generated.

### Rule 4 — Never add framework imports to customImports
MetaEngine auto-injects standard library types. Adding them manually causes duplication or errors. Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

Auto-imported (never specify in customImports):
- **TypeScript**: no imports needed — built-in types
- **C#**: `System.*`, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.*
- **Python**: `typing.*`, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses
- **Java**: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, jakarta.validation.*, jackson.*
- **Kotlin**: `java.time.*`, `java.math.*`, `java.util.UUID`, kotlinx.serialization.*
- **Go**: time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more
- **Swift**: Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.)
- **Groovy**: `java.time.*`, `java.math.*`, java.util (UUID, Date), java.io (File, InputStream, OutputStream)
- **Scala**: `java.time.*`, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.*
- **PHP**: DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable

### Rule 5 — templateRefs are ONLY for internal batch types
External library types → `customImports`. Same-batch types → `typeIdentifier` or `templateRefs`. Never mix.

### Rule 6 — Constructor parameters auto-create properties (C#/Java/Go/Groovy)
In these languages, constructor parameters **automatically become class properties**. Do NOT also list them in `properties[]` — causes "Sequence contains more than one matching element" errors.

### Rule 7 — Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` create reusable type references only. They never produce output files. Use them by referencing their `typeIdentifier` in properties of file-generating types.

---

## Primitive Type Mappings

| MetaEngine primitiveType | TypeScript | C# | Python | Java | Go |
|---|---|---|---|---|---|
| `String` | `string` | `string` | `str` | `String` | `string` |
| `Number` | `number` | `int` (**not double**) | `int` | `int` | `int` |
| `Boolean` | `boolean` | `bool` | `bool` | `boolean` | `bool` |
| `Date` | `Date` | `DateTime` | `datetime` | `LocalDateTime` | `time.Time` |
| `Any` | `unknown` | `object` | `Any` | `Object` | `interface{}` |

**C# gotcha**: `Number` → `int`. Use `"type": "decimal"` or `"type": "double"` for non-integer numbers.

---

## Output Structure

MetaEngine produces one file per file-generating type (interface, class, enum, customFile). Files are placed at `path/name.ext` relative to the output root. Language-specific suffixes are applied automatically:
- TypeScript interfaces: `user-repository.ts` (strips `I`, uses kebab-case)
- TypeScript enums: `order-status.enum.ts`
- C#: `UserRepository.cs`, `OrderStatus.cs`

The engine handles:
- All import/using directive generation (for both batch cross-references and framework types)
- Language-specific naming conventions (Java `ALL_CAPS` enum members, Python `snake_case` methods)
- File naming and directory structure

---

## Patterns Reference

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

### Generic class + concrete instantiation

```jsonc
{
  "classes": [
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{
       "name": "T", "constraintTypeIdentifier": "base-entity",
       "propertyName": "items", "isArrayProperty": true
     }],
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

Reference via `"typeIdentifier": "user-list"` in properties.

### Complex type with templateRefs in property

```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
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

### Service with external DI (Angular/TypeScript)

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

### Interface with method signatures (correct pattern for implementable interfaces)

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

**Do NOT** use function-typed properties for interface method signatures that a class will `implements` — the implementing class will emit duplicate property declarations alongside the customCode methods.

### CustomFiles for barrel exports and type aliases

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

The `identifier` field on `customFile` enables import resolution by identifier string (auto-resolves to relative path).

---

## Language-Specific Notes

### TypeScript
- MetaEngine strips `I` prefix from interface names: `IUserRepository` → exported as `UserRepository`
- Use `fileName: "i-user-repository"` on the interface to avoid file name collision with implementing class
- `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- `\n` in customCode auto-indented
- Decorators supported directly on classes, properties, customCode items

### C#
- `I` prefix preserved on interface names
- `Number` → `int` (NOT `double`/`decimal`). Use `"type": "decimal"` or `"type": "double"` explicitly
- `packageName` sets namespace. Omit for GlobalUsings pattern
- Interface properties: `{ get; }`. Class properties: `{ get; set; }`
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs
- `isOptional` on properties generates nullable reference type (`string?`)
- Every internal cross-namespace type in customCode MUST use templateRefs or `using` directives won't be generated

### Python
- Must provide explicit 4-space indentation after `\n` in customCode
- `typing` imports are automatic

### Go
- Requires `packageName` for multi-file projects
- No constructors — use factory functions in customCode

### Java / Kotlin
- Enum member names: conventionally `ALL_CAPS` (engine applies this automatically)
- Constructor parameters auto-create properties — do not duplicate in `properties[]`

---

## Common Mistakes to Avoid

1. **Missing type in batch**: referencing a `typeIdentifier` that isn't defined in the same call — the property is silently dropped. Verify every typeIdentifier matches a defined type.

2. **Method signatures as function-typed properties**: for interfaces that a class will `implements`, use `customCode` for signatures, NOT `"type": "() => Promise<User[]>"` in properties.

3. **Raw internal type strings in customCode**: writing `"code": "private repo: IUserRepository"` without templateRefs means no import is generated. Always use `$placeholder` + templateRefs for batch types.

4. **C# `arrayTypes` when `List<T>` needed**: `arrayTypes` generate `IEnumerable<T>`. Use `"type": "List<$user>"` with templateRefs for mutable lists.

5. **Manual framework imports**: do not add `System.*`, `typing.*`, `java.util.*` to `customImports` — they are auto-injected.

6. **Duplicate constructor params**: in C#/Java/Go/Groovy, fields declared in `constructorParameters` automatically become properties. Listing the same field in `properties[]` causes a generation error.

7. **Reserved word property names**: avoid `delete`, `class`, `import` as property names. Use `remove`, `clazz`, `importData` etc.

8. **Splitting related types across calls**: all types that reference each other must be in ONE call. Cross-call import resolution does not work.

9. **C# `Number` → `double` assumption**: it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.

10. **TypeScript file name collision**: when an `I`-prefixed interface and its implementing class have the same base name, set `fileName` on the interface (e.g. `"fileName": "i-user-repository"`) to prevent the engine from generating both as the same filename.

---

## Summary Checklist for generate_code Calls

- [ ] All mutually-referencing types are in ONE call
- [ ] Every `typeIdentifier` referenced in properties/customCode/templateRefs is defined in this batch
- [ ] `properties[]` contains only type declarations (no methods, no initialization)
- [ ] `customCode[]` contains only methods and initialized fields (one item = one member)
- [ ] Internal type references in `customCode`/`type` fields use `$placeholder` + `templateRefs`
- [ ] No framework/stdlib types in `customImports` (only external libraries)
- [ ] Constructor params NOT duplicated in `properties[]` (C#/Java/Go/Groovy)
- [ ] For C# `List<T>`: using `"type": "List<$x>"` + templateRefs, NOT `arrayTypes`
- [ ] For TS interface + implementing class with same base name: `fileName` set on interface
- [ ] Interface method signatures in `customCode`, NOT as function-typed `properties`
- [ ] Python `customCode` with multi-line bodies has explicit 4-space indent after `\n`
- [ ] Go multi-file project has `packageName` on all types
