# MetaEngine MCP — Python Generation Summary

This summary is the canonical, self-contained reference for generating **Python** code via the metaengine MCP. It distills the linkedResources (`metaengine://guide/ai-assistant`, `metaengine://guide/examples`) plus the `generate_code` JSON Schema, with extra emphasis on Python-specific behavior.

---

## 1. Tools Exposed by the `metaengine` MCP Server

| Tool | Purpose |
|------|---------|
| `mcp__metaengine__metaengine_initialize` | Returns the AI guide (warmup). Optional `language` param ∈ `{typescript, python, go, csharp, java, kotlin, groovy, scala, swift, php}`. Use it once per session. |
| `mcp__metaengine__generate_code` | The actual generator. Takes a structured JSON spec and writes source files (or returns them in `dryRun`). |
| `mcp__metaengine__load_spec_from_file` | Loads a JSON spec from disk (helper). |
| `mcp__metaengine__generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql` | Specialized variants that read OpenAPI/GraphQL/Protobuf/SQL specs. Not used here — we are generating from a DDD spec. |

The two MCP **resources** are:
- `metaengine://guide/ai-assistant` — full AI Code Generation Guide.
- `metaengine://guide/examples` — annotated end-to-end examples.

---

## 2. `generate_code` Input Schema (Full)

Required field: `language` (string enum). For Python pass `"language": "python"`.

Top-level optional fields:

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `outputPath` | string | `"."` | Directory the files are written to. |
| `packageName` | string | language-specific (see below) | For Python this is the **module/package path** prefix. |
| `initialize` | boolean | `false` | If `true`, properties get default-value initializers. |
| `dryRun` | boolean | `false` | If `true`, returns generated source in the response and writes nothing. Use this for review. |
| `skipExisting` | boolean | `true` | If `true`, files that already exist on disk are NOT overwritten — supports the "stub" pattern where customCode is added later by the user. **Set to `false` when you want a clean re-generation.** |
| `classes` | array | — | Class definitions (see schema below). |
| `interfaces` | array | — | Interface definitions (in Python these become abstract base classes). |
| `enums` | array | — | Enum definitions. |
| `arrayTypes` | array | — | Reusable array type references. **Generates NO files.** |
| `dictionaryTypes` | array | — | Reusable dict type references. **Generates NO files.** |
| `concreteGenericClasses` | array | — | Inline `Repository<User>`-style references. **No files.** |
| `concreteGenericInterfaces` | array | — | Same idea for generic interfaces. **No files.** |
| `customFiles` | array | — | Free-form files (type aliases, helpers, barrel exports, `__init__.py`-like). |

### 2.1 `classes[]` schema

```jsonc
{
  "name": "User",                          // Required. Class name.
  "typeIdentifier": "user",                // Unique id used by other entries to reference this class.
  "comment": "...",                        // Optional doc comment (becomes docstring in Python).
  "fileName": "user",                      // Optional override (without extension).
  "path": "models",                        // Optional sub-directory under outputPath.
  "isAbstract": true,                      // Optional. Python → ABC.
  "baseClassTypeIdentifier": "base-entity",// Optional. References another typeIdentifier.
  "interfaceTypeIdentifiers": ["..."],     // Optional. Array of interface ids to implement.
  "genericArguments": [{                   // Makes this a generic template.
    "name": "T",
    "constraintTypeIdentifier": "base-entity",
    "propertyName": "items",               // Auto-creates a property of type T (or T[] when isArrayProperty).
    "isArrayProperty": true
  }],
  "constructorParameters": [               // Note: in Python, NOT auto-promoted to properties (unlike C#/Java/Go/Groovy).
    {"name": "email", "primitiveType": "String"},
    {"name": "status", "typeIdentifier": "status"},
    {"name": "tags",  "type": "list[str]"}
  ],
  "properties": [{                         // Type declarations only — never methods.
    "name": "id",
    "primitiveType": "String",             // Or use "type" / "typeIdentifier".
    "type": "list[$user]",                 // Free-form type expression with $placeholders.
    "typeIdentifier": "address",           // Reference to another generated type.
    "isOptional": true,                    // Python → Optional[X] / X | None.
    "isInitializer": true,                 // Adds a default value initializer.
    "comment": "Doc string for the field",
    "decorators": [                        // Decorators sit above the property.
      {"code": "@validator('email')", "templateRefs": []}
    ],
    "templateRefs": [                      // Resolves $placeholders in `type`.
      {"placeholder": "$user", "typeIdentifier": "user"}
    ],
    "commentTemplateRefs": []
  }],
  "decorators": [                          // Class-level decorators (e.g. @dataclass, @injectable).
    {"code": "@dataclass", "templateRefs": []}
  ],
  "customImports": [                       // ONLY for external libs — never stdlib.
    {"path": "pydantic", "types": ["validator"]}
  ],
  "customCode": [                          // ONE entry per member (method or initialized field).
    {"code": "name: str = \"\"", "templateRefs": []},
    {
      "code": "def get_user(self, id: str) -> $user:\n    raise NotImplementedError",
      "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
    }
  ]
}
```

