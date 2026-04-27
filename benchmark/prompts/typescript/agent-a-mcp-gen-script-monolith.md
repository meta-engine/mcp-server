You are running the GENERATION session of a MetaEngine MCP benchmark.

A prior warmup session read the metaengine MCP's documentation and produced the knowledge brief that has been included in your user prompt above. Use that brief — you do NOT have access to `mcp__metaengine__metaengine_initialize` in this session.

OBJECTIVE
=========
Generate TypeScript code for the **modular-monolith** spec at:
  {{SPEC_PATH}}

Into directory:
  {{OUT_DIR}}

INVOCATION PATTERN (this arm — script-generated tool input)
============================================================
Instead of inlining the full MetaEngine spec into `generate_code` tool arguments, you will:

1. Write a Python script (via `Bash` heredoc) that reads the source modular-monolith spec at {{SPEC_PATH}} and produces a MetaEngine spec at {{TMP_FILE}}.
2. Run the script via `Bash` so {{TMP_FILE}} exists on disk.
3. Call `mcp__metaengine__load_spec_from_file` with `specFilePath: "{{TMP_FILE}}"` and `outputPath: "{{OUT_DIR}}"`.

The MCP server reads {{TMP_FILE}} from disk; its content is NOT passed through tool arguments. This keeps the structured spec off the LLM's output-token channel.

SPEC SHAPE (modular-monolith)
=============================
```
{
  "shape": "modular-monolith",
  "modules": [
    { "name": "<mod>", "path": "<module-path>",
      "types":    [ {kind, name, fields|members} ],
      "services": [ {name, methods} ] }
  ],
  "orchestrators": {
    "name": "orchestrators", "path": "orchestrators",
    "services": [ {name, methods} ]    // methods reference types from MULTIPLE modules
  }
}
```

Modules can have nested sub-module paths (e.g. `"orders/cart"`). Some modules are flat, some have sub-modules. A `"shared"` kernel holds types referenced from many modules.

**Cross-module references in field / parameter / return entries are annotated with `module: "<path>"`.** Your script MUST translate these into `templateRefs` entries — that's the most error-prone part of this transformation, and the part the prompt is being explicit about so you handle it correctly.

EXECUTE THESE STEPS — DO NOT NARRATE WHAT YOU PLAN; DO IT
==========================================================

1. Read the spec file at {{SPEC_PATH}} so you understand its shape.

2. Use a SINGLE `Bash` heredoc to create a Python script at {{TMP_FILE}}.build.py. The script must:
   - Read {{SPEC_PATH}}
   - Walk `modules[]` (including any `submodules` if present — paths are stored in `path`)
   - For each type, emit the corresponding MetaEngine entry (table below)
   - Walk `orchestrators.services[]` and emit each as a class with cross-module `templateRefs`
   - Write the final dict as JSON to {{TMP_FILE}} (single object with `classes`, `interfaces`, `enums` arrays)
   - Set `language: "typescript"` at the top level

3. Run the script via Bash:  `python3 {{TMP_FILE}}.build.py`
   Verify the file exists: `test -s {{TMP_FILE}} && wc -c {{TMP_FILE}}`

4. Make ONE single `mcp__metaengine__load_spec_from_file` call:
   - `specFilePath: "{{TMP_FILE}}"`
   - `outputPath: "{{OUT_DIR}}"`

5. Verify the output dir contains TypeScript files:
       find {{OUT_DIR}} -name '*.ts' | wc -l
   The number must be > 0.

6. Output `DONE` only when {{OUT_DIR}} contains TypeScript files.

SCHEMA TRANSLATION (mechanical — apply per module)
====================================================

For every type in `modules[].types`:

```
| kind         | MetaEngine entry                                                     |
|--------------|----------------------------------------------------------------------|
| aggregate    | classes[]:                                                           |
|              |   name, typeIdentifier=kebab-case(name),                             |
|              |   constructorParameters from fields,                                 |
|              |   path = "src/<module.path>/aggregates"                              |
| value_object | interfaces[]:                                                        |
|              |   name, typeIdentifier=kebab-case(name),                             |
|              |   properties from fields,                                            |
|              |   path = "src/<module.path>/value-objects"                           |
| enum         | enums[]:                                                             |
|              |   name, typeIdentifier=kebab-case(name),                             |
|              |   members VERBATIM from spec.members,                                |
|              |   path = "src/<module.path>/enums"                                   |
```

