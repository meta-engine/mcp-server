# MetaEngine MCP — Knowledge Brief

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON — MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, and PHP. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. A single well-formed JSON call replaces dozens of error-prone file writes.

---

## Tools Exposed

### `mcp__metaengine__metaengine_initialize`
- **Purpose**: Returns essential MetaEngine patterns and documentation resources.
- **Parameters**: `language` (optional enum): `"typescript"` | `"python"` | `"go"` | `"csharp"` | `"java"` | `"kotlin"` | `"groovy"` | `"scala"` | `"swift"` | `"php"`
- **When to call**: Before generating code for the first time, or when you need guidance. Returns the critical rules and pattern reference.

### `mcp__metaengine__generate_code`
- **Purpose**: Generates compilable source files from a structured JSON spec.
- **Input**: A JSON object describing `language`, `interfaces`, `classes`, `enums`, `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`, `customFiles`, etc.
- **Output**: One or more generated source files with correct imports and language idioms.

### `mcp__metaengine__load_spec_from_file`
- **Purpose**: Loads a MetaEngine spec from a file rather than inline JSON.

### `mcp__metaengine__generate_graphql`, `mcp__metaengine__generate_openapi`, `mcp__metaengine__generate_protobuf`, `mcp__metaengine__generate_sql`
- **Purpose**: Spec conversion tools — convert OpenAPI/GraphQL/Protobuf/SQL specs to MetaEngine-compatible code generation calls.

---

## `generate_code` — Input Schema (Full)

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `language` | string (required) | Target language: `"typescript"`, `"csharp"`, `"python"`, `"go"`, `"java"`, `"kotlin"`, `"groovy"`, `"scala"`, `"swift"`, `"php"` |
| `interfaces` | array | Interface type definitions |
| `classes` | array | Class type definitions |
| `enums` | array | Enum type definitions |
| `arrayTypes` | array | Virtual array type aliases (no files generated) |
| `dictionaryTypes` | array | Virtual dictionary/map type aliases (no files generated) |
| `concreteGenericClasses` | array | Virtual concrete instantiations of generic classes (no files generated) |
| `concreteGenericInterfaces` | array | Virtual concrete instantiations of generic interfaces (no files generated) |
| `customFiles` | array | Arbitrary source files (type aliases, barrel exports, etc.) |

