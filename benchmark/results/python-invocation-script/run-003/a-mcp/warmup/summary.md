# MetaEngine MCP — Warmup Summary (Python target)

This is a self-contained reference for a downstream session that will generate **Python** code from a DDD spec via the metaengine MCP. The next session will NOT have access to `linkedResources`, so everything you need to call `generate_code` correctly is below.

---

## 1. Tools exposed by the metaengine MCP server

Two tools matter for code generation:

### `mcp__metaengine__metaengine_initialize`
- **Purpose:** Returns essential MetaEngine patterns and language-specific notes.
- **Schema:** one optional parameter `language` (enum: `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php`).
- Returns a markdown guide. **Already called in warmup** — do not re-call in a generation-only session.

### `mcp__metaengine__generate_code` ← the one you'll actually call
- **Purpose:** Generates compilable source files (with imports, cross-refs, language idioms) from a structured JSON spec.
- **Required field:** `language` (use `"python"`).
- See full schema in §3 below.

Other server tools advertised but not used here: `generate_graphql`, `generate_openapi`, `generate_protobuf`, `generate_sql`, `load_spec_from_file`. Ignore them for DDD code generation.

### Linked resources (already read; not available to gen session)
- `metaengine://guide/ai-assistant` — the canonical guide. Contents fully captured below.
- `metaengine://guide/examples` — usage examples. Key examples summarized below.

---

## 2. Cardinal Rules (read-before-call)

These are the rules whose violation causes the most failures.

### Rule 1 — Generate ALL related types in ONE call
`typeIdentifier` references only resolve **within the current batch**. If `OrderService` references `Order`, both must be in the same `generate_code` call. Cross-call references are silently dropped.

### Rule 2 — `properties[]` = type declarations only. `customCode[]` = everything with logic.
- `properties[]`: name + type. No initialization, no methods.
- `customCode[]`: methods, initialized fields, decorators-on-fields, anything containing logic. **One `customCode` entry = one member.**
- Never put methods in `properties`. Never put uninitialized type declarations in `customCode`.

### Rule 3 — Use `templateRefs` for internal types referenced in `customCode` / `properties.type` / decorators
When `customCode` references a type from the same batch, use a `$placeholder` token and a matching `templateRefs` entry. This triggers automatic import resolution. Without it, MetaEngine cannot generate the import.

```jsonc
"customCode": [{
  "code": "def get_user(self) -> $user:\n    raise NotImplementedError",
  "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]
}]
```

