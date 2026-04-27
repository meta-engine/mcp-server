#!/usr/bin/env python3
import json
import re
from pathlib import Path

SPEC_PATH = Path("<benchmark>/spec/monolith.json")
OUT_PATH = Path("<benchmark>/results/20260426-210323-typescript-script-monolith/run-002/a-mcp/metaengine-spec.json")

PRIMITIVES = {"string", "number", "boolean", "Date", "void"}
PRIMITIVE_MAP = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}


def kebab(name):
    out = []
    for i, c in enumerate(name):
        if c.isupper() and i > 0:
            out.append("-")
        out.append(c.lower())
    return "".join(out)


def to_placeholder(type_name):
    return "$" + type_name[0].lower() + type_name[1:]


def parse_type(type_str):
    """Translate a TS-ish type string to (rendered_with_placeholders, refs_dict).
    refs_dict maps placeholder -> typeIdentifier."""
    refs = {}
    if type_str in PRIMITIVES:
        return type_str, refs

    m = re.match(r"^Partial<(\w+)>$", type_str)
    if m:
        inner = m.group(1)
        ph = to_placeholder(inner)
        refs[ph] = kebab(inner)
        return f"Partial<{ph}>", refs

    m = re.match(r"^(\w+)\[\]$", type_str)
    if m:
        inner = m.group(1)
        ph = to_placeholder(inner)
        refs[ph] = kebab(inner)
        return f"{ph}[]", refs

    m = re.match(r"^(\w+)\s*\|\s*null$", type_str)
    if m:
        inner = m.group(1)
        ph = to_placeholder(inner)
        refs[ph] = kebab(inner)
        return f"{ph} | null", refs

    m = re.match(r"^(\w+)$", type_str)
    if m:
        inner = m.group(1)
        ph = to_placeholder(inner)
        refs[ph] = kebab(inner)
        return ph, refs

    raise ValueError(f"unrecognized type: {type_str}")


def field_to_property(f):
    """Unified translation for value_object property + aggregate ctor param + service method param."""
    t = f["type"]
    if t in PRIMITIVES and t != "void":
        return {"name": f["name"], "primitiveType": PRIMITIVE_MAP[t]}
    return {"name": f["name"], "typeIdentifier": kebab(t)}


def method_to_custom_code(method):
    refs = {}
    parts = []
    for p in method["params"]:
        rendered, p_refs = parse_type(p["type"])
        refs.update(p_refs)
        parts.append(f"{p['name']}: {rendered}")
    ret = method["returns"]
    ret_type_str = ret["type"] if isinstance(ret, dict) else ret
    ret_rendered, r_refs = parse_type(ret_type_str)
    refs.update(r_refs)
    code = f"{method['name']}({', '.join(parts)}): {ret_rendered} {{ throw new Error('not implemented'); }}"
    entry = {"code": code}
    if refs:
        entry["templateRefs"] = [
            {"placeholder": k, "typeIdentifier": v} for k, v in refs.items()
        ]
    return entry


def main():
    with open(SPEC_PATH) as fh:
        spec = json.load(fh)

    classes = []
    interfaces = []
    enums = []

    for module in spec["modules"]:
        mod_path = module["path"]
        for t in module["types"]:
            kind = t["kind"]
            ti = kebab(t["name"])
            if kind == "aggregate":
                classes.append({
                    "name": t["name"],
                    "typeIdentifier": ti,
                    "path": f"src/{mod_path}/aggregates",
                    "constructorParameters": [field_to_property(f) for f in t["fields"]],
                })
            elif kind == "value_object":
                interfaces.append({
                    "name": t["name"],
                    "typeIdentifier": ti,
                    "path": f"src/{mod_path}/value-objects",
                    "properties": [field_to_property(f) for f in t["fields"]],
                })
            elif kind == "enum":
                enums.append({
                    "name": t["name"],
                    "typeIdentifier": ti,
                    "path": f"src/{mod_path}/enums",
                    "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
                })
            else:
                raise ValueError(f"unknown kind: {kind}")

        for svc in module.get("services", []):
            classes.append({
                "name": svc["name"],
                "typeIdentifier": kebab(svc["name"]),
                "path": f"src/{mod_path}/services",
                "customCode": [method_to_custom_code(m) for m in svc["methods"]],
            })

    orch = spec.get("orchestrators")
    if orch:
        for svc in orch["services"]:
            classes.append({
                "name": svc["name"],
                "typeIdentifier": kebab(svc["name"]),
                "path": f"src/{orch['path']}/services",
                "customCode": [method_to_custom_code(m) for m in svc["methods"]],
            })

    out = {
        "language": "typescript",
        "skipExisting": False,
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"wrote {OUT_PATH}: classes={len(classes)} interfaces={len(interfaces)} enums={len(enums)}")


if __name__ == "__main__":
    main()
