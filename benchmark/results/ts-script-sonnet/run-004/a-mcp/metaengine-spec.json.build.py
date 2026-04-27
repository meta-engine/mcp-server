import json
import re
import os

def to_kebab(name):
    return re.sub(r'([A-Z])', r'-\1', name).lstrip('-').lower()

def map_primitive(t):
    return {"string": "String", "number": "Number", "Date": "Date", "boolean": "Boolean"}.get(t, t)

def field_to_entry(field):
    return {"name": field["name"], "primitiveType": map_primitive(field["type"])}

spec_path = "<benchmark>/spec/large.json"
out_path = "<benchmark>/results/20260426-182553-typescript-script-sonnet/run-004/a-mcp/metaengine-spec.json"

with open(spec_path) as f:
    ddd = json.load(f)

classes, interfaces, enums = [], [], []

for domain in ddd["domains"]:
    domain_name = domain["name"]
    agg_type = next((t for t in domain["types"] if t["kind"] == "aggregate"), None)
    agg_name = agg_type["name"] if agg_type else None
    agg_id = to_kebab(agg_name) if agg_name else None

    for t in domain["types"]:
        kind, name = t["kind"], t["name"]
        type_id = to_kebab(name)

        if kind == "aggregate":
            classes.append({
                "name": name,
                "typeIdentifier": type_id,
                "path": f"src/domain/{domain_name}/aggregates",
                "constructorParameters": [field_to_entry(f) for f in t.get("fields", [])],
                "comment": f"{name} aggregate root for the {domain_name} domain."
            })

        elif kind == "value_object":
            interfaces.append({
                "name": name,
                "typeIdentifier": type_id,
                "path": f"src/domain/{domain_name}/value-objects",
                "properties": [field_to_entry(f) for f in t.get("fields", [])],
                "comment": f"{name} value object."
            })

        elif kind == "enum":
            enums.append({
                "name": name,
                "typeIdentifier": type_id,
                "path": f"src/domain/{domain_name}/enums",
                "members": [{"name": m["name"], "value": m["value"]} for m in t.get("members", [])],
                "comment": f"{name} enum."
            })

    for svc in domain.get("services", []):
        svc_name = svc["name"]
        placeholder = f"${agg_name}" if agg_name else None
        custom_code = []

        for method in svc.get("methods", []):
            needs_ref = False
            param_parts = []
            for p in method.get("params", []):
                ptype = p["type"].replace(agg_name, placeholder) if agg_name and agg_name in p["type"] else p["type"]
                if agg_name and agg_name in p["type"]:
                    needs_ref = True
                param_parts.append(f"{p['name']}: {ptype}")

            ret = method["returns"]
            if agg_name and agg_name in ret:
                ret = ret.replace(agg_name, placeholder)
                needs_ref = True

            entry = {
                "code": f"{method['name']}({', '.join(param_parts)}): {ret} {{ throw new Error('not implemented'); }}"
            }
            if needs_ref:
                entry["templateRefs"] = [{"placeholder": placeholder, "typeIdentifier": agg_id}]
            custom_code.append(entry)

        classes.append({
            "name": svc_name,
            "typeIdentifier": to_kebab(svc_name),
            "path": f"src/domain/{domain_name}/services",
            "customCode": custom_code,
            "comment": f"{svc_name} service."
        })

os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump({"language": "typescript", "classes": classes, "interfaces": interfaces, "enums": enums}, f, indent=2)

print(f"Written: {out_path}")
