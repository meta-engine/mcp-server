# MetaEngine MCP — Warmup Summary for Python Generation

This is a self-contained briefing for the next session, which will generate **Python** code from a DDD spec via the MetaEngine MCP server but will NOT have access to the engine's `linkedResources`. Everything you need is here. Read it once, use it.

---

## 1. What the server exposes

The `metaengine` MCP server provides one primary code-generation tool plus several spec-conversion helpers. For DDD code generation only `generate_code` matters; the others (`load_spec_from_file`, `generate_openapi`, `generate_graphql`, `generate_protobuf`, `generate_sql`, `metaengine_initialize`) are not part of the gen path.

`metaengine_initialize` is the documentation entrypoint — it returns the AI Code Generation Guide and is what we used in this warmup. The next session does **not** need to call it; this summary replaces it.

The two markdown linkedResources are:
- `metaengine://guide/ai-assistant` — critical rules + patterns + language notes + common mistakes (full text condensed below).
- `metaengine://guide/examples` — six worked TypeScript examples that apply identically to Python.

---

## 2. `generate_code` — full input schema

Top-level fields (only `language` is required):

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **yes** | `"python"` for our use case. Other valid: `typescript, go, csharp, java, kotlin, groovy, scala, swift, php, rust`. |
| `packageName` | string | no | Package/module/namespace. Java/Kotlin/Groovy default `com.metaengine.generated`; Go default `github.com/metaengine/demo`. **For Python, this is the package directory**. Omit/empty → no namespace declaration where applicable (C# behavior). |
| `outputPath` | string | no | Defaults to `"."`. Where files get written. |
| `initialize` | bool | no, default `false` | If true, properties get default-value initializers in the generated code. |
| `dryRun` | bool | no, default `false` | Preview mode: returns generated code in the response, doesn't write to disk. |
| `skipExisting` | bool | no, default `true` | When true, won't overwrite existing files (stub pattern). |
| `classes[]` | array | no | Class definitions. |
| `interfaces[]` | array | no | Interface definitions (Python: emitted as ABCs). |
| `enums[]` | array | no | Enum definitions. |
| `arrayTypes[]` | array | no | Virtual array type aliases. **NO files generated.** |
| `dictionaryTypes[]` | array | no | Virtual dictionary type aliases. **NO files generated.** |
| `concreteGenericClasses[]` | array | no | Concrete generic class refs (e.g. `Repository<User>`). **NO files generated.** |
| `concreteGenericInterfaces[]` | array | no | Concrete generic interface refs. **NO files generated.** |
| `customFiles[]` | array | no | Files that don't wrap a class — utility files, type aliases, barrel exports. |

### 2.1 `classes[]` element

| Field | Type | Notes |
|---|---|---|
| `name` | string | Class name (PascalCase as written; engine respects exact casing). |
| `typeIdentifier` | string | Unique key used to reference this class from other entries in the same call. **Critical**: cross-references resolve only within the batch. |
| `path` | string | Directory subpath, e.g. `"models"`, `"services/auth"`. |
| `fileName` | string | File name without extension. If omitted, derived from `name`. |
| `comment` | string | Class-level docstring/comment. |
| `isAbstract` | bool | Generates abstract class (Python: `ABC` subclass + `@abstractmethod` where applicable). |
| `baseClassTypeIdentifier` | string | typeIdentifier of base class to extend. |
| `interfaceTypeIdentifiers[]` | string[] | List of interface typeIdentifiers to implement. |
| `genericArguments[]` | array | Makes this a generic template. Each item: `{name, constraintTypeIdentifier?, propertyName?, isArrayProperty?}`. `propertyName` auto-generates a property of type T. |
| `constructorParameters[]` | array | Constructor params. Each: `{name, primitiveType?, type?, typeIdentifier?}`. **In C#/Java/Go/Groovy these auto-become properties — don't duplicate in `properties[]`.** Python behavior: Python uses `__init__`; the engine will emit constructor params as `__init__` arguments and assign them. Safer rule: also avoid duplication in Python. |
| `properties[]` | array | Field declarations only (type + name; no logic / no initialization expressions). See 2.5. |
| `customCode[]` | array | Methods, initialized fields, anything with logic. **One member per item.** See 2.6. |
| `customImports[]` | array | External library imports. Each: `{path, types?: string[]}`. **Never** include framework imports (typing, datetime, etc.) — they're auto-imported. |
| `decorators[]` | array | Class decorators. Each: `{code, templateRefs?}`. |

### 2.2 `interfaces[]` element

Same shape as classes but: no `constructorParameters`, no `baseClassTypeIdentifier`. `interfaceTypeIdentifiers[]` instead lets one interface extend others. For Python, interfaces become `ABC` (abstract base) classes; method signatures should be in `customCode` (NOT as function-typed properties — that produces malformed output across languages, and in Python it would emit attribute slots instead of `@abstractmethod` methods).

### 2.3 `enums[]` element

| Field | Notes |
|---|---|
| `name` | Enum class name. |
| `typeIdentifier` | Reference key. |
| `members[]` | `{name, value: number}`. |
| `path` | Directory subpath. |
| `fileName` | Override file name. |
| `comment` | Doc comment. |

In Python the engine emits an `Enum` subclass (member `value: 0` → integer-valued members). See §4.5 below.

### 2.4 `arrayTypes` / `dictionaryTypes` / `concreteGenericClasses` / `concreteGenericInterfaces`

Virtual type definitions — they don't generate files, only reusable type references.

```jsonc
"arrayTypes": [
  {"typeIdentifier": "user-list", "elementTypeIdentifier": "user"},
  {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
]
"dictionaryTypes": [
  {"typeIdentifier": "scores", "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
  {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
]
"concreteGenericClasses": [
  {"identifier": "user-repo-concrete",
   "genericClassIdentifier": "repo-generic",
   "genericArguments": [{"typeIdentifier": "user"}]}
]
```

`elementPrimitiveType` / `keyPrimitiveType` / `valuePrimitiveType` enum values: `"String" | "Number" | "Boolean" | "Date" | "Any"`.

### 2.5 Property element

| Field | Type | Notes |
|---|---|---|
| `name` | string | Field name. **Avoid Python reserved words**: `class`, `import`, `from`, `lambda`, `pass`, `return`, `def`, `del`, `global`, `try`, etc. Use `clazz`, `import_data`, etc. |
| `primitiveType` | enum | `"String" | "Number" | "Boolean" | "Date" | "Any"` — choose this OR `typeIdentifier` OR `type`. |
| `typeIdentifier` | string | Reference to a type defined elsewhere in this same call (class/interface/enum/arrayType/dictionaryType/concreteGeneric*). |
| `type` | string | Free-form type expression for complex/external types. Use with `templateRefs` when it embeds generated types. |
| `templateRefs[]` | array | Each `{placeholder, typeIdentifier}` — substitutes `$placeholder` in `type` and triggers import resolution. |
| `isOptional` | bool | Marks property optional. In Python this maps to `Optional[T]` / `T | None`. |
| `isInitializer` | bool | Adds default-value initialization. |
| `comment` | string | Docstring/comment. |
| `commentTemplateRefs[]` | array | Same shape as templateRefs but for `comment`. |
| `decorators[]` | array | Property-level decorators (e.g. `@field()`, validation decorators). Each `{code, templateRefs?}`. |

### 2.6 `customCode` element

```jsonc
{
  "code": "def get_user(self, user_id: str) -> $user:\n    raise NotImplementedError",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

- ONE customCode item = ONE method or ONE initialized field.
- Newlines between items are inserted automatically.
- `$placeholder` in `code` is substituted with the resolved Python type name AND triggers an automatic import.
- **Python-specific (CRITICAL)**: you must include explicit indentation (4 spaces) after every `\n` inside `code`. The engine does not auto-indent Python code blocks. So write `"def foo(self):\n    return 1"` NOT `"def foo(self):\nreturn 1"`.

### 2.7 `customFiles[]` element

For files that aren't a class/interface/enum (utilities, type aliases, helper modules):

```jsonc
{
  "name": "types",            // file name without extension
  "path": "shared",           // subdirectory
  "identifier": "shared-types", // (optional) makes this importable from other files via customImports.path = "shared-types"
  "customCode": [
    {"code": "UserId = str"},
    {"code": "Email = str"}
  ],
  "customImports": [...]
}
```

### 2.8 `customImports[]`

```jsonc
{"path": "fastapi", "types": ["FastAPI", "Depends"]}
```
- `path` is the module path (or a customFile `identifier` for cross-file refs to utility modules in the same batch).
- `types[]` is optional; without it, MetaEngine emits `import <path>`; with it, `from <path> import <types...>`.
- **Never** add stdlib modules that the engine auto-imports (see §3.4). Adding `typing`, `datetime`, `enum`, etc. causes duplication.

---

## 3. Critical rules (the things that break generation)

### 3.1 ONE call for all related types
`typeIdentifier` cross-references resolve only within the current `generate_code` call. If `OrderService` references `Order`, both must appear in the same batch. Splitting across multiple calls silently breaks imports.

### 3.2 Properties = type declarations. CustomCode = everything else.
- `properties[]`: name + type, NO logic, NO initialization expressions, NO method bodies.
- `customCode[]`: methods, initialized fields, anything with executable code. ONE member per entry.

Putting a method in `properties` or an uninitialized type declaration in `customCode` breaks output.

### 3.3 Use `templateRefs` for every internal type reference inside customCode / type strings
If `code` contains a generated type name as a raw string, MetaEngine will not generate the import. Always use `$placeholder` + `templateRefs`.

```jsonc
// WRONG
{"code": "def find(self) -> User: raise NotImplementedError"}

// RIGHT
{"code": "def find(self) -> $user:\n    raise NotImplementedError",
 "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
```

This rule is most strict in C# but applies universally — assume it's required for Python imports as well.

### 3.4 Don't put auto-imports in `customImports`
For Python, MetaEngine auto-imports: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`. Putting these in `customImports` causes duplication errors.

`customImports` is exclusively for external libraries (e.g. `fastapi`, `sqlalchemy`, `httpx`, project-internal customFiles via their `identifier`).

### 3.5 `templateRefs` ↔ `customImports` are mutually exclusive
Internal types (in this batch) → `typeIdentifier` / `templateRefs`. External library types → `customImports`. Never mix.

### 3.6 Don't reference unknown `typeIdentifier`s
If a `typeIdentifier` doesn't match any defined type in the batch, the property is silently dropped. Every reference must resolve.

### 3.7 Constructor parameters auto-become properties
In C#/Java/Go/Groovy this is documented; the safe Python convention is the same — don't duplicate `constructorParameters` entries in `properties[]`. Put non-constructor fields (only) in `properties`.

### 3.8 Avoid Python reserved words as identifiers
`class, import, from, lambda, def, del, return, try, except, finally, raise, with, yield, async, await, global, nonlocal, pass, in, is, not, and, or, if, elif, else, for, while, True, False, None`. Use safe alternatives.

### 3.9 Virtual types never generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are reference-only. They appear in `properties` of file-generating types via `typeIdentifier`.

---

## 4. Python-specific behavior

### 4.1 packageName / module naming

`packageName` sets the Python package (the engine writes files under a directory tree whose root is the package). Convention: lowercase with underscores (e.g. `domain.aggregates`, `myapp.generated`). For the DDD use case in this harness, the spec / agent prompt typically pins `packageName` (read it from the spec).

Python module file names use **snake_case**. The engine applies language-aware idiomatic transformations: PascalCase class names → snake_case file names. e.g. `OrderStatus` → `order_status.py`.

The harness convention (also expected by the structural judge in this repo) is:
- aggregates → `aggregates/` directory
- value objects → `value_objects/` directory (underscore!)
- enums → `enums/` directory
- services → `services/` directory

You control these via the per-class `path` field.

### 4.2 File path layout

Final output path = `outputPath` + (`packageName` mapped to dirs?) + per-class `path` + `fileName`/snake_case(`name`) + `.py`. In practice, set `outputPath` to where files should land and `path` per class to the kind directory. Example for an aggregate `Order`: `path: "aggregates"`, name: `Order` → file `aggregates/order.py`, class `class Order:`.

### 4.3 Type mapping

| MetaEngine `primitiveType` | Python type emitted |
|---|---|
| `String` | `str` |
| `Number` | `int` (default for whole-number-y numerics; for floats use explicit `type: "float"`) — N.B. C# also defaults Number to `int`. If your spec needs a decimal/float specifically, set `type: "float"` or `type: "Decimal"`. |
| `Boolean` | `bool` |
| `Date` | `datetime.datetime` (the `datetime` module is auto-imported; `decimal.Decimal` is also auto-imported when needed). |
| `Any` | `Any` (from `typing`, auto-imported) |

For collections produced by `arrayTypes` / `dictionaryTypes`: Python emits `list[T]` / `dict[K, V]` style (or `List[T]` / `Dict[K, V]` from `typing`, auto-imported).

For `isOptional: true` properties → `Optional[T]` / `T | None`.

### 4.4 Dataclasses vs plain classes

The MCP guide does **not** explicitly state whether the Python emitter uses `@dataclass`. The known facts:
- `dataclasses` is in the auto-import allowlist (engine knows about it).
- The harness's structural judge accepts EITHER `__init__` OR `@dataclass` as a valid constructor indicator — i.e. both shapes have been observed in practice.

Practical rule: don't try to force one or the other through the JSON schema. The engine picks the idiomatic form. If you specify `constructorParameters[]` on a class, the engine emits a class with those constructor params (whether as `@dataclass` fields or `__init__` args is engine-internal). If you only specify `properties[]` with `isInitializer: true` and no constructor params, you'll get default-initialized fields.

To force a specific style, use class-level `decorators` with `@dataclass` if you want dataclass semantics; otherwise rely on `constructorParameters` + `properties`.

### 4.5 Enums

`enums[]` entries become Python `Enum` subclasses (the `enum` module is auto-imported). Members `{name, value: number}` produce integer-valued members:

```python
from enum import Enum

class OrderStatus(Enum):
    Pending = 0
    Shipped = 2
```

The judge accepts `Enum`, `IntEnum`, or `StrEnum` superclasses — so the engine's default (`Enum`) is fine. Don't try to coerce IntEnum via raw type strings; let the engine pick.

Note that enum **member casing**: the engine applies language-aware idiomatic transforms — Java emits `ALL_CAPS`, Python may emit `snake_case` for methods. For enum **members** specifically, write them as the spec dictates (PascalCase or ALL_CAPS); the engine and the judge both tolerate the idiomatic form. Don't post-process or rename members afterward.

### 4.6 Method stub bodies

Convention used by the harness and accepted by the judge: `raise NotImplementedError`. Methods that only need to type-check should have body `raise NotImplementedError` (NOT `pass`). The judge's `stub_indicator` for Python is literally the string `"raise NotImplementedError"`, so missing it (e.g. using `pass` or `...`) flags as a structural issue.

Concrete `customCode` shape for a service method stub:

```jsonc
{
  "code": "def find_by_email(self, email: str) -> $user:\n    raise NotImplementedError",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}
```

Note the **4-space indentation** after `\n` — required for Python (the engine does not auto-indent Python customCode).

### 4.7 Method naming idiomatic transforms

The engine applies language-aware idiomatic transformations for method names — Python receives `snake_case` even when you write camelCase in customCode. Don't fight this. The judge tolerates it.

### 4.8 customCode ordering / interaction with method stubs

`customCode` blocks become members in declared order, with auto-newlines between them. If you want a class with N service methods, emit N `customCode` blocks, one per method. Don't try to glue multiple methods into one block.

For a service interface (ABC) implemented by a class: put method signatures (no body, just `raise NotImplementedError`) in the class's `customCode`. Don't define them as function-typed `properties` — that emits attribute slots, not callable methods.

---

## 5. Output structure produced

For a typical DDD spec with aggregates, value objects, enums, and services, MetaEngine generates one file per class/interface/enum, organized as you direct via `path`. Each file:

1. Auto-generated framework imports at the top (typing, datetime, enum, dataclasses, abc, etc. as needed).
2. `customImports` (external libs / customFile refs) below them.
3. Cross-references to other files in the same batch as `from .other_module import OtherClass` — relative imports calculated from `path` of source vs target.
4. Class/enum/interface declaration with members in the order: properties (type-declared), then customCode (methods/initialized fields).

**`dryRun: true`** returns the file contents in the response without writing — useful for previewing but not for the harness benchmark, which writes to disk.

**`skipExisting: true`** (default) means re-running won't clobber files. For our benchmark the agent should rely on outputPath being empty or use `skipExisting: false` if regenerating intentionally.

---

## 6. Worked example — DDD-style call sketch

```jsonc
{
  "language": "python",
  "packageName": "domain",
  "outputPath": "out",
  "enums": [
    {
      "name": "OrderStatus",
      "typeIdentifier": "order-status",
      "path": "enums",
      "members": [
        {"name": "Pending", "value": 0},
        {"name": "Confirmed", "value": 1},
        {"name": "Shipped", "value": 2}
      ]
    }
  ],
  "classes": [
    {
      "name": "Money",
      "typeIdentifier": "money",
      "path": "value_objects",
      "properties": [
        {"name": "amount", "type": "Decimal"},
        {"name": "currency", "primitiveType": "String"}
      ]
    },
    {
      "name": "Order",
      "typeIdentifier": "order",
      "path": "aggregates",
      "properties": [
        {"name": "id", "primitiveType": "String"},
        {"name": "status", "typeIdentifier": "order-status"},
        {"name": "total", "typeIdentifier": "money"},
        {"name": "created_at", "primitiveType": "Date"}
      ],
      "customCode": [
        {
          "code": "def confirm(self) -> None:\n    raise NotImplementedError"
        },
        {
          "code": "def ship(self) -> None:\n    raise NotImplementedError"
        }
      ]
    },
    {
      "name": "OrderService",
      "typeIdentifier": "order-service",
      "path": "services",
      "customCode": [
        {
          "code": "def place_order(self, order: $order) -> $order:\n    raise NotImplementedError",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
        },
        {
          "code": "def find(self, id: str) -> $order:\n    raise NotImplementedError",
          "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
        }
      ]
    }
  ]
}
```

Expected output tree:

```
out/
  domain/
    enums/
      order_status.py     # class OrderStatus(Enum): Pending = 0; ...
    value_objects/
      money.py            # class Money: amount: Decimal; currency: str
    aggregates/
      order.py            # imports OrderStatus, Money. class Order with confirm/ship raising NotImplementedError
    services/
      order_service.py    # imports Order. class OrderService with place_order/find raising NotImplementedError
```

(Exact directory rooting depends on whether `packageName` produces a `domain/` top-level dir or whether files go directly under `outputPath`. Inspect after the first call and adjust `outputPath`/`packageName` if the layout doesn't match the spec's expectations.)

---

## 7. Common mistakes — pre-flight checklist

1. ✗ Splitting types across multiple `generate_code` calls → cross-refs break. ✓ Bundle everything in ONE call.
2. ✗ Method bodies written as `properties` with function-typed `type` strings. ✓ Methods always go in `customCode`.
3. ✗ Raw type names inside customCode strings (`"def foo() -> User"`). ✓ `"def foo() -> $user"` with `templateRefs`.
4. ✗ Adding `typing`, `datetime`, `enum`, etc. to `customImports`. ✓ Let the engine auto-import.
5. ✗ Duplicating `constructorParameters` in `properties[]`. ✓ Constructor params only in `constructorParameters`.
6. ✗ Using Python reserved words as field names. ✓ Use safe aliases.
7. ✗ Forgetting 4-space indentation after `\n` in Python customCode. ✓ Always indent: `"def foo():\n    return 1"`.
8. ✗ Using `pass` or `...` as method stub bodies. ✓ Use `raise NotImplementedError`.
9. ✗ Referencing a `typeIdentifier` that doesn't exist in the batch. ✓ Verify every reference resolves.
10. ✗ Defining interface methods as function-typed properties. ✓ Put method signatures in `customCode` (with `raise NotImplementedError` body for ABCs).
11. ✗ Mixing `templateRefs` and `customImports` for the same type. ✓ Internal → templateRefs/typeIdentifier; external → customImports.

---

## 8. The minimum mental model

- **One JSON document, one MCP call.** Everything related must coexist there.
- **Properties declare shape; customCode declares behavior.**
- **`typeIdentifier` is the lingua franca** — every cross-reference inside the batch uses it.
- **`templateRefs` makes imports happen** — without them, internal type refs in code strings won't trigger imports.
- **`customImports` is for external libs only.**
- **Python: indent customCode bodies; stub bodies use `raise NotImplementedError`; let the engine pick `@dataclass` vs plain class.**

That's the contract. Hand the engine a well-formed JSON spec and you get back a coherent multi-file Python package with correct imports.