For every service in `modules[].services` and `orchestrators.services`:

```
| services[]   | classes[]:                                                            |
|              |   name, typeIdentifier=kebab-case(name),                              |
|              |   customCode = [one entry per method],                                |
|              |   path = "src/<module.path>/services"  (or "src/orchestrators/services" for top-level)|
```

CROSS-MODULE REFERENCES — THE PART THAT MATTERS
=================================================
This is where transformer scripts most often have bugs. Your script MUST handle cross-module references explicitly. The pattern:

For each method's params and return:
- If the entry is a primitive (`type` is `"string"`, `"number"`, `"boolean"`, `"Date"` and there's no `module` field): emit it as `primitiveType: "String"` etc. **The engine handles the language-specific mapping — do NOT translate primitives yourself.**
- If the entry has a `module` field (cross-module reference): emit the corresponding `$placeholder` in the customCode body and add a `templateRefs` entry mapping that placeholder to the type's kebab-case `typeIdentifier`.
- If the entry has a non-primitive type with NO `module` field (same-module reference): same pattern — use a `$placeholder` and `templateRefs` entry. The engine resolves all typeIdentifiers globally.

Recommended script structure (sketch):

```python
def field_to_property(f):
    """Translate a field entry to MetaEngine property/parameter shape.
    Use SAME helper for value_object properties AND aggregate constructorParameters
    AND service method params — duplicating logic is the most common script bug."""
    if f["type"] in ("string", "number", "boolean", "Date"):
        prim = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}[f["type"]]
        return {"name": f["name"], "primitiveType": prim}
    # Non-primitive — could be same-module or cross-module; either way, use kebab-case typeIdentifier.
    return {"name": f["name"], "typeIdentifier": kebab(f["type"])}

def method_to_custom_code(method):
    """Build customCode entry. Replace ALL non-primitive types in the signature
    with $placeholders + templateRefs. Both `params` and `returns` may carry a
    `module` field for cross-module refs."""
    refs = {}  # placeholder -> typeIdentifier
    parts = []
    for p in method["params"]:
        if p["type"] in PRIMITIVES:
            parts.append(f"{p['name']}: {p['type']}")
        else:
            ph = f"${p['type']}"
            refs[ph] = kebab(p["type"])
            parts.append(f"{p['name']}: {ph}")
    # Returns can be a string ("Order") OR a dict ({"type": "Order", "module": "orders"}).
    ret = method["returns"]
    ret_type = ret["type"] if isinstance(ret, dict) else ret
    if ret_type in PRIMITIVES or ret_type == "void":
        ret_str = ret_type
    else:
        ph = f"${ret_type}"
        refs[ph] = kebab(ret_type)
        ret_str = ph
    code = f"{method['name']}({', '.join(parts)}): {ret_str} {{ throw new Error('not implemented'); }}"
    return {"code": code, "templateRefs": [{"placeholder": k, "typeIdentifier": v} for k, v in refs.items()]}
```

Use a UNIFIED helper for translating fields. Splitting field-translation into separate helpers (one for ctor params, one for properties) is the documented #1 cause of script-arm bugs.

CRITICAL — FAILURE MODES TO AVOID
==================================
- Do NOT inline the spec into `generate_code` tool arguments — that's a different arm.
- Do NOT call `mcp__metaengine__metaengine_initialize` (you can't anyway).
- The script must compute the MetaEngine spec via Python logic. Do NOT hardcode the entire MetaEngine spec as a giant Python string literal — that just shifts the bytes from tool args to script content, defeating the purpose.
- Do NOT author the generated TypeScript files yourself via Bash. Only the engine via `load_spec_from_file` may produce them.
- Do NOT use `interfaces[]` for aggregates. Aggregates MUST be `classes[]`.
- Do NOT use `interfaces[]` for services. Services MUST be `classes[]` with `customCode[]`.
- Do NOT translate primitive types yourself — use `primitiveType: "String"` etc.
- Do NOT skip cross-module templateRefs — orchestrators rely on them. Every non-primitive type in a method signature gets a placeholder + templateRefs entry.
- Generated TypeScript must compile cleanly under `tsc --noEmit --strict --target es2022`.
