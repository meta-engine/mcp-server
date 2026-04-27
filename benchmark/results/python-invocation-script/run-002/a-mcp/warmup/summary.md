# MetaEngine MCP — Warmup Summary (Python Generation Focus)

This is a self-contained reference for generating Python source files via the MetaEngine MCP server. The next session will receive a DDD spec and generate Python code WITHOUT access to the MCP's `linkedResources`. Everything required to call `mcp__metaengine__generate_code` correctly for Python is captured below.

---

## 1. Tools Exposed by the `metaengine` MCP Server

There are three tools exposed:

### 1.1 `mcp__metaengine__metaengine_initialize`
Documentation helper. Returns critical patterns + links to the AI guide. Optional `language` parameter (one of: `typescript`, `python`, `go`, `csharp`, `java`, `kotlin`, `groovy`, `scala`, `swift`, `php`). Call this when in doubt; do **not** call repeatedly.

### 1.2 `mcp__metaengine__generate_code` (the main tool)
Semantic code generation. Single call → multiple files written to disk with cross-references and imports resolved. **Required field**: `language`. See full schema in §3.

### 1.3 `mcp__metaengine__load_spec_from_file`
Reads a `.json` file with the same shape as `generate_code` input and runs it. Useful when the spec is large; not required for typical usage.

There are also two MCP **resources** (read-only docs) — already consumed during this warmup; not callable as tools:
- `metaengine://guide/ai-assistant`
- `metaengine://guide/examples`

---

## 2. Cardinal Rules (must internalize before generating)

1. **ONE call generates ALL related types.** `typeIdentifier` cross-references resolve only within a single batch. Splitting a related type set across calls = broken imports.
2. **`properties[]` = type declarations only. `customCode[]` = methods, initialized fields, anything with logic.** One `customCode` entry = exactly one member.
3. **For internal type references inside `customCode` or complex `type` strings, use `templateRefs` with `$placeholder` syntax.** This is what triggers automatic import generation. Raw type names won't be auto-imported.
4. **Never put framework imports in `customImports`.** Python auto-imports: `typing.*`, `pydantic` (BaseModel, Field), `datetime`, `decimal`, `enum`, `abc`, `dataclasses`. Use `customImports` ONLY for genuinely external libs (e.g., `httpx`, `fastapi`, `sqlalchemy`, etc.).
5. **`templateRefs` are ONLY for types defined in the same batch.** External libs go in `customImports`. Don't mix.
6. **Constructor parameters in C#/Java/Go/Groovy auto-create properties — don't duplicate.** *Python does not have this auto-promotion behavior in the same form*; safest practice is still: don't duplicate names between `constructorParameters` and `properties`.
7. **Virtual types never produce files**: `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`. They are reusable type aliases used via `typeIdentifier` references.
8. **Reserved words must be avoided as property names** (`class`, `import`, `delete`, `from`, `lambda`, `return`, etc. for Python). Use safe alternatives (`clazz`, `importData`).
9. **Dropped silently**: an unresolvable `typeIdentifier` in a property silently drops that property. Verify every identifier is defined somewhere in the batch.
10. **Single-call mindset**: a well-formed JSON tree replaces dozens of file writes. Don't iterate per-file.

---

## 3. `generate_code` Input Schema (full)

```jsonc
{
  // REQUIRED
  "language": "python",  // one of: typescript|python|go|csharp|java|kotlin|groovy|scala|swift|php|rust

  // Optional top-level
  "packageName": "...",        // module/package name. Java/Kotlin/Groovy default 'com.metaengine.generated'; Go default 'github.com/metaengine/demo'. For Python, see §4.
  "outputPath": ".",           // directory to write files; default current dir
  "skipExisting": true,        // default true — don't overwrite existing files (stub-friendly)
  "dryRun": false,             // when true: returns file contents in response, writes nothing
  "initialize": false,         // when true: properties get default-value initializers

  // Type definitions (each is an array; arrays are concatenated if repeated within one call)
  "classes":     [ /* ClassDef */ ],
  "interfaces":  [ /* InterfaceDef */ ],
  "enums":       [ /* EnumDef */ ],
  "customFiles": [ /* CustomFileDef */ ],

  // Virtual types (no files generated; used by typeIdentifier reference)
  "arrayTypes":               [ /* ArrayTypeDef */ ],
  "dictionaryTypes":          [ /* DictionaryTypeDef */ ],
  "concreteGenericClasses":   [ /* ConcreteGenericDef */ ],
  "concreteGenericInterfaces":[ /* ConcreteGenericDef */ ]
}
```

