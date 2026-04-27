# MetaEngine MCP — Knowledge Brief (TypeScript focus, but cross-language facts retained)

MetaEngine is a *semantic* code generator exposed via MCP. You hand it a single structured-JSON spec describing types, relationships, and methods; it produces compilable, correctly-imported source files for TypeScript, C#, Python, Go, Java, Kotlin, Groovy, Scala, Swift, PHP, and Rust. Unlike templates, MetaEngine resolves cross-references, manages imports, and applies language idioms automatically. **One well-formed JSON call replaces dozens of error-prone file writes.**

---

## Tools exposed by the `metaengine` MCP server

- `mcp__metaengine__metaengine_initialize(language?)` — returns this guide. Helper, no side effects. `language` is one of `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php`.
- `mcp__metaengine__generate_code(...spec)` — **the workhorse.** Takes the full spec inline (see schema below) and writes generated files to `outputPath` (default `.`). Supports `dryRun` (returns content, no writes) and `skipExisting` (default `true`).
- `mcp__metaengine__load_spec_from_file({ specFilePath, outputPath?, skipExisting?, dryRun? })` — same as `generate_code` but reads the spec JSON from disk. Use when the spec is large enough that inlining would bloat context. Overrides take precedence over the in-file values.
- `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` — spec-conversion tools (OpenAPI / GraphQL SDL / .proto / SQL DDL → MetaEngine code). Not used for hand-authored specs.

The MCP also exposes resources:
- `metaengine://guide/ai-assistant` — the canonical AI guide (mirrored here).
- `metaengine://guide/examples` — runnable JSON examples (mirrored in the Examples section below).

---

## THE CARDINAL RULE

> **Generate ALL related types in ONE `generate_code` call.**
>
> `typeIdentifier` references resolve only within the current batch. If `UserService` references `User`, both must appear in the same call. Splitting per-domain breaks the typegraph: imports won't be generated, references silently drop.

---

## `generate_code` — full input schema

Top-level fields (all optional except `language`):

| Field | Type | Notes |
|---|---|---|
| `language` | enum (required) | `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php|rust` |
| `packageName` | string | Namespace/package/module. Defaults: Go `github.com/metaengine/demo`; Java/Kotlin/Groovy `com.metaengine.generated`. C#: omit/empty → no namespace declaration (good for GlobalUsings). |
| `outputPath` | string | Output directory. Default `.`. |
| `skipExisting` | bool | Default `true`. Skip files that already exist (stub pattern). |
| `dryRun` | bool | Default `false`. When true, returns file contents in the response and writes nothing. |
| `initialize` | bool | Default `false`. When true, properties get default-value initializers (e.g. `id = ''` instead of `id!: string`). |
| `classes` | array | See class shape below. |
| `interfaces` | array | Same shape as classes plus `interfaceTypeIdentifiers` to extend other interfaces. |
| `enums` | array | `{ name, typeIdentifier, members:[{name, value:number}], path?, fileName?, comment? }` |
| `arrayTypes` | array | Virtual reusable array types. **No file generated.** |
| `dictionaryTypes` | array | Virtual reusable map/dict types. **No file generated.** |
| `concreteGenericClasses` | array | Virtual `Foo<Bar>` references. **No file generated.** |
| `concreteGenericInterfaces` | array | Virtual `IFoo<Bar>` references. **No file generated.** |
| `customFiles` | array | Free-form files (type aliases, barrel exports). |

### Class / Interface shape

