# MetaEngine MCP — Knowledge Brief

MetaEngine is a semantic code generation system exposed via MCP. You describe types,
relationships, and methods as structured JSON. MetaEngine produces compilable,
correctly-imported source files. Unlike templates, it resolves cross-references,
manages imports, and handles language idioms automatically. **A single well-formed
JSON call replaces dozens of error-prone file writes.**

---

## Tools Exposed

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns the canonical guide (this brief is built from it). Optional `language` param: typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php. |
| `mcp__metaengine__generate_code` | Primary tool. Generates classes/interfaces/enums/customFiles/array+dict types from a structured spec. Targets: typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php, **rust**. |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code` but loads the spec JSON from disk (specFilePath). Lets you reuse spec files & avoid context bloat. Overrides: outputPath, skipExisting, dryRun. |
| `mcp__metaengine__generate_openapi` | Generates HTTP clients from an OpenAPI spec (inline string `openApiSpec` or `openApiSpecUrl`). Frameworks: angular, react, typescript-fetch, go-nethttp, java-spring, python-fastapi, csharp-httpclient, kotlin-ktor, rust-reqwest, swift-urlsession. |
| `mcp__metaengine__generate_graphql` | HTTP client from a GraphQL SDL (`graphQLSchema`). Same framework set (python is python-fastapi, no rust feature flags special). |
| `mcp__metaengine__generate_protobuf` | HTTP client from `.proto` content (`protoSource`). Frameworks identical except python is **python-httpx** (not fastapi). |
| `mcp__metaengine__generate_sql` | Typed model classes from `ddlSource` (CREATE TABLE statements). Languages: typescript, csharp, go, python, java, kotlin, groovy, scala, swift, php, rust. Options for nav properties, validation annotations, interfaces. |

---

## generate_code — Full Input Schema

Top-level fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **YES** | typescript / python / go / csharp / java / kotlin / groovy / scala / swift / php / rust |
| `outputPath` | string | no | Defaults to `.`. Directory where files are written. |
| `packageName` | string | no | Sets namespace/module. Defaults: Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C#: omit/empty → no namespace declaration (good for GlobalUsings). |
| `dryRun` | bool | no (default false) | Returns generated code in response without writing files. |
| `skipExisting` | bool | no (default true) | Skip existing files (stub pattern). |
| `initialize` | bool | no (default false) | Initialize properties with default values. |
| `classes` | array | no | Class definitions (regular + generic templates). |
| `interfaces` | array | no | Interface definitions (regular + generic templates). |
| `enums` | array | no | Enum definitions. |
| `customFiles` | array | no | Files WITHOUT a class wrapper — type aliases, utility functions, barrel exports. |
| `arrayTypes` | array | no | Virtual reusable array type refs (no files). |
| `dictionaryTypes` | array | no | Virtual reusable dictionary refs (no files). |
| `concreteGenericClasses` | array | no | Concrete `Repository<User>` refs (no files). |
| `concreteGenericInterfaces` | array | no | Concrete `IRepository<User>` refs (no files). |

### Class definition fields

```
name                        string
typeIdentifier              string  unique id used for cross-references
path                        string  directory subpath (e.g. "models", "services/auth")
fileName                    string  custom file name w/o extension
comment                     string  doc comment
isAbstract                  bool
baseClassTypeIdentifier     string  references another class OR a concreteGenericClass identifier
interfaceTypeIdentifiers    string[]  references interfaces or concreteGenericInterfaces
genericArguments            array   makes class a generic template
constructorParameters       array   {name, type|primitiveType|typeIdentifier}
properties                  array   field declarations (type-only)
customCode                  array   one entry per method/initialized field
customImports               array   {path, types[]} — external libs only
decorators                  array   {code, templateRefs[]}
```

### Property fields

```
name              string
primitiveType     enum: String|Number|Boolean|Date|Any
type              string  raw type literal (use for complex/external types)
typeIdentifier    string  reference to another generated type
templateRefs      array   {placeholder, typeIdentifier} for $-substitution in `type`
isOptional        bool
isInitializer     bool    add default value
comment           string
commentTemplateRefs array
decorators        array
```

### CustomCode entry

```
code           string         exactly one member's source (method/initialized field/decorator)
templateRefs   array          {placeholder, typeIdentifier} — use for any internal type reference
```

### Generic argument fields

```
name                       string  e.g. "T", "K"
constraintTypeIdentifier   string  emits e.g. `where T : BaseEntity`
propertyName               string  auto-creates a property of type T with this name
isArrayProperty            bool    if true, property is T[]
```

### Enum entry

```
name, typeIdentifier, fileName, path, comment
members: [{name, value}]
```

### Interface entry

Same shape as class, plus `interfaceTypeIdentifiers` to extend other interfaces.
Interface methods go in `customCode` as **signatures** (no body), e.g.
`"findAll(): Promise<$user[]>;"` — NOT as function-typed properties.

### CustomFile entry (no class wrapper)

```
name                 string
path                 string
identifier           string  optional, lets other files import this via customImports.path = identifier
fileName             string  override
customCode           array   one entry per export/alias/function
customImports        array
```

### Virtual type refs (NO files generated)

```
arrayTypes:               {typeIdentifier, elementPrimitiveType|elementTypeIdentifier}
dictionaryTypes:          {typeIdentifier, keyPrimitiveType|keyType|keyTypeIdentifier,
                                          valuePrimitiveType|valueTypeIdentifier}