### 3.1 ClassDef
```jsonc
{
  "name": "User",                          // class name (PascalCase)
  "typeIdentifier": "user",                // unique kebab-case ID for cross-refs
  "comment": "Domain user entity",         // class-level docstring
  "path": "domain/users",                  // sub-directory under outputPath
  "fileName": "user_entity",               // override filename (no extension)
  "isAbstract": false,                     // emits ABC class in Python
  "baseClassTypeIdentifier": "base-entity",// extends another type from this batch
  "interfaceTypeIdentifiers": ["repo"],    // implements these interfaces (Python: ABC inheritance)
  "genericArguments": [ /* GenericArg */ ],
  "constructorParameters": [ /* CtorParam */ ],
  "properties": [ /* PropertyDef */ ],
  "customCode": [ /* CustomCodeBlock */ ],
  "customImports": [ /* CustomImport */ ],
  "decorators": [ /* DecoratorDef */ ]
}
```

### 3.2 InterfaceDef (same shape, with `customCode[]` for method signatures)
For Python, interfaces become ABC classes (or Protocol-style depending on engine; treat as abstract base). Define method signatures via `customCode` (NOT as function-typed properties).

### 3.3 EnumDef
```jsonc
{
  "name": "OrderStatus",
  "typeIdentifier": "order-status",
  "comment": "...",
  "fileName": "order_status",       // optional
  "path": "domain/order",           // optional
  "members": [
    { "name": "Pending", "value": 0 },
    { "name": "Shipped", "value": 2 }
  ]
}
```
- Python emits a subclass of `enum.Enum` (or `IntEnum` when all values are integers — confirmed engine behavior for languages with auto-import of `enum`).
- Member casing is **language-aware**: Python idiomatic is `UPPER_SNAKE_CASE`. The engine performs this transformation automatically (judges/snapshots in the harness explicitly tolerate it; do **not** force lowercase). Java does the same with `ALL_CAPS`; Python with `UPPER_SNAKE`. Stick with the natural casing in the spec — engine will idiomize.

### 3.4 PropertyDef
```jsonc
{
  "name": "email",                  // property/field name (engine snake_cases for Python)
  "comment": "User email address",  // docstring
  "primitiveType": "String",        // String | Number | Boolean | Date | Any
  "type": "Decimal",                // OR: explicit string for non-primitive types
  "typeIdentifier": "address",      // OR: ref to another generated type
  "isOptional": false,              // Python: emits Optional[T]
  "isInitializer": false,           // adds default value (e.g., field(default_factory=...))
  "decorators": [ /* DecoratorDef */ ],
  "templateRefs": [ /* TemplateRef */ ],   // when `type` contains $placeholders
  "commentTemplateRefs": [ /* TemplateRef */ ]
}
```
**Use exactly one** of `primitiveType` / `type` / `typeIdentifier`.

### 3.5 CustomCodeBlock
```jsonc
{
  "code": "def get_full_name(self) -> str:\n    return f\"{self.first_name} {self.last_name}\"",
  "templateRefs": [
    { "placeholder": "$user", "typeIdentifier": "user" }
  ]
}
```
**Python-critical**: see §4.5 for indentation rules. Each block = exactly one method/field.

### 3.6 GenericArg
```jsonc
{
  "name": "T",                              // type parameter name
  "constraintTypeIdentifier": "base-entity",// upper-bound (Python: TypeVar bound)
  "propertyName": "items",                  // optional: auto-creates property of type T
  "isArrayProperty": true                   // makes the auto-property a list[T]
}
```