```jsonc
{
  "name": "UserService",                  // class/interface name
  "typeIdentifier": "user-service",       // unique identifier used by other entries to reference this
  "path": "services",                     // directory under outputPath; optional
  "fileName": "user-service",             // override file name (no extension); optional
  "comment": "Docstring/JSDoc for the type",
  "isAbstract": false,                    // class only

  "baseClassTypeIdentifier": "base-entity",       // class only; references another class OR a concreteGeneric*
  "interfaceTypeIdentifiers": ["user-repo"],      // class implements / interface extends

  "genericArguments": [{                  // makes this a generic template like Repository<T>
    "name": "T",
    "constraintTypeIdentifier": "base-entity",
    "propertyName": "items",              // optional: auto-creates a property of type T
    "isArrayProperty": true               //   ...or T[]
  }],

  "constructorParameters": [              // C#/Java/Go/Groovy/TS: params auto-become properties (do NOT duplicate in properties[])
    { "name": "email", "primitiveType": "String" },
    { "name": "status", "typeIdentifier": "status" },
    { "name": "raw", "type": "Map<string, any>" }
  ],

  "properties": [{
    "name": "id",
    "primitiveType": "String",            // String|Number|Boolean|Date|Any
    "typeIdentifier": "user",             // OR reference an internal type
    "type": "Map<string, $resp>",         // OR raw type expression with placeholders
    "templateRefs": [{ "placeholder": "$resp", "typeIdentifier": "api-response" }],
    "isOptional": true,
    "isInitializer": true,                // adds default-value init
    "comment": "Doc comment",
    "commentTemplateRefs": [...],
    "decorators": [{ "code": "@IsEmail()", "templateRefs": [...] }]
  }],

  "customCode": [                         // ONE entry = ONE member (method, getter, init field, etc.)
    { "code": "private http = inject(HttpClient);" },
    {
      "code": "getUser(id: string): Promise<$user> { return this.repo.findById(id); }",
      "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
    }
  ],

  "decorators": [{ "code": "@Injectable({ providedIn: 'root' })", "templateRefs": [...] }],

  "customImports": [                      // ONLY for external libraries — never standard lib
    { "path": "@angular/core", "types": ["Injectable", "inject"] },
    { "path": "rxjs", "types": ["Observable"] }
  ]
}
```

### Property typing — pick ONE of:
- `primitiveType: "String|Number|Boolean|Date|Any"` for primitives.
- `typeIdentifier: "<id>"` to reference another type in this batch (or an arrayType / dictionaryType / concreteGeneric).
- `type: "<raw expression>"` for complex/external expressions; combine with `templateRefs` to inject internal type names via `$placeholder`.

### Virtual types (no files generated)

```jsonc
"arrayTypes": [
  { "typeIdentifier": "user-list",     "elementTypeIdentifier": "user" },
  { "typeIdentifier": "string-array",  "elementPrimitiveType": "String" }
],
"dictionaryTypes": [
  { "typeIdentifier": "scores",         "keyPrimitiveType": "String", "valuePrimitiveType": "Number" },
  { "typeIdentifier": "user-lookup",    "keyPrimitiveType": "String", "valueTypeIdentifier": "user" },
  { "typeIdentifier": "user-names",     "keyTypeIdentifier": "user",  "valuePrimitiveType": "String" },
  { "typeIdentifier": "user-meta",      "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata" }
],
"concreteGenericClasses": [
  { "identifier": "user-repo",  "genericClassIdentifier": "repo-generic",  "genericArguments": [{ "typeIdentifier": "user" }] }
],
"concreteGenericInterfaces": [
  { "identifier": "iuser-repo", "genericClassIdentifier": "irepo-generic", "genericArguments": [{ "typeIdentifier": "user" }] }
]
```
Reference these by their `typeIdentifier` / `identifier` in `properties`, `baseClassTypeIdentifier`, `interfaceTypeIdentifiers`, or via `templateRefs`.

### CustomFiles (free-form files — no class wrapper)

```jsonc
"customFiles": [{
  "name": "types",                  // file name (no extension)
  "path": "shared",                 // dir
  "identifier": "shared-types",     // optional — lets others customImports it via this id
  "fileName": "types",              // override file name; optional
  "customCode": [
    { "code": "export type UserId = string;" },
    { "code": "export type Email = string;" }
  ],
  "customImports": [{ "path": "external-lib", "types": ["X"] }]
}]
```
Other files reference it via `customImports: [{ "path": "shared-types" }]` (the identifier is auto-resolved to the relative path).

---

## The Seven Critical Rules

### 1. ONE call with the full spec
typeIdentifiers resolve only within the call. Splitting causes silent drops and missing imports.

### 2. `properties[]` = type declarations only. `customCode[]` = everything else.
- `properties` = uninitialized type declarations (no logic, no init values).
- `customCode` = methods, getters/setters, initialized fields, anything with logic. **One entry per member.** Newlines between entries are added automatically.
- **Never** put methods in `properties`. **Never** put bare type declarations in `customCode`.

