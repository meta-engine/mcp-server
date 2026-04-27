#!/usr/bin/env python3
"""Translate the modular-monolith spec into a MetaEngine TypeScript spec."""
import json
import re
from pathlib import Path

SRC = Path("<benchmark>/spec/monolith.json")
OUT = Path("<benchmark>/results/20260426-210323-typescript-script-monolith/run-004/a-mcp/metaengine-spec.json")

PRIMITIVES = {"string", "number", "boolean", "Date"}
PRIMITIVE_MAP = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}


def kebab(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


def field_to_property(f):
    """Translate a spec field to a MetaEngine property/parameter entry.
    Single helper used for value_object properties, aggregate constructor params,
    and (indirectly via the same primitive/typeIdentifier rules) service methods."""
    t = f["type"]
    if t in PRIMITIVE_MAP:
        return {"name": f["name"], "primitiveType": PRIMITIVE_MAP[t]}
    return {"name": f["name"], "typeIdentifier": kebab(t)}


def signature_for_param(p, refs):
    t = p["type"]
    if t in PRIMITIVES:
        return f"{p['name']}: {t}"
    m = re.match(r"^Partial<(.+)>$", t)
    if m:
        inner = m.group(1)
        ph = f"${kebab(inner)}"
        refs[ph] = kebab(inner)
        return f"{p['name']}: Partial<{ph}>"
    ph = f"${kebab(t)}"
    refs[ph] = kebab(t)
    return f"{p['name']}: {ph}"


def signature_for_return(ret, refs):
    if isinstance(ret, dict):
        t = ret["type"]
    else:
        t = ret
    if t == "void" or t in PRIMITIVES:
        return t
    m = re.match(r"^(.+)\[\]$", t)
    if m:
        inner = m.group(1)
        ph = f"${kebab(inner)}"
        refs[ph] = kebab(inner)
        return f"{ph}[]"
    m = re.match(r"^(.+) \| null$", t)
    if m:
        inner = m.group(1)
        ph = f"${kebab(inner)}"
        refs[ph] = kebab(inner)
        return f"{ph} | null"
    ph = f"${kebab(t)}"
    refs[ph] = kebab(t)
    return ph


def method_to_custom_code(method):
    refs = {}
    parts = [signature_for_param(p, refs) for p in method.get("params", [])]
    ret_str = signature_for_return(method["returns"], refs)
    code = f"{method['name']}({', '.join(parts)}): {ret_str} {{ throw new Error('not implemented'); }}"
    entry = {"code": code}
    if refs:
        entry["templateRefs"] = [{"placeholder": k, "typeIdentifier": v} for k, v in refs.items()]
    return entry


def service_to_class(service, base_path):
    return {
        "name": service["name"],
        "typeIdentifier": kebab(service["name"]),
        "path": f"{base_path}/services",
        "customCode": [method_to_custom_code(m) for m in service.get("methods", [])],
    }


def main():
    spec = json.loads(SRC.read_text())
    out = {
        "language": "typescript",
        "classes": [],
        "interfaces": [],
        "enums": [],
    }

    for module in spec["modules"]:
        mod_path = module["path"]
        base = f"src/{mod_path}"

        for t in module.get("types", []):
            kind = t["kind"]
            tid = kebab(t["name"])
            if kind == "aggregate":
                out["classes"].append({
                    "name": t["name"],
                    "typeIdentifier": tid,
                    "path": f"{base}/aggregates",
                    "constructorParameters": [field_to_property(f) for f in t.get("fields", [])],
                })
            elif kind == "value_object":
                out["interfaces"].append({
                    "name": t["name"],
                    "typeIdentifier": tid,
                    "path": f"{base}/value-objects",
                    "properties": [field_to_property(f) for f in t.get("fields", [])],
                })
            elif kind == "enum":
                out["enums"].append({
                    "name": t["name"],
                    "typeIdentifier": tid,
                    "path": f"{base}/enums",
                    "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
                })
            else:
                raise ValueError(f"Unknown kind: {kind}")

        for svc in module.get("services", []):
            out["classes"].append(service_to_class(svc, base))

    orch = spec.get("orchestrators")
    if orch:
        orch_base = f"src/{orch['path']}"
        for svc in orch.get("services", []):
            out["classes"].append(service_to_class(svc, orch_base))

    OUT.write_text(json.dumps(out, indent=2))
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"  classes:    {len(out['classes'])}")
    print(f"  interfaces: {len(out['interfaces'])}")
    print(f"  enums:      {len(out['enums'])}")


if __name__ == "__main__":
    main()
