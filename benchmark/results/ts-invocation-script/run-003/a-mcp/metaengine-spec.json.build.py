import json
import re

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-105828-typescript-script/run-003/a-mcp/metaengine-spec.json"

def kebab(name):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", s)
    return s.lower()

PRIMS = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date", "any": "Any"}

def map_field(f):
    out = {"name": f["name"]}
    t = f["type"]
    if t in PRIMS:
        out["primitiveType"] = PRIMS[t]
    else:
        out["typeIdentifier"] = kebab(t)
    return out

def render_param(p, agg):
    t = p["type"]
    code = re.sub(r"\b" + re.escape(agg) + r"\b", "$Agg", t)
    return p["name"] + ": " + code

def render_return(t, agg):
    return re.sub(r"\b" + re.escape(agg) + r"\b", "$Agg", t)

with open(SRC) as fh:
    spec = json.load(fh)

classes = []
interfaces = []
enums = []

for domain in spec["domains"]:
    dname = domain["name"]
    aggregate_name = next((t["name"] for t in domain["types"] if t["kind"] == "aggregate"), None)
    agg_id = kebab(aggregate_name) if aggregate_name else None

    for t in domain["types"]:
        kind = t["kind"]
        name = t["name"]
        tid = kebab(name)
        if kind == "aggregate":
            ctor_params = []
            for f in t["fields"]:
                p = {"name": f["name"]}
                ft = f["type"]
                if ft in PRIMS:
                    p["primitiveType"] = PRIMS[ft]
                else:
                    p["typeIdentifier"] = kebab(ft)
                ctor_params.append(p)
            classes.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/domain/{dname}/aggregates",
                "comment": f"{name} aggregate root for the {dname} domain.",
                "constructorParameters": ctor_params,
            })
        elif kind == "value_object":
            interfaces.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/domain/{dname}/value-objects",
                "comment": f"{name} value object.",
                "properties": [map_field(f) for f in t["fields"]],
            })
        elif kind == "enum":
            enums.append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"src/domain/{dname}/enums",
                "comment": f"{name} enum.",
                "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
            })

    for svc in domain.get("services", []):
        sname = svc["name"]
        sid = kebab(sname)
        custom_code = []
        for m in svc["methods"]:
            params_str = ", ".join(render_param(p, aggregate_name) for p in m["params"])
            ret = render_return(m["returns"], aggregate_name)
            code = f"{m['name']}({params_str}): {ret} {{ throw new Error('not implemented'); }}"
            entry = {"code": code}
            if "$Agg" in code:
                entry["templateRefs"] = [{"placeholder": "$Agg", "typeIdentifier": agg_id}]
            custom_code.append(entry)
        classes.append({
            "name": sname,
            "typeIdentifier": sid,
            "path": f"src/domain/{dname}/services",
            "comment": f"{sname} service.",
            "customCode": custom_code,
        })

result = {
    "language": "typescript",
    "classes": classes,
    "interfaces": interfaces,
    "enums": enums,
}

with open(DST, "w") as fh:
    json.dump(result, fh, indent=2)

print(f"classes={len(classes)} interfaces={len(interfaces)} enums={len(enums)}")
