# MetaEngine MCP — Python Generation Warmup Summary

This is a self-contained reference distilled from the MetaEngine MCP `linkedResources` (`metaengine://guide/ai-assistant`, `metaengine://guide/examples`) and the live tool schemas. It is the only documentation the next generation session will have.

MetaEngine is a **semantic** code generator: you describe types, relationships, and methods as structured JSON, and it produces compilable, correctly-imported source files. Cross-references resolve, imports are computed, and language idioms are applied automatically. One well-formed JSON call replaces dozens of file writes.

---

## 1. Tools Exposed by the `metaengine` MCP Server

The next session has access to the following tools (only `generate_code` and `load_spec_from_file` actually emit files):

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns this guide. Optional `language` parameter (`typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`). Pure docs; no side effects. |
| `mcp__metaengine__generate_code` | The core tool — see full schema below. Accepts a single JSON document describing classes/interfaces/enums/etc. and writes files under `outputPath`. |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code` but reads the JSON spec from disk. Useful when the spec is large (saves context). Args: `specFilePath` (required), optional `outputPath`, `skipExisting`, `dryRun` (override values from the file). |
| `mcp__metaengine__generate_openapi` | (Available, not used here) Generate code from an OpenAPI spec. |
| `mcp__metaengine__generate_graphql` | (Available, not used here) Generate from GraphQL schema. |
| `mcp__metaengine__generate_protobuf` | (Available, not used here) Generate from `.proto`. |
| `mcp__metaengine__generate_sql` | (Available, not used here) Generate from SQL DDL. |

**MCP resources** (also available via `ListMcpResourcesTool` / `ReadMcpResourceTool`, server `metaengine`):
- `metaengine://guide/ai-assistant` — the canonical guide
- `metaengine://guide/examples` — worked examples (TypeScript-flavored but the structure is identical for all languages)

---

