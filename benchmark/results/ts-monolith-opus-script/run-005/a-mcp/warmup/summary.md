# MetaEngine MCP — Knowledge Brief (Self-Contained)

MetaEngine is a semantic code generation system exposed via MCP. You describe types, relationships, and methods as structured JSON; MetaEngine produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, it resolves cross-references, manages imports, and handles language idioms automatically. **A single well-formed JSON call replaces dozens of error-prone file writes.**

---

## Tools Exposed

- `mcp__metaengine__metaengine_initialize` — returns the AI-assistant guide (already consumed in this warmup).
- `mcp__metaengine__generate_code` — **the workhorse**. Generates source files from a structured spec.
- `mcp__metaengine__load_spec_from_file` — loads a JSON spec from disk.
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` — convert specs from those formats.

For this benchmark we call **only** `generate_code`.

---

## generate_code — Full Input Schema

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | YES | `"typescript" | "python" | "go" | "csharp" | "java" | "kotlin" | "groovy" | "scala" | "swift" | "php" | "rust"` |
| `outputPath` | string | no | Default `"."`. Output directory. |
| `packageName` | string | no | Namespace / package / module. Default Go=`github.com/metaengine/demo`, Java/Kotlin/Groovy=`com.metaengine.generated`. C#: omit for GlobalUsings. |
| `initialize` | boolean | no | Default `false`. If `true`, properties get default-value initialization. |
| `skipExisting` | boolean | no | Default `true`. Skip files that exist. |
| `dryRun` | boolean | no | Default `false`. Returns generated code in response without writing to disk. |
| `classes` | array | no | Class definitions. |
| `interfaces` | array | no | Interface definitions. |
| `enums` | array | no | Enum definitions. |
| `customFiles` | array | no | Files without a class wrapper (type aliases, barrel exports, utility funcs). |
| `arrayTypes` | array | no | Reusable array type references — **NO files generated**. |
| `dictionaryTypes` | array | no | Reusable dictionary type references — **NO files generated**. |
| `concreteGenericClasses` | array | no | Concrete generic implementations like `Repository<User>` — **NO files generated**. |
| `concreteGenericInterfaces` | array | no | Same idea for interfaces. |

### `classes[]` shape (most-used type)

```jsonc
{
  "name": "string",                         // class name (required)
  "typeIdentifier": "string",               // unique id used for cross-references
  "path": "models/auth",                    // optional sub-directory
  "fileName": "custom-name",                // optional override (no extension)
  "comment": "Doc comment",                 // optional
  "isAbstract": false,
  "baseClassTypeIdentifier": "id-of-parent",
  "interfaceTypeIdentifiers": ["id1","id2"],
  "genericArguments": [
    { "name": "T",
      "constraintTypeIdentifier": "base-entity",
      "propertyName": "items",              // creates a `items: T[]` field
      "isArrayProperty": true }
  ],
  "constructorParameters": [
    { "name": "email", "primitiveType": "String" },
    { "name": "user", "typeIdentifier": "user" }
  ],
  "properties": [
    { "name": "id",
      "primitiveType": "String",            // String|Number|Boolean|Date|Any
      "typeIdentifier": "user",             // OR ref to internal type
      "type": "Map<string, $r>",            // OR raw type expression
      "templateRefs": [{"placeholder":"$r","typeIdentifier":"resp"}],
      "isOptional": false,
      "isInitializer": false,
      "decorators": [{"code":"@IsEmail()"}],
      "comment": "doc",
      "commentTemplateRefs": [] }
  ],
  "decorators": [
    { "code": "@Injectable({ providedIn: 'root' })",
      "templateRefs": [] }
  ],
  "customImports": [
    { "path": "@angular/core", "types": ["Injectable","inject"] }
  ],
  "customCode": [
    { "code": "private http = inject(HttpClient);" },
    { "code": "getById(id: string): Promise<$user> { ... }",
      "templateRefs": [{"placeholder":"$user","typeIdentifier":"user"}] }
  ]
}
```

### `interfaces[]` shape

Same as classes but: `genericArguments`, `properties`, `customCode`, `customImports`, `decorators`, `interfaceTypeIdentifiers` (extends-list), `fileName`, `path`, `comment`.

### `enums[]` shape

```jsonc
{ "name": "OrderStatus", "typeIdentifier": "order-status",
  "path": "models", "fileName": "order-status",
  "comment": "Doc",
  "members": [{"name":"Pending","value":0},{"name":"Shipped","value":2}] }