### Rule 4 — Never add framework imports to `customImports`
For Python, MetaEngine **auto-imports**: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`. Do not add these to `customImports` — duplication or errors result. Use `customImports` only for *external* libraries (e.g. `requests`, `sqlalchemy`, `fastapi`).

### Rule 5 — `templateRefs` are ONLY for internal (same-batch) types
External library types must use `customImports`. Same-batch types use `typeIdentifier` (in properties) or `templateRefs` (in code strings). Never mix.

### Rule 6 — Constructor parameters auto-create properties (in some langs)
In **C#, Java, Go, Groovy**, constructor params automatically become properties — duplicating in `properties[]` raises *"Sequence contains more than one matching element"*. **Python is not explicitly listed**; safest stance is to treat Python the same way: if you use `constructorParameters`, do NOT also list those names in `properties[]`. Put only *additional* (non-constructor) fields in `properties[]`.

### Rule 7 — Virtual types don't generate files
`arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` are **reusable type references only** — they never produce a file. They're used by referencing their `typeIdentifier` from a property of a file-generating type.

### Rule 8 — Don't reference a non-existent `typeIdentifier`
The property is silently dropped. Verify every `typeIdentifier` corresponds to a defined entity in the same call.

### Rule 9 — Reserved-word property names
Don't use Python keywords (`class`, `import`, `from`, `def`, `lambda`, `return`, `yield`, `raise`, `try`, `except`, `with`, `as`, `del`, `is`, `not`, `and`, `or`, `if`, `elif`, `else`, `for`, `while`, `pass`, `break`, `continue`, `global`, `nonlocal`, `True`, `False`, `None`) as property names. Use safe alternatives (`clazz`, `import_data`, etc.).

---

## 3. `generate_code` Full Input Schema

Top-level fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `language` | enum | **yes** | `typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php|rust` |
| `packageName` | string | no | Module/package/namespace name. Defaults: Go `github.com/metaengine/demo`, Java/Kotlin/Groovy `com.metaengine.generated`. For C# omit → no namespace. **For Python, see §4 below.** |
| `outputPath` | string | no | Directory where files are written. Default `.` |
| `dryRun` | bool | no | If true, returns file contents in response without writing. Default false. **Strongly recommended for first call to verify Python output before committing.** |
| `skipExisting` | bool | no | If true, files that already exist are not overwritten. Default true. |
| `initialize` | bool | no | Whether to initialize properties with default values. Default false. |
| `classes` | array | no | Class definitions. |
| `interfaces` | array | no | Interface definitions (Python: maps to abstract base classes). |
| `enums` | array | no | Enum definitions. |
| `arrayTypes` | array | no | Reusable array type refs (no files). |
| `dictionaryTypes` | array | no | Reusable dict type refs (no files). |
| `concreteGenericClasses` | array | no | Inline `Repo<User>`-style refs (no files). |
| `concreteGenericInterfaces` | array | no | Same for interfaces. |
| `customFiles` | array | no | Free-form files (type aliases, utilities). |

### `classes[]` item

| Field | Notes |
|---|---|
| `name` | Class name (PascalCase). |
| `typeIdentifier` | Unique key for cross-references. Conventionally kebab-case (`user`, `order-service`). |
| `path` | Subdirectory under `outputPath` (`models`, `services/auth`). |
| `fileName` | Override file name (no extension). |
| `comment` | Class docstring/comment. |
| `isAbstract` | bool. |
| `baseClassTypeIdentifier` | typeIdentifier of base class (single inheritance). |
| `interfaceTypeIdentifiers` | string[] of interface typeIdentifiers to implement. |
| `genericArguments` | makes the class a generic *template* (`Repo[T]`). Each item: `{name, constraintTypeIdentifier, propertyName, isArrayProperty}`. |
| `constructorParameters` | array of `{name, primitiveType|type|typeIdentifier}`. |
| `properties` | see below. |
| `customCode` | array of `{code, templateRefs}`. **One member per entry.** |
| `decorators` | array of `{code, templateRefs}` (class-level decorators). |
| `customImports` | array of `{path, types}` for external libs only. |

### `properties[]` item (used in classes & interfaces)

| Field | Notes |
|---|---|
| `name` | Property name. |
| `primitiveType` | enum: `String|Number|Boolean|Date|Any`. Use this for built-in scalars. |
| `typeIdentifier` | Reference to another type generated in same batch. |
| `type` | Free-form type expression string (e.g. `"List[$user]"` with templateRefs). Use when neither `primitiveType` nor `typeIdentifier` fits. |
| `templateRefs` | `[{placeholder, typeIdentifier}]` — required when `type` contains `$placeholder` tokens. |
| `isOptional` | bool. |
| `isInitializer` | bool. Adds default initialization. |
| `comment` | Property docstring. |
| `commentTemplateRefs` | templateRefs usable inside the comment. |
| `decorators` | property-level decorators (`@Field(...)`, `@validator`...). |

### `enums[]` item

| Field | Notes |
|---|---|
| `name` | Enum class name. |
| `typeIdentifier` | Unique key. |
| `path` | Optional subdir. |
| `fileName` | Optional override. |
| `comment` | Enum docstring. |
| `members` | `[{name, value}]` — value is a number. |

### `interfaces[]` item
Same structure as `classes[]` (name, typeIdentifier, path, fileName, comment, customCode, customImports, decorators, genericArguments, interfaceTypeIdentifiers, properties).

### `arrayTypes[]` item
| Field | Notes |
|---|---|
| `typeIdentifier` | **required** — the key you'll reference. |
| `elementPrimitiveType` | enum `String|Number|Boolean|Date|Any` for primitive elements. |
| `elementTypeIdentifier` | reference to a custom type for non-primitive elements. |

### `dictionaryTypes[]` item
| Field | Notes |
|---|---|
| `typeIdentifier` | **required**. |
| `keyPrimitiveType` / `keyTypeIdentifier` / `keyType` | one of these. |
| `valuePrimitiveType` / `valueTypeIdentifier` | one of these. |

All four key/value combinations (prim/prim, prim/custom, custom/prim, custom/custom) are supported.

### `concreteGenericClasses[]` / `concreteGenericInterfaces[]` items
| Field | Notes |
|---|---|
| `identifier` | The new typeIdentifier for the concrete generic. |
| `genericClassIdentifier` (or `genericInterfaceIdentifier`) | The generic-template class/interface this concretizes. |
| `genericArguments` | `[{typeIdentifier|primitiveType}]` |

### `customFiles[]` item
| Field | Notes |
|---|---|
| `name` | File name (no extension). |
| `path` | Subdirectory. |
| `fileName` | Optional override. |
| `identifier` | Lets other files reference this one via `customImports.path = identifier`. |
| `customCode` | array of `{code, templateRefs}` — one entry per export/alias. |
| `customImports` | external library imports. |

---

## 4. Python-Specific Notes

What the linkedResources explicitly state about Python:

1. **`customCode` indentation** — *"Must provide explicit indentation (4 spaces) after `\n` in customCode."* In other languages MetaEngine auto-indents method bodies; in Python you must include the four-space indent on every continuation line of a multi-line method body.
2. **`typing` imports are automatic** — never add `typing` to `customImports`.
3. **Auto-imported modules:** `typing.*`, `pydantic` (`BaseModel`, `Field`), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`.

