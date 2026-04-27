# MetaEngine MCP — Knowledge Brief (TypeScript focus)

This is a self-contained reference for using the `metaengine` MCP server to
generate TypeScript code from a structured JSON spec. The next session will use
this brief instead of the canonical docs — everything below is what you need.

---

## Tools exposed by the `metaengine` MCP server

- `mcp__metaengine__metaengine_initialize` — returns the AI Code Generation Guide
  (already read; this brief replaces it).
- `mcp__metaengine__generate_code` — **the only tool you call**. Takes one big
  JSON object describing every type/class/interface/enum/etc. and returns
  generated source files for the requested language.
- `mcp__metaengine__generate_openapi` / `generate_graphql` / `generate_protobuf`
  / `generate_sql` — convenience wrappers that translate from those specs to
  the same internal model (don't use these unless you've been given an OpenAPI/
  GraphQL/Proto/SQL spec).
- `mcp__metaengine__load_spec_from_file` — loads a JSON spec file (rarely
  needed; you usually inline the spec in the call).

---

## The cardinal rule: ONE call with EVERYTHING

`typeIdentifier` references only resolve **within a single `generate_code`
call**. If `OrderService` references `Order` and `OrderItem`, all three MUST
appear in the same call. Splitting per-domain breaks the typegraph and you get
broken/missing imports. **One call. Full spec. No exceptions.**

---

## Top-level shape of a `generate_code` call

```jsonc
{
  "language": "typescript",         // one of: typescript|csharp|python|go|java|kotlin|groovy|scala|swift|php
  "initialize": true,               // optional, harmless to include on first call

  "classes":                 [...], // file-generating
  "interfaces":              [...], // file-generating
  "enums":                   [...], // file-generating

  "arrayTypes":              [...], // virtual — reusable refs only, no file
  "dictionaryTypes":         [...], // virtual — reusable refs only, no file
  "concreteGenericClasses":  [...], // virtual — closes a generic, no file
  "concreteGenericInterfaces":[...],// virtual — closes a generic interface, no file

  "customFiles":             [...]  // arbitrary file (type aliases, barrels, raw code)
}
```

You can repeat the keys (the docs example does) — the engine merges arrays — but
prefer one array per kind for clarity.

---

## Properties vs CustomCode (most-violated rule)

| Field          | Use for                                  | Don't use for                |
|----------------|-------------------------------------------|------------------------------|
| `properties[]` | type declarations only — `name: Type`    | methods, initialized fields, logic |
| `customCode[]` | methods, initialized fields, any logic   | uninitialized type declarations |

One `customCode` entry = exactly one member (one method, one field). MetaEngine
auto-inserts blank lines between entries.

```jsonc
"properties": [
  {"name": "id", "primitiveType": "String"}     // type only, no initialization
],
"customCode": [
  {"code": "private http = inject(HttpClient);"},                      // initialized field
  {"code": "getAll(): T[] { return this.items; }"}                     // method
]
```

---

## Class schema (most important type)

```jsonc
{
  "name": "UserService",                     // PascalCase class name
  "typeIdentifier": "user-service",          // kebab-case, must be unique in the call
  "fileName": "user-service",                // optional — overrides default file name
  "path": "services",                        // optional — subdirectory
  "isAbstract": false,                       // optional
  "baseClassTypeIdentifier": "base-service", // optional — references another typeIdentifier OR a concreteGenericClass identifier
  "implementsTypeIdentifiers": ["i-foo"],    // optional — implemented interfaces (by typeIdentifier)
  "genericArguments": [...],                 // optional — see "Generics"
  "constructorParameters": [...],            // optional — see "Constructors"
  "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
  "customImports": [{"path": "@angular/core", "types": ["Injectable", "inject"]}],
  "properties": [...],
  "customCode": [...]
}
```

## Interface schema

Same shape as classes for the parts that apply (name, typeIdentifier, fileName,
path, properties, customCode, customImports, genericArguments,
baseClassTypeIdentifier as "extends"). Method signatures go in `customCode` as
unterminated declarations:

```jsonc
{
  "name": "IUserRepository",
  "typeIdentifier": "user-repo",
  "fileName": "i-user-repository",   // recommended in TS to avoid collision with implementing class
  "customCode": [
    {"code": "findAll(): Promise<$user[]>;",
     "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
    {"code": "findById(id: string): Promise<$user | null>;",
     "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
  ]
}
```

**TS gotcha:** the engine strips a leading `I` from interface *exported names*
(but not file names). `IUserRepository` exports as `UserRepository`. If a class
named `UserRepository` would collide, set `fileName: "i-user-repository"` on
the interface. Also: do NOT use function-typed properties (`"type": "() => Foo"`)
on an interface that a class will implement — the implementing class will
duplicate them as property declarations.

