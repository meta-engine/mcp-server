#!/usr/bin/env python3
"""Build a MetaEngine spec from the modular-monolith spec."""
import json
import re
import os

SRC = "<benchmark>/spec/monolith.json"
OUT = "<benchmark>/results/20260426-210323-typescript-script-monolith/run-001/a-mcp/metaengine-spec.json"

PRIMITIVES = {"string", "number", "boolean", "Date"}
PRIM_MAP = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}


def kebab(name: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", s)
    return s.lower()


def field_to_property(f):
    """Translate a field/param to MetaEngine property/parameter shape.
    Same helper for value_object props, aggregate ctor params, AND service params."""
    t = f["type"]
    if t in PRIMITIVES:
        return {"name": f["name"], "primitiveType": PRIM_MAP[t]}
    return {"name": f["name"], "typeIdentifier": kebab(t)}


def process_type_expression(type_str: str):
    """Translate a method param/return type expression.
    Handles: primitives, void, bare type, Partial<X>, X[], X | null."""
    refs = {}
    if type_str == "void":
        return "void", refs
    if type_str in PRIMITIVES:
        return type_str, refs

    inner = type_str
    prefix_partial = False
    suffix_array = False
    suffix_null = False

    if inner.startswith("Partial<") and inner.endswith(">"):
        inner = inner[len("Partial<"):-1]
        prefix_partial = True

    if inner.endswith(" | null"):
        inner = inner[: -len(" | null")]
        suffix_null = True

    if inner.endswith("[]"):
        inner = inner[:-2]
        suffix_array = True

    if inner in PRIMITIVES:
        rendered = inner
    else:
        ph = f"${kebab(inner)}"
        refs[ph] = kebab(inner)
        rendered = ph

    if suffix_array:
        rendered = f"{rendered}[]"
    if suffix_null:
        rendered = f"{rendered} | null"
    if prefix_partial:
        rendered = f"Partial<{rendered}>"

    return rendered, refs


def method_to_custom_code(method):
    refs = {}
    parts = []
    for p in method["params"]:
        rendered, prefs = process_type_expression(p["type"])
        refs.update(prefs)
        parts.append(f"{p['name']}: {rendered}")

    ret = method["returns"]
    ret_type = ret["type"] if isinstance(ret, dict) else ret
    rendered_ret, rrefs = process_type_expression(ret_type)
    refs.update(rrefs)

    code = (
        f"{method['name']}({', '.join(parts)}): {rendered_ret} "
        f"{{ throw new Error('not implemented'); }}"
    )
    template_refs = [
        {"placeholder": k, "typeIdentifier": v} for k, v in refs.items()
    ]
    entry = {"code": code}
    if template_refs:
        entry["templateRefs"] = template_refs
    return entry


def main():
    with open(SRC, "r") as f:
        spec = json.load(f)

    classes = []
    interfaces = []
    enums = []

    for module in spec.get("modules", []):
        mod_path = module["path"]
        for t in module.get("types", []):
            kind = t["kind"]
            if kind == "aggregate":
                ctor_params = [field_to_property(f) for f in t.get("fields", [])]
                classes.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "constructorParameters": ctor_params,
                    "path": f"src/{mod_path}/aggregates",
                })
            elif kind == "value_object":
                props = [field_to_property(f) for f in t.get("fields", [])]
                interfaces.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "properties": props,
                    "path": f"src/{mod_path}/value-objects",
                })
            elif kind == "enum":
                enums.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "members": [
                        {"name": m["name"], "value": m["value"]}
                        for m in t.get("members", [])
                    ],
                    "path": f"src/{mod_path}/enums",
                })
            else:
                raise ValueError(f"Unknown kind: {kind}")

        for s in module.get("services", []):
            custom_code = [method_to_custom_code(m) for m in s.get("methods", [])]
            classes.append({
                "name": s["name"],
                "typeIdentifier": kebab(s["name"]),
                "customCode": custom_code,
                "path": f"src/{mod_path}/services",
            })

    orch = spec.get("orchestrators")
    if orch:
        orch_path = orch.get("path", "orchestrators")
        for s in orch.get("services", []):
            custom_code = [method_to_custom_code(m) for m in s.get("methods", [])]
            classes.append({
                "name": s["name"],
                "typeIdentifier": kebab(s["name"]),
                "customCode": custom_code,
                "path": f"src/{orch_path}/services",
            })

    spec_out = {
        "language": "typescript",
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(spec_out, f, indent=2)

    print(
        f"Wrote {OUT}: {len(classes)} classes, "
        f"{len(interfaces)} interfaces, {len(enums)} enums"
    )


if __name__ == "__main__":
    main()
