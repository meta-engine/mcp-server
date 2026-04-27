# MetaEngine MCP — Knowledge Brief (TypeScript focus)

This brief is self-contained. The next session has no access to MetaEngine docs and must rely on this file. MetaEngine is a semantic code generator: you describe types, relationships, and methods as a structured JSON spec; it emits compilable source files with imports and cross-references resolved automatically. One well-formed JSON call can replace dozens of file writes.

---

## Tools exposed by the MCP server

- `mcp__metaengine__metaengine_initialize(language?)` — Returns the documentation/guide. Already consulted; do NOT call again from the gen session, this brief replaces it.
- `mcp__metaengine__generate_code({...spec})` — The main generator. Takes a JSON spec describing all types and emits files. **Use this once with the entire spec.**
- `mcp__metaengine__load_spec_from_file({specFilePath, outputPath?, skipExisting?, dryRun?})` — Same generator, but the spec is loaded from a JSON file on disk. Useful for huge specs or version-controlled templates.

---

## Top-level `generate_code` input schema

Required: `language` (one of: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`).

Top-level fields (all optional except `language`):

| Field | Type | Purpose |
|---|---|---|
| `language` | enum (see above) | **Required.** Target language. |
| `outputPath` | string (default `.`) | Directory to write files into. |
| `packageName` | string | Namespace/package/module. Default differs per language (Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`). For C#, omit/empty = no namespace declaration (good for GlobalUsings). |
| `skipExisting` | bool (default `true`) | If true, files that already exist are not overwritten. |
| `dryRun` | bool (default `false`) | Preview mode — returns generated content in the response, no disk writes. |
| `initialize` | bool (default `false`) | If true, properties get default-value initialization. |
| `classes` | Class[] | Class definitions (regular and generic templates). Generates files. |
| `interfaces` | Interface[] | Interface definitions (regular and generic templates). Generates files. |
| `enums` | Enum[] | Enum definitions. Generates files. |
| `customFiles` | CustomFile[] | Free-form files (type aliases, barrels, utilities) without a class wrapper. Generates files. |
| `arrayTypes` | ArrayType[] | Reusable array type references. **No files generated.** |
| `dictionaryTypes` | DictionaryType[] | Reusable dictionary/map type references. **No files generated.** |
| `concreteGenericClasses` | ConcreteGeneric[] | Concrete instantiations of generic classes (e.g. `Repository<User>`). **No files generated.** |
| `concreteGenericInterfaces` | ConcreteGeneric[] | Concrete instantiations of generic interfaces. **No files generated.** |

### Class object

```jsonc
{
  "name": "User",                              // class name (required)
  "typeIdentifier": "user",                    // unique key used for cross-references
  "path": "models",                            // dir under outputPath, e.g. "models", "services/auth"
  "fileName": "user",                          // optional override (no extension)
  "comment": "Represents a user.",             // doc comment
  "isAbstract": false,
  "baseClassTypeIdentifier": "base-entity",    // typeIdentifier of base class
  "interfaceTypeIdentifiers": ["i-user"],      // typeIdentifiers of interfaces to implement
  "genericArguments": [                        // makes this a generic template
    {
      "name": "T",
      "constraintTypeIdentifier": "base-entity", // optional 'where T : BaseEntity' style
      "propertyName": "items",                   // creates property of type T
      "isArrayProperty": true                    // when true, property is T[]
    }
  ],
  "constructorParameters": [                   // ⚠ in C#/Java/Go/Groovy, these auto-create properties — do NOT also list in "properties"
    { "name": "id", "primitiveType": "String" },
    { "name": "address", "typeIdentifier": "address" },
    { "name": "raw", "type": "Buffer" }        // free-form type string
  ],
  "properties": [ Property, ... ],
  "customCode": [ CodeBlock, ... ],            // ONE per member (method or initialized field)
  "decorators": [ { "code": "@Injectable()", "templateRefs": [...] } ],
  "customImports": [
    { "path": "@angular/core", "types": ["Injectable", "inject"] }
  ]
}
```

