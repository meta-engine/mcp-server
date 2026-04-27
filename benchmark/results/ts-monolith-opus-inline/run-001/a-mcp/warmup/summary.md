# MetaEngine MCP — Knowledge Brief (TypeScript focus)

This is a self-contained brief for a downstream generation session that will NOT have access
to the MCP's `linkedResources`. Everything below is what was learned from
`mcp__metaengine__metaengine_initialize` plus the `metaengine://guide/examples` resource.

MetaEngine is a **semantic code generation system** exposed via MCP. You describe types,
relationships and methods as a structured JSON spec; MetaEngine produces compilable, correctly
imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP,
Rust. It is **not a template engine** — it resolves cross-references, manages imports, and
applies language-idiomatic transformations automatically. The headline benefit for an AI
caller is that **one well-formed JSON call replaces dozens of error-prone file writes**.

---

## Tools exposed

- `mcp__metaengine__metaengine_initialize` — returns the AI guide. Call once at warmup.
  Optional arg: `language` (one of `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php`).
- `mcp__metaengine__generate_code` — main code-gen tool. Single big JSON in, files written to
  disk (or returned in `dryRun` mode). Schema documented below.
- `mcp__metaengine__load_spec_from_file` — alternative entry point. Reads the same JSON spec
  from a `.json` file (path arg `specFilePath`). Useful for big specs to keep them out of
  context. Optional overrides: `outputPath`, `skipExisting`, `dryRun`.
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` —
  spec-conversion entry points (out of scope here; we use plain `generate_code`).
- Resources (read via `ReadMcpResourceTool`):
  - `metaengine://guide/ai-assistant` — same content `metaengine_initialize` returns.
  - `metaengine://guide/examples` — worked-out examples (incorporated below).

---

## CARDINAL RULE: ONE call, ALL related types

`typeIdentifier` cross-references **only resolve within a single batch**. If a class
references another type, both MUST appear in the same `generate_code` call. Splitting per
domain or per file silently drops references and breaks imports — there is no follow-up
"merge" pass. **Make ONE big call. Do not iterate file by file.**

---

## Properties vs customCode (the most-violated rule)

- `properties[]` = **type declarations only**. Field name + type. No initialization,
  no logic. One entry per field.
- `customCode[]` = **everything else** — methods, initialized fields, getters, anything with
  expression/body. **One `customCode` item = exactly one member.** MetaEngine inserts
  blank lines between blocks automatically.

```jsonc
"properties": [{"name": "id", "primitiveType": "String"}]   // declaration only
"customCode": [
  {"code": "private http = inject(HttpClient);"},           // initialized field
  {"code": "getAll(): T[] { return this.items; }"}          // method
]
```

Never put methods in `properties`. Never put uninitialized declarations in `customCode`.

---

## Internal references in customCode → use templateRefs

When `customCode` references another type from the same batch, reference it via a
`$placeholder` and add a `templateRefs` entry. This is what triggers automatic import
resolution.

```jsonc
"customCode": [{
  "code": "getUser(): Promise<$user> { ... }",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

If you write the type as a raw string (`"Promise<User>"`) the engine cannot generate the
import. Critical in C# (cross-namespace `using` is missed) and still recommended in TS for
correctness. Placeholders are arbitrary strings starting with `$` — name them clearly.
templateRefs work in `properties.type`, `customCode.code`, decorators, and comments.

**templateRefs are ONLY for types defined in this same batch.** External library types must
go in `customImports`. Never mix.

---

## customImports vs auto-imports

MetaEngine **auto-imports the standard library** for every language — never list these
yourself in `customImports`, you'll get duplication or errors.

| Language   | Auto-imported (do NOT add)                                                                    |
|------------|-----------------------------------------------------------------------------------------------|
| TypeScript | (none needed — built-in primitives)                                                           |
| C#         | `System.*`, `System.Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python     | `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java       | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin     | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*`                    |
| Go         | `time, fmt, log, strings, strconv, errors, context, sync, io, os, encoding/json, net/http`    |
| Swift      | `Foundation` (Date, UUID, URL, Decimal, URLSession, JSONEncoder, JSONDecoder, ...)            |
| Rust       | `std::collections` (HashMap, HashSet), `chrono`, `uuid`, `rust_decimal`, `serde`              |
| Groovy     | `java.time.*`, `java.math.*`, `java.util` (UUID, Date), `java.io` (File, InputStream, ...)   |
| Scala      | `java.time.*`, `scala.math` (BigDecimal, BigInt), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP        | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |

