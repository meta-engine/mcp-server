You are running the GENERATION session of a MetaEngine MCP benchmark — **Java** target.

A prior warmup session read the metaengine MCP's documentation and produced the knowledge brief that has been included in your user prompt above. Use that brief — you do NOT have access to `mcp__metaengine__metaengine_initialize` in this session.

OBJECTIVE
=========
Generate **Java** code for the DDD spec at:
  {{SPEC_PATH}}

Into directory:
  {{OUT_DIR}}

EXECUTE THESE STEPS — DO NOT NARRATE WHAT YOU PLAN; DO IT
==========================================================

1. Read the spec file at {{SPEC_PATH}} so you have the full set of types and services in context.

2. Translate every spec entry to the corresponding MetaEngine schema using the table below. This is mandatory for the benchmark to be apples-to-apples with the baseline variant.

3. Make ONE single `mcp__metaengine__generate_code` call passing the FULL translated spec — every type and every service from every domain in a single invocation. Splitting per-domain breaks the typegraph (cross-references won't resolve).

   On the call, set:
     - `language: "java"`
     - `packageName: "com.metaengine.demo"`
     - `outputPath: "{{OUT_DIR}}"`

4. Verify with Bash that the output directory contains Java files:
       find {{OUT_DIR}} -name '*.java' | wc -l
   The number must be > 0 (the spec has ~70 entities; expect roughly that many files).

5. Output `DONE` only when {{OUT_DIR}} contains Java files.

SCHEMA TRANSLATION (apply for every spec entry)
================================================

```
| Spec entry         | MetaEngine call shape                                          |
|--------------------|----------------------------------------------------------------|
| kind=aggregate     | classes[] with:                                                |
|   name=X           |   - name: X                                                    |
|   fields=[...]     |   - typeIdentifier: kebab-case(X)                              |
|                    |   - constructorParameters: from `fields` (engine emits the     |
|                    |     Java class with appropriate field declarations + ctor)     |
|                    |   - path: "<domain>/aggregates"                                 |
|                    |   - comment: "<X> aggregate root for the <domain> domain."     |
|--------------------|----------------------------------------------------------------|
| kind=value_object  | classes[] with:                                                |
|   name=X           |   - name: X                                                    |
|   fields=[...]     |   - typeIdentifier: kebab-case(X)                              |
|                    |   - constructorParameters: from `fields`                       |
|                    |   - path: "<domain>/value_objects"                              |
|                    |   - comment: "<X> value object."                               |
|                    |   (Use class — same shape as aggregate. Engine may emit a     |
|                    |    record for Java 14+; either is acceptable to the judge.)   |
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
|                    |   - customCode: ONE entry per method, body throws:            |
|                    |       {                                                        |
|                    |         "code": "public <ReturnType> <name>(<params>) {        |
|                    |                  throw new UnsupportedOperationException(      |
|                    |                  \"not implemented\"); }",                     |
|                    |         "templateRefs": [                                      |
|                    |           {"placeholder": "$Agg",                              |
|                    |            "typeIdentifier": "<agg-id>"}                       |
|                    |         ]                                                      |
|                    |       }                                                        |
|                    |     For any reference to the domain's aggregate inside the     |
|                    |     method signature, use a $placeholder + templateRefs entry. |
|                    |   - path: "<domain>/services"                                  |
|                    |   - comment: "<Y> service."                                    |
```

typeIdentifier convention: kebab-case of the type name.
  Order        → "order"
  OrderLine    → "order-line"
  OrderStatus  → "order-status"
  OrderService → "order-service"

Path note: paths are relative to outputPath. With `packageName: "com.metaengine.demo"`, the engine will produce files at:
  {{OUT_DIR}}/com/metaengine/demo/<your_path>/<File>.java

So `path: "ordering/aggregates"` → file at `com/metaengine/demo/ordering/aggregates/Order.java`.

Type mapping notes (engine handles these from `primitiveType`):
  String  → String
  Number  → double (or appropriate numeric primitive)
  Boolean → boolean
  Date    → java.time.Instant or java.time.LocalDateTime (engine's choice)
  Any     → Object

CRITICAL — FAILURE MODES TO AVOID
==================================
- Do NOT split into multiple per-domain calls. ONE call with the full spec.
- Do NOT call `mcp__metaengine__metaengine_initialize` (you can't anyway — not in allowed tools).
- Do NOT use `interfaces[]` for aggregates or services. They MUST be `classes[]` so they get encapsulation and method bodies. An interface declaration is not equivalent to a class with stub bodies.
- Do NOT use the `Write` tool to author code yourself. Manual authorship invalidates the run.
- Reciting your understanding without calling generate_code IS A FAILED RUN.
- For multiple constructorParameters of the same primitive type (e.g. two Date fields), use `primitiveType: "Date"` for both — do NOT invent unique typeIdentifiers per parameter to disambiguate.
- Generated Java must compile cleanly under `javac --release 17` (or higher).