### Property object

```jsonc
{
  "name": "email",
  "primitiveType": "String",     // one of: String | Number | Boolean | Date | Any
  // OR
  "typeIdentifier": "address",   // reference to another type in this batch
  // OR
  "type": "Map<string, $resp>",  // free-form type expression; can use $placeholders
  "templateRefs": [              // resolves $placeholders in `type` (and triggers imports)
    { "placeholder": "$resp", "typeIdentifier": "api-response" }
  ],
  "isOptional": true,
  "isInitializer": false,        // adds default-value init
  "comment": "User email",
  "commentTemplateRefs": [...],
  "decorators": [ { "code": "@IsEmail()", "templateRefs": [...] } ]
}
```

### CodeBlock (used in `customCode` and decorators)

```jsonc
{
  "code": "getUser(): Promise<$user> { return Promise.resolve(this.user); }",
  "templateRefs": [
    { "placeholder": "$user", "typeIdentifier": "user" }
  ]
}
```

**One `customCode` item = exactly one member.** Newlines between blocks are added automatically.

### Interface object

Same shape as Class but typically only uses: `name`, `typeIdentifier`, `path`, `fileName`, `properties`, `customCode` (for method signatures), `interfaceTypeIdentifiers` (to extend other interfaces), `genericArguments`, `decorators`, `customImports`, `comment`.

