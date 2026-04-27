import json
import re

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-105828-typescript-script/run-004/a-mcp/metaengine-spec.json"

PRIM_MAP = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
    "any": "Any",
}

def kebab(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    return s.lower()

def field_to_property(field):
    t = field["type"]
    if t in PRIM_MAP:
        return {"name": field["name"], "primitiveType": PRIM_MAP[t]}
    return {"name": field["name"], "typeIdentifier": kebab(t)}

def field_to_ctor_param(field):
    t = field["type"]
    if t in PRIM_MAP:
        return {"name": field["name"], "primitiveType": PRIM_MAP[t]}
    return {"name": field["name"], "typeIdentifier": kebab(t)}

def build_method_code(method, agg_name):
    params = method.get("params", [])
    rendered_params = []
    for p in params:
        rendered_params.append(f"{p['name']}: {p['type']}")
    params_str = ", ".join(rendered_params)
    ret = method.get("returns", "void")
    sig = f"{method['name']}({params_str}): {ret}"
    code = f"{sig} {{ throw new Error('not implemented'); }}"
    # Substitute aggregate name with $Agg using word boundary
    pattern = re.compile(r"\b" + re.escape(agg_name) + r"\b")
    has_ref = bool(pattern.search(code))
    code = pattern.sub("$Agg", code)
    entry = {"code": code}
    if has_ref:
        entry["templateRefs"] = [
            {"placeholder": "$Agg", "typeIdentifier": kebab(agg_name)}
        ]
    return entry

def main():
    with open(SRC) as f:
        spec = json.load(f)

    out = {
        "language": "typescript",
        "classes": [],
        "interfaces": [],
        "enums": [],
    }

    for domain in spec["domains"]:
        d = domain["name"]
        aggregates = [t for t in domain["types"] if t["kind"] == "aggregate"]
        agg_name = aggregates[0]["name"] if aggregates else None

        for t in domain["types"]:
            kind = t["kind"]
            name = t["name"]
            tid = kebab(name)
            if kind == "aggregate":
                out["classes"].append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"src/domain/{d}/aggregates",
                    "comment": f"{name} aggregate root for the {d} domain.",
                    "constructorParameters": [field_to_ctor_param(f) for f in t.get("fields", [])],
                })
            elif kind == "value_object":
                out["interfaces"].append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"src/domain/{d}/value-objects",
                    "comment": f"{name} value object.",
                    "properties": [field_to_property(f) for f in t.get("fields", [])],
                })
            elif kind == "enum":
                out["enums"].append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"src/domain/{d}/enums",
                    "comment": f"{name} enum.",
                    "members": [{"name": m["name"], "value": m["value"]} for m in t.get("members", [])],
                })

        for svc in domain.get("services", []):
            sname = svc["name"]
            sid = kebab(sname)
            custom_code = [build_method_code(m, agg_name) for m in svc.get("methods", [])]
            out["classes"].append({
                "name": sname,
                "typeIdentifier": sid,
                "path": f"src/domain/{d}/services",
                "comment": f"{sname} service.",
                "customCode": custom_code,
            })

    with open(DST, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {DST}")
    print(f"classes={len(out['classes'])} interfaces={len(out['interfaces'])} enums={len(out['enums'])}")

if __name__ == "__main__":
    main()
