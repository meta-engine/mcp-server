# MetaEngine MCP — Python Generation Warmup Summary

This summary distills the metaengine MCP `linkedResources` (the AI Code Generation Guide and the Examples resource) plus the full JSONSchema of every `mcp__metaengine__*` tool, with a focus on **Python** generation. The next session will rely on this without re-reading the docs.

---

## 1. Tools Exposed by the metaengine MCP

The server (`metaengine`) exposes these tools. Only `generate_code` and `load_spec_from_file` are relevant for the DDD-spec → Python task. The others convert specific source formats (OpenAPI/GraphQL/Proto/SQL).

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__metaengine_initialize` | Returns the AI Code Generation Guide. Optional `language` param (enum: typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php). |
| `mcp__metaengine__generate_code` | **Main tool.** Semantic code generation from a structured JSON spec (classes, interfaces, enums, etc.). |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code` but loads the spec from a JSON file path (saves context). Params: `specFilePath` (required), `outputPath`, `skipExisting`, `dryRun`. |
| `mcp__metaengine__generate_openapi` | Generates HTTP clients from OpenAPI specs (10 frameworks incl. python-fastapi). |
| `mcp__metaengine__generate_graphql` | Generates HTTP clients from GraphQL SDL (incl. python-fastapi). |
| `mcp__metaengine__generate_protobuf` | Generates HTTP clients from `.proto` definitions (incl. python-httpx). |
| `mcp__metaengine__generate_sql` | Generates typed model classes from SQL DDL. Python supports `modelStyle: "dataclass" | "pydantic" | "plain"`. |

Two MCP resources are exposed:
- `metaengine://guide/ai-assistant` — the canonical AI guide
- `metaengine://guide/examples` — worked examples (input + generated output)

---

## 2. `generate_code` — Full Input Schema

**Required**: `language` (enum). For us: `"language": "python"`.

### Top-level fields

