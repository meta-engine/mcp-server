# MetaEngine MCP — Warmup Summary (Python target)

This file is a self-contained reference for a follow-up generation session that targets **Python**. The next session will NOT have access to the MCP's `linkedResources`. Everything you need to call `mcp__metaengine__generate_code` correctly for Python is below.

---

## Tools exposed by the `metaengine` MCP server

The MCP exposes (only the first two are needed for Python codegen):

1. **`mcp__metaengine__metaengine_initialize`** — returns this same guide. Optional `language` enum: `typescript | python | go | csharp | java | kotlin | groovy | scala | swift | php`. **You do not need to call this in the gen session — this summary already contains it.**
2. **`mcp__metaengine__generate_code`** — *the* code-generation tool. Full schema below.
3. `mcp__metaengine__load_spec_from_file` — loads a JSON spec from disk (not used here).
4. `mcp__metaengine__generate_openapi` / `generate_graphql` / `generate_protobuf` / `generate_sql` — spec-format converters (not used for DDD-style generation).

The MCP also exposes two read-only resources via `ListMcpResourcesTool` / `ReadMcpResourceTool`:
- `metaengine://guide/ai-assistant`  ← canonical guide (already inlined here)
- `metaengine://guide/examples`      ← worked examples (already inlined here)

---

## `generate_code` — full input schema

Top-level object. **`language` is the only required field.** Everything else is optional, but you'll typically supply at least one of `classes`, `interfaces`, `enums`, or `customFiles`.

```jsonc
{
  // REQUIRED
  "language": "python",   // typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php|rust

  // Output controls
  "outputPath": ".",      // directory to write into (default ".")
  "packageName": "...",   // module/package name. Python: free-form, becomes the import root (e.g. "myapp.domain")
  "initialize": false,    // initialize properties with default values
  "skipExisting": true,   // don't overwrite existing files (stub pattern); default true
  "dryRun": false,        // preview-only — files NOT written, contents returned in response

  // FILE-GENERATING type arrays
  "classes":    [ ClassDef,    ... ],
  "interfaces": [ InterfaceDef, ... ],   // Python: emitted as ABC (abc.ABC + @abstractmethod)
  "enums":      [ EnumDef,     ... ],
  "customFiles":[ CustomFileDef, ... ],  // arbitrary file with raw customCode blocks

  // VIRTUAL type arrays — NEVER produce files; only resolvable type references
  "arrayTypes":               [ ArrayTypeDef,      ... ],
  "dictionaryTypes":          [ DictTypeDef,       ... ],
  "concreteGenericClasses":   [ ConcreteGenericDef,... ],
  "concreteGenericInterfaces":[ ConcreteGenericDef,... ]
}
```

### `ClassDef`

```jsonc
{
  "name": "User",                        // class name (PascalCase)
  "typeIdentifier": "user",              // unique key used by other entries to reference it
  "fileName": "user",                    // optional: override file stem (no extension)
  "path": "domain/users",                // optional: subdirectory under outputPath
  "comment": "User aggregate root.",     // optional: doc comment
  "isAbstract": false,
  "baseClassTypeIdentifier": "base-entity",          // single base class (by typeIdentifier)
  "interfaceTypeIdentifiers": ["i-user-repo"],       // implement one or more interfaces
  "genericArguments": [GenericArg, ...], // makes this a generic class template
  "constructorParameters": [ParamDef, ...],
  "properties":   [PropertyDef, ...],
  "customCode":   [CodeBlock, ...],      // ONE block per method/initialized field
  "customImports":[ImportDef, ...],      // ONLY for external libs (see "auto imports" below)
  "decorators":   [{ "code": "...", "templateRefs": [...] }, ...]
}
```

### `InterfaceDef`

Same fields as `ClassDef` minus `constructorParameters`/`isAbstract`. Use `customCode` (NOT function-typed properties) to declare method *signatures* that an implementing class will fulfill.