### 3.7 CtorParam
```jsonc
{
  "name": "email",
  "primitiveType": "String",   // or
  "type": "Decimal",           // or
  "typeIdentifier": "address"
}
```

### 3.8 ArrayTypeDef
```jsonc
{
  "typeIdentifier": "user-list",
  "elementPrimitiveType": "String",   // OR
  "elementTypeIdentifier": "user"
}
```
Python rendering: `list[User]` / `List[User]` (typing auto-imported).

### 3.9 DictionaryTypeDef
```jsonc
{
  "typeIdentifier": "user-lookup",
  "keyPrimitiveType": "String",       // or keyTypeIdentifier / keyType
  "valuePrimitiveType": "Number",     // or valueTypeIdentifier
}
```
Python: `dict[K, V]` / `Dict[K, V]`.

### 3.10 ConcreteGenericDef
```jsonc
{
  "identifier": "user-repo-concrete",
  "genericClassIdentifier": "repo-generic",
  "genericArguments": [ { "typeIdentifier": "user" } ]
}
```
Reference via `baseClassTypeIdentifier` or `templateRefs.typeIdentifier`. NEVER emits a file.

### 3.11 CustomFileDef
```jsonc
{
  "name": "types",            // filename (no extension)
  "path": "shared",
  "identifier": "shared-types",  // optional — lets other files import via customImports
  "fileName": "types",        // optional override
  "customCode": [ { "code": "UserId = str" } ],
  "customImports": [ { "path": "decimal", "types": ["Decimal"] } ]
}
```
Use for module-level type aliases, constants, or free functions in Python.

### 3.12 CustomImport
```jsonc
{ "path": "httpx", "types": ["AsyncClient"] }
```
Python emits `from httpx import AsyncClient`. The `path` is the import source; `types` is the symbol list.

### 3.13 DecoratorDef
```jsonc
{
  "code": "@dataclass(frozen=True)",
  "templateRefs": [ /* TemplateRef */ ]
}
```

### 3.14 TemplateRef
```jsonc
{ "placeholder": "$user", "typeIdentifier": "user" }
```
Inside any `code` / `type` string, the literal `$user` (or whatever placeholder) is substituted with the resolved Python type name AND its import is auto-emitted.

---

## 4. Python-Specific Notes

### 4.1 `packageName` / Module Naming
- Defaults: not documented as a Python-specific default. Pass an explicit `packageName` if multi-module layout is desired. For a flat layout (single package), omit `packageName` and rely on `path` per-file.
- Python is **path-driven**, not namespace-driven. A class with `"path": "domain/users"` lands at `<outputPath>/domain/users/<file>.py`.
- The engine idiomizes file names to **`snake_case`** (e.g., `OrderStatus` → `order_status.py`). You can override via `fileName`.
- If you need an `__init__.py`, generate it via `customFiles` with `name: "__init__"`.

### 4.2 File Path Layout
For a class `name: "OrderRepository"`, `path: "domain/orders"`, `outputPath: "src"`:
- Written to `src/domain/orders/order_repository.py`
- Module-level `from .order import Order` (or absolute, depending on `packageName`) auto-emitted for cross-references resolved via `typeIdentifier` / `templateRefs`.

Enums: file gets the snake_cased enum name (e.g., `order_status.py`), not a TS-style `.enum.` suffix.

### 4.3 Type Mapping (primitive → Python)
| `primitiveType` | Python type emitted             | Notes |
|------------------|---------------------------------|-------|
| `String`         | `str`                           | |
| `Number`         | `int` (per engine convention)   | If you need a float/Decimal, use `"type": "float"` or `"type": "Decimal"` (Decimal is auto-imported). |
| `Boolean`        | `bool`                          | |
| `Date`           | `datetime.datetime`             | `datetime` module is auto-imported. If a date-only is required, use `"type": "date"` (still resolved via `datetime` import). |
| `Any`            | `Any`                           | from `typing` (auto-imported) |

**Rule of thumb for non-integer numbers**: don't use `primitiveType: "Number"` — be explicit with `"type": "float"`, `"type": "Decimal"`, or `"type": "int"`.