```

### `customFiles[]` shape (type aliases / barrels)

```jsonc
{ "name": "types", "path": "shared",
  "fileName": "types",
  "identifier": "shared-types",            // optional; lets others import via this id
  "customImports": [...],
  "customCode": [{"code":"export type UserId = string;"}] }
```

### `arrayTypes[]` shape (virtual)

```jsonc
{ "typeIdentifier": "user-array",
  "elementTypeIdentifier": "user"          // OR
  // "elementPrimitiveType": "String"
}
```

### `dictionaryTypes[]` shape (virtual)

```jsonc
{ "typeIdentifier": "scores",
  "keyPrimitiveType": "String",            // or keyTypeIdentifier
  "valuePrimitiveType": "Number",          // or valueTypeIdentifier
  "keyType": "string"                       // raw literal alternative
}
```
All 4 combos (prim/prim, prim/custom, custom/prim, custom/custom) work.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` shape

```jsonc
{ "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier":"user"}]
  //                  or {"primitiveType":"String"}
}
```

Reference these via `baseClassTypeIdentifier`, `typeIdentifier`, or `templateRefs`.

---

## The 7 Critical Rules (highest-impact failures)

### 1. Generate ALL related types in ONE call
`typeIdentifier` references resolve **only within the current batch**. If `UserService` references `User`, both must be in the same `generate_code` call. Splitting per-domain breaks cross-file imports silently.

### 2. Properties = type declarations. CustomCode = everything else.
- `properties[]` = uninitialized fields with a type only.
- `customCode[]` = methods, initialized fields, getters, anything with logic. **One `customCode` item = exactly one member.** MetaEngine inserts blank lines between blocks automatically.
- Never put methods in `properties`. Never put uninitialized type-only declarations in `customCode`.