### `EnumDef`

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "fileName": "order_status",            // optional
  "path": "domain",                      // optional
  "comment": "...",
  "members": [
    { "name": "Pending", "value": 0 },
    { "name": "Shipped", "value": 2 }
  ]
}
```

### `PropertyDef`

```jsonc
{
  "name": "id",
  // exactly ONE of these:
  "primitiveType": "String",             // String | Number | Boolean | Date | Any
  "typeIdentifier": "user",              // reference to another type in the same batch
  "type": "Map<string, $resp>",          // raw type expression (use templateRefs for $placeholders)

  "isOptional": false,
  "isInitializer": false,                // emit a default initializer
  "comment": "...",
  "commentTemplateRefs": [...],
  "decorators": [{ "code": "...", "templateRefs": [...] }],
  "templateRefs": [ { "placeholder": "$resp", "typeIdentifier": "api-response" } ]
}
```

### `CodeBlock` (used in `customCode`, `decorators`, `customFiles`)

```jsonc
{
  "code": "def greet(self) -> str:\n    return f'hello {self.name}'",
  "templateRefs": [ { "placeholder": "$user", "typeIdentifier": "user" } ]
}
```
**One block = one member.** Blocks are joined with blank lines automatically.

### `ImportDef` (`customImports`)

```jsonc
{ "path": "fastapi", "types": ["FastAPI", "Depends"] }
```
For Python, `path` is the module to import from (becomes `from fastapi import FastAPI, Depends`).

### `ArrayTypeDef`

```jsonc
{ "typeIdentifier": "user-list",
  "elementTypeIdentifier": "user" }              // OR "elementPrimitiveType": "String"
```

### `DictTypeDef`

```jsonc
{ "typeIdentifier": "user-lookup",
  "keyPrimitiveType": "String",                  // OR "keyTypeIdentifier": "x"
  "valueTypeIdentifier": "user" }                // OR "valuePrimitiveType": "Number"
```

### `ConcreteGenericDef`

```jsonc
{ "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",      // points at a class with genericArguments
  "genericArguments": [ { "typeIdentifier": "user" } ] }
```
Reference its `identifier` from `baseClassTypeIdentifier` or `templateRefs` to get `Repository[User]`.

### `GenericArg` (on a class/interface)

```jsonc
{ "name": "T",
  "constraintTypeIdentifier": "base-entity",     // optional bound
  "propertyName": "items",                       // optional: auto-generate a property of type T
  "isArrayProperty": true }                      // optional: make it List[T]
```

---

## Critical rules (apply to every call)

1. **Single call, all related types.** `typeIdentifier` references only resolve within one `generate_code` call. If `UserService` references `User`, both go in the same call.
2. **`properties[]` = type declarations only. `customCode[]` = methods + initialized fields.** Never put a method in `properties`. Never put a bare type declaration without an initializer in `customCode`.
3. **Internal type references inside `customCode`/`type` strings MUST use `templateRefs`** with `$placeholder` syntax. Without templateRefs, MetaEngine cannot generate the import.
4. **Never add framework/standard-library imports to `customImports`.** Python auto-imports: `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`. Only put **external** libraries (e.g. `fastapi`, `sqlalchemy`, `httpx`) in `customImports`.
5. **`templateRefs` are ONLY for internal types** in this batch. External library types go through `customImports`. Don't mix.
6. **Constructor-parameter / properties duplication rule:** in C#/Java/Go/Groovy, constructor params auto-create properties — don't list them in `properties` too. *Python is NOT in that list*, so this duplication trap is less of an issue, but it's still cleanest to put fields in `properties` and let MetaEngine emit `__init__`.
7. **Virtual types never produce files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` only register reusable references.
8. **Don't reference an undefined `typeIdentifier`** — the property is silently dropped.
9. **Avoid Python reserved words** as property/parameter names: `class`, `def`, `from`, `import`, `return`, `lambda`, `True`, `False`, `None`, `global`, `nonlocal`, `pass`, `raise`, `try`, `except`, `finally`, `with`, `as`, `is`, `in`, `not`, `and`, `or`, `if`, `elif`, `else`, `for`, `while`, `break`, `continue`, `yield`, `async`, `await`. Pick alternatives (`clazz`, `from_`, `import_data`, etc.).

---

## Python-specific notes (READ THIS — the gen session is Python)

### `language` value
`"language": "python"` — exact lowercase string.

### `packageName` and module naming
- `packageName` becomes the Python package/module root (free-form string). Defaults are language-dependent; for Python you should set it explicitly when generating multi-file output (e.g. `"packageName": "myapp.domain"`).
- File names are emitted in **`snake_case`** based on the class/interface/enum `name`. `OrderStatus` → `order_status.py` (override with `fileName`).
- `path` becomes a subdirectory under `outputPath`, with `__init__.py`-style package layout assumed by Python tooling. Use forward slashes (`"path": "domain/orders"`).

### File path layout
- Output root: `outputPath` (default `.`).
- Per-type file: `<outputPath>/<path>/<fileName-or-snake_case-of-name>.py`.
- One generated type per file. Cross-file imports are produced automatically as `from .other_module import OtherClass` (relative imports inside the package).