For DDD value objects that semantically represent monetary values, prefer `"type": "Decimal"`.

### 4.4 Dataclasses vs Plain Classes
- Default emitted Python class is a **plain class** with typed attributes (no `@dataclass` unless you add it).
- To get `@dataclass`, add a class-level decorator:
  ```jsonc
  "decorators": [ { "code": "@dataclass" } ]
  ```
  `dataclass` is auto-imported from `dataclasses` — do NOT add it to `customImports`.
- For frozen / kw_only / slots use `"@dataclass(frozen=True, slots=True)"` etc.
- For pydantic models, use `baseClassTypeIdentifier` referencing a class you defined OR add `BaseModel` directly via `customImports`-free path: `pydantic` is auto-imported, so a `customCode` block like `class UserModel(BaseModel): ...` works, but the cleaner pattern is to declare a regular class and add the right base.

**Recommended default for DDD entities**: plain class with typed attributes + `customCode` for behavior. Use `@dataclass` when the spec describes a value object (immutable, equality-by-value).

### 4.5 Enums
- Default Python output: subclass of `enum.Enum` with the supplied `members[]`.
- All member values in the schema are numeric (`value: number`). The engine maps them to integer enum values; for an `IntEnum`, no extra config is needed if all values are integers (engine picks the idiomatic base).
- Member names are idiomized to `UPPER_SNAKE_CASE` (e.g., `Pending` → `PENDING`, `OrderShipped` → `ORDER_SHIPPED`). Don't fight this — the harness's judge tolerates it.
- File: `<snake_case_name>.py` at `path` if specified.
- To reference an enum from a property: `{ "typeIdentifier": "<enum-id>" }`. Auto-imports the enum class.

### 4.6 Method Stub Bodies (customCode indentation)
**CRITICAL — Python-only quirk** documented explicitly in the AI guide:
> Python: must provide explicit indentation (4 spaces) after `\n` in customCode.

Other languages get auto-indented; Python does not. Every `customCode` block that defines a method must include the body indented with 4 spaces:

```jsonc
{
  "code": "def total(self) -> Decimal:\n    return sum(line.amount for line in self.lines)"
}
```

**Stub-body convention** (when no behavior is provided in the spec):
- Use `raise NotImplementedError` to mark intentionally-unimplemented methods. This is the safer default for DDD interfaces / abstract methods because passing tests / type-checkers will catch a forgotten implementation.
- `pass` is acceptable for methods that legitimately have no body (e.g., a no-op default).
- For abstract classes (`isAbstract: true`) or interface (ABC) method signatures, the convention is:
  ```jsonc
  { "code": "@abstractmethod\ndef find_by_id(self, id: str) -> Optional[$user]:\n    ...",
    "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
  ```
  Note `...` (Ellipsis literal) is the idiomatic body for an abstract stub. `abstractmethod` and `ABC` come from auto-imported `abc`.

**Newlines**: `\n` between blocks is added automatically. Inside one block, embed `\n    ` for body lines.

### 4.7 Optional / Nullable
`isOptional: true` on a property → emits `Optional[T]` (Python `typing.Optional`, auto-imported). With `isInitializer: true` you also get a default (typically `= None`).

### 4.8 Collections
- Prefer `arrayTypes` for "list of X" reused across the spec; reference via `typeIdentifier`.
- One-off lists of primitives in a `type` string: `"type": "list[str]"` works (Python 3.9+ generics). For older-target output use `"type": "List[str]"` (List is auto-imported from `typing`).
- Same for `dict[K,V]` / `Dict[K,V]`.

### 4.9 Dependency Injection / Decorators
- Class-level decorators (e.g., `@dataclass`, `@final`) go in `decorators[]`.
- Method-level decorators (e.g., `@staticmethod`, `@classmethod`, `@property`, `@abstractmethod`) are written inline in the `customCode.code` string before the `def`.