| Field | Type | Description |
|-------|------|-------------|
| `language` | enum (required) | `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`. |
| `packageName` | string | Module/package/namespace name. **Python**: this becomes the package directory and `__init__.py` import root (see §4). For Go default `github.com/metaengine/demo`; for Java/Kotlin/Groovy default `com.metaengine.generated`. |
| `outputPath` | string (default `.`) | Output directory on disk. |
| `skipExisting` | boolean (default `true`) | Skip files that already exist (useful for stub pattern — re-runs don't clobber hand-edited files). |
| `dryRun` | boolean (default `false`) | If true, do NOT write files; return contents in the response. |
| `initialize` | boolean (default `false`) | Initialize properties with default values (e.g. `id = ''`). When false, properties are non-default-initialized (e.g. TS `id!: string`). |
| `classes[]` | array | Class definitions (regular & generic templates). |
| `interfaces[]` | array | Interface / abstract definitions (Python → ABC). |
| `enums[]` | array | Enum definitions (Python → `enum.Enum` subclass; see §4). |
| `arrayTypes[]` | array | **Virtual** array type aliases. NO files generated. |
| `dictionaryTypes[]` | array | **Virtual** dictionary type aliases. NO files generated. |
| `concreteGenericClasses[]` | array | **Virtual** concrete generic instantiations (e.g. `Repository[User]`). NO files generated. |
| `concreteGenericInterfaces[]` | array | Same as above for interfaces. NO files generated. |
| `customFiles[]` | array | Files WITHOUT class wrapper (utility files, type aliases, barrel exports). |

### `classes[]` element shape

```jsonc
{
  "name": "User",                           // Class name
  "typeIdentifier": "user",                 // UNIQUE id used for cross-references
  "fileName": "user_model",                 // Optional override (no extension)
  "path": "models",                         // Subdirectory under outputPath
  "comment": "...",                         // Doc comment (becomes Python docstring)
  "isAbstract": true,                       // Abstract class
  "baseClassTypeIdentifier": "base-entity", // Single base class
  "interfaceTypeIdentifiers": ["..."],      // Interfaces to implement (Python: ABC subclassing)
  "genericArguments": [{
      "name": "T",
      "constraintTypeIdentifier": "base-entity", // For 'where T : BaseEntity'
      "propertyName": "items",                   // Auto-creates a property of type T
      "isArrayProperty": true                    // Makes that property T[]
  }],
  "constructorParameters": [{
      "name": "email", "type": "str",        // OR primitiveType / typeIdentifier
      "primitiveType": "String",
      "typeIdentifier": "address"
  }],
  "properties": [ /* see below */ ],
  "customCode": [ /* see below */ ],
  "decorators": [{
      "code": "@dataclass",                  // Raw decorator code
      "templateRefs": [ /* if internal type referenced */ ]
  }],
  "customImports": [{
      "path": "pydantic", "types": ["BaseModel", "Field"]
  }]
}
```

### `properties[]` element shape

```jsonc
{
  "name": "id",
  "primitiveType": "String",          // String | Number | Boolean | Date | Any
  "typeIdentifier": "address",        // OR reference another generated type
  "type": "List[$user]",              // OR a raw type expression with placeholders
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}],
  "isOptional": true,                 // Generates Optional[T] / T | None in Python
  "isInitializer": true,              // Add a default value
  "comment": "Doc comment",
  "commentTemplateRefs": [ /* placeholder/typeIdentifier pairs for the comment */ ],
  "decorators": [{ "code": "...", "templateRefs": [...] }]
}
```

**Critical rule**: `properties` declares *types only*, no logic, no initialization with computation. Anything with logic goes in `customCode`.

### `customCode[]` element shape

```jsonc
{
  "code": "def get_email(self) -> str:\n    return self._email",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

**ONE customCode block = ONE member** (one method, one initialized field). Blocks get automatic newlines between them.

### `enums[]` element shape

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "fileName": "order_status",
  "path": "models",
  "comment": "...",
  "members": [
      {"name": "Pending", "value": 0},
      {"name": "Shipped", "value": 2}
  ]
}
```

### `interfaces[]` element shape

Same fields as classes (`name`, `typeIdentifier`, `properties`, `customCode`, `customImports`, `decorators`, `genericArguments`, `interfaceTypeIdentifiers`, `fileName`, `path`, `comment`).

For interfaces that a class will implement, **method signatures go in `customCode`** (NOT as function-typed properties), or you'll get duplicated declarations.

### `arrayTypes[]` element shape

```jsonc
{
  "typeIdentifier": "user-list",
  "elementTypeIdentifier": "user",        // Reference to another generated type
  "elementPrimitiveType": "String"        // OR a primitive
}
```
Required: `typeIdentifier`. Specify exactly one of `elementTypeIdentifier` / `elementPrimitiveType`.

### `dictionaryTypes[]` element shape

```jsonc
{
  "typeIdentifier": "scores",
  "keyPrimitiveType": "String",           // OR keyType (raw string) OR keyTypeIdentifier
  "keyType": "str",
  "keyTypeIdentifier": "user",
  "valuePrimitiveType": "Number",         // OR valueTypeIdentifier
  "valueTypeIdentifier": "metadata"
}
```
Required: `typeIdentifier`. Supports all 4 combinations of primitive/custom for key/value.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]`

```jsonc
{
  "identifier": "user-repository",
  "genericClassIdentifier": "repo-generic",   // The generic class typeIdentifier
  "genericArguments": [
      {"typeIdentifier": "user"},
      {"primitiveType": "String"}
  ]
}
```
Used to materialize `Repository[User]` as a referenceable type. NO files generated.

### `customFiles[]` element shape

```jsonc
{
  "name": "types",                            // file name without extension
  "fileName": "types_alt",                    // optional override
  "path": "shared",
  "identifier": "shared-types",               // optional: lets other customImports reference this file by id
  "customCode": [
      {"code": "UserId = str"},
      {"code": "Email = str"}
  ],
  "customImports": [
      {"path": "typing_extensions", "types": ["TypeAlias"]}
  ]
}
```

---

## 3. The 7 Critical Rules (Memorize These)

1. **Generate ALL related types in ONE call.** `typeIdentifier` references only resolve within the current batch. Cross-call imports do not work.
2. **`properties` = type declarations only. `customCode` = everything else** (methods, initialized fields, anything with logic). One customCode item = one member.
3. **Use `templateRefs` for internal types in customCode.** Without `$placeholder` + templateRefs, MetaEngine cannot resolve imports for cross-file references.
4. **Never add framework imports to `customImports`.** Standard-lib types are auto-imported. For Python, the engine auto-imports: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`. Use `customImports` ONLY for external packages (e.g. `fastapi`, `sqlalchemy`, `httpx`).
5. **`templateRefs` are ONLY for internal types** (defined in the same call). External library types must use `customImports`. Never mix.
6. **Constructor parameters auto-create properties** in C#/Java/Go/Groovy — do NOT duplicate them in `properties[]` ("Sequence contains more than one matching element" error). For Python the doc shows the same warning; treat constructorParameters as canonical and put only *additional* fields in `properties[]`.
7. **Virtual types don't generate files**: `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`. They are reference-only.