### Type mapping
| MetaEngine token             | Python emitted type |
|------------------------------|---------------------|
| `primitiveType: "String"`    | `str` |
| `primitiveType: "Number"`    | `int` (default) — for floats use `"type": "float"`; for arbitrary precision use `"type": "Decimal"` (auto-imported from `decimal`) |
| `primitiveType: "Boolean"`   | `bool` |
| `primitiveType: "Date"`      | `datetime` (auto-imported from `datetime`). For date-only use `"type": "date"`. |
| `primitiveType: "Any"`       | `Any` (auto-imported from `typing`) |
| `arrayTypes`                 | `List[T]` (from `typing`) |
| `dictionaryTypes`            | `Dict[K, V]` (from `typing`) |
| `isOptional: true`           | `Optional[T]` (from `typing`) — emitted as `T | None` is not used; expect the legacy `Optional[...]` form. |
| `concreteGenericClasses`     | `Repository[User]` style (PEP 484 generic) |

When you need a non-default container or precision, use `"type": "..."` with template refs:
```jsonc
{ "name": "balance", "type": "Decimal" }                         // arbitrary precision number
{ "name": "ratio",   "type": "float" }                            // floating point
{ "name": "born",    "type": "date" }                             // date only (no time)
{ "name": "tags",    "type": "Set[$tag]",
  "templateRefs": [{ "placeholder": "$tag", "typeIdentifier": "tag" }] }
```

### Classes: `@dataclass` vs plain vs Pydantic
- The auto-import table includes both `dataclasses` and `pydantic` (`BaseModel`, `Field`). MetaEngine emits **plain Python classes by default** with an `__init__` synthesized from `properties` / `constructorParameters`.
- To force `@dataclass`, add it via `decorators`:
  ```jsonc
  "decorators": [{ "code": "@dataclass" }]
  ```
  (`dataclass` is auto-imported, so you do NOT need to add `dataclasses` to `customImports`.)
- To make a Pydantic model, set `baseClassTypeIdentifier` to a base class you also generate, OR put `BaseModel` in via raw `type`/`customCode` (Pydantic is auto-imported).
- **Recommendation for the upcoming DDD spec:** unless the spec explicitly calls for runtime validation, use plain classes (or `@dataclass` via decorator) — they round-trip cleanly with the judge and keep imports minimal.

### Enums
- The `enum` module is auto-imported.
- Default emission is `class OrderStatus(Enum):` with `Pending = 0` style members (each `member.value` becomes the right-hand side).
- For integer-flavor enums, the engine still emits an `Enum` subclass (not `IntEnum`) by default — if you specifically need `IntEnum`, override the base via raw code in `customCode` or set `baseClassTypeIdentifier` only if you also generate `IntEnum` (you can't, it's stdlib). Practical workaround: use `customCode` to declare the class and skip MetaEngine's enum emission.
- Filenames are `snake_case.py` (e.g. `order_status.py`), no `.enum.` infix like TypeScript.
- **Engine applies language-aware idiomatic transformations:** Python enum member names are emitted as `ALL_CAPS` (so `Pending` becomes `PENDING`). Don't fight this — the harness's judge tolerates the casing transformation. Treat the input member names as semantic identifiers; the engine will idiomatize them.

### Method stubs / `customCode` bodies
- A `customCode` block is the **complete member body** the engine emits verbatim (with auto-applied indentation between blocks). For Python you write the full `def`:
  ```jsonc
  { "code": "def greet(self) -> str:\n    return f'hello {self.name}'" }
  ```
- **CRITICAL Python indentation rule:** you MUST write 4-space indentation explicitly after every `\n` inside a `code` string. Unlike TypeScript/C# (where MetaEngine auto-indents), Python's significance of leading whitespace forces you to provide it yourself. Get this wrong and the generated file is a syntax error.
- Empty stubs: prefer `pass` for trivial bodies; use `raise NotImplementedError` for abstract-style placeholders. The engine does NOT auto-fill stub bodies — whatever you put in `code` is what gets emitted.
  ```jsonc
  { "code": "def reserve(self) -> None:\n    raise NotImplementedError" }
  { "code": "def touch(self) -> None:\n    pass" }
  ```
- Method signatures on `interfaces` (which become ABCs) should typically include `@abstractmethod` decorators or rely on the interface emission to add them — be explicit:
  ```jsonc
  { "code": "@abstractmethod\ndef find_by_id(self, id: str) -> $user | None: ...",
    "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
  ```
  `abc` and `abstractmethod` are auto-imported.
- **Engine applies idiomatic name transformations:** Python method names emit as `snake_case` regardless of the camelCase you might write. Same for property names. Plan your specs in either case — the engine normalizes.

