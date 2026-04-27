# MetaEngine MCP — Knowledge Brief (TypeScript-focused)

MetaEngine is a *semantic* code generator. You describe types, relationships, and code as structured JSON; the engine produces compilable source files with correct cross-file imports, language-idiomatic identifiers, and resolved generics. Unlike templating, references resolve **across the batch** so a single call replaces dozens of error-prone file writes.

---

## Tools exposed (all under `mcp__metaengine__`)

- **`metaengine_initialize`** — returns this guide. Optional arg `language`. Pure documentation; no side effects.
- **`generate_code`** — the main tool. Takes a JSON spec (classes, interfaces, enums, etc.) and writes source files. Required: `language`. See full schema below.
- **`load_spec_from_file`** — same as `generate_code` but reads the spec from a `.json` file. Required: `specFilePath`. Optional overrides: `outputPath`, `skipExisting`, `dryRun`. Use this for large specs to avoid context bloat.
- **`generate_openapi`** — generates HTTP clients from an OpenAPI spec (inline `openApiSpec` or `openApiSpecUrl`). Frameworks: `angular | react | typescript-fetch | go-nethttp | java-spring | python-fastapi | csharp-httpclient | kotlin-ktor | rust-reqwest | swift-urlsession`.
- **`generate_graphql`** — HTTP client from a GraphQL SDL schema (`graphQLSchema`). Same framework set (minus `python-fastapi` → `python-fastapi`).
- **`generate_protobuf`** — HTTP client from `.proto` source (`protoSource`). Note: Python option here is `python-httpx` (not fastapi).
- **`generate_sql`** — typed model classes from SQL DDL (CREATE TABLE statements). Supports `typescript | csharp | go | python | java | kotlin | groovy | scala | swift | php | rust`.

For this benchmark we are concerned almost exclusively with **`generate_code`** in **TypeScript** mode.

---

## THE Cardinal Rule

**ONE call with ALL related types.** `typeIdentifier` references only resolve within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks the typegraph and imports won't resolve. Don't iterate file-by-file — analyze the whole spec, define every type, and emit them in a single call.

---

## Other Critical Rules

### Properties = type declarations. CustomCode = everything else.
- `properties[]` declares fields with types only (no initialization, no logic).
- `customCode[]` handles methods, initialized fields, anything with logic. **One `customCode` item = exactly one member.**
- Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

```jsonc
"properties": [{ "name": "id", "primitiveType": "String" }]
"customCode": [
  { "code": "private http = inject(HttpClient);" },
  { "code": "getAll(): T[] { return this.items; }" }
]
```