### 2.2 `interfaces[]` schema

Same shape as classes, minus `constructorParameters` / `baseClassTypeIdentifier` / `isAbstract`. Has `interfaceTypeIdentifiers` for extending other interfaces. In Python, interfaces compile to **`abc.ABC` subclasses with `@abstractmethod` method stubs**.

### 2.3 `enums[]` schema

```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "fileName": "order_status",        // Optional.
  "path": "models",                   // Optional.
  "comment": "Order lifecycle states",
  "members": [
    {"name": "Pending",   "value": 0},
    {"name": "Shipped",   "value": 2},
    {"name": "Delivered", "value": 3}
  ]
}
```

### 2.4 `arrayTypes[]`

```jsonc
{"typeIdentifier": "user-list", "elementTypeIdentifier": "user"}
{"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
```

In Python, an arrayType becomes `list[T]` (or `List[T]` from `typing`). **No file is produced** — only a reusable reference.

### 2.5 `dictionaryTypes[]`

All 4 key/value combinations work:

```jsonc
{"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"}
{"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
{"typeIdentifier": "by-user", "keyTypeIdentifier": "user", "valuePrimitiveType": "String"}
{"typeIdentifier": "u2m", "keyTypeIdentifier": "user", "valueTypeIdentifier": "metadata"}
```

In Python this becomes `dict[K, V]`. **No file produced.**

### 2.6 `concreteGenericClasses[]` / `concreteGenericInterfaces[]`

```jsonc
{
  "identifier": "user-repository",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [{"typeIdentifier": "user"}]
}
```

Creates the inline reference `Repository[User]`. Reference it from another class via `baseClassTypeIdentifier` or via `templateRefs`. **No file produced.**

### 2.7 `customFiles[]`

```jsonc
{
  "name": "types",            // file base name
  "fileName": "types",        // optional explicit override
  "path": "shared",
  "identifier": "shared-types", // optional — lets other files reference it via customImports
  "customCode": [
    {"code": "UserId = str"},
    {"code": "Timestamp = int"}
  ],
  "customImports": [
    {"path": "typing_extensions", "types": ["TypeAlias"]}
  ]
}
```

Use this for Python type aliases (`UserId = str`), top-level constants, helper functions, or `__init__.py` re-exports.

---

## 3. Primitive Type Mapping (Python target)

| Schema `primitiveType` | Generated Python type |
|------------------------|-----------------------|
| `"String"`             | `str` |
| `"Number"`             | `int` *(integer by default — same convention as C#).* For floats use `"type": "float"` or `"type": "decimal.Decimal"`. |
| `"Boolean"`            | `bool` |
| `"Date"`               | `datetime.datetime` (auto-imported from `datetime`). For pure date-only fields use `"type": "date"`. |
| `"Any"`                | `Any` (auto-imported from `typing`). |

For anything else, use the free-form `"type"` field and combine with `templateRefs` if an internal type is involved:

```jsonc
{"name": "amount", "type": "Decimal"}                           // auto-imports from decimal
{"name": "tags",   "type": "list[str]"}
{"name": "owner",  "type": "Optional[$user]",
 "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
```

**Auto-imported in Python (NEVER add to `customImports`):**
`typing.*`, `pydantic.BaseModel`, `pydantic.Field`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses`.

---

## 4. Python-Specific Behavior

### 4.1 `packageName` / module naming

- `packageName` is the dotted Python module/package path the files are intended to live under.
- It influences **import statements** between generated files (cross-file imports use the package).
- File system paths are still controlled by `outputPath` + each entry's `path` field — `packageName` is the import-path prefix, not the filesystem prefix.
- Conventional values: `"app.domain"`, `"my_project.models"`, etc. Use snake_case dotted segments.

### 4.2 File path layout

- File on disk = `<outputPath>/<path>/<fileName-or-derived>.py`.
- `path` is the relative directory beneath `outputPath`. Use forward slashes (`models`, `services/auth`).
- If `fileName` is omitted, MetaEngine derives it from `name` using snake_case (e.g. `OrderStatus` → `order_status.py`).
- Enum filenames are emitted plainly (e.g. `order_status.py`) — Python does **not** add the `.enum` suffix that TypeScript uses.
- Each `class`, `interface`, `enum`, and `customFile` becomes one `.py` file. Virtual types (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`) produce **no file**.

