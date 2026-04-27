# MetaEngine MCP — Knowledge Brief

MetaEngine is a **semantic code generation system** exposed via MCP. You describe types, relationships and methods as structured JSON; MetaEngine produces compilable, correctly-imported source files for **TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust**. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. **A single well-formed JSON call replaces dozens of error-prone file writes.**

---

## Tools exposed (MCP)

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__metaengine_initialize` | Returns the AI guide and resource links. Optional `language` arg returns language-specific patterns. Call once when starting. |
| `mcp__metaengine__generate_code` | **The main tool.** Generates source files from a structured JSON spec (classes, interfaces, enums, customFiles, arrayTypes, dictionaryTypes, concrete generics). |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code` but reads spec from a `.json` file path (`specFilePath`). Saves AI context. Optional overrides: `outputPath`, `skipExisting`, `dryRun`. |
| `mcp__metaengine__generate_openapi` | Generates a fully typed HTTP client from an OpenAPI spec (inline or URL). Frameworks: angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi, csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession. |
| `mcp__metaengine__generate_graphql` | Generates HTTP client from a GraphQL SDL schema. Frameworks: angular, react, typescript-fetch, go-nethttp, java-spring, csharp-httpclient, kotlin-ktor, python-fastapi, rust-reqwest, swift-urlsession. |
| `mcp__metaengine__generate_protobuf` | Generates HTTP client from `.proto` definitions. Frameworks: angular, react, typescript-fetch, go-nethttp, java-spring, csharp-httpclient, kotlin-ktor, python-httpx, rust-reqwest, swift-urlsession. |
| `mcp__metaengine__generate_sql` | Generates typed model classes from SQL DDL (`CREATE TABLE`). Languages: typescript, csharp, go, python, java, kotlin, groovy, scala, swift, php, rust. Options: `generateInterfaces`, `generateNavigationProperties`, `generateValidationAnnotations`, `initializeProperties`. |

