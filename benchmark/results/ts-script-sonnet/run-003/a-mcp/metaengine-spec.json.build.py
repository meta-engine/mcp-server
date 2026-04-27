import json
import re
import os

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-182553-typescript-script-sonnet/run-003/a-mcp/metaengine-spec.json"

def to_kebab(name):
    s = re.sub(r'(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s).lower()

PRIM_MAP = {"string": "String", "Date": "Date", "number": "Number", "boolean": "Boolean"}

def field_to_prop(field):
    p = {"name": field["name"]}
    prim = PRIM_MAP.get(field["type"])
    if prim:
        p["primitiveType"] = prim
    else:
        p["type"] = field["type"]
    return p

def make_stub(method, agg_name, agg_id):
    ph = f"${agg_name}"
    template_refs = []

    def sub(s):
        nonlocal template_refs
        if agg_name and re.search(r'\b' + re.escape(agg_name) + r'\b', s):
            if not template_refs:
                template_refs.append({"placeholder": ph, "typeIdentifier": agg_id})
            return re.sub(r'\b' + re.escape(agg_name) + r'\b', ph, s)
        return s

    params_str = ", ".join(f"{p['name']}: {sub(p['type'])}" for p in method["params"])
    ret = sub(method["returns"])
    code = f"{method['name']}({params_str}): {ret} {{ throw new Error('not implemented'); }}"
    entry = {"code": code}
    if template_refs:
        entry["templateRefs"] = template_refs
    return entry

with open(SRC) as f:
    spec = json.load(f)

classes, interfaces, enums = [], [], []

for domain in spec["domains"]:
    dn = domain["name"]
    agg = next((t for t in domain["types"] if t["kind"] == "aggregate"), None)
    agg_name = agg["name"] if agg else None
    agg_id = to_kebab(agg_name) if agg_name else None

    for t in domain["types"]:
        name, tid = t["name"], to_kebab(t["name"])
        if t["kind"] == "aggregate":
            classes.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/domain/{dn}/aggregates",
                "comment": f"{name} aggregate root for the {dn} domain.",
                "constructorParameters": [field_to_prop(f) for f in t["fields"]],
            })
        elif t["kind"] == "value_object":
            interfaces.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/domain/{dn}/value-objects",
                "comment": f"{name} value object.",
                "properties": [field_to_prop(f) for f in t["fields"]],
            })
        elif t["kind"] == "enum":
            enums.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/domain/{dn}/enums",
                "comment": f"{name} enum.",
                "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
            })

    for svc in domain.get("services", []):
        classes.append({
            "name": svc["name"],
            "typeIdentifier": to_kebab(svc["name"]),
            "path": f"src/domain/{dn}/services",
            "comment": f"{svc['name']} service.",
            "customCode": [make_stub(m, agg_name, agg_id) for m in svc["methods"]],
        })

os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, "w") as f:
    json.dump({"language": "typescript", "classes": classes, "interfaces": interfaces, "enums": enums}, f, indent=2)

print(f"Written {DST} ({os.path.getsize(DST)} bytes)")