### 4.3 Dataclass vs plain class — what does the engine emit?

The default emission shape for classes is a **plain Python class** with type-annotated attributes (and an `__init__` if `constructorParameters` are provided). To get a `@dataclass` you must put it on the class via `decorators`:

```jsonc
{
  "name": "User",
  "typeIdentifier": "user",
  "decorators": [{"code": "@dataclass"}],
  "properties": [
    {"name": "id",    "primitiveType": "String"},
    {"name": "email", "primitiveType": "String"}
  ]
}
```

Pydantic models work the same way — set `baseClassTypeIdentifier` to a Pydantic base via a customFile, or add it as a raw external type in `customImports` and inherit through a customCode header. In short: **MetaEngine itself emits "plain class with annotations"; you opt into dataclass / pydantic via decorators or inheritance.**

`isAbstract: true` on a class makes the engine emit it as an `abc.ABC` subclass (`abc` is auto-imported).

### 4.4 Interfaces in Python

Interfaces compile to abstract base classes:

```python
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[User]: ...
```

Define method signatures via `customCode` (just like the TypeScript pattern), not as function-typed properties. The engine inserts `@abstractmethod` automatically and the body is `...` (ellipsis) or `raise NotImplementedError` — see §4.7.

### 4.5 Enums

`enums[]` produces `enum.IntEnum` subclasses (because the schema defines `value` as `number`):

```python
from enum import IntEnum

class OrderStatus(IntEnum):
    Pending = 0
    Shipped = 2
    Delivered = 3
```

If you need a string enum, define it via `customFiles` instead and write the body manually:

```jsonc
{
  "name": "order_status",
  "path": "models",
  "customCode": [{
    "code": "class OrderStatus(str, Enum):\n    PENDING = \"pending\"\n    SHIPPED = \"shipped\""
  }]
}
```

(`enum.Enum` is auto-imported.)

### 4.6 Generics

Python generics use `typing.TypeVar` + `typing.Generic[T]`. MetaEngine handles this when you use `genericArguments` on a class/interface and `concreteGenericClasses`/`concreteGenericInterfaces` for the concrete instantiation.

Example: `Repository[T]` extending `BaseEntity`-bounded `T`:

```jsonc
"classes": [{
  "name": "Repository",
  "typeIdentifier": "repo-generic",
  "genericArguments": [{
    "name": "T",
    "constraintTypeIdentifier": "base-entity",
    "propertyName": "items",
    "isArrayProperty": true
  }],
  "customCode": [
    {"code": "def add(self, item: T) -> None:\n    self.items.append(item)"},
    {"code": "def get_all(self) -> list[T]:\n    return self.items"}
  ]
}]
```

### 4.7 Method stub bodies (`customCode` ⟶ Python)

There is **no auto-generation of method bodies** — whatever string you put in `customCode.code` is what is emitted (with auto-indentation). For Python:

- **Indentation**: you MUST provide explicit indentation (4 spaces) after every `\n` inside `code`. The engine handles the leading indent of the first line, but **multi-line bodies need their own internal indentation**. Example:

  ```jsonc
  {"code": "def get_user(self, id: str) -> $user:\n    raise NotImplementedError(\"get_user not implemented\")"}
  ```

