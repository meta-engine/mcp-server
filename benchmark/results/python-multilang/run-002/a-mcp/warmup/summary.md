# MetaEngine MCP — Comprehensive Warmup Summary (Python Generation)

This is a self-contained reference compiled from the MetaEngine MCP `linkedResources`
(`metaengine://guide/ai-assistant`, `metaengine://guide/examples`), the `generate_code`
JSON Schema, and verified actual Python output from prior runs in
`results/20260426-034110-python/` and `results/20260426-035312-python/`.

The next session will NOT have access to the docs — everything needed to call
`mcp__metaengine__generate_code` correctly for **Python** is captured below.

---

## 1. What MetaEngine Is

A semantic code generator. You hand it a JSON description of types, relationships,
methods. It emits compilable source files with imports, cross-references, and
language idioms resolved automatically. ONE well-formed JSON call replaces dozens
of file writes.

Languages supported: typescript, python, go, csharp, java, kotlin, groovy, scala,
swift, php, rust.

---

## 2. Tools Exposed by the MCP Server

Three tools are relevant. Only `generate_code` and `load_spec_from_file` produce
files. `metaengine_initialize` returns docs only.

### 2.1 `mcp__metaengine__metaengine_initialize`
- Optional `language` param (enum: typescript, python, go, csharp, java, kotlin,
  groovy, scala, swift, php). Returns the same large markdown guide regardless,
  with no language-specific examples beyond a couple bullet points.
- Call this once per session if you need refresher docs. NOT required to run before
  generate_code.

### 2.2 `mcp__metaengine__generate_code` — THE primary tool
Full input schema (JSON):
```jsonc
{
  // Required
  "language": "python",                 // enum: typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php|rust

  // Optional top-level controls
  "packageName": "myapp",               // module/namespace prefix; for Python see §6
  "outputPath": ".",                    // directory for written files (default ".")
  "skipExisting": true,                 // default true — won't overwrite existing files (stub-friendly)
  "dryRun": false,                      // if true, returns file contents in response, writes nothing
  "initialize": false,                  // if true, properties get default value initialization

  // Type collections (any subset)
  "classes": [ ... ],                   // see §2.2.1
  "interfaces": [ ... ],                // same shape as classes
  "enums": [ ... ],                     // see §2.2.2
  "arrayTypes": [ ... ],                // virtual; no files
  "dictionaryTypes": [ ... ],           // virtual; no files
  "concreteGenericClasses": [ ... ],    // virtual; no files
  "concreteGenericInterfaces": [ ... ], // virtual; no files
  "customFiles": [ ... ]                // freeform files (type aliases, utilities)
}
```

#### 2.2.1 Class / Interface item shape
```jsonc
{
  "name": "OrderService",              // type name (PascalCase)
  "typeIdentifier": "order-service",   // unique key; OTHER items reference this
  "fileName": "order_service",         // optional override of filename (no extension)
  "path": "ordering/services",         // directory under outputPath
  "comment": "OrderService service.",  // becomes docstring (placed BEFORE class in Python)
  "isAbstract": false,
  "baseClassTypeIdentifier": "...",    // single inheritance
  "interfaceTypeIdentifiers": [...],   // array of interface type identifiers
  "decorators": [ {"code": "@something", "templateRefs": [...]} ],

  "constructorParameters": [
    {"name": "id",     "primitiveType": "String"},
    {"name": "items",  "typeIdentifier": "order-line-array"},
    {"name": "raw",    "type": "Dict[str, Any]"}      // free-form type string
  ],

  "properties": [
    {
      "name": "createdAt",             // camelCase input → snake_case in Python
      "primitiveType": "Date",         // OR typeIdentifier OR type
      "typeIdentifier": "user",        // reference another generated type
      "type": "List[$user]",           // free-form, supports $placeholder
      "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}],
      "isOptional": true,              // → Optional[T]
      "isInitializer": true,           // give it a default value
      "comment": "...",                // doc comment
      "decorators": [ ... ]
    }
  ],

  "customCode": [                      // ONE entry per method/initialized field
    {
      "code": "def find_by_email(self, email: str) -> Optional[$user]:\n    return None",
      "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
    }
  ],

  "customImports": [                   // ONLY for external libs — never stdlib
    {"path": "fastapi", "types": ["APIRouter", "Depends"]}
  ],

  "genericArguments": [                // makes class a generic template (Repository<T>)
    {
      "name": "T",
      "constraintTypeIdentifier": "base-entity",
      "propertyName": "items",         // creates a property of type T (or T[])
      "isArrayProperty": true
    }
  ]
}
```