### 4.10 Reserved Words to Avoid
Don't use Python keywords as property names: `class`, `import`, `from`, `lambda`, `return`, `def`, `pass`, `as`, `is`, `in`, `not`, `and`, `or`, `if`, `else`, `elif`, `while`, `for`, `try`, `except`, `finally`, `with`, `yield`, `global`, `nonlocal`, `raise`, `del`, `assert`, `async`, `await`, `True`, `False`, `None`. Substitute `clazz`, `importData`, `from_addr`, etc.

---

## 5. Output Structure Produced

`generate_code` returns:
- When `dryRun: false` (default): files written to `outputPath/<path>/<filename>.py`. Response confirms file count + paths.
- When `dryRun: true`: response includes generated file contents so they can be reviewed without disk writes.
- File list includes:
  - One file per `classes[]` entry
  - One file per `interfaces[]` entry
  - One file per `enums[]` entry
  - One file per `customFiles[]` entry
  - **No** files for `arrayTypes`, `dictionaryTypes`, `concreteGenericClasses`, `concreteGenericInterfaces`

Imports between generated files are computed automatically based on `typeIdentifier` references and `templateRefs`. Manual `customImports` are appended only for items not auto-resolved.

---

## 6. Worked Python Patterns (mental templates)

### 6.1 Plain entity with cross-ref
```jsonc
{
  "language": "python",
  "outputPath": "src",
  "classes": [
    { "name": "Address", "typeIdentifier": "address",
      "properties": [
        { "name": "street", "primitiveType": "String" },
        { "name": "city",   "primitiveType": "String" }
      ]
    },
    { "name": "User", "typeIdentifier": "user",
      "properties": [
        { "name": "id",       "primitiveType": "String" },
        { "name": "address",  "typeIdentifier": "address" },
        { "name": "createdAt","primitiveType": "Date" }
      ]
    }
  ]
}
```
Produces `src/address.py` and `src/user.py` with `from .address import Address` in user.py.

### 6.2 Dataclass value object
```jsonc
{
  "name": "Money", "typeIdentifier": "money",
  "decorators": [ { "code": "@dataclass(frozen=True)" } ],
  "properties": [
    { "name": "amount",   "type": "Decimal" },
    { "name": "currency", "primitiveType": "String" }
  ]
}
```

### 6.3 Enum + class using it
```jsonc
{
  "enums": [
    { "name": "OrderStatus", "typeIdentifier": "order-status",
      "members": [
        { "name": "Pending", "value": 0 },
        { "name": "Paid",    "value": 1 },
        { "name": "Shipped", "value": 2 }
      ]
    }
  ],
  "classes": [
    { "name": "Order", "typeIdentifier": "order",
      "properties": [
        { "name": "id",     "primitiveType": "String" },
        { "name": "status", "typeIdentifier": "order-status" }
      ],
      "customCode": [
        { "code": "def mark_shipped(self) -> None:\n    self.status = $status.SHIPPED",
          "templateRefs": [ { "placeholder": "$status", "typeIdentifier": "order-status" } ] }
      ]
    }
  ]
}
```

### 6.4 Abstract repository (ABC)
```jsonc
{
  "interfaces": [{
    "name": "UserRepository", "typeIdentifier": "user-repo",
    "customCode": [
      { "code": "@abstractmethod\ndef find_by_id(self, id: str) -> Optional[$user]:\n    ...",
        "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] },
      { "code": "@abstractmethod\ndef save(self, user: $user) -> None:\n    ...",
        "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
    ]
  }],
  "classes": [
    { "name": "User", "typeIdentifier": "user",
      "properties": [{ "name": "id", "primitiveType": "String" }] },
    { "name": "InMemoryUserRepository", "typeIdentifier": "mem-repo",
      "interfaceTypeIdentifiers": ["user-repo"],
      "customCode": [
        { "code": "def __init__(self) -> None:\n    self._store: dict[str, $user] = {}",
          "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] },
        { "code": "def find_by_id(self, id: str) -> Optional[$user]:\n    return self._store.get(id)",
          "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] },
        { "code": "def save(self, user: $user) -> None:\n    self._store[user.id] = user",
          "templateRefs": [{ "placeholder": "$user", "typeIdentifier": "user" }] }
      ]
    }
  ]
}
```