Linked resources read during warmup:
- `metaengine://guide/ai-assistant` — Critical rules + patterns + language notes + common mistakes
- `metaengine://guide/examples` — Concrete input/output examples (TS/Python/Go/C#/Java/Kotlin/Groovy/Scala)

---

## generate_code — full input schema

Top-level (only `language` is required):

| Field | Type | Notes |
|-------|------|-------|
| `language` | enum (required) | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust` |
| `outputPath` | string | Output directory. Default `.` |
| `packageName` | string | Namespace/package/module. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. For C#: omit/empty for GlobalUsings (no namespace declaration). |
| `initialize` | bool | Whether to initialize properties with default values. Default `false`. |
| `skipExisting` | bool | Skip files that already exist. Default `true`. |
| `dryRun` | bool | Preview mode — returns code in response, writes nothing. Default `false`. |
| `classes` | array | Class definitions (regular and generic templates). |
| `interfaces` | array | Interface definitions (regular and generic templates). |
| `enums` | array | Enum definitions. |
| `customFiles` | array | File-without-class-wrapper (type aliases, barrels, utilities). |
| `arrayTypes` | array | Reusable array refs. NO file generated. |
| `dictionaryTypes` | array | Reusable dict/map refs. NO file generated. |
| `concreteGenericClasses` | array | Reusable inline `Repository<User>` refs. NO file generated. |
| `concreteGenericInterfaces` | array | Reusable inline `IRepository<User>` refs. NO file generated. |

### Class shape

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Class name. |
| `typeIdentifier` | string | **Unique key** used for cross-referencing. |
| `fileName` | string | Optional, override file name (without extension). |
| `path` | string | Subdirectory under `outputPath` (e.g. `services`, `models/auth`). |
| `comment` | string | Doc comment for the class. |
| `isAbstract` | bool | Abstract class flag. |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class (or of a `concreteGenericClasses` entry). |
| `interfaceTypeIdentifiers` | string[] | Interface ids to implement (also accepts `concreteGenericInterfaces` ids). |
| `genericArguments` | array | Makes this a generic template. Each: `{name, constraintTypeIdentifier?, propertyName?, isArrayProperty?}`. `propertyName` auto-creates a `T` (or `T[]` if `isArrayProperty:true`) property. |
| `constructorParameters` | array | `{name, type? \| primitiveType? \| typeIdentifier?}`. **In C#/Java/Go/Groovy these auto-become properties — DO NOT also list them in `properties[]`.** |
| `properties` | array | Field declarations only (see Property shape). |
| `customCode` | array | Methods, initialized fields, anything with logic. ONE per member. |
| `customImports` | array | External library imports only. `[{path, types?: string[]}]`. |
| `decorators` | array | `[{code, templateRefs?}]`. |

### Interface shape

Same fields as class except no `constructorParameters`/`isAbstract`/`baseClassTypeIdentifier`. Use `interfaceTypeIdentifiers` to extend other interfaces.

### Property shape

| Field | Notes |
|-------|-------|
| `name` | Field name. **Avoid reserved words** (`delete`, `class`, `import`) — use `remove`, `clazz`, `importData`. |
| `primitiveType` | One of `String`, `Number`, `Boolean`, `Date`, `Any`. |
| `typeIdentifier` | Reference to another type generated in the same call (or to an `arrayTypes`/`dictionaryTypes`/`concreteGeneric*` entry). |
| `type` | String literal type (e.g. `"List<$user>"`, `"Map<string, $resp>"`, `"decimal"`). For complex/external/composite types. |
| `templateRefs` | `[{placeholder, typeIdentifier}]` — resolves `$placeholder` inside `type` (and triggers imports). |
| `isOptional` | Generates nullable (`string?` in C#, `string | undefined` in TS, etc.). |
| `isInitializer` | Add default value initialization. |
| `comment` | Doc comment. |
| `commentTemplateRefs` | Template refs inside the comment. |
| `decorators` | `[{code, templateRefs?}]` (e.g. `@IsEmail()`, `@Required()`). |

### CustomCode shape

`{code: string, templateRefs?: [{placeholder, typeIdentifier}]}`. **One block = exactly one member.** Blocks get automatic newlines between them. Use `$placeholder` syntax to reference other generated types — without `templateRefs`, MetaEngine cannot generate the import directive.

### Enum shape

`{name, typeIdentifier, fileName?, path?, comment?, members: [{name, value: number}]}`.

### customFiles shape

`{name, path?, fileName?, identifier?, customCode: [...], customImports?: [...]}`. Use for type aliases, barrel exports, utility modules. Set `identifier` so other files can target it via `customImports: [{path: "<identifier>"}]` (auto-resolves to a relative path).

### arrayTypes shape

`{typeIdentifier, elementPrimitiveType? | elementTypeIdentifier?}`. **No file produced.** Reference via `typeIdentifier` in property fields.

### dictionaryTypes shape

`{typeIdentifier, keyPrimitiveType? | keyTypeIdentifier? | keyType?, valuePrimitiveType? | valueTypeIdentifier?}`. Supports all 4 primitive/custom combinations. **No file produced.**

### concreteGenericClasses / concreteGenericInterfaces shape

`{identifier, genericClassIdentifier, genericArguments: [{primitiveType? | typeIdentifier?}]}`. Creates a virtual `Repository<User>` reference. **No file produced.** Used as `baseClassTypeIdentifier`, `interfaceTypeIdentifiers`, or via templateRefs to embed `Repository<User>` inline.

### customImports shape

`{path: string, types?: string[]}`. Use ONLY for external libraries. `path` may also be a `customFiles.identifier` for cross-file refs within the batch.

---

## Critical rules (read these first — most failures violate one)

### 1. Generate ALL related types in ONE call
`typeIdentifier` resolves only within the current batch. If `UserService` references `User`, both must be in the same `generate_code` call. **Splitting per-domain breaks cross-file imports.**

### 2. Properties = type declarations. CustomCode = everything else.
- `properties[]` → fields with types, no initialization, no logic.
- `customCode[]` → methods, initialized fields (`private http = inject(HttpClient);`), anything with logic. **One block per member.**
- Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

### 3. Use `templateRefs` for internal types in `customCode` and complex `type` strings
`$placeholder` syntax + `templateRefs: [{placeholder, typeIdentifier}]` is what triggers automatic import resolution. Raw type names will compile-fail across namespaces (especially in C#).

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

### 4. Never add framework/std-lib imports to `customImports`
MetaEngine auto-imports the standard library per language:

| Language | Auto-imported (do NOT add) |
|----------|----------------------------|
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, +more |
| Swift | `Foundation` (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.) |
| Rust | `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, OutputStream) |
| Scala | `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | (no imports needed — built-in types) |

`customImports` is for `@angular/core`, `FluentValidation`, `rxjs`, `@nestjs/common`, etc.

### 5. `templateRefs` are ONLY for internal types
External-library types use `customImports`. Internal (same batch) types use `typeIdentifier` or `templateRefs`. Don't mix.

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Listing the same name in both `constructorParameters` and `properties` causes **"Sequence contains more than one matching element"**. Put shared fields only in `constructorParameters`; put extra (non-constructor) fields in `properties`.

### 7. Virtual types never produce files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` only create reusable references. They appear as types, not as files.