## 2. `generate_code` — Full Input Schema

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **YES** | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`. Use `"python"`. |
| `packageName` | string | no | Module/package/namespace. For Python this becomes the package directory and influences relative imports. Defaults differ per language (Go: `github.com/metaengine/demo`; Java/Kotlin/Groovy: `com.metaengine.generated`). |
| `outputPath` | string | no | Directory where files are written. Default: `.` (cwd). |
| `skipExisting` | bool | no | Default `true`. Skip files that already exist on disk (stub pattern). |
| `dryRun` | bool | no | Default `false`. When `true`, returns generated content in the response **without writing files**. Use this to preview. |
| `initialize` | bool | no | Default `false`. When `true`, properties are emitted with default initializers (e.g. `id = ''`). |
| `classes` | `Class[]` | no | Class definitions (regular AND generic class templates live here). |
| `interfaces` | `Interface[]` | no | Interface definitions. In Python these become `abc.ABC` / `Protocol` style abstract classes (see Python notes). |
| `enums` | `Enum[]` | no | Enum definitions. |
| `arrayTypes` | `ArrayType[]` | no | **Virtual** — declares reusable array references; emits NO files. |
| `dictionaryTypes` | `DictionaryType[]` | no | **Virtual** — declares reusable map references; emits NO files. |
| `concreteGenericClasses` | `ConcreteGeneric[]` | no | **Virtual** — `Repository<User>`-style inline reference; emits NO files. |
| `concreteGenericInterfaces` | `ConcreteGeneric[]` | no | **Virtual** — same as above for interfaces. |
| `customFiles` | `CustomFile[]` | no | Files without a class wrapper — type aliases, barrel exports, helper modules. |

> **Critical rule:** All cross-referenced types must appear **in the same single call**. `typeIdentifier` resolution does not span calls.

### `Class` shape

```jsonc
{
  "name": "User",                    // class name (CamelCase)
  "typeIdentifier": "user",          // unique handle for cross-refs (kebab/snake — your choice, just be consistent)
  "fileName": "user_model",          // optional: override generated file name (without extension)
  "path": "domain/users",            // optional: subdirectory under outputPath / packageName
  "comment": "Aggregate root",       // optional: doc comment

  "isAbstract": true,                // optional
  "baseClassTypeIdentifier": "base-entity",
  "interfaceTypeIdentifiers": ["i-aggregate", "i-serializable"],

  "genericArguments": [
    {
      "name": "T",
      "constraintTypeIdentifier": "base-entity",
      "propertyName": "items",       // creates a property named `items` of type T (or T[])
      "isArrayProperty": true
    }
  ],

  "constructorParameters": [
    { "name": "email", "primitiveType": "String" },
    { "name": "status", "typeIdentifier": "status" },
    { "name": "raw", "type": "dict[str, Any]" }   // raw string when nothing else fits
  ],

  "properties": [
    {
      "name": "id",
      "primitiveType": "String",     // String | Number | Boolean | Date | Any
      "comment": "Unique id",
      "isOptional": false,
      "isInitializer": true,         // emit default value
      "decorators": [ ... ],
      "templateRefs": [ ... ],       // for $placeholders inside `type`
      "type": "list[$user]"          // raw type expression — alternative to primitiveType/typeIdentifier
    },
    { "name": "owner", "typeIdentifier": "user" },
    { "name": "createdAt", "primitiveType": "Date" }
  ],

  "decorators": [
    { "code": "@dataclass", "templateRefs": [] }
  ],

  "customImports": [
    { "path": "external.lib", "types": ["SomeThing"] }
  ],

  "customCode": [
    {
      "code": "def display_name(self) -> str:\n    return self.email",
      "templateRefs": [
        { "placeholder": "$user", "typeIdentifier": "user" }
      ]
    }
  ]
}
```

Property type sources are mutually exclusive — choose one of:
- `primitiveType` — `String`, `Number`, `Boolean`, `Date`, `Any`
- `typeIdentifier` — reference to a same-batch class/interface/enum/array/dict
- `type` — raw string for complex expressions (combine with `templateRefs` for `$placeholder` substitution)

### `Interface` shape

Same shape as `Class` (name, typeIdentifier, fileName, path, comment, properties, customCode, customImports, decorators, genericArguments, interfaceTypeIdentifiers — to extend other interfaces).

For interfaces meant to be **implemented** by a class, declare method signatures in `customCode`, not as function-typed properties — otherwise the implementing class duplicates them.

### `Enum` shape

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "fileName": "order_status",       // optional
  "path": "domain/orders",          // optional
  "comment": "Lifecycle states",    // optional
  "members": [
    { "name": "Pending",  "value": 0 },
    { "name": "Shipped",  "value": 2 }
  ]
}
```

### `ArrayType` (virtual)

```jsonc
{ "typeIdentifier": "user-list", "elementTypeIdentifier": "user" }
{ "typeIdentifier": "string-array", "elementPrimitiveType": "String" }
```

### `DictionaryType` (virtual) — supports all 4 key/value combinations

```jsonc
{ "typeIdentifier": "scores",        "keyPrimitiveType": "String", "valuePrimitiveType": "Number" }
{ "typeIdentifier": "user-lookup",   "keyPrimitiveType": "String", "valueTypeIdentifier": "user" }
{ "typeIdentifier": "user-names",    "keyTypeIdentifier": "user",  "valuePrimitiveType": "String" }
{ "typeIdentifier": "user-meta",     "keyTypeIdentifier": "user",  "valueTypeIdentifier": "metadata" }
```

### `ConcreteGeneric` (virtual — for `Repository<User>` style references)

```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{ "typeIdentifier": "user" }]
}
```
Reference via `baseClassTypeIdentifier` or `templateRefs`. No file emitted.

### `CustomFile` shape

```jsonc
{
  "name": "types",                 // file name (no extension)
  "fileName": "types",             // optional override
  "path": "shared",                // directory
  "identifier": "shared-types",    // optional — lets other files import it via customImports
  "customCode": [
    { "code": "UserId = str" },
    { "code": "Email = str" }
  ],
  "customImports": [ ... ]
}
```

### `customImports` shape (used on classes / interfaces / customFiles)

```jsonc
{ "path": "fastapi", "types": ["FastAPI", "Depends"] }
```

For Python this becomes `from fastapi import FastAPI, Depends`. Use only for **external** libraries — never for stdlib types covered by auto-imports (see §3).

