# MetaEngine MCP — Knowledge Brief (Warmup Summary)

This is a self-contained brief for a generation session that will NOT have access to MetaEngine's `linkedResources`. It captures everything required to call `mcp__metaengine__generate_code` correctly: tools, the full input schema, critical rules, patterns, language-specific behaviors, output expectations, and common mistakes.

MetaEngine is a **semantic code generation system**: you describe types, relationships, and methods as structured JSON; MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, it resolves cross-references, manages imports, and applies language idioms automatically. A single well-formed JSON call replaces dozens of individual file writes.

---

## Tools exposed

- **`mcp__metaengine__metaengine_initialize`** — Returns the AI guidance + critical patterns. Optional arg `language` (one of `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php`). Call only when you need refresher; not required to generate.
- **`mcp__metaengine__generate_code`** — Primary tool. Takes a structured JSON spec (schema below). Writes generated files to disk under `outputPath` (default `.`). Returns generated file list (and contents if `dryRun: true`).
- **`mcp__metaengine__load_spec_from_file`** — Same as `generate_code` but reads the spec from a JSON file. Args: `specFilePath` (required, absolute or relative), and optional overrides `outputPath`, `skipExisting`, `dryRun`. Useful when the spec is large; saves context.
- **`mcp__metaengine__generate_openapi`**, **`generate_graphql`**, **`generate_protobuf`**, **`generate_sql`** — convert specs from those formats. Not needed for the typical generation use case.

> Constraints in the warmup environment may make `generate_code` unavailable — the gen session must use whichever generation tool is actually allowed (typically `generate_code`).

---

## generate_code — full input schema

### Top-level fields

| Field | Type | Required | Description |
|---|---|---|---|
| `language` | enum | **yes** | One of: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `classes` | array | no | Class definitions (regular and generic templates) |
| `interfaces` | array | no | Interface definitions (regular and generic templates) |
| `enums` | array | no | Enum definitions |
| `arrayTypes` | array | no | Reusable array type references (NO files) |
| `dictionaryTypes` | array | no | Reusable map/dict type references (NO files) |
| `concreteGenericClasses` | array | no | Concrete generic implementations like `Repository<User>` (NO files) |
| `concreteGenericInterfaces` | array | no | Concrete generic interface implementations (NO files) |
| `customFiles` | array | no | Free-form files (type aliases, barrel exports, utilities) — NO class wrapper |
| `outputPath` | string | no | Directory to write to. Default `.` (current dir) |
| `packageName` | string | no | Namespace/package for generated code. Defaults: Go=`github.com/metaengine/demo`; Java/Kotlin/Groovy=`com.metaengine.generated`; C#=omit/empty for GlobalUsings (no namespace). |
| `initialize` | bool | no | Initialize properties with default values. Default `false`. |
| `skipExisting` | bool | no | If true, do not overwrite existing files. Default `true`. |
| `dryRun` | bool | no | If true, returns generated content without writing. Default `false`. |

### `classes[]` item

| Field | Type | Description |
|---|---|---|
| `name` | string | Class name |
| `typeIdentifier` | string | Unique id for cross-references in the same call |
| `path` | string | Subdir for the file (e.g. `services`, `services/auth`) |
| `fileName` | string | Override file name (no extension) |
| `comment` | string | Class-level doc comment |
| `isAbstract` | bool | Abstract class |
| `baseClassTypeIdentifier` | string | Extends another defined class (or `concreteGenericClasses` identifier) |
| `interfaceTypeIdentifiers` | string[] | Implements these interfaces |
| `genericArguments` | array | Makes this a generic class template like `Repository<T>`. Each item: `{name, constraintTypeIdentifier?, propertyName?, isArrayProperty?}` |
| `constructorParameters` | array | Each: `{name, primitiveType?, type?, typeIdentifier?}`. **In C#/Java/Go/Groovy these auto-create properties — never duplicate them in `properties[]`.** |
| `properties` | array | Field declarations (see schema below) |
| `customCode` | array | Methods, initialized fields, anything with logic. One member per item. |
| `customImports` | array | External-library imports only. Each: `{path, types?[]}` |
| `decorators` | array | Class-level decorators. Each: `{code, templateRefs?[]}` |

### `properties[]` item (used by classes & interfaces)