### Other failure modes to avoid

- Referencing a `typeIdentifier` that doesn't exist in the batch → property is silently dropped.
- Function-typed properties on interfaces that a class will implement → duplicate declarations.
- Reserved words as property names: `class`, `import`, `delete`, `def`, `return`, `from`, etc. — pick safe alternatives (`clazz`, `importData`, `remove`).
- Mixing `arrayTypes` with raw `type` strings inconsistently.

---

## 4. Python-Specific Notes (CRITICAL for our task)

### packageName / module naming

- `packageName` becomes the Python package directory name and the import root for cross-file imports.
- Convention: lowercase `snake_case` (e.g. `my_domain`, NOT `MyDomain`).
- If omitted, the engine generates files at `outputPath` directly without a package wrapper. For DDD work where there are multiple bounded contexts, use a single coherent `packageName`.
- Module file names follow Python `snake_case` convention: `OrderStatus` enum → `order_status.py`. (Compare TS `order-status.enum.ts`, C# `OrderStatus.cs`.) Override with the `fileName` field if needed (no extension, snake_case preferred).
- Sub-packages are created from the `path` field on a class/enum/customFile (e.g. `"path": "domain/orders"` → file goes to `domain/orders/order.py`).

### File path layout

`<outputPath>/<packageName>/<path>/<fileName>.py`

If `packageName` is omitted: `<outputPath>/<path>/<fileName>.py`. Each generated package directory typically gets an `__init__.py` (the engine handles this; do not write one yourself).

### Type mapping — `primitiveType` → Python

| primitiveType | Python type | Module |
|---------------|-------------|--------|
| `String` | `str` | builtin |
| `Number` | `float` (NOTE: in C# this maps to `int`; in Python the safer assumption per docs is float-style numeric, but if you need an integer use `"type": "int"` explicitly) |
| `Boolean` | `bool` | builtin |
| `Date` | `datetime.datetime` (or `datetime.date` if you need date-only — use raw `"type": "date"` with `from datetime import date` auto-imported) | `datetime` (auto-imported) |
| `Any` | `Any` | `typing` (auto-imported) |

> **Tactic for ambiguous numeric types**: when a DDD spec says "amount" or "money", use `"type": "Decimal"` (the engine auto-imports `decimal`). For integer IDs use `"type": "int"`. For floating-point measurements use `"primitiveType": "Number"` or `"type": "float"`.

### Collection mapping

- `arrayTypes` → `List[T]` (typing). For typed lists prefer `"type": "list[$item]"` or `"type": "List[$item]"` with templateRefs if you want a specific Python form.
- `dictionaryTypes` → `Dict[K, V]` (typing). All four key/value combinations work.
- Optional → `Optional[T]` (or `T | None` in 3.10+). Use `"isOptional": true` on the property.

### Class style — dataclass vs plain vs Pydantic

- **`generate_code` (the DDD path) emits PLAIN classes by default.** It does NOT auto-add `@dataclass` or `BaseModel`. To opt in, use the `decorators` field:
  ```jsonc
  "decorators": [{"code": "@dataclass"}]
  ```
  The engine will auto-import `dataclass` from `dataclasses` (it's in the auto-import list).
- For Pydantic models: add `"decorators"` is not enough — Pydantic uses inheritance, not decoration. Either:
  - Use `interfaceTypeIdentifiers` / `baseClassTypeIdentifier` to extend a `BaseModel` defined as a customFile or external import, OR
  - Add `customImports: [{"path": "pydantic", "types": ["BaseModel"]}]` and put `class Foo(BaseModel):` via raw class is NOT how the engine works — instead, declare a class whose base is the BaseModel via a customFile alias, or just rely on the auto-import of `pydantic` (BaseModel, Field are in the auto-import list) and define the inheritance via a base class type.
  - **Practical heuristic for DDD entities**: prefer `@dataclass` decoration via `decorators: [{"code": "@dataclass"}]`. It's the cleanest, idiomatic match for value objects and entities.
- The `generate_sql` tool (different tool!) accepts `pythonOptions.modelStyle: "dataclass" | "pydantic" | "plain"`. **`generate_code` does NOT have this option** — you must drive style via decorators / base classes / customCode.

### Enums

- `enums[]` produces a Python `Enum` subclass:
  ```python
  from enum import Enum
  class OrderStatus(Enum):
      Pending = 0
      Shipped = 2
  ```
- The `value` field on members is numeric per the schema (`"type": "number"`), so this is effectively `IntEnum`-shaped (numeric values), but the engine emits the regular `Enum` base. If you need `IntEnum` explicitly, use a class with `baseClassTypeIdentifier` pointing at a customFile that aliases IntEnum, or add a decorator/customCode workaround. For most DDD specs the default `Enum` with int values is fine.
- For string-valued enums, use `customFiles` with raw class code — the schema only supports numeric values for enum members.

### customCode bodies and method stubs

- **The engine does NOT auto-generate `pass` or `raise NotImplementedError` stubs.** Whatever you put in `code` is emitted verbatim.
- For abstract methods (in an interface / ABC class), write the signature only:
  ```jsonc
  {"code": "def find_by_id(self, id: str) -> Optional[$user]:\n    ...",
   "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
  ```
  Use `...` (Ellipsis) for an empty stub body — Python idiomatic; or `pass`; or `raise NotImplementedError`. Choose based on intent:
  - **Abstract / Protocol method** → `...` or `raise NotImplementedError`
  - **Concrete method placeholder for hand-edit** → `pass` or `raise NotImplementedError("TODO")`
- **Indentation**: per the AI guide ("Python — Must provide explicit indentation (4 spaces) after `\n` in customCode"). Auto-indent is NOT applied for Python multi-line code. Always include the leading 4 spaces inside method bodies:
  ```jsonc
  "code": "def total(self) -> Decimal:\n    return sum(item.price for item in self.items)"
  ```
  TypeScript and similar languages auto-indent; Python does not.
- **Decorators on methods** (e.g. `@property`, `@classmethod`, `@staticmethod`) are part of the `code` string — write them on a line preceding the `def`:
  ```jsonc
  "code": "@property\ndef full_name(self) -> str:\n    return f'{self.first} {self.last}'"
  ```
- **Type hints reference internal types via templateRefs**:
  ```jsonc
  "code": "def assign(self, user: $user) -> None:\n    self._owner = user",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
  ```

### customImports for Python

Only for external libraries. Examples:
```jsonc
"customImports": [
  {"path": "fastapi", "types": ["APIRouter", "Depends"]},
  {"path": "sqlalchemy.orm", "types": ["Session"]},
  {"path": "uuid", "types": ["UUID", "uuid4"]}
]
```
**Never** add `typing.*`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses`, `pydantic` (BaseModel, Field) — auto-imported.

### Constructor parameters in Python

The engine docs list C#/Java/Go/Groovy as the languages where constructor parameters auto-become properties. Python is **not** on that list, so the safest interpretation:

- For `@dataclass` classes, do **not** set `constructorParameters`; declare fields via `properties[]` and let the dataclass decorator synthesize `__init__`.
- For non-dataclass classes where you need an explicit `__init__`, write it via `customCode` (one block for the `__init__` method) rather than `constructorParameters`. This gives you full control over body assignments.

If you do use `constructorParameters` in Python, treat it as orthogonal to `properties[]` (i.e. don't duplicate names) and verify the output. The engine has a Python emitter, but the docs are silent on its exact behavior — when in doubt, prefer `customCode` for Python `__init__`.

### Comments / docstrings

- The `comment` field on a class/enum/property becomes a Python docstring (or `#` comment for properties; the exact form is driven by the emitter).
- Use `commentTemplateRefs` if a docstring needs to reference an internal type by resolved name.

---

## 5. Output Structure Produced

A single `generate_code` call produces a tree under `outputPath`:

```
<outputPath>/
└── <packageName>/                   # if packageName provided
    ├── __init__.py                  # engine-managed
    ├── <fileName>.py                # one per class/interface/enum/customFile
    └── <path>/                      # subdirectory if 'path' set on the def
        ├── __init__.py
        └── <fileName>.py
```

Files generated:
- One `.py` per class
- One `.py` per interface
- One `.py` per enum (snake_case filename, e.g. `order_status.py`)
- One `.py` per customFile
- **Zero** files for `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` (virtual types only)

Imports between files are auto-resolved when a `typeIdentifier` from the same batch is referenced (either directly in `properties` or via a `templateRefs` entry on customCode/properties/decorators).

### Response from `generate_code`

- When `dryRun: false` (default for real runs): files are written to disk; the response confirms file paths and counts.
- When `dryRun: true`: the response includes the file contents inline (use this for review before committing).

---

## 6. End-to-End Python Example (template for the next session)

```jsonc
{
  "language": "python",
  "packageName": "ordering_domain",
  "outputPath": "./src",
  "skipExisting": true,
  "dryRun": false,

  "enums": [{
    "name": "OrderStatus",
    "typeIdentifier": "order-status",
    "members": [
      {"name": "Pending", "value": 0},
      {"name": "Confirmed", "value": 1},
      {"name": "Shipped", "value": 2},
      {"name": "Delivered", "value": 3}
    ]
  }],

  "classes": [
    {
      "name": "Money",
      "typeIdentifier": "money",
      "decorators": [{"code": "@dataclass(frozen=True)"}],
      "properties": [
        {"name": "amount", "type": "Decimal"},
        {"name": "currency", "primitiveType": "String"}
      ]
    },
    {
      "name": "OrderItem",
      "typeIdentifier": "order-item",
      "decorators": [{"code": "@dataclass"}],
      "properties": [
        {"name": "product_id", "primitiveType": "String"},
        {"name": "quantity", "type": "int"},
        {"name": "unit_price", "typeIdentifier": "money"}
      ]
    },
    {
      "name": "Order",
      "typeIdentifier": "order",
      "decorators": [{"code": "@dataclass"}],
      "properties": [
        {"name": "id", "primitiveType": "String"},
        {"name": "status", "typeIdentifier": "order-status"},
        {"name": "created_at", "primitiveType": "Date"},
        {"name": "items", "typeIdentifier": "order-item-list"}
      ],
      "customCode": [
        {
          "code": "def total(self) -> Decimal:\n    return sum((i.unit_price.amount * i.quantity for i in self.items), Decimal('0'))"
        },
        {
          "code": "def confirm(self) -> None:\n    if self.status is not $status.Pending:\n        raise ValueError('Order must be Pending to confirm')\n    self.status = $status.Confirmed",
          "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
        }
      ]
    }
  ],

  "arrayTypes": [
    {"typeIdentifier": "order-item-list", "elementTypeIdentifier": "order-item"}
  ]
}
```

This produces (approximately):

```
src/ordering_domain/
├── __init__.py
├── order_status.py        # class OrderStatus(Enum)
├── money.py               # @dataclass(frozen=True) class Money
├── order_item.py          # @dataclass class OrderItem (imports Money)
└── order.py               # @dataclass class Order (imports OrderStatus, OrderItem; uses List[OrderItem])
```

---

## 7. Quick Decision Cheatsheet

| Need | Where it goes |
|------|---------------|
| Field with a type, no default | `properties[]` |
| Field with computed/initialized value | `customCode[]` (e.g. `"_cache: Dict[str, Any] = {}"`) |
| Method (concrete or abstract) | `customCode[]`, one per method |
| Class decorator (`@dataclass`, `@final`) | `decorators[]` on the class |
| Method decorator (`@property`, `@staticmethod`) | Inside the `code` string of the customCode block |
| Reference another generated type from a customCode body | `$placeholder` + `templateRefs` |
| Reference another generated type from a property type | `typeIdentifier` (simple) OR `type` + `templateRefs` (complex/generic) |
| Import an external library | `customImports[]` |
| Import stdlib / typing / pydantic / datetime / decimal / enum / abc / dataclasses | **Do nothing** — auto-imported |
| Define `List[Foo]` reusable alias | `arrayTypes[]` |
| Define `Dict[K,V]` reusable alias | `dictionaryTypes[]` |
| Define `Repository[User]` from a generic | `concreteGenericClasses[]` |
| Type alias (e.g. `UserId = str`) | `customFiles[]` with raw `code` |
| Optional field | `"isOptional": true` |
| Default-value initialized field | `"isInitializer": true` and/or use `customCode` |

---

## 8. Gotchas Specific to Python Generation

1. **Indentation must be explicit in customCode bodies.** Always prepend 4 spaces inside multi-line `code` strings. The engine auto-indents TS but NOT Python.
2. **No method-stub auto-bodies.** If you need `pass` or `raise NotImplementedError`, write it yourself in the `code`.
3. **`Number` ambiguity.** Decide per-field: `int` (raw `"type": "int"`), `float` (raw `"type": "float"` or `primitiveType: "Number"`), or `Decimal` (raw `"type": "Decimal"`, no customImport needed — `decimal` is auto).
4. **`Date` is `datetime.datetime`.** For date-only use `"type": "date"`.
5. **Enum values are integer-only** in the schema. For string enums use a `customFile`.
6. **No constructor-param auto-property** documented for Python — drive `__init__` via `@dataclass` decorator + `properties`, or write `__init__` manually in `customCode`.
7. **Snake_case everything**: `packageName`, `fileName`, property names, method names. The engine emits class names CamelCase as written but file names follow Python convention; if naming is critical, set `fileName` explicitly.
8. **Reserved words**: avoid `class`, `def`, `from`, `import`, `return`, `lambda`, `pass`, `global`, `nonlocal`, `yield`, `async`, `await` as identifier names.
9. **`I`-prefix on interface names**: the docs note TS strips `I` and C# preserves it. Python convention is `IFoo` or `FooProtocol` or just `Foo` (ABC). The engine doesn't strip prefixes for Python in the docs — write the name you want.
10. **Single MCP call**: every class / interface / enum / array-alias / dict-alias / generic-instantiation in the DDD spec must go into ONE `generate_code` call to get cross-file imports right.

---

## 9. Reference: Auto-imports for Python (NEVER add to customImports)

- `typing.*` — Optional, List, Dict, Tuple, Set, Any, Union, Callable, Generic, TypeVar, Protocol, etc.
- `pydantic` — BaseModel, Field
- `datetime` — datetime, date, time, timedelta, timezone
- `decimal` — Decimal
- `enum` — Enum, IntEnum, auto
- `abc` — ABC, abstractmethod
- `dataclasses` — dataclass, field, asdict, astuple

If you list any of the above in `customImports`, you'll get duplicate or conflicting imports.

---

## 10. Generation Workflow for the Next Session

1. Parse the DDD spec into entities, value objects, aggregates, repositories, services, enums.
2. Decide style: `@dataclass` for entities/VOs (default); raw classes with custom `__init__` for aggregates needing invariants in the constructor.
3. Build ONE `generate_code` call:
   - Set `language: "python"`, `packageName: "<snake_case>"`, `outputPath`, `skipExisting: true`.
   - Add all enums first (easy).
   - Add all value objects (Money, Email, etc.) with `@dataclass(frozen=True)`.
   - Add all entities with `@dataclass`.
   - Add aggregates with explicit invariants in `customCode`.
   - Add repository interfaces (abstract) — methods in `customCode` with `...` bodies.
   - Add domain services as plain classes with `customCode` methods.
   - Define `arrayTypes` and `dictionaryTypes` for any collection field.
   - Define `concreteGenericClasses` if any generic repositories/instances are used.
4. For every cross-type reference in a `customCode` body or complex `type` expression, use `$placeholder` + `templateRefs`.
5. **Test with `dryRun: true` first** to inspect the output without writing files. When satisfied, re-run with `dryRun: false`.
6. Hand-edit only files NOT regenerated (or set `skipExisting: true` to preserve them on re-runs).

---

End of warmup summary.