### `templateRefs` shape

```jsonc
{ "placeholder": "$user", "typeIdentifier": "user" }
```
Replace `$user` in `code` / `type` strings with the resolved type name AND auto-generate the import. Only valid for **internal** types (defined in the same call). External library types must use `customImports`.

---

## 3. Critical Rules (memorize before generating)

1. **One call, all related types.** Cross-references only resolve within a single batch.
2. **Properties = type declarations only. CustomCode = everything else** (methods, initialized fields, anything with logic). One `customCode` item = exactly one member.
3. **Use `templateRefs` for internal types in customCode.** Raw type names won't trigger imports. Pattern: `"$alias"` placeholder + `templateRefs[{placeholder:"$alias", typeIdentifier:"..."}]`.
4. **Never put framework / stdlib imports in `customImports`.** For Python the auto-imports cover: `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`. Adding them manually causes duplication or errors.
5. **`templateRefs` are for internal types only.** External library types → `customImports`. Never mix.
6. **Constructor params auto-create properties** (in C#/Java/Go/Groovy — TypeScript does it too via `public` shortcut). Python is more flexible but the safe rule remains: do NOT duplicate a name across `constructorParameters` and `properties`.
7. **Virtual types emit no files.** `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` produce reusable references only. They are referenced by `typeIdentifier` from properties/customCode/baseClass.
8. **Don't reference a `typeIdentifier` that doesn't exist in the batch** — the property is silently dropped.
9. **Avoid reserved words** as property names (`class`, `import`, `del`, `from`, `lambda`, `def`, etc. for Python). Use safe alternatives.
10. **Verify with `dryRun: true`** when uncertain — files are returned in the response but nothing is written.

---

## 4. Python-Specific Notes (PRIMARY FOCUS)

The published guide says relatively little about Python. Capture every confirmed fact, then mark the inferences clearly so the gen session knows where to verify with `dryRun`.

### 4.1 `language`
Use `"language": "python"`. Rust would be `"rust"`; do not confuse.

### 4.2 `packageName` / module naming
- Python convention: lowercase, snake_case, dotted (`my_app.domain.users`).
- The default if omitted is the same as Java/Kotlin/Groovy: `com.metaengine.generated` — **this is wrong-looking for Python**. Always set `packageName` explicitly to a snake_case module path (e.g. `domain`, `app.domain`, `mypkg`).
- The package name typically lays out the directory structure under `outputPath`. Combined with per-class `path`, this controls the final file location.

### 4.3 File path layout
- `outputPath` = base directory (e.g. `./src`).
- `packageName` may translate to a directory tree.
- `path` on a class/interface/enum/customFile = subdirectory below the package root.
- File names: by default derived from `name`. For Python the convention emitted is **snake_case** (`UserRepository` → `user_repository.py`). Use `fileName` to override (without extension).
- Enums get a similar treatment. Other languages add suffixes (`.enum.ts`, `OrderStatus.cs`); for Python the file is typically `<snake_name>.py` containing an `Enum` subclass.

### 4.4 Type mapping (`primitiveType` → Python type)
Confirmed from the auto-import list (`typing.*`, `datetime`, `decimal`):

| `primitiveType` | Python emitted type |
|---|---|
| `String` | `str` |
| `Number` | `int` (the engine uses integer for `Number` consistently across most languages — for floating point use raw `type: "float"`; for arbitrary precision use raw `type: "Decimal"`, which is auto-imported from `decimal`) |
| `Boolean` | `bool` |
| `Date` | `datetime` (from `datetime` module — the auto-import covers the whole module). If a date-only is needed, use raw `type: "date"`. |
| `Any` | `Any` (from `typing`) |

Collections (via virtual types):
- `arrayTypes` → `list[X]` (or `List[X]`); emitted with the `typing` shim auto-imported.
- `dictionaryTypes` → `dict[K, V]` (or `Dict[K, V]`).

If a precise float / Decimal / UUID / date type is required, use the `type` raw string (e.g. `"type": "float"`, `"type": "Decimal"`, `"type": "UUID"`). UUID is **not** in the auto-import list for Python, so for `UUID` add `customImports: [{path: "uuid", types: ["UUID"]}]`.

### 4.5 Dataclasses vs plain classes
- The auto-import list explicitly includes `dataclasses` and `pydantic (BaseModel, Field)` — meaning the engine is prepared to emit either pattern, depending on the decorators you supply.
- The engine itself does **not** automatically slap `@dataclass` on a class. The default emit is a plain class. To get dataclasses, add a class-level decorator:
  ```jsonc
  "decorators": [{ "code": "@dataclass" }]
  ```
  `dataclass` is auto-imported (no `customImports` needed).
- For Pydantic models, set `baseClassTypeIdentifier` to a custom-defined class **OR** use a raw extension via `interfaceTypeIdentifiers` is not appropriate; the cleanest approach is a `customCode`-based class header is not supported either. The supported pattern: declare a "BaseModel" placeholder via `customFiles` (or rely on the auto-import) and then set `decorators` / extend with `baseClassTypeIdentifier` referencing a same-batch class that itself extends `BaseModel`. Simpler path for the gen session: **stick with plain classes or `@dataclass`**, since DDD entities are typically not Pydantic. Use `dryRun: true` to confirm.

### 4.6 Enums
- Auto-import covers `enum`. Default emission: subclass of `Enum`. If integer-valued members are provided (`value: 0`, `value: 2`) the engine commonly emits `IntEnum` semantics — this is best verified with `dryRun`. To force a flavor explicitly, prefer a class-level decorator pattern is not supported for enums; instead rely on the integer values you supply.
- Each `member.value` is required to be a `number` per schema; that's compatible with `IntEnum`. If you want string-valued enums, you must instead declare a custom class via `customFiles`.

### 4.7 Method stubs and indentation
- **Critical Python-specific rule from the guide**: *"Must provide explicit indentation (4 spaces) after `\n` in customCode."*
- Other languages auto-indent method bodies; Python does NOT. Every line break inside a `customCode.code` string must be followed by exactly 4 spaces (or 8 for nested) **manually** in the JSON.
- Recommended stub body: `raise NotImplementedError`. Example for a method declared on a class:
  ```jsonc
  {
    "code": "def find_by_id(self, id: str) -> $user | None:\n    raise NotImplementedError",
    "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }]
  }
  ```
  Note the literal `\n` followed by 4 spaces.
- For interface methods that a subclass must implement, prefer either:
  - `raise NotImplementedError` (works in any plain class), or
  - decorate with `@abstractmethod` if the class extends `ABC` (the `abc` module is auto-imported). Example:
    ```jsonc
    "decorators": [{ "code": "@abstractmethod" }],
    "code": "def get_all(self) -> list[$user]:\n    ...",
    ```
- For empty bodies use `pass` — DO NOT leave the body empty (would be a syntax error).
- Constructor `__init__`: emit explicitly via `customCode` if you need a body. Constructor parameters declared via `constructorParameters` are typically emitted into the class signature; for Python the safest path is to put the constructor as a single `customCode` block with explicit `__init__(self, ...): \n    self.x = x` and skip `constructorParameters` if behavior is uncertain — verify with `dryRun`.

### 4.8 customImports for Python
Format:
```jsonc
"customImports": [
  { "path": "uuid", "types": ["UUID"] },
  { "path": "fastapi", "types": ["FastAPI", "Depends"] }
]
```
Becomes `from uuid import UUID` etc. To do plain `import x` (no `from`), use `path: "x"` with empty/omitted `types` — verify behavior with `dryRun` if needed.

### 4.9 Things confirmed auto-imported (do NOT add to customImports)
`typing.*` (Any, Optional, List, Dict, Union, etc.), `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`.

### 4.10 Things NOT auto-imported (you MUST customImport them when used)
`uuid.UUID`, `pathlib.Path`, `collections.*`, `functools.*`, third-party libs (`fastapi`, `sqlalchemy`, `httpx`, etc.).

---

## 5. Worked Pattern Examples (translated to Python intent)

### 5.1 Two related classes, one call
```jsonc
{
  "language": "python",
  "packageName": "domain",
  "classes": [
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
Produces `address.py` and `user.py` with `from .address import Address` in `user.py`.

### 5.2 Class extending an abstract base (DDD entity)
```jsonc
{
  "language": "python",
  "packageName": "domain",
  "classes": [
    {"name": "Entity", "typeIdentifier": "entity", "isAbstract": true,
     "decorators": [{"code": "@dataclass"}],
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "entity",
     "decorators": [{"code": "@dataclass"}],
     "properties": [{"name": "email", "primitiveType": "String"}],
     "customCode": [
       {"code": "def display_name(self) -> str:\n    return self.email"}
     ]}
  ]
}
```

### 5.3 Repository interface + stub
```jsonc
{
  "language": "python",
  "packageName": "domain",
  "interfaces": [{
    "name": "UserRepository", "typeIdentifier": "user-repo",
    "fileName": "user_repository",
    "customCode": [
      {"code": "def find_all(self) -> list[$user]:\n    ...",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "def find_by_id(self, id: str) -> $user | None:\n    ...",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }],
  "classes": [{
    "name": "User", "typeIdentifier": "user",
    "properties": [{"name": "id", "primitiveType": "String"}, {"name": "email", "primitiveType": "String"}]
  }]
}
```

### 5.4 Enum + class
```jsonc
{
  "language": "python",
  "packageName": "domain",
  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [
      {"name": "Pending", "value": 0},
      {"name": "Shipped", "value": 1},
      {"name": "Delivered", "value": 2}
    ]
  }],
  "classes": [{
    "name": "Order", "typeIdentifier": "order",
    "properties": [
      {"name": "id", "primitiveType": "String"},
      {"name": "status", "typeIdentifier": "order-status"}
    ],
    "customCode": [{
      "code": "def update_status(self, s: $status) -> None:\n    self.status = s",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]
  }]
}
```

### 5.5 Lists and Dicts via virtual types
```jsonc
{
  "language": "python",
  "packageName": "domain",
  "classes": [
    {"name": "Product", "typeIdentifier": "product",
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "Cart", "typeIdentifier": "cart",
     "properties": [
       {"name": "items", "typeIdentifier": "product-list"},
       {"name": "tags", "typeIdentifier": "string-array"},
       {"name": "scores", "typeIdentifier": "score-map"}
     ]}
  ],
  "arrayTypes": [
    {"typeIdentifier": "product-list", "elementTypeIdentifier": "product"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "score-map", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"}
  ]
}
```

### 5.6 Service with external import
```jsonc
{
  "language": "python",
  "packageName": "app",
  "classes": [{
    "name": "UserService", "typeIdentifier": "user-service", "path": "services",
    "customImports": [
      {"path": "uuid", "types": ["UUID"]}
    ],
    "customCode": [
      {"code": "def new_id(self) -> UUID:\n    raise NotImplementedError"},
      {"code": "def get(self, id: UUID) -> $user | None:\n    raise NotImplementedError",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }],
  "classes_dup_note": "the second classes block in TS examples actually merges; in JSON spec you keep ONE classes array — list both User and UserService inside it."
}
```

### 5.7 Generic Repository<T> + concrete repository (uncommon in Python)
Python typically uses `typing.Generic[T]`. The engine supports it via `genericArguments` on the class. Use `concreteGenericClasses` to produce a `Repository<User>` reference for `baseClassTypeIdentifier` or templateRefs. Verify final emission with `dryRun` before relying on it for Python.

---

## 6. `customCode` mechanics (Python-relevant)

- One member per `customCode` block — methods, initialized class fields, single `__init__`.
- Newlines inside `code` are preserved, but Python REQUIRES manual 4-space indentation after every `\n`. The engine will not auto-indent for Python.
- Decorators on methods: include them on a separate line inside the same `code` string (no separate `decorators` array on customCode):
  ```jsonc
  { "code": "@property\ndef email(self) -> str:\n    return self._email" }
  ```
  Note: that's `\n    ` (4 spaces) on continuation lines.
- For abstract methods place `@abstractmethod` on the line above `def`. Don't forget the class itself must extend `ABC` (use `interfaceTypeIdentifiers` or define a base via `customFiles`/another class).
- Stub policy:
  - **Concrete method placeholder**: `raise NotImplementedError`
  - **Abstract method body**: `...` (ellipsis literal — Python's idiomatic abstract body) or `raise NotImplementedError`
  - **Empty body (no logic intended)**: `pass`
  - Never leave the body empty — that's a SyntaxError.

---

## 7. Output structure produced

`generate_code` writes one `.py` file per non-virtual entity (each class, interface, enum, or customFile). With `dryRun: true` the same content is returned in the JSON response instead of being written.

For a typical DDD-style call you can expect:

```
<outputPath>/
  <packageName-or-path>/
    user.py             (class User)
    address.py          (class Address)
    order_status.py     (Enum subclass)
    user_repository.py  (abstract interface — note explicit fileName)
    services/
      user_service.py
```

File naming defaults to the snake_case form of `name`. Override with `fileName` (no extension).

The MCP response from `generate_code` typically reports each file written (path + size or contents in dryRun). The next session should inspect this response to confirm what was emitted before reading from disk.

---

## 8. Common Mistakes to Avoid

1. Generating related types in **separate** calls — cross-refs break.
2. Putting methods in `properties` — methods belong in `customCode`.
3. Writing internal type names as raw strings inside `customCode` (`"def get(self) -> User"`) — needed imports won't be generated. Use `$user` + `templateRefs`.
4. Forgetting Python-specific 4-space indentation in `customCode` newlines.
5. Adding `typing`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses`, `pydantic` to `customImports` (already auto-imported).
6. Duplicating names between `constructorParameters` and `properties`.
7. Empty method bodies — always `pass`, `...`, or `raise NotImplementedError`.
8. Referencing a `typeIdentifier` that doesn't exist in the batch — silently dropped.
9. Leaving `packageName` unset — Python ends up with the wrong default `com.metaengine.generated`.
10. Using reserved Python keywords as property names (`class`, `from`, `import`, `def`, `return`, `lambda`, `del`, `pass`, `not`, `is`, `or`, `and`, `if`, `else`, `elif`, `while`, `for`, `in`, `try`, `except`, `finally`, `raise`, `with`, `as`, `yield`, `global`, `nonlocal`).

---

## 9. Recommended Workflow for the Generation Session

1. Build ONE JSON spec describing the entire DDD module: aggregate roots, value objects, repositories (as interfaces), domain services, enums, and any value-object collections (via `arrayTypes` / `dictionaryTypes`).
2. Set `language: "python"`, `packageName: "<snake_case>"`, `outputPath: "<target dir>"`.
3. Use `dryRun: true` first to inspect the output. Adjust if:
   - Methods miss imports → add `templateRefs`.
   - Indentation looks off → add 4 spaces after every `\n`.
   - File layout is wrong → set `fileName` and/or `path` per class.
4. Re-run with `dryRun: false`. Set `skipExisting: true` (default) to avoid clobbering hand-edited files; set to `false` for clean regeneration.
5. If the spec is large, write it to a JSON file and call `mcp__metaengine__load_spec_from_file` with `specFilePath` to keep MCP message size small.

---

## 10. Quick `customImports` ↔ `templateRefs` Decision Table

| What you reference | Mechanism |
|---|---|
| Another class/interface/enum/array/dict declared **in the same call** | `typeIdentifier` (in properties) or `$placeholder` + `templateRefs` (in `code` / `type` strings) |
| stdlib module covered by auto-imports (`typing`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses`, `pydantic`) | NOTHING — engine auto-imports |
| External library (`fastapi`, `sqlalchemy`, `uuid`, `pathlib`, `httpx`, etc.) | `customImports: [{path, types}]` |
| A type alias / helper defined in a `customFile` | `customImports` referencing the customFile's `identifier` (or its `path/name`) |

---

## 11. Final Reminder

If at any point the gen session is unsure about how Python output will look (decorators, dataclass placement, indentation, file naming), call `generate_code` with `dryRun: true` first — the response includes the file contents without writing to disk. Iterate until the output is correct, then run again with `dryRun: false`.

End of summary.