`customImports` is for **external libraries only** (`@angular/core`, `rxjs`, `FluentValidation`,
custom packages, …). Each entry: `{"path": "<package>", "types": ["A","B"]}`. The `types`
array is optional in some contexts (e.g. when importing a customFile by identifier alone).

---

## generate_code — input schema (full)

Top-level fields:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `language` | enum | **yes** | `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php|rust` |
| `outputPath` | string | no (default `.`) | directory for generated files |
| `packageName` | string | no | namespace/module/package; for C# omit/empty → no namespace; Java/Kotlin/Groovy default `com.metaengine.generated`; Go default `github.com/metaengine/demo` |
| `initialize` | bool | no (default `false`) | initialize properties with default values |
| `skipExisting` | bool | no (default `true`) | when true, existing files are not overwritten |
| `dryRun` | bool | no (default `false`) | preview mode — file contents returned, nothing written |
| `classes` | array | no | class definitions (regular + generic templates) |
| `interfaces` | array | no | interface definitions |
| `enums` | array | no | enum definitions |
| `arrayTypes` | array | no | reusable array type references — **no files generated** |
| `dictionaryTypes` | array | no | reusable dict/map type references — **no files generated** |
| `concreteGenericClasses` | array | no | inline `Repository<User>`-style references — **no files** |
| `concreteGenericInterfaces` | array | no | inline `IRepository<User>` references — **no files** |
| `customFiles` | array | no | files generated WITHOUT a class wrapper (type aliases, barrel exports, utility fns) |

### Class / Interface item

```jsonc
{
  "name": "UserService",                           // type name (TS strips leading 'I' on interfaces)
  "typeIdentifier": "user-service",                // unique slug used for cross-references
  "fileName": "user-service",                      // optional override (no extension)
  "path": "services/auth",                         // optional output subdirectory
  "comment": "Doc comment for the type",
  "isAbstract": true,                              // classes only
  "baseClassTypeIdentifier": "base-entity",        // classes only — extend a base class
  "interfaceTypeIdentifiers": ["i-foo","i-bar"],   // implements list (or interface 'extends' list)
  "decorators": [{"code": "@Injectable()", "templateRefs": [...]}],
  "customImports": [{"path": "@angular/core", "types": ["Injectable", "inject"]}],
  "constructorParameters": [                       // see Constructor section below
    {"name": "email", "primitiveType": "String"},
    {"name": "user",  "typeIdentifier": "user"},
    {"name": "limit", "type": "number"}
  ],
  "properties": [                                  // see Property section
    {"name": "id", "primitiveType": "String", "comment": "...", "isOptional": true,
     "isInitializer": true, "decorators": [...]}
  ],
  "customCode": [                                  // one entry = one method/initialized field
    {"code": "...", "templateRefs": [{"placeholder": "$x", "typeIdentifier": "x"}]}
  ],
  "genericArguments": [                            // makes this a generic template (Repository<T>)
    {"name": "T",
     "constraintTypeIdentifier": "base-entity",    // optional `T extends BaseEntity`
     "propertyName": "items",                      // creates property of type T (or T[])
     "isArrayProperty": true}
  ]
}
```

### Property item

| Field | Notes |
|-------|-------|
| `name` | property name |
| `primitiveType` | `String|Number|Boolean|Date|Any` — the only allowed primitives |
| `typeIdentifier` | reference to another type in this batch (class/interface/enum/arrayType/dictionaryType/concreteGeneric) |
| `type` | raw type expression (e.g. `"Map<string, $resp>"`, `"decimal"`, `"List<$user>"`). Use with `templateRefs` for placeholders |
| `templateRefs` | resolves `$placeholder` tokens in `type` |
| `comment` | doc comment; supports `commentTemplateRefs` |
| `isOptional` | nullable / optional |
| `isInitializer` | add a default-value initializer |
| `decorators` | `[{code, templateRefs}]` — e.g. `@IsEmail()`, `@Required()` |

Use **exactly one** of `primitiveType` / `typeIdentifier` / `type` per property.

### ConstructorParameter item

`{"name", "primitiveType" | "typeIdentifier" | "type"}` — same shape, fewer options.

**Critical:** in C#, Java, Go, and Groovy, constructor parameters **auto-create class
properties**. Do NOT also list them in `properties[]` — you will get
"Sequence contains more than one matching element". Put only *additional, non-constructor*
fields in `properties[]`. (TypeScript also auto-creates them via `public x: T` constructor
params — same rule applies; example 6 in the docs is TypeScript-flavored.)