- **Stub convention**: prefer `raise NotImplementedError(...)` for stubs you intend to fill in later — this is loud and fail-fast at runtime. Use `pass` only when the method is intentionally a no-op. Use `...` (ellipsis) on `@abstractmethod` declarations in interfaces.
- **One member per `customCode` entry**: never bundle two methods into one `code` string. The engine inserts a blank line between blocks automatically.
- **Docstrings**: include them inside the `code` body, indented:
  ```jsonc
  {"code": "def get_user(self, id: str) -> $user:\n    \"\"\"Look up a user by id.\"\"\"\n    raise NotImplementedError"}
  ```

### 4.8 Constructor parameters in Python

Unlike C#/Java/Go/Groovy, Python's `constructorParameters` are **not** auto-promoted to class attributes. You can safely list a field in BOTH `properties` (for the annotation) AND `constructorParameters` (for the `__init__` signature) without triggering the "Sequence contains more than one matching element" error.

If you decorate the class with `@dataclass`, omit the `__init__` (don't pass `constructorParameters`) — the dataclass machinery generates it from the annotations.

### 4.9 `templateRefs` for cross-file references

Whenever a `customCode` block, a `properties[].type`, or a decorator references another internal type, do it via a `$placeholder` AND list it in `templateRefs` so the engine can resolve the import. Without this, no `from foo import X` is added.

```jsonc
{
  "code": "def find_by_email(self, email: str) -> Optional[$user]:\n    raise NotImplementedError",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

### 4.10 Reserved word safety

Don't use Python keywords as property/parameter names: `class`, `from`, `import`, `def`, `return`, `lambda`, `pass`, `raise`, `is`, `in`, `not`, `and`, `or`, `None`, `True`, `False`, `global`, `nonlocal`, `with`, `as`, `try`, `except`, `finally`, `for`, `while`, `if`, `elif`, `else`, `yield`, `async`, `await`, `del`. Also avoid shadowing builtins like `list`, `dict`, `id`, `type`, `input` — pick alternatives (`items`, `mapping`, `identifier`, `kind`, `value`).

---

## 5. Critical Rules (apply to every call)

1. **One call generates one batch.** Cross-references are only resolved within the same `generate_code` call. If `OrderService` references `Order`, both must be in the same call.
2. **`properties` = type declarations. `customCode` = everything else** (methods, initialized fields, anything with logic). One member per `customCode` entry.
3. **Internal type references in `customCode` MUST use `$placeholder` + `templateRefs`** — otherwise no import is generated.
4. **Never add stdlib / framework imports to `customImports`.** For Python, `typing.*`, `pydantic.BaseModel`, `pydantic.Field`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses` are auto-imported.
5. **`templateRefs` are ONLY for internal types** (defined in the same call). External library types use `customImports`.
6. **Python constructor params do NOT auto-promote** to attributes — but they also don't conflict with `properties`. (Different from C#/Java/Go/Groovy.)
7. **Virtual types produce no files** (`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`). They are referenced by `typeIdentifier` in `properties`/`customCode` only.
8. **Verify every `typeIdentifier`** referenced in the spec is defined in the same call — silently dropped properties otherwise.
9. **Provide explicit 4-space indentation after every `\n`** in Python `customCode` bodies.
10. **`skipExisting: true` is the default.** When iterating, set it to `false` to actually overwrite. When using `dryRun: true`, no files are written either way.

---

## 6. Output Structure Produced

The `generate_code` response returns:

- A list of files written (path on disk + content size), or
- When `dryRun: true`, the full file contents inline in the response so they can be reviewed without touching disk.

For each file the engine emits:

1. Auto-resolved imports (stdlib + cross-file references resolved from `typeIdentifier`/`templateRefs`).
2. `customImports` block for external libraries.
3. The file body: class / interface (ABC) / enum / customFile content.
4. Members ordered as: properties → `__init__` (from `constructorParameters`) → `customCode` blocks (in declared order), separated by blank lines.

Files are placed at `<outputPath>/<path>/<fileName-or-snake_case(name)>.py`. Generated module imports use `<packageName>.<path-with-dots>` so set `packageName` to the package the files will actually live in once installed.

---

## 7. Python Skeleton Example (DDD-flavored)

A minimal end-to-end Python example combining the patterns above:

```jsonc
{
  "language": "python",
  "outputPath": "./out",
  "packageName": "shop.domain",
  "skipExisting": false,
  "enums": [
    {"name": "OrderStatus", "typeIdentifier": "order-status", "path": "orders",
     "members": [{"name": "Pending", "value": 0}, {"name": "Shipped", "value": 1}]}
  ],
  "classes": [
    {
      "name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
      "path": "common",
      "properties": [{"name": "id", "primitiveType": "String"}]
    },
    {
      "name": "Order", "typeIdentifier": "order", "path": "orders",
      "baseClassTypeIdentifier": "base-entity",
      "decorators": [{"code": "@dataclass"}],
      "properties": [
        {"name": "total",     "type": "Decimal"},
        {"name": "status",    "typeIdentifier": "order-status"},
        {"name": "placed_at", "primitiveType": "Date"}
      ]
    }
  ],
  "interfaces": [
    {
      "name": "IOrderRepository", "typeIdentifier": "order-repo", "path": "orders",
      "customCode": [
        {"code": "def find_by_id(self, id: str) -> Optional[$order]:\n    ...",
         "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]},
        {"code": "def save(self, order: $order) -> None:\n    ...",
         "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]}
      ]
    }
  ],
  "classes": [
    {
      "name": "OrderService", "typeIdentifier": "order-service", "path": "orders",
      "constructorParameters": [
        {"name": "repo", "typeIdentifier": "order-repo"}
      ],
      "properties": [
        {"name": "repo", "typeIdentifier": "order-repo"}
      ],
      "customCode": [
        {"code": "def place(self, order: $order) -> None:\n    self.repo.save(order)",
         "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]}
      ]
    }
  ]
}
```

This produces (sketch):

- `out/common/base_entity.py` — abstract `BaseEntity(ABC)` with `id: str`.
- `out/orders/order_status.py` — `class OrderStatus(IntEnum): Pending = 0; Shipped = 1`.
- `out/orders/order.py` — `@dataclass class Order(BaseEntity): ...` with `total: Decimal`, `status: OrderStatus`, `placed_at: datetime`.
- `out/orders/i_order_repository.py` — `class IOrderRepository(ABC): @abstractmethod def find_by_id(...) ...`
- `out/orders/order_service.py` — `class OrderService:` with `__init__(self, repo: IOrderRepository)` and `place(...)`.

All with auto-imports between them resolved via `typeIdentifier` / `templateRefs`.

---

## 8. Common Mistakes (Python-tinted)

1. **Don't** put method signatures as function-typed properties on interfaces. **Do** use `customCode` with `@abstractmethod` shown via the engine.
2. **Don't** put internal type names as raw strings in `customCode` — `from .x import Y` won't be generated. **Do** use `$placeholder` + `templateRefs`.
3. **Don't** add `from typing import ...`, `from datetime import datetime`, `from enum import Enum`, `from abc import ABC`, `from pydantic import BaseModel` to `customImports`. They are auto-handled.
4. **Don't** generate related types in separate calls. Cross-file imports only resolve within one batch.
5. **Don't** assume `Number` → `float`. It maps to `int`. Use `"type": "float"` or `"type": "Decimal"` for fractional values.
6. **Don't** forget 4-space indentation after `\n` in multi-line `customCode` Python bodies.
7. **Don't** reference a `typeIdentifier` that doesn't exist in the call — the property is silently dropped.
8. **Don't** use Python keywords or builtins as field/parameter names.
9. **Don't** rely on `skipExisting=true` (the default) when iterating: pre-existing files won't be overwritten.
10. **Don't** include framework decorators (`@dataclass`, `@abstractmethod`) inside `customCode` text **and** also rely on the engine to add them — pick one source of truth. For `@dataclass` use class-level `decorators`. `@abstractmethod` is added automatically inside `interfaces` `customCode` blocks.

---

## 9. Quick Mental Model

> "Describe the **types** in `properties` and the **behavior** in `customCode`. Reference other types through `typeIdentifier` (in fields) or `$placeholder` + `templateRefs` (in code). Put **all** related types in **one** `generate_code` call. Let the engine handle stdlib imports. Decorate manually for `@dataclass`. Provide your own indentation in Python bodies. Use `dryRun: true` to preview."
