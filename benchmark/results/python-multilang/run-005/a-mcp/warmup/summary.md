# MetaEngine MCP — Python Generation Cheat Sheet (self-contained)

This is the canonical reference for the next session, which will generate **Python**
code from a DDD spec via the `mcp__metaengine__generate_code` tool. The next session
will NOT have access to the MetaEngine documentation, so this file is everything.

---

## 1. What MetaEngine MCP is

A semantic code generation system. Instead of writing code line-by-line, you describe
**types, relationships, and methods as structured JSON**, and the engine emits
compilable, correctly-imported source files. It resolves cross-references between
types, manages framework imports automatically, and applies language-idiom defaults.
A single well-formed JSON call replaces dozens of file writes.

Supported languages: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`,
`groovy`, `scala`, `swift`, `php`, `rust`.

---

## 2. Tools exposed by the MCP server

### 2.1 `mcp__metaengine__metaengine_initialize`
Returns the AI guide. Optional `language` param (enum of supported languages) returns
language-specific patterns. **Call this once at the start** of generation work if
you need to refresh the guide. Not needed otherwise — the documentation is in this
summary.

### 2.2 `mcp__metaengine__generate_code`  ← the workhorse
Semantic code generation. Full schema below in §3.

### 2.3 Spec converters (NOT used here, listed for completeness)
- `mcp__metaengine__generate_openapi` — generate from an OpenAPI spec
- `mcp__metaengine__generate_graphql` — generate from a GraphQL schema
- `mcp__metaengine__generate_protobuf` — generate from a `.proto` file
- `mcp__metaengine__generate_sql` — generate from SQL DDL
- `mcp__metaengine__load_spec_from_file` — load a spec from disk

For DDD-spec → Python generation, you use **only `generate_code`**.

### 2.4 MCP resources (also listed for completeness)
- `metaengine://guide/ai-assistant` — the AI guide (same content as `metaengine_initialize`)
- `metaengine://guide/examples` — worked input/output examples

---

## 3. `generate_code` — full input schema

### Top-level fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **YES** | One of `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`, `rust`. Use `"python"`. |
| `packageName` | string | optional | Package/module/namespace. **Python**: this becomes the module/package name root. Defaults vary by language; for Python, set this explicitly to control imports (see §4). |
| `outputPath` | string | optional, default `"."` | Output directory where files are written. |
| `dryRun` | bool | optional, default `false` | If `true`, no files are written; generated code is returned in the response for review. |
| `skipExisting` | bool | optional, default `true` | If `true`, files that already exist are not overwritten. Useful for the "stub then customize" workflow. **Set `false` if you want the engine to overwrite.** |
| `initialize` | bool | optional, default `false` | If `true`, properties get default-value initializers (e.g. `id = ''`, `items = []`). |
| `classes` | array | optional | Class definitions (regular or generic templates). |
| `interfaces` | array | optional | Interface definitions (in Python, these become abstract base classes via `abc.ABC`). |
| `enums` | array | optional | Enum definitions. |
| `arrayTypes` | array | optional | Virtual array type aliases — **no file generated**, used by reference. |
| `dictionaryTypes` | array | optional | Virtual dictionary type aliases — **no file generated**, used by reference. |
| `concreteGenericClasses` | array | optional | Virtual concrete generic instantiations like `Repository<User>` — **no file generated**, used by reference. |
| `concreteGenericInterfaces` | array | optional | Same idea for interfaces. |
| `customFiles` | array | optional | Free-form files (utilities, type aliases, barrel exports) that don't fit the class/interface mold. |

