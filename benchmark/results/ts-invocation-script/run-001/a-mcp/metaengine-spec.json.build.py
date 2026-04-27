import json
import re

SPEC_IN  = "<benchmark>/spec/large.json"
SPEC_OUT = "<benchmark>/results/20260426-105828-typescript-script/run-001/a-mcp/metaengine-spec.json"

def kebab(name: str) -> str:
    return re.sub(r'(?<!^)([A-Z])', r'-\1', name).lower()

PRIM = {"string": "String", "Date": "Date", "number": "Number", "boolean": "Boolean"}

def field_to_prop(f):
    p = {"name": f["name"]}
    t = f["type"]
    if t in PRIM:
        p["primitiveType"] = PRIM[t]
    else:
        p["type"] = t
    return p

with open(SPEC_IN) as fh:
    spec = json.load(fh)

classes, interfaces, enums = [], [], []

for domain in spec["domains"]:
    dname = domain["name"]
    agg = next((t for t in domain["types"] if t["kind"] == "aggregate"), None)
    agg_name = agg["name"] if agg else None
    agg_id = kebab(agg_name) if agg else None

    for t in domain["types"]:
        nm = t["name"]
        tid = kebab(nm)
        kind = t["kind"]
        if kind == "aggregate":
            classes.append({
                "name": nm,
                "typeIdentifier": tid,
                "path": f"src/domain/{dname}/aggregates",
                "comment": f"{nm} aggregate root for the {dname} domain.",
                "constructorParameters": [field_to_prop(f) for f in t["fields"]],
            })
        elif kind == "value_object":
            interfaces.append({
                "name": nm,
                "typeIdentifier": tid,
                "path": f"src/domain/{dname}/value-objects",
                "comment": f"{nm} value object.",
                "properties": [field_to_prop(f) for f in t["fields"]],
            })
        elif kind == "enum":
            enums.append({
                "name": nm,
                "typeIdentifier": tid,
                "path": f"src/domain/{dname}/enums",
                "comment": f"{nm} enum.",
                "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
            })

    for svc in domain.get("services", []):
        sname = svc["name"]
        sid = kebab(sname)
        custom_code = []
        for m in svc["methods"]:
            template_refs = []
            def sub_agg(s):
                if agg_name and re.search(rf'\b{re.escape(agg_name)}\b', s):
                    if not any(tr["placeholder"] == "$Agg" for tr in template_refs):
                        template_refs.append({"placeholder": "$Agg", "typeIdentifier": agg_id})
                    return re.sub(rf'\b{re.escape(agg_name)}\b', "$Agg", s)
                return s
            params = ", ".join(f"{p['name']}: {sub_agg(p['type'])}" for p in m["params"])
            ret = sub_agg(m["returns"])
            entry = {"code": f"{m['name']}({params}): {ret} {{ throw new Error('not implemented'); }}"}
            if template_refs:
                entry["templateRefs"] = template_refs
            custom_code.append(entry)
        classes.append({
            "name": sname,
            "typeIdentifier": sid,
            "path": f"src/domain/{dname}/services",
            "comment": f"{sname} service.",
            "customCode": custom_code,
        })

out = {
    "language": "typescript",
    "classes": classes,
    "interfaces": interfaces,
    "enums": enums,
}

with open(SPEC_OUT, "w") as fh:
    json.dump(out, fh, indent=2)

print(f"wrote {SPEC_OUT}: {len(classes)} classes, {len(interfaces)} interfaces, {len(enums)} enums")
