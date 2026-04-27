You are running the baseline variant of a code-generation benchmark.

OBJECTIVE
=========
Generate TypeScript code for the DDD spec located at:
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

2. For every type and every service in the spec, create a separate TypeScript file using the `Write` tool. Do not skip any entity. Do not summarise or batch — every entity gets its own file.

OUTPUT STRUCTURE (deep DDD layering)
====================================
- src/domain/<domain>/aggregates/<TypeName>.ts        — for kind=aggregate
- src/domain/<domain>/value-objects/<TypeName>.ts     — for kind=value_object
- src/domain/<domain>/enums/<TypeName>.ts             — for kind=enum
- src/domain/<domain>/services/<ServiceName>.ts       — for services

STYLE
=====
- Aggregates: `export class <Name>` with a constructor taking `public readonly` parameters for each field. Do NOT add a separate field-declaration block — TypeScript ctor params auto-become properties.
- Value objects: `export interface <Name>` with explicit field types.
- Enums: `export enum <Name>` whose members are exactly the spec's `members[]` — emit each as `<member.name> = <member.value>` (values are numeric integers).
- Services: `export class <Name>` with the methods from the spec; method bodies must `throw new Error("not implemented")`. Use `void <param>;` to suppress unused-param warnings if needed.
- Include a one-line JSDoc on each top-level export.
- Code must compile cleanly under `tsc --noEmit --strict --target es2022`.

When every file in the spec has been written, output exactly: `DONE` and stop.