### templateRefs are how internal types are referenced inside `customCode`/`type`/decorators
When a code string references another type from the same batch, use `$placeholder` syntax + `templateRefs`. This is what triggers automatic import resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
}]
```

Without `templateRefs`, MetaEngine cannot generate the import. Raw type names like `User` written inline will compile-fail across files.

### templateRefs are ONLY for internal types
- Same batch → `typeIdentifier` (in properties) or `templateRefs` (in code/strings).
- External library → `customImports`.
- Never mix these.

### Never add framework imports to `customImports`
The engine auto-imports the standard library for the target language. Adding them manually duplicates or errors. For **TypeScript** specifically: no built-in imports are needed — primitives are global. Only specify `customImports` for true third-party packages (e.g. `@angular/core`, `rxjs`, `zod`).

Auto-imported per language (illustrative, NOT an exhaustive list):
| Language | Auto-imported (do NOT include) |
|---|---|
| C# | `System.*`, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python | `typing.*`, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | `java.util.*`, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, etc. |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder/Decoder…) |
| Rust | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy | java.time.*, java.math.*, java.util (UUID, Date), java.io |
| Scala | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |
| TypeScript | (none needed) |

### Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Don't duplicate them in `properties[]` — that produces "Sequence contains more than one matching element" errors. **TypeScript also treats constructor params as fields if marked**, but in TS you typically use `properties[]` + a custom constructor in `customCode`. For TS, prefer `properties[]` and don't duplicate via `constructorParameters`.

### Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are **reusable type references only** — no files are emitted. They're used by referencing their `typeIdentifier` in properties, customCode templateRefs, or `baseClassTypeIdentifier`.

### Interface method signatures
For interfaces a class will `implements`, define method signatures inside `customCode` of the interface — NOT as function-typed properties. Function-typed properties create duplicate fields when the implementing class adds matching `customCode` methods.

```jsonc
"customCode": [
  { "code": "findAll(): Promise<$user[]>;",
    "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
]
```

### Reserved words / collisions
- Don't use TS reserved words (`delete`, `class`, `import`) as property names → use `remove`, `clazz`, `importData`.
- TypeScript strips `I` prefix from interface names: `IUserRepository` exports as `UserRepository`. If an `I*` interface and its implementing class would collide, set `"fileName": "i-user-repository"` on the interface.

---

## `generate_code` — full input schema

Top-level required field: **`language`** (`typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php | rust`).

Top-level optional fields:
- `packageName` — package/module/namespace name. For TS this is unused; for Java/Kotlin/Groovy default `com.metaengine.generated`; for Go default `github.com/metaengine/demo`. For C#: when omitted/empty, no namespace is emitted (good for GlobalUsings).
- `outputPath` — directory to write files into (default `.`).
- `skipExisting` — default `true`. If a file already exists, skip writing it.
- `dryRun` — default `false`. When `true`, files are NOT written; generated content is returned in the response for review.
- `initialize` — default `false`. If `true`, properties are initialized with default values.
- `classes[]`
- `interfaces[]`
- `enums[]`
- `arrayTypes[]`
- `dictionaryTypes[]`
- `concreteGenericClasses[]`
- `concreteGenericInterfaces[]`
- `customFiles[]`

### `classes[]` item

```
{
  "name": string,                          // class name
  "typeIdentifier": string,                // unique handle for cross-references
  "fileName": string?,                     // override file name (no extension)
  "path": string?,                         // directory path, e.g. "models" or "services/auth"
  "comment": string?,                      // class-level doc comment

  "isAbstract": boolean?,
  "baseClassTypeIdentifier": string?,      // refers to another class typeIdentifier OR a concreteGenericClasses identifier
  "interfaceTypeIdentifiers": string[]?,   // refers to interface typeIdentifiers (regular OR concreteGenericInterfaces ids)

  "genericArguments": [{                   // makes this a generic CLASS TEMPLATE (e.g. Repository<T>)
    "name": "T",                           // generic param name
    "constraintTypeIdentifier": string?,   // e.g. "where T : BaseEntity"
    "propertyName": string?,               // creates a property of type T with this name
    "isArrayProperty": boolean?            // if true, the property is T[]
  }],

  "constructorParameters": [{              // For C#/Java/Go/Groovy these auto-become properties.
    "name": string,
    "primitiveType": "String|Number|Boolean|Date|Any"?,
    "type": string?,                       // raw type string for complex/external types
    "typeIdentifier": string?              // refers to another type in the batch
  }],

  "properties": [{
    "name": string,
    "primitiveType": "String|Number|Boolean|Date|Any"?,
    "type": string?,                       // raw type expression for complex/external types
    "typeIdentifier": string?,             // refers to another type in the batch
    "templateRefs": [{ "placeholder": "$x", "typeIdentifier": string }]?, // when "type" uses placeholders
    "isOptional": boolean?,                // generates string?/T | undefined as appropriate
    "isInitializer": boolean?,             // emit default-value initialization
    "decorators": [{                       // e.g. @IsEmail()
      "code": string,
      "templateRefs": [{...}]?
    }],
    "comment": string?,
    "commentTemplateRefs": [{...}]?
  }],

  "customCode": [{                         // ONE entry per member (method, initialized field, ctor body, etc.)
    "code": string,                        // EXACTLY one member's source code
    "templateRefs": [{ "placeholder": "$x", "typeIdentifier": string }]?
  }],

  "decorators": [{                         // class-level decorators (e.g. @Injectable())
    "code": string,
    "templateRefs": [{...}]?
  }],

  "customImports": [{                      // ONLY external libraries / customFile identifiers
    "path": "@angular/core",               // package path OR a customFile identifier
    "types": ["Injectable", "inject"]      // named imports
  }]
}
```

### `interfaces[]` item

Same shape as classes, minus `isAbstract`/`constructorParameters`. Supports `genericArguments`, `interfaceTypeIdentifiers` (extends), `properties`, `customCode` (for method signatures), `decorators`, `customImports`, `path`, `fileName`, `comment`, `typeIdentifier`, `name`.

### `enums[]` item

```
{
  "name": string,
  "typeIdentifier": string,
  "fileName": string?,
  "path": string?,
  "comment": string?,
  "members": [{ "name": string, "value": number }]
}
```

TypeScript: enum file gets suffix `.enum.ts` (e.g. `order-status.enum.ts`).

### `arrayTypes[]` item — virtual, no file produced

```
{
  "typeIdentifier": string,                // referenced from properties as typeIdentifier: ...
  "elementPrimitiveType": "String|Number|Boolean|Date|Any"?, // for primitive arrays
  "elementTypeIdentifier": string?         // for arrays of custom types
}
```

In **C#**, arrayTypes generate `IEnumerable<T>`. If you need `List<T>` use a raw `"type": "List<$user>"` with templateRefs instead. In **TypeScript**, arrayTypes produce `T[]`.

### `dictionaryTypes[]` item — virtual, no file produced

```
{
  "typeIdentifier": string,
  "keyPrimitiveType": "String|Number|Boolean|Date|Any"?,
  "keyType": string?,                      // raw type literal e.g. "string"
  "keyTypeIdentifier": string?,            // custom key type
  "valuePrimitiveType": "String|Number|Boolean|Date|Any"?,
  "valueTypeIdentifier": string?
}
```

All 4 combinations of primitive/custom for key/value are supported.

### `concreteGenericClasses[]` item — virtual, no file produced

Creates an inline reference to a concrete generic, e.g. `Repository<User>`, that other classes can `extends` via `baseClassTypeIdentifier`.

```
{
  "identifier": string,                            // handle for this concrete impl
  "genericClassIdentifier": string,                // refers to the open generic class
  "genericArguments": [
    { "primitiveType": "..."? , "typeIdentifier": "..."? }
  ]
}
```

### `concreteGenericInterfaces[]` item — virtual, no file produced

Same shape as `concreteGenericClasses` but for interfaces — gives you a referencable `IRepository<User>`.

### `customFiles[]` item — generates files WITHOUT class wrapper

Use for type aliases, barrel exports, free functions, constants.

```
{
  "name": string,                                  // file name (no extension)
  "fileName": string?,
  "path": string?,
  "identifier": string?,                           // makes this customFile importable from elsewhere via customImports.path: "<identifier>"
  "customCode": [{ "code": string, "templateRefs": [...]? }],
  "customImports": [{ "path": string, "types": string[]? }]
}
```

---

## How references work end-to-end

1. Define each generated type with a unique `typeIdentifier`.
2. Reference it from another property by setting `typeIdentifier`.
3. Reference it inside a `code` string (customCode / type expressions / decorators) by writing `$placeholder` and supplying `templateRefs: [{ placeholder: "$placeholder", typeIdentifier: "..." }]`.
4. The engine resolves the placeholder to the real type name at generation time and adds the appropriate import statement to that file.

External/library types skip steps 1–3 entirely: list them in `customImports` and use them by their real name.

---

## TypeScript specifics (for this benchmark)

- Primitive mapping: `String → string`, `Number → number`, `Boolean → boolean`, `Date → Date`, `Any → unknown`.
- `arrayTypes` → `T[]`.
- `dictionaryTypes` → `Record<K, V>` / `{ [key: K]: V }` shape (engine handles it).
- Interfaces: `I` prefix is stripped from the exported name. Set `fileName` on the interface if it would collide with a class file name.
- Decorators are emitted directly above the class/property.
- `customCode` newlines are auto-indented for the surrounding scope.
- No `customImports` needed for TS built-in types.
- `isOptional: true` on a property generates `name?: T` (which TS treats as `T | undefined`).
- For methods returning a domain type, write the body in one `customCode` entry and reference the type via `$placeholder` + `templateRefs`.

---

## Output structure

For every concrete (non-virtual) type, the engine writes one source file at `<outputPath>/<path>/<filename>.<ext>`. Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) emit zero files but contribute to the type graph.

Files include:
- correct extension for the target language (`.ts`, `.cs`, `.py`, `.go`, …)
- exact named imports for every internal cross-reference
- `customImports` rendered into `import` / `using` / `package` directives
- decorators / annotations
- class/interface/enum body, members in declaration order

Default behavior:
- `skipExisting: true` — never overwrites; remove or set to `false` to regenerate.
- `dryRun: false` — actually writes to disk. Set to `true` to inspect generated content without writing.
- `outputPath: "."` — relative to current working directory; pass an absolute path when needed.

---

## Common mistakes to avoid

1. Splitting one logical schema across multiple `generate_code` calls. Cross-file imports do not resolve across calls — types referenced from outside the batch silently drop.
2. Writing internal type names as raw strings inside a `customCode` body (e.g. `"private repo: IUserRepository"`) without `templateRefs`. Imports won't be generated.
3. Putting methods or initialized fields in `properties[]`. Use `customCode`. Putting bare type declarations in `customCode`. Use `properties`.
4. Adding standard-library imports (e.g. `typing`, `System.*`, TS primitives) to `customImports`. The engine handles these automatically.
5. In C#/Java/Go/Groovy: duplicating constructor params in `properties[]`. Pick `constructorParameters` for shared fields; put non-constructor-only fields in `properties`.
6. Using function-typed properties for interface method signatures. Use `customCode` so implementing classes don't get duplicate property declarations.
7. Referencing a `typeIdentifier` that doesn't exist in the same batch — the property is silently dropped.
8. Using TS reserved words (`delete`, `class`, `import`) as identifiers.
9. In C# expecting `Number` to map to `double` — it maps to `int`. Use `"type": "decimal"` or `"type": "double"` explicitly.
10. Forgetting `fileName` on a TS `I*` interface that collides with its implementing class file.

---

## Putting it all together — TypeScript example

```jsonc
{
  "language": "typescript",
  "outputPath": "src",

  "enums": [
    { "name": "OrderStatus", "typeIdentifier": "order-status",
      "members": [
        { "name": "Pending", "value": 0 },
        { "name": "Shipped", "value": 1 }
      ]}
  ],

  "interfaces": [
    { "name": "Address", "typeIdentifier": "address",
      "properties": [
        { "name": "street", "primitiveType": "String" },
        { "name": "city",   "primitiveType": "String" }
      ]},

    { "name": "IUserRepository", "typeIdentifier": "user-repo",
      "fileName": "i-user-repository",
      "customCode": [
        { "code": "findById(id: string): Promise<$user | null>;",
          "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
      ]}
  ],

  "classes": [
    { "name": "User", "typeIdentifier": "user",
      "properties": [
        { "name": "id",      "primitiveType": "String" },
        { "name": "email",   "primitiveType": "String" },
        { "name": "address", "typeIdentifier": "address" },
        { "name": "status",  "typeIdentifier": "order-status" }
      ],
      "customCode": [
        { "code": "displayName(): string { return this.email; }" }
      ]},

    { "name": "UserService", "typeIdentifier": "user-service",
      "properties": [
        { "name": "repo", "type": "$repo",
          "templateRefs": [{ "placeholder": "$repo", "typeIdentifier": "user-repo" }] }
      ],
      "customCode": [
        { "code": "constructor(repo: $repo) { this.repo = repo; }",
          "templateRefs": [{ "placeholder": "$repo", "typeIdentifier": "user-repo" }] },
        { "code": "async getUser(id: string): Promise<$user | null> { return this.repo.findById(id); }",
          "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
      ]}
  ],

  "arrayTypes": [
    { "typeIdentifier": "user-list", "elementTypeIdentifier": "user" }
  ]
}
```

That single call generates: `address.ts`, `i-user-repository.ts`, `order-status.enum.ts`, `user.ts`, `user-service.ts`. Imports are wired automatically across all five files.

---

## Workflow recommended for this benchmark

1. Read the task spec end-to-end. Build the entire type graph in your head before writing any JSON.
2. Assign a unique `typeIdentifier` to every generated type up front.
3. Decide what's a `class`, what's an `interface`, what's an `enum`, what's a `customFile` (for type aliases / barrels).
4. List `arrayTypes` / `dictionaryTypes` for any reusable collection shape; reference them via `typeIdentifier`.
5. For every method or initialized field, write ONE `customCode` entry. Use `$placeholder` + `templateRefs` for any internal type reference inside the code. Use plain identifiers for external/library types and add the imports to `customImports`.
6. Make exactly **ONE `generate_code` call** with the whole spec, `language: "typescript"`, and the desired `outputPath`.
7. If the spec is large, consider writing it to a `.json` file and using `load_spec_from_file` to keep context lean.
8. Use `dryRun: true` if you want to inspect output without writing; otherwise the default `dryRun: false` writes files directly.

That's everything you need. Build the graph, place all types in one batch, mark all internal references with `templateRefs` or `typeIdentifier`, leave standard-library imports alone, and the engine handles the rest.