concreteGenericClasses:   {identifier, genericClassIdentifier, genericArguments[]}
concreteGenericInterfaces:{identifier, genericClassIdentifier, genericArguments[]}
```

Reference these by their `typeIdentifier`/`identifier` in properties or via
`baseClassTypeIdentifier` / `interfaceTypeIdentifiers`.

---

## CRITICAL RULES — Most Common Failure Sources

### 1. Generate ALL related types in ONE call
`typeIdentifier` references resolve **only within the current batch**. Splitting per-domain
breaks the typegraph: cross-file imports won't be generated. If `UserService` references
`User`, both must be in the same `generate_code` call.

### 2. properties = type declarations. customCode = everything else.
- `properties[]` = fields with types only, no init.
- `customCode[]` = methods, initialized fields, anything with logic. **One entry = one member.**
- Never put methods in properties. Never put uninitialized type declarations in customCode.

### 3. Use templateRefs for internal type references in customCode
When customCode (or a complex `type` string in a property) names a type from the same batch,
use `$placeholder` and supply `templateRefs`. This is what triggers automatic import generation.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

**Critical in C#**: every internal type reference in customCode MUST use templateRefs, or
`using` directives for cross-namespace types won't be generated. Raw strings like
`IUserRepository` will compile-fail across namespaces.

### 4. Never add framework imports to customImports
MetaEngine auto-imports standard library types. Adding them manually causes duplication or
errors. The full auto-import list:

| Language   | Auto-imported (never specify) |
|------------|---|
| C#         | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python     | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java       | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin     | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go         | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more |
| Swift      | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, etc.) |
| Rust       | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy     | java.time.*, java.math.*, java.util (UUID, Date), java.io (File, InputStream, OutputStream) |
| Scala      | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP        | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |
| TypeScript | (no imports needed — built-in types) |

`customImports` is **only** for external libraries (`@angular/core`, `FluentValidation`,
`rxjs`, etc.).

### 5. templateRefs vs customImports
- Same batch (internal) → `typeIdentifier` (in properties) or `templateRefs` (in customCode).
- External library → `customImports`.
- **Never mix.** Don't templateRef an external lib type; don't customImport a generated type.

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Don't duplicate. In these languages, a `constructorParameters` entry already produces the
backing property. Adding the same name to `properties[]` causes:
"Sequence contains more than one matching element".

```jsonc
// WRONG for C#/Java/Go/Groovy
"constructorParameters": [{"name": "email", "type": "string"}],
"properties":            [{"name": "email", "type": "string"}]   // DUPLICATE