#### 2.2.2 Enum item shape
```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "path": "ordering/enums",
  "fileName": "order_status",
  "comment": "OrderStatus enum.",
  "members": [
    {"name": "DRAFT",     "value": 0},
    {"name": "PLACED",    "value": 1},
    {"name": "CANCELLED", "value": 5}
  ]
}
```
Members **must** have integer `value`s. Python output uses `IntEnum`.

#### 2.2.3 arrayTypes / dictionaryTypes — virtual reference types
```jsonc
"arrayTypes": [
  {"typeIdentifier": "order-line-array", "elementTypeIdentifier": "order-line"},
  {"typeIdentifier": "string-array",     "elementPrimitiveType": "String"}
],
"dictionaryTypes": [
  {"typeIdentifier": "scores",     "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-by-id", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
]
```
NO files generated. Reference these by `typeIdentifier` in another type's properties.

#### 2.2.4 concreteGenericClasses / concreteGenericInterfaces
```jsonc
"concreteGenericClasses": [
  {
    "identifier": "user-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{"typeIdentifier": "user"}]
  }
]
```
NO files generated. Creates a virtual `Repository[User]` type for `baseClassTypeIdentifier`
references or templateRef placeholders.

#### 2.2.5 customFiles — freeform file (no class wrapper)
```jsonc
"customFiles": [{
  "name": "types",                     // file basename (no extension)
  "path": "shared",
  "identifier": "shared-types",        // optional — lets other files import via this id
  "fileName": "types",                 // optional override
  "customCode": [
    {"code": "UserId = str"},
    {"code": "Status = Literal['active', 'inactive']"}
  ],
  "customImports": [...]
}]
```

### 2.3 `mcp__metaengine__load_spec_from_file`
Loads the same spec (identical schema) from a JSON file on disk:
```jsonc
{ "specFilePath": "specs/user-system.json", "outputPath": "src", "dryRun": false }
```
Use this when the spec is large to avoid context bloat.

### 2.4 Other MCP tools available (NOT for code generation)
`generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` — convert
specs to/from those formats. Not needed for DDD → Python code generation.

---

## 3. Critical Rules (memorize — these cause the most failures)

### Rule 1 — ONE call generates everything that cross-references
`typeIdentifier` references resolve **only within the current `generate_code` call**.
If `OrderService` references `Order`, both must be in the same call. Splitting into
multiple calls breaks imports.

### Rule 2 — `properties[]` declares fields. `customCode[]` does everything else.
- `properties[]`: type-only declarations, no logic, no initialization.
- `customCode[]`: methods, initialized fields, anything with code. **One entry =
  exactly one member.**

### Rule 3 — Internal types in `customCode` MUST use `templateRefs`
Without templateRefs, MetaEngine cannot generate the import. Pattern:
```jsonc
{
  "code": "def get_user(self, id: str) -> $user:\n    raise NotImplementedError",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```
Same applies to `properties.type`, `properties.decorators`, `decorators`, etc.

### Rule 4 — Never auto-import stdlib in `customImports`
For Python, MetaEngine auto-imports: **typing.\***, **pydantic** (BaseModel, Field),
**datetime**, **decimal**, **enum**, **abc**, **dataclasses**.

Use `customImports` only for external libs (fastapi, sqlalchemy, pytest, etc.).

### Rule 5 — `templateRefs` are ONLY for internal types in this batch
External types: use `customImports`. Internal types: use `templateRefs` /
`typeIdentifier`. Never mix.

### Rule 6 — Constructor parameter duplication causes errors (C#/Java/Go/Groovy)
Per the docs, in **C#/Java/Go/Groovy** constructor parameters auto-create properties;
duplicating them in `properties[]` throws "Sequence contains more than one matching
element". Python is NOT explicitly listed in this rule, but actual Python output
shows `__init__` is built from `constructorParameters` — DO NOT duplicate names
in `properties[]` to be safe.

### Rule 7 — Virtual types never produce files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`
exist only as references. They produce no Python file.

