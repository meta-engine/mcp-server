import json, re

SRC = "<benchmark>/spec/large.json"
DST = "<benchmark>/results/20260426-113002-java-script/run-002/a-mcp/metaengine-spec.json"

PRIM = {"string": "String", "number": "Number", "Date": "Date"}

def kebab(name: str) -> str:
    s = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    return s.lower()

def field_to_param(f):
    return {"name": f["name"], "primitiveType": PRIM[f["type"]]}

def java_type_for_param(t, type_ids):
    """Return (java_type_str, template_refs_list).
    java_type_str uses $placeholder for any in-batch type reference."""
    refs = []
    def addref(name):
        ph = "$" + kebab(name)
        refs.append({"placeholder": ph, "typeIdentifier": kebab(name)})
        return ph
    if t == "string": return "String", refs
    if t == "number": return "double", refs
    if t == "void":   return "void", refs
    m = re.match(r"^Partial<(\w+)>$", t)
    if m and m.group(1) in type_ids:
        return addref(m.group(1)), refs
    m = re.match(r"^(\w+)\[\]$", t)
    if m and m.group(1) in type_ids:
        ph = addref(m.group(1))
        return f"List<{ph}>", refs
    m = re.match(r"^(\w+)\s*\|\s*null$", t)
    if m and m.group(1) in type_ids:
        ph = addref(m.group(1))
        return f"Optional<{ph}>", refs
    if t in type_ids:
        return addref(t), refs
    return t, refs

def main():
    spec = json.load(open(SRC))
    classes, enums = [], []

    type_names = set()
    for d in spec["domains"]:
        for t in d.get("types", []):
            type_names.add(t["name"])
        for s in d.get("services", []):
            type_names.add(s["name"])

    for d in spec["domains"]:
        dom = d["name"]
        for t in d.get("types", []):
            if t["kind"] == "enum":
                enums.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "members": [{"name": m["name"], "value": m["value"]} for m in t["members"]],
                    "path": f"{dom}/enums",
                    "comment": f"{t['name']} enum.",
                })
            elif t["kind"] == "aggregate":
                classes.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "constructorParameters": [field_to_param(f) for f in t.get("fields", [])],
                    "path": f"{dom}/aggregates",
                    "comment": f"{t['name']} aggregate root for the {dom} domain.",
                })
            elif t["kind"] == "value_object":
                classes.append({
                    "name": t["name"],
                    "typeIdentifier": kebab(t["name"]),
                    "constructorParameters": [field_to_param(f) for f in t.get("fields", [])],
                    "path": f"{dom}/value_objects",
                    "comment": f"{t['name']} value object.",
                })

        for s in d.get("services", []):
            custom = []
            for m in s.get("methods", []):
                ret_str, ret_refs = java_type_for_param(m.get("returns", "void"), type_names)
                params_strs, all_refs = [], list(ret_refs)
                for p in m.get("params", []):
                    p_type, p_refs = java_type_for_param(p["type"], type_names)
                    params_strs.append(f"{p_type} {p['name']}")
                    all_refs.extend(p_refs)
                # de-dup refs
                seen, uniq_refs = set(), []
                for r in all_refs:
                    k = (r["placeholder"], r["typeIdentifier"])
                    if k not in seen:
                        seen.add(k); uniq_refs.append(r)
                code = (
                    f"public {ret_str} {m['name']}({', '.join(params_strs)}) {{\n"
                    f"    throw new UnsupportedOperationException(\"not implemented\");\n"
                    f"}}"
                )
                entry = {"code": code}
                if uniq_refs:
                    entry["templateRefs"] = uniq_refs
                custom.append(entry)
            classes.append({
                "name": s["name"],
                "typeIdentifier": kebab(s["name"]),
                "customCode": custom,
                "path": f"{dom}/services",
                "comment": f"{s['name']} service.",
            })

    out = {
        "language": "java",
        "packageName": "com.metaengine.demo",
        "classes": classes,
        "enums": enums,
    }
    with open(DST, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {DST}: classes={len(classes)} enums={len(enums)}")

if __name__ == "__main__":
    main()