// CORRECT
"constructorParameters": [{"name": "email", "type": "string"}]
// non-constructor-only fields can still go in properties[]
```

In TypeScript, constructorParameters auto-become properties as well.

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are
reusable references. Use them by referencing their `typeIdentifier` from a file-generating
type's property / baseClassTypeIdentifier / interfaceTypeIdentifiers.

---

## Language-Specific Notes

### TypeScript
- MetaEngine **strips the `I` prefix** from interface names. `IUserRepository` → exported as
  `UserRepository`. If this collides with the implementing class, set `"fileName": "i-user-repository"`
  on the interface.
- Type mappings: `Number` → `number`, `String` → `string`, `Boolean` → `boolean`, `Date` → `Date`,
  `Any` → `unknown`.
- Auto-indents customCode newlines (`\n`).
- Decorators supported directly.

### C#
- `I` prefix preserved on interface names.
- `Number` maps to **`int`**, NOT `double`. Use `"type": "decimal"` or `"type": "double"`
  explicitly when you need non-integer numbers.
- `packageName` sets the namespace; omit/empty → no namespace declaration (GlobalUsings).
- Interface properties → `{ get; }`. Class properties → `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>` use `"type": "List<$user>"` with templateRefs.
- `isOptional` on properties → nullable reference type (`string?`).
- Every internal type reference in customCode must use templateRefs (see Rule 3).

### Python
- **Must provide explicit indentation (4 spaces)** after `\n` inside customCode bodies.
- typing imports are automatic.
- Pydantic available (BaseModel, Field) without import.

### Go
- Requires `packageName` for multi-file projects (default `github.com/metaengine/demo`).
- **No constructors** — use factory functions written in customCode.

### Java / Kotlin / Groovy
- `packageName` defaults to `com.metaengine.generated`.
- Constructor params auto-create properties (don't duplicate).

### Rust
- `generate_code` supports rust. Uses serde, chrono, uuid, rust_decimal automatically.

---

## Pattern Cookbook

### Basic interfaces with cross-references
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
Two files, automatic imports between them.

### Class with inheritance + methods
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

### Generic class + concrete implementation
```jsonc
{
  "classes":[
    {"name":"Repository","typeIdentifier":"repo-generic",
     "genericArguments":[{
        "name":"T","constraintTypeIdentifier":"base-entity",
        "propertyName":"items","isArrayProperty":true}],
     "customCode":[
       {"code":"add(item: T): void { this.items.push(item); }"},
       {"code":"getAll(): T[] { return this.items; }"}]},
    {"name":"User","typeIdentifier":"user",
     "baseClassTypeIdentifier":"base-entity",
     "properties":[{"name":"email","primitiveType":"String"}]},
    {"name":"UserRepository","typeIdentifier":"user-repo-class",
     "baseClassTypeIdentifier":"user-repo-concrete",
     "customCode":[{
       "code":"findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
       "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}]}]}
  ],
  "concreteGenericClasses":[
    {"identifier":"user-repo-concrete",
     "genericClassIdentifier":"repo-generic",
     "genericArguments":[{"typeIdentifier":"user"}]}
  ]
}
```
The concrete-generic creates a virtual `Repository<User>`. The class extends it via
`baseClassTypeIdentifier` → MetaEngine emits `extends Repository<User>` with imports.

### Array & dictionary virtual types
```jsonc
{
  "arrayTypes":[
    {"typeIdentifier":"user-list","elementTypeIdentifier":"user"},
    {"typeIdentifier":"string-array","elementPrimitiveType":"String"}],
  "dictionaryTypes":[
    {"typeIdentifier":"scores","keyPrimitiveType":"String","valuePrimitiveType":"Number"},
    {"typeIdentifier":"user-lookup","keyPrimitiveType":"String","valueTypeIdentifier":"user"}]
}
```
Reference via `"typeIdentifier": "user-list"` in properties.
**C# caveat**: arrayTypes → `IEnumerable<T>`. For `List<T>` use `"type":"List<$user>"`+templateRefs.

### Complex type expressions with templateRefs in properties
```jsonc
"properties":[{
  "name":"cache",
  "type":"Map<string, $resp>",
  "templateRefs":[{"placeholder":"$resp","typeIdentifier":"api-response"}]
}]
```
`templateRefs` work in properties, customCode, decorators, and (commentTemplateRefs) comments.

### Enum + class that uses it
```jsonc
{
  "enums":[{"name":"OrderStatus","typeIdentifier":"order-status",
    "members":[{"name":"Pending","value":0},{"name":"Shipped","value":2}]}],
  "classes":[{"name":"Order","typeIdentifier":"order",
    "properties":[{"name":"status","typeIdentifier":"order-status"}],
    "customCode":[{
      "code":"updateStatus(s: $status): void { this.status = s; }",
      "templateRefs":[{"placeholder":"$status","typeIdentifier":"order-status"}]}]}]
}
```
Enum filenames auto-suffixed: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#).

### Service with external DI
```jsonc
{
  "classes":[{
    "name":"ApiService","typeIdentifier":"api-service",
    "decorators":[{"code":"@Injectable({ providedIn: 'root' })"}],
    "customImports":[
      {"path":"@angular/core","types":["Injectable","inject"]},
      {"path":"@angular/common/http","types":["HttpClient"]}],
    "customCode":[
      {"code":"private http = inject(HttpClient);"},
      {"code":"getUsers(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
       "templateRefs":[{"placeholder":"$list","typeIdentifier":"user-array"}]}]}],
  "arrayTypes":[{"typeIdentifier":"user-array","elementTypeIdentifier":"user-dto"}]
}
```

### CustomFiles for type aliases / barrels
```jsonc
{
  "customFiles":[{
    "name":"types","path":"shared","identifier":"shared-types",
    "customCode":[
      {"code":"export type UserId = string;"},
      {"code":"export type Email = string;"}]}],
  "classes":[{
    "name":"UserHelper","path":"helpers",
    "customImports":[{"path":"shared-types"}],
    "customCode":[{"code":"static format(email: Email): string { return email.trim(); }"}]
  }]
}
```
`identifier` lets other files cite it via `customImports: [{path:"shared-types"}]`. Resolved
to a relative path.

### Interface method signatures (TS / C#) — IMPORTANT
For interfaces that a class will `implements`/`:`, define method signatures in `customCode`,
NOT as function-typed properties:

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
Function-typed properties (`"type":"() => Promise<User[]>"`) cause the implementing class
to duplicate them as property declarations alongside the customCode methods.

---

## Output Structure

- One file per generated `class` / `interface` / `enum` / `customFile` entry.
- File names: derived from `name` (kebab-case for TS, PascalCase for C#/Java, etc.) unless
  `fileName` is set.
- Path: `outputPath` + `path` (subdirectory).
- Imports/usings: auto-resolved between same-batch types via `typeIdentifier`/`templateRefs`.
- Virtual types (arrayTypes, dictionaryTypes, concreteGenericClasses,
  concreteGenericInterfaces) produce **NO files** — they're inline references only.
- `dryRun: true` returns the file contents in the response without writing.
- `skipExisting: true` (default) preserves existing files (stub pattern). Set false to overwrite.

---

## Common Mistakes (Top 10)

1. Referencing a `typeIdentifier` not in the same batch → property silently dropped. Verify
   every typeIdentifier matches a defined type in the same call.
2. Putting interface method signatures as function-typed properties → implementing class
   duplicates them. Use `customCode` for signatures.
3. Writing internal type names as raw strings in customCode (`"private repo: IUserRepository"`).
   Use `"private repo: $repo"` + `templateRefs`.
4. Using `arrayTypes` in C# expecting `List<T>` → you get `IEnumerable<T>`. Use
   `"type":"List<$user>"` + templateRefs for mutable lists.
5. Adding `System.*`, `typing.*`, `java.util.*` to customImports → duplication/errors.
   Let MetaEngine handle framework imports.
6. Duplicating constructor parameter names in `properties` (C#/Java/Go/Groovy) → "Sequence
   contains more than one matching element".
7. Using reserved words (`delete`, `class`, `import`) as property names → use `remove`,
   `clazz`, `importData`.
8. Splitting related types across multiple `generate_code` calls → cross-file imports won't
   resolve. Always batch.
9. Expecting `Number` → `double` in C#. It maps to `int`. Use `"type":"double"` or
   `"type":"decimal"` explicitly.
10. In TypeScript, forgetting `fileName` when `I`-prefixed interface and implementing class
    would collide on disk (since `I` is stripped from the export name).

---

## Spec-Driven Generators (openapi / graphql / protobuf / sql)

These are higher-level than `generate_code`. You don't construct types; you provide a
machine-readable spec and a target framework/language. The MCP itself produces a typed
client/model layer.

### generate_openapi
- Required: `framework` (angular|react|typescript-fetch|go-nethttp|java-spring|python-fastapi|csharp-httpclient|kotlin-ktor|rust-reqwest|swift-urlsession).
- Spec: `openApiSpec` (inline YAML/JSON) OR `openApiSpecUrl`.
- Per-framework option blocks (most are required where shown):
  - `csharpOptions.namespaceName` (REQUIRED for C#)
  - `goOptions.moduleName`, `goOptions.packageName` (BOTH REQUIRED for Go)
  - `javaSpringOptions.packageName` (REQUIRED)
  - `kotlinOptions.packageName` (REQUIRED)
  - `rustOptions.crateName` (REQUIRED)
  - `angularOptions`, `reactOptions`, `fetchOptions`, `pythonOptions`, `swiftOptions` are optional tunings.
- Cross-cutting: `bearerAuth`, `basicAuth`, `customHeaders[]`, `retries`, `timeout`,
  `errorHandling`, `documentation`, `optionsObjectThreshold`, `strictValidation`,
  `outputPath`, `skipExisting`, `dryRun`.
- Notable react option: `useTanStackQuery` (generates Query hooks).
- Notable fetch option: `useImportMetaEnv` (Vite/SvelteKit), `useMiddleware` (onRequest/onResponse/onError hooks), `useResultPattern`.
- Angular options: `useHttpResources`/`httpResourceTrigger` (Angular 19 `httpResource`),
  `useInjectFunction`, `providedIn`, `baseUrlToken`.

### generate_graphql
- Required: `framework` (same set, python is `python-fastapi`), `graphQLSchema` (SDL string).
- Same per-framework REQUIRED option blocks as openapi (csharp namespace, go module/package,
  java/kotlin packageName, rust crateName).
- Extras: `discriminatedUnions` (for GraphQL union types), `documentation`,
  `errorHandling.mode` (throw|result), `bearerAuth.enabled`, `basicAuth.enabled`,
  `customHeaders.headers[]`, `retries.maxRetries`, `timeout.seconds`.

### generate_protobuf
- Required: `framework` (python is **`python-httpx`** here, not fastapi), `protoSource`.
- Same option-block structure with REQUIRED keys (csharp namespace, go module+package,
  java/kotlin packageName, rust crateName).
- Python option `useCamelCaseAliases` adds Pydantic JSON aliases.
- Same auth/header/retry/timeout/errorHandling shape as graphql.

### generate_sql
- Required: `language` (typescript|csharp|go|python|java|kotlin|groovy|scala|swift|php|rust),
  `ddlSource` (CREATE TABLE statements).
- Per-language REQUIRED options where shown: go.moduleName, java.packageName,
  kotlin.packageName, groovy.packageName, scala.packageName, php.rootNamespace.
  Optional: csharp.namespace, rust.crateName, python.modelStyle (dataclass|pydantic|plain),
  php.useStrictTypes.
- Toggles: `generateInterfaces`, `generateNavigationProperties` (FK relationships),
  `generateValidationAnnotations`, `initializeProperties`.

---

## Workflow Summary (when generating)

1. **Analyze first**. Identify ALL types involved (entities, DTOs, services, repos, enums)
   across all files. The whole closure must go in one call.
2. Decide what's a class vs interface vs enum vs customFile vs virtual type.
3. Identify base classes / generic templates / concrete-generic instantiations.
4. For each type:
   - Plain fields → `properties[]` with `primitiveType`/`typeIdentifier`/raw `type`+`templateRefs`.
   - Methods, initialized fields, decorators → `customCode[]`, one entry per member.
   - Internal references in customCode → `templateRefs` with `$placeholder`.
   - External library types → `customImports`.
5. Construct ONE `generate_code` call (or persist to a JSON file and use
   `load_spec_from_file` for big specs).
6. Use `dryRun: true` first when uncertain, review the response, then run for real.
7. Honor language-specific gotchas (esp. C# `Number→int`, Python explicit indent, TS `I`-prefix
   stripping, C#/Java/Go/Groovy constructor-param duplication rule).

---

## Quick Decision Cheatsheet

| Need | Use |
|---|---|
| One method on a class | `customCode` entry |
| Field with no init | `properties` entry |
| Field with init / readonly | `customCode` entry (init form) |
| Reference another generated type from a property | `typeIdentifier` |
| Reference another generated type inside customCode/decorator/`type` string | `templateRefs` + `$placeholder` |
| Import an external library | `customImports` |
| Reusable `T[]` shape | `arrayTypes` (refer by typeIdentifier) |
| Reusable `Map<K,V>` shape | `dictionaryTypes` |
| Extend `Repository<User>` | `concreteGenericClasses` + `baseClassTypeIdentifier` |
| Implement `IRepository<User>` | `concreteGenericInterfaces` + `interfaceTypeIdentifiers` |
| Plain file (type alias / barrel / function) | `customFiles` |
| Generate from OpenAPI/GraphQL/proto/SQL | use the dedicated `generate_*` tool, not `generate_code` |
| Big or reusable spec | save JSON file, call `load_spec_from_file` |
| Preview without writing | `dryRun: true` |
| Stub pattern (don't overwrite custom edits) | leave `skipExisting: true` (default) |
