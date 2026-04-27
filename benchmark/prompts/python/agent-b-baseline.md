You are running the baseline variant of a code-generation benchmark — **Python** target.

OBJECTIVE
=========
Generate **Python** code for the DDD spec located at:
  {{SPEC_PATH}}

Write all generated files into:
  {{OUT_DIR}}

INSTRUCTIONS
============
1. Read the spec file. It is a JSON document with this shape:

   {
     "domains": [
       {
         "name": "<domain>",
         "types": [
           {"name": "X", "kind": "aggregate" | "value_object",
            "fields": [{"name": "...", "type": "..."}]},
           {"name": "Y", "kind": "enum",
            "members": [{"name": "Pascal", "value": 0}, ...]}
         ],
         "services": [
           {"name": "Z", "methods": [{"name": "...", "params": [...], "returns": "..."}]}
         ]
       }
     ]
   }

2. For every type and every service in the spec, create a separate Python file using the `Write` tool. Do not skip any entity. Do not summarise or batch — every entity gets its own file.

OUTPUT STRUCTURE
================
Use module path `metaengine_demo.<domain>.<kind>` for every file. File path:

- `metaengine_demo/<domain>/aggregates/<snake_name>.py`     — for kind=aggregate
- `metaengine_demo/<domain>/value_objects/<snake_name>.py`  — for kind=value_object
- `metaengine_demo/<domain>/enums/<snake_name>.py`          — for kind=enum
- `metaengine_demo/<domain>/services/<snake_name>.py`       — for services

Where `<snake_name>` is `snake_case` of the entity name (e.g. `OrderLine` → `order_line`, `OrderService` → `order_service`).

Do NOT create `__init__.py` files — modern Python (PEP 420, 3.3+) supports implicit namespace packages, no init files needed.

STYLE
=====
- **Aggregates**: `class <Name>:` with `__init__(self, ...)` that takes all fields and assigns to attributes. Or `@dataclass` decorator (preferred for brevity). Type hints required on every parameter.
- **Value objects**: `@dataclass(frozen=True)` `class <Name>:` (immutable). Type hints on every field.
- **Enums**: `class <Name>(IntEnum):` (since values are int) with each member from spec.members:
  ```python
  from enum import IntEnum
  class OrderStatus(IntEnum):
      Draft = 0
      Placed = 1
      ...
  ```
- **Services**: `class <Name>:` with the methods from the spec; each method body must `raise NotImplementedError("not implemented")`. Method signatures must include `self` and full type hints.
- Type mapping from spec strings (use these exactly):
  - `"string"` → `str`
  - `"number"` → `float` (or `int` for clearly-integer fields)
  - `"Date"`   → `datetime.datetime` (add `from datetime import datetime`)
  - `"Partial<T>"` → `Optional[T]` (add `from typing import Optional`)
  - `"T | null"` → `Optional[T]`
  - `"T[]"`    → `list[T]`
  - `"void"`   → `None`
- Include a one-line module-level docstring and a class-level docstring on each top-level declaration.
- All imports must be explicit and resolve.
- Code must pass `python -m py_compile <file>` on every file.

When every file in the spec has been written, output exactly: `DONE` and stop.