### Enum object

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "path": "models",
  "fileName": "order-status",       // optional
  "comment": "Order lifecycle states.",
  "members": [
    { "name": "Pending", "value": 0 },
    { "name": "Shipped", "value": 2 }
  ]
}
```

### CustomFile object (no class wrapper — for type aliases, barrel exports, etc.)

```jsonc
{
  "name": "types",                  // file name without extension
  "fileName": "types",              // optional override
  "path": "shared",
  "identifier": "shared-types",     // optional — referenced by other files in customImports.path
  "customCode": [
    { "code": "export type UserId = string;" },
    { "code": "export type Email = string;" }
  ],
  "customImports": [
    { "path": "shared-types" }
  ]
}
```

### ArrayType (virtual — no file)

```jsonc
{ "typeIdentifier": "user-list", "elementTypeIdentifier": "user" }
{ "typeIdentifier": "string-array", "elementPrimitiveType": "String" }
```
Reference via `"typeIdentifier": "user-list"` in a property.

### DictionaryType (virtual — no file)

```jsonc
{
  "typeIdentifier": "user-lookup",
  "keyPrimitiveType": "String",       // or keyTypeIdentifier / keyType (free-form)
  "valueTypeIdentifier": "user"       // or valuePrimitiveType
}
```

### ConcreteGenericClass / ConcreteGenericInterface (virtual — no file)

```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",     // (or genericClassIdentifier on interface variant)
  "genericArguments": [ { "typeIdentifier": "user" } ]
}
```
Reference via `"baseClassTypeIdentifier": "user-repo-concrete"` or in `interfaceTypeIdentifiers`.

---

## Critical rules — break these and generation fails

### 1. ONE call with the whole spec

`typeIdentifier` references only resolve within the same batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting by domain breaks the type graph and cross-file imports.

### 2. `properties` = type declarations only. `customCode` = everything with logic.

- `properties[]` declares a typed field, no logic and no initializer (unless `isInitializer: true`).
- `customCode[]` is for methods, initialized fields (`private http = inject(HttpClient);`), and any code with a body.
- One `customCode` item = exactly one member.
- **Never** put method signatures or initialized fields as a function-typed `property` — they will collide with the implementing methods or generate broken code.

### 3. `templateRefs` are for INTERNAL types referenced inside free-form code/strings

Whenever `customCode`, `decorators`, comment text, or a free-form `type` string mentions a type from the same batch, write it as `$placeholder` and add an entry to `templateRefs`:

```jsonc
{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
}
```

This triggers automatic import resolution. Without `templateRefs`, internal type names typed as raw strings will not produce imports — across namespaces this fails to compile (especially in C#).

### 4. `customImports` is ONLY for external libraries

Use `customImports` for external library types like `@angular/core`, `rxjs`, `FluentValidation`. Internal (same-batch) types use `typeIdentifier` / `templateRefs` instead. Never mix them.

### 5. Never add framework imports to `customImports`

The engine auto-imports stdlib types per language. Adding them manually causes duplication or compile errors. Auto-imported per language:

| Language | Auto-imported (don't list in customImports) |
|---|---|
| TypeScript | (no imports needed — built-in types) |
| C# | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, etc. |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder/Decoder…) |
| Rust | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy | java.time.*, java.math.*, java.util (UUID, Date), java.io |
| Scala | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy)

In those languages, items in `constructorParameters` automatically become class properties. **Do not** also list them in `properties[]` — duplicates cause a "Sequence contains more than one matching element" error. TypeScript also auto-creates them; just don't duplicate.

### 7. Virtual types never generate files

`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` only define reusable type references. They produce no source files. Reference them by their `typeIdentifier`/`identifier` from properties or as base/interface types.

### 8. Interface method signatures go in `customCode`, not `properties`

For an interface that a class will implement, put method signatures in `customCode` (e.g. `findAll(): Promise<$user[]>;`) — not as function-typed properties. Otherwise the implementing class will duplicate them as fields alongside its real methods.

### 9. Use `$placeholders` for ALL internal type references in code strings

Raw type names in customCode strings (e.g. `private repo: IUserRepository`) won't resolve imports. Use `private repo: $repo` with a corresponding `templateRefs` entry. This is especially critical in C# (cross-namespace `using` directives only generate from templateRefs).

### 10. Don't reference a `typeIdentifier` that doesn't exist in the batch

Unresolved `typeIdentifier`s are silently dropped from properties. Always verify each one is defined in the same call.

---

## Output structure

- The engine writes `.ts` / `.cs` / `.py` / etc. files under `outputPath`, one file per file-generating spec entry (classes, interfaces, enums, customFiles).
- Subdirectories are created from each entry's `path`.
- Filenames follow language idioms: TypeScript kebab-case (`user-service.ts`), C# PascalCase (`UserService.cs`), Python snake_case (`user_service.py`), enums get suffixes per language (e.g. TypeScript `order-status.enum.ts`).
- TypeScript: the `I` prefix is stripped from interface names when exporting (`IUserRepository` → exported as `UserRepository`). Use `fileName` to avoid file-name collisions with the implementing class.
- C#: `I` prefix is preserved. Properties on classes generate `{ get; set; }`; properties on interfaces generate `{ get; }`. `isOptional` produces `string?`. `arrayTypes` generate `IEnumerable<T>` — for `List<T>`, use a free-form `type: "List<$user>"` with `templateRefs`.
- Python: customCode newlines need explicit 4-space indentation after `\n`.
- Go: requires `packageName` for multi-file projects; no constructors (use factory functions in `customCode`).
- Imports across files in the batch are resolved automatically; `customFiles` with an `identifier` can be imported by setting `customImports.path` to that identifier (resolves to the relative path).
- `dryRun: true` returns generated content in the response without writing.

---

## Pattern cookbook (TypeScript-leaning, applies broadly)

### Two interfaces with a cross-reference
```jsonc
{
  "language": "typescript",
  "interfaces": [
    { "name": "Address", "typeIdentifier": "address", "properties": [
      { "name": "street", "primitiveType": "String" },
      { "name": "city",   "primitiveType": "String" }
    ]},
    { "name": "User", "typeIdentifier": "user", "properties": [
      { "name": "id",      "primitiveType": "String" },
      { "name": "address", "typeIdentifier": "address" }
    ]}
  ]
}
```

### Class inheritance + method
```jsonc
{
  "classes": [
    { "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "properties": [{ "name": "id", "primitiveType": "String" }] },
    { "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{ "name": "email", "primitiveType": "String" }],
      "customCode": [
        { "code": "getDisplayName(): string { return this.email; }" }
      ]}
  ]
}
```

### Generic class + concrete subclass
```jsonc
{
  "classes": [
    { "name": "Repository", "typeIdentifier": "repo-generic",
      "genericArguments": [{
        "name": "T",
        "constraintTypeIdentifier": "base-entity",
        "propertyName": "items",
        "isArrayProperty": true
      }],
      "customCode": [
        { "code": "add(item: T): void { this.items.push(item); }" },
        { "code": "getAll(): T[] { return this.items; }" }
      ]},
    { "name": "User", "typeIdentifier": "user",
      "baseClassTypeIdentifier": "base-entity",
      "properties": [{ "name": "email", "primitiveType": "String" }] },
    { "name": "UserRepository", "typeIdentifier": "user-repo-class",
      "baseClassTypeIdentifier": "user-repo-concrete",
      "customCode": [{
        "code": "findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
        "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
      }]}
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{ "typeIdentifier": "user" }]
  }]
}
```

### Array + dictionary virtual types
```jsonc
{
  "arrayTypes": [
    { "typeIdentifier": "user-list",    "elementTypeIdentifier": "user" },
    { "typeIdentifier": "string-array", "elementPrimitiveType": "String" }
  ],
  "dictionaryTypes": [
    { "typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number" },
    { "typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
  ]
}
```

### Complex type expression in a property
```jsonc
{
  "name": "cache",
  "type": "Map<string, $resp>",
  "templateRefs": [{ "placeholder": "$resp", "typeIdentifier": "api-response" }]
}
```

### Enum + class consuming it
```jsonc
{
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [
      { "name": "Pending", "value": 0 },
      { "name": "Shipped", "value": 2 }
    ]
  }],
  "classes": [{
    "name": "Order", "typeIdentifier": "order",
    "properties": [{ "name": "status", "typeIdentifier": "order-status" }],
    "customCode": [{
      "code": "updateStatus(s: $status): void { this.status = s; }",
      "templateRefs": [{ "placeholder": "$status", "typeIdentifier": "order-status" }]
    }]
  }]
}
```

### Service with external DI (Angular flavor)
```jsonc
{
  "classes": [{
    "name": "ApiService", "typeIdentifier": "api-service",
    "decorators": [{ "code": "@Injectable({ providedIn: 'root' })" }],
    "customImports": [
      { "path": "@angular/core",         "types": ["Injectable", "inject"] },
      { "path": "@angular/common/http",  "types": ["HttpClient"] }
    ],
    "customCode": [
      { "code": "private http = inject(HttpClient);" },
      { "code": "getUsers(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
        "templateRefs": [{ "placeholder": "$list", "typeIdentifier": "user-array" }] }
    ]
  }],
  "arrayTypes": [{ "typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto" }]
}
```

### customFile (type aliases / barrel) + cross-file import
```jsonc
{
  "customFiles": [{
    "name": "types", "path": "shared", "identifier": "shared-types",
    "customCode": [
      { "code": "export type UserId = string;" },
      { "code": "export type Email = string;" }
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers",
    "customImports": [{ "path": "shared-types" }],
    "customCode": [{ "code": "static format(email: Email): string { return email.trim(); }" }]
  }]
}
```

### Interface with method signatures (TypeScript / C#)
```jsonc
{
  "interfaces": [{
    "name": "IUserRepository", "typeIdentifier": "user-repo",
    "fileName": "i-user-repository",
    "customCode": [
      { "code": "findAll(): Promise<$user[]>;",
        "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] },
      { "code": "findById(id: string): Promise<$user | null>;",
        "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
    ]
  }]
}
```

---

## Language-specific notes

### TypeScript
- Strips `I` prefix on interfaces when exporting. Set `fileName` on the interface (e.g. `"fileName": "i-user-repository"`) to avoid clashing with the implementing class file.
- Primitive mapping: `String→string`, `Number→number`, `Boolean→boolean`, `Date→Date`, `Any→unknown`.
- No imports needed for built-in types; only use `customImports` for `@angular/core`, `rxjs`, etc.
- Decorators supported directly (`@Injectable()`, `@IsEmail()`, etc.).
- customCode preserves indentation automatically across `\n`.

### C#
- `I` prefix preserved on interfaces.
- `Number` maps to `int` — for non-integer numbers use `"type": "decimal"` or `"type": "double"`.
- `packageName` controls namespace; omit for GlobalUsings setups.
- Class properties → `{ get; set; }`; interface properties → `{ get; }`.
- `isOptional` → nullable reference type (`string?`).
- `arrayTypes` → `IEnumerable<T>`. For `List<T>` use `"type": "List<$user>"` with `templateRefs`.
- Internal type references in customCode MUST use `templateRefs`, otherwise no `using` is generated and cross-namespace builds fail.

### Python
- Indent customCode bodies explicitly (4 spaces) after each `\n`. The engine doesn't auto-indent Python.
- typing imports auto-handled.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — write factory functions in `customCode`.
- `constructorParameters` auto-create struct fields; don't duplicate in `properties`.

### Java / Kotlin / Groovy / Scala / Swift / PHP / Rust
- Standard idiomatic identifier transformations are applied (e.g. Java enum members ALL_CAPS, Python methods snake_case). Don't fight the language; supply the source name normally and let the engine idiomatize.
- Auto-imported stdlib lists above. Use `customImports` only for third-party libs.

---

## Common mistake checklist (quick scan before calling)

1. Every `typeIdentifier` referenced is also defined in this same batch (no dangling refs).
2. No internal type names appear as raw strings in `customCode` — use `$placeholder` + `templateRefs`.
3. No framework/stdlib imports (`System.*`, `typing.*`, `java.util.*`, etc.) in `customImports`.
4. Methods and initialized fields live in `customCode`, never in `properties`.
5. Interface method signatures live in `customCode`, never as function-typed `properties`.
6. C#/Java/Go/Groovy: constructor parameters are not duplicated in `properties`.
7. Generic class consumers use `concreteGenericClasses` + `baseClassTypeIdentifier`/`interfaceTypeIdentifiers`, not raw `extends Foo<Bar>` strings.
8. C# `arrayTypes` produce `IEnumerable<T>` — switch to `"type": "List<$x>"` if you need `List`.
9. Reserved words (`delete`, `class`, `import`) are not used as property names — pick alternatives (`remove`, `clazz`, `importData`).
10. TypeScript: if an interface and its implementing class would share a base name, set `fileName` on the interface (`i-foo`).
11. Single `generate_code` call for the whole graph — never split related types across calls.

---

## How to use it (the gen session pattern)

1. Read the user's spec/requirements once.
2. Plan the type graph: every nominal type, every reference, every method that needs a body.
3. Build a single JSON object with `language`, `outputPath`, and the relevant top-level arrays (`classes`, `interfaces`, `enums`, `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`, `customFiles`).
4. Verify rules above (especially: every internal reference uses `typeIdentifier` or `templateRefs`; nothing stdlib-ish is in `customImports`; no method-as-property mistakes).
5. Call `mcp__metaengine__generate_code` ONCE with the full spec. If preview is desired, set `dryRun: true` first. If the spec is huge, write it to a JSON file and use `mcp__metaengine__load_spec_from_file`.
6. Do not attempt to fix issues by making more `generate_code` calls per file — fix the spec, then regenerate as one batch.