### Enum item

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "comment": "...",
  "fileName": "order-status",      // optional
  "path": "enums",                 // optional
  "members": [
    {"name": "Pending", "value": 0},
    {"name": "Shipped", "value": 2}
  ]
}
```

Filename auto-suffixed: TS → `order-status.enum.ts`, C# → `OrderStatus.cs`.

### arrayTypes item (no file produced)

```jsonc
{ "typeIdentifier": "user-list", "elementTypeIdentifier": "user" }
{ "typeIdentifier": "string-array", "elementPrimitiveType": "String" }
```

In TS this becomes `Array<User>` / `Array<string>` when referenced. In C# arrayTypes generate
`IEnumerable<T>`; if you need `List<T>` use `"type": "List<$user>"` with templateRefs.

### dictionaryTypes item (no file produced) — all 4 combinations

```jsonc
{ "typeIdentifier": "scores",       "keyPrimitiveType": "String", "valuePrimitiveType": "Number" }
{ "typeIdentifier": "userLookup",   "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
{ "typeIdentifier": "byUser",       "keyTypeIdentifier": "user",  "valuePrimitiveType": "String" }
{ "typeIdentifier": "userMetadata", "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata" }
```

In TS: rendered as `Record<K, V> = {}`.

### concreteGenericClasses / concreteGenericInterfaces (no file produced)

Inline reference for `Repository<User>` etc.:

```jsonc
{
  "identifier": "user-repo",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
  // genericArguments may also use {"primitiveType": "String"}
}
```

Reference `user-repo` from another type's `baseClassTypeIdentifier` or via templateRefs. The
engine emits e.g. `extends Repository<User>` with the right imports.

### customFiles item (free-form file)

```jsonc
{
  "name": "types",
  "fileName": "types",         // optional override (no extension)
  "path": "utils",             // optional subdirectory
  "identifier": "shared-types",// optional — lets other files import via customImports {path:"shared-types"}
  "customImports": [...],
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type ResultSet<T> = { data: T[]; total: number; };"}
  ]
}
```

Used for type aliases, barrel exports, utility functions — anything that should NOT be wrapped
in a class. The optional `identifier` is what other files reference in `customImports.path` to
get the engine to compute the relative path automatically.

---

## TypeScript-specific notes (this run is TS)

- Primitive mapping: `String→string`, `Number→number`, `Boolean→boolean`, `Date→Date`, `Any→unknown`.
- Interface names: a leading `I` is **stripped** from the *exported* name (e.g. `IUserRepo` →
  exported as `UserRepo`). If the implementing class would collide on disk, set `fileName`
  on the interface: `"fileName": "i-user-repository"`.
- For interface methods you intend to `implements`, define them as **method signatures in
  `customCode`** (e.g. `"findAll(): Promise<$user[]>;"`), NOT as function-typed properties.
  Function-typed properties cause the implementing class to duplicate them as fields alongside
  your method bodies.
- Decorators are written as raw strings in `decorators[].code` (with optional templateRefs for
  custom decorators that come from other generated code).
- `customCode` newlines are auto-indented; engine inserts blank lines between blocks.
- `customImports` paths can be:
  - npm packages (`"@angular/core"`)
  - relative paths (`"../utils/types"`) — but prefer `customFiles.identifier` when possible
  - the `identifier` of a `customFiles` entry (no `types` array needed in some cases)
- arrayTypes render as `Array<T>` (or `T[]` in some contexts). Don't list `Array` in imports.
- dictionaryTypes render as `Record<K, V>`.

### Brief notes on other languages (for context only — this run is TS)

- C#: `Number→int` (NOT double — use `"type":"double"` or `"decimal"`); `I` prefix is preserved
  on interfaces; `packageName` sets namespace; class properties → `{ get; set; }`, interface
  properties → `{ get; }`; arrayTypes → `IEnumerable<T>` (use `List<$T>` for mutable).
  EVERY internal type reference in customCode MUST use templateRefs — raw class names break
  cross-namespace `using` resolution.
- Python: must provide explicit 4-space indentation after `\n` in `customCode` (TS auto-indents,
  Python does not).
- Go: requires `packageName` for multi-file projects; no constructors — use factory functions.
- Java: ALL_CAPS enum members are produced from PascalCase input (judges should tolerate this).

---

## Output structure

- Each `class`, `interface`, `enum`, and `customFile` produces ONE source file.
- `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`
  produce **zero files** — they are *type references* used in other entities' properties.
- File name = kebab-case of `name` (TS), Pascal of `name` (C#/Java/Kotlin), snake_case (Py/Go),
  unless `fileName` is set explicitly.
- Subdirectory comes from `path` (relative to `outputPath`).
- Imports: MetaEngine emits the correct imports for every cross-referenced type, computing
  relative paths between subdirectories. Standard library is auto-imported. Anything you list
  in `customImports` is added verbatim.
- In `dryRun: true` mode the response contains the generated file contents instead of writing
  to disk — useful to validate without touching the filesystem.

---

## Common mistakes (verbatim from the AI guide)

1. **Don't** reference a `typeIdentifier` that doesn't exist in the batch — the property is
   silently dropped. **Do** verify every typeIdentifier matches a defined type in the same call.
2. **Don't** put method signatures as function-typed properties on interfaces you'll
   `implements`. **Do** use `customCode` for interface method signatures.
3. **Don't** write internal type names as raw strings in customCode (e.g.
   `"private repo: IUserRepository"`). **Do** use templateRefs:
   `"private repo: $repo"` + `[{"placeholder":"$repo","typeIdentifier":"user-repo"}]`.
4. **Don't** use `arrayTypes` in C# when you actually need `List<T>`. **Do** use
   `"type": "List<$user>"` with templateRefs.
5. **Don't** add framework imports (`System.*`, `typing.*`, `java.util.*`, …) to `customImports`.
6. **Don't** duplicate constructor parameter names in the `properties` array
   (C#/Java/Go/Groovy). The engine raises "Sequence contains more than one matching element".
7. **Don't** use reserved words (`delete`, `class`, `import`) as property names — use
   `remove` / `clazz` / `importData` etc.
8. **Don't** generate related types in separate MCP calls — cross-file imports only resolve
   within a single batch. **Make one big call.**
9. **Don't** expect `Number` to map to `double` in C#. It maps to `int`. Use `"type":"double"`
   or `"decimal"` explicitly.
10. **Don't** forget `fileName` when both an `I`-prefixed interface and its implementing class
    would collide in TypeScript.

---

## Worked patterns (compact, ready to adapt)

### Pattern A — interfaces with cross-references

```jsonc
{
  "language": "typescript",
  "interfaces": [
    {"name":"Address","typeIdentifier":"address","properties":[
      {"name":"street","primitiveType":"String"},
      {"name":"city","primitiveType":"String"}
    ]},
    {"name":"User","typeIdentifier":"user","properties":[
      {"name":"id","primitiveType":"String"},
      {"name":"address","typeIdentifier":"address"}
    ]}
  ]
}
```

### Pattern B — class with inheritance + method

```jsonc
{
  "classes":[
    {"name":"BaseEntity","typeIdentifier":"base-entity","isAbstract":true,
     "properties":[{"name":"id","primitiveType":"String"}]},
    {"name":"User","typeIdentifier":"user","baseClassTypeIdentifier":"base-entity",
     "properties":[{"name":"email","primitiveType":"String"}],
     "customCode":[{"code":"getDisplayName(): string { return this.email; }"}]}
  ]
}
```

### Pattern C — generic class + concrete impl + extending class

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
       {"code":"getAll(): T[] { return this.items; }"}
     ]},
    {"name":"User","typeIdentifier":"user","baseClassTypeIdentifier":"base-entity",
     "properties":[{"name":"email","primitiveType":"String"}]},
    {"name":"UserRepository","typeIdentifier":"user-repo-class",
     "baseClassTypeIdentifier":"user-repo-concrete",
     "customCode":[{
       "code":"findByEmail(email: string): $user | undefined { return this.getAll().find(u => u.email === email); }",
       "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}]
     }]}
  ],
  "concreteGenericClasses":[{
    "identifier":"user-repo-concrete",
    "genericClassIdentifier":"repo-generic",
    "genericArguments":[{"typeIdentifier":"user"}]
  }]
}
```