What is **NOT** explicitly specified in the linkedResources for Python (use `dryRun: true` on first generation to verify, then conform downstream calls to whatever the engine actually produces):

- Whether classes are emitted as `@dataclass`, plain classes, or `pydantic.BaseModel` subclasses by default (the auto-import list includes both `dataclasses` and `pydantic`, so the engine knows about both — current behavior must be confirmed empirically).
- Whether enums emit `class X(Enum)` or `class X(IntEnum)` (members declare integer `value`, so `IntEnum` is plausible — verify).
- Whether method stub bodies use `pass`, `...`, or `raise NotImplementedError`.
- The exact file naming (snake_case `user.py` vs PascalCase `User.py`) — strongly expected to be snake_case but verify.
- Whether `packageName` becomes a Python package directory (with `__init__.py`) or just a logical namespace.

### Recommended Python conventions in the JSON spec

- **`packageName`** — provide a snake_case dotted module path, e.g. `"app.domain"`. Treat it like a Python package; the engine will likely create a matching directory layout under `outputPath`.
- **`name`** — use **PascalCase** for classes/interfaces/enums in the spec (`OrderLine`, `Customer`, `OrderStatus`). The engine generally preserves type names; it's the *file name* that gets idiomatic-cased.
- **`typeIdentifier`** — kebab-case (`order-line`, `customer`, `order-status`). Pure routing key — never appears in output.
- **Property names** — use snake_case (`first_name`, `created_at`). The engine applies "language-aware idiomatic transformations" — Python methods become `snake_case`, Java enum members become `ALL_CAPS`. Properties: safest to spec them already in snake_case.
- **`path`** — use forward slashes, lowercase (`models`, `services/auth`).
- **`fileName`** — only set if needed to override. Use snake_case (`user_repository`).
- **DDD layout suggestion:** `path: "domain"` for entities/value objects, `path: "domain/services"` for domain services, `path: "application"` for application services, `path: "infrastructure"` for repositories.

### Type mapping for Python

| `primitiveType` | Likely Python type | Notes |
|---|---|---|
| `String` | `str` | |
| `Number` | `int` or `float` | The C# guide explicitly states `Number → int`. The same default *probably* applies to Python: **use `"type": "float"` or `"type": "Decimal"` explicitly when you need non-integer numbers.** Don't assume `Number` gives a float. |
| `Boolean` | `bool` | |
| `Date` | `datetime.datetime` (or `datetime.date`) | Auto-imported. Engine likely chooses `datetime`; if you need a calendar date specifically, use `"type": "date"` and rely on auto-import of `datetime`. |
| `Any` | `Any` (from `typing`) | |

### Collections in Python

- For **arrays/lists** you can either declare an `arrayTypes[]` entry and reference its `typeIdentifier`, or write the type inline: `"type": "list[$item]"` (or `"List[$item]"`) with templateRefs. The TS-rendered example in the docs uses `Array<T>` so the Python equivalent is *expected* to be `list[T]` / `List[T]`. Verify with dryRun.
- For **dictionaries**, prefer `dictionaryTypes[]` entries. The TS example shows `Record<string, User>` → for Python this would render as `dict[str, User]` or `Dict[str, User]`.

### Optional / nullable

Use `"isOptional": true` on properties. The C# guide says this generates `string?`; Python likely renders as `Optional[T]` (or `T | None`). Verify with dryRun.

### Python customCode patterns

- Method stub:
  ```jsonc
  {
    "code": "def submit(self) -> $order:\n    raise NotImplementedError",
    "templateRefs": [{"placeholder": "$order", "typeIdentifier": "order"}]
  }
  ```
  Note the `\n    ` (newline + 4 spaces) for the body.
- Initialized field:
  ```jsonc
  {"code": "_history: list[str] = []"}
  ```
