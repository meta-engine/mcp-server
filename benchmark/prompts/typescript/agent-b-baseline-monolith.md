You are running the baseline variant of a code-generation benchmark.

OBJECTIVE
=========
Generate TypeScript code for the **modular-monolith** spec located at:
  {{SPEC_PATH}}

Write all generated files into:
  {{OUT_DIR}}

INSTRUCTIONS
============
1. Read the spec file. It is a JSON document with this shape:

   {
     "shape": "modular-monolith",
     "modules": [
       {
         "name": "<mod>",
         "path": "<module-path>",                  // e.g. "catalog", "orders/cart" — asymmetric depth
         "types": [
           {"name": "X", "kind": "aggregate" | "value_object",
            "fields": [{"name": "...", "type": "...", "module"?: "..."}]},
           {"name": "Y", "kind": "enum",
            "members": [{"name": "Pascal", "value": 0}, ...]}
         ],
         "services": [
           {"name": "Z", "methods": [
             {"name": "...", "params": [{"name": "...", "type": "...", "module"?: "..."}],
              "returns": "..." | {"type": "...", "module": "..."}}
           ]}
         ]
       }
     ],
     "orchestrators": {
       "name": "orchestrators", "path": "orchestrators",
       "services": [ {name, methods} ]   // methods reference types from MULTIPLE modules
     }
   }

   Some modules are flat (`"catalog"`, `"customers"`, `"billing"`); some have sub-modules (`"orders"` + `"orders/cart"`, `"orders/checkout"`, `"orders/fulfillment"`). A `"shared"` kernel holds types referenced from many modules.

2. For every type and every service (in modules and in orchestrators), create a separate TypeScript file using the `Write` tool. Do not skip any entity. Do not summarise or batch — every entity gets its own file.

OUTPUT STRUCTURE (preserve the asymmetric module depth)
========================================================
- src/<module.path>/aggregates/<TypeName>.ts        — for kind=aggregate
- src/<module.path>/value-objects/<TypeName>.ts     — for kind=value_object
- src/<module.path>/enums/<TypeName>.ts             — for kind=enum
- src/<module.path>/services/<ServiceName>.ts       — for module-level services
- src/orchestrators/services/<OrchestratorName>.ts  — for top-level orchestrators

Examples:
  src/shared/value-objects/Money.ts
  src/shared/enums/Currency.ts
  src/catalog/aggregates/Product.ts
  src/orders/cart/aggregates/Cart.ts
  src/orders/fulfillment/value-objects/TrackingInfo.ts
  src/orchestrators/services/CheckoutOrchestrator.ts

STYLE
=====
- Aggregates: `export class <Name>` with a constructor taking `public readonly` parameters for each field. Do NOT add a separate field-declaration block — TypeScript ctor params auto-become properties.
- Value objects: `export interface <Name>` with explicit field types.
- Enums: `export enum <Name>` whose members are exactly the spec's `members[]` — emit each as `<member.name> = <member.value>` (numeric values).
- Services (incl. orchestrators): `export class <Name>` with the methods from the spec; method bodies must `throw new Error("not implemented")`. Use `void <param>;` to suppress unused-param warnings if needed.
- For cross-module references in fields/params/returns (entries with a `module` field), import the referenced type using a relative path that matches the target module's location. For example, a `Money` ref in `src/orders/value-objects/OrderTotal.ts` imports from `../../shared/value-objects/Money`.
- Include a one-line JSDoc on each top-level export.
- Code must compile cleanly under `tsc --noEmit --strict --target es2022`.

When every type and every service in the spec has been written, output exactly: `DONE` and stop.
