#!/usr/bin/env python3
import json
import re
import os

SPEC_PATH = "<benchmark>/spec/monolith.json"
OUT_PATH = "<benchmark>/results/20260426-223154-typescript-script-sonnet-monolith/run-004/a-mcp/metaengine-spec.json"

PRIMITIVES = {"string", "number", "boolean", "Date", "void"}
PRIM_MAP = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}


def kebab(name):
    s = re.sub(r'([A-Z])', r'-\1', name).lstrip('-').lower()
    return s


def field_to_param(f):
    """Unified: translate a field/param entry to MetaEngine property/constructorParameter shape."""
    if f["type"] in PRIMITIVES:
        return {"name": f["name"], "primitiveType": PRIM_MAP[f["type"]]}
    return {"name": f["name"], "typeIdentifier": kebab(f["type"])}


def extract_base_and_expr(type_str):
    """
    Parse a raw type string into (base_type_name_or_None, expr_with_placeholder).
    Handles: Partial<X>, X | null, X[], plain X.
    Returns (None, type_str) for primitives/void.
    """
    if type_str in PRIMITIVES:
        return None, type_str

    m = re.match(r'^Partial<(.+)>$', type_str)
    if m:
        base = m.group(1)
        return base, f"Partial<${base}>"

    m = re.match(r'^(.+?) \| null$', type_str)
    if m:
        base = m.group(1)
        return base, f"${base} | null"

    m = re.match(r'^(.+?)\[\]$', type_str)
    if m:
        base = m.group(1)
        return base, f"${base}[]"

    return type_str, f"${type_str}"


def method_to_custom_code(method):
    """Build one customCode entry for a service method, with all templateRefs resolved."""
    refs = {}  # placeholder -> typeIdentifier (dict deduplicates same-type refs)
    param_parts = []

    for p in method["params"]:
        base, expr = extract_base_and_expr(p["type"])
        if base is None:
            param_parts.append(f"{p['name']}: {p['type']}")
        else:
            ph = f"${base}"
            refs[ph] = kebab(base)
            param_parts.append(f"{p['name']}: {expr}")

    ret = method["returns"]
    ret_type = ret["type"] if isinstance(ret, dict) else ret
    base, ret_expr = extract_base_and_expr(ret_type)
    if base is not None:
        refs[f"${base}"] = kebab(base)

    params_str = ", ".join(param_parts)
    code = f"{method['name']}({params_str}): {ret_expr} {{ throw new Error('not implemented'); }}"

    entry = {"code": code}
    if refs:
        entry["templateRefs"] = [{"placeholder": k, "typeIdentifier": v} for k, v in refs.items()]
    return entry


def process_type(t, module_path):
    kind = t["kind"]
    name = t["name"]
    tid = kebab(name)

    if kind == "aggregate":
        return "classes", {
            "name": name,
            "typeIdentifier": tid,
            "path": f"src/{module_path}/aggregates",
            "constructorParameters": [field_to_param(f) for f in t.get("fields", [])]
        }
    elif kind == "value_object":
        return "interfaces", {
            "name": name,
            "typeIdentifier": tid,
            "path": f"src/{module_path}/value-objects",
            "properties": [field_to_param(f) for f in t.get("fields", [])]
        }
    elif kind == "enum":
        return "enums", {
            "name": name,
            "typeIdentifier": tid,
            "path": f"src/{module_path}/enums",
            "members": [{"name": m["name"], "value": m["value"]} for m in t.get("members", [])]
        }
    else:
        raise ValueError(f"Unknown kind: {kind}")


def process_service(svc, module_path):
    name = svc["name"]
    tid = kebab(name)
    return {
        "name": name,
        "typeIdentifier": tid,
        "path": f"src/{module_path}/services",
        "customCode": [method_to_custom_code(m) for m in svc.get("methods", [])]
    }


def main():
    with open(SPEC_PATH) as f:
        spec = json.load(f)

    classes = []
    interfaces = []
    enums = []

    for module in spec["modules"]:
        module_path = module["path"]
        for t in module.get("types", []):
            key, entry = process_type(t, module_path)
            if key == "classes":
                classes.append(entry)
            elif key == "interfaces":
                interfaces.append(entry)
            elif key == "enums":
                enums.append(entry)
        for svc in module.get("services", []):
            classes.append(process_service(svc, module_path))

    orch = spec.get("orchestrators", {})
    orch_path = orch.get("path", "orchestrators")
    for svc in orch.get("services", []):
        classes.append(process_service(svc, orch_path))

    result = {
        "language": "typescript",
        "classes": classes,
        "interfaces": interfaces,
        "enums": enums
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Written {OUT_PATH}")
    print(f"  classes={len(classes)}, interfaces={len(interfaces)}, enums={len(enums)}")


if __name__ == "__main__":
    main()