### Rule 8 — Reserved word avoidance
Don't use Python keywords as property names: `class`, `from`, `import`, `def`,
`return`, `lambda`, `pass`, `is`, `in`, `not`, `and`, `or`, `del`, `global`,
`nonlocal`, `raise`, `try`, `except`, `finally`, `with`, `yield`, `async`,
`await`. Use safe alternatives (`klass` for `class`, `module` for `import`).

---

## 4. Output Structure (verified from real Python runs)

### File path layout
```
<outputPath>/<class.path>/<snake_case_filename>.py
```
- The `name` field (PascalCase like `OrderService`) becomes the class name AS-IS.
- The filename is derived as **snake_case** of `name` UNLESS overridden via `fileName`.
- Subdirectories are taken literally from `path`. Dot-separated paths are NOT used —
  use `/` (e.g. `"path": "ordering/services"`).
- **No `__init__.py` files are auto-generated.** If you need them as Python packages,
  create them via `customFiles` or write them yourself afterwards.

### Verified example
Spec: `{"name": "OrderService", "typeIdentifier": "order-service", "path": "ordering/services"}`
File: `<outputPath>/ordering/services/order_service.py`

### Module / import naming
Inter-file imports use the `path` as a dotted module path, with snake_case file basename:
```python
from ordering.aggregates.order import Order
```
**`packageName` is NOT prefixed onto these import paths in observed Python output.**
If you set `outputPath="."` and `path="ordering/aggregates"`, the import will be
`from ordering.aggregates.order import Order`, not `from <packageName>.ordering.aggregates...`.
Plan your `outputPath` so this dotted path is importable from your project root.

---

## 5. Python Type Mapping (verified from output files)

| Spec primitiveType | Python type generated      | Import added (auto)                |
|--------------------|----------------------------|------------------------------------|
| `String`           | `str`                      | (none)                             |
| `Number`           | `float`                    | (none) — **NOT `int`**             |
| `Boolean`          | `bool`                     | (none)                             |
| `Date`             | `datetime`                 | `from datetime import datetime`    |
| `Any`              | `Any`                      | `from typing import Any`           |

| Spec construct                                 | Python type                          |
|------------------------------------------------|--------------------------------------|
| `arrayTypes` (element ref)                     | `List[Element]`                      |
| `dictionaryTypes` (key/value)                  | `Dict[Key, Value]`                   |
| `isOptional: true`                             | `Optional[T]`                        |
| Free-form `Dict[str, Any]` in `type`           | passed through verbatim              |
| `concreteGenericClasses` for `Repository<User>`| `Repository[User]` (inline)          |

`typing` imports (`Any`, `Dict`, `List`, `Optional`) are added automatically when used.

### Property name conversion
camelCase / PascalCase property names are auto-converted to **snake_case** in Python
output. Example: spec property `createdAt` → Python `self.created_at`. The original
case is preserved only inside method names you write yourself in `customCode`.

If you want exact control of attribute names in Python, write them snake_case in
the spec.

---

## 6. `packageName` for Python

The `generate_code` schema notes per-language defaults: Go uses
`github.com/metaengine/demo`; Java/Kotlin/Groovy use `com.metaengine.generated`;
C# omits namespace when empty. **Python has no documented default and no observed
prefix in generated import paths.**

Practical guidance:
- `packageName` may be safely OMITTED for Python.
- If included, treat it as a project-level identifier — do not expect MetaEngine
  to prepend it onto import statements.
- Inter-file imports come from `class.path` joined with `/` and the snake_case
  filename — design these so they form a valid Python dotted module path from
  whatever Python sys.path root you intend (typically `outputPath` or one level
  above it).

---

## 7. Class Style: NOT pydantic, NOT dataclass — plain classes

The docs list `pydantic` and `dataclasses` as **available** auto-imports for Python,
but verified output shows MetaEngine emits **plain Python classes** by default:

```python
from datetime import datetime

"""Order aggregate root for the ordering domain."""
class Order:
    def __init__(self, id: str, created_at: datetime, updated_at: datetime, name: str, description: str):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = name
        self.description = description
```

Notes:
- No `@dataclass` decorator emitted automatically.
- No `BaseModel` inheritance.
- The `comment` field becomes a triple-quoted string placed **before** `class`
  (not as a docstring inside the class — this is unusual but is how MetaEngine
  emits it).
- Constructor body assigns each parameter to `self.<name>`.
- An empty trailing newline is left at the end of file.

