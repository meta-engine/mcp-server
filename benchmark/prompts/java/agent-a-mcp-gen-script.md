You are running the GENERATION session of a MetaEngine MCP benchmark — **Java** target.

A prior warmup session read the metaengine MCP's documentation and produced the knowledge brief that has been included in your user prompt above. Use that brief — you do NOT have access to `mcp__metaengine__metaengine_initialize` in this session.

OBJECTIVE
=========
Generate **Java** code for the DDD spec at:
  {{SPEC_PATH}}

Into directory:
  {{OUT_DIR}}

INVOCATION PATTERN (this arm — script-generated tool input)
============================================================
Instead of inlining the full MetaEngine spec into `generate_code` tool arguments, you will:

1. Write a small Python script — via a `Bash` heredoc (`cat > {{TMP_FILE}}.build.py <<'PYEOF'` … `PYEOF`) — that:
   - Reads the source DDD spec JSON at {{SPEC_PATH}}
   - Transforms each entry to MetaEngine schema (per the table below)
   - Writes the resulting MetaEngine spec JSON to {{TMP_FILE}}
2. Run the script via `Bash` (`python3 {{TMP_FILE}}.build.py`) so {{TMP_FILE}} exists on disk.
3. Call `mcp__metaengine__load_spec_from_file` with:
   - `specFilePath: "{{TMP_FILE}}"`
   - `outputPath: "{{OUT_DIR}}"`

The MCP server reads {{TMP_FILE}} from disk; its content is NOT passed through tool arguments. This keeps the large structured spec off the LLM's output-token channel — only the (much shorter) transformation logic in your script counts as output.

EXECUTE THESE STEPS — DO NOT NARRATE WHAT YOU PLAN; DO IT
==========================================================

1. Read the spec file at {{SPEC_PATH}} so you understand its shape.

2. Use a SINGLE `Bash` heredoc to create a Python script at {{TMP_FILE}}.build.py. The script must:
   - Read {{SPEC_PATH}}
   - For each spec entry, emit the corresponding MetaEngine entry per the SCHEMA TRANSLATION table below
   - Write the final dict as JSON to {{TMP_FILE}}
   - Set `language: "java"` and `packageName: "com.metaengine.demo"` at the top level

3. Run the script via Bash:  `python3 {{TMP_FILE}}.build.py`
   Verify the file exists: `test -s {{TMP_FILE}} && wc -c {{TMP_FILE}}`

4. Make ONE single `mcp__metaengine__load_spec_from_file` call:
   - `specFilePath: "{{TMP_FILE}}"`
   - `outputPath: "{{OUT_DIR}}"`

5. Verify with Bash that the output directory contains Java files:
       find {{OUT_DIR}} -name '*.java' | wc -l
   The number must be > 0 (the spec has ~70 entities; expect roughly that many files).

6. Output `DONE` only when {{OUT_DIR}} contains Java files.

SCHEMA TRANSLATION (apply for every spec entry — same as inline arm)
=====================================================================

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
- Do NOT inline the spec into `generate_code` tool arguments — that's a different arm. Use `load_spec_from_file` with a path.
- The script must compute the MetaEngine spec via Python logic (read source → transform → write JSON). Do NOT hardcode the entire spec as a giant Python string literal or `json.loads("""...""")` block — that just shifts the bytes from tool args to script content, defeating the purpose. The transformation logic should be short; only the input/output paths and a translation function.
- Do NOT call `mcp__metaengine__metaengine_initialize` (you can't anyway — not in allowed tools).
- Do NOT author the generated Java files yourself via Bash. Manual authorship invalidates the run; only the engine via `load_spec_from_file` may produce them.
- Do NOT use `interfaces[]` for aggregates or services. They MUST be `classes[]`.
- Reciting your understanding without calling `load_spec_from_file` IS A FAILED RUN.
- For multiple constructorParameters of the same primitive type (e.g. two Date fields), use `primitiveType: "Date"` for both — do NOT invent unique typeIdentifiers per parameter to disambiguate.
- Generated Java must compile cleanly under `javac --release 17` (or higher).
