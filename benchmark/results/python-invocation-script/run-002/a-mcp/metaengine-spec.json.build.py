import json, re, pathlib

SPEC = pathlib.Path('<benchmark>/spec/large.json')
OUT  = pathlib.Path('<benchmark>/results/20260426-115000-python-script/run-002/a-mcp/metaengine-spec.json')

PRIM = {"string": "String", "number": "Number", "boolean": "Boolean", "Date": "Date"}
PY_BASE = {"string": "str", "number": "float", "boolean": "bool", "Date": "datetime.datetime", "any": "Any", "void": "None"}

def kebab(name: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()

def field_to_param(field):
    out = {"name": field["name"]}
    pt = PRIM.get(field["type"])
    if pt:
        out["primitiveType"] = pt
    else:
        out["typeIdentifier"] = kebab(field["type"])
    return out

def py_type_with_refs(ts: str):
    refs = []
    s = ts.strip()
    if s in PY_BASE:
        return PY_BASE[s], refs
    m = re.match(r'^Partial<(\w+)>$', s)
    if m:
        t = m.group(1)
        refs.append({"placeholder": f"${t}", "typeIdentifier": kebab(t)})
        return f"${t}", refs
    m = re.match(r'^(\w+)\s*\|\s*null$', s)
    if m:
        t = m.group(1)
        refs.append({"placeholder": f"${t}", "typeIdentifier": kebab(t)})
        return f"Optional[${t}]", refs
    m = re.match(r'^(\w+)\[\]$', s)
    if m:
        t = m.group(1)
        refs.append({"placeholder": f"${t}", "typeIdentifier": kebab(t)})
        return f"list[${t}]", refs
    if re.match(r'^\w+$', s):
        refs.append({"placeholder": f"${s}", "typeIdentifier": kebab(s)})
        return f"${s}", refs
    return s, refs

def dedupe_refs(refs):
    seen, out = set(), []
    for r in refs:
        k = (r["placeholder"], r["typeIdentifier"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out

spec = json.loads(SPEC.read_text())
result = {"language": "python", "packageName": "metaengine_demo", "classes": [], "enums": []}

for domain in spec["domains"]:
    dname = domain["name"]
    for t in domain["types"]:
        kind, name = t["kind"], t["name"]
        tid = kebab(name)
        if kind == "aggregate":
            result["classes"].append({
                "name": name, "typeIdentifier": tid,
                "comment": f"{name} aggregate root for the {dname} domain.",
                "path": f"{dname}/aggregates",
                "constructorParameters": [field_to_param(f) for f in t["fields"]],
            })
        elif kind == "value_object":
            result["classes"].append({
                "name": name, "typeIdentifier": tid,
                "comment": f"{name} value object.",
                "path": f"{dname}/value_objects",
                "constructorParameters": [field_to_param(f) for f in t["fields"]],
            })
        elif kind == "enum":
            result["enums"].append({
                "name": name, "typeIdentifier": tid,
                "comment": f"{name} enum.",
                "path": f"{dname}/enums",
                "members": t["members"],
            })
    for svc in domain["services"]:
        sname = svc["name"]
        sid = kebab(sname)
        custom_code = []
        for m in svc["methods"]:
            parts = ["self"]
            all_refs = []
            for p in m["params"]:
                pt, refs = py_type_with_refs(p["type"])
                all_refs.extend(refs)
                parts.append(f"{p['name']}: {pt}")
            ret, ret_refs = py_type_with_refs(m["returns"])
            all_refs.extend(ret_refs)
            sig = f"def {m['name']}({', '.join(parts)}) -> {ret}:\n    raise NotImplementedError('not implemented')"
            entry = {"code": sig}
            d = dedupe_refs(all_refs)
            if d:
                entry["templateRefs"] = d
            custom_code.append(entry)
        result["classes"].append({
            "name": sname, "typeIdentifier": sid,
            "comment": f"{sname} service.",
            "path": f"{dname}/services",
            "customCode": custom_code,
        })

OUT.write_text(json.dumps(result, indent=2))
print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
print(f"Classes: {len(result['classes'])}, Enums: {len(result['enums'])}")