If you want `@dataclass` or pydantic models, add them explicitly via `decorators`
and `customImports`, e.g.:
```jsonc
"decorators": [{"code": "@dataclass"}],
"customImports": [{"path": "dataclasses", "types": ["dataclass"]}]
```
(Treat dataclasses/pydantic as opt-in, NOT default.)

---

## 8. Enums in Python

```python
from enum import IntEnum

"""OrderStatus enum."""
class OrderStatus(IntEnum):
    DRAFT = 0
    PLACED = 1
    PAID = 2
    SHIPPED = 3
    DELIVERED = 4
    CANCELLED = 5
```

- Always `IntEnum`. Members must have integer `value`s in the spec.
- `from enum import IntEnum` is auto-added.
- File path follows the same `path`/snake_case rules.
- Cannot generate `Enum` (str-valued) or `Flag` enums via this primitive — would
  need a `customFile` for that.

---

## 9. Methods, Stubs, and `customCode` for Python

### 9.1 Stub method bodies
For service interfaces / not-yet-implemented methods, the convention seen in
verified output is:
```python
def find_by_id(self, id: str) -> Optional[Order]:
    raise NotImplementedError('not implemented')
```
This is **what you must emit yourself in `customCode.code`** — MetaEngine does NOT
insert a default stub. Pattern:
```jsonc
{
  "code": "def find_by_id(self, id: str) -> Optional[$order]:\n    raise NotImplementedError('not implemented')",
  "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
}
```

### 9.2 Indentation rule (Python-specific)
Per the docs: **you must include explicit 4-space indentation after `\n` in
customCode for Python.** Other languages auto-indent; Python does not.

Wrong: `"def foo(self):\nreturn 1"` → emits invalid Python.
Right: `"def foo(self):\n    return 1"`.

### 9.3 Method signature anatomy
- `self` is your responsibility — write it in the code string.
- Type hints reference `$placeholder` for internal types, plain identifiers for
  stdlib types (typing.* etc. are auto-imported).
- One `customCode` entry per method. Multiple entries get blank-line separation
  in output.

### 9.4 Initialized fields vs properties
- Uninitialized type declaration → `properties[]` with `name`+`primitiveType`/
  `typeIdentifier`/`type`.
- Field with default value or computed init → `customCode[]`:
  `{"code": "items: List[$user] = []", "templateRefs": [...]}`.
  In Python this lands as a class-level attribute, not in `__init__`.

