import json, re

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-115000-python-script/run-005/a-mcp/metaengine-spec.json"

PRIMITIVE_MAP = {
    "string": "String",
    "number": "Number",
    "boolean": "Boolean",
    "Date": "Date",
    "any": "Any",
}

def kebab(name: str) -> str:
    s = re.sub(r'(?<!^)(?=[A-Z])', '-', name).lower()
    return s

def field_to_param(field):
    t = field["type"]
    if t in PRIMITIVE_MAP:
        return {"name": field["name"], "primitiveType": PRIMITIVE_MAP[t]}
    return {"name": field["name"], "typeIdentifier": kebab(t)}

def parse_return_type(ret):
    # Returns (code_text, refs_list, primitive_or_none)
    # code_text uses placeholders like $T for any generated type ref
    ret = ret.strip()
    if ret == "void":
        return "None", []
    # X[]
    m = re.match(r'^(\w+)\[\]$', ret)
    if m:
        name = m.group(1)
        return f"list[${name}]", [{"placeholder": f"${name}", "typeIdentifier": kebab(name)}]
    # X | null
    m = re.match(r'^(\w+)\s*\|\s*null$', ret)
    if m:
        name = m.group(1)
        return f"${name} | None", [{"placeholder": f"${name}", "typeIdentifier": kebab(name)}]
    # plain primitive
    if ret == "string": return "str", []
    if ret == "number": return "float", []
    if ret == "boolean": return "bool", []
    if ret == "Date": return "datetime.datetime", []
    # plain entity
    if re.match(r'^\w+$', ret):
        return f"${ret}", [{"placeholder": f"${ret}", "typeIdentifier": kebab(ret)}]
    return "Any", []

def parse_param_type(param_type):
    # Partial<X>, string, number, etc.
    m = re.match(r'^Partial<(\w+)>$', param_type)
    if m:
        name = m.group(1)
        return f"${name}", [{"placeholder": f"${name}", "typeIdentifier": kebab(name)}]
    if param_type == "string": return "str", []
    if param_type == "number": return "float", []
    if param_type == "boolean": return "bool", []
    if param_type == "Date": return "datetime.datetime", []
    if re.match(r'^\w+$', param_type):
        return f"${param_type}", [{"placeholder": f"${param_type}", "typeIdentifier": kebab(param_type)}]
    return "Any", []

def safe_param_name(name):
    reserved = {"class","import","from","lambda","def","del","return","try","except",
                "finally","raise","with","yield","async","await","global","nonlocal",
                "pass","in","is","not","and","or","if","elif","else","for","while",
                "True","False","None"}
    if name in reserved:
        return name + "_"
    return name

def main():
    spec = json.load(open(SRC))
    out = {
        "language": "python",
        "packageName": "metaengine_demo",
        "classes": [],
        "enums": [],
    }
    for domain in spec["domains"]:
        dname = domain["name"]
        for t in domain.get("types", []):
            kind = t["kind"]
            name = t["name"]
            tid = kebab(name)
            if kind == "enum":
                out["enums"].append({
                    "name": name,
                    "typeIdentifier": tid,
                    "path": f"{dname}/enums",
                    "members": t["members"],
                    "comment": f"{name} enum.",
                })
            elif kind == "aggregate":
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
        for svc in domain.get("services", []):
            sname = svc["name"]
            stid = kebab(sname)
            custom_code = []
            for m in svc["methods"]:
                mname = m["name"]
                params = m.get("params", [])
                ret_text, ret_refs = parse_return_type(m["returns"])
                param_strs = ["self"]
                refs = list(ret_refs)
                seen_placeholders = {r["placeholder"] for r in refs}
                for p in params:
                    pt_text, pt_refs = parse_param_type(p["type"])
                    param_strs.append(f"{safe_param_name(p['name'])}: {pt_text}")
                    for r in pt_refs:
                        if r["placeholder"] not in seen_placeholders:
                            refs.append(r)
                            seen_placeholders.add(r["placeholder"])
                code = f"def {mname}({', '.join(param_strs)}) -> {ret_text}:\n    raise NotImplementedError('not implemented')"
                entry = {"code": code}
                if refs:
                    entry["templateRefs"] = refs
                custom_code.append(entry)
            out["classes"].append({
                "name": sname,
                "typeIdentifier": stid,
                "path": f"{dname}/services",
                "comment": f"{sname} service.",
                "customCode": custom_code,
            })
    with open(DST, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {DST}: classes={len(out['classes'])} enums={len(out['enums'])}")

if __name__ == "__main__":
    main()