### Interface definition fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Interface name |
| `typeIdentifier` | string | Yes | Unique ID for cross-referencing within the batch |
| `fileName` | string | No | Override generated filename (important in TypeScript to avoid I-prefix collisions) |
| `path` | string | No | Subdirectory path for the file |
| `packageName` | string | No | Package/namespace (C#, Java, Go) |
| `properties` | array | No | Field declarations (type only, no initialization) |
| `customCode` | array | No | Method signatures, initialized fields, any code with logic |
| `customImports` | array | No | External library imports only |
| `decorators` | array | No | Language decorators/attributes |
| `isGeneric` | boolean | No | Whether the interface is generic |
| `genericArguments` | array | No | Generic type parameter definitions |
| `baseInterfaceTypeIdentifiers` | array | No | Extends other interfaces — array of typeIdentifiers |

### Class definition fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Class name |
| `typeIdentifier` | string | Yes | Unique ID for cross-referencing |
| `fileName` | string | No | Override generated filename |
| `path` | string | No | Subdirectory path |
| `packageName` | string | No | Namespace (C#, Java, Kotlin, Go) |
| `isAbstract` | boolean | No | Generate as abstract class |
| `properties` | array | No | Field declarations (uninitialized, type only) |
| `customCode` | array | No | Methods, initialized fields, constructors with logic |
| `customImports` | array | No | External library imports only |
| `decorators` | array | No | Decorators/attributes |
| `baseClassTypeIdentifier` | string | No | Extends a class — single typeIdentifier |
| `implementsTypeIdentifiers` | array | No | Implements interfaces — array of typeIdentifiers |
| `constructorParameters` | array | No | Constructor params (C#/Java/Go/Groovy: auto-create properties — do NOT duplicate in properties[]) |
| `genericArguments` | array | No | Generic type parameter definitions |

### Enum definition fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Enum name |
| `typeIdentifier` | string | Yes | Unique ID for cross-referencing |
| `fileName` | string | No | Override filename (auto-suffix: `.enum.ts` in TS, etc.) |
| `path` | string | No | Subdirectory path |
| `packageName` | string | No | Namespace |
| `members` | array | Yes | Array of `{ name: string, value: number \| string }` |

### Property definition fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Property name |
| `primitiveType` | string | One of primitiveType/typeIdentifier/type | Primitive: `"String"`, `"Number"`, `"Boolean"`, `"Date"`, `"Any"` |
| `typeIdentifier` | string | One of above | References an internal type in the same batch |
| `type` | string | One of above | Raw type string (use with templateRefs for internal references) |
| `isOptional` | boolean | No | Makes property optional/nullable |
| `isArray` | boolean | No | Wraps type as array |
| `templateRefs` | array | No | Placeholder → typeIdentifier mappings when using `type` field with internal refs |

### customCode item fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `code` | string | Yes | The method body, initialized field, or code member. One item = one member. |
| `templateRefs` | array | No | Placeholder → typeIdentifier mappings for internal type references in the code string |

### customImports item fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Import path (e.g., `"@angular/core"`, `"rxjs"`) |
| `types` | array | No | Named imports from that path (e.g., `["Injectable", "inject"]`) |

### templateRefs item fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `placeholder` | string | Yes | The `$placeholder` token in the code/type string (e.g., `"$user"`) |
| `typeIdentifier` | string | Yes | The typeIdentifier in the same batch that resolves this placeholder |

### arrayTypes item fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `typeIdentifier` | string | Yes | Unique ID for the virtual type |
| `elementTypeIdentifier` | string | One of these | References an internal type |
| `elementPrimitiveType` | string | One of these | Primitive element type |

### dictionaryTypes item fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `typeIdentifier` | string | Yes | Unique ID |
| `keyPrimitiveType` | string | Yes | Key primitive type |
| `valueTypeIdentifier` | string | One of these | Internal type value |
| `valuePrimitiveType` | string | One of these | Primitive value type |

### concreteGenericClasses item fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `identifier` | string | Yes | Unique ID — referenced by a class's `baseClassTypeIdentifier` |
| `genericClassIdentifier` | string | Yes | typeIdentifier of the generic class to instantiate |
| `genericArguments` | array | Yes | Array of `{ typeIdentifier: string }` filling in the type params |

### customFiles item fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | File name (without extension) |
| `path` | string | No | Subdirectory path |
| `identifier` | string | No | Enables import resolution — other files can reference this in `customImports.path` |
| `customCode` | array | No | Code members in the file |
| `customImports` | array | No | External imports |

---

## Critical Rules (Must Not Violate)

### Rule 1: Generate ALL related types in ONE call
`typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting related types across multiple calls causes unresolved references (silently dropped properties, missing imports).

### Rule 2: properties[] = type declarations only; customCode[] = everything else
- `properties[]`: Uninitialized field declarations with types. No methods, no initialization.
- `customCode[]`: Methods, initialized fields, constructor logic. One item per member.
- Never put methods in `properties[]`. Never put uninitialized type declarations in `customCode[]`.

### Rule 3: Use templateRefs for internal types in customCode
When customCode references a type from the same batch, use `$placeholder` syntax with `templateRefs`. This is what triggers automatic import generation.
```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```
Without templateRefs, MetaEngine cannot generate the import/using directive. In C#, every internal type reference in customCode MUST use templateRefs, or `using` directives for cross-namespace types won't be generated, causing compile failures.

### Rule 4: Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or errors.

**Auto-imported per language (never specify in customImports):**
- **TypeScript**: No imports needed — built-in types
- **C#**: `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*`
- **Python**: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`
- **Java**: `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, jackson
- **Kotlin**: `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`
- **Go**: `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, and more
- **Swift**: Foundation (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`, etc.)
- **Groovy**: `java.time.*`, `java.math.*`, `java.util (UUID, Date)`, `java.io`
- **Scala**: `java.time.*`, `scala.math`, `java.util.UUID`, `scala.collection.mutable.*`
- **PHP**: `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable`

Only use `customImports` for external libraries (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### Rule 5: templateRefs are ONLY for internal types
External library types → `customImports`. Same-batch types → `typeIdentifier` or `templateRefs`. Never mix.

### Rule 6: Constructor parameters auto-create properties (C#/Java/Go/Groovy)
In C#, Java, Go, and Groovy, constructor parameters automatically become class properties. Do NOT duplicate them in `properties[]` — this causes "Sequence contains more than one matching element" errors.

### Rule 7: Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, and `concreteGenericInterfaces` create reusable type references only. They never produce files. Use their `typeIdentifier`/`identifier` to reference them from real types.

---

## TypeScript-Specific Notes

- MetaEngine **strips `I` prefix** from interface names. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control the file name if collisions arise between an `I`-prefixed interface and its implementing class.
- Primitive mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`
- Auto-indent for `customCode` newlines (`\n`)
- Decorators supported directly
- Interface method signatures: use `customCode` (not function-typed properties) for methods that a class will `implements` — otherwise the implementing class duplicates them as property declarations
- Enum files auto-suffixed: `order-status.enum.ts`
- No imports needed for built-in types

---

## Output Structure

MetaEngine generates **one file per interface/class/enum** (plus any customFiles). Files are placed at the configured `path` subdirectory. Imports between generated files are resolved automatically based on typeIdentifier cross-references. The engine returns the generated file contents; the caller writes them to disk.

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
The `concreteGenericClasses` entry creates a virtual `Repository<User>` type. `UserRepository` extends it via `baseClassTypeIdentifier`. MetaEngine generates `extends Repository<User>` with correct imports.

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

### Complex type expressions with templateRefs
```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```
`templateRefs` work in `properties`, `customCode`, and `decorators`.

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
Enums auto-suffix filenames: `order-status.enum.ts` (TS).

### Service with external dependency injection (Angular/TypeScript)
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

### Interface with method signatures (TypeScript)
For interfaces that will be `implements`-ed by a class, define method signatures in `customCode`, NOT as function-typed properties:
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
If you use function-typed properties instead, the implementing class will duplicate them as property declarations alongside your `customCode` methods.

---

## Common Mistakes (Anti-Patterns)

1. **Splitting related types across multiple calls** → cross-batch references silently drop. Always batch everything in one call.
2. **Putting method signatures as function-typed properties** on interfaces you'll `implements` → duplicated declarations in implementing class. Use `customCode` for method signatures.
3. **Raw internal type strings in customCode** (e.g., `"code": "private repo: IUserRepository"`) → missing import. Use templateRefs: `"code": "private repo: $repo"` with mapping.
4. **Adding `System.*`, `typing.*`, `java.util.*` to customImports** → duplication/errors. Let MetaEngine handle all framework imports.
5. **Duplicating constructor parameters in properties[]** (C#/Java/Go/Groovy) → "Sequence contains more than one matching element" error.
6. **Using reserved words** (`delete`, `class`, `import`) as property names → use safe alternatives (`remove`, `clazz`, `importData`).
7. **Using arrayTypes in C# when you need `List<T>`** → arrayTypes generate `IEnumerable<T>` in C#. Use `"type": "List<$user>"` with templateRefs instead.
8. **Referencing a typeIdentifier that doesn't exist in the batch** → property silently dropped. Verify every typeIdentifier matches a defined type in the same call.
9. **Expecting `Number` to map to `double` in C#** → it maps to `int`. Use `"type": "double"` or `"type": "decimal"` explicitly.
10. **Forgetting `fileName` on I-prefixed interfaces in TypeScript** → MetaEngine strips the `I` prefix, causing file name collision with the implementing class. Set `"fileName": "i-user-repository"` on the interface.

---

## Summary Decision Tree

```
Need to generate code?
  ├─ ALL related types → ONE generate_code call
  ├─ Field with no logic? → properties[]
  ├─ Method / initialized field? → customCode[]
  ├─ References internal batch type in customCode/properties(type field)?
  │   └─ Use $placeholder + templateRefs
  ├─ External library? → customImports
  ├─ Array of internal type? → arrayTypes (virtual) + reference by typeIdentifier
  ├─ Generic class instantiation? → concreteGenericClasses (virtual) + baseClassTypeIdentifier
  └─ Type alias / barrel? → customFiles with identifier
```
