import json, re

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-113002-java-script/run-005/a-mcp/metaengine-spec.json"

def kebab(name):
    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()

def field_to_param(field):
    name, t = field["name"], field["type"]
    if t == "string":  return {"name": name, "primitiveType": "String"}
    if t == "number":  return {"name": name, "type": "double"}
    if t == "boolean": return {"name": name, "primitiveType": "Boolean"}
    if t == "Date":    return {"name": name, "primitiveType": "Date"}
    return {"name": name, "primitiveType": "Any"}

def map_simple(t):
    return {"string": "String", "number": "double", "boolean": "boolean", "void": "void"}.get(t)

def render_param_type(t):
    s = map_simple(t)
    if s is not None: return s, False
    if t.startswith("Partial<") and t.endswith(">"): return "$Agg", True
    return "$Agg", True

def render_return_type(t):
    s = map_simple(t)
    if s is not None: return s, False
    if t.endswith("[]"):       return "java.util.List<$Agg>", True
    if " | null" in t:         return "java.util.Optional<$Agg>", True
    return "$Agg", True

def build_method_code(method, agg_id):
    parts, needs = [], False
    for p in method["params"]:
        jt, n = render_param_type(p["type"])
        needs = needs or n
        parts.append(f"{jt} {p['name']}")
    ret, n = render_return_type(method["returns"])
    needs = needs or n
    code = f'public {ret} {method["name"]}({", ".join(parts)}) {{ throw new UnsupportedOperationException("not implemented"); }}'
    entry = {"code": code}
    if needs:
        entry["templateRefs"] = [{"placeholder": "$Agg", "typeIdentifier": agg_id}]
    return entry

with open(SRC) as f:
    src = json.load(f)

out = {
    "language": "java",
    "packageName": "com.metaengine.demo",
    "classes": [],
    "interfaces": [],
    "enums": [],
}

for domain in src["domains"]:
    dname = domain["name"]
    agg_id = None
    for t in domain["types"]:
        if t["kind"] == "aggregate":
            agg_id = kebab(t["name"])
            break

    for t in domain["types"]:
        kind = t["kind"]
        name = t["name"]
        tid = kebab(name)
        if kind == "aggregate":
            out["classes"].append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"{dname}/aggregates",
                "comment": f"{name} aggregate root for the {dname} domain.",
                "constructorParameters": [field_to_param(f) for f in t["fields"]],
            })
        elif kind == "value_object":
            out["classes"].append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"{dname}/value_objects",
                "comment": f"{name} value object.",
                "constructorParameters": [field_to_param(f) for f in t["fields"]],
            })
        elif kind == "enum":
            out["enums"].append({
                "name": name,
                "typeIdentifier": tid,
                "path": f"{dname}/enums",
                "comment": f"{name} enum.",
                "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
            })

    for svc in domain.get("services", []):
        sname = svc["name"]
        out["classes"].append({
            "name": sname,
            "typeIdentifier": kebab(sname),
            "path": f"{dname}/services",
            "comment": f"{sname} service.",
            "customCode": [build_method_code(m, agg_id) for m in svc["methods"]],
        })

with open(DST, "w") as f:
    json.dump(out, f, indent=2)

print(f"classes={len(out['classes'])} enums={len(out['enums'])}")