### 8. Interface method signatures go in `customCode`, not as function-typed properties
For interfaces a class will `implements`, declare method signatures via `customCode` (e.g. `"findAll(): Promise<$user[]>;"`). Function-typed properties cause the implementing class to duplicate them as fields.

---

## Pattern reference (cookbook)

### Cross-referenced interfaces
```jsonc
{
  "language": "typescript",
  "interfaces": [
    {"name":"Address","typeIdentifier":"address","properties":[
      {"name":"street","primitiveType":"String"},
      {"name":"city","primitiveType":"String"}]},
    {"name":"User","typeIdentifier":"user","properties":[
      {"name":"id","primitiveType":"String"},
      {"name":"address","typeIdentifier":"address"}]}
  ]
}
```

### Class inheritance + methods
```jsonc
{
  "classes":[
    {"name":"BaseEntity","typeIdentifier":"base-entity","isAbstract":true,
     "properties":[{"name":"id","primitiveType":"String"}]},
    {"name":"User","typeIdentifier":"user",
     "baseClassTypeIdentifier":"base-entity",
     "properties":[{"name":"email","primitiveType":"String"}],
     "customCode":[{"code":"getDisplayName(): string { return this.email; }"}]}
  ]
}
```

### Generic class + concrete instantiation
```jsonc
{
  "classes":[
    {"name":"Repository","typeIdentifier":"repo-generic",
     "genericArguments":[{"name":"T","constraintTypeIdentifier":"base-entity",
       "propertyName":"items","isArrayProperty":true}],
     "customCode":[
       {"code":"add(item: T): void { this.items.push(item); }"},
       {"code":"getAll(): T[] { return this.items; }"}]},
    {"name":"User","typeIdentifier":"user",
     "baseClassTypeIdentifier":"base-entity",
     "properties":[{"name":"email","primitiveType":"String"}]},
    {"name":"UserRepository","typeIdentifier":"user-repo-class",
     "baseClassTypeIdentifier":"user-repo-concrete",
     "customCode":[{"code":"findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
       "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}]}]}
  ],
  "concreteGenericClasses":[{
    "identifier":"user-repo-concrete",
    "genericClassIdentifier":"repo-generic",
    "genericArguments":[{"typeIdentifier":"user"}]}]
}
```

### Array & dictionary types
```jsonc
{
  "arrayTypes":[
    {"typeIdentifier":"user-list","elementTypeIdentifier":"user"},
    {"typeIdentifier":"string-array","elementPrimitiveType":"String"}],
  "dictionaryTypes":[
    {"typeIdentifier":"scores","keyPrimitiveType":"String","valuePrimitiveType":"Number"},
    {"typeIdentifier":"user-lookup","keyPrimitiveType":"String","valueTypeIdentifier":"user"},
    {"typeIdentifier":"user-names","keyTypeIdentifier":"user","valuePrimitiveType":"String"},
    {"typeIdentifier":"user-meta","keyTypeIdentifier":"user","valueTypeIdentifier":"metadata"}]
}
```
Then reference via `"typeIdentifier": "user-list"` in property fields.
**C# nuance**: `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with `templateRefs` instead.

### Complex `type` expressions
```jsonc
"properties":[{
  "name":"cache",
  "type":"Map<string, $resp>",
  "templateRefs":[{"placeholder":"$resp","typeIdentifier":"api-response"}]
}]
```
`templateRefs` work in `properties.type`, `customCode.code`, and `decorators.code`.