### 3. Use `templateRefs` for internal types in `customCode`, `properties.type`, `decorators`, comments.
The `$placeholder` syntax both substitutes the resolved type name AND triggers automatic import generation. Without `templateRefs`, MetaEngine cannot generate the import/using directive — raw strings like `User` will refer to nothing across files.

C# is the strictest: every cross-namespace internal type reference in customCode MUST use templateRefs or `using` directives won't be emitted.

### 4. Never put framework imports in `customImports`.
MetaEngine auto-imports standard lib types per language. Adding them manually causes duplicate or invalid imports.

| Language | Auto-imported (NEVER specify) |
|---|---|
| C# | `System.*`, `Collections.Generic`, `Linq`, `Tasks`, `Text`, `IO`, `Net.Http`, `DataAnnotations`, `Extensions.*` |
| Python | `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses` |
| Java | `java.util.*`, `java.time.*`, `java.util.stream.*`, `java.math.*`, `jakarta.validation.*`, `jackson.*` |
| Kotlin | `java.time.*`, `java.math.*`, `java.util.UUID`, `kotlinx.serialization.*` |
| Go | `time`, `fmt`, `log`, `strings`, `strconv`, `errors`, `context`, `sync`, `io`, `os`, `encoding/json`, `net/http`, … |
| Swift | `Foundation` (`Date`, `UUID`, `URL`, `Decimal`, `URLSession`, `JSONEncoder`, `JSONDecoder`, …) |
| Rust | `std::collections` (`HashMap`, `HashSet`), `chrono`, `uuid`, `rust_decimal`, `serde` |
| Groovy | `java.time.*`, `java.math.*`, `java.util` (`UUID`, `Date`), `java.io` (`File`, …) |
| Scala | `java.time.*`, `scala.math` (`BigDecimal`, `BigInt`), `java.util.UUID`, `scala.collection.mutable.*` |
| PHP | `DateTime*`, `DateTimeImmutable`, `Exception*`, `ArrayObject`, `JsonSerializable`, `Stringable` |
| TypeScript | (no imports needed — built-in types) |

`customImports` is for external libs only: `@angular/core`, `rxjs`, `FluentValidation`, your own `customFiles` identifier, etc.

### 5. `templateRefs` are ONLY for internal (in-batch) types.
External library types must use `customImports`. Same call → `typeIdentifier`/`templateRefs`. Outside the call → `customImports`. Never mix them.

### 6. Constructor parameters auto-create properties (C#/Java/Go/Groovy and TypeScript with `public` shorthand).
Do NOT also add the same name to `properties[]`. Doing so causes runtime errors like "Sequence contains more than one matching element". Put shared fields only in `constructorParameters`; put additional non-constructor fields in `properties`.

### 7. Virtual types do NOT generate files.
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reference factories. They appear only when other types use their `typeIdentifier`. They never produce a file of their own.

---

## Patterns at a glance

### Cross-referenced interfaces

```jsonc
{
  "language": "typescript",
  "interfaces": [
    { "name": "Address", "typeIdentifier": "address",
      "properties": [{"name":"street","primitiveType":"String"},{"name":"city","primitiveType":"String"}] },
    { "name": "User", "typeIdentifier": "user",
      "properties": [{"name":"id","primitiveType":"String"},{"name":"address","typeIdentifier":"address"}] }
  ]
}
```

### Class with inheritance + a method

```jsonc
"classes": [
  { "name":"BaseEntity","typeIdentifier":"base-entity","isAbstract":true,
    "properties":[{"name":"id","primitiveType":"String"}] },
  { "name":"User","typeIdentifier":"user","baseClassTypeIdentifier":"base-entity",
    "properties":[{"name":"email","primitiveType":"String"}],
    "customCode":[{"code":"getDisplayName(): string { return this.email; }"}] }
]
```

