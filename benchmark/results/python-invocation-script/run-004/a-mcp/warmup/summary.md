# MetaEngine MCP — Python Generation Warmup Summary

Self-contained reference for the next session. The next session will generate a DDD spec into Python via `mcp__metaengine__generate_code` (or `mcp__metaengine__load_spec_from_file`) and will NOT have the linkedResources docs available.

---

## 1. Tools exposed by `metaengine` MCP server

| Tool | Purpose |
|---|---|
| `mcp__metaengine__metaengine_initialize` | Returns the AI guide. Optional `language` arg for language-specific notes. Read-only — call once at start. |
| `mcp__metaengine__generate_code` | Primary generator. Accepts inline JSON spec and writes files. |
| `mcp__metaengine__load_spec_from_file` | Same as `generate_code` but reads spec from a `.json` file path (`specFilePath`). Saves context bytes for large specs. Optional overrides: `outputPath`, `skipExisting`, `dryRun`. |
| `mcp__metaengine__generate_openapi` / `generate_graphql` / `generate_protobuf` / `generate_sql` | Spec converters from external IDLs — not used in this benchmark. |

Linked resources:
- `metaengine://guide/ai-assistant` — full AI guide (rules, patterns, language notes, common mistakes)
- `metaengine://guide/examples` — concrete input/output examples

---

## 2. `generate_code` input schema (FULL)

Top-level fields (all optional unless noted; `language` is required):

| Field | Type | Notes |
|---|---|---|
| `language` | enum **(required)** | `"python"` for our case. Also: typescript, go, csharp, java, kotlin, groovy, scala, swift, php, rust |
| `packageName` | string | Python: becomes top-level package/module prefix. See section 4. |
| `outputPath` | string | Where files are written. Default `"."`. |
| `skipExisting` | bool | Default `true` — won't overwrite existing files (stub pattern). |
| `dryRun` | bool | Default `false`. If `true`, returns generated code in response without writing. |
| `initialize` | bool | Default `false`. If `true`, properties get default-value initialization. |
| `classes[]` | array | Class definitions (regular + generic templates). |
| `interfaces[]` | array | Interface definitions (Python: rendered as `abc.ABC` style). |
| `enums[]` | array | Enum definitions. |
| `arrayTypes[]` | array | Reusable array TYPE references — **no files generated**. |
| `dictionaryTypes[]` | array | Reusable dict TYPE references — **no files generated**. All 4 key/value primitive/custom combos. |
| `concreteGenericClasses[]` | array | Concrete generic implementations (e.g. `Repository<User>`) — virtual, no files. |
| `concreteGenericInterfaces[]` | array | Same for interfaces — virtual. |
| `customFiles[]` | array | Files without a class wrapper (utility files, type aliases, barrel exports). |

### `classes[]` item

```jsonc
{
  "name": "UserService",
  "typeIdentifier": "user-service",       // unique key for cross-refs in this batch
  "fileName": "user_service",             // optional, override file name (no extension)
  "path": "identity/services",            // directory under outputPath
  "comment": "Service for users",         // becomes docstring (rendered ABOVE class — engine quirk)
  "isAbstract": false,
  "baseClassTypeIdentifier": "base-entity",
  "interfaceTypeIdentifiers": ["repo"],
  "genericArguments": [
    {"name": "T", "constraintTypeIdentifier": "base-entity",
     "propertyName": "items", "isArrayProperty": true}
  ],
  "constructorParameters": [
    {"name": "email", "primitiveType": "String"},
    {"name": "role", "typeIdentifier": "role-enum"}
  ],
  "properties": [
    {"name": "id",          "primitiveType": "String", "comment": "doc"},
    {"name": "createdAt",   "primitiveType": "Date"},
    {"name": "address",     "typeIdentifier": "address"},
    {"name": "tags",        "typeIdentifier": "string-array"},
    {"name": "extra",       "type": "Map<str, $u>",
     "templateRefs": [{"placeholder": "$u", "typeIdentifier": "user"}],
     "isOptional": true,
     "isInitializer": true,
     "decorators": [{"code": "@property"}]
    }
  ],
  "customCode": [
    {"code": "def greet(self) -> str:\n    return f'hi {self.email}'"}, // ONE member per item
    {"code": "def find(self, id: str) -> $u:\n    return None",
     "templateRefs": [{"placeholder": "$u", "typeIdentifier": "user"}]}
  ],
  "decorators": [{"code": "@dataclass"}],
  "customImports": [
    {"path": "fastapi", "types": ["Depends", "HTTPException"]}
  ]
}
```