- Multi-line method:
  ```jsonc
  {
    "code": "def total(self) -> Decimal:\n    return sum(line.subtotal for line in self.lines)\n"
  }
  ```

### Decorators

For class-level decorators (e.g. `@dataclass`, `@pydantic.BaseModel`, framework decorators), use the `decorators[]` array on the class:
```jsonc
"decorators": [{"code": "@dataclass(frozen=True)"}]
```
**Caveat:** if MetaEngine already emits `@dataclass` automatically for plain classes, adding it manually duplicates. Run a dryRun first; only add explicit decorators when the default behavior doesn't match what you need.

For property-level decorators (e.g. `@field_validator`), use `properties[].decorators[]`.

---

## 5. Pattern Reference (condensed, language-agnostic)

### Basic class with cross-reference
```jsonc
{
  "language": "python",
  "classes": [
    {"name": "Address", "typeIdentifier": "address", "properties": [
      {"name": "street", "primitiveType": "String"},
      {"name": "city",   "primitiveType": "String"}
    ]},
    {"name": "User", "typeIdentifier": "user", "properties": [
      {"name": "id",      "primitiveType": "String"},
      {"name": "address", "typeIdentifier": "address"}
    ]}
  ]
}
```
→ Two files; the `User` file imports `Address`.

### Inheritance + method
```jsonc
{
  "classes": [
    {"name": "BaseEntity", "typeIdentifier": "base-entity", "isAbstract": true,
     "properties": [{"name": "id", "primitiveType": "String"}]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}],
     "customCode": [
       {"code": "def display_name(self) -> str:\n    return self.email"}
     ]}
  ]
}
```

### Generic + concrete generic
```jsonc
{
  "classes": [
    {"name": "Repository", "typeIdentifier": "repo-generic",
     "genericArguments": [{
       "name": "T",
       "constraintTypeIdentifier": "base-entity",
       "propertyName": "items",
       "isArrayProperty": true
     }],
     "customCode": [
       {"code": "def add(self, item: T) -> None:\n    self.items.append(item)"},
       {"code": "def get_all(self) -> list[T]:\n    return self.items"}
     ]},
    {"name": "User", "typeIdentifier": "user",
     "baseClassTypeIdentifier": "base-entity",
     "properties": [{"name": "email", "primitiveType": "String"}]},
    {"name": "UserRepository", "typeIdentifier": "user-repo-class",
     "baseClassTypeIdentifier": "user-repo-concrete"}
  ],
  "concreteGenericClasses": [{
    "identifier": "user-repo-concrete",
    "genericClassIdentifier": "repo-generic",
    "genericArguments": [{"typeIdentifier": "user"}]
  }]
}
```
The `concreteGenericClasses` entry creates the virtual `Repository[User]` reference; `UserRepository` extends it via `baseClassTypeIdentifier`.

### Array & dictionary types
```jsonc
{
  "arrayTypes": [
    {"typeIdentifier": "user-list",    "elementTypeIdentifier": "user"},
    {"typeIdentifier": "string-array", "elementPrimitiveType": "String"}
  ],
  "dictionaryTypes": [
    {"typeIdentifier": "scores",      "keyPrimitiveType": "String", "valuePrimitiveType": "Number"},
    {"typeIdentifier": "user-lookup", "keyPrimitiveType": "String", "valueTypeIdentifier": "user"}
  ]
}
```
Then reference via `"typeIdentifier": "user-list"` in a class property.

### Complex inline types via templateRefs
```jsonc
"properties": [{
  "name": "cache",
  "type": "dict[str, $resp]",
  "templateRefs": [{"placeholder": "$resp", "typeIdentifier": "api-response"}]
}]
```

### Enum + class that uses it
```jsonc
{
  "enums": [{"name": "OrderStatus", "typeIdentifier": "order-status",
    "members": [
      {"name": "Pending", "value": 0},
      {"name": "Shipped", "value": 2}
    ]}],
  "classes": [{"name": "Order", "typeIdentifier": "order",
    "properties": [{"name": "status", "typeIdentifier": "order-status"}],
    "customCode": [{
      "code": "def update_status(self, s: $status) -> None:\n    self.status = s",
      "templateRefs": [{"placeholder": "$status", "typeIdentifier": "order-status"}]
    }]}]
}
```