### Generic class + concrete impl
```jsonc
"classes":[
  { "name":"Repository","typeIdentifier":"repo-generic",
    "genericArguments":[{ "name":"T","constraintTypeIdentifier":"base-entity",
                          "propertyName":"items","isArrayProperty":true }],
    "customCode":[
      {"code":"add(item: T): void { this.items.push(item); }"},
      {"code":"getAll(): T[] { return this.items; }"}
    ]},
  { "name":"User","typeIdentifier":"user","baseClassTypeIdentifier":"base-entity",
    "properties":[{"name":"email","primitiveType":"String"}] },
  { "name":"UserRepository","typeIdentifier":"user-repo-class",
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
```
Result: `UserRepository extends Repository<User>` with imports of both `Repository` and `User` resolved.

### Complex type expression with placeholders
```jsonc
"properties":[{
  "name":"cache",
  "type":"Map<string, $resp>",
  "templateRefs":[{"placeholder":"$resp","typeIdentifier":"api-response"}]
}]
```

### Enum + class that uses it
```jsonc
"enums":[{ "name":"OrderStatus","typeIdentifier":"order-status",
  "members":[{"name":"Pending","value":0},{"name":"Shipped","value":2}]}],
"classes":[{ "name":"Order","typeIdentifier":"order",
  "properties":[{"name":"status","typeIdentifier":"order-status"}],
  "customCode":[{
    "code":"updateStatus(s: $status): void { this.status = s; }",
    "templateRefs":[{"placeholder":"$status","typeIdentifier":"order-status"}]
  }]}]
```
Enum file naming: `order-status.enum.ts` (TS), `OrderStatus.cs` (C#), language idioms apply.

### Interface method signatures (for `implements`-able interfaces)
Use `customCode`, NOT function-typed properties:

```jsonc
"interfaces":[{
  "name":"IUserRepository","typeIdentifier":"user-repo","fileName":"i-user-repository",
  "customCode":[
    { "code":"findAll(): Promise<$user[]>;",
      "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}] },
    { "code":"findById(id: string): Promise<$user | null>;",
      "templateRefs":[{"placeholder":"$user","typeIdentifier":"user"}] }
  ]
}]
```
If you put method signatures as function-typed properties, the implementing class will end up with property declarations duplicated alongside its real methods.

### Service with external DI
```jsonc
"classes":[{
  "name":"ApiService","typeIdentifier":"api-service",
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
```

### CustomFiles for type aliases / barrels
```jsonc
"customFiles":[{
  "name":"types","path":"utils","identifier":"shared-types",
  "customCode":[
    {"code":"export type UserId = string;"},
    {"code":"export type Status = 'active' | 'inactive' | 'pending';"},
    {"code":"export type ResultSet<T> = { data: T[]; total: number; page: number; };"}
  ]
}],
"classes":[{
  "name":"UserService","path":"services",
  "customImports":[{"path":"shared-types","types":["UserId","Status","ResultSet"]}],
  "customCode":[
    {"code":"updateStatus(id: UserId, status: Status): void { }"}
  ]
}]
```

### Constructor-parameter pattern (TS shown — same logic in C#/Java/Go/Groovy)
```jsonc
"classes":[{
  "name":"User","typeIdentifier":"user",
  "constructorParameters":[
    {"name":"email","primitiveType":"String"},
    {"name":"status","typeIdentifier":"status"}
  ],
  "properties":[
    {"name":"createdAt","primitiveType":"Date"}    // ONLY non-constructor fields here
  ]
}]
```
Generates `constructor(public email: string, public status: Status) {}` and `createdAt!: Date;` — no duplication.

---

## Output structure

- One file per non-virtual entry (`classes`, `interfaces`, `enums`, `customFiles`).
- File naming follows language idioms: kebab-case `.ts` for TypeScript, PascalCase `.cs` for C#, snake_case `.py` for Python, etc.
- Files are written under `outputPath` (default `.`); subdirs come from each entry's `path`.
- `skipExisting: true` (default) → existing files are left alone.
- `dryRun: true` → returns generated file contents inline, writes nothing. Use to preview.
- Cross-file imports are auto-generated for any reference resolved via `typeIdentifier` or `templateRefs`.

---

## Language-specific gotchas

### TypeScript
- Interface names: MetaEngine **strips a leading `I`** when emitting the symbol. `IUserRepository` becomes exported as `UserRepository`. Use `fileName` (e.g. `"i-user-repository"`) to keep file names distinct from the implementing class.
- Primitive map: `Number → number`, `String → string`, `Boolean → boolean`, `Date → Date`, `Any → unknown`.
- `customCode` newlines auto-indented; one entry = one method/field with auto blank line between.
- Decorators (`@Injectable(...)`) supported directly; class decorators on the type, property decorators on each property.
- Constructor parameters become `public x: T` shorthand fields — don't duplicate.

### C#
- `I` prefix preserved on interfaces.
- `Number → int`. For non-integers, set `"type": "decimal"` or `"type": "double"`.
- `packageName` sets the namespace; omit/empty for GlobalUsings.
- Interface props → `{ get; }`; class props → `{ get; set; }`.
- `arrayTypes` generate `IEnumerable<T>`. For `List<T>`, use `"type": "List<$user>"` with templateRefs.
- `isOptional: true` → nullable reference type (`string?`).
- ALL internal references in `customCode` MUST use templateRefs or `using` directives won't emit.

### Python
- Provide explicit 4-space indentation after `\n` inside `customCode` (no auto-indent).
- `typing.*`, `pydantic`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses` are auto-imported.
- Engine applies idiomatic `snake_case` to method names — judges should tolerate this.

### Go
- `packageName` is required for multi-file projects.
- No constructors — use factory functions in `customCode`.
- Constructor-parameter rule applies (don't duplicate names in `properties`).

### Java / Kotlin / Groovy / Scala
- Java/Groovy follow the constructor-parameter de-dup rule.
- Java enums emitted as `ALL_CAPS` (idiomatic) — don't fight this; judges have tolerance.
- Standard java.* / jakarta.* / jackson.* / kotlinx.serialization auto-imported.

### Swift / PHP / Rust
- Listed primitives auto-imported (Foundation / DateTime classes / std::collections etc.).
- Otherwise pattern is identical to other languages.

---

## Top 10 mistakes (and the fix)

1. Reference a `typeIdentifier` not in the batch → property silently dropped. **Verify every `typeIdentifier`.**
2. Method signatures as function-typed properties on an interface → the implementor double-declares them. **Use `customCode` for interface methods.**
3. Internal types as raw strings in `customCode` → no import. **Use `templateRefs`.**
4. Using `arrayTypes` in C# when you need `List<T>` → you get `IEnumerable<T>`. **Use `"type": "List<$user>"` with templateRefs.**
5. Adding `System.*` / `typing.*` / `java.util.*` to `customImports` → duplicate or broken imports. **Let MetaEngine handle them.**
6. Duplicating constructor parameters in `properties[]` (C#/Java/Go/Groovy/TS public-shorthand) → "Sequence contains more than one matching element". **Constructor params auto-create the property.**
7. Reserved words (`delete`, `class`, `import`) as property names → invalid code. **Rename (`remove`, `clazz`, `importData`).**
8. Splitting related types across multiple `generate_code` calls → cross-file imports break. **One call.**
9. Expecting `Number` to map to `double` in C# → it maps to `int`. **Use explicit `"type": "double"` / `"decimal"`.**
10. Forgetting `fileName` when an `I`-interface and its impl class would collide in TypeScript (after the `I` strip). **Set `"fileName": "i-user-repository"`.**

---

## Mental checklist before calling `generate_code`

1. Pick a single batch — every `typeIdentifier` referenced anywhere is defined here.
2. Each member is in the right bucket: declarations → `properties`, logic/initialized fields/methods → `customCode` (one per entry).
3. Every internal reference in `customCode`/`type`/`decorators` uses `$placeholder` + `templateRefs`.
4. Every external library reference uses `customImports`. Standard library? Don't list it.
5. Constructor params not duplicated in `properties`.
6. `arrayTypes` / `dictionaryTypes` / `concreteGenericClasses` defined for any reusable composite shape, then referenced via their `typeIdentifier`.
7. For interfaces meant to be `implements`-ed: method signatures are in `customCode`, not function-typed properties.
8. Set `language` (always), `packageName` if relevant, `outputPath` to the desired write root, and `dryRun:true` first if you want to preview.

If all eight check out, the call should produce compilable output with correct imports.