## Enum schema

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "members": [
    {"name": "Pending",  "value": 0},
    {"name": "Shipped",  "value": 2},
    {"name": "Delivered","value": 3}
  ]
}
```

In TS, enum filenames get `.enum.ts` suffix (e.g. `order-status.enum.ts`). The
engine applies language idiomatic transforms — for Java enum members become
`ALL_CAPS`, for TS they stay PascalCase as written. Don't fight it.

---

## Property schema

```jsonc
{
  "name": "items",                       // property name (camelCase in TS)
  "primitiveType": "String",             // EITHER primitiveType
  "typeIdentifier": "user-array",        // OR typeIdentifier (reference internal type)
  "type": "Map<string, $resp>",          // OR type (raw type expression, supports templateRefs)
  "templateRefs": [                      // required when `type` contains $placeholders
    {"placeholder": "$resp", "typeIdentifier": "api-response"}
  ],
  "isOptional": false,                   // optional — generates `field?: T` (or nullable)
  "comment": "Documentation for this field"
}
```

`primitiveType` values: `"String" | "Number" | "Boolean" | "Date" | "Any" | "Decimal" | "Guid" | ...`
- TS mappings: `String→string`, `Number→number`, `Boolean→boolean`, `Date→Date`,
  `Any→unknown`.
- (C# treats `Number` as `int`; TS does not. Use `"type": "double"` if you need
  a non-integer.)

**Use exactly ONE of** `primitiveType`, `typeIdentifier`, or `type` per property.
Prefer `primitiveType`/`typeIdentifier` over `type` when possible — `type` is
the escape hatch for complex expressions.

---

## CustomCode schema

```jsonc
{
  "code": "getUser(id: string): Promise<$user> { return this.repo.findById(id); }",
  "templateRefs": [
    {"placeholder": "$user", "typeIdentifier": "user"}
  ]
}
```

- Each entry = one member (method, getter, setter, initialized field).
- `\n` inside `code` is preserved. In Python you must indent (4 spaces) after
  newlines yourself; TS auto-indents.
- Any reference to an internal type (a type defined in the same call) MUST go
  through templateRefs — that's how the engine knows to add an `import`.

---

## templateRefs — internal-type references

```jsonc
"templateRefs": [
  {"placeholder": "$user",     "typeIdentifier": "user"},
  {"placeholder": "$userList", "typeIdentifier": "user-array"}
]
```

- `placeholder` must start with `$` and be unique within the `code` string.
- `typeIdentifier` MUST match a type defined elsewhere in the same call
  (a class, interface, enum, arrayType, dictionaryType, concreteGenericClass,
  or concreteGenericInterface).
- Triggers auto-import for the resolved type.
- Works in `customCode.code`, `properties[].type`, and `decorators[].code`.

**External library types do NOT go in templateRefs.** They go in `customImports`.

---

## customImports — external libraries only

```jsonc
"customImports": [
  {"path": "@angular/core",       "types": ["Injectable", "inject"]},
  {"path": "@angular/common/http","types": ["HttpClient"]},
  {"path": "rxjs",                "types": ["Observable"]}
]
```

Or for a customFile by identifier:

```jsonc
"customImports": [
  {"path": "shared-types"}        // resolves to the customFile with identifier "shared-types"
]
```

**Never put auto-imported things here.** TypeScript has no auto-imports — all
its primitive types are built-in language keywords — but for other languages
the engine auto-imports stdlib (`System.*` in C#, `typing.*` in Python,
`java.util.*` in Java, etc.). Adding them to customImports causes duplicate /
broken output.

---

## Virtual types (no files generated)

### `arrayTypes`

```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-array",    "elementTypeIdentifier": "user"},
  {"typeIdentifier": "string-array",  "elementPrimitiveType": "String"}
]
```

Reference via `"typeIdentifier": "user-array"` in a property — generates
`Array<User>` / `Array<string>` in TS with proper imports.

### `dictionaryTypes` (4 key/value combos)

```jsonc
"dictionaryTypes": [
  {"typeIdentifier": "scores",        "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-lookup",   "keyPrimitiveType": "String", "valueTypeIdentifier": "user"},
  {"typeIdentifier": "user-by-key",   "keyTypeIdentifier": "user-id","valuePrimitiveType": "String"},
  {"typeIdentifier": "user-meta",     "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata"}
]
```

In TS produces `Record<K, V>` typed properties.

### `concreteGenericClasses` and `concreteGenericInterfaces`

Closes a generic so it can be referenced as a normal type:

```jsonc
"concreteGenericClasses": [{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]   // or "primitiveType": "String"
}]
```

Then a class can `baseClassTypeIdentifier: "user-repo-concrete"` and the engine
emits `extends Repository<User>` with both imports. You can also reference the
identifier in templateRefs: `{"placeholder": "$ur", "typeIdentifier": "user-repo-concrete"}`.

---

## Generic class definition

```jsonc
{
  "name": "Repository",
  "typeIdentifier": "repo-generic",
  "genericArguments": [{
    "name": "T",
    "constraintTypeIdentifier": "base-entity",   // optional — `T extends BaseEntity`
    "propertyName": "items",                     // optional — auto-creates a property of type T (or T[])
    "isArrayProperty": true                      // optional — makes the auto-property an array
  }],
  "customCode": [
    {"code": "add(item: T): void { this.items.push(item); }"},
    {"code": "getAll(): T[] { return this.items; }"}
  ]
}
```

`T` inside `customCode` is treated as a type parameter literal — no templateRef
needed for the generic parameter itself.

---

## Constructor parameters

```jsonc
{
  "name": "User", "typeIdentifier": "user",
  "constructorParameters": [
    {"name": "email",  "primitiveType": "String"},
    {"name": "status", "typeIdentifier": "order-status"}
  ],
  "properties": [
    {"name": "createdAt", "primitiveType": "Date"}   // ONLY non-constructor fields here
  ]
}
```

In TypeScript, constructor parameters become parameter-properties:
`constructor(public email: string, public status: OrderStatus) {}` — they
become readable fields automatically. **Do not duplicate them in `properties[]`**
or you'll get "Sequence contains more than one matching element". (This is
strict for C#/Java/Go/Groovy; TypeScript also auto-promotes, follow the same
rule.)

---

## customFiles — type aliases, barrels, raw code

```jsonc
"customFiles": [{
  "name": "types",                    // file basename
  "path": "shared",                   // optional subdirectory
  "identifier": "shared-types",       // optional — enables `customImports: [{path: "shared-types"}]`
  "customCode": [
    {"code": "export type UserId = string;"},
    {"code": "export type Email = string;"},
    {"code": "export type Status = 'active' | 'inactive';"}
  ]
}]
```

Use this for TS type aliases, union/literal types, barrel exports, or any
free-form file content that doesn't fit a class/interface/enum.

---

## TypeScript-specific notes

- No imports for primitives — `string`, `number`, `boolean`, `Date`, `unknown`
  are all built-in.
- `I`-prefix on interface name is stripped from the exported symbol but kept
  on the file. To avoid collisions, set `fileName` on the interface (e.g.
  `"fileName": "i-user-repository"`).
- File names are kebab-case derived from the type name (`UserService` →
  `user-service.ts`). `path` adds a subdirectory.
- Decorators (`@Injectable`, `@Component`, etc.) supported via the `decorators`
  array.
- `arrayTypes` produce `Array<T>`. `dictionaryTypes` produce `Record<K, V>`.
- `customCode` newlines auto-indent. Methods get blank lines between them.

---

## Decorators

```jsonc
"decorators": [
  {"code": "@Injectable({ providedIn: 'root' })"},
  {"code": "@Component({ selector: 'app-x', templateUrl: './x.html' })"}
]
```

Decorators belong on the class itself. For property decorators, embed the
decorator in `customCode`:

```jsonc
"customCode": [
  {"code": "@Input() label!: string;"}
]
```

…and add the import via `customImports`.

---

## Worked example — full payload shape

```jsonc
{
  "language": "typescript",
  "initialize": true,

  "enums": [
    {"name": "OrderStatus", "typeIdentifier": "order-status",
     "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 1}]}
  ],

  "classes": [
    {"name": "Address", "typeIdentifier": "address",
     "properties": [
       {"name": "street", "primitiveType": "String"},
       {"name": "city",   "primitiveType": "String"}
     ]},

    {"name": "User", "typeIdentifier": "user",
     "properties": [
       {"name": "id",      "primitiveType": "String"},
       {"name": "email",   "primitiveType": "String"},
       {"name": "address", "typeIdentifier": "address"}
     ]},

    {"name": "Order", "typeIdentifier": "order",
     "properties": [
       {"name": "id",     "primitiveType": "String"},
       {"name": "user",   "typeIdentifier": "user"},
       {"name": "status", "typeIdentifier": "order-status"},
       {"name": "items",  "typeIdentifier": "order-item-array"}
     ]},

    {"name": "OrderItem", "typeIdentifier": "order-item",
     "properties": [
       {"name": "sku",      "primitiveType": "String"},
       {"name": "quantity", "primitiveType": "Number"},
       {"name": "price",    "primitiveType": "Number"}
     ]},

    {"name": "OrderService", "typeIdentifier": "order-service", "path": "services",
     "decorators": [{"code": "@Injectable({ providedIn: 'root' })"}],
     "customImports": [
       {"path": "@angular/core",        "types": ["Injectable", "inject"]},
       {"path": "@angular/common/http", "types": ["HttpClient"]},
       {"path": "rxjs",                 "types": ["Observable"]}
     ],
     "customCode": [
       {"code": "private http = inject(HttpClient);"},
       {"code": "private baseUrl = '/api/orders';"},
       {"code": "list(): Observable<$orderArray> { return this.http.get<$orderArray>(this.baseUrl); }",
        "templateRefs": [{"placeholder": "$orderArray", "typeIdentifier": "order-array"}]},
       {"code": "get(id: string): Observable<$order> { return this.http.get<$order>(`${this.baseUrl}/${id}`); }",
        "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]},
       {"code": "place(order: $order): Observable<$order> { return this.http.post<$order>(this.baseUrl, order); }",
        "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]},
       {"code": "updateStatus(id: string, status: $status): Observable<$order> { return this.http.patch<$order>(`${this.baseUrl}/${id}`, { status }); }",
        "templateRefs": [
          {"placeholder": "$status", "typeIdentifier": "order-status"},
          {"placeholder": "$order",  "typeIdentifier": "order"}
        ]}
     ]}
  ],

  "arrayTypes": [
    {"typeIdentifier": "order-array",      "elementTypeIdentifier": "order"},
    {"typeIdentifier": "order-item-array", "elementTypeIdentifier": "order-item"}
  ]
}
```

Notice:
- All cross-referenced types in one call.
- Internal type references go through `typeIdentifier`/templateRefs.
- External libraries (`@angular/core`, `rxjs`) go through `customImports`.
- No methods in `properties`, no uninitialized declarations in `customCode`.

---

## Output structure

`generate_code` returns a list of generated files (each with relative path and
content). For TypeScript:
- One `.ts` file per class/interface (filename = kebab-case type name, with
  `path` as subdirectory if specified).
- Enums get `.enum.ts` suffix.
- Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGeneric*`) produce
  no file — they're inlined as `Array<T>` / `Record<K,V>` / `Repository<User>`
  wherever referenced.
- Imports are computed automatically across all files in the batch.

Treat the returned files as the canonical output: the engine handles
indentation, blank-line spacing, and import resolution. Don't post-process them
unless absolutely necessary.

---

## Top-15 mistakes to avoid

1. **Splitting** related types across multiple `generate_code` calls. Cross-file
   imports only resolve within ONE call.
2. Putting **methods in `properties`** or uninitialized fields in `customCode`.
3. Writing **internal type names as raw strings** in `customCode` (e.g.
   `"private repo: UserRepository"`) instead of using `templateRefs` with `$placeholder`.
4. Adding **stdlib imports** (`System.*`, `typing.*`, `java.util.*`) to
   `customImports`. The engine auto-imports those.
5. Putting **external library types in templateRefs**. Only internal types
   defined in the same call go in templateRefs; libraries go in `customImports`.
6. **Duplicating constructor parameters** in `properties[]` → "Sequence
   contains more than one matching element".
7. Referencing a `typeIdentifier` that isn't defined in the batch — the
   property is silently dropped.
8. Using **function-typed properties** (`"type": "() => T"`) on an interface
   that a class will implement — the implementer duplicates them.
9. Forgetting `fileName` on an `I`-prefixed interface in TS when the
   implementing class would collide with its file name.
10. Using **reserved words** (`delete`, `class`, `import`) as property names.
11. Expecting `Number` to mean `double` (TS maps it to `number`, which is fine,
    but C# maps it to `int` — use `"type": "double"` if you need floating-point
    in C#).
12. Trying to use `arrayTypes` to get a mutable `List<T>` in C# (it produces
    `IEnumerable<T>`). Use `"type": "List<$user>"` with templateRefs instead.
13. Forgetting that **virtual types don't generate files** — if you expect a
    file for a `concreteGenericClass`, you misunderstand it.
14. Writing **multiple methods in one customCode entry**. One member per entry.
15. Forgetting to call `generate_code` ONCE with the entire spec.

---

## Mental model recap

- Spec is **declarative**. You describe types, the engine emits files.
- Internal references (`typeIdentifier` / templateRefs) → engine resolves and
  imports.
- External references (`customImports`) → engine emits the import line as-is.
- Virtual types (arrays, dicts, concrete generics) → reusable references, no
  files.
- One call. Full graph. Idiomatic output.

When in doubt: check `typeIdentifier` is defined; check methods are in
`customCode`; check internal refs use templateRefs; check stdlib isn't in
`customImports`.