### Interface with method signatures (abstract base in Python)
For interfaces that a class will `implements` / inherit, declare method **signatures** in `customCode` — **not** as function-typed properties (or the implementing class will duplicate them).
```jsonc
{
  "interfaces": [{
    "name": "UserRepository", "typeIdentifier": "user-repo",
    "customCode": [
      {"code": "def find_all(self) -> list[$user]:\n    ...",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]},
      {"code": "def find_by_id(self, id: str) -> $user | None:\n    ...",
       "templateRefs": [{"placeholder": "$user", "typeIdentifier": "user"}]}
    ]
  }]
}
```
For Python this should map to an `abc.ABC` subclass with `@abstractmethod` (auto-imported).

### Service with external dependency
```jsonc
{
  "classes": [{
    "name": "ApiService", "typeIdentifier": "api-service",
    "path": "services",
    "customImports": [
      {"path": "requests", "types": ["Session"]}
    ],
    "customCode": [
      {"code": "_session: Session = Session()"},
      {"code": "def get_users(self) -> $list:\n    return self._session.get('/api/users').json()",
       "templateRefs": [{"placeholder": "$list", "typeIdentifier": "user-array"}]}
    ]
  }],
  "arrayTypes": [{"typeIdentifier": "user-array", "elementTypeIdentifier": "user-dto"}]
}
```

### customFiles for type aliases / utilities
```jsonc
{
  "customFiles": [{
    "name": "types", "path": "shared", "identifier": "shared-types",
    "customCode": [
      {"code": "UserId = str"},
      {"code": "Email = str"}
    ]
  }],
  "classes": [{
    "name": "UserHelper", "path": "helpers",
    "customImports": [{"path": "shared-types", "types": ["UserId", "Email"]}],
    "customCode": [{"code": "@staticmethod\ndef format_email(email: Email) -> str:\n    return email.strip()"}]
  }]
}
```
The `identifier` lets other files reference this customFile via `customImports.path`.

---

## 6. Common Mistakes (universal)

1. **Don't** reference a `typeIdentifier` that isn't defined in the same call — silently dropped.
2. **Don't** use function-typed properties for interface methods — the implementer will duplicate them. Use `customCode` for method signatures.
3. **Don't** write internal type names as raw strings in `customCode` (e.g. `def x(u: User)` directly). Use `$placeholder` + `templateRefs`.
4. **Don't** add framework imports (`typing`, `datetime`, `decimal`, `enum`, `abc`, `dataclasses`, `pydantic`) to `customImports`. They're auto-imported.
5. **Don't** duplicate constructor params in `properties[]` — at minimum for C#/Java/Go/Groovy; play it safe in Python too.
6. **Don't** use Python reserved words as property names.
7. **Don't** split related types across multiple `generate_code` calls — cross-file imports only resolve within one batch.
8. **Don't** assume `Number` → `float`. The C# default is `int`; assume the same for Python and use explicit `"type": "float"` / `"type": "Decimal"` when needed.
9. **Don't** forget the **4-space indent after `\n`** in Python `customCode`.
10. **Don't** skip `dryRun: true` on the first call when generating into a real project — verify the layout, the dataclass/pydantic choice, and stub bodies before writing files.

---

## 7. Output structure produced

- One file per `class` / `interface` / `enum` / `customFile`. Subdirectories taken from `path`.
- File names: derived from `name` (idiomatic-cased per language — for Python expect snake_case). Override with `fileName` (without extension).
- `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces` produce **no** files — only resolvable type references used inside other files' generated source.
- Imports between generated files are **resolved automatically** from `typeIdentifier` references and `templateRefs` — you never write them.
- External imports come from `customImports` only.
- The response (especially under `dryRun: true`) returns the generated file contents and paths so you can inspect before committing.

---

## 8. Recommended workflow for the Python DDD generation session

1. **Read the spec** — extract entities, value objects, aggregates, domain services, repositories, enums.
2. **Plan one big `generate_code` call** — list every type the spec mentions, give each a kebab-case `typeIdentifier`, decide their `path` (`domain/`, `domain/services/`, `application/`, `infrastructure/`).
3. **First call: `dryRun: true`** — confirm:
   - File names are snake_case as expected.
   - `@dataclass` vs plain class vs `BaseModel` matches what you want; if not, set `decorators` explicitly.
   - Enum class is `Enum` or `IntEnum` as you'd like; if not, you may need to use `customFiles` for full control.
   - Method stubs use `pass` / `...` / `raise NotImplementedError` — pick whichever matches the engine's default for your spec or override via `customCode`.
   - `Number` mapped to int vs float — switch to explicit `"type": "float"` / `"type": "Decimal"` where needed.
4. **Adjust the spec, then call once more with `dryRun: false`.**
5. **Never split into multiple calls** — cross-references break.

