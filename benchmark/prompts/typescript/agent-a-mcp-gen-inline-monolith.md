You are running the GENERATION session of a MetaEngine MCP benchmark.

A prior warmup session read the metaengine MCP's documentation and produced the knowledge brief that has been included in your user prompt above. Use that brief — you do NOT have access to `mcp__metaengine__metaengine_initialize` in this session.

OBJECTIVE
=========
Generate TypeScript code for the **modular-monolith** spec at:
  {{SPEC_PATH}}

Into directory:
  {{OUT_DIR}}

INVOCATION PATTERN (this arm — inline tool arguments)
======================================================
Make ONE single `mcp__metaengine__generate_code` call with the full translated MetaEngine spec embedded directly as tool arguments.

SPEC SHAPE (modular-monolith)
=============================
The source spec has this top-level structure:

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

Modules can have nested sub-module paths (e.g. `"orders/cart"`, `"orders/fulfillment"`). The spec is intentionally not symmetric — some modules are flat (`"catalog"`, `"customers"`), some have sub-modules (`"orders"` with `"orders/cart"`, `"orders/checkout"`, `"orders/fulfillment"`). A `"shared"` kernel module contains types referenced from many modules (Money, Id, Currency, Timestamp, Result).

Cross-module references in field / parameter / return entries are annotated with `module: "<path>"` — that field tells you which module the type lives in. Same-module refs omit the field. **You must turn every cross-module ref into a `templateRefs` placeholder + corresponding kebab-case `typeIdentifier`** so the engine resolves the import path correctly.

EXECUTE THESE STEPS — DO NOT NARRATE WHAT YOU PLAN; DO IT
==========================================================

1. Read the spec file at {{SPEC_PATH}} so you have the full module tree, the orchestrators, and every type in context.

2. Translate every spec entry to the corresponding MetaEngine schema using the table below. Every entity gets a unique kebab-case `typeIdentifier` and an explicit `path` derived from the module's path.

3. Make ONE single `mcp__metaengine__generate_code` call passing the FULL translated spec — every type from every module (including sub-modules), every service, and the top-level orchestrators in a single invocation. Splitting per-module breaks the typegraph (cross-references won't resolve).

   Set `outputPath: "{{OUT_DIR}}"` on the call.

4. Verify with Bash that the output directory contains TypeScript files:
       find {{OUT_DIR}} -name '*.ts' | wc -l
   The number must be > 0.

5. Output `DONE` only when {{OUT_DIR}} contains TypeScript files.

SCHEMA TRANSLATION (apply for every spec entry)
================================================

For every type in `modules[].types`:

```
| Spec entry         | MetaEngine call shape                                           |
|--------------------|-----------------------------------------------------------------|
| kind=aggregate     | classes[] with:                                                 |
|                    |   - name: <Name>                                                |
|                    |   - typeIdentifier: kebab-case(<Name>)                          |
|                    |   - constructorParameters: from `fields` (Rule 6 — TS ctor      |
|                    |     params auto-become properties; do NOT also list them in     |
|                    |     properties[])                                               |
|                    |   - path: "src/<module.path>/aggregates"                        |
|                    |   - comment: "<Name> aggregate root for the <module.name> module."|
|--------------------|-----------------------------------------------------------------|
| kind=value_object  | interfaces[] with:                                              |
|                    |   - name: <Name>                                                |
|                    |   - typeIdentifier: kebab-case(<Name>)                          |
|                    |   - properties: from `fields`                                   |
|                    |   - path: "src/<module.path>/value-objects"                     |
|                    |   - comment: "<Name> value object."                             |
|--------------------|-----------------------------------------------------------------|
| kind=enum          | enums[] with:                                                   |
|                    |   - name: <Name>                                                |
|                    |   - typeIdentifier: kebab-case(<Name>)                          |
|                    |   - members: VERBATIM from spec.members ({name, value} pairs;   |
|                    |     numeric values; the engine doesn't accept string values)    |
|                    |   - path: "src/<module.path>/enums"                             |
|                    |   - comment: "<Name> enum."                                     |
```

For every service in `modules[].services` AND every orchestrator in `orchestrators.services`:

```
| services[]         | classes[] (one per service) with:                               |
|                    |   - name: <ServiceName>                                         |
|                    |   - typeIdentifier: kebab-case(<ServiceName>)                   |
|                    |   - customCode: ONE entry per method, body is a stub:           |
|                    |     {                                                           |
|                    |       "code": "<methodName>(<params>): <returnType> {           |
|                    |                  throw new Error('not implemented'); }",        |
|                    |       "templateRefs": [                                         |
|                    |         {"placeholder": "$X", "typeIdentifier": "<x-id>"},      |
|                    |         …                                                       |
|                    |       ]                                                         |
|                    |     }                                                           |
|                    |   - path: "src/<module.path>/services" for module-level services|
|                    |          "src/orchestrators/services" for orchestrators         |
|                    |   - comment: "<ServiceName> service."                           |
```

CROSS-MODULE REFERENCES — IMPORTANT
====================================
Whenever a field / param / return has a `module: "<path>"` annotation:
- The referenced type lives in module `<path>`. Replace it in the generated code with a `$placeholder`, and add a `templateRefs` entry mapping that placeholder to the type's kebab-case `typeIdentifier`.
- The engine resolves the import path correctly using the typeIdentifier — it knows where each entity was placed because every entity has an explicit `path`.

When a field is a primitive (`string`, `number`, `boolean`, `Date`):
- Use `primitiveType: "String"` (or "Number" / "Boolean" / "Date"). Do NOT translate to a TS type yourself; the engine handles the language mapping.

When a field/param/return has a non-primitive type with NO `module` annotation:
- It's a same-module reference. Use the type's kebab-case typeIdentifier with the standard same-module ref form.

EXAMPLE — orchestrator method customCode entry
================================================
For `CheckoutOrchestrator.placeOrder(cartId: Id [shared], customerId: Id [shared], paymentMethodId: PaymentMethod [customers]): Order [orders]`:

```json
{
  "code": "placeOrder(cartId: $Id, customerId: $Id, paymentMethodId: $PaymentMethod): $Order { throw new Error('not implemented'); }",
  "templateRefs": [
    {"placeholder": "$Id",            "typeIdentifier": "id"},
    {"placeholder": "$PaymentMethod", "typeIdentifier": "payment-method"},
    {"placeholder": "$Order",         "typeIdentifier": "order"}
  ]
}
```

Note: `$Id` appears twice in the signature but is declared once in `templateRefs` — the engine substitutes it everywhere.

CRITICAL — FAILURE MODES TO AVOID
==================================
- Do NOT split into multiple per-module calls. ONE call with the full spec.
- Do NOT use `mcp__metaengine__load_spec_from_file` — that's a different arm.
- Do NOT use `interfaces[]` for aggregates. Aggregates MUST be `classes[]` with `constructorParameters`.
- Do NOT use `interfaces[]` for services. Services MUST be `classes[]` with `customCode[]` method stubs.
- Do NOT translate primitive types yourself — use `primitiveType: "String"` etc.
- Do NOT skip `templateRefs` entries for cross-module references — orchestrators rely on them.
- Do NOT use the `Write` tool to author code yourself. Manual authorship invalidates the run.
- Generated TypeScript must compile cleanly under `tsc --noEmit --strict --target es2022`.