### Enum + class using it
```jsonc
{
  "enums":[{"name":"OrderStatus","typeIdentifier":"order-status",
    "members":[{"name":"Pending","value":0},{"name":"Shipped","value":2}]}],
  "classes":[{"name":"Order","typeIdentifier":"order",
    "properties":[{"name":"status","typeIdentifier":"order-status"}],
    "customCode":[{"code":"updateStatus(s: $status): void { this.status = s; }",
      "templateRefs":[{"placeholder":"$status","typeIdentifier":"order-status"}]}]}]
}
```
Enum filenames auto-suffixed: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### Service with external DI (Angular/NestJS-style)
```jsonc
{
  "classes":[{
    "name":"PetService","typeIdentifier":"pet-service","path":"services",
    "decorators":[{"code":"@Injectable({ providedIn: 'root' })"}],
    "customImports":[
      {"path":"@angular/core","types":["Injectable","inject"]},
      {"path":"@angular/common/http","types":["HttpClient"]},
      {"path":"rxjs","types":["Observable"]}],
    "customCode":[
      {"code":"private http = inject(HttpClient);"},
      {"code":"private baseUrl = '/api/pets';"},
      {"code":"getAll(): Observable<$petArray> { return this.http.get<$petArray>(this.baseUrl); }",
       "templateRefs":[{"placeholder":"$petArray","typeIdentifier":"pet-array"}]},
      {"code":"getById(id: string): Observable<$pet> { return this.http.get<$pet>(`${this.baseUrl}/${id}`); }",
       "templateRefs":[{"placeholder":"$pet","typeIdentifier":"pet"}]}]
  }],
  "arrayTypes":[{"typeIdentifier":"pet-array","elementTypeIdentifier":"pet"}]
}
```

### Type aliases / barrel via customFiles
```jsonc
{
  "customFiles":[{
    "name":"types","path":"utils","identifier":"shared-types",
    "customCode":[
      {"code":"export type UserId = string;"},
      {"code":"export type Status = 'active' | 'inactive' | 'pending';"},
      {"code":"export type ResultSet<T> = { data: T[]; total: number; page: number; };"}]
  }],
  "classes":[{
    "name":"UserService","path":"services",
    "customImports":[{"path":"shared-types","types":["UserId","Status","ResultSet"]}],
    "customCode":[
      {"code":"async getUser(id: UserId): Promise<User> { return null as any; }"},
      {"code":"updateStatus(id: UserId, status: Status): void { }"}]
  }]
}
```

### Interface signatures (so a class can implement it)
```jsonc
{
  "interfaces":[{
    "name":"IUserRepository","typeIdentifier":"user-repo",
    "fileName":"i-user-repository",
    "customCode":[
      {"code":"findAll(): Promise<$user[]>;",
       "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}]},
      {"code":"findById(id: string): Promise<$user | null>;",
       "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}]}]
  }]
}
```

### Constructor parameter pattern (TypeScript shorthand)
```jsonc
{
  "language":"typescript",
  "enums":[{"name":"Status","typeIdentifier":"status",
    "members":[{"name":"Active","value":1}]}],
  "classes":[{
    "name":"User","typeIdentifier":"user",
    "constructorParameters":[
      {"name":"email","type":"string"},
      {"name":"status","typeIdentifier":"status"}],
    "properties":[
      {"name":"createdAt","primitiveType":"Date"}    // ✅ Only ADDITIONAL fields
    ]
  }]
}
```
Output (TS): constructor params become public class fields (`constructor(public email: string, public status: Status) {}`); `createdAt` becomes a regular field. **Never list `email`/`status` in `properties` again.**

---

## Language-specific notes

### TypeScript
- `I` prefix is **stripped** from interface names. `IUserRepository` → exported as `UserRepository`. Use `fileName` to control file name on collisions (e.g. `"fileName":"i-user-repository"`).
- Primitive mapping: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`, `Any` → `unknown`.
- Auto-indent for customCode newlines (`\n`).
- Decorators supported directly.
- No imports needed for built-in types.

### C#
- `I` prefix **preserved** on interface names.
- Primitive mapping: `Number` → `int` (NOT `double`). Use `"type":"decimal"` or `"type":"double"` for non-integer numbers explicitly.
- `packageName` sets the namespace. **Omit/empty** for GlobalUsings pattern (no `namespace` block).
- Interface properties generate `{ get; }`; class properties generate `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type":"List<$user>"` with templateRefs.
- `isOptional: true` on properties generates `string?` (nullable reference type).
- **Every internal type in customCode MUST use `templateRefs`** — without it, cross-namespace `using` directives won't be generated and code will fail to compile.
- Constructor parameters auto-become properties — don't duplicate.

### Python
- Must provide explicit indentation (4 spaces) after `\n` in customCode (not auto-indented).
- typing/pydantic/datetime/decimal/enum/abc/dataclasses imports are automatic.

### Go
- `packageName` required for multi-file projects.
- No constructors — use factory functions in customCode.
- Constructor parameters (if any) auto-become struct fields — don't duplicate.

### Java / Kotlin / Groovy / Scala
- `packageName` defaults to `com.metaengine.generated` if omitted.
- Constructor parameters auto-become properties (Java/Groovy). Don't duplicate.

### Swift / Rust / PHP
- See auto-import table above. Rust uses `chrono`, `uuid`, `rust_decimal`, `serde`. PHP uses standard library types.