### `classes[]` item

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name. |
| `typeIdentifier` | string | **Unique key** used by other types in the same call to reference this class. |
| `path` | string | Subdirectory path, e.g. `"models"`, `"services/auth"`. |
| `fileName` | string | Override the file name (no extension). |
| `comment` | string | Doc comment for the class. |
| `isAbstract` | bool | Marks the class abstract. |
| `baseClassTypeIdentifier` | string | typeIdentifier of the base class to extend. |
| `interfaceTypeIdentifiers` | string[] | typeIdentifiers of interfaces to implement. |
| `genericArguments` | array | Defines this as a generic class template (Python uses `TypeVar` + `Generic[T]`). Each item: `name` (e.g. `"T"`), `constraintTypeIdentifier`, `propertyName` (creates a property of type T), `isArrayProperty` (creates `T[]`/`List[T]`). |
| `constructorParameters` | array | Constructor params. Each: `{name, primitiveType?, type?, typeIdentifier?}`. **In C#/Java/Go/Groovy** they auto-become properties (don't duplicate). For Python, behavior is engine-managed. |
| `properties` | array | See "Property item" below. |
| `customCode` | array | Method/initialized-field code blocks. **One method = one item.** Each: `{code, templateRefs?}`. |
| `customImports` | array | External library imports. Each: `{path, types?}`. **Never** add stdlib imports here (see §6). |
| `decorators` | array | Class-level decorators. Each: `{code, templateRefs?}`. |

### Property item (used in `classes[].properties`, `interfaces[].properties`, etc.)

| Field | Type | Notes |
|---|---|---|
| `name` | string | Property name. **Avoid Python reserved words** (`class`, `import`, `from`, `del`, `lambda`, etc.). |
| `primitiveType` | enum | One of `String`, `Number`, `Boolean`, `Date`, `Any`. See §5 for Python mapping. |
| `typeIdentifier` | string | Reference to another type in this batch. |
| `type` | string | Free-form type expression for complex/external types (e.g. `List[$user]`). Use with `templateRefs`. |
| `isOptional` | bool | Marks property optional/nullable. |
| `isInitializer` | bool | Adds default-value initialization. |
| `comment` | string | Doc comment. |
| `commentTemplateRefs` | array | TemplateRefs for the comment text. |
| `decorators` | array | Property-level decorators. |
| `templateRefs` | array | TemplateRef map for `type` and `decorators` placeholders. |

### `interfaces[]` item
Same shape as `classes[]` minus `isAbstract`/`constructorParameters`/`baseClassTypeIdentifier`. Has `interfaceTypeIdentifiers` for extending other interfaces. **In Python, interfaces are emitted as `abc.ABC` subclasses with `@abstractmethod` methods.**

### `enums[]` item

| Field | Type | Notes |
|---|---|---|
| `name` | string | Enum class name. |
| `typeIdentifier` | string | Reference key. |
| `members` | array | Each: `{name: string, value: number}`. |
| `path` | string | Subdirectory. |
| `fileName` | string | Override file name. |
| `comment` | string | Doc comment. |

### `arrayTypes[]` item — **no file generated**
- `typeIdentifier` (required)
- `elementPrimitiveType` (`String`/`Number`/`Boolean`/`Date`/`Any`) **OR** `elementTypeIdentifier` (reference)

