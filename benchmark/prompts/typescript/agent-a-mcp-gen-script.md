You are running the GENERATION session of a MetaEngine MCP benchmark.

A prior warmup session read the metaengine MCP's documentation and produced the knowledge brief that has been included in your user prompt above. Use that brief — you do NOT have access to `mcp__metaengine__metaengine_initialize` in this session.

OBJECTIVE
=========
Generate TypeScript code for the DDD spec at:
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
   - Write the final dict as JSON to {{TMP_FILE}} (single object with `classes`, `interfaces`, `enums` arrays — the input shape `mcp__metaengine__load_spec_from_file` expects)
   - Set `language: "typescript"` at the top level

3. Run the script via Bash:  `python3 {{TMP_FILE}}.build.py`
   Verify the file exists: `test -s {{TMP_FILE}} && wc -c {{TMP_FILE}}`

4. Make ONE single `mcp__metaengine__load_spec_from_file` call:
   - `specFilePath: "{{TMP_FILE}}"`
   - `outputPath: "{{OUT_DIR}}"`

5. Verify with Bash that the output directory contains TypeScript files:
       find {{OUT_DIR}} -name '*.ts' | wc -l
   The number must be > 0 (the spec has ~70 entities; expect roughly that many files).

6. Output `DONE` only when {{OUT_DIR}} contains TypeScript files.

SCHEMA TRANSLATION (apply for every spec entry — same as other arms)
=====================================================================

```
| Spec entry         | MetaEngine call shape                                          |
|--------------------|----------------------------------------------------------------|
| kind=aggregate     | classes[] with:                                                |
|   name=X           |   - name: X                                                    |
|   fields=[...]     |   - typeIdentifier: kebab-case(X)   (e.g. "order-line")        |
|                    |   - constructorParameters: from `fields` (Rule 6 — TS ctor    |
|                    |     params auto-become properties; do NOT also list them in    |
|                    |     properties[])                                              |
|                    |   - path: "src/domain/<domain>/aggregates"                     |
|                    |   - comment: "<X> aggregate root for the <domain> domain."     |
|--------------------|----------------------------------------------------------------|
| kind=value_object  | interfaces[] with:                                             |
|   name=X           |   - name: X                                                    |
|   fields=[...]     |   - typeIdentifier: kebab-case(X)                              |
|                    |   - properties: from `fields`                                  |
|                    |   - path: "src/domain/<domain>/value-objects"                  |
|                    |   - comment: "<X> value object."                               |
|--------------------|----------------------------------------------------------------|
| kind=enum          | enums[] with:                                                  |
|   name=X           |   - name: X                                                    |
|   members=[{...}]  |   - typeIdentifier: kebab-case(X)                              |
|                    |   - members: VERBATIM from spec.members (each {name, value})   |
|                    |     — values are numeric integers (engine schema requires it)  |
|                    |   - path: "src/domain/<domain>/enums"                          |
|                    |   - comment: "<X> enum."                                       |
|--------------------|----------------------------------------------------------------|
| services[]         | classes[] (one per service) with:                              |
|   name=Y           |   - name: Y                                                    |
|   methods=[...]    |   - typeIdentifier: kebab-case(Y)                              |
|                    |   - customCode: ONE entry per method, body is a stub:         |
|                    |       {                                                        |
|                    |         "code": "<methodName>(<params>): <returnType> {        |
|                    |                  throw new Error('not implemented'); }",       |
|                    |         "templateRefs": [                                      |
|                    |           {"placeholder": "$Agg",                              |
|                    |            "typeIdentifier": "<agg-id>"}                       |
|                    |         ]                                                      |
|                    |       }                                                        |
|                    |     For any reference to the domain's aggregate (Order, User,  |
|                    |     etc.) inside the method signature, use a $placeholder and  |
|                    |     a templateRefs entry — this gives you correct imports for  |
|                    |     free.                                                      |
|                    |   - path: "src/domain/<domain>/services"                       |
|                    |   - comment: "<Y> service."                                    |
```

typeIdentifier convention: kebab-case of the type name.
  Order        → "order"
  OrderLine    → "order-line"
  OrderStatus  → "order-status"
  OrderService → "order-service"

Example service customCode entry (for OrderService.create):
```json
{
  "code": "create(input: Partial<$Order>): $Order { throw new Error('not implemented'); }",
  "templateRefs": [{"placeholder": "$Order", "typeIdentifier": "order"}]
}
```

CRITICAL — FAILURE MODES TO AVOID
==================================
- Do NOT inline the spec into `generate_code` tool arguments — that defeats the purpose of this arm. Use `load_spec_from_file` with a path.
- Do NOT call `mcp__metaengine__metaengine_initialize` (you can't anyway — not in allowed tools).
- The script must compute the MetaEngine spec via Python logic (read source → transform → write JSON). Do NOT hardcode the entire spec as a giant Python string literal or `json.loads("""...""")` block — that just shifts the bytes from tool args to script content, defeating the purpose. The transformation logic should be short; only the input/output paths and a translation function.
- Do NOT author the generated TypeScript files yourself via Bash. Manual authorship (e.g. `cat > foo.ts <<EOF`) invalidates the run; only the engine via `load_spec_from_file` may produce them.
- Do NOT use `interfaces[]` for aggregates. Aggregates MUST be `classes[]` with `constructorParameters` so they get encapsulation.
- Do NOT use `interfaces[]` for services. Services MUST be `classes[]` with `customCode[]` method stubs.
- Reciting your understanding without calling `load_spec_from_file` IS A FAILED RUN.
- Generated TypeScript must compile cleanly under `tsc --noEmit --strict --target es2022`.