Output: `class UserRepository extends Repository<User>` with all imports auto-generated.

### Pattern D — array & dictionary types

```jsonc
{
  "arrayTypes":[
    {"typeIdentifier":"user-list","elementTypeIdentifier":"user"},
    {"typeIdentifier":"string-array","elementPrimitiveType":"String"}
  ],
  "dictionaryTypes":[
    {"typeIdentifier":"scores","keyPrimitiveType":"String","valuePrimitiveType":"Number"},
    {"typeIdentifier":"user-lookup","keyPrimitiveType":"String","valueTypeIdentifier":"user"}
  ]
}
```

### Pattern E — complex type expression with templateRefs

```jsonc
"properties":[{
  "name":"cache",
  "type":"Map<string, $resp>",
  "templateRefs":[{"placeholder":"$resp","typeIdentifier":"api-response"}]
}]
```

### Pattern F — enum + class that uses it

```jsonc
{
  "enums":[{"name":"OrderStatus","typeIdentifier":"order-status",
    "members":[{"name":"Pending","value":0},{"name":"Shipped","value":2}]}],
  "classes":[{"name":"Order","typeIdentifier":"order",
    "properties":[{"name":"status","typeIdentifier":"order-status"}],
    "customCode":[{
      "code":"updateStatus(s: $status): void { this.status = s; }",
      "templateRefs":[{"placeholder":"$status","typeIdentifier":"order-status"}]
    }]}]
}
```