### 9.5 Interface method signatures
Python doesn't have native interfaces. MetaEngine `interfaces` map roughly to
ABCs. To declare an interface method, prefer `customCode` with the `@abstractmethod`
decorator pattern (you'd add `from abc import ABC, abstractmethod`, but those are
auto-imported per the docs):
```jsonc
{
  "code": "@abstractmethod\ndef find_all(self) -> List[$user]:\n    ...",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

---

## 10. Common Gotchas Specific to Python

1. **Number maps to `float`, not `int`.** If you need `int` IDs, use
   `"type": "int"` rather than `"primitiveType": "Number"`.
2. **No `__init__.py` files** are emitted. Add them post-hoc or via `customFiles`
   if Python package semantics are needed.
3. **packageName has no observed effect on imports.** Don't rely on it for
   dotted-module rooting.
4. **Property names are snake_cased** automatically. `createdAt` → `created_at`.
   Methods you write inside `customCode` are NOT auto-converted.
5. **Indentation in customCode is your responsibility.** Always use 4 spaces
   after `\n` in Python `customCode.code`.
6. **No default stub bodies.** Every method body must be present in your `code`
   string; otherwise you get a syntax error.
7. **Doc comments land before the `class` keyword**, not as a docstring inside.
   This is functional but unusual — don't fight it.
8. **Plain classes by default** — opt into `@dataclass`/pydantic explicitly via
   `decorators` + `customImports` if desired.
9. **Don't reference unknown `typeIdentifier`s** — silently dropped, no error.
10. **`primitiveType` enum is exactly: `String | Number | Boolean | Date | Any`.**
    Anything else goes in `type` as a free-form string.

---

## 11. Worked Example — Python DDD Bounded Context

Spec snippet (the kind of input the next session will assemble):
```jsonc
{
  "language": "python",
  "outputPath": "output",
  "skipExisting": true,
  "enums": [
    {
      "name": "OrderStatus",
      "typeIdentifier": "order-status",
      "path": "ordering/enums",
      "comment": "Lifecycle states for an order.",
      "members": [
        {"name": "DRAFT",   "value": 0},
        {"name": "PLACED",  "value": 1},
        {"name": "SHIPPED", "value": 2}
      ]
    }
  ],
  "classes": [
    {
      "name": "OrderLine",
      "typeIdentifier": "order-line",
      "path": "ordering/value_objects",
      "comment": "OrderLine value object.",
      "constructorParameters": [
        {"name": "sku",      "primitiveType": "String"},
        {"name": "quantity", "primitiveType": "Number"},
        {"name": "price",    "primitiveType": "Number"}
      ]
    },
    {
      "name": "Order",
      "typeIdentifier": "order",
      "path": "ordering/aggregates",
      "comment": "Order aggregate root.",
      "constructorParameters": [
        {"name": "id",         "primitiveType": "String"},
        {"name": "created_at", "primitiveType": "Date"},
        {"name": "status",     "typeIdentifier": "order-status"}
      ],
      "properties": [
        {"name": "lines", "typeIdentifier": "order-line-array"}
      ],
      "customCode": [
        {
          "code": "def add_line(self, line: $line) -> None:\n    self.lines.append(line)",
          "templateRefs": [{"placeholder": "$line", "typeIdentifier": "order-line"}]
        }
      ]
    },
    {
      "name": "OrderService",
      "typeIdentifier": "order-service",
      "path": "ordering/services",
      "comment": "OrderService.",
      "customCode": [
        {
          "code": "def create(self, input: Dict[str, Any]) -> $order:\n    raise NotImplementedError('not implemented')",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
        },
        {
          "code": "def find_by_id(self, id: str) -> Optional[$order]:\n    raise NotImplementedError('not implemented')",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
        },
        {
          "code": "def list(self, limit: int) -> List[$order]:\n    raise NotImplementedError('not implemented')",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
        }
      ]
    }
  ],
  "arrayTypes": [
    {"typeIdentifier": "order-line-array", "elementTypeIdentifier": "order-line"}
  ]
}
```

Expected output files:
- `output/ordering/enums/order_status.py`
- `output/ordering/value_objects/order_line.py`
- `output/ordering/aggregates/order.py`
- `output/ordering/services/order_service.py`

Each with auto-imports (`datetime`, `IntEnum`, `typing.*`) and cross-file imports
generated based on `path` + snake_case basename.

---

## 12. Cheat-Sheet for the Generation Session

Before each `generate_code` call:
1. **Single-call check** — every `typeIdentifier` referenced anywhere must be
   defined in the same call (in `classes`, `interfaces`, `enums`, `arrayTypes`,
   `dictionaryTypes`, or `concreteGeneric*`).
2. **Path + filename** — set `path` to a slash-separated relative dir; trust the
   engine to snake_case the filename from `name`.
3. **Property vs customCode** — fields with no logic → `properties`; everything
   else → `customCode` (one item per member).
4. **TemplateRefs** — every internal type referenced inside a `code` string OR a
   free-form `type` string MUST have a matching entry in `templateRefs`.
5. **Indentation** — every `\n` in a Python `code` string must be followed by
   4 spaces of indentation if the next line is inside a function body.
6. **Stub bodies** — explicitly write
   `raise NotImplementedError('not implemented')` for unimplemented methods.
7. **Don't duplicate** constructor parameter names in `properties`.
8. **Don't customImport** stdlib (typing, datetime, enum, abc, dataclasses,
   decimal, pydantic) — they're auto-imported.
9. **Don't expect** `packageName` to prefix Python imports.
10. **Don't expect** `__init__.py` files — write them yourself if needed.

---

## 13. Reference: Auto-imported Python modules

The following are added automatically when used by MetaEngine — never list them
in `customImports`:

- `typing.*` — `Any`, `Dict`, `List`, `Optional`, `Union`, `Tuple`, `Callable`, `Literal`, ...
- `datetime` — `datetime`, `date`, `time`, `timedelta`
- `decimal` — `Decimal`
- `enum` — `Enum`, `IntEnum`, `Flag`, `auto`
- `abc` — `ABC`, `abstractmethod`
- `dataclasses` — `dataclass`, `field`
- `pydantic` — `BaseModel`, `Field`

Anything outside the stdlib (fastapi, sqlalchemy, pytest, requests, etc.) goes
in `customImports`.
