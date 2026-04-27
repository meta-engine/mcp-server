import json
import re
from pathlib import Path

SPEC_PATH = "<benchmark>/spec/large.json"
OUT_PATH = "<benchmark>/results/20260426-113002-java-script/run-003/a-mcp/metaengine-spec.json"

def kebab(s):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', s).lower()

PRIM_MAP = {
    "string": "String",
    "Date": "Date",
    "boolean": "Boolean",
    "number": "Number",
}

def field_to_param(field):
    java_t = PRIM_MAP.get(field["type"], field["type"])
    return {"name": field["name"], "primitiveType": java_t}

def parse_param(t, agg_name):
    m = re.match(r'^Partial<(\w+)>$', t)
    if m:
        n = m.group(1)
        return f"${n}", [{"placeholder": f"${n}", "typeIdentifier": kebab(n)}]
    if t == "string":
        return "String", []
    if t == "number":
        return "int", []
    if t == "boolean":
        return "boolean", []
    return f"${t}", [{"placeholder": f"${t}", "typeIdentifier": kebab(t)}]

def parse_return(t, agg_name):
    if t == "void":
        return "void", []
    if t == "string":
        return "String", []
    if t == "number":
        return "int", []
    m = re.match(r'^(\w+)\s*\|\s*null$', t)
    if m:
        n = m.group(1)
        return f"${n}", [{"placeholder": f"${n}", "typeIdentifier": kebab(n)}]
    m = re.match(r'^(\w+)\[\]$', t)
    if m:
        n = m.group(1)
        return f"List<${n}>", [{"placeholder": f"${n}", "typeIdentifier": kebab(n)}]
    return f"${t}", [{"placeholder": f"${t}", "typeIdentifier": kebab(t)}]

def build_method(method, agg_name):
    refs = {}
    parts = []
    for p in method["params"]:
        jt, prefs = parse_param(p["type"], agg_name)
        parts.append(f"{jt} {p['name']}")
        for r in prefs:
            refs[r["placeholder"]] = r
    rt, rrefs = parse_return(method["returns"], agg_name)
    for r in rrefs:
        refs[r["placeholder"]] = r
    code = f'public {rt} {method["name"]}({", ".join(parts)}) {{ throw new UnsupportedOperationException("not implemented"); }}'
    entry = {"code": code}
    if refs:
        entry["templateRefs"] = list(refs.values())
    return entry

def main():
    with open(SPEC_PATH) as f:
        spec = json.load(f)
    classes = []
    enums = []
    for domain in spec["domains"]:
        dn = domain["name"]
        agg_name = next((t["name"] for t in domain["types"] if t["kind"] == "aggregate"), None)
        for t in domain["types"]:
            if t["kind"] == "enum":
                enums.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "fileName": t["name"],
                    "path": f"{dn}/enums",
                    "comment": f"{t['name']} enum.",
                    "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
                })
            elif t["kind"] == "aggregate":
                classes.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "fileName": t["name"],
                    "path": f"{dn}/aggregates",
                    "comment": f"{t['name']} aggregate root for the {dn} domain.",
                    "constructorParameters": [field_to_param(f) for f in t["fields"]],
                })
            elif t["kind"] == "value_object":
                classes.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "fileName": t["name"],
                    "path": f"{dn}/value_objects",
                    "comment": f"{t['name']} value object.",
                    "constructorParameters": [field_to_param(f) for f in t["fields"]],
                })
        for s in domain["services"]:
            classes.append({
                "name": s["name"],
                "typeIdentifier": kebab(s["name"]),
                "fileName": s["name"],
                "path": f"{dn}/services",
                "comment": f"{s['name']} service.",
                "customCode": [build_method(m, agg_name) for m in s["methods"]],
            })
    out = {
        "language": "java",
        "packageName": "com.metaengine.demo",
        "classes": classes,
        "enums": enums,
    }
    Path(OUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {OUT_PATH}: {len(classes)} classes, {len(enums)} enums")

if __name__ == "__main__":
    main()