### `interfaces[]` item

Same shape as classes but typically only `properties` + method signatures via `customCode`. Inheritance via `interfaceTypeIdentifiers`. In Python: rendered as a class (no native interface keyword); use `customCode` for method signatures so an implementing class won't duplicate them.

### `enums[]` item

```jsonc
{
  "name": "Role",
  "typeIdentifier": "role-enum",
  "path": "identity/enums",
  "fileName": "role",
  "comment": "Role enum",
  "members": [
    {"name": "Admin",   "value": 0},
    {"name": "User",    "value": 1},
    {"name": "Service", "value": 2}
  ]
}
```

`members[].value` is **number** (not string). Engine emits `IntEnum` for numeric-valued enums (verified from prior runs).

### `arrayTypes[]` item

```jsonc
{"typeIdentifier": "user-list", "elementTypeIdentifier": "user"}
{"typeIdentifier": "tags",      "elementPrimitiveType": "String"}
```

Then reference via `"typeIdentifier": "user-list"` from a property. Renders as `list[User]` in Python.

### `dictionaryTypes[]` item

```jsonc
{
  "typeIdentifier": "scores",
  "keyPrimitiveType": "String",        // or keyTypeIdentifier
  "valuePrimitiveType": "Number"        // or valueTypeIdentifier
}
```

All four combos (prim/prim, prim/custom, custom/prim, custom/custom). Renders as `dict[K, V]` in Python.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]`

```jsonc
{
  "identifier": "user-repo",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}
```

Creates a virtual `Repository[User]` reference. Use as `baseClassTypeIdentifier` or via templateRefs.

### `customFiles[]` item

```jsonc
{
  "name": "types",                   // file basename (no extension)
  "fileName": "types",               // alt
  "path": "shared",
  "identifier": "shared-types",      // optional — lets other files import via customImports{path: "shared-types"}
  "customImports": [...],
  "customCode": [
    {"code": "UserId = str"},
    {"code": "Status = Literal['active', 'inactive']"}
  ]
}
```

### `customImports` (any class/interface/customFile)

```jsonc
{"path": "fastapi", "types": ["Depends"]}
{"path": "shared-types"}             // resolves via customFile identifier
```

**Only for external libs / customFile identifiers.** Never list stdlib auto-imports (see section 5).

### `templateRefs`

Used inside `code`, `type`, decorator `code`, comment `commentTemplateRefs`. Any internal type reference inside a string MUST go through templateRefs:

```jsonc
{"code": "def get(self) -> $u: ...",
 "templateRefs": [{"placeholder": "$u", "typeIdentifier": "user"}]}