### 3. Use templateRefs for internal types in customCode
Inside any `customCode.code`, `properties.type`, `decorators.code`, or `properties.comment` that mentions a type from the same batch, use a `$placeholder` plus a matching `templateRefs` entry. This is what triggers automatic import generation.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder":"$user","typeIdentifier":"user"}]
}]
```

Without `templateRefs`, the import won't be emitted — works in TS for same-folder collisions but fails across paths/namespaces; **mandatory in C#** for any cross-namespace internal type.

### 4. Never add framework imports to customImports
MetaEngine auto-imports the standard library. Adding them manually causes duplicates or errors. Only use `customImports` for **external libraries** (e.g. `@angular/core`, `rxjs`, `FluentValidation`).

| Language | Auto-imported (DO NOT specify) |
|---|---|
| C# | System.*, Collections.Generic, Linq, Tasks, Text, IO, Net.Http, DataAnnotations, Extensions.* |
| Python | typing.*, pydantic (BaseModel, Field), datetime, decimal, enum, abc, dataclasses |
| Java | java.util.*, java.time.*, java.util.stream.*, java.math.*, jakarta.validation.*, jackson.* |
| Kotlin | java.time.*, java.math.*, java.util.UUID, kotlinx.serialization.* |
| Go | time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http, +more |
| Swift | Foundation (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder…) |
| Rust | std::collections (HashMap, HashSet), chrono, uuid, rust_decimal, serde |
| Groovy | java.time.*, java.math.*, java.util (UUID, Date), java.io |
| Scala | java.time.*, scala.math (BigDecimal, BigInt), java.util.UUID, scala.collection.mutable.* |
| PHP | DateTime*, DateTimeImmutable, Exception*, ArrayObject, JsonSerializable, Stringable |
| TypeScript | (built-ins need no import) |

### 5. templateRefs are ONLY for internal types
External library types must use `customImports`. Internal types in same batch → `typeIdentifier` or `templateRefs`. **Never mix.**

### 6. Constructor parameters auto-create properties (C# / Java / Go / Groovy)
In these languages, `constructorParameters` automatically become class properties. **Do not duplicate them in `properties[]`** — error is `"Sequence contains more than one matching element"`. TypeScript: same — `constructor(public email: string)` already declares the field. Put only **non-constructor** fields in `properties[]`.

### 7. Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are *references only*. They never produce files. Use them by referencing their `typeIdentifier`/`identifier` in another type's properties, baseClass, or templateRefs.

---

## Output Structure

`generate_code` returns metadata about generated files. With `dryRun: true`, the response contains the actual file contents for inspection. With `dryRun: false` (default), files are written under `outputPath` using language-idiomatic conventions:

- **TypeScript**: `kebab-case.ts`, enums get `.enum.ts` suffix, `export class/interface/enum`, `import { X } from './path'`.
- **C#**: `PascalCase.cs`, `namespace` from `packageName`, `IInterface` preserved, `{ get; set; }` props for classes, `{ get; }` for interfaces.
- **Python**: `snake_case.py`, idiomatic `snake_case` method names (engine transforms), pydantic `BaseModel`s when appropriate.
- **Java**: `PascalCase.java`, `ALL_CAPS` enum members (idiomatic transform), `package` from `packageName`.
- **Go**: lowercase files, factory funcs (no constructors), exported `PascalCase` symbols.
- **Kotlin / Groovy / Scala / Swift / PHP / Rust**: language-idiomatic naming and imports.

`path` on a type controls sub-directory; `fileName` overrides the filename stem.

---

## Language-Specific Notes

### TypeScript
- `I` prefix is **stripped** from interface names: `IUserRepository` → exported as `UserRepository`. Use `fileName: "i-user-repository"` to avoid file collisions with the implementing class.
- Primitive map: `String→string`, `Number→number`, `Boolean→boolean`, `Date→Date`, `Any→unknown`.
- `customCode` newlines auto-indent.
- Decorators supported directly.
- TypeScript constructor parameters with modifiers (`public`, `private`) auto-create properties — same don't-duplicate rule applies.

### C#
- `I` prefix preserved.
- `Number` → `int` (NOT `double`). For non-int numerics use `"type": "decimal"` or `"type": "double"`.
- `packageName` sets the namespace; omit for GlobalUsings projects.
- Interface props emit `{ get; }`; class props `{ get; set; }`.
- `arrayTypes` produce `IEnumerable<T>`. For mutable list, use `"type": "List<$user>"` with templateRefs.
- `isOptional: true` → `string?` (nullable reference type).
- **Every internal type reference in customCode must use templateRefs**, or `using` directives won't be added across namespaces.

### Python
- Provide explicit 4-space indentation after `\n` inside `customCode.code` strings.
- `typing` imports are automatic.
- Methods get idiomatic `snake_case` (engine transforms from camelCase).

### Java / Kotlin
- Enums get idiomatic `ALL_CAPS` member names automatically.
- `packageName` required for non-default packages.
- `jakarta.validation`, `jackson` auto-imported.

### Go
- Requires `packageName` for multi-file projects.
- No constructors — use factory functions placed in `customCode`.
- Constructor parameters in spec are mapped accordingly.

---

## Pattern Reference (the patterns most likely to be needed)

### Two interfaces with cross-reference

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

### Class with inheritance and a method

```jsonc
{ "classes":[
  {"name":"BaseEntity","typeIdentifier":"base-entity","isAbstract":true,
   "properties":[{"name":"id","primitiveType":"String"}]},
  {"name":"User","typeIdentifier":"user",
   "baseClassTypeIdentifier":"base-entity",
   "properties":[{"name":"email","primitiveType":"String"}],
   "customCode":[{"code":"getDisplayName(): string { return this.email; }"}]}
]}
```

### Generic repo + concrete `Repository<User>`

```jsonc
{
 "classes":[
  {"name":"BaseEntity","typeIdentifier":"base-entity","isAbstract":true,
   "properties":[{"name":"id","primitiveType":"String"}]},
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
   "customCode":[{
    "code":"findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
    "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}]}]}
 ],
 "concreteGenericClasses":[{
   "identifier":"user-repo-concrete",
   "genericClassIdentifier":"repo-generic",
   "genericArguments":[{"typeIdentifier":"user"}]}]
}
```

The concrete generic creates the inline `Repository<User>`; the class extends via `baseClassTypeIdentifier`.

### Array & dictionary types

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
Reference via `"typeIdentifier":"user-list"` in a property.

### Complex type expression with templateRefs

```jsonc
"properties":[{
  "name":"cache",
  "type":"Map<string, $resp>",
  "templateRefs":[{"placeholder":"$resp","typeIdentifier":"api-response"}]
}]
```

### Enum + class using it

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

### Service with external DI (NestJS / Angular style)

```jsonc
{
 "classes":[{
   "name":"ApiService","typeIdentifier":"api-service","path":"services",
   "decorators":[{"code":"@Injectable({ providedIn: 'root' })"}],
   "customImports":[
    {"path":"@angular/core","types":["Injectable","inject"]},
    {"path":"@angular/common/http","types":["HttpClient"]},
    {"path":"rxjs","types":["Observable"]}],
   "customCode":[
    {"code":"private http = inject(HttpClient);"},
    {"code":"private baseUrl = '/api/users';"},
    {"code":"getAll(): Observable<$list> { return this.http.get<$list>(this.baseUrl); }",
     "templateRefs":[{"placeholder":"$list","typeIdentifier":"user-array"}]}]
 }],
 "arrayTypes":[{"typeIdentifier":"user-array","elementTypeIdentifier":"user-dto"}]
}
```

### customFiles for type aliases / barrel exports

```jsonc
{
 "customFiles":[{
   "name":"types","path":"utils","identifier":"shared-types",
   "customCode":[
    {"code":"export type UserId = string;"},
    {"code":"export type Email = string;"},
    {"code":"export type Status = 'active' | 'inactive' | 'pending';"}]
 }],
 "classes":[{
   "name":"UserHelper","path":"helpers",
   "customImports":[{"path":"shared-types"}],
   "customCode":[{"code":"static format(email: Email): string { return email.trim(); }"}]
 }]
}
```
The `identifier` on customFile + matching `path` in customImports auto-resolves the relative import.

### Interface method signatures (TS / C#) — use customCode, NOT function-typed properties

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
If you instead set `"type":"() => Promise<User[]>"` on a property, an implementing class will duplicate it as a property declaration.

### Constructor params — DON'T duplicate

```jsonc
// ✅ CORRECT
"constructorParameters":[
  {"name":"email","type":"string"},
  {"name":"status","typeIdentifier":"status"}],
"properties":[
  {"name":"createdAt","primitiveType":"Date"}    // only ADDITIONAL props
]
```

```jsonc
// ❌ WRONG — "Sequence contains more than one matching element"
"constructorParameters":[{"name":"email","type":"string"}],
"properties":[{"name":"email","type":"string"}]   // duplicate
```

---

## Common Mistakes (top 10)

1. **Don't** reference a `typeIdentifier` that doesn't exist in the batch → property silently dropped. **Do** verify every id matches.
2. **Don't** put method signatures as function-typed properties on interfaces being implemented. **Do** use `customCode`.
3. **Don't** write internal type names as raw strings in `customCode` (e.g. `"private repo: IUserRepository"`). **Do** use `$placeholder` + `templateRefs`.
4. **Don't** use `arrayTypes` in C# when you need a mutable `List<T>`. **Do** use `"type":"List<$x>"` + templateRefs.
5. **Don't** add `System.*`, `typing.*`, `java.util.*` to `customImports`. **Do** rely on auto-imports.
6. **Don't** duplicate constructor params in `properties` (C#/Java/Go/Groovy/TS-with-modifiers).
7. **Don't** use reserved words (`delete`, `class`, `import`) as property names. **Do** use `remove`, `clazz`, `importData`.
8. **Don't** split related types across multiple MCP calls. **Do** batch in one call — cross-file imports only resolve within a single batch.
9. **Don't** expect `Number` to map to `double` in C# — it's `int`. **Do** use `"type":"double"` or `"decimal"` explicitly.
10. **Don't** forget `fileName` when an `I`-prefixed interface and its implementing class would collide in TS. **Do** set `"fileName":"i-user-repository"`.

---

## TL;DR For The Generation Session

- ONE `generate_code` call. All related types together.
- `language: "typescript"` (this benchmark).
- Each type gets a unique `typeIdentifier`.
- Type-only fields → `properties[]`. Methods/initialized fields → `customCode[]` (one per member).
- Cross-references inside `customCode` / complex `type` strings → `$placeholder` with matching `templateRefs`.
- Inheritance → `baseClassTypeIdentifier`. Interface implementation → `interfaceTypeIdentifiers`.
- Generics: declare with `genericArguments` on the class; use `concreteGenericClasses` to create `Repository<User>`-style inline references.
- Reusable arrays/dicts → `arrayTypes` / `dictionaryTypes` (no files).
- Type aliases / utility files → `customFiles`.
- External libs → `customImports`. Standard lib → never specify.
- TS interface names lose `I` prefix (file collision risk → use `fileName`).
- TS `Number→number`, `String→string`, `Boolean→boolean`, `Date→Date`, `Any→unknown`.
- One call, complete spec, compilable output with correct imports — that's the contract.