---

## Output structure

- For each non-virtual type in the spec, MetaEngine writes one source file under `outputPath/<class.path>/`. Filenames follow language conventions (`user-service.ts`, `UserService.cs`, `user_service.py`, `user_service.go`, etc.).
- File names default to a kebab/Pascal/snake conversion of `name`; override via `fileName`.
- Imports/usings are generated automatically based on cross-references discovered through `typeIdentifier`/`templateRefs` AND any `customImports` you provided.
- When `dryRun: true`, the tool returns the would-be file contents in the response payload (no disk writes).
- When `skipExisting: true` (default), already-existing files are not overwritten — useful for the **stub pattern** (regenerate models, leave hand-edited services alone).

---

## Common mistakes (10 must-avoid)

1. **Don't** reference a `typeIdentifier` that's not in the same batch → property silently dropped. **Do** verify every `typeIdentifier` matches a defined type in the same call.
2. **Don't** declare interface methods as function-typed properties when a class will implement the interface — implementing class duplicates them as fields. **Do** put method signatures in `customCode` (e.g. `"findAll(): Promise<$user[]>;"`).
3. **Don't** write internal type names as raw strings in `customCode` (e.g. `"private repo: IUserRepository"`). **Do** use `templateRefs` (`"private repo: $repo"` + `templateRefs: [{placeholder:"$repo",typeIdentifier:"user-repo"}]`).
4. **Don't** use `arrayTypes` in C# when you need `List<T>` — `arrayTypes` produce `IEnumerable<T>`. **Do** use `"type":"List<$user>"` with templateRefs.
5. **Don't** add `System.*`, `typing.*`, `java.util.*`, etc. to `customImports`. **Do** let MetaEngine auto-import the standard library.
6. **Don't** duplicate constructor parameter names in `properties` (C#/Java/Go/Groovy) — causes "Sequence contains more than one matching element". **Do** put shared fields only in `constructorParameters`; only additional fields go in `properties`.
7. **Don't** use reserved words (`delete`, `class`, `import`) as property names. **Do** use safe alternatives (`remove`, `clazz`, `importData`).
8. **Don't** generate related types in separate MCP calls. **Do** batch everything in ONE call — cross-file imports only resolve within a single batch.
9. **Don't** expect `Number` to map to `double` in C# — it maps to `int`. **Do** use `"type":"double"` or `"type":"decimal"` when needed.
10. **Don't** forget `fileName` when both an `I`-prefixed interface and its implementing class would collide in TypeScript. **Do** set `"fileName":"i-user-repository"` on the interface.

---

## Workflow (analysis-first)

1. **Identify the problem across ALL affected files.** Don't edit file-by-file.
2. **Understand the root cause.** Map every required type into a single mental graph.
3. **Prove it (TDD)** when fixing bugs.
4. **Batch-generate.** One `generate_code` call per coherent typegraph. Splitting per-domain breaks cross-file imports.
5. **Use `dryRun: true`** to preview the spec output before writing files.
6. **Use `skipExisting: true`** (default) for the stub pattern when you want to regenerate models without clobbering hand-written code.
7. **Spec-from-file** (`load_spec_from_file`) is preferred for large multi-file generations — keeps AI context clean and the spec version-controllable.

---

## Quick decision tree

| Need | Use |
|------|-----|
| Field with a known type, no logic | `properties[]` |
| Method, initialized field, anything with logic | `customCode[]` |
| Reference an internal type inside a method/initializer/decorator | `$placeholder` + `templateRefs` |
| Reference an external library type | `customImports` (no templateRefs) |
| `T[]` of a generated type | `arrayTypes` (or `"type":"List<$x>"` for C# mutable list) |
| `Map<K,V>` / `Record<K,V>` / `Dictionary<K,V>` | `dictionaryTypes` |
| `Repository<User>` as base class / interface / property type | `concreteGenericClasses` / `concreteGenericInterfaces` |
| Type alias / barrel / utility module | `customFiles` (set `identifier` for cross-file refs) |
| Nullable reference | `isOptional: true` (or include `?` in `type` string) |
| Avoid Number → int trap in C# | `"type":"decimal"` or `"type":"double"` |
| Generate from a schema | `generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` |
| Avoid context bloat for large specs | `load_spec_from_file` |

---

**Bottom line:** every related type goes in ONE call. Properties declare types; customCode does logic. Internal refs use `typeIdentifier`/`templateRefs`; external refs use `customImports`. Don't duplicate constructor parameters into properties. Don't add stdlib imports.
