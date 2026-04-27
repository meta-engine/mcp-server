#!/usr/bin/env python3
import json
import os
import re

PRIM_MAP = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}
TS_UTILITIES = {
    "Partial", "Required", "Readonly", "Record", "Pick", "Omit",
    "Exclude", "Extract", "NonNullable", "ReturnType", "InstanceType",
    "Promise", "Array", "Object", "Function",
}

def kebab(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()

def extract_custom_types(type_str, registry):
    identifiers = re.findall(r'\b([A-Z][a-zA-Z0-9]*)\b', type_str)
    return [i for i in identifiers if i in registry and i not in TS_UTILITIES]

def replace_with_placeholders(type_str, custom_types):
    result = type_str
    refs = {}
    for t in custom_types:
        ph = f"${t}"
        result = re.sub(r'\b' + re.escape(t) + r'\b', ph, result)
        refs[ph] = kebab(t)
    return result, refs

def field_to_property(f):
    """Unified helper — works for aggregate constructorParameters AND value_object properties."""
    if f["type"] in PRIM_MAP:
        return {"name": f["name"], "primitiveType": PRIM_MAP[f["type"]]}
    return {"name": f["name"], "typeIdentifier": kebab(f["type"])}

def method_to_custom_code(method, registry):
    refs = {}
    param_strs = []

    for p in method["params"]:
        t = p["type"]
        ctypes = extract_custom_types(t, registry)
        if ctypes:
            modified, new_refs = replace_with_placeholders(t, ctypes)
            refs.update(new_refs)
            param_strs.append(f"{p['name']}: {modified}")
        else:
            param_strs.append(f"{p['name']}: {t}")

    ret = method["returns"]
    ret_type = ret["type"] if isinstance(ret, dict) else ret

    if ret_type == "void":
        ret_str = "void"
    else:
        ctypes = extract_custom_types(ret_type, registry)
        if ctypes:
            ret_str, new_refs = replace_with_placeholders(ret_type, ctypes)
            refs.update(new_refs)
        else:
            ret_str = ret_type

    params = ", ".join(param_strs)
    code = f"{method['name']}({params}): {ret_str} {{ throw new Error('not implemented'); }}"

    entry = {"code": code}
    if refs:
        entry["templateRefs"] = [{"placeholder": k, "typeIdentifier": v} for k, v in refs.items()]
    return entry

def process_type(t, module_path):
    kind = t["kind"]
    name = t["name"]
    tid = kebab(name)

    if kind == "aggregate":
        ctor_params = [field_to_property(f) for f in t.get("fields", [])]
        return "classes", {
            "name": name,
            "typeIdentifier": tid,
            "path": f"src/{module_path}/aggregates",
            "constructorParameters": ctor_params,
        }
    elif kind == "value_object":
        props = [field_to_property(f) for f in t.get("fields", [])]
        return "interfaces", {
            "name": name,
            "typeIdentifier": tid,
            "path": f"src/{module_path}/value-objects",
            "properties": props,
        }
    elif kind == "enum":
        return "enums", {
            "name": name,
            "typeIdentifier": tid,
            "path": f"src/{module_path}/enums",
            "members": t["members"],
        }
    else:
        raise ValueError(f"Unknown kind: {kind}")

def process_service(svc, module_path, registry):
    name = svc["name"]
    tid = kebab(name)
    custom_code = [method_to_custom_code(m, registry) for m in svc.get("methods", [])]
    return {
        "name": name,
        "typeIdentifier": tid,
        "path": f"src/{module_path}/services",
        "customCode": custom_code,
    }

def main():
    src = "<benchmark>/spec/monolith.json"
    dst = "<benchmark>/results/20260426-223154-typescript-script-sonnet-monolith/run-001/a-mcp/metaengine-spec.json"

    with open(src) as f:
        spec = json.load(f)

    # Build registry of all custom type names
    registry = set()
    for module in spec["modules"]:
        for t in module.get("types", []):
            registry.add(t["name"])

    result = {"language": "typescript", "classes": [], "interfaces": [], "enums": []}

    # Process modules
    for module in spec["modules"]:
        path = module["path"]
        for t in module.get("types", []):
            bucket, entry = process_type(t, path)
            result[bucket].append(entry)
        for svc in module.get("services", []):
            result["classes"].append(process_service(svc, path, registry))

    # Process orchestrators
    orch = spec.get("orchestrators", {})
    orch_path = orch.get("path", "orchestrators")
    for svc in orch.get("services", []):
        result["classes"].append(process_service(svc, orch_path, registry))

    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Wrote {dst}")
    c = sum(len(result[k]) for k in ("classes", "interfaces", "enums"))
    print(f"  classes={len(result['classes'])}  interfaces={len(result['interfaces'])}  enums={len(result['enums'])}  total={c}")

if __name__ == "__main__":
    main()