### 6.5 Service with external dependency
```jsonc
{
  "classes": [{
    "name": "EmailNotifier", "typeIdentifier": "email-notifier",
    "path": "infrastructure/notifications",
    "customImports": [
      { "path": "httpx", "types": ["AsyncClient"] }
    ],
    "customCode": [
      { "code": "def __init__(self, client: AsyncClient) -> None:\n    self._client = client" },
      { "code": "async def send(self, to: str, subject: str, body: str) -> None:\n    await self._client.post(\"/email\", json={\"to\": to, \"subject\": subject, \"body\": body})" }
    ]
  }]
}
```

---

## 7. Common Mistakes (Python-tinted)

1. Forgetting 4-space indentation in `customCode` method bodies → invalid Python.
2. Using `primitiveType: "Number"` for monetary values → emits `int`. Use `"type": "Decimal"`.
3. Adding `from typing import Optional` to `customImports` → duplicate / conflict. typing is auto-imported.
4. Putting a method as a function-typed property on an interface → the implementing class will duplicate it. Use `customCode` for method signatures.
5. Naming a property `class` or `from` → syntax error. Substitute.
6. Splitting related entities across multiple `generate_code` calls → broken imports. Always batch.
7. Writing internal types as raw strings inside `code` (e.g., `def find(self) -> User:`) when `User` is in the same batch → no import generated. Use `$user` + `templateRefs`.
8. Adding `@dataclass` via `customImports` → duplicates the auto-import. Just put the decorator in `decorators[]`.
9. Mismatching `typeIdentifier` strings (typo) → property silently dropped. Verify each ref resolves.
10. Forcing lowercase Python enum members in the spec → engine still idiomizes to `UPPER_SNAKE_CASE`. Don't fight it.

---

## 8. Single-Call Mental Model (the headline)

Build the WHOLE spec in memory first:
- Walk the DDD model: entities, value objects, enums, repositories (interfaces), domain services, application services, aggregate roots.
- Assign each a `typeIdentifier` (kebab-case is conventional but any string works).
- Cross-reference via `typeIdentifier` / `baseClassTypeIdentifier` / `interfaceTypeIdentifiers` / `templateRefs`.
- Decide `path` per type for DDD layering (`domain`, `application`, `infrastructure`, `interfaces`).
- Issue **one** `generate_code` call.

If you discover a missing type after the call, prefer regenerating the full batch with `skipExisting: true` (default) so existing files are preserved while new ones are added — but ideally the spec is complete on the first attempt.

---

## 9. Quick Reference Card

| Need | Field |
|------|-------|
| String field | `{ "name": "...", "primitiveType": "String" }` |
| Decimal money field | `{ "name": "...", "type": "Decimal" }` |
| Optional field | `{ ..., "isOptional": true }` |
| List of T (reusable) | `arrayTypes[].typeIdentifier` then refer via `typeIdentifier` |
| Dict[K,V] (reusable) | `dictionaryTypes[]` then refer via `typeIdentifier` |
| Method | `customCode[]` with one entry per method, body indented 4 spaces |
| Method referring to in-batch type | `customCode[].code` uses `$ref`, plus `templateRefs[]` |
| Class-level decorator | `decorators[]` |
| Method-level decorator | inline in `customCode.code` (`@staticmethod\ndef ...`) |
| External lib | `customImports[]` |
| Abstract class | `isAbstract: true`; methods use `@abstractmethod` inline |
| Interface | `interfaces[]`, method signatures in `customCode[]` |
| Enum | `enums[]` with `members[]` (numeric values) |
| Type alias / module-level helper | `customFiles[]` |
| Inheritance | `baseClassTypeIdentifier` |
| Implements interface | `interfaceTypeIdentifiers: ["..."]` |
| Custom filename | `fileName: "..."` (no extension) |
| Subdirectory | `path: "domain/orders"` |

---

End of warmup. Generation session: build one comprehensive JSON spec, then call `mcp__metaengine__generate_code` exactly once.