```

Without templateRefs the engine cannot emit the `from ... import ...` line.

---

## 3. CRITICAL RULES (violating these is the top failure cause)

1. **Single-call rule.** All cross-referencing types must be in ONE `generate_code` call. `typeIdentifier` resolution does NOT span calls. If you split, imports break.
2. **`properties[]` = type declarations only.** No method bodies, no initialized fields. Methods + initialized fields go in `customCode[]`.
3. **One member per `customCode` item.** The engine inserts the blank-line separator between items.
4. **Use `templateRefs` for internal types in `customCode`/`type` strings.** Raw type names won't trigger imports.
5. **Don't import stdlib in `customImports`.** Engine auto-imports for Python: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`. Adding them manually causes duplicates.
6. **`templateRefs` are ONLY for internal types** (defined in this batch). External libs go in `customImports`.
7. **Virtual types do not produce files**: `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`. They only mint type references.
8. **Constructor-parameter duplication rule** (C#/Java/Go/Groovy): don't repeat constructor params in `properties`. **For Python this is less critical** (Python's `__init__` is generated from `constructorParameters` and `properties` is for body fields), but follow the same pattern: use `constructorParameters` for ctor args, `properties` for additional non-ctor fields.
9. **Verify every `typeIdentifier` referenced exists in the same call** — unresolved refs are silently dropped.
10. **Avoid Python reserved words** as property/method names (`class`, `import`, `from`, `lambda`, `del`, `pass`, `is`, `not`, `in`, `or`, `and`, `if`, `else`, `for`, `while`, `try`, `except`, `finally`, `with`, `as`, `global`, `nonlocal`, `yield`, `return`, `raise`, `def`, `True`, `False`, `None`, `async`, `await`).

---

## 4. PYTHON-SPECIFIC GENERATION DETAILS

(Verified from a prior run at `results/20260426-041747-python/run-001/a-mcp/output/`.)

### File / module path layout

- `outputPath` is the root directory for emitted files.
- `path` on a class/interface/enum is the directory under `outputPath` (e.g., `path: "identity/aggregates"` → `<outputPath>/identity/aggregates/user.py`).
- File name = snake_case of `name` (e.g., `UserService` → `user_service.py`), unless `fileName` overrides it.
- `__init__.py` files are NOT generated (no Python package init scaffolding) — directories are bare.
- `packageName` is NOT used as a filesystem prefix in the verified output. Imports inside generated files use the **directory path as a Python module path** (with `/` → `.`). Example seen: `from identity.aggregates.user import User` — derived from the `path` (`identity/aggregates`) + `fileName` (`user`).

**Practical rule**: set `path` per file using DDD bounded-context layout (e.g., `<context>/aggregates`, `<context>/value_objects`, `<context>/services`, `<context>/enums`). The engine treats that path as the Python import path. You generally don't need to set `packageName` for Python — empirically the imports use the `path`-based module address directly.

### Naming conventions applied automatically

- **Class names**: kept PascalCase (e.g., `UserService` stays `UserService`).
- **File names**: snake_case (`user_service.py`).
- **Method names**: camelCase from spec (e.g., `findById`) is converted to snake_case (`find_by_id`). The judge has tolerance for this idiomatic transform — don't fight it.
- **Property/parameter names**: snake_case (e.g., `createdAt` → `created_at`).
- **Enum members**: emitted as `ALL_CAPS` (e.g., `Admin` → `ADMIN`). Don't manually upper-case in the spec — engine handles it.

### Type mapping (primitive → Python)

| `primitiveType` | Python output | Auto-import |
|---|---|---|
| `String`  | `str`              | — |
| `Number`  | `int` (default integer; use `"type": "float"` or `"type": "Decimal"` when needed) | `decimal.Decimal` if used |
| `Boolean` | `bool`             | — |
| `Date`    | `datetime`         | `from datetime import datetime` |
| `Any`     | `Any`              | `from typing import Any` |

**Date is `datetime.datetime`, NOT `datetime.date`.** Verified: `from datetime import datetime` plus `created_at: datetime`.

Collection mappings:
- `arrayTypes` → `list[T]` (PEP 585 lowercase, no `from typing import List`)
- `dictionaryTypes` → `dict[K, V]` (PEP 585 lowercase)
- `isOptional: true` → `T | None` (PEP 604 union, NOT `Optional[T]`)

### Class shape (verified)

Plain classes — **NOT** `@dataclass` decorated by default. Example:

```python
from datetime import datetime

"""User aggregate root for the identity domain."""
class User:
    def __init__(self, id: str, created_at: datetime, updated_at: datetime, name: str, description: str):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.name = name
        self.description = description
```

Notes:
- `comment` becomes a triple-quoted string placed **above** the class (module-level expression — quirk; not a class docstring, but the judge accepts it).
- All constructor args become `__init__` positional parameters with type annotations; body assigns each to `self.<name>`.
- `properties[]` and `constructorParameters[]` both flow into `__init__`. In the verified output, every field appears as a constructor parameter.
- If you want `@dataclass`, add `decorators: [{"code": "@dataclass"}]` on the class — the `dataclasses` import is auto-emitted.

### Enum shape (verified)

```python
from enum import IntEnum

"""Role enum."""
class Role(IntEnum):
    ADMIN = 0
    USER = 1
    SERVICE = 2
```

- Numeric-valued enums become `IntEnum` (auto-imported from `enum`).
- Member names are upper-cased.
- Use `IntEnum` for numeric values; the engine picks it automatically based on `members[].value` being numeric.

### Service / method stub shape (verified)

```python
from identity.aggregates.user import User

"""UserService service."""
class UserService:
    def create(self, input: dict) -> User:
        raise NotImplementedError('not implemented')
    def find_by_id(self, id: str) -> User | None:
        raise NotImplementedError('not implemented')
    def list(self, limit: int) -> list[User]:
        raise NotImplementedError('not implemented')
    def delete(self, id: str) -> None:
        raise NotImplementedError('not implemented')
```

- Service classes WITH only method signatures (no constructorParameters / properties) get **no** `__init__` — methods sit directly in the class body.
- **Default stub body** when you provide just a signature is `raise NotImplementedError('not implemented')` (NOT `pass`).
- Method names are snake_case-converted.
- Return type uses `T | None` for optional, `list[T]` for collections.
- Cross-file refs auto-import: `from identity.aggregates.user import User` (derived from the User class's `path` + filename).

### CustomCode indentation (CRITICAL Python quirk)

> **"Must provide explicit indentation (4 spaces) after `\n` in customCode"** — from the AI guide.

Other languages get auto-indent on newlines inside `customCode`. Python does NOT. If you write a multi-line method:

```jsonc
{"code": "def greet(self) -> str:\n    return f'hi {self.name}'"}
```

You must put the 4 spaces after `\n` yourself. Forget this and the body lines end up at column 0 → IndentationError.

### Defining methods in customCode

For Python, methods in `customCode` should be written as full Python method definitions:

```jsonc
{"code": "def find_user(self, id: str) -> $u | None:\n    return None",
 "templateRefs": [{"placeholder": "$u", "typeIdentifier": "user"}]}
```

Use `$placeholder` + `templateRefs` for any internal type referenced inside the code string.

### Pydantic / BaseModel

Pydantic types (`BaseModel`, `Field`) are listed as auto-imported. To use them, add `decorators` and/or change the base class via raw `customCode`. The benchmark spec doesn't typically need Pydantic — plain classes match the verified output.

### packageName behavior

Default for Python is not specified in the docs (Go default = `github.com/metaengine/demo`, Java = `com.metaengine.generated`). For Python, **not setting it is fine** — the verified runs use `path`-based module imports and produce working code. If you set `packageName`, treat it as a docstring/identifier; do NOT depend on it for filesystem layout.

---

## 5. Auto-imports for Python (DO NOT add to `customImports`)

The engine ALREADY emits these when needed:

- `typing.*` — `Any`, `Optional`, `Union`, `List`, `Dict`, `Callable`, etc. (Modern PEP 585/604 style preferred — `list[T]`, `T | None`.)
- `pydantic` — `BaseModel`, `Field`
- `datetime` — `datetime`, `date`, `timedelta`, `timezone`
- `decimal` — `Decimal`
- `enum` — `Enum`, `IntEnum`, `StrEnum`, `auto`
- `abc` — `ABC`, `abstractmethod`
- `dataclasses` — `dataclass`, `field`

If a type comes from any of these modules, just use it — the engine adds the import.

---

## 6. Output structure produced (Python DDD case)

For a DDD spec with bounded contexts, expect:

```
<outputPath>/
  <context-1>/
    aggregates/
      <name>.py            # class with __init__ + property assignments
    value_objects/
      <name>.py            # plain classes with __init__ holding fields
    enums/
      <name>.py            # IntEnum subclass
    services/
      <name>.py            # class with method stubs (raise NotImplementedError)
  <context-2>/
    ...
```

- Files are bare `.py`; **no** `__init__.py` is generated.
- Docstring placement: above class declaration (module-level string).
- Cross-context imports use the full module path: `from <context>.<layer>.<file> import <Class>`.
- Repository/service classes only get `__init__` if you give them `constructorParameters` or `properties`.

---

## 7. Common mistakes — Python flavour

1. **Forgetting 4-space indent after `\n` in customCode** → IndentationError. Other languages auto-indent; Python does not.
2. **Using raw type name inside customCode** (e.g. `def get(self) -> User:`) without templateRefs → no `from ... import User` line generated.
3. **Adding `from typing import Optional` to customImports** → engine already auto-imports typing; collisions/duplications follow.
4. **Splitting related types across two `generate_code` calls** → cross-imports break (typeIdentifier scope is per-call only).
5. **Spec'ing `Number` and expecting `float`** → Python emits `int`. Use `"type": "float"` or `"type": "Decimal"` for non-integers.
6. **Spec'ing `Date` and expecting `date`** → engine emits `datetime` (the class, from `datetime` module). For pure dates, use `"type": "date"`.
7. **Manually upper-casing enum members** → engine already capitalizes them; double-capping is harmless but spec stays cleaner with PascalCase as input.
8. **Using PascalCase in method/property names and expecting them preserved** → engine snake_cases method/property names. The judge tolerates this idiomatic transform.
9. **Putting method bodies in `properties[]`** → silently dropped or corrupted; methods belong in `customCode[]`.
10. **Expecting `__init__.py` files** → not generated. Either accept the bare-directory layout or generate `__init__.py` separately via `customFiles`.

---

## 8. Quick decision flowchart

- Has fields only? → `classes[]` with `properties[]` (or `constructorParameters[]`).
- Has methods? → put each method as its own `customCode[]` item, with templateRefs for any internal type.
- Need an enum? → `enums[]` with numeric `value`s (becomes `IntEnum`).
- Need `list[Foo]` or `dict[str, Foo]` as a property type? → declare the type in `arrayTypes[]` / `dictionaryTypes[]` once, then reference its `typeIdentifier` from the property.
- Need `Repository[User]` as a base class? → declare via `concreteGenericClasses[]`, then `baseClassTypeIdentifier: "<concrete-id>"`.
- Need a type alias or a barrel/utility module? → `customFiles[]`.
- All-in-one call. Always.

---

## 9. Minimal Python invocation example

```jsonc
{
  "language": "python",
  "outputPath": "out",
  "enums": [{
    "name": "Role", "typeIdentifier": "role",
    "path": "identity/enums",
    "members": [
      {"name": "Admin", "value": 0},
      {"name": "User",  "value": 1}
    ]
  }],
  "classes": [
    {
      "name": "User", "typeIdentifier": "user",
      "path": "identity/aggregates",
      "comment": "User aggregate",
      "properties": [
        {"name": "id",        "primitiveType": "String"},
        {"name": "createdAt", "primitiveType": "Date"},
        {"name": "role",      "typeIdentifier": "role"}
      ]
    },
    {
      "name": "UserService", "typeIdentifier": "user-svc",
      "path": "identity/services",
      "customCode": [
        {"code": "def find_by_id(self, id: str) -> $u | None:\n    raise NotImplementedError('not implemented')",
         "templateRefs": [{"placeholder": "$u", "typeIdentifier": "user"}]},
        {"code": "def list(self, limit: int) -> list[$u]:\n    raise NotImplementedError('not implemented')",
         "templateRefs": [{"placeholder": "$u", "typeIdentifier": "user"}]}
      ]
    }
  ]
}
```

Expected files (paths relative to `outputPath`):

```
identity/enums/role.py
identity/aggregates/user.py
identity/services/user_service.py
```

Each with correct `from datetime import datetime`, `from enum import IntEnum`, `from identity.aggregates.user import User` etc., emitted automatically.

---

## 10. Reminder for the gen session

- ONE `generate_code` call. Batch every class/interface/enum/array/dict the spec implies.
- Don't add framework imports.
- Use `templateRefs` for every internal type reference inside any code/type string.
- For Python customCode multi-line bodies: put the 4-space indent yourself after each `\n`.
- Method/property names you write get snake_cased; class names stay PascalCase.
- Service stubs default to `raise NotImplementedError('not implemented')`, not `pass`.
- Plain classes by default (no `@dataclass` unless you ask).
- `IntEnum` for numeric enum values.
- `Date` → `datetime` (the class).
- No `__init__.py` files are emitted; that's fine for the benchmark.
