import json
import re
import os

PRIMITIVES = {"string", "number", "boolean", "Date", "void"}

def to_kebab(name):
    s = re.sub(r'([A-Z])', r'-\1', name).lower().lstrip('-')
    return s

def get_base_type(type_str):
    m = re.match(r'Partial<([^>]+)>', type_str)
    if m:
        return m.group(1)
    m = re.match(r'^([A-Za-z][A-Za-z0-9]*)\[\]$', type_str)
    if m:
        return m.group(1)
    m = re.match(r'^([A-Za-z][A-Za-z0-9]*)\s*\|\s*null$', type_str)
    if m:
        return m.group(1)
    return type_str

def replace_with_placeholder(type_str):
    """Returns (code_type_str, placeholder_or_None, base_type_or_None)."""
    if type_str in PRIMITIVES:
        return type_str, None, None
    base = get_base_type(type_str)
    if base in PRIMITIVES:
        return type_str, None, None
    ph = f"${base}"
    code_type = type_str.replace(base, ph, 1)
    return code_type, ph, base

def field_to_property(f):
    t = f["type"]
    prim_map = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}
    if t in prim_map:
        return {"name": f["name"], "primitiveType": prim_map[t]}
    return {"name": f["name"], "typeIdentifier": to_kebab(t)}

def method_to_custom_code(method):
    refs = {}
    param_strs = []
    for p in method["params"]:
        code_type, ph, base = replace_with_placeholder(p["type"])
        if ph:
            refs[ph] = to_kebab(base)
        param_strs.append(f"{p['name']}: {code_type}")

    ret = method["returns"]
    ret_type = ret["type"] if isinstance(ret, dict) else ret
    ret_code, ph, base = replace_with_placeholder(ret_type)
    if ph:
        refs[ph] = to_kebab(base)

    params_str = ", ".join(param_strs)
    code = f"{method['name']}({params_str}): {ret_code} {{ throw new Error('not implemented'); }}"
    entry = {"code": code}
    if refs:
        entry["templateRefs"] = [{"placeholder": k, "typeIdentifier": v} for k, v in refs.items()]
    return entry

SPEC_PATH = "<benchmark>/spec/monolith.json"
OUT_PATH  = "<benchmark>/results/20260426-223154-typescript-script-sonnet-monolith/run-002/a-mcp/metaengine-spec.json"

with open(SPEC_PATH) as fh:
    spec = json.load(fh)

interfaces = []
classes    = []
enums      = []

for module in spec["modules"]:
    mod_path = module["path"]

    for t in module.get("types", []):
        kind    = t["kind"]
        name    = t["name"]
        type_id = to_kebab(name)

        if kind == "enum":
            enums.append({
                "name":           name,
                "typeIdentifier": type_id,
                "path":           f"src/{mod_path}/enums",
                "members":        t["members"],
            })
        elif kind == "value_object":
            props = [field_to_property(f) for f in t.get("fields", [])]
            interfaces.append({
                "name":           name,
                "typeIdentifier": type_id,
                "path":           f"src/{mod_path}/value-objects",
                "properties":     props,
            })
        elif kind == "aggregate":
            ctor_params = [field_to_property(f) for f in t.get("fields", [])]
            classes.append({
                "name":                  name,
                "typeIdentifier":        type_id,
                "path":                  f"src/{mod_path}/aggregates",
                "constructorParameters": ctor_params,
            })

    for svc in module.get("services", []):
        svc_id      = to_kebab(svc["name"])
        custom_code = [method_to_custom_code(m) for m in svc.get("methods", [])]
        classes.append({
            "name":           svc["name"],
            "typeIdentifier": svc_id,
            "path":           f"src/{mod_path}/services",
            "customCode":     custom_code,
        })

orch = spec["orchestrators"]
for svc in orch.get("services", []):
    svc_id      = to_kebab(svc["name"])
    custom_code = [method_to_custom_code(m) for m in svc.get("methods", [])]
    classes.append({
        "name":           svc["name"],
        "typeIdentifier": svc_id,
        "path":           f"src/{orch['path']}/services",
        "customCode":     custom_code,
    })

result = {
    "language":   "typescript",
    "interfaces": interfaces,
    "classes":    classes,
    "enums":      enums,
}

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w") as fh:
    json.dump(result, fh, indent=2)

print(f"Written {OUT_PATH}")
print(f"  interfaces: {len(interfaces)}, classes: {len(classes)}, enums: {len(enums)}")