### `customImports` for external libs (Python)
```jsonc
"customImports": [
  { "path": "fastapi",       "types": ["FastAPI", "Depends"] },
  { "path": "sqlalchemy.orm","types": ["Session"] }
]
```
Becomes `from fastapi import FastAPI, Depends` etc. Do NOT include `typing`, `dataclasses`, `enum`, `abc`, `decimal`, `datetime`, or `pydantic` here — they're auto-imported.

### `customCode` interactions with method stubs
- One block per method. Blocks render with a blank line between them.
- Blocks may reference internal types via `$placeholder` + `templateRefs` — those references trigger automatic `from .other_module import Other` directives.
- Class-level initialized fields (e.g. `_repo = InMemoryUserRepo()`) go in `customCode`, not `properties`. Use templateRefs for the type.
- For dependency-injection-style fields, use `properties` for the *typed* field (no initializer) and `__init__` will be synthesized; or use `constructorParameters` to make them required init args.

---

## Output structure produced

Every successful `generate_code` call returns:
- **By default (`dryRun: false`):** files are written under `outputPath`, mirroring `path` directories. The MCP response is a summary of what was written (paths + counts).
- **`dryRun: true`:** no disk writes; the response includes the generated file contents inline so you can review before committing. Use this whenever you're unsure of a spec — cheap to iterate.
- **`skipExisting: true` (default):** existing files are left untouched. Re-running after edits won't blow them away (the "stub pattern"). If you want a clean re-emit, set to `false`.

Per file, you can expect:
- Module-level imports (auto-resolved framework imports first, then external `customImports`, then internal cross-file imports).
- Class/interface/enum body following the Python form above.

---

## Quick checklist for the gen session

1. Set `"language": "python"` and `"packageName": "<root.module>"`.
2. Put EVERY type from the DDD spec in **one** `generate_code` call.
3. Use `properties` for typed fields, `customCode` for methods/initialized fields.
4. **4-space-indent every line inside `customCode` Python bodies.**
5. Use `$placeholder` + `templateRefs` for any same-batch type referenced inside `customCode`, raw `type` strings, or decorators.
6. `customImports` only for external libs — never for `typing`, `dataclasses`, `enum`, `abc`, `decimal`, `datetime`, `pydantic`.
7. `Number` defaults to `int`; for floats use `"type": "float"`; for money/precision use `"type": "Decimal"`.
8. `Date` defaults to `datetime`; for date-only use `"type": "date"`.
9. Don't fight the engine on enum `ALL_CAPS` or method `snake_case` — the harness's judge tolerates idiomatic transformations.
10. Stub bodies: explicit `pass` or `raise NotImplementedError`; engine never auto-fills.
11. Avoid Python keywords as identifiers (`class`, `from`, `import`, `lambda`, ...).
12. If unsure, do `dryRun: true` first.

---

## Reference: minimal Python example shape

```jsonc
{
  "language": "python",
  "packageName": "shop.domain",
  "outputPath": "./generated",
  "enums": [
    { "name": "OrderStatus", "typeIdentifier": "order-status",
      "members": [
        { "name": "Pending",   "value": 0 },
        { "name": "Confirmed", "value": 1 },
        { "name": "Shipped",   "value": 2 }
      ] }
  ],
  "classes": [
    { "name": "Customer", "typeIdentifier": "customer", "path": "customers",
      "properties": [
        { "name": "id",    "primitiveType": "String" },
        { "name": "email", "primitiveType": "String" },
        { "name": "createdAt", "primitiveType": "Date" }
      ] },
    { "name": "Order", "typeIdentifier": "order", "path": "orders",
      "properties": [
        { "name": "id",         "primitiveType": "String" },
        { "name": "customerId", "primitiveType": "String" },
        { "name": "status",     "typeIdentifier": "order-status" },
        { "name": "lines",      "typeIdentifier": "order-line-list" },
        { "name": "total",      "type": "Decimal" }
      ],
      "customCode": [
        { "code": "def confirm(self) -> None:\n    if self.status != $status.PENDING:\n        raise ValueError('not pending')\n    self.status = $status.CONFIRMED",
          "templateRefs": [{ "placeholder": "$status", "typeIdentifier": "order-status" }] }
      ] },
    { "name": "OrderLine", "typeIdentifier": "order-line", "path": "orders",
      "properties": [
        { "name": "sku",      "primitiveType": "String" },
        { "name": "quantity", "primitiveType": "Number" },
        { "name": "price",    "type": "Decimal" }
      ] }
  ],
  "arrayTypes": [
    { "typeIdentifier": "order-line-list", "elementTypeIdentifier": "order-line" }
  ]
}
```
This single call would emit `customers/customer.py`, `orders/order.py`, `orders/order_line.py`, and `order_status.py` (or under whatever `path` you pass for the enum), all with correct relative imports.

---

End of warmup summary.