| Field | Type | Description |
|---|---|---|
| `name` | string | Property name |
| `primitiveType` | enum | One of `String`, `Number`, `Boolean`, `Date`, `Any`. Mutually exclusive with `type`/`typeIdentifier`. |
| `typeIdentifier` | string | Reference to another generated type |
| `type` | string | Raw type expression for complex/external types. Combine with `templateRefs` to embed `$placeholder` for internal types (e.g. `"Map<string, $resp>"`). |
| `templateRefs` | array | `[{placeholder, typeIdentifier}]` — substitutions for `$placeholder` tokens in `type` |
| `isOptional` | bool | Generates optional/nullable form (`string?` in C#, `Optional` in TS unions, etc.) |
| `isInitializer` | bool | Add a default value initializer |
| `comment` | string | Doc comment for the property |
| `commentTemplateRefs` | array | templateRefs usable inside the doc comment |
| `decorators` | array | Property decorators (e.g. `@IsEmail()`, `@Required()`). Each: `{code, templateRefs?[]}` |

### `customCode[]` item (used by classes, interfaces, customFiles, decorators, etc.)

```jsonc
{
  "code": "getUser(id: string): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

- One `customCode` block = exactly ONE method, ONE initialized field, OR one statement.
- MetaEngine inserts blank lines between blocks automatically.
- Use `$placeholder` + `templateRefs` to refer to any type in the same generation batch — that triggers correct import emission.

### `customImports[]` item

```jsonc
{"path": "@angular/core", "types": ["Injectable", "inject"]}
```

- ONLY for external libraries / framework code. Never for types you generate in this batch (use `templateRefs` instead) and never for built-ins (auto-imported).
- For TS, `path` may also be a relative path (e.g. `../utils/types`) or a `customFiles[].identifier` (then resolved automatically to its relative path).
- `types` can be omitted to import the module side-effects only.

### `decorators[]` item

```jsonc
{"code": "@Injectable({ providedIn: 'root' })", "templateRefs": []}
```

### `interfaces[]` item

Same shape as `classes` but no `constructorParameters`. Use `customCode` for method signatures (NOT function-typed properties — see Critical Rule #2 below). `interfaceTypeIdentifiers` extends other interfaces.

### `enums[]` item

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "path": "models",
  "fileName": "order-status",
  "comment": "Order lifecycle states",
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2}
  ]
}
```

Filename auto-suffixes: `order-status.enum.ts` for TS, `OrderStatus.cs` for C#, etc.

### `arrayTypes[]` item (virtual — produces NO file)

```jsonc
{"typeIdentifier": "user-list", "elementTypeIdentifier": "user"}
{"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
```

Use one of `elementPrimitiveType` (`String|Number|Boolean|Date|Any`) OR `elementTypeIdentifier`.

### `dictionaryTypes[]` item (virtual — produces NO file)

```jsonc
{"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
```

All four key/value combinations are supported (primitive×primitive, primitive×custom, custom×primitive, custom×custom). Optional `keyType` accepts a raw string-literal key type.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` (virtual — produces NO file)

```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}
```

Reference its `identifier` from `baseClassTypeIdentifier`, `interfaceTypeIdentifiers`, or via `templateRefs` to emit correctly-typed inline references like `Repository<User>`.

### `customFiles[]` item (free-form file, no class wrapper)

```jsonc
{
  "name": "types",
  "path": "shared",
  "fileName": "types",
  "identifier": "shared-types",
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"}
  ],
  "customImports": []
}
```

`identifier` enables other files to `customImports` against this file (relative path is auto-resolved).

---

## CRITICAL RULES (most-violated — internalize these)

### 1. Generate ALL related types in ONE call
`typeIdentifier` references resolve only within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. **Never split per-domain.** Cross-file imports rely on the entire typegraph being visible at generation time.

### 2. `properties` = type declarations only. `customCode` = everything else.
- `properties[]` declares fields with types only — no initializers, no method bodies.
- `customCode[]` handles methods, initialized fields, and any code with logic. One `customCode` item = exactly one member.
- Never put method signatures as function-typed properties on interfaces you'll `implements` — the implementing class will end up duplicating them. Define interface methods in `customCode` instead.

### 3. Use `templateRefs` for internal type references in `customCode` / `type` strings
When custom code or a complex `type` expression mentions a type that lives in the same batch, use a `$placeholder` and add a `templateRefs` entry. Without this, MetaEngine cannot emit the correct import / using directive.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**C# is especially strict**: every internal type reference in `customCode` MUST go through `templateRefs`, otherwise cross-namespace `using` directives are missed.

### 4. NEVER add framework imports to `customImports`
MetaEngine auto-imports standard library types. Manual entries cause duplicates or errors.

| Language | Auto-imported (do NOT specify) |
|---|---|
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, +more |
| Swift | `Foundation` (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, ...) |
| Rust | `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream) |
| Scala | `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | (no framework imports needed — built-in types) |

`customImports` is reserved for **external libraries only** (`@angular/core`, `FluentValidation`, `rxjs`, etc.).

### 5. `templateRefs` are ONLY for internal types
External library types must use `customImports`. Mnemonic: same batch → `typeIdentifier` / `templateRefs`. External library → `customImports`. Never mix.

### 6. Constructor parameters auto-create properties (C#, Java, Go, Groovy)
Do NOT also list them in `properties[]`. Doing so triggers: `Sequence contains more than one matching element`. Put shared fields only in `constructorParameters`; put extra fields (createdAt, etc.) in `properties[]`. (TypeScript also auto-creates them, so the same rule applies.)

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reusable type references only. They never produce files. Reference them via `typeIdentifier`/`identifier` in real (file-generating) types' properties or `baseClassTypeIdentifier`.

---

## Pattern Reference (idioms you can copy)

### Cross-referenced interfaces

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

### Inheritance + methods

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

### Generic class + concrete subtype via `concreteGenericClasses`

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

### Service with DI + external imports

```jsonc
{
  "classes": [{
    "name": "ApiService", "typeIdentifier": "api-service",
    "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
    "customImports": [
      {"path": "@angular/core", "types": ["Injectable", "inject"]},
      {"path": "@angular/common/http", "types": ["HttpClient"]},
      {"path": "rxjs", "types": ["Observable"]}
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

### Type aliases via `customFiles`

```jsonc
{
  "customFiles": [{
    "name": "types", "path": "utils", "identifier": "shared-types",
    "customCode": [
      {"code": "export type UserId = string;"},
      {"code": "export type Status = 'active' | 'inactive' | 'pending';"},
      {"code": "export type ResultSet<T> = { data: T[]; total: number; page: number; };"}
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers",
    "customImports": [{"path": "shared-types"}],
    "customCode": [{"code": "static format(email: Email): string { return email.trim(); }"}]
  }]
}
```

`identifier: "shared-types"` lets the helper import via the identifier; MetaEngine resolves the relative path.

### Interface method signatures (TS / C#)

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

The `;` ending is important — these are *signatures*, not bodies.

### Complex `type` expression with `templateRefs`

```jsonc
"properties": [{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

`templateRefs` work in `properties.type`, `customCode.code`, and `decorators.code`.

### Constructor parameters — correct usage

```jsonc
{
  "language": "typescript",
  "enums": [{"name": "Status", "typeIdentifier": "status",
    "members": [{"name": "Active", "value": 1}]}],
  "classes": [{
    "name": "User", "typeIdentifier": "user",
    "constructorParameters": [
      {"name": "email", "type": "string"},
      {"name": "status", "typeIdentifier": "status"}
    ],
    "properties": [
      {"name": "createdAt", "primitiveType": "Date"}
    ]
  }]
}
```

Generates:

```typescript
import { Status } from './status.enum';
export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

---

## Output structure / behavior

- One file per file-generating type (class, interface, enum, customFile). Virtual types (arrayTypes, dictionaryTypes, concreteGenericClasses, concreteGenericInterfaces) emit NO files.
- File names default to kebab-case for TS (e.g. `user-service.ts`), PascalCase for C# (`UserService.cs`), snake_case for Python (`user_service.py`), Pascal for Java (`UserService.java`). Override with `fileName` (no extension).
- `path` is appended to `outputPath`. Relative imports between files are computed automatically.
- Enums get a `.enum` infix in TS (`order-status.enum.ts`); other languages just use the type name.
- `dryRun: true` returns generated content in the response without writing — use to inspect before committing files.
- `skipExisting: true` (default) leaves existing files untouched; set to `false` to overwrite.
- `customCode` blocks are separated by blank lines; `\n` inside a block is honored. **Python requires explicit 4-space indent on continuation lines inside a block.**

---

## Language-specific notes

### TypeScript
- Strips `I` prefix from interface names: `IUserRepository` exports as `UserRepository`. Use `fileName` (e.g. `i-user-repository`) to disambiguate file names when the implementing class would collide.
- Primitives: `String→string`, `Number→number`, `Boolean→boolean`, `Date→Date`, `Any→unknown`.
- arrayTypes generate `Array<T>`; dictionaryTypes generate `Record<K, V>`.
- Auto-indents `\n` inside `customCode`. No framework imports needed.
- Decorators emitted directly.
- `language-aware idiomatic transformations` may slightly normalize names (camelCase methods, etc.) — the use-case judge tolerates these.

### C#
- `I` prefix is preserved on interfaces.
- Primitives: `Number→int` (NOT `double`). For non-integers, use `"type": "decimal"` or `"type": "double"`.
- `packageName` sets the namespace; omit for GlobalUsings (no namespace declaration).
- Interface properties → `{ get; }`; class properties → `{ get; set; }`.
- arrayTypes → `IEnumerable<T>`. For mutable lists, use `"type": "List<$user>"` with `templateRefs`.
- `isOptional: true` on a property → nullable reference type (`string?`).
- Every internal type reference inside `customCode` MUST use `templateRefs` (otherwise no `using` is emitted).

### Python
- Provide explicit 4-space indentation after `\n` inside `customCode` (no auto-indent).
- typing imports auto-added.
- Methods are `snake_case` by language idiom — judge tolerates this even if input names are camelCase.

### Java
- `java.util.*`, `java.time.*`, `java.util.stream.*`, jackson, jakarta validation — all auto-imported.
- Constructor parameters auto-become final fields (do not duplicate in `properties`).
- Enum members emit `ALL_CAPS` per Java convention — judge tolerates this.

### Kotlin
- `java.time.*`, `java.math.*`, `kotlinx.serialization.*` auto-imported.
- Idiomatic data classes / val/var.

### Go
- Requires `packageName` for multi-file projects (default `github.com/metaengine/demo`).
- No constructors — write factory functions in `customCode`.
- Constructor parameters still auto-add the corresponding struct fields; don't duplicate them in `properties`.

### Groovy
- Constructor parameters auto-add fields; same rule applies.
- `java.util` (UUID/Date), `java.io` (File/InputStream/OutputStream), `java.time.*`, `java.math.*` auto-imported.

### Scala
- `java.time.*`, `scala.math.{BigDecimal, BigInt}`, `java.util.UUID`, `scala.collection.mutable.*` auto-imported.

### Swift
- `Foundation` types (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder) auto-imported.

### PHP
- `DateTime`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` auto-imported.

### Rust
- `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde` auto-imported.

---

## Common mistakes (the 10 that bite hardest)

1. Referencing a `typeIdentifier` that doesn't exist in the batch — the property is silently dropped. Verify every reference.
2. Putting interface method signatures as function-typed `properties` — implementing class will duplicate them. Use `customCode` with `;` endings.
3. Internal type names as raw strings in `customCode` (e.g., `"private repo: IUserRepository"`) — no import generated. Use `$placeholder` + `templateRefs`.
4. Using `arrayTypes` in C# when you need `List<T>` — arrayTypes emit `IEnumerable<T>`. Use `"type": "List<$x>"` with templateRefs.
5. Adding framework types to `customImports` (`System.*`, `typing.*`, `java.util.*`, etc.) — duplication/error. Let MetaEngine handle them.
6. Duplicating constructor parameter names in `properties[]` (C#/Java/Go/Groovy/TS) — `Sequence contains more than one matching element`. Only place them in `constructorParameters`; extras-only in `properties`.
7. Reserved-word property names (`delete`, `class`, `import`) — emit broken code. Use safe alternatives.
8. Splitting related types across multiple `generate_code` calls — cross-file imports break. **One call per related typegraph.**
9. Expecting `Number → double` in C# (it maps to `int`). Use `"type": "double"` or `"type": "decimal"` explicitly.
10. Forgetting `fileName` on an `I`-prefixed interface in TypeScript when its implementing class shares the stem name — file collision. Set e.g. `"fileName": "i-user-repository"`.

---

## Operational checklist before calling `generate_code`

1. **One call.** Have you bundled every cross-referenced class/interface/enum?
2. **Identifiers consistent.** Every `typeIdentifier`/`identifier` referenced from `baseClassTypeIdentifier`, `interfaceTypeIdentifiers`, `typeIdentifier` in props, `templateRefs`, `concreteGenericClasses.genericClassIdentifier`, etc. exists in this same call?
3. **Methods are in `customCode`** (one per item), and properties are bare type declarations?
4. **Internal refs use templateRefs**, external refs use `customImports`?
5. **No duplicated constructor params in `properties`**?
6. **No framework imports** in `customImports`?
7. **`language` set**? `outputPath` set if you want files outside `.`?
8. If using virtual types (arrayTypes/dictionaryTypes/concreteGeneric*), is at least one file-generating type referencing them so they end up in someone's import list?

If all eight are satisfied, the call should produce a clean, compilable batch.

---

## Quick reference — primitive types

`primitiveType` values across all languages: `String`, `Number`, `Boolean`, `Date`, `Any`. Mapping:

| primitiveType | TS | C# | Python | Go | Java | Kotlin |
|---|---|---|---|---|---|---|
| String | `string` | `string` | `str` | `string` | `String` | `String` |
| Number | `number` | `int` | `int` | `int` | `Integer` | `Int` |
| Boolean | `boolean` | `bool` | `bool` | `bool` | `Boolean` | `Boolean` |
| Date | `Date` | `DateTime` | `datetime` | `time.Time` | `LocalDateTime` | `LocalDateTime` |
| Any | `unknown` | `object` | `Any` | `interface{}` | `Object` | `Any` |

For non-integer numbers (decimal, double, float), DON'T use `Number`; instead use `"type": "decimal"` / `"type": "double"` explicitly.