### `dictionaryTypes[]` item — **no file generated**
- `typeIdentifier` (required)
- Key: `keyPrimitiveType` OR `keyTypeIdentifier` OR `keyType` (free-form string)
- Value: `valuePrimitiveType` OR `valueTypeIdentifier`
- All 4 key×value combos (prim/prim, prim/custom, custom/prim, custom/custom) work.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` items — **no file generated**
- `identifier` — the new typeIdentifier you can reference
- `genericClassIdentifier` — the generic template's typeIdentifier
- `genericArguments[]` — each `{primitiveType?, typeIdentifier?}`

### `customFiles[]` item — generates a file WITHOUT a class wrapper
- `name` (required) — file name (no extension)
- `path` — subdirectory
- `fileName` — override
- `identifier` — optional; lets other files import via `customImports: [{path: "<identifier>"}]`
- `customCode` — array of `{code, templateRefs?}` items, one per export/alias/function
- `customImports` — external imports for this file

### `customCode[]` item (used everywhere)
- `code` — the literal code text (one method/field per item)
- `templateRefs` — array of `{placeholder, typeIdentifier}` mappings. The engine
  replaces `$placeholder` in the `code` string with the resolved type name and
  generates the matching `import` automatically.

### `customImports[]` item
- `path` — module path (e.g. `"fastapi"`, `"sqlalchemy.orm"`)
- `types` — list of names to import (e.g. `["FastAPI", "Depends"]`). Becomes
  `from <path> import <types>` in Python.

### `decorators[]` item
- `code` — decorator literal (e.g. `"@dataclass"`, `"@app.get('/')"`)
- `templateRefs` — same placeholder pattern as customCode

---

## 4. Python-specific notes (THE CRITICAL SECTION)

### 4.1 `packageName` / module naming
- `packageName` becomes the Python package root. Sub-paths (via `path` on each
  type) become subpackages.
- Pythonic convention is `snake_case`. Use `packageName: "myapp"` or
  `packageName: "myapp.domain"` (dotted) — it maps to a folder layout.
- File names are **snake_case** derived from the class name (`UserRepository` →
  `user_repository.py`). Override via the `fileName` field if needed.
- **Important**: typing imports (`List`, `Optional`, `Dict`, `Any`, etc.) are
  auto-managed by the engine. **Don't put them in `customImports`.**

### 4.2 File path layout
- Files land at `{outputPath}/{packageName-as-dirs}/{path}/{fileName}.py`.
- `path` on a type is a subdirectory under the package root.
- The engine emits `__init__.py` files where required for the Python package
  structure to work — but verify in dryRun if uncertain.
- Cross-file imports between generated types are emitted as relative or
  absolute imports automatically (the engine resolves them from `typeIdentifier`).

### 4.3 Type mapping (primitiveType → Python type)

| `primitiveType` | Python type emitted |
|---|---|
| `String` | `str` |
| `Number` | `int` (default — same as C#). Use the `type` field with `"float"` or `"Decimal"` if you need non-integer numbers. |
| `Boolean` | `bool` |
| `Date` | `datetime` (from `datetime` module — auto-imported). For date-only, use `type: "date"`. |
| `Any` | `Any` (from `typing` — auto-imported) |

For richer types (e.g. UUID, Decimal, dates), use the free-form `type` field:
- `"type": "UUID"` (the `uuid` module is auto-imported per the auto-import table)
- `"type": "Decimal"` (the `decimal` module is auto-imported)
- `"type": "date"` (date-only, from `datetime`)

For collections, prefer `arrayTypes` and `dictionaryTypes` (they emit as
`List[T]` / `Dict[K, V]`). For more exotic generics (`Set[T]`, `Tuple[...]`,
`Optional[T]`), use the free-form `type` with `templateRefs`.

### 4.4 Auto-imported modules in Python (DO NOT add to customImports)

- `typing.*` — `List`, `Dict`, `Optional`, `Any`, `Union`, `Tuple`, `Set`, `Callable`, `TypeVar`, `Generic`, etc.
- `pydantic` — `BaseModel`, `Field`
- `datetime` — `datetime`, `date`, `time`, `timedelta`
- `decimal` — `Decimal`
- `enum` — `Enum`, `IntEnum`, `auto`
- `abc` — `ABC`, `abstractmethod`
- `dataclasses` — `dataclass`, `field`
- `uuid` — `UUID`

`customImports` is **only** for third-party libraries (`fastapi`, `sqlalchemy`,
`httpx`, `pytest`, etc.) or your own non-generated modules.

### 4.5 Class style: dataclass vs pydantic vs plain

Based on the auto-import table the engine emits **both** `dataclass` and
`pydantic.BaseModel` machinery. The default emission for a `class` definition is
a **plain Python class with type-annotated attributes** (no decorator) unless
you explicitly attach one:

- **Want a `@dataclass`?** Add a class-level decorator: `decorators: [{code: "@dataclass"}]`.
  The engine handles the `from dataclasses import dataclass` import.
- **Want a Pydantic model?** Set `baseClassTypeIdentifier` to a synthetic class
  you define for `BaseModel`, OR add `customImports: [{path: "pydantic", types: ["BaseModel"]}]`
  and use it as a base via the free-form mechanism. Simpler: rely on the
  auto-import and add a class decorator or base class manually.
- **Plain class** (no decorator) is the default and works fine for DTOs.

Rule of thumb for DDD: use plain classes by default; add `@dataclass` when you
want value-object semantics with `__init__`/`__eq__`/`__repr__` for free.

### 4.6 Enums
- `enums[]` emits an `Enum` subclass: `class OrderStatus(Enum):` with members
  `PENDING = 0`, `SHIPPED = 2`, etc.
- `enum` module is auto-imported.
- Member values from the schema are integers — they emit as `IntEnum`-style
  numeric values. If you need a `str`-valued enum, use `customFiles` with
  hand-rolled enum code.
- File names: `order_status.py` (snake_case of the enum name).

### 4.7 Method stub bodies
Python is whitespace-sensitive — method bodies must have a body. The engine's
default behavior for an interface method (`abc.ABC` + `@abstractmethod`) is to
emit `pass` (or `...`). For class methods you write in `customCode`, **you
provide the body**. If you want a "to be implemented" stub, write it
explicitly:

```json
{ "code": "def get_user(self, id: str) -> '$user':\n    raise NotImplementedError",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}] }
```

For a no-op stub: `"def do_thing(self) -> None:\n    pass"`.

### 4.8 Indentation rule (CRITICAL)
> "Must provide explicit indentation (4 spaces) after `\n` in customCode"

Other languages auto-indent newlines in customCode blocks; **Python does not.**
Every line inside a method body must start with **literal 4-space indentation
in the `code` string**:

```jsonc
{
  "code": "def add(self, item: T) -> None:\n    self.items.append(item)\n    self._dirty = True"
}
```

For multi-line bodies count the indentation carefully: methods inside a class
need at least 4 spaces of body indent (so 8 from column zero if the engine
re-indents — but you write 4 in the JSON because the engine adds the class
indent itself).

If indentation is wrong the file won't parse — Python is unforgiving here.
**Test with `dryRun: true` first** for any non-trivial method body.

### 4.9 Constructor parameters in Python
The engine's per-language note says constructor-parameter / property
duplication is a problem in **C#/Java/Go/Groovy**. Python is not in that list,
but the safest approach is the same: **don't duplicate names** between
`constructorParameters` and `properties`. Put shared init fields only in
`constructorParameters`, additional fields in `properties`.

For dataclasses, prefer `properties` only and let the `@dataclass` decorator
synthesize `__init__`.

### 4.10 Generics in Python
The engine emits `TypeVar` + `Generic[T]`:
- Generic class: `class Repository(Generic[T]): ...` with `T = TypeVar("T", bound=BaseEntity)`.
- Concrete via `concreteGenericClasses` resolves to `Repository[User]` where
  used as a base or type expression.

### 4.11 Interfaces in Python
- An `interfaces[]` entry is emitted as an `abc.ABC` subclass.
- Method signatures defined in `customCode` get `@abstractmethod`.
- Implementing class uses `interfaceTypeIdentifiers` to declare the relationship.
- **Do NOT** put method signatures as function-typed properties; use `customCode`.

---

## 5. Critical rules (apply universally; reread before each call)

### Rule 1 — ONE call for related types
`typeIdentifier` references resolve **only within the current `generate_code`
batch**. If `OrderService` references `Order`, both must be in the same call.
Generate the whole DDD spec in one shot. Cross-call imports are not resolved.

### Rule 2 — `properties` vs `customCode`
- `properties[]` = type-annotated attribute declarations only. No logic, no init values (unless you set `isInitializer`).
- `customCode[]` = methods, computed/initialized fields, anything with logic.
- **One `customCode` item = exactly one method or one field.** The engine adds
  blank lines between blocks.
- Never put a method in `properties`. Never put an uninitialized
  type declaration in `customCode`.

### Rule 3 — `templateRefs` for internal types in `customCode`
When a method body or signature references another type from this batch, use
the `$placeholder` syntax with `templateRefs`. This is what makes the engine
emit the correct `import`.

```jsonc
{
  "code": "def get_user(self, id: str) -> '$user':\n    raise NotImplementedError",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

If you write the bare type name (e.g. `User`) instead of `$user`, the import
won't be generated and you'll get a `NameError` at runtime.

### Rule 4 — Never add framework imports to `customImports`
Python auto-imported modules are listed in §4.4. Adding them to `customImports`
causes duplication or errors. `customImports` is **only** for third-party libs
or your own non-generated modules.

### Rule 5 — `templateRefs` ≠ `customImports`
- Same batch (this MCP call) → `typeIdentifier` (in properties) or `templateRefs` (in customCode/decorators).
- External library → `customImports`.
- Never mix.

### Rule 6 — Constructor parameters auto-create properties (C#/Java/Go/Groovy)
Listed in the docs as a C#/Java/Go/Groovy gotcha. For Python: avoid duplication
to be safe (see §4.9).

### Rule 7 — Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`,
`concreteGenericInterfaces` create reusable type references **only**. They do
not produce files. Reference them via `typeIdentifier` in properties of a
real (file-generating) type.

### Rule 8 — Verify every typeIdentifier resolves
Referencing a typeIdentifier that doesn't exist in the batch silently drops
the property. Cross-check every reference before calling.

### Rule 9 — Avoid Python reserved words
Don't use `class`, `import`, `from`, `del`, `lambda`, `yield`, `pass`, `return`,
`global`, `nonlocal`, `try`, `except`, `finally`, `raise`, `with`, `as`, `is`,
`in`, `not`, `and`, `or`, `if`, `elif`, `else`, `for`, `while`, `def`, `async`,
`await`, `True`, `False`, `None` as property names. Pick alternatives
(`clazz`, `module_path`, `remove`, etc.).

---

## 6. Output structure produced

Given:
```
outputPath: "./out"
packageName: "myapp"
classes:
  - {name: "User", path: "domain", typeIdentifier: "user", properties: [{name: "id", primitiveType: "String"}]}
  - {name: "UserService", path: "application", typeIdentifier: "user-svc", customCode: [...]}
enums:
  - {name: "OrderStatus", path: "domain", members: [...]}
```

Emits:
```
./out/myapp/
  domain/
    user.py
    order_status.py
    __init__.py    # if engine emits package markers
  application/
    user_service.py
    __init__.py
  __init__.py
```

The exact package-marker behaviour is engine-managed; use `dryRun: true` to
inspect before writing.

---

## 7. End-to-end Python example (template to mimic)

This is a synthesized Python example based on the cross-language patterns shown
in the docs. Use it as a starting structure for the DDD spec generation.

```jsonc
{
  "language": "python",
  "packageName": "myapp",
  "outputPath": "./out",
  "skipExisting": false,
  "initialize": true,

  "enums": [{
    "name": "OrderStatus", "typeIdentifier": "order-status", "path": "domain",
    "members": [
      {"name": "PENDING", "value": 0},
      {"name": "PAID",    "value": 1},
      {"name": "SHIPPED", "value": 2}
    ]
  }],

  "interfaces": [{
    "name": "OrderRepository", "typeIdentifier": "order-repo", "path": "domain",
    "customCode": [
      { "code": "@abstractmethod\ndef find_by_id(self, id: str) -> '$order':\n    ...",
        "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}] },
      { "code": "@abstractmethod\ndef save(self, order: '$order') -> None:\n    ...",
        "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}] }
    ]
  }],

  "classes": [
    {
      "name": "Order", "typeIdentifier": "order", "path": "domain",
      "decorators": [{"code": "@dataclass"}],
      "properties": [
        {"name": "id",     "primitiveType": "String"},
        {"name": "status", "typeIdentifier": "order-status"},
        {"name": "total",  "type": "Decimal"},
        {"name": "created_at", "primitiveType": "Date"}
      ]
    },
    {
      "name": "OrderService", "typeIdentifier": "order-svc", "path": "application",
      "constructorParameters": [
        {"name": "repo", "typeIdentifier": "order-repo"}
      ],
      "customCode": [
        { "code": "def get(self, id: str) -> '$order':\n    return self.repo.find_by_id(id)",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}] },
        { "code": "def mark_paid(self, id: str) -> None:\n    order = self.repo.find_by_id(id)\n    order.status = $status.PAID\n    self.repo.save(order)",
          "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}] }
      ]
    }
  ],

  "arrayTypes": [
    {"typeIdentifier": "order-list", "elementTypeIdentifier": "order"}
  ]
}
```

This single call produces:
- `myapp/domain/order_status.py` — `class OrderStatus(Enum): ...`
- `myapp/domain/order_repository.py` — `class OrderRepository(ABC): ...`
- `myapp/domain/order.py` — `@dataclass class Order: ...` with `Decimal` and `datetime` auto-imports
- `myapp/application/order_service.py` — uses `OrderRepository` and `Order` with auto-imports

---

## 8. Common mistakes — the 10 cardinal sins

1. Referencing a `typeIdentifier` that doesn't exist in the batch → silently dropped.
2. Method signatures as function-typed `properties` on an interface → duplicated by implementing class.
3. Internal type names as raw strings in `customCode` → no import → `NameError`.
4. Adding `typing.*`, `datetime`, etc. to `customImports` → duplicate imports / errors.
5. Splitting related types across multiple `generate_code` calls → broken cross-references.
6. Duplicating constructor params in `properties[]` → "Sequence contains more than one matching element".
7. Using Python reserved words as property names.
8. Forgetting to indent multi-line method bodies in `customCode` (Python only).
9. Expecting `Number` to map to `float` — it maps to `int`. Use `type: "float"` or `type: "Decimal"`.
10. Putting external lib types via `templateRefs` instead of `customImports`. (templateRefs are for in-batch types only.)

---

## 9. Quick mental model

- **Define every type up front** in one big JSON object.
- **Properties = annotated attributes.** No logic.
- **CustomCode = methods + initialized fields.** One per item. Use `$placeholder` + `templateRefs` for any cross-type reference.
- **Virtual types** (`arrayTypes`, `dictionaryTypes`, `concreteGeneric*`) are aliases — they don't make files, they make type expressions reusable.
- **External imports** go in `customImports`. **Stdlib/typing/pydantic/dataclasses/datetime/enum/abc/decimal/uuid** are automatic.
- **Indent Python method bodies manually** (4 spaces after `\n`). Use `dryRun: true` to verify if unsure.
- **One `generate_code` call per coherent batch** (e.g. the whole DDD spec).

---

## 10. Suggested workflow for the next session

1. Read the DDD spec; enumerate every entity, value object, aggregate, domain
   service, repository interface, and enum.
2. Assign each one a `typeIdentifier` (kebab-case is fine; it's just a key).
3. Build the JSON in one pass:
   - `enums[]` for enumerations.
   - `interfaces[]` for repository contracts and other ports.
   - `classes[]` for entities, VOs, aggregates, services.
   - `arrayTypes[]` / `dictionaryTypes[]` for collection aliases used in
     multiple places.
4. Map all primitive types via the §4.3 table; use `type` for `Decimal`,
   `UUID`, `date`-only.
5. For methods, write the body with literal `\n    ` indentation. For "to be
   implemented" stubs use `raise NotImplementedError`; for no-ops use `pass`.
6. Wire cross-type references via `templateRefs` (in customCode) or
   `typeIdentifier` (in properties).
7. Set `packageName` to a Python-friendly module name (e.g. `myapp` or
   `myapp.domain`).
8. Run with `dryRun: true` first. Inspect generated files. Then run with
   `dryRun: false`, `skipExisting: false` to write.
9. Verify generated files import cleanly (`python -c "import myapp.domain.order"`).
