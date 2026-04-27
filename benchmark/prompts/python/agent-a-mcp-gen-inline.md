You are running the GENERATION session of a MetaEngine MCP benchmark — **Python** target.

A prior warmup session read the metaengine MCP's documentation and produced the knowledge brief that has been included in your user prompt above. Use that brief — you do NOT have access to `mcp__metaengine__metaengine_initialize` in this session.

OBJECTIVE
=========
Generate **Python** code for the DDD spec at:
  {{SPEC_PATH}}

Into directory:
  {{OUT_DIR}}

EXECUTE THESE STEPS — DO NOT NARRATE WHAT YOU PLAN; DO IT
==========================================================

1. Read the spec file at {{SPEC_PATH}}.

2. Translate every spec entry to the corresponding MetaEngine schema using the table below.

3. Make ONE single `mcp__metaengine__generate_code` call passing the FULL translated spec — every type and every service from every domain in a single invocation. Splitting per-domain breaks the typegraph.

   On the call, set:
     - `language: "python"`
     - `packageName: "metaengine_demo"`
     - `outputPath: "{{OUT_DIR}}"`

4. Verify with Bash:
       find {{OUT_DIR}} -name '*.py' | wc -l
   Number must be > 0 (~70 files expected).

5. Output `DONE` only when {{OUT_DIR}} contains Python files.

SCHEMA TRANSLATION
===================

```
| Spec entry         | MetaEngine call shape                                          |
|--------------------|----------------------------------------------------------------|
| kind=aggregate     | classes[] with:                                                |
|   name=X           |   - name: X                                                    |
|   fields=[...]     |   - typeIdentifier: kebab-case(X)                              |
|                    |   - constructorParameters: from `fields` (engine emits the     |
|                    |     Python class with __init__ assigning fields, OR a          |
|                    |     @dataclass — engine's choice)                              |
|                    |   - path: "<domain>/aggregates"                                |
|                    |   - comment: "<X> aggregate root for the <domain> domain."     |
|--------------------|----------------------------------------------------------------|
| kind=value_object  | classes[] with:                                                |
|   name=X           |   - name: X                                                    |
|   fields=[...]     |   - typeIdentifier: kebab-case(X)                              |
|                    |   - constructorParameters: from `fields`                       |
|                    |   - path: "<domain>/value_objects"                              |
|                    |   - comment: "<X> value object."                               |
|--------------------|----------------------------------------------------------------|
| kind=enum          | enums[] with:                                                  |
|   name=X           |   - name: X                                                    |
|   members=[{...}]  |   - typeIdentifier: kebab-case(X)                              |
|                    |   - members: VERBATIM from spec.members ({name, value})        |
|                    |     — values are numeric integers                              |
|                    |   - path: "<domain>/enums"                                     |
|                    |   - comment: "<X> enum."                                       |
|--------------------|----------------------------------------------------------------|
| services[]         | classes[] (one per service) with:                              |
|   name=Y           |   - name: Y                                                    |
|   methods=[...]    |   - typeIdentifier: kebab-case(Y)                              |
|                    |   - customCode: ONE entry per method, body raises:            |
|                    |       {                                                        |
|                    |         "code": "def <name>(self, <params>) -> <ReturnType>:   |
|                    |                  raise NotImplementedError('not implemented')",|
|                    |         "templateRefs": [                                      |
|                    |           {"placeholder": "$Agg",                              |
|                    |            "typeIdentifier": "<agg-id>"}                       |
|                    |         ]                                                      |
|                    |       }                                                        |
|                    |   - path: "<domain>/services"                                  |
|                    |   - comment: "<Y> service."                                    |
```

typeIdentifier convention: kebab-case of the type name.
  Order        → "order"
  OrderLine    → "order-line"
  OrderStatus  → "order-status"
  OrderService → "order-service"

Path note: with `packageName: "metaengine_demo"`, expect engine output at:
  {{OUT_DIR}}/metaengine_demo/<your_path>/<file>.py

Type mapping (engine handles from `primitiveType`):
  String  → str
  Number  → float (or int)
  Boolean → bool
  Date    → datetime.datetime
  Any     → Any

CRITICAL — FAILURE MODES TO AVOID
==================================
- Do NOT split into multiple per-domain calls. ONE call with the full spec.
- Do NOT call `mcp__metaengine__metaengine_initialize`.
- Do NOT use `interfaces[]` for aggregates or services (in Python they should be classes).
- Do NOT use the `Write` tool to author code yourself.
- For multiple constructorParameters of the same primitive type (e.g. two Date fields), use `primitiveType: "Date"` for both — do NOT invent unique typeIdentifiers per parameter.
- Generated Python must pass `python -m py_compile` on every file.