### Pattern G — service with external DI

```jsonc
{
  "classes":[{
    "name":"ApiService","typeIdentifier":"api-service","path":"services",
    "decorators":[{"code":"@Injectable({ providedIn: 'root' })"}],
    "customImports":[
      {"path":"@angular/core","types":["Injectable","inject"]},
      {"path":"@angular/common/http","types":["HttpClient"]},
      {"path":"rxjs","types":["Observable"]}
    ],
    "customCode":[
      {"code":"private http = inject(HttpClient);"},
      {"code":"getUsers(): Observable<$list> { return this.http.get<$list>('/api/users'); }",
       "templateRefs":[{"placeholder":"$list","typeIdentifier":"user-array"}]}
    ]
  }],
  "arrayTypes":[{"typeIdentifier":"user-array","elementTypeIdentifier":"user-dto"}]
}
```

### Pattern H — type aliases via customFiles + import by identifier

```jsonc
{
  "customFiles":[{
    "name":"types","path":"shared","identifier":"shared-types",
    "customCode":[
      {"code":"export type UserId = string;"},
      {"code":"export type Email = string;"}
    ]
  }],
  "classes":[{
    "name":"UserHelper","path":"helpers",
    "customImports":[{"path":"shared-types"}],
    "customCode":[{"code":"static format(email: Email): string { return email.trim(); }"}]
  }]
}
```

### Pattern I — interface methods (NOT function-typed properties)

```jsonc
{
  "interfaces":[{
    "name":"IUserRepository","typeIdentifier":"user-repo","fileName":"i-user-repository",
    "customCode":[
      {"code":"findAll(): Promise<$user[]>;",
       "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}]},
      {"code":"findById(id: string): Promise<$user | null>;",
       "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}]}
    ]
  }]
}
```

### Pattern J — constructor parameters (DO NOT duplicate)

```jsonc
{
  "enums":[{"name":"Status","typeIdentifier":"status",
            "members":[{"name":"Active","value":1}]}],
  "classes":[{
    "name":"User","typeIdentifier":"user",
    "constructorParameters":[
      {"name":"email","type":"string"},
      {"name":"status","typeIdentifier":"status"}
    ],
    "properties":[
      {"name":"createdAt","primitiveType":"Date"}   // ONLY non-constructor fields here
    ]
  }]
}
```

Generated:

```typescript
import { Status } from './status.enum';
export class User {
  createdAt!: Date;
  constructor(public email: string, public status: Status) {}
}
```

---

## Quick decision table

| You want… | Use |
|-----------|-----|
| A field declaration | `properties[]` |
| A method body | `customCode[]` (one entry per method) |
| An initialized field (`= inject(...)`, `= []`, etc.) | `customCode[]` (one entry) |
| Reference another type-in-this-batch from a method | `customCode.code` with `$placeholder` + `templateRefs` |
| Reference an external library | `customImports[]` |
| `Array<User>` / `User[]` field | `arrayTypes[]` then `properties[].typeIdentifier = "<arrayId>"` |
| `Record<string, User>` field | `dictionaryTypes[]` then `properties[].typeIdentifier = ...` |
| `Repository<User>` (extends or as a property type) | `concreteGenericClasses[]` |
| Type alias / barrel export / utility fns | `customFiles[]` (`identifier` for cross-imports) |
| Interface method signature (will be implemented) | `customCode[]` on the interface, NOT function-typed properties |
| Multiple files | All in one `generate_code` call |

---

## Final reminders

- The schema is permissive — invalid `typeIdentifier` values are silently ignored. Double-check
  every reference resolves to something defined in the same call.
- Reserved words as property names break codegen for the target language — pick safe synonyms.
- `dryRun: true` returns generated content without writing files; useful as a sanity check.
- If you can't fit the spec in the prompt, write it to a `.json` file and call
  `mcp__metaengine__load_spec_from_file` instead — same schema, no context cost.
- One call. One language. All related types. Cross-references resolve only within the batch.
